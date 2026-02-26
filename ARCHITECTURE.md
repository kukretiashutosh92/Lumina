LuminaLib Architecture

1. Database Schema – User Preferences & Core Data Model
User preferences are the primary personalization driver in the recommendation engine.
1.1 user_preferences Table
The user_preferences table stores weighted genre interests per user:
•	user_id (INT, FK → users.id)
•	genre (STRING)
•	weight (FLOAT, range typically 0–1 or 0–10 depending on normalization strategy)
A higher weight indicates stronger affinity toward that genre.
Why Weighted Preferences?
Instead of binary preferences (liked/disliked), weighted preferences:
•	Allow ranking differentiation across genres
•	Enable soft personalization
•	Support gradual preference evolution
•	Allow blending with other signals (collaborative, content similarity)

1.2 How Preferences Are Used in Scoring
During recommendation generation:
1.	Candidate books are selected.
2.	Each book’s genre is matched against the user’s stored weights.
3.	The corresponding weight becomes the raw preference score.
4.	Scores are normalized to the range [0, 1].
5.	Books already borrowed by the user are excluded.
This keeps the schema minimal while allowing future expansion.

1.3 Extending Preference Dimensions
The schema is intentionally simple to allow growth.
Future enhancements may include:
•	author_preferences table
•	decade_preferences table
•	language_preferences
•	Implicit preferences (calculated from borrow frequency)
•	Time-decayed preference weights
No redesign of the recommendation engine is required — only additional scoring modules.

1.4 Supporting Core Tables
Other essential tables include:
•	users
•	books
•	borrow_history
•	reviews
•	book_summaries
•	review_analyses
Each table is normalized and structured to avoid duplication and support hybrid scoring.

2. Async LLM Usage (Non-Blocking AI Processing)
LuminaLib integrates LLM functionality for:
•	Book summarization
•	Review sentiment aggregation
•	Optional recommendation ranking
All LLM tasks run asynchronously to prevent blocking API responses.

2.1 Book Summarization Flow
When a book is uploaded:
1.	The API handler saves:
o	Book metadata
o	Uploaded file (via StorageBackend)
2.	A background task is triggered.
3.	The background task:
o	Loads and decodes file content
o	Sends content to the configured LLM
o	Receives generated summary
o	Stores summary in book_summaries
o	Updates books.summary
The API response is returned immediately after the background task starts.
This ensures:
•	Fast upload response
•	No user wait time for LLM processing
•	Better API throughput

2.2 Review Sentiment Aggregation
When a review is submitted:
1.	Review is saved instantly.
2.	A background task:
o	Fetches all reviews for that book
o	Sends combined text to the LLM
o	Generates consensus sentiment
o	Updates review_analyses
This design ensures:
•	Immediate response to user
•	Eventually consistent sentiment analysis
•	No blocking request cycle

2.3 Thread & Database Safety
Each background task:
•	Runs in a separate thread
•	Creates a new async DB session
•	Does not reuse request session
•	Commits independently
This avoids:
•	Session conflicts
•	Event loop blocking
•	Shared state corruption

2.4 LLM Provider Abstraction
LLM access is abstracted via an LLMBackend interface.
Configured via:
LLM_PROVIDER=mock | ollama
•	mock → deterministic test responses
•	ollama → local LLM runtime using Ollama
•	Example model: Llama 3
Why Abstraction?
This ensures:
•	No router changes when switching providers
•	No business logic modification
•	Clean separation of AI infrastructure
Adding OpenAI requires:
•	New class implementing required interface methods
•	Factory update
•	API key configuration
Nothing else changes.

3. Recommendation Model (ML-Style Hybrid Architecture)
LuminaLib uses a hybrid recommendation engine combining three signals.
Weights:
•	0.4 Preference-Based
•	0.4 Collaborative
•	0.2 Content Similarity
Final Score:
Final Score =
0.4 × Preference Score +
0.4 × Collaborative Score +
0.2 × Content Similarity Score

3.1 Candidate Selection Strategy
To ensure performance scalability:
•	Only the most recent 500 books are considered
•	Already borrowed books are excluded
•	Scoring occurs only on filtered candidates
Why limit to 500?
•	Prevents full dataset vectorization
•	Predictable latency
•	Scales linearly with bounded computation

3.2 Preference-Based Signal (40%)
Source: user_preferences
Process:
•	Match candidate book genre
•	Retrieve weight
•	Normalize to [0,1]
Strength:
•	Fast
•	Personalized
•	Deterministic
Weakness:
•	Does not capture behavior patterns

