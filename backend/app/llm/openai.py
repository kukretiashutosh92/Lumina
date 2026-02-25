import re

from app.config import settings
from app.llm.base import LLMBackend
from app.llm.prompts import (
    recommend_for_user_prompt,
    recommend_similar_prompt,
    sentiment_prompt,
    suggest_books_prompt,
    suggest_books_similar_prompt,
    summary_prompt,
)


# -------------------------------------------------
# Helper: Parse comma/space separated IDs
# -------------------------------------------------

def _parse_id_list(text: str) -> list[int]:
    """
    Extract numeric IDs from LLM output.

    The LLM is instructed to return:
        "5, 12, 3"

    This function safely:
    - Splits by comma or whitespace
    - Removes trailing periods
    - Keeps only valid integers
    """

    ids = []

    for part in re.split(r"[\s,]+", text.strip()):
        part = part.strip().rstrip(".")
        if part.isdigit():
            ids.append(int(part))

    return ids


# -------------------------------------------------
# OpenAI LLM Implementation
# -------------------------------------------------

class OpenAILLM(LLMBackend):
    """
    Concrete implementation of LLMBackend using OpenAI API.

    This class:
    - Sends prompts to OpenAI
    - Handles response parsing
    - Provides structured results to the rest of the app
    """

    def __init__(self):
        # Use configured model or fallback
        self.model = settings.openai_model or "gpt-4o-mini"

    # -------------------------------------------------
    # Internal API Call Wrapper
    # -------------------------------------------------

    async def _call(self, prompt: str, system: str = "") -> str:
        """
        Send request to OpenAI Chat Completion API.

        Returns:
            Model response as plain text.
        Returns empty string if:
            - API key missing
            - API error
            - Invalid response
        """

        if not settings.openai_api_key:
            return ""

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=settings.openai_api_key)

            resp = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system or "You are helpful."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1024,
            )

            # Ensure valid content exists
            if resp.choices and resp.choices[0].message.content:
                return resp.choices[0].message.content.strip() or ""

            return ""

        except Exception:
            # In production, you should log this error
            return ""

    # -------------------------------------------------
    # Book Summary
    # -------------------------------------------------

    async def summarize(self, text: str) -> str:
        """
        Generate short summary of book content.
        """

        # Basic validation to avoid sending empty content
        if not text or len(text.strip()) < 10:
            return "Summary not available."

        prompt, system = summary_prompt(text)

        return await self._call(prompt, system)

    # -------------------------------------------------
    # Sentiment Analysis
    # -------------------------------------------------

    async def analyze_sentiment(self, reviews: list[str]) -> str:
        """
        Generate overall sentiment summary from reviews.
        """

        if not reviews:
            return "No reviews yet."

        prompt, system = sentiment_prompt(reviews)

        return await self._call(prompt, system)

    # -------------------------------------------------
    # Recommend Similar Books
    # -------------------------------------------------

    async def recommend_similar(
        self,
        book_info: str,
        candidates: list[dict],
        limit: int = 10,
    ) -> list[int]:
        """
        Ask LLM to select most similar books from candidate list.

        Returns:
            Ordered list of book IDs.
        """

        if not candidates:
            return []

        prompt, system = recommend_similar_prompt(book_info, candidates)

        # Raw LLM output
        out = await self._call(prompt, system)

        # Extract numeric IDs
        ids = _parse_id_list(out)

        # Remove duplicates and invalid IDs
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

    # -------------------------------------------------
    # Personalized Recommendation
    # -------------------------------------------------

    async def recommend_for_user(
        self,
        preferences: str,
        candidates: list[dict],
        limit: int = 10,
    ) -> list[int]:
        """
        Ask LLM to recommend books based on user preferences.
        """

        if not candidates:
            return []

        prompt, system = recommend_for_user_prompt(preferences, candidates)

        out = await self._call(prompt, system)

        ids = _parse_id_list(out)

        # Clean and validate returned IDs
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

    # -------------------------------------------------
    # Suggest Books By Genre
    # -------------------------------------------------

    async def suggest_books_by_genre(
        self,
        genres: list[str],
        limit: int = 10,
    ) -> list[dict[str, str]]:
        """
        Ask LLM to suggest well-known books by genre.

        Parses output formatted as:
            Title by Author (Genre)
        """

        if not genres:
            return []

        prompt, system = suggest_books_prompt(genres, limit)

        out = await self._call(prompt, system)

        suggestions = []

        for line in out.splitlines():
            line = line.strip()

            # Skip empty or comment lines
            if not line or line.startswith("#"):
                continue

            by_idx = line.find(" by ")
            if by_idx <= 0:
                continue

            title = line[:by_idx].strip().strip('"')
            rest = line[by_idx + 4:].strip()

            # Extract genre if present in parentheses
            paren = rest.rfind(" (")

            if paren > 0 and rest.endswith(")"):
                author = rest[:paren].strip()
                genre = rest[paren + 2:-1].strip()
            else:
                author = rest
                genre = genres[0] if genres else ""

            if title and author:
                suggestions.append({
                    "title": title,
                    "author": author,
                    "genre": genre or (genres[0] if genres else ""),
                })

            if len(suggestions) >= limit:
                break

        return suggestions[:limit]

    # -------------------------------------------------
    # Suggest Books Similar To Given Book
    # -------------------------------------------------

    async def suggest_books_similar_to(
        self,
        book_title: str,
        book_author: str | None = None,
        book_genre: str | None = None,
        book_summary: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, str]]:
        """
        Ask LLM to suggest books similar to a specific book.
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

        suggestions = []
        fallback_genre = book_genre or "Fiction"

        for line in out.splitlines():
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            by_idx = line.find(" by ")
            if by_idx <= 0:
                continue

            title = line[:by_idx].strip().strip('"')
            rest = line[by_idx + 4:].strip()

            paren = rest.rfind(" (")

            if paren > 0 and rest.endswith(")"):
                author = rest[:paren].strip()
                genre = rest[paren + 2:-1].strip()
            else:
                author = rest
                genre = fallback_genre

            if title and author:
                suggestions.append({
                    "title": title,
                    "author": author,
                    "genre": genre or fallback_genre,
                })

            if len(suggestions) >= limit:
                break

        return suggestions[:limit]