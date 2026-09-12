"""
CropMind - Finance Schemas
Pydantic v2 schemas for financial transactions

Author: CropMind Team
Date: 2026
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date as DateType


class TransactionBase(BaseModel):
    """
    Base schema for transaction data.
    """
    farm_id: int = Field(..., description="Farm ID")
    type: str = Field(..., description="Transaction type: income or expense", max_length=50)
    category: str = Field(..., description="Transaction category", max_length=255)
    amount: float = Field(..., description="Transaction amount", gt=0)
    description: Optional[str] = Field(default=None, description="Transaction description", max_length=1000)
    date: DateType = Field(..., description="Transaction date")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate that type is one of the allowed values."""
        allowed = ["income", "expense"]
        if v not in allowed:
            raise ValueError(f"Type must be one of: {', '.join(allowed)}")
        return v


class TransactionCreate(TransactionBase):
    """
    Schema for transaction creation.
    """
    pass


class TransactionUpdate(BaseModel):
    """
    Schema for transaction update - all fields optional.
    """
    farm_id: Optional[int] = Field(default=None, description="Farm ID")
    type: Optional[str] = Field(default=None, description="Transaction type: income or expense", max_length=50)
    category: Optional[str] = Field(default=None, description="Transaction category", max_length=255)
    amount: Optional[float] = Field(default=None, description="Transaction amount", gt=0)
    description: Optional[str] = Field(default=None, description="Transaction description", max_length=1000)
    date: Optional[DateType] = Field(default=None, description="Transaction date")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate that type is one of the allowed values."""
        if v is not None:
            allowed = ["income", "expense"]
            if v not in allowed:
                raise ValueError(f"Type must be one of: {', '.join(allowed)}")
        return v

    model_config = ConfigDict(from_attributes=True)


class TransactionResponse(TransactionBase):
    """
    Schema for transaction response.
    """
    id: int = Field(..., description="Transaction ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class FinanceSummary(BaseModel):
    """
    Schema for financial summary.
    """
    total_income: float = Field(..., description="Total income")
    total_expense: float = Field(..., description="Total expense")
    net_profit: float = Field(..., description="Net profit (income - expense)")
    transactions_count: int = Field(..., description="Total number of transactions")

    model_config = ConfigDict(from_attributes=True)