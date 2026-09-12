"""
CropMind - Farm Performance Report
Generates comprehensive farm performance reports

Author: CropMind Team
Date: 2026
"""

import asyncio
import asyncpg
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.app.core.config import settings
from analytics.kpis.farm_dna_calculator import FarmDNACalculator


class FarmPerformanceReport:
    """
    Farm Performance Report generator.
    Combines DNA Score, financial, crop, worker, and alert data.
    """
    
    def __init__(self):
        """Initialize the Farm Performance Report."""
        self.db_pool = None
        self.dna_calculator = FarmDNACalculator()
        print("[FarmReport] ✅ Initialized")
    
    async def connect_db(self):
        """Create database connection pool."""
        try:
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"),
                min_size=1,
                max_size=5
            )
            print("[FarmReport] ✅ Database connected")
        except Exception as e:
            print(f"[FarmReport] ❌ Database connection error: {e}")
            raise
    
    async def close_db(self):
        """Close database connection pool."""
        if self.db_pool:
            await self.db_pool.close()
            print("[FarmReport] ✅ Database disconnected")
    
    async def get_farm_info(self, farm_id: int) -> Dict[str, Any]:
        """Get basic farm information."""
        try:
            async with self.db_pool.acquire() as conn:
                farm = await conn.fetchrow(
                    """
                    SELECT id, name, location, area, crop_type, is_active, created_at
                    FROM farms WHERE id = $1
                    """,
                    farm_id
                )
                
                if farm:
                    return dict(farm)
                return {"error": "Farm not found"}
        except Exception as e:
            print(f"[FarmReport] ⚠️ Error fetching farm info: {e}")
            return {}
    
    async def get_finance_summary(self, farm_id: int) -> Dict[str, Any]:
        """Get financial summary."""
        try:
            async with self.db_pool.acquire() as conn:
                total_income = await conn.fetchval(
                    """
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE farm_id = $1 AND type = 'income'
                    """,
                    farm_id
                )
                
                total_expense = await conn.fetchval(
                    """
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE farm_id = $1 AND type = 'expense'
                    """,
                    farm_id
                )
                
                return {
                    "total_income": float(total_income),
                    "total_expense": float(total_expense),
                    "net_profit": float(total_income) - float(total_expense)
                }
        except Exception as e:
            print(f"[FarmReport] ⚠️ Error fetching finance summary: {e}")
            return {"total_income": 0, "total_expense": 0, "net_profit": 0}
    
    async def get_crops_summary(self, farm_id: int) -> Dict[str, Any]:
        """Get crops summary."""
        try:
            async with self.db_pool.acquire() as conn:
                stats = await conn.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE status = 'growing') as growing,
                        COUNT(*) FILTER (WHERE status = 'harvested') as harvested,
                        COUNT(*) FILTER (WHERE status = 'failed') as failed,
                        COALESCE(AVG(health_score), 0) as avg_health
                    FROM crops
                    WHERE farm_id = $1
                    """,
                    farm_id
                )
                
                return dict(stats)
        except Exception as e:
            print(f"[FarmReport] ⚠️ Error fetching crops summary: {e}")
            return {"total": 0, "growing": 0, "harvested": 0, "failed": 0, "avg_health": 0}
    
    async def get_workers_summary(self, farm_id: int) -> Dict[str, Any]:
        """Get workers summary."""
        try:
            async with self.db_pool.acquire() as conn:
                stats = await conn.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE is_active = true) as active
                    FROM workers
                    WHERE farm_id = $1
                    """,
                    farm_id
                )
                
                return dict(stats)
        except Exception as e:
            print(f"[FarmReport] ⚠️ Error fetching workers summary: {e}")
            return {"total": 0, "active": 0}
    
    async def get_top_alerts(self, farm_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top alerts (low stock + anomalies)."""
        alerts = []
        
        try:
            async with self.db_pool.acquire() as conn:
                # Low stock alerts
                low_stock = await conn.fetch(
                    """
                    SELECT 
                        name as item_name,
                        quantity,
                        min_quantity,
                        unit
                    FROM inventory_items
                    WHERE farm_id = $1 AND quantity < min_quantity
                    ORDER BY (min_quantity - quantity) DESC
                    LIMIT $2
                    """,
                    farm_id, limit
                )
                
                for item in low_stock:
                    alerts.append({
                        "type": "low_stock",
                        "severity": "critical" if item['quantity'] == 0 else "high",
                        "message": f"Low stock: {item['item_name']} ({item['quantity']} {item['unit']} remaining, minimum {item['min_quantity']} {item['unit']})",
                        "data": dict(item)
                    })
                
                # Recent anomalies
                anomalies = await conn.fetch(
                    """
                    SELECT 
                        type,
                        value,
                        unit,
                        timestamp
                    FROM sensor_readings
                    WHERE farm_id = $1 AND is_anomaly = true
                    ORDER BY timestamp DESC
                    LIMIT $2
                    """,
                    farm_id, limit - len(alerts)
                )
                
                for anomaly in anomalies:
                    alerts.append({
                        "type": "sensor_anomaly",
                        "severity": "high",
                        "message": f"Anomaly detected: {anomaly['type']} = {anomaly['value']} {anomaly['unit']} at {anomaly['timestamp']}",
                        "data": dict(anomaly)
                    })
                
                return alerts[:limit]
                
        except Exception as e:
            print(f"[FarmReport] ⚠️ Error fetching alerts: {e}")
            return []
    
    async def generate_report(self, farm_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive farm performance report.
        
        Args:
            farm_id: Farm ID
            
        Returns:
            Dict with complete report
        """
        print(f"[FarmReport] 📊 Generating report for farm {farm_id}")
        
        await self.connect_db()
        
        try:
            # Get all data
            farm_info = await self.get_farm_info(farm_id)
            
            if "error" in farm_info:
                return {"error": "Farm not found", "farm_id": farm_id}
            
            dna_score = await self.dna_calculator.calculate_dna_score(farm_id)
            finance = await self.get_finance_summary(farm_id)
            crops = await self.get_crops_summary(farm_id)
            workers = await self.get_workers_summary(farm_id)
            alerts = await self.get_top_alerts(farm_id, limit=5)
            
            # Compile report
            report = {
                "farm_id": farm_id,
                "generated_at": datetime.now().isoformat(),
                "farm_info": farm_info,
                "dna_score": dna_score,
                "finance": finance,
                "crops": crops,
                "workers": workers,
                "alerts": alerts,
                "summary": {
                    "overall_health": dna_score.get("overall_score", 0),
                    "profitability": finance.get("net_profit", 0),
                    "crop_count": crops.get("total", 0),
                    "worker_count": workers.get("total", 0),
                    "alert_count": len(alerts)
                }
            }
            
            print(f"[FarmReport] ✅ Report generated for farm {farm_id}")
            return report
            
        except Exception as e:
            print(f"[FarmReport] ❌ Error generating report: {e}")
            return {"error": str(e), "farm_id": farm_id}
        finally:
            await self.close_db()
    
    async def print_report(self, farm_id: int) -> None:
        """
        Print formatted report to console.
        
        Args:
            farm_id: Farm ID
        """
        report = await self.generate_report(farm_id)
        
        if "error" in report:
            print(f"❌ Error: {report.get('error')}")
            return
        
        print("\n" + "="*70)
        print(f"🌾 CROPMIND - FARM PERFORMANCE REPORT")
        print("="*70)
        
        # Farm Info
        farm = report.get("farm_info", {})
        print(f"\n📋 FARM INFORMATION")
        print("-"*70)
        print(f"  Name: {farm.get('name', 'N/A')}")
        print(f"  Location: {farm.get('location', 'N/A')}")
        print(f"  Area: {farm.get('area', 0)} feddans")
        print(f"  Primary Crop: {farm.get('crop_type', 'N/A')}")
        print(f"  Status: {'Active' if farm.get('is_active') else 'Inactive'}")
        
        # DNA Score
        dna = report.get("dna_score", {})
        print(f"\n🧬 FARM DNA SCORE")
        print("-"*70)
        print(f"  Overall Score: {dna.get('overall_score', 0)}/100")
        print(f"  Status: {dna.get('status', 'N/A')}")
        
        dimensions = dna.get("dimensions", {})
        for dim, data in dimensions.items():
            print(f"  {dim.replace('_', ' ').title()}: {data.get('score', 0)}/100")
        
        # Finance
        finance = report.get("finance", {})
        print(f"\n💰 FINANCE SUMMARY")
        print("-"*70)
        print(f"  Total Income: EGP {finance.get('total_income', 0):,.2f}")
        print(f"  Total Expenses: EGP {finance.get('total_expense', 0):,.2f}")
        print(f"  Net Profit: EGP {finance.get('net_profit', 0):,.2f}")
        
        # Crops
        crops = report.get("crops", {})
        print(f"\n🌱 CROPS SUMMARY")
        print("-"*70)
        print(f"  Total Crops: {crops.get('total', 0)}")
        print(f"  Growing: {crops.get('growing', 0)}")
        print(f"  Harvested: {crops.get('harvested', 0)}")
        print(f"  Failed: {crops.get('failed', 0)}")
        print(f"  Average Health: {crops.get('avg_health', 0):.1f}/100")
        
        # Workers
        workers = report.get("workers", {})
        print(f"\n👥 WORKERS SUMMARY")
        print("-"*70)
        print(f"  Total Workers: {workers.get('total', 0)}")
        print(f"  Active Workers: {workers.get('active', 0)}")
        
        # Alerts
        alerts = report.get("alerts", [])
        print(f"\n🔔 TOP ALERTS")
        print("-"*70)
        if alerts:
            for i, alert in enumerate(alerts[:5], 1):
                print(f"  {i}. {alert.get('message', 'N/A')}")
        else:
            print("  ✅ No alerts")
        
        # Summary
        summary = report.get("summary", {})
        print(f"\n📊 QUICK SUMMARY")
        print("-"*70)
        print(f"  Overall Health: {summary.get('overall_health', 0)}/100")
        print(f"  Profitability: EGP {summary.get('profitability', 0):,.2f}")
        print(f"  Active Crops: {summary.get('crop_count', 0)}")
        print(f"  Active Workers: {summary.get('worker_count', 0)}")
        print(f"  Active Alerts: {summary.get('alert_count', 0)}")
        
        print("\n" + "="*70)
        print(f"Report generated at: {report.get('generated_at', 'N/A')}")
        print("="*70 + "\n")


async def main():
    """
    Main entry point for testing.
    """
    print("="*70)
    print("🌾 CropMind - Farm Performance Report")
    print("="*70)
    
    report_gen = FarmPerformanceReport()
    await report_gen.print_report(1)


if __name__ == "__main__":
    asyncio.run(main())
