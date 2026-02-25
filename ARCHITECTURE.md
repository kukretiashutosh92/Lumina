1. Overview & High-Level Architecture

This system is designed with scalability and maintainability in mind. The main goal is to provide personalized book recommendations using a hybrid intelligence approach that combines:

Content-based filtering

Collaborative filtering

TF-IDF–based similarity scoring

The architecture focuses on clean separation of concerns, non-blocking API execution, modular recommendation logic, and structured frontend-backend communication.

The overall system consists of:

Backend API layer handling business logic

Database layer storing users, books, preferences, and reviews

Hybrid recommendation engine

Frontend built with Next.js and Tailwind CSS

2. Database Design

The database stores structured data required for recommendations, including users, books, borrowing history, and user preferences.

A key table is user_preferences, which captures reading interests.

It includes:

user_id (INT) → Unique identifier for the user

genre (STRING) → Book genre such as fiction, sci-fi, history

weight (FLOAT) → Preference strength (higher value = stronger interest)

During recommendation generation:

Book genres are matched against user preference weights.

Books already borrowed by the user are excluded.

Scores are normalized to maintain consistency.

The schema is designed to be extensible, allowing additional preference dimensions like author or publication year in the future.

3. Recommendation Engine

The recommendation engine is the core intelligence component of the system.

It uses a hybrid weighted scoring model combining three signals:

40% Preference-based scoring

40% Collaborative filtering

20% Content similarity

3.1 Preference-Based Scoring (40%)

This score is calculated using genre weights stored in the user_preferences table.

If a user has a high weight for a particular genre, books in that genre receive a higher score.

Scores are normalized between 0 and 1.

3.2 Collaborative Filtering (40%)

Collaborative filtering follows the logic:

“Users who borrowed what you borrowed also borrowed this.”

The system:

Identifies overlapping users based on borrowing history

Counts shared borrow patterns

Normalizes the result to generate a collaborative score

This captures behavioral similarity between users.

3.3 Content Similarity (20%)

Content similarity is computed using:

TF-IDF vectorization (scikit-learn TfidfVectorizer)

Book title

Author

Genre

Summary

Process:

Create a vector representation for each book.

Build a user centroid vector based on previously borrowed books.

Compute cosine similarity between the user centroid and candidate books.

Normalize similarity scores.

3.4 Candidate Selection & Final Scoring

To optimize performance:

Only the most recent 500 books are considered.

Already borrowed books are excluded.

The final score is computed as:

Final Score =
0.4 × Preference Score +
0.4 × Collaborative Score +
0.2 × Content Similarity Score

The system returns the Top N books ranked by this final score.

4. Similar Books Endpoint

The system provides an endpoint to retrieve similar books based on a selected book:

GET /recommendations/similar/{book_id}

This endpoint uses TF-IDF vectorization and cosine similarity to compare:

Title

Author

Genre

Summary

The most similar books are returned based on normalized similarity scores.

5. Backend Design Principles

The backend is designed with:

Clear separation between API routes and business logic

Modular recommendation engine logic

Normalized scoring strategy

Exclusion rules for already borrowed books

Performance optimization through candidate limiting

The recommendation logic is structured so additional signals can be added in the future without restructuring the entire system.

6. Frontend Architecture

The frontend is built using:

Next.js (App Router)

Tailwind CSS

Routing is handled via Next.js App Router with SSR support where required.

State management is lightweight:

Component-level state using useState

Authentication state managed via React Context (AuthProvider)

All API calls are centralized in:

src/lib/api.ts

Components do not call fetch directly. This ensures:

Centralized request handling

Consistent error handling

Cleaner UI components

Reusable UI components include:

BookCard

Nav

ErrorMessage

LoadingSpinner

Styling is handled entirely with Tailwind CSS using responsive design principles.

Error handling:

API errors are thrown from the network layer

Components catch and display inline messages

error.tsx acts as fallback UI

7. Architectural Strengths

This system provides:

Hybrid recommendation intelligence

Multi-signal weighted scoring

Clean modular backend logic

Performance-optimized candidate selection

TF-IDF–based semantic similarity

Structured frontend-backend communication

Maintainable and extensible design

8. Conclusion

The architecture combines structured database-driven logic with machine learning–based similarity scoring to provide personalized book recommendations.

The hybrid model improves recommendation quality by blending preference matching, collaborative behavior, and content similarity. The modular backend and modern frontend ensure the system remains maintainable, scalable, and ready for future enhancements.