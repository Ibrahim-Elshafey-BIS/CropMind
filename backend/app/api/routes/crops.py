"""
CropMind - Crops Routes
FastAPI routes for crop operations

Author: CropMind Team
Date: 2026
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.crop import Crop
from app.models.farm import Farm
from app.schemas.crop import CropCreate, CropUpdate, CropResponse

router = APIRouter()


# ============================================
# GET / - Get all crops
# ============================================

@router.get("/", response_model=List[CropResponse])
async def get_crops(
    farm_id: Optional[int] = Query(default=None, description="Filter by farm ID"),
    skip: int = Query(default=0, description="Number of records to skip"),
    limit: int = Query(default=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all crops with optional farm filter and pagination.
    """
    query = select(Crop)
    
    if farm_id is not None:
        query = query.where(Crop.farm_id == farm_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    crops = result.scalars().all()
    return crops


# ============================================
# POST / - Create a new crop
# ============================================

@router.post("/", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
async def create_crop(
    crop_data: CropCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new crop.
    """
    # Verify farm exists
    result = await db.execute(
        select(Farm).where(Farm.id == crop_data.farm_id)
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {crop_data.farm_id} not found",
        )
    
    # Validate planting and harvest dates
    if crop_data.expected_harvest_date and crop_data.planting_date > crop_data.expected_harvest_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Planting date cannot be after expected harvest date",
        )
    
    # Create new crop
    crop = Crop(**crop_data.model_dump())
    db.add(crop)
    await db.commit()
    await db.refresh(crop)
    return crop


# ============================================
# GET /{crop_id} - Get a specific crop
# ============================================

@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(
    crop_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific crop by ID.
    """
    result = await db.execute(
        select(Crop).where(Crop.id == crop_id)
    )
    crop = result.scalar_one_or_none()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with ID {crop_id} not found",
        )
    
    return crop


# ============================================
# PUT /{crop_id} - Update a crop
# ============================================

@router.put("/{crop_id}", response_model=CropResponse)
async def update_crop(
    crop_id: int,
    crop_data: CropUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a specific crop.
    """
    result = await db.execute(
        select(Crop).where(Crop.id == crop_id)
    )
    crop = result.scalar_one_or_none()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with ID {crop_id} not found",
        )
    
    # If farm_id is being updated, verify new farm exists
    if crop_data.farm_id is not None and crop_data.farm_id != crop.farm_id:
        result = await db.execute(
            select(Farm).where(Farm.id == crop_data.farm_id)
        )
        farm = result.scalar_one_or_none()
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm with ID {crop_data.farm_id} not found",
            )
    
    # Validate planting and harvest dates if both are being updated
    planting_date = crop_data.planting_date if crop_data.planting_date is not None else crop.planting_date
    expected_harvest_date = crop_data.expected_harvest_date if crop_data.expected_harvest_date is not None else crop.expected_harvest_date
    
    if expected_harvest_date and planting_date > expected_harvest_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Planting date cannot be after expected harvest date",
        )
    
    # Update only provided fields
    update_data = crop_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(crop, field, value)
    
    await db.commit()
    await db.refresh(crop)
    return crop


# ============================================
# DELETE /{crop_id} - Delete a crop
# ============================================

@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crop(
    crop_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific crop.
    """
    result = await db.execute(
        select(Crop).where(Crop.id == crop_id)
    )
    crop = result.scalar_one_or_none()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with ID {crop_id} not found",
        )
    
    await db.delete(crop)
    await db.commit()
