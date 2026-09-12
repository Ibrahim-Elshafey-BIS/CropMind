"""
CropMind - Irrigation Routes
FastAPI routes for irrigation and sensor reading operations

Author: CropMind Team
Date: 2026
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.core.database import get_db
from app.models.sensor_reading import SensorReading
from app.models.farm import Farm
from app.models.irrigation_schedule import IrrigationSchedule
from app.schemas.irrigation_schedule import (
    IrrigationScheduleCreate,
    IrrigationScheduleUpdate,
    IrrigationScheduleResponse,
)


# ============================================
# Schemas
# ============================================

class SensorReadingBase(BaseModel):
    """Base schema for sensor reading data."""
    farm_id: int = Field(..., description="Farm ID")
    sensor_id: str = Field(..., description="Sensor identifier", max_length=100)
    type: str = Field(..., description="Sensor type", max_length=50)
    value: float = Field(..., description="Sensor value")
    unit: str = Field(..., description="Unit of measurement", max_length=50)
    is_anomaly: bool = Field(default=False, description="Whether this reading is an anomaly")
    timestamp: datetime = Field(..., description="Reading timestamp")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate that type is one of the allowed values."""
        allowed = ["temperature", "humidity", "soil_moisture", "ph", "light"]
        if v not in allowed:
            raise ValueError(f"Type must be one of: {', '.join(allowed)}")
        return v


class SensorReadingCreate(BaseModel):
    """Schema for sensor reading creation."""
    farm_id: int = Field(..., description="Farm ID")
    sensor_id: str = Field(..., description="Sensor identifier", max_length=100)
    type: str = Field(..., description="Sensor type", max_length=50)
    value: float = Field(..., description="Sensor value")
    unit: str = Field(..., description="Unit of measurement", max_length=50)
    is_anomaly: bool = Field(default=False, description="Whether this reading is an anomaly")
    timestamp: Optional[datetime] = Field(default=None, description="Reading timestamp (defaults to now)")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate that type is one of the allowed values."""
        allowed = ["temperature", "humidity", "soil_moisture", "ph", "light"]
        if v not in allowed:
            raise ValueError(f"Type must be one of: {', '.join(allowed)}")
        return v


class SensorReadingResponse(SensorReadingBase):
    """Schema for sensor reading response."""
    id: int = Field(..., description="Reading ID")

    model_config = ConfigDict(from_attributes=True)


# ============================================
# Router
# ============================================

router = APIRouter()


# ============================================
# GET /farms/{farm_id}/readings - Get sensor readings for a farm
# ============================================

@router.get("/farms/{farm_id}/readings", response_model=List[SensorReadingResponse])
async def get_sensor_readings(
    farm_id: int,
    type: Optional[str] = Query(default=None, description="Filter by sensor type"),
    limit: int = Query(default=100, description="Number of records to return"),
    skip: int = Query(default=0, description="Number of records to skip"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get sensor readings for a specific farm with optional filters.
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
    
    # Build query
    query = select(SensorReading).where(SensorReading.farm_id == farm_id)
    
    if type is not None:
        query = query.where(SensorReading.type == type)
    
    query = query.order_by(desc(SensorReading.timestamp)).offset(skip).limit(limit)
    result = await db.execute(query)
    readings = result.scalars().all()
    return readings


# ============================================
# POST /readings - Create a new sensor reading
# ============================================

@router.post("/readings", response_model=SensorReadingResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor_reading(
    reading_data: SensorReadingCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new sensor reading.
    """
    # Verify farm exists
    result = await db.execute(
        select(Farm).where(Farm.id == reading_data.farm_id)
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {reading_data.farm_id} not found",
        )
    
    # Set timestamp to now if not provided
    if reading_data.timestamp is None:
        reading_data.timestamp = datetime.utcnow()
    
    # Create new reading
    reading = SensorReading(**reading_data.model_dump())
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    return reading


# ============================================
# GET /farms/{farm_id}/anomalies - Get anomaly readings
# ============================================

