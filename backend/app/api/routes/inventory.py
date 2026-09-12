"""
CropMind - Inventory Routes
FastAPI routes for inventory item operations

Author: CropMind Team
Date: 2026
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.core.database import get_db
from app.models.inventory_item import InventoryItem
from app.models.farm import Farm


# ============================================
# Schemas
# ============================================

class InventoryItemBase(BaseModel):
    """Base schema for inventory item data."""
    farm_id: int = Field(..., description="Farm ID")
    name: str = Field(..., description="Item name", max_length=255)
    category: str = Field(..., description="Item category", max_length=50)
    quantity: float = Field(..., description="Current quantity", ge=0)
    unit: str = Field(..., description="Unit of measurement", max_length=50)
    min_quantity: float = Field(..., description="Minimum quantity for alerts", ge=0)
    price_per_unit: float = Field(..., description="Price per unit", ge=0)
    notes: Optional[str] = Field(default=None, description="Additional notes", max_length=1000)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate that category is one of the allowed values."""
        allowed = ["seeds", "fertilizer", "pesticide", "equipment", "other"]
        if v not in allowed:
            raise ValueError(f"Category must be one of: {', '.join(allowed)}")
        return v


class InventoryItemCreate(InventoryItemBase):
    """Schema for inventory item creation."""
    pass


class InventoryItemUpdate(BaseModel):
    """Schema for inventory item update - all fields optional."""
    farm_id: Optional[int] = Field(default=None, description="Farm ID")
    name: Optional[str] = Field(default=None, description="Item name", max_length=255)
    category: Optional[str] = Field(default=None, description="Item category", max_length=50)
    quantity: Optional[float] = Field(default=None, description="Current quantity", ge=0)
    unit: Optional[str] = Field(default=None, description="Unit of measurement", max_length=50)
    min_quantity: Optional[float] = Field(default=None, description="Minimum quantity for alerts", ge=0)
    price_per_unit: Optional[float] = Field(default=None, description="Price per unit", ge=0)
    notes: Optional[str] = Field(default=None, description="Additional notes", max_length=1000)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        """Validate that category is one of the allowed values."""
        if v is not None:
            allowed = ["seeds", "fertilizer", "pesticide", "equipment", "other"]
            if v not in allowed:
                raise ValueError(f"Category must be one of: {', '.join(allowed)}")
        return v

    model_config = ConfigDict(from_attributes=True)


class InventoryItemResponse(InventoryItemBase):
    """Schema for inventory item response."""
    id: int = Field(..., description="Item ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


# ============================================
# Router
# ============================================

router = APIRouter()


# ============================================
# GET / - Get all inventory items
# ============================================

@router.get("/", response_model=List[InventoryItemResponse])
async def get_inventory_items(
    farm_id: Optional[int] = Query(default=None, description="Filter by farm ID"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    skip: int = Query(default=0, description="Number of records to skip"),
    limit: int = Query(default=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all inventory items with optional filters and pagination.
    """
    query = select(InventoryItem)
    
    if farm_id is not None:
        query = query.where(InventoryItem.farm_id == farm_id)
    
    if category is not None:
        query = query.where(InventoryItem.category == category)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    return items


# ============================================
# POST / - Create a new inventory item
# ============================================

@router.post("/", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item_data: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new inventory item.
    """
    # Verify farm exists
    result = await db.execute(
        select(Farm).where(Farm.id == item_data.farm_id)
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {item_data.farm_id} not found",
        )
    
    # Check for duplicate item name in same farm
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.farm_id == item_data.farm_id)
        .where(InventoryItem.name == item_data.name)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item '{item_data.name}' already exists in this farm",
        )
    
    # Create new item
    item = InventoryItem(**item_data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


# ============================================
# GET /{item_id} - Get a specific inventory item
# ============================================

@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific inventory item by ID.
    """
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with ID {item_id} not found",
        )
    
    return item


# ============================================
# PUT /{item_id} - Update an inventory item
# ============================================

@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: int,
    item_data: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a specific inventory item.
    """
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with ID {item_id} not found",
        )
    
    # If farm_id is being updated, verify new farm exists
    if item_data.farm_id is not None and item_data.farm_id != item.farm_id:
        result = await db.execute(
            select(Farm).where(Farm.id == item_data.farm_id)
        )
        farm = result.scalar_one_or_none()
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm with ID {item_data.farm_id} not found",
            )
    
    # Check for duplicate name if name is being updated
    if item_data.name and item_data.name != item.name:
        result = await db.execute(
            select(InventoryItem)
            .where(InventoryItem.farm_id == (item_data.farm_id or item.farm_id))
            .where(InventoryItem.name == item_data.name)
            .where(InventoryItem.id != item_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item '{item_data.name}' already exists in this farm",
            )
    
    # Update only provided fields
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    return item


# ============================================
# DELETE /{item_id} - Delete an inventory item
# ============================================

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific inventory item.
    """
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with ID {item_id} not found",
        )
    
    await db.delete(item)
    await db.commit()


# ============================================
# GET /farms/{farm_id}/low-stock - Get low stock items
# ============================================

@router.get("/farms/{farm_id}/low-stock", response_model=List[InventoryItemResponse])
async def get_low_stock_items(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all inventory items with quantity below minimum threshold for a specific farm.
    """
    # Verify farm exists
    result = await db.execute(
        select(Farm).where(Farm.id == farm_id)
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found",
        )
    
    # Get low stock items
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.farm_id == farm_id)
        .where(InventoryItem.quantity < InventoryItem.min_quantity)
        .order_by(InventoryItem.quantity)
    )
    items = result.scalars().all()
    return items
