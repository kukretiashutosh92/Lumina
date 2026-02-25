import json
import logging
import re

import httpx

from app.config import settings

# Module-level logger (used for warnings and debugging)
logger = logging.getLogger(__name__)

from app.llm.base import LLMBackend
from app.llm.prompts import (
    recommend_for_user_prompt,
    recommend_similar_prompt,
    sentiment_prompt,
    suggest_books_prompt,
    suggest_books_similar_prompt,
    summary_prompt,
)


# ---------------------------------------------------------
# Helper: Parse Comma-Separated ID List from LLM Output
# ---------------------------------------------------------

def _parse_id_list(text: str) -> list[int]:
    """
    Extract integer IDs from LLM output.

    The LLM is instructed to return:
        "5, 2, 10"

    But it might return:
        "5, 2, 10."
        "5 2 10"
        "5,2,10"

    This function safely extracts only valid integers.
    """
    ids = []
    for part in re.split(r"[\s,]+", text.strip()):
        part = part.strip().rstrip(".")
        if part.isdigit():
            ids.append(int(part))
    return ids


# ---------------------------------------------------------
# Helper: Clean LLM List Formatting
# ---------------------------------------------------------

def _normalize_suggestion_line(line: str) -> str:
    """
    Normalize a suggestion line by removing numbering or markdown.

    Converts:
        "1. Dune by Frank Herbert (Sci-Fi)"
        "- Dune by Frank Herbert (Sci-Fi)"
        "* Dune by Frank Herbert (Sci-Fi)"

    Into:
        "Dune by Frank Herbert (Sci-Fi)"
    """
    line = line.strip()

    # Remove leading numbering like "1. " or "2) "
    line = re.sub(r"^\s*\d+[.)]\s*", "", line)

    # Remove markdown bullet symbols like "-" or "*"
    line = re.sub(r"^[-*]\s+", "", line)

    return line.strip()


# ---------------------------------------------------------
# Helper: Parse Suggestion Line into Structured Dict
# ---------------------------------------------------------

def _parse_suggestion_line(line: str, fallback_genre: str) -> dict[str, str] | None:
    """
    Parse a line like:

        "Dune by Frank Herbert (Sci-Fi)"
        "Dune by Frank Herbert"

    Returns:
        {
            "title": "...",
            "author": "...",
            "genre": "..."
        }

    If parsing fails, returns None.
    """

    line = _normalize_suggestion_line(line)

    # Ignore empty lines or markdown headers
    if not line or line.startswith("#"):
        return None

    # Must contain " by " separator
    by_idx = line.find(" by ")
    if by_idx <= 0:
        return None

    title = line[:by_idx].strip().strip('"')
    rest = line[by_idx + 4 :].strip()

    # Try extracting genre from parentheses
    paren = rest.rfind(" (")
    if paren > 0 and rest.endswith(")"):
        author = rest[:paren].strip()
        genre = rest[paren + 2 : -1].strip()
    else:
        author = rest
        genre = fallback_genre

    if title and author:
        return {
            "title": title,
            "author": author,
            "genre": genre or fallback_genre,
        }

    return None


# =========================================================
# Ollama LLM Backend Implementation
# =========================================================

