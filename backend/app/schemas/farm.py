"""
CropMind - Farm Schemas
Pydantic v2 schemas for farm operations
Matches the Farm SQLAlchemy model exactly

Author: CropMind Team
Date: 2026
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FarmBase(BaseModel):
    """
    Base schema for farm data.
    All fields match the Farm SQLAlchemy model.
    """
    name: str = Field(..., description="Farm name", max_length=255)
    location: Optional[str] = Field(default=None, description="Farm location", max_length=500)
    area: float = Field(..., description="Area in feddans", ge=0)
    crop_type: Optional[str] = Field(default=None, description="Primary crop type", max_length=255)
    is_active: bool = Field(default=True, description="Whether the farm is active")


class FarmCreate(FarmBase):
    """
    Schema for farm creation.
    Inherits all fields from FarmBase.
    """
    pass


class FarmUpdate(BaseModel):
    """
    Schema for farm update - all fields optional for partial updates.
    """
    name: Optional[str] = Field(default=None, description="Farm name", max_length=255)
    location: Optional[str] = Field(default=None, description="Farm location", max_length=500)
    area: Optional[float] = Field(default=None, description="Area in feddans", ge=0)
    crop_type: Optional[str] = Field(default=None, description="Primary crop type", max_length=255)
    is_active: Optional[bool] = Field(default=None, description="Whether the farm is active")

    model_config = ConfigDict(from_attributes=True)


class FarmResponse(FarmBase):
    """
    Schema for farm response.
    Includes database-generated fields (id, created_at, updated_at).
    """
    id: int = Field(..., description="Farm ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
