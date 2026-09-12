"""
CropMind - Database Core
Async SQLAlchemy setup with asyncpg

Author: CropMind Team
Date: 2026
"""

from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import MetaData

from app.core.config import settings


# ============================================
# Database Configuration
# ============================================

# Naming convention for constraints (optional but recommended)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Base class for all models
Base = declarative_base(metadata=MetaData(naming_convention=convention))


# ============================================
# Engine & Session Factory
# ============================================

def create_async_engine_from_settings() -> AsyncEngine:
    """
    Create async engine from settings.
    """
    is_sqlite = settings.DATABASE_URL.startswith("sqlite")
    
    engine_kwargs = {
        "echo": settings.DEBUG,
        "future": True,
    }
    
    if is_sqlite:
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        })
    
    return create_async_engine(
        settings.DATABASE_URL,
        **engine_kwargs
    )


# Initialize engine
async_engine = create_async_engine_from_settings()

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ============================================
# Database Dependency
# ============================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for database session.
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================
# Database Initialization
# ============================================

async def init_db() -> None:
    """
    Initialize database - create all tables.
    Called during application startup.
    """
    async with async_engine.begin() as conn:
        # Create all tables with checkfirst=True to avoid duplicate index errors
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


# ============================================
# Database Cleanup
# ============================================

async def close_db() -> None:
    """
    Close database connections.
    Called during application shutdown.
    """
    await async_engine.dispose()


# ============================================
# Convenience Functions
# ============================================

async def get_engine() -> AsyncEngine:
    """
    Get the async engine.
    """
    return async_engine