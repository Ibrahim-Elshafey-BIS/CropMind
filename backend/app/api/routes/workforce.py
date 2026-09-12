"""
CropMind - Workforce Routes
FastAPI routes for workforce operations

Author: CropMind Team
Date: 2026
"""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.core.database import get_db
from app.models.worker import Worker
from app.models.farm import Farm


# ============================================
# Schemas
# ============================================

class WorkerBase(BaseModel):
    """Base schema for worker data."""
    farm_id: int = Field(..., description="Farm ID")
    full_name: str = Field(..., description="Worker full name", max_length=255)
    phone: str = Field(..., description="Phone number", max_length=20)
    role: str = Field(..., description="Worker role", max_length=50)
    daily_wage: float = Field(..., description="Daily wage", ge=0)
    hire_date: date = Field(..., description="Date hired")
    notes: Optional[str] = Field(default=None, description="Additional notes", max_length=1000)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate that role is one of the allowed values."""
        allowed = ["laborer", "supervisor", "irrigation_specialist"]
        if v not in allowed:
            raise ValueError(f"Role must be one of: {', '.join(allowed)}")
        return v


class WorkerCreate(WorkerBase):
    """Schema for worker creation."""
    is_active: bool = Field(default=True, description="Whether the worker is active")


class WorkerUpdate(BaseModel):
    """Schema for worker update - all fields optional."""
    farm_id: Optional[int] = Field(default=None, description="Farm ID")
    full_name: Optional[str] = Field(default=None, description="Worker full name", max_length=255)
    phone: Optional[str] = Field(default=None, description="Phone number", max_length=20)
    role: Optional[str] = Field(default=None, description="Worker role", max_length=50)
    daily_wage: Optional[float] = Field(default=None, description="Daily wage", ge=0)
    hire_date: Optional[date] = Field(default=None, description="Date hired")
    is_active: Optional[bool] = Field(default=None, description="Whether the worker is active")
    notes: Optional[str] = Field(default=None, description="Additional notes", max_length=1000)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        """Validate that role is one of the allowed values."""
        if v is not None:
            allowed = ["laborer", "supervisor", "irrigation_specialist"]
            if v not in allowed:
                raise ValueError(f"Role must be one of: {', '.join(allowed)}")
        return v

    model_config = ConfigDict(from_attributes=True)


class WorkerResponse(WorkerBase):
    """Schema for worker response."""
    id: int = Field(..., description="Worker ID")
    is_active: bool = Field(..., description="Whether the worker is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


# ============================================
# Router
# ============================================

router = APIRouter()


# ============================================
# GET / - Get all workers
# ============================================

@router.get("/", response_model=List[WorkerResponse])
async def get_workers(
    farm_id: Optional[int] = Query(default=None, description="Filter by farm ID"),
    role: Optional[str] = Query(default=None, description="Filter by role"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    skip: int = Query(default=0, description="Number of records to skip"),
    limit: int = Query(default=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all workers with optional filters and pagination.
    """
    query = select(Worker)
    
    if farm_id is not None:
        query = query.where(Worker.farm_id == farm_id)
    
    if role is not None:
        query = query.where(Worker.role == role)
    
    if is_active is not None:
        query = query.where(Worker.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    workers = result.scalars().all()
    return workers


# ============================================
# POST / - Create a new worker
# ============================================

@router.post("/", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
async def create_worker(
    worker_data: WorkerCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new worker.
    """
    # Verify farm exists
    result = await db.execute(
        select(Farm).where(Farm.id == worker_data.farm_id)
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {worker_data.farm_id} not found",
        )
    
    # Create new worker
    worker = Worker(**worker_data.model_dump())
    db.add(worker)
    await db.commit()
    await db.refresh(worker)
    return worker


# ============================================
# GET /{worker_id} - Get a specific worker
# ============================================

@router.get("/{worker_id}", response_model=WorkerResponse)
async def get_worker(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific worker by ID.
    """
    result = await db.execute(
        select(Worker).where(Worker.id == worker_id)
    )
    worker = result.scalar_one_or_none()
    
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker with ID {worker_id} not found",
        )
    
    return worker


# ============================================
# PUT /{worker_id} - Update a worker
# ============================================

@router.put("/{worker_id}", response_model=WorkerResponse)
async def update_worker(
    worker_id: int,
    worker_data: WorkerUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a specific worker.
    """
    result = await db.execute(
        select(Worker).where(Worker.id == worker_id)
    )
    worker = result.scalar_one_or_none()
    
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker with ID {worker_id} not found",
        )
    
    # If farm_id is being updated, verify new farm exists
    if worker_data.farm_id is not None and worker_data.farm_id != worker.farm_id:
        result = await db.execute(
            select(Farm).where(Farm.id == worker_data.farm_id)
        )
        farm = result.scalar_one_or_none()
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm with ID {worker_data.farm_id} not found",
            )
    
    # Update only provided fields
    update_data = worker_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(worker, field, value)
    
    await db.commit()
    await db.refresh(worker)
    return worker


# ============================================
# DELETE /{worker_id} - Delete a worker
# ============================================

@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_worker(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific worker.
    """
    result = await db.execute(
        select(Worker).where(Worker.id == worker_id)
    )
    worker = result.scalar_one_or_none()
    
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker with ID {worker_id} not found",
        )
    
    await db.delete(worker)
    await db.commit()


# ============================================
# GET /farms/{farm_id}/active - Get active workers for a farm
# ============================================

@router.get("/farms/{farm_id}/active", response_model=List[WorkerResponse])
async def get_active_workers(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all active workers for a specific farm.
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
    
    # Get active workers
    result = await db.execute(
        select(Worker)
        .where(Worker.farm_id == farm_id)
        .where(Worker.is_active == True)
        .order_by(Worker.full_name)
    )
    workers = result.scalars().all()
    return workers
