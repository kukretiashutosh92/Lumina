"""
Structured, reusable prompts for LLM-backed features.

This module centralizes all prompt-building logic for AI features.
Instead of writing prompts inside routers, we keep them here to:

- Keep routers clean
- Reuse prompt logic
- Easily modify AI behavior
- Maintain consistency
"""


# -------------------------------------------------
# System Messages (Define AI Behavior / Role)
# -------------------------------------------------

# Tells the LLM how to behave for summarization
SUMMARY_SYSTEM = "You write concise book summaries."

# Tells the LLM how to behave for sentiment analysis
SENTIMENT_SYSTEM = "You synthesize reader opinions."

# Tells the LLM how to behave for recommendations
RECOMMEND_SYSTEM = "You recommend books. Reply only with numbers."

# Tells the LLM how to behave for book suggestions
SUGGEST_BOOKS_SYSTEM = (
    "You suggest real, well-known books. One per line: Title by Author (Genre)."
)


# -------------------------------------------------
# Book Summary Prompt
# -------------------------------------------------

def summary_prompt(text: str, max_chars: int = 4000) -> tuple[str, str]:
    """
    Build prompt for summarizing book content.

    - text: full book content or excerpt
    - max_chars: limits size to avoid large token usage

    Returns:
        (prompt_text, system_message)
    """

    # Truncate text to avoid sending too much content to LLM
    prompt = f"Summarize this book content in 2-3 sentences:\n\n{text[:max_chars]}"

    return prompt, SUMMARY_SYSTEM


# -------------------------------------------------
# Sentiment / Review Analysis Prompt
# -------------------------------------------------

def sentiment_prompt(reviews: list[str], max_reviews: int = 20) -> tuple[str, str]:
    """
    Build prompt to generate overall sentiment from reviews.

    - reviews: list of user review texts
    - max_reviews: limits how many reviews to include

    Returns:
        (prompt_text, system_message)
    """

    # If no reviews exist, return empty prompt
    if not reviews:
        return "", SENTIMENT_SYSTEM

    # Combine first N reviews into bullet list
    combined = "\n".join(f"- {r}" for r in reviews[:max_reviews])

    prompt = (
        "Based on these reader reviews, write one short paragraph (2-3 sentences) "
        "describing the overall reader sentiment:\n\n" + combined
    )

    return prompt, SENTIMENT_SYSTEM


# -------------------------------------------------
# Helper: Format Candidate Books
# -------------------------------------------------

def _candidates_lines(candidates: list[dict], max_items: int = 80) -> str:
    """
    Convert list of candidate books into formatted text
    for LLM input.

    Each book is formatted as:
    ID 1: Title by Author (Genre)

    This helps LLM pick by ID.
    """

    return "\n".join(
        f"ID {c['id']}: {c.get('title', '')} by {c.get('author', '')} ({c.get('genre', '')})"
        for c in candidates[:max_items]
    )


# -------------------------------------------------
# Similar Books Recommendation Prompt
# -------------------------------------------------

def recommend_similar_prompt(book_info: str, candidates: list[dict]) -> tuple[str, str]:
    """
    Build prompt for recommending similar books.

    - book_info: description of reference book
    - candidates: list of possible books to choose from

    LLM must return ONLY comma-separated book IDs.
    """

    lines = _candidates_lines(candidates)

    prompt = f"""Book to match:
{book_info}

Candidates (pick the most similar, in order):
{lines}

Reply with ONLY a comma-separated list of book IDs, most similar first.
Example: 5, 12, 3"""

    return prompt, RECOMMEND_SYSTEM


# -------------------------------------------------
# Personalized User Recommendation Prompt
# -------------------------------------------------

def recommend_for_user_prompt(preferences: str, candidates: list[dict]) -> tuple[str, str]:
    """
    Build prompt for personalized recommendations.

    - preferences: user preferences or behavior summary
    - candidates: available books

    LLM must choose IDs based on user taste.
    """

    lines = _candidates_lines(candidates)

    prompt = f"""User preferences / context:
{preferences}

Available books:
{lines}

Reply with ONLY a comma-separated list of book IDs to recommend, best first.
Example: 2, 7, 1"""

    return prompt, RECOMMEND_SYSTEM


# -------------------------------------------------
# Suggest Books by Genre Prompt
# -------------------------------------------------

def suggest_books_prompt(genres: list[str], limit: int) -> tuple[str, str]:
    """
    Build prompt to suggest well-known books by genre.

    - genres: list of genres
    - limit: number of books to suggest

    Forces strict output format to simplify parsing.
    """

    genre_str = ", ".join(genres[:5])  # limit number of genres

    prompt = f"""Suggest {limit} well-known books in these genres: {genre_str}.
Reply with one book per line in this exact format: Title by Author (Genre)

Example:
Dune by Frank Herbert (Sci-Fi)
1984 by George Orwell (Fiction)

Do not number the lines.
Only output the lines, nothing else."""

    return prompt, SUGGEST_BOOKS_SYSTEM


# -------------------------------------------------
# Suggest Books Similar to Given Book Prompt
# -------------------------------------------------

def suggest_books_similar_prompt(
    book_title: str,
    book_author: str | None,
    book_genre: str | None,
    book_summary: str | None,
    limit: int,
) -> tuple[str, str]:
    """
    Build prompt to suggest well-known books similar to a specific book.

    Includes:
    - Title
    - Author (optional)
    - Genre (optional)
    - Short summary (optional)
    """

    # Build book info string dynamically
    info = f"Title: {book_title}"

    if book_author:
        info += f", Author: {book_author}"

    if book_genre:
        info += f", Genre: {book_genre}"

    # Add short summary if available
    if book_summary and book_summary.strip():
        info += f"\nSummary/context: {book_summary[:400].strip()}"

    prompt = f"""This book: {info}

Suggest {limit} well-known books that readers who liked this book would also enjoy 
(similar style, theme, or genre). Books can be from any era.

Reply with one book per line in this exact format: Title by Author (Genre)

Example:
Childsplay by Franklin

Do not number the lines.
Only output the lines, nothing else."""

    return prompt, SUGGEST_BOOKS_SYSTEM