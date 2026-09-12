"""
CropMind - ETL Weather Data
ETL pipeline that fetches weather data from OpenWeatherMap API

Author: CropMind Team
Date: 2026
"""

import asyncio
import asyncpg
import aiohttp
from datetime import datetime
from typing import Dict, List, Any, Optional

from backend.app.core.config import settings


class WeatherETL:
    """
    ETL pipeline for fetching and storing weather data.
    Uses OpenWeatherMap API to get current weather for Egyptian cities.
    """
    
    def __init__(self):
        """Initialize the ETL pipeline."""
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.db_pool = None
        
        self.locations = [
            {"name": "الفيوم", "city": "Fayoum", "farm_id": 1},
            {"name": "الإسماعيلية", "city": "Ismailia", "farm_id": 2},
            {"name": "بني سويف", "city": "Beni Suef", "farm_id": 3},
        ]
        
        if not self.api_key:
            print("[ETL Weather Data] ⚠️ WEATHER_API_KEY not configured")
        else:
            print("[ETL Weather Data] ✅ Weather API key loaded")
    
    async def connect_db(self):
        """Create database connection pool."""
        try:
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"),
                min_size=1,
                max_size=5
            )
            print("[ETL Weather Data] ✅ Database connected")
        except Exception as e:
            print(f"[ETL Weather Data] ❌ Database connection error: {e}")
            raise
    
    async def close_db(self):
        """Close database connection pool."""
        if self.db_pool:
            await self.db_pool.close()
            print("[ETL Weather Data] ✅ Database disconnected")
    
    async def fetch_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Fetch weather data from OpenWeatherMap API.
        
        Args:
            city: City name in English
            
        Returns:
            Dict with weather data or None
        """
        if not self.api_key:
            return None
        
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=10) as response:
                    if response.status != 200:
                        print(f"[ETL Weather Data] ⚠️ API error for {city}: {response.status}")
                        return None
                    
                    data = await response.json()
                    
                    return {
                        "temperature": data["main"]["temp"],
                        "humidity": data["main"]["humidity"],
                        "wind_speed": data["wind"]["speed"] * 3.6,  # Convert m/s to km/h
                        "description": data["weather"][0]["description"],
                        "timestamp": datetime.now()
                    }
                    
        except aiohttp.ClientError as e:
            print(f"[ETL Weather Data] ⚠️ Network error for {city}: {e}")
            return None
        except Exception as e:
            print(f"[ETL Weather Data] ⚠️ Error fetching weather for {city}: {e}")
            return None
    
    async def fetch_all_weather(self) -> List[Dict[str, Any]]:
        """
        Fetch weather data for all locations.
        
        Returns:
            List of weather records
        """
        records = []
        
        for location in self.locations:
            print(f"[ETL Weather Data] 🌤️ Fetching weather for {location['name']}...")
            
            weather = await self.fetch_weather(location["city"])
            
            if weather:
                records.append({
                    "farm_id": location["farm_id"],
                    "city": location["name"],
                    "temperature": weather["temperature"],
                    "humidity": weather["humidity"],
                    "wind_speed": weather["wind_speed"],
                    "description": weather["description"],
                    "timestamp": weather["timestamp"]
                })
                print(f"[ETL Weather Data] ✅ {location['name']}: {weather['temperature']}°C, {weather['humidity']}%")
            else:
                print(f"[ETL Weather Data] ⚠️ Failed to fetch weather for {location['name']}")
        
        return records
    
    async def save_to_db(self, records: List[Dict[str, Any]]) -> int:
        """
        Save weather records to sensor_readings table.
        
        Args:
            records: List of weather records
            
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
                        farm_id = record["farm_id"]
                        timestamp = record["timestamp"]
                        city = record["city"]
                        
                        # Insert temperature
                        await conn.execute(
                            """
                            INSERT INTO sensor_readings
                            (farm_id, sensor_id, type, value, unit, is_anomaly, timestamp)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                            """,
                            farm_id,
                            f"weather_{city}",
                            "temperature",
                            record["temperature"],
                            "°C",
                            False,
                            timestamp
                        )
                        
                        # Insert humidity
                        await conn.execute(
                            """
                            INSERT INTO sensor_readings
                            (farm_id, sensor_id, type, value, unit, is_anomaly, timestamp)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                            """,
                            farm_id,
                            f"weather_{city}",
                            "humidity",
                            record["humidity"],
                            "%",
                            False,
                            timestamp
                        )
                        
                        inserted_count += 2
                        
                    except Exception as e:
                        print(f"[ETL Weather Data] ⚠️ Error saving weather for {record.get('city', 'unknown')}: {e}")
                        continue
        
        print(f"[ETL Weather Data] ✅ Saved {inserted_count} weather readings to database")
        return inserted_count
    
    async def run(self) -> Dict[str, Any]:
        """
        Run the full ETL pipeline.
        
        Returns:
            Dict with pipeline results
        """
        print("[ETL Weather Data] 🚀 Starting ETL pipeline...")
        
        try:
            # Fetch weather data
            records = await self.fetch_all_weather()
            
            if not records:
                return {
                    "status": "error",
                    "message": "No weather data fetched",
                    "inserted": 0
                }
            
            # Save to database
            await self.connect_db()
            inserted = await self.save_to_db(records)
            await self.close_db()
            
            return {
                "status": "success",
                "message": f"ETL pipeline completed",
                "fetched": len(records),
                "inserted": inserted,
                "locations": [loc["name"] for loc in self.locations]
            }
            
        except Exception as e:
            print(f"[ETL Weather Data] ❌ Pipeline error: {e}")
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
    print("🌾 CropMind - Weather Data ETL Pipeline")
    print("="*60)
    
    etl = WeatherETL()
    result = await etl.run()
    
    print("\n" + "="*60)
    print("📊 ETL Pipeline Results")
    print("="*60)
    print(f"Status: {result.get('status')}")
    print(f"Message: {result.get('message')}")
    print(f"Fetched: {result.get('fetched', 0)}")
    print(f"Inserted: {result.get('inserted', 0)}")
    print(f"Locations: {result.get('locations', [])}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
