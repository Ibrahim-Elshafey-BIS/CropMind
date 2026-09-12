"""
CropMind - Irrigation Schedule Schemas
Pydantic v2 schemas for irrigation schedule operations

Author: CropMind Team
Date: 2026
"""

from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class IrrigationScheduleBase(BaseModel):
    """
    Base schema for irrigation schedule data.
    """
    farm_id: int = Field(..., description="Farm ID")
    day_of_week: int = Field(
        ..., 
        description="Day of week: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday",
        ge=0,
        le=6
    )
    start_time: time = Field(..., description="Irrigation start time")
    duration_minutes: int = Field(
        default=30,
        description="Duration in minutes",
        gt=0
    )
    is_active: bool = Field(default=True, description="Whether the schedule is active")
    notes: Optional[str] = Field(default=None, description="Additional notes", max_length=500)


class IrrigationScheduleCreate(IrrigationScheduleBase):
    """
    Schema for irrigation schedule creation.
    """
    pass


class IrrigationScheduleUpdate(BaseModel):
    """
    Schema for irrigation schedule update - all fields optional.
    """
    farm_id: Optional[int] = Field(default=None, description="Farm ID")
    day_of_week: Optional[int] = Field(
        default=None,
        description="Day of week: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday",
        ge=0,
        le=6
    )
    start_time: Optional[time] = Field(default=None, description="Irrigation start time")
    duration_minutes: Optional[int] = Field(
        default=None,
        description="Duration in minutes",
        gt=0
    )
    is_active: Optional[bool] = Field(default=None, description="Whether the schedule is active")
    notes: Optional[str] = Field(default=None, description="Additional notes", max_length=500)

    model_config = ConfigDict(from_attributes=True)


class IrrigationScheduleResponse(IrrigationScheduleBase):
    """
    Schema for irrigation schedule response.
    """
    id: int = Field(..., description="Schedule ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)