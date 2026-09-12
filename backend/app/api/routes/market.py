"""
CropMind - Market Routes
FastAPI routes for market price operations

Author: CropMind Team
Date: 2026
"""

from typing import List, Optional
from datetime import datetime
from datetime import date as DateType
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.core.database import get_db
from app.models.market_price import MarketPrice


# ============================================
# Schemas
# ============================================

class MarketPriceBase(BaseModel):
    """Base schema for market price data."""
    commodity: str = Field(..., description="Commodity name", max_length=255)
    price: float = Field(..., description="Current price", gt=0)
    min_price: Optional[float] = Field(default=None, description="Minimum price", gt=0)
    max_price: Optional[float] = Field(default=None, description="Maximum price", gt=0)
    unit: str = Field(default="EGP/kg", description="Unit of measurement", max_length=50)
    market_name: str = Field(..., description="Market name", max_length=255)
    date: DateType = Field(..., description="Price date")

    @field_validator("max_price")
    @classmethod
    def validate_price_range(cls, v: Optional[float], info) -> Optional[float]:
        """Validate that max_price >= min_price."""
        if v is not None:
            min_price = info.data.get("min_price")
            if min_price is not None and v < min_price:
                raise ValueError("max_price must be greater than or equal to min_price")
        return v


class MarketPriceCreate(MarketPriceBase):
    """Schema for market price creation."""
    pass


class MarketPriceResponse(MarketPriceBase):
    """Schema for market price response."""
    id: int = Field(..., description="Price record ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


# ============================================
# Router
# ============================================

router = APIRouter()


# ============================================
# GET /prices - Get market prices
# ============================================

@router.get("/prices", response_model=List[MarketPriceResponse])
async def get_market_prices(
    commodity: Optional[str] = Query(default=None, description="Filter by commodity name"),
    market_name: Optional[str] = Query(default=None, description="Filter by market name"),
    from_date: Optional[DateType] = Query(default=None, description="Filter from date"),
    to_date: Optional[DateType] = Query(default=None, description="Filter to date"),
    skip: int = Query(default=0, description="Number of records to skip"),
    limit: int = Query(default=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get market prices with optional filters and pagination.
    """
    query = select(MarketPrice)
    
    if commodity is not None:
        query = query.where(MarketPrice.commodity.ilike(f"%{commodity}%"))
    
    if market_name is not None:
        query = query.where(MarketPrice.market_name.ilike(f"%{market_name}%"))
    
    if from_date is not None:
        query = query.where(MarketPrice.date >= from_date)
    
    if to_date is not None:
        query = query.where(MarketPrice.date <= to_date)
    
    query = query.order_by(desc(MarketPrice.date)).offset(skip).limit(limit)
    result = await db.execute(query)
    prices = result.scalars().all()
    return prices


# ============================================
# POST /prices - Create a new market price
# ============================================

@router.post("/prices", response_model=MarketPriceResponse, status_code=status.HTTP_201_CREATED)
async def create_market_price(
    price_data: MarketPriceCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new market price record.
    """
    # Check for duplicate entry (same commodity, market, date)
    result = await db.execute(
        select(MarketPrice)
        .where(MarketPrice.commodity == price_data.commodity)
        .where(MarketPrice.market_name == price_data.market_name)
        .where(MarketPrice.date == price_data.date)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Price for {price_data.commodity} in {price_data.market_name} on {price_data.date} already exists",
        )
    
    # Create new price record
    price = MarketPrice(**price_data.model_dump())
    db.add(price)
    await db.commit()
    await db.refresh(price)
    return price


# ============================================
# GET /prices/latest - Get latest price for each commodity
# ============================================

@router.get("/prices/latest", response_model=List[MarketPriceResponse])
async def get_latest_prices(
    db: AsyncSession = Depends(get_db),
):
    """
    Get the latest price for each commodity.
    Returns one price record per commodity (most recent date).
    """
    # Subquery to get latest date for each commodity
    subquery = (
        select(
            MarketPrice.commodity,
            func.max(MarketPrice.date).label("latest_date")
        )
        .group_by(MarketPrice.commodity)
        .subquery()
    )
    
    # Main query
    query = (
        select(MarketPrice)
        .join(
            subquery,
            (MarketPrice.commodity == subquery.c.commodity) &
            (MarketPrice.date == subquery.c.latest_date)
        )
        .order_by(MarketPrice.commodity)
    )
    
    result = await db.execute(query)
    prices = result.scalars().all()
    return prices


# ============================================
# GET /prices/{commodity} - Get price history for a commodity
# ============================================

@router.get("/prices/{commodity}", response_model=List[MarketPriceResponse])
async def get_commodity_prices(
    commodity: str,
    market_name: Optional[str] = Query(default=None, description="Filter by market name"),
    from_date: Optional[DateType] = Query(default=None, description="Filter from date"),
    to_date: Optional[DateType] = Query(default=None, description="Filter to date"),
    skip: int = Query(default=0, description="Number of records to skip"),
    limit: int = Query(default=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get price history for a specific commodity with optional filters.
    """
    query = select(MarketPrice).where(MarketPrice.commodity == commodity)
    
    if market_name is not None:
        query = query.where(MarketPrice.market_name.ilike(f"%{market_name}%"))
    
    if from_date is not None:
        query = query.where(MarketPrice.date >= from_date)
    
    if to_date is not None:
        query = query.where(MarketPrice.date <= to_date)
    
    query = query.order_by(desc(MarketPrice.date)).offset(skip).limit(limit)
    result = await db.execute(query)
    prices = result.scalars().all()
    
    if not prices and skip == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No price records found for commodity: {commodity}",
        )
    
    return prices