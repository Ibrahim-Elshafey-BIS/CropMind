# ============================================
# FILE: crop.py
# ============================================

"""
CropMind - Crop Model
SQLAlchemy async model for crops

Author: CropMind Team
Date: 2026
"""

from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Crop(Base):
    """
    Crop model representing crops planted on a farm.
    Tracks planting, harvest, health status, and performance.
    """
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    variety = Column(String(255), nullable=True)
    area = Column(Float, nullable=False)
    
    planting_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=True)
    
    status = Column(String(50), nullable=False, default="growing")
    health_score = Column(Float, nullable=True)
    notes = Column(String(1000), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farm = relationship("Farm", back_populates="crops")

    # Indexes
    __table_args__ = (
        Index("ix_crops_id", "id"),
        Index("ix_crops_farm_id", "farm_id"),
        Index("ix_crops_name", "name"),
        Index("ix_crops_status", "status"),
        Index("ix_crops_planting_date", "planting_date"),
        CheckConstraint("status IN ('growing', 'harvested', 'failed')", name="ck_crops_status"),
        CheckConstraint("health_score >= 0 AND health_score <= 100", name="ck_crops_health_score"),
    )

    def __repr__(self) -> str:
        return f"<Crop(id={self.id}, name={self.name}, farm_id={self.farm_id}, status={self.status})>"