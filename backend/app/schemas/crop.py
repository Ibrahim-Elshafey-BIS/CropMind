"""
CropMind - Crop Schemas
Pydantic v2 schemas for crop operations

Author: CropMind Team
Date: 2026
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class CropBase(BaseModel):
    """
    Base schema for crop data.
    """
    farm_id: int = Field(..., description="Farm ID")
    name: str = Field(..., description="Crop name", max_length=255)
    variety: Optional[str] = Field(default=None, description="Crop variety", max_length=255)
    area: float = Field(..., description="Area in feddans", gt=0)
    planting_date: date = Field(..., description="Date planted")
    expected_harvest_date: Optional[date] = Field(default=None, description="Expected harvest date")
    status: str = Field(default="growing", description="Crop status", max_length=50)
    health_score: Optional[float] = Field(default=None, description="Health score 0-100", ge=0, le=100)
    notes: Optional[str] = Field(default=None, description="Additional notes", max_length=1000)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that status is one of the allowed values."""
        allowed = ["growing", "harvested", "failed"]
        if v not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v


class CropCreate(CropBase):
    """
    Schema for crop creation.
    """
    pass


class CropUpdate(BaseModel):
    """
    Schema for crop update - all fields optional.
    """
    farm_id: Optional[int] = Field(default=None, description="Farm ID")
    name: Optional[str] = Field(default=None, description="Crop name", max_length=255)
    variety: Optional[str] = Field(default=None, description="Crop variety", max_length=255)
    area: Optional[float] = Field(default=None, description="Area in feddans", gt=0)
    planting_date: Optional[date] = Field(default=None, description="Date planted")
    expected_harvest_date: Optional[date] = Field(default=None, description="Expected harvest date")
    status: Optional[str] = Field(default=None, description="Crop status", max_length=50)
    health_score: Optional[float] = Field(default=None, description="Health score 0-100", ge=0, le=100)
    notes: Optional[str] = Field(default=None, description="Additional notes", max_length=1000)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate that status is one of the allowed values."""
        if v is not None:
            allowed = ["growing", "harvested", "failed"]
            if v not in allowed:
                raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v

    model_config = ConfigDict(from_attributes=True)


class CropResponse(CropBase):
    """
    Schema for crop response.
    """
    id: int = Field(..., description="Crop ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
