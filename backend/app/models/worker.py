# ============================================
# FILE: worker.py
# ============================================

"""
CropMind - Worker Model
SQLAlchemy async model for farm workers

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
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Worker(Base):
    """
    Worker model representing farm workers.
    Tracks worker details, roles, wages, and employment status.
    """
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    role = Column(String(50), nullable=False, default="laborer")
    daily_wage = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, default=True, nullable=False)
    hire_date = Column(Date, nullable=False)
    notes = Column(String(1000), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farm = relationship("Farm", back_populates="workers")

    # Indexes
    __table_args__ = (
        Index("ix_workers_id", "id"),
        Index("ix_workers_farm_id", "farm_id"),
        Index("ix_workers_full_name", "full_name"),
        Index("ix_workers_role", "role"),
        Index("ix_workers_is_active", "is_active"),
        CheckConstraint("role IN ('laborer', 'supervisor', 'irrigation_specialist')", name="ck_workers_role"),
        CheckConstraint("daily_wage >= 0", name="ck_workers_daily_wage"),
    )

    def __repr__(self) -> str:
        return f"<Worker(id={self.id}, full_name={self.full_name}, role={self.role}, farm_id={self.farm_id})>"