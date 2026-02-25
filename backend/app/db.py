# app/db.py

"""
- Creates async database engine
- Creates session factory
- Provides dependency to access DB in routes
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.config import settings

# Create async database engine
# echo=False -> disables SQL query logging
# NullPool -> avoids connection pooling (useful for serverless / small apps)
engine = create_async_engine(
    settings.db_url,
    echo=False,
    poolclass=NullPool,
)

# Session factory for creating DB sessions
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents objects from expiring after commit
    autoflush=False,
)

# Base class for all SQLAlchemy models
Base = declarative_base()


async def get_db():
    """
    Dependency function to provide DB session.

    Used in routes like:
        db: AsyncSession = Depends(get_db)

    Automatically closes session after request.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()