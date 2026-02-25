"""
Auth utilities.

Responsibilities:
- Password hashing and verification
- JWT creation and validation
- Token expiration handling

Design:
- Stateless authentication (JWT-based)
- Strong typing
- Defensive error handling
- Clear separation of concerns
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


# ---------------------------------------------------------------------
# Password Hashing Configuration
# ---------------------------------------------------------------------
# bcrypt is a strong adaptive hashing algorithm.
# CryptContext allows future algorithm upgrades without breaking hashes.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ---------------------------------------------------------------------
# Password Utilities
# ---------------------------------------------------------------------
def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        password: Raw user password.

    Returns:
        Secure hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a stored hash.

    Args:
        plain_password: User input password.
        hashed_password: Stored bcrypt hash.

    Returns:
        True if password matches, otherwise False.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------
# JWT Configuration
# ---------------------------------------------------------------------
ALGORITHM = "HS256"


def create_token(payload: Dict[str, Any]) -> str:
    """
    Create a signed JWT token with expiration.

    Args:
        payload: Dictionary containing user identity claims.

    Returns:
        Encoded JWT string.
    """
    to_encode = payload.copy()

    expire_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.token_expire_minutes
    )

    to_encode.update({"exp": expire_at})

    token = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=ALGORITHM,
    )

    return token


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.

    Args:
        token: Encoded JWT string.

    Returns:
        Decoded payload if valid, otherwise None.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )
        return payload

    except JWTError:
        # Token invalid, expired, or tampered with
        return None