from app.llm.base import LLMBackend


class MockLLM(LLMBackend):
    """
    Mock implementation of LLMBackend.

    Purpose:
    - Used for local development
    - Used for testing without external API calls
    - Provides deterministic responses
    - Removes dependency on OpenAI / Ollama

    This allows:
    - Faster unit testing
    - CI environments without API keys
    - Offline development
    """

    # ---------------------------------------------------------
    # Mock Summarization
    # ---------------------------------------------------------

    async def summarize(self, text: str) -> str:
        """
        Return a simple truncated summary.

        Instead of calling a real LLM:
        - If text is too short → return fallback
        - Otherwise → return first 500 chars

        This simulates summarization behavior
        while staying deterministic.
        """

        if not text or len(text.strip()) < 10:
            return "Summary not available."

        return text[:500] + "..." if len(text) > 500 else text

    # ---------------------------------------------------------
    # Mock Sentiment Analysis
    # ---------------------------------------------------------

    async def analyze_sentiment(self, reviews: list[str]) -> str:
        """
        Simulate sentiment analysis by combining review snippets.

        Logic:
        - Take up to first 5 reviews
        - Extract first 100 chars of each
        - Build synthetic consensus message
        """

        if not reviews:
            return "No reviews yet."

        # Clean and trim review snippets
        snippets = [r.strip()[:100] for r in reviews[:5] if r and r.strip()]

        if not snippets:
            return "No reviews yet."

        # If only one review → simple message
        if len(snippets) == 1:
            return (
                f"One reader noted: {snippets[0]}"
                f"{'...' if len(reviews[0]) > 100 else '.'}"
            )

        # If multiple reviews → synthesize theme-style output
        themes = (
            "; ".join(snippets)
            if len(snippets) <= 2
            else "; ".join(snippets[:2]) + f" (and {len(snippets) - 2} more)"
        )

        return f"Readers shared mixed perspectives. Recurring themes: {themes}"

    # ---------------------------------------------------------
    # Mock Similar Recommendation
    # ---------------------------------------------------------

    async def recommend_similar(
        self,
        book_info: str,
        candidates: list[dict],
        limit: int = 10,
    ) -> list[int]:
        """
        Deterministic recommendation:
        Simply return first N candidate IDs.

        Useful for:
        - Testing ordering logic
        - Testing router integration
        """
        return [c["id"] for c in candidates[:limit]]

    # ---------------------------------------------------------
    # Mock Personalized Recommendation
    # ---------------------------------------------------------

    async def recommend_for_user(
        self,
        preferences: str,
        candidates: list[dict],
        limit: int = 10,
    ) -> list[int]:
        """
        Deterministic user recommendation:
        Ignores preferences and returns first N IDs.

        Keeps behavior predictable for tests.
        """
        return [c["id"] for c in candidates[:limit]]

    # ---------------------------------------------------------
    # Mock Suggest Books by Genre
    # ---------------------------------------------------------

    async def suggest_books_by_genre(
        self,
        genres: list[str],
        limit: int = 10,
    ) -> list[dict[str, str]]:
        """
        Suggest books from a predefined in-memory dictionary.

        This simulates:
        - Genre-based suggestion logic
        - Controlled, realistic book outputs

        No LLM is involved.
        """

        suggestions = []

        # Static genre → books mapping
        # Used to simulate AI suggestions
        by_genre: dict[str, list[tuple[str, str]]] = {
            "fiction": [
                ("To Kill a Mockingbird", "Harper Lee"),
                ("1984", "George Orwell"),
                ("Pride and Prejudice", "Jane Austen"),
                ("The Great Gatsby", "F. Scott Fitzgerald"),
            ],
            "sci-fi": [
                ("Dune", "Frank Herbert"),
                ("Foundation", "Isaac Asimov"),
                ("The Martian", "Andy Weir"),
                ("Neuromancer", "William Gibson"),
            ],
            "science fiction": [
                ("Dune", "Frank Herbert"),
                ("Foundation", "Isaac Asimov"),
                ("The Martian", "Andy Weir"),
            ],
            "mystery": [
                ("The Girl with the Dragon Tattoo", "Stieg Larsson"),
                ("Gone Girl", "Gillian Flynn"),
                ("The Da Vinci Code", "Dan Brown"),
            ],
            "fantasy": [
                ("The Lord of the Rings", "J.R.R. Tolkien"),
                ("A Game of Thrones", "George R.R. Martin"),
                ("Harry Potter and the Philosopher's Stone", "J.K. Rowling"),
            ],
            "non-fiction": [
                ("Sapiens", "Yuval Noah Harari"),
                ("The Lean Startup", "Eric Ries"),
                ("Atomic Habits", "James Clear"),
            ],
            "nonfiction": [
                ("Sapiens", "Yuval Noah Harari"),
                ("Atomic Habits", "James Clear"),
            ],
        }

        # Match requested genres against dictionary
        for g in genres[:5]:
            key = g.lower().strip()

            for genre_key, books in by_genre.items():
                if genre_key in key or key in genre_key:

                    # Distribute results proportionally
                    for title, author in books[
                        : max(2, limit // max(1, len(genres)))
                    ]:
                        suggestions.append(
                            {"title": title, "author": author, "genre": g}
                        )
                    break

            if len(suggestions) >= limit:
                break

        # Fallback to fiction if no matches found
        if not suggestions and genres:
            for title, author in by_genre.get("fiction", [])[:limit]:
                suggestions.append(
                    {
                        "title": title,
                        "author": author,
                        "genre": genres[0] or "Fiction",
                    }
                )

        return suggestions[:limit]

    # ---------------------------------------------------------
    # Mock Suggest Books Similar To Specific Book
    # ---------------------------------------------------------

    async def suggest_books_similar_to(
        self,
        book_title: str,
        book_author: str | None = None,
        book_genre: str | None = None,
        book_summary: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, str]]:
        """
        Suggest books based on genre similarity only.

        This ignores:
        - Title
        - Author
        - Summary

        and matches purely on genre for predictability.
        """

        genre = (book_genre or "fiction").lower()

        by_genre: dict[str, list[tuple[str, str]]] = {
            "fiction": [
                ("To Kill a Mockingbird", "Harper Lee"),
                ("1984", "George Orwell"),
                ("Pride and Prejudice", "Jane Austen"),
                ("The Great Gatsby", "F. Scott Fitzgerald"),
                ("The Catcher in the Rye", "J.D. Salinger"),
            ],
            "sci-fi": [
                ("Dune", "Frank Herbert"),
                ("Foundation", "Isaac Asimov"),
                ("The Martian", "Andy Weir"),
                ("Neuromancer", "William Gibson"),
            ],
            "science fiction": [
                ("Dune", "Frank Herbert"),
                ("Foundation", "Isaac Asimov"),
                ("The Martian", "Andy Weir"),
            ],
            "mystery": [
                ("The Girl with the Dragon Tattoo", "Stieg Larsson"),
                ("Gone Girl", "Gillian Flynn"),
                ("The Da Vinci Code", "Dan Brown"),
            ],
            "fantasy": [
                ("The Lord of the Rings", "J.R.R. Tolkien"),
                ("A Game of Thrones", "George R.R. Martin"),
                ("Harry Potter and the Philosopher's Stone", "J.K. Rowling"),
            ],
        }

        suggestions = []

        # Match closest genre key
        for key, books in by_genre.items():
            if key in genre or genre in key:
                for title, author in books[:limit]:
                    suggestions.append(
                        {
                            "title": title,
                            "author": author,
                            "genre": book_genre or key,
                        }
                    )
                break

        # Fallback to fiction if no genre matched
        if not suggestions:
            for title, author in by_genre["fiction"][:limit]:
                suggestions.append(
                    {
                        "title": title,
                        "author": author,
                        "genre": book_genre or "Fiction",
                    }
                )

        return suggestions[:limit]