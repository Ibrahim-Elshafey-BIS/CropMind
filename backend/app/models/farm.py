# ============================================
# FILE: farm.py
# ============================================
"""
CropMind - Farm Model
SQLAlchemy async model for farms

Author: CropMind Team
Date: 2026
"""
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Farm(Base):
    """
    Farm model representing agricultural farms.
    Each farm can have multiple users, crops, workers, and sensors.
    """
    __tablename__ = "farms"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(500), nullable=True)
    area = Column(Float, nullable=False, default=0.0)
    crop_type = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    crops = relationship("Crop", back_populates="farm", cascade="all, delete-orphan")
    workers = relationship("Worker", back_populates="farm", cascade="all, delete-orphan")
    sensor_readings = relationship("SensorReading", back_populates="farm", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="farm", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="farm", cascade="all, delete-orphan")
    # NEW: added for the irrigation schedule feature
    irrigation_schedules = relationship("IrrigationSchedule", back_populates="farm", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_farms_id", "id"),
        Index("ix_farms_name", "name"),
        Index("ix_farms_is_active", "is_active"),
        Index("ix_farms_crop_type", "crop_type"),
    )

    def __repr__(self) -> str:
        return f"<Farm(id={self.id}, name={self.name}, location={self.location})>"

