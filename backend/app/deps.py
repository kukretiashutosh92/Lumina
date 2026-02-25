"""

- Storage system
- LLM provider
- Current logged-in user
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import decode_token
from app.config import settings
from app.db import get_db
from app.models import User

from app.llm.mock import MockLLM
from app.llm.ollama import OllamaLLM
from app.llm.openai import OpenAILLM

from app.storage.local import LocalStorage
from app.storage.s3 import S3Storage


# -------------------------
# Token Security
# -------------------------
security = HTTPBearer()


# -------------------------
# Storage Provider
# -------------------------
def get_storage():
    """
    Returns storage system based on settings.
    """

    if settings.storage_backend == "s3":
        return S3Storage()

    # Default storage = local
    return LocalStorage(settings.local_storage_path)


# -------------------------
# LLM Provider
# -------------------------
def get_llm():
    """
    Returns AI provider based on settings.
    """

    if settings.llm_provider == "ollama":
        return OllamaLLM()

    if settings.llm_provider == "openai":
        return OpenAILLM()

    # Default = mock AI (for testing)
    return MockLLM()


# -------------------------
# Get Current Logged-in User
# -------------------------
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials = Depends(security),
):
    """
    Used in protected routes.
    Returns logged-in user.
    """

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # Decode JWT token
    payload = decode_token(credentials.credentials)

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Find user in database
    result = await db.execute(
        select(User).where(User.id == int(payload["sub"]))
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# -------------------------
# Optional User (not required login)
# -------------------------
async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    credentials = Depends(security),
):
    """
    Returns user if logged in.
    Otherwise returns None.
    """

    if not credentials:
        return None

    payload = decode_token(credentials.credentials)

    if not payload or "sub" not in payload:
        return None

    result = await db.execute(
        select(User).where(User.id == int(payload["sub"]))
    )

    return result.scalar_one_or_none()