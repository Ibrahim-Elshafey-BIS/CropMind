"""
CropMind - Monthly Summary
Generates monthly and yearly farm performance summaries

Author: CropMind Team
Date: 2026
"""

import asyncio
import asyncpg
from datetime import datetime, date
from typing import Dict, Any, List, Optional

from backend.app.core.config import settings


class MonthlySummary:
    """
    Monthly and yearly summary generator for farm performance.
    Aggregates financial, crop, and sensor data by month.
    """
    
    def __init__(self):
        """Initialize the Monthly Summary."""
        self.db_pool = None
        print("[MonthlySummary] ✅ Initialized")
    
    async def connect_db(self):
        """Create database connection pool."""
        try:
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"),
                min_size=1,
                max_size=5
            )
            print("[MonthlySummary] ✅ Database connected")
        except Exception as e:
            print(f"[MonthlySummary] ❌ Database connection error: {e}")
            raise
    
    async def close_db(self):
        """Close database connection pool."""
        if self.db_pool:
            await self.db_pool.close()
            print("[MonthlySummary] ✅ Database disconnected")
    
    def get_month_range(self, year: int, month: int) -> tuple:
        """Get start and end dates for a month."""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        return start_date, end_date
    
    async def get_monthly_finance(
        self, 
        farm_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Get monthly finance summary."""
        try:
            async with self.db_pool.acquire() as conn:
                # Total income
                income = await conn.fetchval(
                    """
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE farm_id = $1 
                    AND type = 'income'
                    AND date >= $2 AND date < $3
                    """,
                    farm_id, start_date, end_date
                )
                
                # Total expense
                expense = await conn.fetchval(
                    """
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE farm_id = $1 
                    AND type = 'expense'
                    AND date >= $2 AND date < $3
                    """,
                    farm_id, start_date, end_date
                )
                
                # Top expense categories
                top_expenses = await conn.fetch(
                    """
                    SELECT category, COALESCE(SUM(amount), 0) as total
                    FROM transactions
                    WHERE farm_id = $1 
                    AND type = 'expense'
                    AND date >= $2 AND date < $3
                    GROUP BY category
                    ORDER BY total DESC
                    LIMIT 5
                    """,
                    farm_id, start_date, end_date
                )
                
                # Top income sources
                top_income = await conn.fetch(
                    """
                    SELECT category, COALESCE(SUM(amount), 0) as total
                    FROM transactions
                    WHERE farm_id = $1 
                    AND type = 'income'
                    AND date >= $2 AND date < $3
                    GROUP BY category
                    ORDER BY total DESC
                    LIMIT 5
                    """,
                    farm_id, start_date, end_date
                )
                
                return {
                    "income": float(income),
                    "expense": float(expense),
                    "profit": float(income) - float(expense),
                    "top_expenses": [dict(row) for row in top_expenses],
                    "top_income": [dict(row) for row in top_income]
                }
        except Exception as e:
            print(f"[MonthlySummary] ⚠️ Error fetching finance: {e}")
            return {"income": 0, "expense": 0, "profit": 0, "top_expenses": [], "top_income": []}
    
    async def get_monthly_crops(
        self, 
        farm_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Get monthly crops summary."""
        try:
            async with self.db_pool.acquire() as conn:
                # Crops planted this month
                planted = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM crops
                    WHERE farm_id = $1 
                    AND planting_date >= $2 AND planting_date < $3
                    """,
                    farm_id, start_date, end_date
                )
                
                # Crops harvested this month
                harvested = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM crops
                    WHERE farm_id = $1 
                    AND status = 'harvested'
                    AND expected_harvest_date >= $2 AND expected_harvest_date < $3
                    """,
                    farm_id, start_date, end_date
                )
                
                # Average health of active crops
                avg_health = await conn.fetchval(
                    """
                    SELECT COALESCE(AVG(health_score), 0)
                    FROM crops
                    WHERE farm_id = $1 
                    AND status = 'growing'
                    """,
                    farm_id
                )
                
                return {
                    "planted": planted or 0,
                    "harvested": harvested or 0,
                    "avg_health": float(avg_health) if avg_health else 0
                }
        except Exception as e:
            print(f"[MonthlySummary] ⚠️ Error fetching crops: {e}")
            return {"planted": 0, "harvested": 0, "avg_health": 0}
    
    async def get_monthly_anomalies(
        self, 
        farm_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Get monthly anomalies summary."""
        try:
            async with self.db_pool.acquire() as conn:
                # Total anomalies
                total = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM sensor_readings
                    WHERE farm_id = $1 
                    AND is_anomaly = true
                    AND timestamp >= $2 AND timestamp < $3
                    """,
                    farm_id, start_date, end_date
                )
                
                # Anomalies by type
                by_type = await conn.fetch(
                    """
                    SELECT type, COUNT(*) as count
                    FROM sensor_readings
                    WHERE farm_id = $1 
                    AND is_anomaly = true
                    AND timestamp >= $2 AND timestamp < $3
                    GROUP BY type
                    ORDER BY count DESC
                    """,
                    farm_id, start_date, end_date
                )
                
                return {
                    "total": total or 0,
                    "by_type": [dict(row) for row in by_type]
                }
        except Exception as e:
            print(f"[MonthlySummary] ⚠️ Error fetching anomalies: {e}")
            return {"total": 0, "by_type": []}
    
    async def generate_monthly_summary(
        self, 
        farm_id: int, 
        year: int, 
        month: int
    ) -> Dict[str, Any]:
        """Generate comprehensive monthly summary."""
        print(f"[MonthlySummary] 📊 Generating summary for {year}-{month:02d} (farm {farm_id})")
        
        await self.connect_db()
        
        try:
            start_date, end_date = self.get_month_range(year, month)
            
            finance = await self.get_monthly_finance(farm_id, start_date, end_date)
            crops = await self.get_monthly_crops(farm_id, start_date, end_date)
            anomalies = await self.get_monthly_anomalies(farm_id, start_date, end_date)
            
            summary = {
                "farm_id": farm_id,
                "year": year,
                "month": month,
                "period": f"{year}-{month:02d}",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "finance": finance,
                "crops": crops,
                "anomalies": anomalies,
                "summary": {
                    "net_profit": finance.get("profit", 0),
                    "crops_planted": crops.get("planted", 0),
                    "crops_harvested": crops.get("harvested", 0),
                    "anomalies_count": anomalies.get("total", 0)
                }
            }
            
            print(f"[MonthlySummary] ✅ Summary generated for {year}-{month:02d}")
            return summary
            
        except Exception as e:
            print(f"[MonthlySummary] ❌ Error generating summary: {e}")
            return {"error": str(e), "farm_id": farm_id, "year": year, "month": month}
        finally:
            await self.close_db()
    
    async def generate_yearly_summary(
        self, 
        farm_id: int, 
        year: int
    ) -> Dict[str, Any]:
        """Generate yearly summary with monthly breakdown."""
        print(f"[MonthlySummary] 📊 Generating yearly summary for {year} (farm {farm_id})")
        
        await self.connect_db()
        
        try:
            monthly_summaries = []
            year_totals = {
                "income": 0,
                "expense": 0,
                "profit": 0,
                "crops_planted": 0,
                "crops_harvested": 0,
                "anomalies": 0
            }
            
            for month in range(1, 13):
                summary = await self.generate_monthly_summary(farm_id, year, month)
                if "error" not in summary:
                    monthly_summaries.append(summary)
                    
                    # Accumulate totals
                    year_totals["income"] += summary.get("finance", {}).get("income", 0)
                    year_totals["expense"] += summary.get("finance", {}).get("expense", 0)
                    year_totals["profit"] += summary.get("finance", {}).get("profit", 0)
                    year_totals["crops_planted"] += summary.get("crops", {}).get("planted", 0)
                    year_totals["crops_harvested"] += summary.get("crops", {}).get("harvested", 0)
                    year_totals["anomalies"] += summary.get("anomalies", {}).get("total", 0)
            
            yearly_summary = {
                "farm_id": farm_id,
                "year": year,
                "monthly": monthly_summaries,
                "totals": year_totals,
                "summary": {
                    "total_income": year_totals["income"],
                    "total_expense": year_totals["expense"],
                    "net_profit": year_totals["profit"],
                    "total_crops_planted": year_totals["crops_planted"],
                    "total_crops_harvested": year_totals["crops_harvested"],
                    "total_anomalies": year_totals["anomalies"]
                }
            }
            
            print(f"[MonthlySummary] ✅ Yearly summary generated for {year}")
            return yearly_summary
            
        except Exception as e:
            print(f"[MonthlySummary] ❌ Error generating yearly summary: {e}")
            return {"error": str(e), "farm_id": farm_id, "year": year}
        finally:
            await self.close_db()
    
    async def print_summary(
        self, 
        farm_id: int, 
        year: int, 
        month: Optional[int] = None
    ) -> None:
        """Print formatted summary to console."""
        if month:
            summary = await self.generate_monthly_summary(farm_id, year, month)
            self._print_monthly_summary(summary)
        else:
            summary = await self.generate_yearly_summary(farm_id, year)
            self._print_yearly_summary(summary)
    
    def _print_monthly_summary(self, summary: Dict[str, Any]) -> None:
        """Print monthly summary."""
        if "error" in summary:
            print(f"❌ Error: {summary.get('error')}")
            return
        
        print("\n" + "="*60)
        print(f"📊 MONTHLY SUMMARY - {summary.get('period')}")
        print("="*60)
        
        finance = summary.get("finance", {})
        print("\n💰 FINANCE")
        print("-"*40)
        print(f"  Income: EGP {finance.get('income', 0):,.2f}")
        print(f"  Expenses: EGP {finance.get('expense', 0):,.2f}")
        print(f"  Profit: EGP {finance.get('profit', 0):,.2f}")
        
        print("\n  Top Expenses:")
        for exp in finance.get("top_expenses", [])[:3]:
            print(f"    - {exp.get('category')}: EGP {exp.get('total', 0):,.2f}")
        
        print("\n  Top Income:")
        for inc in finance.get("top_income", [])[:3]:
            print(f"    - {inc.get('category')}: EGP {inc.get('total', 0):,.2f}")
        
        crops = summary.get("crops", {})
        print("\n🌱 CROPS")
        print("-"*40)
        print(f"  Planted: {crops.get('planted', 0)}")
        print(f"  Harvested: {crops.get('harvested', 0)}")
        print(f"  Avg Health: {crops.get('avg_health', 0):.1f}/100")
        
        anomalies = summary.get("anomalies", {})
        print("\n⚠️ ANOMALIES")
        print("-"*40)
        print(f"  Total: {anomalies.get('total', 0)}")
        
        print("\n" + "="*60)
    
    def _print_yearly_summary(self, summary: Dict[str, Any]) -> None:
        """Print yearly summary."""
        if "error" in summary:
            print(f"❌ Error: {summary.get('error')}")
            return
        
        print("\n" + "="*60)
        print(f"📊 YEARLY SUMMARY - {summary.get('year')}")
        print("="*60)
        
        totals = summary.get("totals", {})
        print("\n💰 ANNUAL FINANCE")
        print("-"*40)
        print(f"  Total Income: EGP {totals.get('income', 0):,.2f}")
        print(f"  Total Expenses: EGP {totals.get('expense', 0):,.2f}")
        print(f"  Net Profit: EGP {totals.get('profit', 0):,.2f}")
        
        print("\n🌱 ANNUAL CROPS")
        print("-"*40)
        print(f"  Total Planted: {totals.get('crops_planted', 0)}")
        print(f"  Total Harvested: {totals.get('crops_harvested', 0)}")
        
        print("\n⚠️ ANNUAL ANOMALIES")
        print("-"*40)
        print(f"  Total: {totals.get('anomalies', 0)}")
        
        print("\n📈 MONTHLY BREAKDOWN")
        print("-"*40)
        print("  Month | Profit (EGP) | Planted | Harvested")
        print("  ----- | ------------ | ------- | ---------")
        
        for month in summary.get("monthly", []):
            finance = month.get("finance", {})
            crops = month.get("crops", {})
            print(f"  {month.get('period')} | {finance.get('profit', 0):12,.2f} | {crops.get('planted', 0):7} | {crops.get('harvested', 0):8}")
        
        print("\n" + "="*60)


async def main():
    """
    Main entry point for testing.
    """
    print("="*60)
    print("🌾 CropMind - Monthly Summary")
    print("="*60)
    
    summary_gen = MonthlySummary()
    
    # Get current month
    now = datetime.now()
    year = now.year
    month = now.month
    
    # Print current month summary
    await summary_gen.print_summary(1, year, month)


if __name__ == "__main__":
    asyncio.run(main())
