"""
CropMind - Task Model
SQLAlchemy async model for farm tasks

Author: CropMind Team
Date: 2026
"""

from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Task(Base):
    """
    Task model representing farm tasks assigned to workers.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    
    priority = Column(String(50), nullable=False, default="medium")
    status = Column(String(50), nullable=False, default="pending")
    
    due_date = Column(Date, nullable=True)
    
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farm = relationship("Farm", back_populates="tasks")
    worker = relationship("Worker", back_populates="tasks")
    creator = relationship("User", foreign_keys=[created_by])

    # Indexes
    __table_args__ = (
        Index("ix_tasks_id", "id"),
        Index("ix_tasks_farm_id", "farm_id"),
        Index("ix_tasks_worker_id", "worker_id"),
        Index("ix_tasks_priority", "priority"),
        Index("ix_tasks_status", "status"),
        Index("ix_tasks_due_date", "due_date"),
        Index("ix_tasks_created_by", "created_by"),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="ck_tasks_priority"
        ),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'done')",
            name="ck_tasks_status"
        ),
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status}, priority={self.priority})>"
