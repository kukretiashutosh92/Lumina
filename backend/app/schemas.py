"""
Schemas (Data Models for API requests and responses)

These models:
- Validate incoming request data
- Control what data is returned in API responses
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# =========================
# User Schemas
# =========================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # Allows converting DB model to response


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# =========================
# Book Schemas
# =========================

class BookCreate(BaseModel):
    title: str
    author: Optional[str] = None
    genre: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: Optional[str] = None
    genre: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookDetailResponse(BookResponse):
    currently_borrowed_by_me: bool = False
    can_review: bool = False
    file_name: Optional[str] = None
    my_review: Optional["MyReviewResponse"] = None


class BookListResponse(BaseModel):
    items: List[BookResponse]
    total: int
    skip: int
    limit: int


# =========================
# Review Schemas
# =========================

class ReviewCreate(BaseModel):
    rating: int
    text: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    rating: int
    text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MyReviewResponse(BaseModel):
    rating: int
    text: Optional[str] = None


# =========================
# Preferences


class PreferenceCreate(BaseModel):
    genre: str
    weight: float = 1.0


# =========================
# AI Analysis
# =========================

class AnalysisResponse(BaseModel):
    summary: Optional[str] = None
    consensus: Optional[str] = None