"""

1. Find similar books (content-based)
2. Recommend books based on other users (collaborative)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.models import Book


# -----------------------------------
# Convert book object to single text
# -----------------------------------
def book_text(book):
    """
    Combine book fields into one string.
    Used for similarity comparison.
    """
    text = f"{book.title or ''} {book.author or ''} {book.genre or ''} {(book.summary or '')[:500]}"
    text = text.strip()

    # If everything empty → use book id
    return text if text else str(book.id)


# -----------------------------------
# Find similar books
# -----------------------------------
def similar_books(books, book_id, limit=10):
    """
    Returns books similar to given book_id.
    """

    if len(books) < 2:
        return []

    # Find index of selected book
    index = None
    for i, b in enumerate(books):
        if b.id == book_id:
            index = i
            break

    if index is None:
        return []

    # Convert all books to text
    texts = [book_text(b) for b in books]

    # Convert text to numeric vectors
    vectorizer = TfidfVectorizer(max_features=200, stop_words="english")

    try:
        matrix = vectorizer.fit_transform(texts)
    except:
        return []

    # Calculate similarity
    similarity = cosine_similarity(matrix[index:index+1], matrix).flatten()

    # Sort by similarity (highest first)
    sorted_indexes = similarity.argsort()[::-1]

    results = []

    for i in sorted_indexes:
        if i == index:
            continue

        if similarity[i] <= 0:
            continue

        results.append((books[i], float(similarity[i])))

        if len(results) >= limit:
            break

    return results


# -----------------------------------
# Collaborative filtering
# -----------------------------------
def collaborative_scores(user_book_ids, all_borrows, candidate_book_ids):
    """
    Recommend books based on other users with similar borrowing.
    
    user_book_ids = books current user borrowed
    all_borrows = list of (user_id, book_id)
    candidate_book_ids = books we want to score
    """

    if not user_book_ids or not all_borrows:
        return {bid: 0.0 for bid in candidate_book_ids}

    # Create mapping: user → books they borrowed
    user_books = {}

    for user_id, book_id in all_borrows:
        user_books.setdefault(user_id, set()).add(book_id)

    # Find users who borrowed same books as current user
    similar_users = []

    for user_id, books in user_books.items():
        if books & user_book_ids:
            similar_users.append(user_id)

    # Score candidate books
    scores = {}

    for book_id in candidate_book_ids:
        count = 0

        for user_id in similar_users:
            if book_id in user_books.get(user_id, set()):
                count += 1

        scores[book_id] = float(count)

    return scores


# -----------------------------------
# Build vector matrix for all books
# -----------------------------------
def build_book_matrix(books):
    """
    Converts all books into TF-IDF matrix.
    Used for advanced recommendations.
    """

    if not books:
        return None, None

    texts = [book_text(b) for b in books]
    vectorizer = TfidfVectorizer(max_features=200, stop_words="english")

    try:
        matrix = vectorizer.fit_transform(texts)
        return vectorizer, matrix
    except:
        return None, None


# -----------------------------------
# Recommend based on user history
# -----------------------------------
def content_similarity_to_user_books(books, user_book_ids, matrix):
    """
    Recommend books similar to books user already borrowed.
    """

    if not user_book_ids or matrix is None:
        return {}

    # Map book id → index
    book_index = {book.id: i for i, book in enumerate(books)}

    borrowed_indexes = []

    for bid in user_book_ids:
        if bid in book_index:
            borrowed_indexes.append(book_index[bid])

    if not borrowed_indexes:
        return {}

    # Create average vector of user books
    user_vector = np.asarray(matrix[borrowed_indexes].mean(axis=0))

    # Calculate similarity
    similarities = cosine_similarity(user_vector.reshape(1, -1), matrix).flatten()

    results = {}

    for i, book in enumerate(books):
        if book.id not in user_book_ids:
            results[book.id] = float(similarities[i])

    return results