class OllamaLLM(LLMBackend):
    """
    Concrete LLM implementation using Ollama local API.

    This class:
    - Builds prompts using prompt builder functions
    - Sends them to Ollama
    - Parses and validates responses
    - Returns structured results to the application
    """

    def __init__(self):
        # Base URL for Ollama server (e.g., http://localhost:11434)
        self.base = settings.ollama_base_url.rstrip("/")

        # Default model (fallback to llama3.2 if not configured)
        self.model = getattr(settings, "ollama_model", "llama3.2") or "llama3.2"

    # -----------------------------------------------------
    # Core HTTP Call to Ollama
    # -----------------------------------------------------

    async def _call(self, prompt: str, system: str = "") -> str:
        """
        Send prompt to Ollama /api/generate endpoint.

        Ollama streams responses line-by-line as JSON.
        We accumulate "response" fields and return full text.
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.post(
                    f"{self.base}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "system": system or "You are helpful.",
                    },
                )

                # Raise exception if HTTP error
                r.raise_for_status()

                # Ollama streams JSON lines → collect responses
                out = []
                async for line in r.aiter_lines():
                    if line:
                        d = json.loads(line)
                        if "response" in d:
                            out.append(d["response"])

                return "".join(out).strip() or "No response."

        except Exception as e:
            # Log detailed warning but return safe fallback
            logger.warning("Ollama _call failed: %s", e, exc_info=True)
            return ""

    # -----------------------------------------------------
    # Summarization
    # -----------------------------------------------------

    async def summarize(self, text: str) -> str:
        """
        Generate short summary of provided text.
        """
        if not text or len(text.strip()) < 10:
            return "Summary not available."

        prompt, system = summary_prompt(text)
        return await self._call(prompt, system)

    # -----------------------------------------------------
    # Sentiment Analysis
    # -----------------------------------------------------

    async def analyze_sentiment(self, reviews: list[str]) -> str:
        """
        Analyze overall sentiment from review list.
        """
        if not reviews:
            return "No reviews yet."

        prompt, system = sentiment_prompt(reviews)
        return await self._call(prompt, system)

    # -----------------------------------------------------
    # Recommend Similar Books
    # -----------------------------------------------------

    async def recommend_similar(
        self,
        book_info: str,
        candidates: list[dict],
        limit: int = 10,
    ) -> list[int]:
        """
        Recommend similar books based on:
        - Book description
        - Candidate pool

        LLM returns IDs → we validate and filter them.
        """
        if not candidates:
            return []

        prompt, system = recommend_similar_prompt(book_info, candidates)
        out = await self._call(prompt, system)

        ids = _parse_id_list(out)

        # Validate IDs against candidates
        seen = set()
        ordered = []
        valid_ids = {c["id"] for c in candidates}

        for i in ids:
            if i not in seen and i in valid_ids:
                seen.add(i)
                ordered.append(i)
            if len(ordered) >= limit:
                break

        return ordered

    # -----------------------------------------------------
    # Personalized Recommendations
    # -----------------------------------------------------

    async def recommend_for_user(
        self,
        preferences: str,
        candidates: list[dict],
        limit: int = 10,
    ) -> list[int]:
        """
        Recommend books based on user preferences.
        """
        if not candidates:
            return []

        prompt, system = recommend_for_user_prompt(preferences, candidates)
        out = await self._call(prompt, system)

        ids = _parse_id_list(out)

        seen = set()
        ordered = []
        valid_ids = {c["id"] for c in candidates}

        for i in ids:
            if i not in seen and i in valid_ids:
                seen.add(i)
                ordered.append(i)
            if len(ordered) >= limit:
                break

        return ordered

    # -----------------------------------------------------
    # Suggest Books by Genre
    # -----------------------------------------------------

    async def suggest_books_by_genre(
        self,
        genres: list[str],
        limit: int = 10,
    ) -> list[dict[str, str]]:
        """
        Suggest well-known books for given genres.
        """
        if not genres:
            return []

        prompt, system = suggest_books_prompt(genres, limit)
        out = await self._call(prompt, system)

        # Detect empty or failed response
        if not out or not out.strip() or out.strip().lower() == "no response.":
            logger.warning(
                "Ollama suggest_books_by_genre returned empty response "
                "(check Ollama is running and model is loaded)"
            )
            return []

        suggestions = []
        fallback = genres[0] if genres else ""

        for line in out.splitlines():
            parsed = _parse_suggestion_line(line, fallback)
            if parsed:
                suggestions.append(parsed)

            if len(suggestions) >= limit:
                break

        # Log if model returned unparseable output
        if not suggestions and out.strip():
            logger.warning(
                "Ollama suggest_books_by_genre returned text but no parseable lines. "
                "First 300 chars: %s",
                out[:300],
            )

        return suggestions[:limit]

    # -----------------------------------------------------
    # Suggest Books Similar to Specific Book
    # -----------------------------------------------------

    async def suggest_books_similar_to(
        self,
        book_title: str,
        book_author: str | None = None,
        book_genre: str | None = None,
        book_summary: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, str]]:
        """
        Suggest books similar to a given book.
        """
        if not book_title or not book_title.strip():
            return []

        prompt, system = suggest_books_similar_prompt(
            book_title.strip(),
            book_author,
            book_genre,
            book_summary,
            limit,
        )

        out = await self._call(prompt, system)

        if not out or not out.strip() or out.strip().lower() == "no response.":
            logger.warning(
                "Ollama suggest_books_similar_to returned empty response "
                "(check Ollama is running and model is loaded)"
            )
            return []

        suggestions = []
        fallback_genre = book_genre or "Fiction"

        for line in out.splitlines():
            parsed = _parse_suggestion_line(line, fallback_genre)
            if parsed:
                suggestions.append(parsed)

            if len(suggestions) >= limit:
                break

        if not suggestions and out.strip():
            logger.warning(
                "Ollama suggest_books_similar_to returned text but no parseable lines. "
                "First 300 chars: %s",
                out[:300],
            )

        return suggestions[:limit]