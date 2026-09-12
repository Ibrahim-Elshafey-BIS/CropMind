# === FILE: backend/app/services/user_service.py ===
"""
CropMind - User Service
Business logic for user management and authentication

Author: CropMind Team
Date: 2026
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import get_password_hash, verify_password


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get a user by their ID.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Optional[User]: User object or None if not found
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get a user by their email.
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        Optional[User]: User object or None if not found
    """
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    full_name: str,
    role: str = "worker",
    farm_id: Optional[int] = None
) -> User:
    """
    Create a new user with hashed password.
    
    Args:
        db: Database session
        email: User email
        password: Plain text password (will be hashed)
        full_name: User's full name
        role: User role (manager or worker)
        farm_id: Optional farm ID
        
    Returns:
        User: Created user object
    """
    hashed_password = get_password_hash(password)
    
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role,
        farm_id=farm_id,
        is_active=True,
        is_superuser=False,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
        
    Returns:
        Optional[User]: User object if authentication successful, None otherwise
    """
    user = await get_user_by_email(db, email)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user
