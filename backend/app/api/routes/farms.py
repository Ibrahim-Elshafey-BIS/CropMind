"""
CropMind - Farms Routes
FastAPI routes for farm operations

Author: CropMind Team
Date: 2026
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmUpdate, FarmResponse

router = APIRouter()


# ============================================
# GET / - Get all farms
# ============================================

@router.get("/", response_model=List[FarmResponse])
async def get_farms(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all farms with pagination.
    """
    result = await db.execute(
        select(Farm).offset(skip).limit(limit)
    )
    farms = result.scalars().all()
    return farms


# ============================================
# POST / - Create a new farm
# ============================================

@router.post("/", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
async def create_farm(
    farm_data: FarmCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new farm.
    """
    # Check if farm with same name already exists
    result = await db.execute(
        select(Farm).where(Farm.name == farm_data.name)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Farm with name '{farm_data.name}' already exists",
        )
    
    # Create new farm
    farm = Farm(**farm_data.model_dump())
    db.add(farm)
    await db.commit()
    await db.refresh(farm)
    return farm


# ============================================
# GET /{farm_id} - Get a specific farm
# ============================================

@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific farm by ID.
    """
    result = await db.execute(
        select(Farm).where(Farm.id == farm_id)
    )
    farm = result.scalar_one_or_none()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found",
        )
    
    return farm


# ============================================
# PUT /{farm_id} - Update a farm
# ============================================

@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: int,
    farm_data: FarmUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a specific farm.
    """
    result = await db.execute(
        select(Farm).where(Farm.id == farm_id)
    )
    farm = result.scalar_one_or_none()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found",
        )
    
    # Check for duplicate name if name is being updated
    if farm_data.name and farm_data.name != farm.name:
        result = await db.execute(
            select(Farm).where(Farm.name == farm_data.name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Farm with name '{farm_data.name}' already exists",
            )
    
    # Update only provided fields
    update_data = farm_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)
    
    await db.commit()
    await db.refresh(farm)
    return farm


# ============================================
# DELETE /{farm_id} - Delete a farm
# ============================================

@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farm(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific farm.
    """
    result = await db.execute(
        select(Farm).where(Farm.id == farm_id)
    )
    farm = result.scalar_one_or_none()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found",
        )
    
    await db.delete(farm)
    await db.commit()
