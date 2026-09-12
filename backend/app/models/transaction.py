# ============================================
# FILE: transaction.py
# ============================================

"""
CropMind - Transaction Model
SQLAlchemy async model for financial transactions

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


class Transaction(Base):
    """
    Transaction model representing financial transactions on a farm.
    Tracks income and expenses with categories and amounts.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    category = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(1000), nullable=True)
    date = Column(Date, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farm = relationship("Farm", back_populates="transactions")

    # Indexes
    __table_args__ = (
        Index("ix_transactions_id", "id"),
        Index("ix_transactions_farm_id", "farm_id"),
        Index("ix_transactions_type", "type"),
        Index("ix_transactions_category", "category"),
        Index("ix_transactions_date", "date"),
        CheckConstraint("type IN ('income', 'expense')", name="ck_transactions_type"),
        CheckConstraint("amount >= 0", name="ck_transactions_amount"),
    )

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, type={self.type}, category={self.category}, amount={self.amount}, farm_id={self.farm_id})>"