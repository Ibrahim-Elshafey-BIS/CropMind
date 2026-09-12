# === FILE: backend/app/api/routes/auth.py ===
"""
CropMind - Authentication Routes
FastAPI routes for user authentication and registration

Author: CropMind Team
Date: 2026
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.core.database import get_db
from app.core.security import create_access_token, get_current_active_user
from app.services.user_service import (
    get_user_by_email,
    create_user,
    authenticate_user,
)
from app.models.user import User

router = APIRouter()


# ============================================
# Schemas
# ============================================

class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    full_name: str = Field(..., description="User's full name")
    role: str = Field(default="worker", description="User role (manager or worker)")
    farm_id: Optional[int] = Field(default=None, description="Farm ID")


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User's full name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether the user is active")
    farm_id: Optional[int] = Field(default=None, description="Farm ID")

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="Authenticated user data")


# ============================================
# Endpoints
# ============================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        TokenResponse: JWT token and user data
    """
    # Check if email already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role,
        farm_id=user_data.farm_id,
    )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a user and return a JWT token.
    
    Args:
        login_data: User login credentials
        db: Database session
        
    Returns:
        TokenResponse: JWT token and user data
    """
    # Authenticate user
    user = await authenticate_user(db, login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the current authenticated user's information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: User data
    """
    return UserResponse.model_validate(current_user)
