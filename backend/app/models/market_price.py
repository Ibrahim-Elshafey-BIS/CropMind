# ============================================
# FILE: market_price.py
# ============================================

"""
CropMind - Market Price Model
SQLAlchemy async model for commodity market prices

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
    Index,
    CheckConstraint,
)
from sqlalchemy.sql import func

from app.core.database import Base


class MarketPrice(Base):
    """
    Market Price model representing commodity prices from different markets.
    Independent table with no relationships.
    """
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True)
    commodity = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    unit = Column(String(50), nullable=False, default="EGP/kg")
    market_name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index("ix_market_prices_id", "id"),
        Index("ix_market_prices_commodity", "commodity"),
        Index("ix_market_prices_market_name", "market_name"),
        Index("ix_market_prices_date", "date"),
        CheckConstraint("price >= 0", name="ck_market_prices_price"),
        CheckConstraint("min_price >= 0 OR min_price IS NULL", name="ck_market_prices_min_price"),
        CheckConstraint("max_price >= 0 OR max_price IS NULL", name="ck_market_prices_max_price"),
        CheckConstraint("max_price >= min_price OR min_price IS NULL OR max_price IS NULL", name="ck_market_prices_price_range"),
    )

    def __repr__(self) -> str:
        return f"<MarketPrice(id={self.id}, commodity={self.commodity}, price={self.price}, market={self.market_name}, date={self.date})>"