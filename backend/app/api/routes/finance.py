"""
CropMind - Finance Routes
FastAPI routes for financial transaction operations

Author: CropMind Team
Date: 2026
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.transaction import Transaction
from app.models.farm import Farm
from app.schemas.finance import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    FinanceSummary,
)

router = APIRouter()


# ============================================
# GET / - Get all transactions
# ============================================

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    farm_id: Optional[int] = Query(default=None, description="Filter by farm ID"),
    type: Optional[str] = Query(default=None, description="Filter by type: income or expense"),
    skip: int = Query(default=0, description="Number of records to skip"),
    limit: int = Query(default=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all transactions with optional filters and pagination.
    """
    query = select(Transaction)
    
    if farm_id is not None:
        query = query.where(Transaction.farm_id == farm_id)
    
    if type is not None:
        query = query.where(Transaction.type == type)
    
    query = query.order_by(Transaction.date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    transactions = result.scalars().all()
    return transactions


# ============================================
# POST / - Create a new transaction
# ============================================

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new financial transaction.
    """
    # Verify farm exists
    result = await db.execute(
        select(Farm).where(Farm.id == transaction_data.farm_id)
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {transaction_data.farm_id} not found",
        )
    
    # Create new transaction
    transaction = Transaction(**transaction_data.model_dump())
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


# ============================================
# GET /{transaction_id} - Get a specific transaction
# ============================================

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific transaction by ID.
    """
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )
    
    return transaction


# ============================================
# PUT /{transaction_id} - Update a transaction
# ============================================

@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a specific transaction.
    """
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )
    
    # If farm_id is being updated, verify new farm exists
    if transaction_data.farm_id is not None and transaction_data.farm_id != transaction.farm_id:
        result = await db.execute(
            select(Farm).where(Farm.id == transaction_data.farm_id)
        )
        farm = result.scalar_one_or_none()
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm with ID {transaction_data.farm_id} not found",
            )
    
    # Update only provided fields
    update_data = transaction_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    await db.commit()
    await db.refresh(transaction)
    return transaction


# ============================================
# DELETE /{transaction_id} - Delete a transaction
# ============================================

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific transaction.
    """
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )
    
    await db.delete(transaction)
    await db.commit()


# ============================================
# GET /farms/{farm_id}/summary - Get financial summary for a farm
# ============================================

@router.get("/farms/{farm_id}/summary", response_model=FinanceSummary)
async def get_finance_summary(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get financial summary for a specific farm.
    """
    # Verify farm exists
    result = await db.execute(
        select(Farm).where(Farm.id == farm_id)
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found",
        )
    
    # Calculate total income
    result = await db.execute(
        select(func.sum(Transaction.amount))
        .where(Transaction.farm_id == farm_id)
        .where(Transaction.type == "income")
    )
    total_income = result.scalar() or 0.0
    
    # Calculate total expense
    result = await db.execute(
        select(func.sum(Transaction.amount))
        .where(Transaction.farm_id == farm_id)
        .where(Transaction.type == "expense")
    )
    total_expense = result.scalar() or 0.0
    
    # Calculate total transactions count
    result = await db.execute(
        select(func.count())
        .select_from(Transaction)
        .where(Transaction.farm_id == farm_id)
    )
    transactions_count = result.scalar() or 0
    
    return FinanceSummary(
        total_income=total_income,
        total_expense=total_expense,
        net_profit=total_income - total_expense,
        transactions_count=transactions_count,
    )
