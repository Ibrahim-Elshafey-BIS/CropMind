"""
CropMind - ETL Sensor Data
ETL pipeline that reads sensor data from CSV and loads into database

Author: CropMind Team
Date: 2026
"""

import asyncio
import asyncpg
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional

from backend.app.core.config import settings


class SensorDataETL:
    """
    ETL pipeline for loading sensor data from CSV to database.
    Maps field_id to farm_id and transforms readings to sensor_readings format.
    """
    
    def __init__(self):
        """Initialize the ETL pipeline."""
        self.csv_path = "data/seeds/sensor_data.csv"
        self.db_pool = None
        
        # Field ID to Farm ID mapping
        self.field_mapping = {
            "A": 1,
            "B": 1,
            "C": 2,
            "D": 2,
            "E": 3,
        }
        
        # Sensor types and their units
        self.sensor_types = {
            "temperature": {"unit": "°C", "column": "temperature"},
            "humidity": {"unit": "%", "column": "humidity"},
            "soil_moisture": {"unit": "%", "column": "soil_moisture"},
            "ph": {"unit": "", "column": "ph"},
        }
        
        print("[ETL Sensor Data] ✅ Initialized")
    
    async def connect_db(self):
        """Create database connection pool."""
        try:
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"),
                min_size=1,
                max_size=5
            )
            print("[ETL Sensor Data] ✅ Database connected")
        except Exception as e:
            print(f"[ETL Sensor Data] ❌ Database connection error: {e}")
            raise
    
    async def close_db(self):
        """Close database connection pool."""
        if self.db_pool:
            await self.db_pool.close()
            print("[ETL Sensor Data] ✅ Database disconnected")
    
    def load_csv(self) -> Optional[pd.DataFrame]:
        """
        Load sensor data from CSV file.
        
        Returns:
            DataFrame with sensor data or None
        """
        try:
            df = pd.read_csv(self.csv_path)
            print(f"[ETL Sensor Data] ✅ Loaded {len(df)} rows from {self.csv_path}")
            print(f"[ETL Sensor Data] 📊 Columns: {df.columns.tolist()}")
            return df
        except FileNotFoundError:
            print(f"[ETL Sensor Data] ❌ CSV file not found: {self.csv_path}")
            return None
        except Exception as e:
            print(f"[ETL Sensor Data] ❌ Error loading CSV: {e}")
            return None
    
    def transform_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Transform CSV data to sensor readings format.
        
        Args:
            df: DataFrame with sensor data
            
        Returns:
            List of sensor reading records
        """
        records = []
        
        for _, row in df.iterrows():
            field_id = row.get("field_id", "").strip()
            
            # Skip if field_id not in mapping
            if field_id not in self.field_mapping:
                continue
            
            farm_id = self.field_mapping[field_id]
            timestamp = pd.to_datetime(row.get("timestamp"))
            
            # Convert timestamp to datetime
            if isinstance(timestamp, pd.Timestamp):
                timestamp = timestamp.to_pydatetime()
            
            # Get anomaly flag
            is_anomaly = bool(row.get("label", 0))
            
            # Create reading for each sensor type
            for sensor_type, config in self.sensor_types.items():
                column = config["column"]
                unit = config["unit"]
                
                # Skip if column is missing or value is NaN
                if column not in row or pd.isna(row[column]):
                    continue
                
                value = float(row[column])
                
                # Sensor ID format: sensor_{field_id}_{type}
                sensor_id = f"sensor_{field_id}_{sensor_type}"
                
                records.append({
                    "farm_id": farm_id,
                    "sensor_id": sensor_id,
                    "type": sensor_type,
                    "value": value,
                    "unit": unit,
                    "is_anomaly": is_anomaly,
                    "timestamp": timestamp
                })
        
        print(f"[ETL Sensor Data] 📊 Transformed {len(records)} sensor readings")
        return records
    
    async def save_to_db(self, records: List[Dict[str, Any]]) -> int:
        """
        Save sensor records to database, avoiding duplicates.
        
        Args:
            records: List of sensor reading records
            
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
                            SELECT COUNT(*) FROM sensor_readings
                            WHERE farm_id = $1 
                              AND sensor_id = $2 
                              AND type = $3 
                              AND timestamp = $4
                            """,
                            record["farm_id"],
                            record["sensor_id"],
                            record["type"],
                            record["timestamp"]
                        )
                        
                        if exists > 0:
                            # Update existing record
                            await conn.execute(
                                """
                                UPDATE sensor_readings
                                SET value = $1,
                                    unit = $2,
                                    is_anomaly = $3
                                WHERE farm_id = $4 
                                  AND sensor_id = $5 
                                  AND type = $6 
                                  AND timestamp = $7
                                """,
                                record["value"],
                                record["unit"],
                                record["is_anomaly"],
                                record["farm_id"],
                                record["sensor_id"],
                                record["type"],
                                record["timestamp"]
                            )
                        else:
                            # Insert new record
                            await conn.execute(
                                """
                                INSERT INTO sensor_readings
                                (farm_id, sensor_id, type, value, unit, is_anomaly, timestamp)
                                VALUES ($1, $2, $3, $4, $5, $6, $7)
                                """,
                                record["farm_id"],
                                record["sensor_id"],
                                record["type"],
                                record["value"],
                                record["unit"],
                                record["is_anomaly"],
                                record["timestamp"]
                            )
                        
                        inserted_count += 1
                        
                    except Exception as e:
                        print(f"[ETL Sensor Data] ⚠️ Error saving record: {e}")
                        continue
        
        print(f"[ETL Sensor Data] ✅ Saved {inserted_count} sensor readings to database")
        return inserted_count
    
    async def run(self) -> Dict[str, Any]:
        """
        Run the full ETL pipeline.
        
        Returns:
            Dict with pipeline results
        """
        print("[ETL Sensor Data] 🚀 Starting ETL pipeline...")
        
        try:
            # Load CSV data
            df = self.load_csv()
            
            if df is None or df.empty:
                return {
                    "status": "error",
                    "message": "No data loaded from CSV",
                    "inserted": 0
                }
            
            # Transform data
            records = self.transform_data(df)
            
            if not records:
                return {
                    "status": "error",
                    "message": "No records transformed",
                    "inserted": 0
                }
            
            # Save to database
            await self.connect_db()
            inserted = await self.save_to_db(records)
            await self.close_db()
            
            return {
                "status": "success",
                "message": f"ETL pipeline completed",
                "total_rows": len(df),
                "transformed": len(records),
                "inserted": inserted,
                "field_mapping": self.field_mapping
            }
            
        except Exception as e:
            print(f"[ETL Sensor Data] ❌ Pipeline error: {e}")
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
    print("🌾 CropMind - Sensor Data ETL Pipeline")
    print("="*60)
    
    etl = SensorDataETL()
    result = await etl.run()
    
    print("\n" + "="*60)
    print("📊 ETL Pipeline Results")
    print("="*60)
    print(f"Status: {result.get('status')}")
    print(f"Message: {result.get('message')}")
    print(f"Total rows: {result.get('total_rows', 0)}")
    print(f"Transformed: {result.get('transformed', 0)}")
    print(f"Inserted: {result.get('inserted', 0)}")
    print(f"Field mapping: {result.get('field_mapping', {})}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
