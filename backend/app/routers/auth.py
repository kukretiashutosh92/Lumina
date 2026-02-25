# app/routers/auth.py

"""
Authentication API.

Handles:
- User signup
- User login (JWT token generation)
- Get current user profile
- Update profile
- Signout
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models import User
from app.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    TokenResponse,
    LoginRequest,
)
from app.auth import hash_password, verify_password, create_token
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


# --------------------------------
# User Signup
# --------------------------------
@router.post("/signup", response_model=UserResponse)
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.

    - Checks if email already exists
    - Hashes password
    - Saves user to database
    """

    # Check if email is already registered
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user with hashed password
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


# --------------------------------
# User Login
# --------------------------------
@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT access token.
    """

    # Find user by email
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()

    # Validate credentials
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Create JWT token with user ID as subject
    token = create_token({"sub": str(user.id)})

    return TokenResponse(access_token=token)


# --------------------------------
# Get Current User Profile
# --------------------------------
@router.get("/me", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_user)):
    """
    Get currently authenticated user's profile.
    """
    return user


# --------------------------------
# Update Profile
# --------------------------------
@router.put("/me", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's profile information.
    """

    # Update fields only if provided
    if data.full_name is not None:
        user.full_name = data.full_name

    await db.commit()
    await db.refresh(user)

    return user


# --------------------------------
# Signout
# --------------------------------
@router.post("/signout")
async def signout():
    """
    Sign out user.

    Note:
    JWT-based systems are stateless.
    Client must delete token on logout.
    """
    return {"message": "Signed out successfully"}