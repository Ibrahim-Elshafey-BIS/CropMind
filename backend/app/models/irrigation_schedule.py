"""
CropMind - Irrigation Schedule Model
SQLAlchemy async model for farm irrigation schedules

Author: CropMind Team
Date: 2026
"""

from datetime import datetime, time
from sqlalchemy import (
    Column,
    Integer,
    String,
    Time,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class IrrigationSchedule(Base):
    """
    Irrigation Schedule model representing weekly recurring irrigation events for a farm.
    Each schedule defines a specific day and time for irrigation.
    """
    __tablename__ = "irrigation_schedules"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Day of week: 0 = Monday, 1 = Tuesday, ... 6 = Sunday
    day_of_week = Column(Integer, nullable=False)
    
    start_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=30)
    
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farm = relationship("Farm", back_populates="irrigation_schedules")

    # Indexes
    __table_args__ = (
        Index("ix_irrigation_schedules_farm_id", "farm_id"),
        Index("ix_irrigation_schedules_day_of_week", "day_of_week"),
        CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name="ck_irrigation_schedules_day_of_week"),
        CheckConstraint("duration_minutes > 0", name="ck_irrigation_schedules_duration"),
    )

    def __repr__(self) -> str:
        return f"<IrrigationSchedule(id={self.id}, farm_id={self.farm_id}, day_of_week={self.day_of_week}, start_time={self.start_time})>"