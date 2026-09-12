# ============================================
# FILE: inventory_item.py
# ============================================

"""
CropMind - Inventory Item Model
SQLAlchemy async model for farm inventory items

Author: CropMind Team
Date: 2026
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class InventoryItem(Base):
    """
    Inventory Item model representing items in farm inventory.
    Tracks quantity, unit, price, and minimum stock levels for alerts.
    """
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, default="other")
    quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), nullable=False, default="piece")
    min_quantity = Column(Float, nullable=False, default=0.0)
    price_per_unit = Column(Float, nullable=False, default=0.0)
    notes = Column(String(1000), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farm = relationship("Farm", back_populates="inventory_items")

    # Indexes
    __table_args__ = (
        Index("ix_inventory_items_id", "id"),
        Index("ix_inventory_items_farm_id", "farm_id"),
        Index("ix_inventory_items_name", "name"),
        Index("ix_inventory_items_category", "category"),
        CheckConstraint("category IN ('seeds', 'fertilizer', 'pesticide', 'equipment', 'other')", name="ck_inventory_items_category"),
        CheckConstraint("quantity >= 0", name="ck_inventory_items_quantity"),
        CheckConstraint("min_quantity >= 0", name="ck_inventory_items_min_quantity"),
        CheckConstraint("price_per_unit >= 0", name="ck_inventory_items_price_per_unit"),
    )

    def __repr__(self) -> str:
        return f"<InventoryItem(id={self.id}, name={self.name}, category={self.category}, quantity={self.quantity}, farm_id={self.farm_id})>"