@router.get("/farms/{farm_id}/anomalies", response_model=List[SensorReadingResponse])
async def get_anomaly_readings(
    farm_id: int,
    limit: int = Query(default=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all sensor readings flagged as anomalies for a specific farm.
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
    
    # Get anomaly readings
    result = await db.execute(
        select(SensorReading)
        .where(SensorReading.farm_id == farm_id)
        .where(SensorReading.is_anomaly == True)
        .order_by(desc(SensorReading.timestamp))
        .limit(limit)
    )
    readings = result.scalars().all()
    return readings


# ============================================
# GET /farms/{farm_id}/latest - Get latest reading for each sensor type
# ============================================

@router.get("/farms/{farm_id}/latest", response_model=List[SensorReadingResponse])
async def get_latest_readings(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the latest reading for each sensor type for a specific farm.
    Returns one reading per sensor type (temperature, humidity, soil_moisture, ph, light).
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
    
    sensor_types = ["temperature", "humidity", "soil_moisture", "ph", "light"]
    latest_readings = []
    
    for sensor_type in sensor_types:
        result = await db.execute(
            select(SensorReading)
            .where(SensorReading.farm_id == farm_id)
            .where(SensorReading.type == sensor_type)
            .order_by(desc(SensorReading.timestamp))
            .limit(1)
        )
        reading = result.scalar_one_or_none()
        if reading:
            latest_readings.append(reading)
    
    return latest_readings


# ============================================
# Irrigation Schedule Endpoints
# ============================================

# ============================================
# GET /schedules/farms/{farm_id} - Get all schedules for a farm
# ============================================

@router.get("/schedules/farms/{farm_id}", response_model=List[IrrigationScheduleResponse])
async def get_farm_schedules(
    farm_id: int,
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all irrigation schedules for a specific farm.
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
    
    # Build query
    query = select(IrrigationSchedule).where(IrrigationSchedule.farm_id == farm_id)
    
    if is_active is not None:
        query = query.where(IrrigationSchedule.is_active == is_active)
    
    query = query.order_by(IrrigationSchedule.day_of_week, IrrigationSchedule.start_time)
    result = await db.execute(query)
    schedules = result.scalars().all()
    return schedules


# ============================================
# POST /schedules - Create a new irrigation schedule
# ============================================

@router.post("/schedules", response_model=IrrigationScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_irrigation_schedule(
    schedule_data: IrrigationScheduleCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new irrigation schedule.
    """
    # Verify farm exists
    result = await db.execute(
        select(Farm).where(Farm.id == schedule_data.farm_id)
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {schedule_data.farm_id} not found",
        )
    
    # Create new schedule
    schedule = IrrigationSchedule(**schedule_data.model_dump())
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule


# ============================================
# PUT /schedules/{schedule_id} - Update an irrigation schedule
# ============================================

@router.put("/schedules/{schedule_id}", response_model=IrrigationScheduleResponse)
async def update_irrigation_schedule(
    schedule_id: int,
    schedule_data: IrrigationScheduleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a specific irrigation schedule.
    """
    result = await db.execute(
        select(IrrigationSchedule).where(IrrigationSchedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Irrigation schedule with ID {schedule_id} not found",
        )
    
    # If farm_id is being updated, verify new farm exists
    if schedule_data.farm_id is not None and schedule_data.farm_id != schedule.farm_id:
        result = await db.execute(
            select(Farm).where(Farm.id == schedule_data.farm_id)
        )
        farm = result.scalar_one_or_none()
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm with ID {schedule_data.farm_id} not found",
            )
    
    # Update only provided fields
    update_data = schedule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    await db.commit()
    await db.refresh(schedule)
    return schedule


# ============================================
# DELETE /schedules/{schedule_id} - Delete an irrigation schedule
# ============================================

@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_irrigation_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific irrigation schedule.
    """
    result = await db.execute(
        select(IrrigationSchedule).where(IrrigationSchedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Irrigation schedule with ID {schedule_id} not found",
        )
    
    await db.delete(schedule)
    await db.commit()


# ============================================
# GET /schedules/farms/{farm_id}/today - Get today's schedules for a farm
# ============================================

@router.get("/schedules/farms/{farm_id}/today", response_model=List[IrrigationScheduleResponse])
async def get_today_schedules(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get today's active irrigation schedules for a specific farm.
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
    
    # Get today's day of week (0=Monday, 6=Sunday)
    today_weekday = datetime.now().weekday()
    
    # Get active schedules for today
    result = await db.execute(
        select(IrrigationSchedule)
        .where(IrrigationSchedule.farm_id == farm_id)
        .where(IrrigationSchedule.day_of_week == today_weekday)
        .where(IrrigationSchedule.is_active == True)
        .order_by(IrrigationSchedule.start_time)
    )
    schedules = result.scalars().all()
    return schedules