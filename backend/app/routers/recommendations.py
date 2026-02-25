# app/routers/recommendations.py

"""
Recommendation system APIs.

Handles:
- User genre preferences
- Personalized book recommendations
- ML-based similarity suggestions
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Book, Borrow, UserPreference
from app.deps import get_current_user
from app.schemas import PreferenceCreate
from app.recommendation_ml import similar_books
from app.config import settings

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/preferences")
async def get_preferences(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Get logged-in user's genre preferences.
    """
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user.id)
    )

    preferences = result.scalars().all()

    return [
        {"genre": p.genre, "weight": p.weight}
        for p in preferences
    ]


@router.post("/preferences")
async def set_preference(data: PreferenceCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Create or update user genre preference.
    """

    result = await db.execute(
        select(UserPreference).where(
            UserPreference.user_id == user.id,
            UserPreference.genre == data.genre
        )
    )

    pref = result.scalar_one_or_none()

    # Update if exists
    if pref:
        pref.weight = data.weight
    else:
        # Create new preference
        pref = UserPreference(
            user_id=user.id,
            genre=data.genre,
            weight=data.weight
        )
        db.add(pref)

    await db.commit()

    return {"message": "Preference saved"}


@router.get("")
async def get_recommendations(
    limit: int = 10,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get personalized book recommendations.
    """

    # Get books already borrowed
    borrowed_result = await db.execute(
        select(Borrow.book_id).where(Borrow.user_id == user.id)
    )
    borrowed_ids = [row[0] for row in borrowed_result.all()]

    # Fetch all books
    books_result = await db.execute(select(Book))
    books = books_result.scalars().all()

    # Remove already borrowed books
    available_books = [
        b for b in books if b.id not in borrowed_ids
    ]

    # If ML engine enabled, use similarity model
    if settings.recommendation_engine == "ml" and borrowed_ids:
        recommendations = similar_books(books, borrowed_ids[0], limit)

        return [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "genre": b.genre,
                "score": round(score, 3),
            }
            for b, score in recommendations
        ]

    # Fallback: return latest available books
    return available_books[:limit]