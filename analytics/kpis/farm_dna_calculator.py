"""
CropMind - Farm DNA Calculator
Calculates Farm DNA Score from 6 dimensions using database data

Author: CropMind Team
Date: 2026
"""

import asyncio
import asyncpg
from typing import Dict, Any, Optional

from backend.app.core.config import settings


class FarmDNACalculator:
    """
    Farm DNA Score calculator using 6 dimensions:
    - Crop Health (22%)
    - Soil Health (20%)
    - Water Efficiency (18%)
    - Operational Efficiency (15%)
    - Market Readiness (13%)
    - Risk Exposure (12%)
    """
    
    def __init__(self):
        """Initialize the Farm DNA Calculator."""
        self.db_pool = None
        
        # Dimension weights
        self.weights = {
            "crop_health": 0.22,
            "soil_health": 0.20,
            "water_efficiency": 0.18,
            "operational_efficiency": 0.15,
            "market_readiness": 0.13,
            "risk_exposure": 0.12,
        }
        
        print("[FarmDNA] ✅ Initialized")
    
    async def connect_db(self):
        """Create database connection pool."""
        try:
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"),
                min_size=1,
                max_size=5
            )
            print("[FarmDNA] ✅ Database connected")
        except Exception as e:
            print(f"[FarmDNA] ❌ Database connection error: {e}")
            raise
    
    async def close_db(self):
        """Close database connection pool."""
        if self.db_pool:
            await self.db_pool.close()
            print("[FarmDNA] ✅ Database disconnected")
    
    async def calculate_crop_health(self, farm_id: int) -> float:
        """
        Calculate Crop Health dimension (0-100).
        Based on average health_score of growing crops.
        """
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.fetchval(
                    """
                    SELECT COALESCE(AVG(health_score), 0)
                    FROM crops
                    WHERE farm_id = $1 AND status = 'growing'
                    """,
                    farm_id
                )
                return float(result) if result else 60.0
        except Exception as e:
            print(f"[FarmDNA] ⚠️ Error calculating crop health: {e}")
            return 60.0
    
    async def calculate_soil_health(self, farm_id: int) -> float:
        """
        Calculate Soil Health dimension (0-100).
        Based on latest soil_moisture and pH readings.
        """
        try:
            async with self.db_pool.acquire() as conn:
                # Get latest soil moisture
                moisture = await conn.fetchval(
                    """
                    SELECT value FROM sensor_readings
                    WHERE farm_id = $1 AND type = 'soil_moisture'
                    ORDER BY timestamp DESC LIMIT 1
                    """,
                    farm_id
                )
                
                # Get latest pH
                ph = await conn.fetchval(
                    """
                    SELECT value FROM sensor_readings
                    WHERE farm_id = $1 AND type = 'ph'
                    ORDER BY timestamp DESC LIMIT 1
                    """,
                    farm_id
                )
                
                # Score soil moisture (optimal: 20-70%)
                moisture_score = 50.0
                if moisture is not None:
                    if 20 <= moisture <= 70:
                        moisture_score = 80 + (30 * (1 - abs(moisture - 45) / 25))
                    elif 10 <= moisture < 20:
                        moisture_score = 40 + (40 * (moisture - 10) / 10)
                    elif 70 < moisture <= 80:
                        moisture_score = 80 - (20 * (moisture - 70) / 10)
                    else:
                        moisture_score = max(0, 40 - (abs(moisture - 45) - 35) * 2)
                
                # Score pH (optimal: 5.5-7.5)
                ph_score = 50.0
                if ph is not None:
                    if 5.5 <= ph <= 7.5:
                        ph_score = 80 + (20 * (1 - abs(ph - 6.5) / 1.0))
                    elif 4.0 <= ph < 5.5:
                        ph_score = 30 + (50 * (ph - 4.0) / 1.5)
                    elif 7.5 < ph <= 9.0:
                        ph_score = 80 - (50 * (ph - 7.5) / 1.5)
                    else:
                        ph_score = max(0, 30 - (abs(ph - 6.5) - 2.5) * 10)
                
                # Weighted average: 60% moisture, 40% pH
                return (moisture_score * 0.6 + ph_score * 0.4)
                
        except Exception as e:
            print(f"[FarmDNA] ⚠️ Error calculating soil health: {e}")
            return 65.0
    
    async def calculate_water_efficiency(self, farm_id: int) -> float:
        """
        Calculate Water Efficiency dimension (0-100).
        Based on humidity readings and irrigation efficiency.
        """
        try:
            async with self.db_pool.acquire() as conn:
                # Get latest humidity
                humidity = await conn.fetchval(
                    """
                    SELECT value FROM sensor_readings
                    WHERE farm_id = $1 AND type = 'humidity'
                    ORDER BY timestamp DESC LIMIT 1
                    """,
                    farm_id
                )
                
                # Score humidity (optimal: 40-80%)
                score = 50.0
                if humidity is not None:
                    if 40 <= humidity <= 80:
                        score = 80 + (20 * (1 - abs(humidity - 60) / 20))
                    elif 20 <= humidity < 40:
                        score = 40 + (40 * (humidity - 20) / 20)
                    elif 80 < humidity <= 90:
                        score = 80 - (40 * (humidity - 80) / 10)
                    else:
                        score = max(0, 40 - (abs(humidity - 60) - 30) * 2)
                
                return score
                
        except Exception as e:
            print(f"[FarmDNA] ⚠️ Error calculating water efficiency: {e}")
            return 70.0
    
    async def calculate_operational_efficiency(self, farm_id: int) -> float:
        """
        Calculate Operational Efficiency dimension (0-100).
        Based on worker utilization and crop management.
        """
        try:
            async with self.db_pool.acquire() as conn:
                # Get worker stats
                worker_stats = await conn.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_workers,
                        COUNT(*) FILTER (WHERE is_active = true) as active_workers
                    FROM workers
                    WHERE farm_id = $1
                    """,
                    farm_id
                )
                
                # Get crop completion rate
                crop_stats = await conn.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_crops,
                        COUNT(*) FILTER (WHERE status IN ('harvested', 'growing')) as active_crops
                    FROM crops
                    WHERE farm_id = $1
                    """,
                    farm_id
                )
                
                total_workers = worker_stats.get('total_workers', 0)
                active_workers = worker_stats.get('active_workers', 0)
                total_crops = crop_stats.get('total_crops', 0)
                active_crops = crop_stats.get('active_crops', 0)
                
                # Worker utilization
                worker_utilization = (active_workers / total_workers * 100) if total_workers > 0 else 50.0
                
                # Crop management
                crop_management = (active_crops / total_crops * 100) if total_crops > 0 else 50.0
                
                # Weighted average: 40% worker utilization, 60% crop management
                return min(100, worker_utilization * 0.4 + crop_management * 0.6)
                
        except Exception as e:
            print(f"[FarmDNA] ⚠️ Error calculating operational efficiency: {e}")
            return 65.0
    
    async def calculate_market_readiness(self, farm_id: int) -> float:
        """
        Calculate Market Readiness dimension (0-100).
        Based on market price data and crop marketability.
        """
        try:
            async with self.db_pool.acquire() as conn:
                # Get crop type from farm
                crop_type = await conn.fetchval(
                    """
                    SELECT crop_type FROM farms WHERE id = $1
                    """,
                    farm_id
                )
                
                # Get market price for the crop
                market_price = 0.0
                if crop_type:
                    market_price_data = await conn.fetchval(
                        """
                        SELECT price FROM market_prices
                        WHERE commodity ILIKE $1
                        ORDER BY date DESC LIMIT 1
                        """,
                        f"%{crop_type}%"
                    )
                    if market_price_data:
                        market_price = float(market_price_data)
                
                # Get crops ready for market
                ready_crops = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM crops
                    WHERE farm_id = $1 
                    AND status = 'growing'
                    """,
                    farm_id
                )
                
                # Score based on market data availability
                market_score = 30.0
                if market_price > 0:
                    market_score += 40
                if ready_crops > 0:
                    market_score += 30
                
                return min(100, market_score)
                
        except Exception as e:
            print(f"[FarmDNA] ⚠️ Error calculating market readiness: {e}")
            return 50.0
    
    async def calculate_risk_exposure(self, farm_id: int) -> float:
        """
        Calculate Risk Exposure dimension (0-100).
        Higher score = lower risk.
        """
        try:
            async with self.db_pool.acquire() as conn:
                # Get recent anomalies
                anomalies = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM sensor_readings
                    WHERE farm_id = $1 AND is_anomaly = true
                    AND timestamp >= NOW() - INTERVAL '24 hours'
                    """,
                    farm_id
                )
                
                # Get low stock items
                low_stock = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM inventory_items
                    WHERE farm_id = $1 AND quantity < min_quantity
                    """,
                    farm_id
                )
                
                # Get failed crops
                failed_crops = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM crops
                    WHERE farm_id = $1 AND status = 'failed'
                    """,
                    farm_id
                )
                
                # Start with perfect score
                score = 100.0
                
                # Penalize anomalies (up to 30 points)
                score -= min(30, anomalies * 5)
                
                # Penalize low stock (up to 30 points)
                score -= min(30, low_stock * 3)
                
                # Penalize failed crops (up to 20 points)
                score -= min(20, failed_crops * 5)
                
                return max(0, min(100, score))
                
        except Exception as e:
            print(f"[FarmDNA] ⚠️ Error calculating risk exposure: {e}")
            return 80.0
    
    async def calculate_dna_score(self, farm_id: int) -> Dict[str, Any]:
        """
        Calculate overall Farm DNA Score with all dimensions.
        
        Returns:
            Dict with overall_score and dimension breakdown
        """
        print(f"[FarmDNA] 🧬 Calculating DNA score for farm {farm_id}")
        
        await self.connect_db()
        
        try:
            # Calculate all dimensions
            crop_health = await self.calculate_crop_health(farm_id)
            soil_health = await self.calculate_soil_health(farm_id)
            water_efficiency = await self.calculate_water_efficiency(farm_id)
            operational_efficiency = await self.calculate_operational_efficiency(farm_id)
            market_readiness = await self.calculate_market_readiness(farm_id)
            risk_exposure = await self.calculate_risk_exposure(farm_id)
            
            # Round scores
            crop_health = round(crop_health, 1)
            soil_health = round(soil_health, 1)
            water_efficiency = round(water_efficiency, 1)
            operational_efficiency = round(operational_efficiency, 1)
            market_readiness = round(market_readiness, 1)
            risk_exposure = round(risk_exposure, 1)
            
            # Calculate overall score (weighted average)
            overall = (
                crop_health * self.weights["crop_health"] +
                soil_health * self.weights["soil_health"] +
                water_efficiency * self.weights["water_efficiency"] +
                operational_efficiency * self.weights["operational_efficiency"] +
                market_readiness * self.weights["market_readiness"] +
                risk_exposure * self.weights["risk_exposure"]
            )
            overall = round(overall, 1)
            
            # Determine status
            if overall >= 80:
                status = "Excellent"
            elif overall >= 60:
                status = "Good"
            elif overall >= 40:
                status = "Fair"
            elif overall >= 20:
                status = "Poor"
            else:
                status = "Critical"
            
            result = {
                "farm_id": farm_id,
                "overall_score": overall,
                "status": status,
                "dimensions": {
                    "crop_health": {
                        "score": crop_health,
                        "weight": self.weights["crop_health"],
                        "weighted_score": round(crop_health * self.weights["crop_health"], 1)
                    },
                    "soil_health": {
                        "score": soil_health,
                        "weight": self.weights["soil_health"],
                        "weighted_score": round(soil_health * self.weights["soil_health"], 1)
                    },
                    "water_efficiency": {
                        "score": water_efficiency,
                        "weight": self.weights["water_efficiency"],
                        "weighted_score": round(water_efficiency * self.weights["water_efficiency"], 1)
                    },
                    "operational_efficiency": {
                        "score": operational_efficiency,
                        "weight": self.weights["operational_efficiency"],
                        "weighted_score": round(operational_efficiency * self.weights["operational_efficiency"], 1)
                    },
                    "market_readiness": {
                        "score": market_readiness,
                        "weight": self.weights["market_readiness"],
                        "weighted_score": round(market_readiness * self.weights["market_readiness"], 1)
                    },
                    "risk_exposure": {
                        "score": risk_exposure,
                        "weight": self.weights["risk_exposure"],
                        "weighted_score": round(risk_exposure * self.weights["risk_exposure"], 1)
                    }
                }
            }
            
            print(f"[FarmDNA] ✅ DNA Score: {overall} ({status})")
            return result
            
        except Exception as e:
            print(f"[FarmDNA] ❌ Error calculating DNA score: {e}")
            return {
                "farm_id": farm_id,
                "overall_score": 0,
                "status": "Error",
                "error": str(e)
            }
        finally:
            await self.close_db()


async def main():
    """
    Main entry point for testing.
    """
    print("="*60)
    print("🧬 CropMind - Farm DNA Calculator")
    print("="*60)
    
    calculator = FarmDNACalculator()
    result = await calculator.calculate_dna_score(1)
    
    print("\n" + "="*60)
    print("📊 Farm DNA Score Results")
    print("="*60)
    print(f"Farm ID: {result.get('farm_id')}")
    print(f"Overall Score: {result.get('overall_score')}/100")
    print(f"Status: {result.get('status')}")
    print("\nDimensions:")
    
    for dim, data in result.get("dimensions", {}).items():
        print(f"  {dim.replace('_', ' ').title()}: {data.get('score')} (weight: {data.get('weight')})")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