3.3 Collaborative Signal (40%)
Logic:
“Users who borrowed what you borrowed also borrowed this.”
Process:
1.	Identify users overlapping with current user.
2.	Count how many of those users borrowed each candidate book.
3.	Use count as collaborative strength.
4.	Normalize across candidates.
Strength:
•	Captures community behavior
•	Independent of metadata
Weakness:
•	Suffers from cold start problem

3.4 Content Similarity Signal (20%)
Uses:
•	scikit-learn
•	TfidfVectorizer
•	Cosine similarity
Fields:
•	Title
•	Author
•	Genre
•	Summary
Process:
1.	Generate TF-IDF vectors for books.
2.	Compute user centroid from borrowed books.
3.	Measure cosine similarity.
4.	Normalize results.
Strength:
•	Semantic matching
•	Works even with sparse collaborative data
No pre-training required — computed dynamically.

4. Similar Books Endpoint
Endpoint:
GET /recommendations/similar/{book_id}
Two execution modes:

4.1 Hybrid Mode (Default)
•	TF-IDF + cosine similarity
•	Deterministic ranking
•	No LLM required

4.2 LLM Mode
Configured via:
RECOMMENDATION_ENGINE=llm
In this mode:
•	LLM receives:
o	Selected book context
o	Candidate book list
•	Returns ranked book IDs
No scikit-learn used in this mode.

5. Extensibility (Single-Config Swap Architecture)
LuminaLib is built around interface-based abstractions.

5.1 Storage Abstraction
Uses StorageBackend.
Configured via:
STORAGE_BACKEND=local | s3
•	local → filesystem
•	s3 → AWS S3
Adding new backend (e.g., MinIO):
•	Implement new class
•	Add branch in get_storage()
•	No router modification

5.2 LLM Abstraction
Uses LLMBackend.
Configured via:
LLM_PROVIDER=mock | ollama
Adding OpenAI:
•	Create OpenAILLM class
•	Implement required methods
•	Update factory
•	Add config
No change to API endpoints.

6. Frontend Architecture
Built using:
•	Next.js (App Router)
•	Tailwind CSS

6.1 Routing & Rendering
•	App Router structure
•	SSR used for SEO-relevant pages
•	Client components for auth-protected routes
•	useEffect used for redirect logic

6.2 State Management
•	No global store (Redux/Zustand not used)
•	Auth stored in React Context (AuthProvider)
•	Page-level data stored via useState
•	No centralized caching layer
Intentional design for simplicity and predictability.

6.3 Network Layer
All API calls routed through:
src/lib/api.ts
Components do not call fetch directly.
Benefits:
•	Centralized base URL
•	Easier token injection
•	Interceptor support
•	Unified error handling

6.4 Component Architecture
Reusable components:
•	BookCard
•	Nav
•	LoadingSpinner
•	ErrorMessage
Pages composed from modular components to avoid monolithic structure.

6.5 Styling Strategy
•	Tailwind CSS only
•	No CSS modules
•	No styled-components
•	Utility-first styling
•	Responsive layout
Mobile-first stacking layout with max-width container.

6.6 Error Handling Strategy
•	API calls throw errors
•	Callers use try/catch
•	Error message stored in state
•	Displayed via ErrorMessage
•	error.tsx acts as error boundary
Provides consistent UX and resilience.

7. Architectural Characteristics
LuminaLib demonstrates:
•	Hybrid multi-signal recommendation intelligence
•	Modular scoring framework
•	Async AI processing
•	Config-driven provider swapping
•	Bounded computational complexity
•	Clear frontend-backend separation
•	Interface-based extensibility
•	Performance-aware candidate limiting

8. Future Enhancements
Potential improvements:
•	Vector embeddings + vector database
•	Redis caching layer
•	Batch recommendation precomputation
•	Popularity decay scoring
•	Real-time recommendation updates
•	Horizontal scaling
•	Microservice extraction of recommendation engine
•	Distributed background worker queue

9. Conclusion
LuminaLib integrates structured preference modeling, collaborative filtering, semantic similarity scoring, and optional LLM-based ranking into a unified hybrid recommendation system.
The architecture is:
•	Scalable
•	Maintainable
•	Extensible
•	Configurable
•	Production-ready
Its modular design ensures that infrastructure components (LLM, storage, recommendation strategy) can be swapped via configuration without impacting core business logic.

