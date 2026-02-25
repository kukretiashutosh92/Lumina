# app/routers/books.py

"""
Books API.

Handles:
- Creating books
- Listing books
- Borrowing / Returning
- Reviews
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Book, Borrow, Review
from app.schemas import BookCreate, ReviewCreate
from app.deps import get_current_user

router = APIRouter(prefix="/books", tags=["books"])


@router.post("")
async def create_book(data: BookCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Create a new book entry.
    """

    book = Book(
        title=data.title,
        author=data.author,
        genre=data.genre,
        added_by_user_id=user.id,
    )

    db.add(book)
    await db.commit()
    await db.refresh(book)  # Reload object from DB

    return book


@router.get("")
async def list_books(db: AsyncSession = Depends(get_db)):
    """
    Get all books.
    """
    result = await db.execute(select(Book))
    return result.scalars().all()


@router.get("/{book_id}")
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get single book by ID.
    """
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@router.post("/{book_id}/borrow")
async def borrow_book(book_id: int, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Borrow a book.
    """

    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    borrow = Borrow(user_id=user.id, book_id=book_id)
    db.add(borrow)

    await db.commit()

    return {"message": "Book borrowed successfully"}


@router.post("/{book_id}/return")
async def return_book(book_id: int, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Return a borrowed book.
    """

    result = await db.execute(
        select(Borrow).where(
            Borrow.book_id == book_id,
            Borrow.user_id == user.id,
            Borrow.returned_at == None
        )
    )

    borrow = result.scalar_one_or_none()

    if not borrow:
        raise HTTPException(status_code=400, detail="Book not borrowed")

    borrow.returned_at = datetime.utcnow()
    await db.commit()

    return {"message": "Book returned successfully"}


@router.post("/{book_id}/reviews")
async def add_review(book_id: int, data: ReviewCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Add review to a book.
    """

    review = Review(
        user_id=user.id,
        book_id=book_id,
        rating=data.rating,
        text=data.text,
    )

    db.add(review)
    await db.commit()
    await db.refresh(review)

    return review