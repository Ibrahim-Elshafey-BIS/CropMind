"""
CropMind - ETL Market Prices
ETL pipeline that generates and stores market price forecasts

Author: CropMind Team
Date: 2026
"""

import asyncio
import asyncpg
from datetime import datetime, timedelta
from typing import List, Dict, Any

from ml_models.price_forecasting.predict import PriceForecaster
from backend.app.core.config import settings


class MarketPriceETL:
    """
    ETL pipeline for generating and storing market price forecasts.
    Uses PriceForecaster to generate daily price predictions.
    """
    
    def __init__(self):
        """Initialize the ETL pipeline."""
        self.forecaster = PriceForecaster()
        self.commodities = ["potato", "wheat", "brinjal", "tomato", "onion"]
        self.db_pool = None
        print("[ETL Market Prices] ✅ Initialized")
    
    async def connect_db(self):
        """Create database connection pool."""
        try:
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"),
                min_size=1,
                max_size=5
            )
            print("[ETL Market Prices] ✅ Database connected")
        except Exception as e:
            print(f"[ETL Market Prices] ❌ Database connection error: {e}")
            raise
    
    async def close_db(self):
        """Close database connection pool."""
        if self.db_pool:
            await self.db_pool.close()
            print("[ETL Market Prices] ✅ Database disconnected")
    
    def generate_forecast_data(self, commodity: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Generate daily forecast data for a commodity.
        
        Args:
            commodity: Commodity name
            days: Number of days to forecast
            
        Returns:
            List of daily forecast records
        """
        try:
            forecast = self.forecaster.forecast_commodity(commodity, days=days)
            
            if not forecast or "weekly_forecast" not in forecast:
                print(f"[ETL Market Prices] ⚠️ No forecast for {commodity}")
                return []
            
            # Get base price
            current_price = forecast.get("current_price", 2000.0)
            
            # Generate daily records
            records = []
            weekly_forecast = forecast.get("weekly_forecast", [])
            
            for i, week_data in enumerate(weekly_forecast):
                # Distribute weekly price across 7 days with slight variation
                base_price = week_data.get("price", current_price)
                
                for day in range(7):
                    date_obj = datetime.now() + timedelta(days=i*7 + day)
                    date_str = date_obj.strftime("%Y-%m-%d")
                    
                    # Add slight daily variation (-2% to +2%)
                    import random
                    daily_variation = random.uniform(0.98, 1.02)
                    price = base_price * daily_variation
                    
                    # Calculate min and max (vary by ±5%)
                    min_price = price * 0.95
                    max_price = price * 1.05
                    
                    records.append({
                        "commodity": commodity,
                        "price": round(price, 2),
                        "min_price": round(min_price, 2),
                        "max_price": round(max_price, 2),
                        "unit": "EGP/ton",
                        "market_name": "CropMind AI Forecast",
                        "date": date_str
                    })
            
            print(f"[ETL Market Prices] ✅ Generated {len(records)} records for {commodity}")
            return records
            
        except Exception as e:
            print(f"[ETL Market Prices] ❌ Error generating forecast for {commodity}: {e}")
            return []
    
    def generate_all_forecasts(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Generate forecasts for all commodities.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            Combined list of all records
        """
        all_records = []
        
        for commodity in self.commodities:
            records = self.generate_forecast_data(commodity, days)
            all_records.extend(records)
        
        print(f"[ETL Market Prices] 📊 Generated {len(all_records)} total records")
        return all_records
    
    async def save_to_db(self, records: List[Dict[str, Any]]) -> int:
        """
        Save forecast records to database, avoiding duplicates.
        
        Args:
            records: List of forecast records
            
        Returns:
            Number of records inserted
        """
        if not records:
            return 0
        
        if not self.db_pool:
            await self.connect_db()
        
        inserted_count = 0
        
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                for record in records:
                    try:
                        # Check if record already exists
                        exists = await conn.fetchval(
                            """
                            SELECT COUNT(*) FROM market_prices
                            WHERE commodity = $1 AND date = $2
                            """,
                            record["commodity"],
                            record["date"]
                        )
                        
                        if exists > 0:
                            # Update existing record
                            await conn.execute(
                                """
                                UPDATE market_prices
                                SET price = $1,
                                    min_price = $2,
                                    max_price = $3,
                                    unit = $4,
                                    market_name = $5
                                WHERE commodity = $6 AND date = $7
                                """,
                                record["price"],
                                record["min_price"],
                                record["max_price"],
                                record["unit"],
                                record["market_name"],
                                record["commodity"],
                                record["date"]
                            )
                        else:
                            # Insert new record
                            await conn.execute(
                                """
                                INSERT INTO market_prices
                                (commodity, price, min_price, max_price, unit, market_name, date)
                                VALUES ($1, $2, $3, $4, $5, $6, $7)
                                """,
                                record["commodity"],
                                record["price"],
                                record["min_price"],
                                record["max_price"],
                                record["unit"],
                                record["market_name"],
                                record["date"]
                            )
                        
                        inserted_count += 1
                        
                    except Exception as e:
                        print(f"[ETL Market Prices] ⚠️ Error saving record: {e}")
                        continue
        
        print(f"[ETL Market Prices] ✅ Saved {inserted_count} records to database")
        return inserted_count
    
    async def run(self, days: int = 30) -> Dict[str, Any]:
        """
        Run the full ETL pipeline.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            Dict with pipeline results
        """
        print("[ETL Market Prices] 🚀 Starting ETL pipeline...")
        
        try:
            # Generate data
            records = self.generate_all_forecasts(days)
            
            if not records:
                return {
                    "status": "error",
                    "message": "No records generated",
                    "inserted": 0
                }
            
            # Save to database
            await self.connect_db()
            inserted = await self.save_to_db(records)
            await self.close_db()
            
            return {
                "status": "success",
                "message": f"ETL pipeline completed",
                "generated": len(records),
                "inserted": inserted,
                "commodities": self.commodities,
                "days": days
            }
            
        except Exception as e:
            print(f"[ETL Market Prices] ❌ Pipeline error: {e}")
            await self.close_db()
            return {
                "status": "error",
                "message": str(e),
                "inserted": 0
            }


async def main():
    """
    Main entry point for the ETL pipeline.
    """
    print("="*60)
    print("🌾 CropMind - Market Prices ETL Pipeline")
    print("="*60)
    
    etl = MarketPriceETL()
    result = await etl.run(days=30)
    
    print("\n" + "="*60)
    print("📊 ETL Pipeline Results")
    print("="*60)
    print(f"Status: {result.get('status')}")
    print(f"Message: {result.get('message')}")
    print(f"Generated: {result.get('generated', 0)}")
    print(f"Inserted: {result.get('inserted', 0)}")
    print(f"Commodities: {result.get('commodities', [])}")
    print(f"Days: {result.get('days', 0)}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
