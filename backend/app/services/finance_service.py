"""
CropMind - Finance Service
Business logic for financial analytics and reporting

Author: CropMind Team
Date: 2026
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction


class FinanceService:
    """
    Service class for financial analytics.
    Provides monthly summaries, cost breakdowns, and profit trends.
    """
    
    async def get_monthly_summary(
        self,
        farm_id: int,
        db: AsyncSession,
        months: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Get monthly revenue, expenses, and profit for the last N months.
        
        Args:
            farm_id: Farm ID
            db: AsyncSession
            months: Number of months to retrieve
            
        Returns:
            list: Monthly summaries with revenue, expenses, and profit
        """
        result = []
        
        # Get current date
        now = datetime.utcnow()
        
        for i in range(months - 1, -1, -1):
            # Calculate month range
            month_date = now.replace(day=1) - timedelta(days=i * 30)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # End of month
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1)
            
            # Get total income for this month
            result_income = await db.execute(
                select(func.sum(Transaction.amount))
                .where(Transaction.farm_id == farm_id)
                .where(Transaction.type == "income")
                .where(Transaction.date >= month_start.date())
                .where(Transaction.date < month_end.date())
            )
            revenue = result_income.scalar() or 0.0
            
            # Get total expense for this month
            result_expense = await db.execute(
                select(func.sum(Transaction.amount))
                .where(Transaction.farm_id == farm_id)
                .where(Transaction.type == "expense")
                .where(Transaction.date >= month_start.date())
                .where(Transaction.date < month_end.date())
            )
            expenses = result_expense.scalar() or 0.0
            
            # Get profit
            profit = revenue - expenses
            
            # Month name
            month_name = month_start.strftime("%b")
            
            result.append({
                "month": month_name,
                "revenue": float(revenue),
                "expenses": float(expenses),
                "profit": float(profit),
            })
        
        return result
    
    async def get_cost_breakdown(
        self,
        farm_id: int,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Get cost breakdown grouped by expense category.
        
        Args:
            farm_id: Farm ID
            db: AsyncSession
            
        Returns:
            list: Cost breakdown by category
        """
        result = await db.execute(
            select(
                Transaction.category,
                func.sum(Transaction.amount).label("total_amount")
            )
            .where(Transaction.farm_id == farm_id)
            .where(Transaction.type == "expense")
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
        )
        
        breakdown = result.all()
        
        # Format categories for display
        category_map = {
            "seeds": "Seeds",
            "fertilizer": "Fertilizer",
            "labor": "Labor",
            "irrigation": "Irrigation",
            "pesticide": "Pesticide",
            "equipment": "Equipment",
            "other": "Other",
        }
        
        return [
            {
                "category": category_map.get(cat, cat.capitalize()),
                "amount": float(total)
            }
            for cat, total in breakdown
        ]
    
    async def get_profit_trend(
        self,
        farm_id: int,
        db: AsyncSession,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get daily profit trend for the last N days.
        
        Args:
            farm_id: Farm ID
            db: AsyncSession
            days: Number of days to retrieve
            
        Returns:
            list: Daily profit and cumulative profit
        """
        result = []
        cumulative_profit = 0.0
        
        # Get current date
        now = datetime.utcnow().date()
        start_date = now - timedelta(days=days - 1)
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            next_date = current_date + timedelta(days=1)
            
            # Get income for this day
            result_income = await db.execute(
                select(func.sum(Transaction.amount))
                .where(Transaction.farm_id == farm_id)
                .where(Transaction.type == "income")
                .where(Transaction.date >= current_date)
                .where(Transaction.date < next_date)
            )
            income = result_income.scalar() or 0.0
            
            # Get expense for this day
            result_expense = await db.execute(
                select(func.sum(Transaction.amount))
                .where(Transaction.farm_id == farm_id)
                .where(Transaction.type == "expense")
                .where(Transaction.date >= current_date)
                .where(Transaction.date < next_date)
            )
            expense = result_expense.scalar() or 0.0
            
            profit = income - expense
            cumulative_profit += profit
            
            result.append({
                "date": current_date.isoformat(),
                "profit": float(profit),
                "cumulative_profit": float(cumulative_profit),
            })
        
        return result
    
    async def get_top_income_sources(
        self,
        farm_id: int,
        db: AsyncSession,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top income sources by category.
        
        Args:
            farm_id: Farm ID
            db: AsyncSession
            limit: Number of top sources to return
            
        Returns:
            list: Top income sources with percentage
        """
        # Get total income
        result_total = await db.execute(
            select(func.sum(Transaction.amount))
            .where(Transaction.farm_id == farm_id)
            .where(Transaction.type == "income")
        )
        total_income = result_total.scalar() or 0.0
        
        if total_income == 0:
            return []
        
        # Get income by category
        result = await db.execute(
            select(
                Transaction.category,
                func.sum(Transaction.amount).label("total_amount")
            )
            .where(Transaction.farm_id == farm_id)
            .where(Transaction.type == "income")
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(limit)
        )
        
        sources = result.all()
        
        # Format categories
        category_map = {
            "sales": "Sales",
            "harvest": "Harvest",
            "subsidy": "Subsidy",
            "loan": "Loan",
            "other": "Other",
        }
        
        return [
            {
                "category": category_map.get(cat, cat.capitalize()),
                "total": float(total),
                "percentage": float(total / total_income * 100)
            }
            for cat, total in sources
        ]
    
    async def get_financial_health_score(
        self,
        farm_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get overall financial health score (0-100).
        
        Args:
            farm_id: Farm ID
            db: AsyncSession
            
        Returns:
            dict: Financial health score with breakdown
        """
        # Get total income and expense
        result_income = await db.execute(
            select(func.sum(Transaction.amount))
            .where(Transaction.farm_id == farm_id)
            .where(Transaction.type == "income")
        )
        total_income = result_income.scalar() or 0.0
        
        result_expense = await db.execute(
            select(func.sum(Transaction.amount))
            .where(Transaction.farm_id == farm_id)
            .where(Transaction.type == "expense")
        )
        total_expense = result_expense.scalar() or 0.0
        
        # Profit margin
        if total_income > 0:
            profit_margin = ((total_income - total_expense) / total_income) * 100
        else:
            profit_margin = 0
        
        # Score based on profit margin
        if profit_margin >= 30:
            profit_score = 100
        elif profit_margin >= 20:
            profit_score = 80
        elif profit_margin >= 10:
            profit_score = 60
        elif profit_margin >= 0:
            profit_score = 40
        else:
            profit_score = 20
        
        # Score based on transaction volume
        result_count = await db.execute(
            select(func.count(Transaction.id))
            .where(Transaction.farm_id == farm_id)
        )
        transaction_count = result_count.scalar() or 0
        
        if transaction_count >= 50:
            volume_score = 100
        elif transaction_count >= 30:
            volume_score = 80
        elif transaction_count >= 15:
            volume_score = 60
        elif transaction_count >= 5:
            volume_score = 40
        else:
            volume_score = 20
        
        # Score based on diversity (number of income categories)
        result_categories = await db.execute(
            select(func.count(func.distinct(Transaction.category)))
            .where(Transaction.farm_id == farm_id)
            .where(Transaction.type == "income")
        )
        category_count = result_categories.scalar() or 0
        
        if category_count >= 5:
            diversity_score = 100
        elif category_count >= 3:
            diversity_score = 70
        elif category_count >= 1:
            diversity_score = 40
        else:
            diversity_score = 20
        
        # Weighted average
        overall_score = (
            profit_score * 0.5 +
            volume_score * 0.3 +
            diversity_score * 0.2
        )
        
        return {
            "overall_score": int(round(overall_score)),
            "profit_margin": float(profit_margin),
            "profit_score": int(profit_score),
            "volume_score": int(volume_score),
            "diversity_score": int(diversity_score),
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "net_profit": float(total_income - total_expense),
        }


# Singleton instance
finance_service = FinanceService()
