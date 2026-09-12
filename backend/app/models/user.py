# ============================================
# FILE: user.py
# ============================================

"""
CropMind - User Model
SQLAlchemy async model for users

Author: CropMind Team
Date: 2026
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """
    User model for authentication and authorization.
    Supports manager and worker roles.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="worker")
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships

    # Indexes
    __table_args__ = (
        Index("ix_users_id", "id"),
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
        Index("ix_users_farm_id", "farm_id"),
        Index("ix_users_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
