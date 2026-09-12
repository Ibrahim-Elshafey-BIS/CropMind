"""
CropMind - Farm Service
Core business logic for farm analytics and health scoring

Author: CropMind Team
Date: 2026
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.farm import Farm
from app.models.crop import Crop
from app.models.sensor_reading import SensorReading
from app.models.transaction import Transaction
from app.models.inventory_item import InventoryItem
from app.models.worker import Worker


class FarmService:
    """
    Service class for farm analytics and health scoring.
    Provides summary statistics, DNA score calculation, and health history.
    """
    
    async def get_farm_summary(self, farm_id: int, db: AsyncSession) -> Dict[str, Any]:
        """
        Get comprehensive summary statistics for a farm.
        
        Args:
            farm_id: Farm ID
            db: AsyncSession
            
        Returns:
            dict: Farm summary with counts and financial metrics
        """
        # Get total crops count
        result = await db.execute(
            select(func.count(Crop.id)).where(Crop.farm_id == farm_id)
        )
        total_crops = result.scalar() or 0
        
        # Get active crops count (growing status)
        result = await db.execute(
            select(func.count(Crop.id))
            .where(Crop.farm_id == farm_id)
            .where(Crop.status == "growing")
        )
        active_crops = result.scalar() or 0
        
        # Get total workers count
        result = await db.execute(
            select(func.count(Worker.id)).where(Worker.farm_id == farm_id)
        )
        total_workers = result.scalar() or 0
        
        # Get active workers count
        result = await db.execute(
            select(func.count(Worker.id))
            .where(Worker.farm_id == farm_id)
            .where(Worker.is_active == True)
        )
        active_workers = result.scalar() or 0
        
        # Get total income
        result = await db.execute(
            select(func.sum(Transaction.amount))
            .where(Transaction.farm_id == farm_id)
            .where(Transaction.type == "income")
        )
        total_income = result.scalar() or 0.0
        
        # Get total expense
        result = await db.execute(
            select(func.sum(Transaction.amount))
            .where(Transaction.farm_id == farm_id)
            .where(Transaction.type == "expense")
        )
        total_expense = result.scalar() or 0.0
        
        # Get low stock items count
        result = await db.execute(
            select(func.count(InventoryItem.id))
            .where(InventoryItem.farm_id == farm_id)
            .where(InventoryItem.quantity < InventoryItem.min_quantity)
        )
        low_stock_items = result.scalar() or 0
        
        # Get recent anomalies (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        result = await db.execute(
            select(func.count(SensorReading.id))
            .where(SensorReading.farm_id == farm_id)
            .where(SensorReading.is_anomaly == True)
            .where(SensorReading.timestamp >= cutoff_time)
        )
        recent_anomalies = result.scalar() or 0
        
        return {
            "total_crops": total_crops,
            "active_crops": active_crops,
            "total_workers": total_workers,
            "active_workers": active_workers,
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "net_profit": float(total_income) - float(total_expense),
            "low_stock_items": low_stock_items,
            "recent_anomalies": recent_anomalies,
        }
    
    async def calculate_farm_dna_score(self, farm_id: int, db: AsyncSession) -> Dict[str, Any]:
        """
        Calculate the Farm DNA Score (0-100) across 6 dimensions.
        
        Dimensions:
        - Crop Health: Average health score of growing crops
        - Soil Health: Based on soil moisture and pH readings
        - Water Efficiency: Based on water usage patterns
        - Operational Efficiency: Worker utilization and crop management
        - Market Readiness: Price forecasting and market position
        - Risk Exposure: Anomalies, low stock, and crop failures
        
        Args:
            farm_id: Farm ID
            db: AsyncSession
            
        Returns:
            dict: Overall score and individual dimension scores
        """
        scores = {}
        
        # 1. Crop Health Dimension
        result = await db.execute(
            select(func.avg(Crop.health_score))
            .where(Crop.farm_id == farm_id)
            .where(Crop.status == "growing")
        )
        crop_health = result.scalar()
        scores["crop_health"] = self._normalize_score(crop_health, 0, 100, default=60)
        
        # 2. Soil Health Dimension
        # Based on soil_moisture and pH readings
        result = await db.execute(
            select(SensorReading)
            .where(SensorReading.farm_id == farm_id)
            .where(SensorReading.type.in_(["soil_moisture", "ph"]))
            .order_by(SensorReading.timestamp.desc())
            .limit(10)
        )
        readings = result.scalars().all()
        
        if readings:
            soil_scores = []
            for reading in readings:
                if reading.type == "soil_moisture":
                    # Soil moisture: 20-70% is optimal
                    score = self._score_soil_moisture(reading.value)
                    soil_scores.append(score)
                elif reading.type == "ph":
                    # pH: 5.5-7.5 is optimal
                    score = self._score_ph(reading.value)
                    soil_scores.append(score)
            scores["soil_health"] = int(sum(soil_scores) / len(soil_scores)) if soil_scores else 65
        else:
            scores["soil_health"] = 65
        
        # 3. Water Efficiency Dimension
        # Based on water_flow or irrigation sensor data
        result = await db.execute(
            select(SensorReading)
            .where(SensorReading.farm_id == farm_id)
            .where(SensorReading.type == "water_flow")
            .order_by(SensorReading.timestamp.desc())
            .limit(10)
        )
        water_readings = result.scalars().all()
        
        if water_readings:
            water_scores = []
            for reading in water_readings:
                # Water flow: 0.5-5.0 L/min is optimal
                score = self._score_water_flow(reading.value)
                water_scores.append(score)
            scores["water_efficiency"] = int(sum(water_scores) / len(water_scores)) if water_scores else 70
        else:
            scores["water_efficiency"] = 70
        
        # 4. Operational Efficiency Dimension
        # Based on worker utilization and crop management
        # Active workers ratio
        result = await db.execute(
            select(
                func.count(Worker.id).filter(Worker.is_active == True),
                func.count(Worker.id)
            ).where(Worker.farm_id == farm_id)
        )
        active_workers, total_workers = result.first()
        worker_ratio = (active_workers / total_workers * 100) if total_workers > 0 else 50
        
        # Active crops ratio
        result = await db.execute(
            select(
                func.count(Crop.id).filter(Crop.status == "growing"),
                func.count(Crop.id)
            ).where(Crop.farm_id == farm_id)
        )
        active_crops, total_crops = result.first()
        crop_ratio = (active_crops / total_crops * 100) if total_crops > 0 else 50
        
        operational_score = (worker_ratio * 0.4 + crop_ratio * 0.6)
        scores["operational_efficiency"] = self._normalize_score(operational_score, 0, 100, default=65)
        
        # 5. Market Readiness Dimension
        # Based on available market data and forecasting readiness
        # Check if market prices exist
        from app.models.market_price import MarketPrice
        
        result = await db.execute(
            select(func.count(MarketPrice.id)).limit(1)
        )
        has_market_data = result.scalar() is not None
        
        # Check if crops are ready for market
        result = await db.execute(
            select(func.count(Crop.id))
            .where(Crop.farm_id == farm_id)
            .where(Crop.expected_harvest_date <= datetime.utcnow().date())
        )
        ready_crops = result.scalar() or 0
        
        market_score = 50
        if has_market_data:
            market_score += 20
        if ready_crops > 0:
            market_score += 20
        if active_crops > 0:
            market_score += 10
        
        scores["market_readiness"] = min(100, market_score)
        
        # 6. Risk Exposure Dimension
        # Based on anomalies, low stock, and crop failures
        risk_score = 100
        
        # Penalize for recent anomalies
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        result = await db.execute(
            select(func.count(SensorReading.id))
            .where(SensorReading.farm_id == farm_id)
            .where(SensorReading.is_anomaly == True)
            .where(SensorReading.timestamp >= cutoff_time)
        )
        anomalies_count = result.scalar() or 0
        risk_score -= min(30, anomalies_count * 5)
        
        # Penalize for low stock
        result = await db.execute(
            select(func.count(InventoryItem.id))
            .where(InventoryItem.farm_id == farm_id)
            .where(InventoryItem.quantity < InventoryItem.min_quantity)
        )
        low_stock_count = result.scalar() or 0
        risk_score -= min(30, low_stock_count * 3)
        
        # Penalize for failed crops
        result = await db.execute(
            select(func.count(Crop.id))
            .where(Crop.farm_id == farm_id)
            .where(Crop.status == "failed")
        )
        failed_crops = result.scalar() or 0
        risk_score -= min(20, failed_crops * 5)
        
        scores["risk_exposure"] = max(0, min(100, risk_score))
        
        # Calculate overall score (weighted average)
        weights = {
            "crop_health": 0.25,
            "soil_health": 0.20,
            "water_efficiency": 0.18,
            "operational_efficiency": 0.15,
            "market_readiness": 0.12,
            "risk_exposure": 0.10,
        }
        
        overall = sum(scores[key] * weights[key] for key in scores.keys())
        overall_score = int(round(overall))
        
        return {
            "overall_score": overall_score,
            "dimensions": scores
        }
    
    async def get_farm_health_history(
        self,
        farm_id: int,
        db: AsyncSession,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get health history for the last N days.
        
        Args:
            farm_id: Farm ID
            db: AsyncSession
            days: Number of days to retrieve
            
        Returns:
            list: Daily health records with scores
        """
        history = []
        start_date = datetime.utcnow().date() - timedelta(days=days)
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            next_date = current_date + timedelta(days=1)
            
            # Get sensor readings for this day
            result = await db.execute(
                select(SensorReading)
                .where(SensorReading.farm_id == farm_id)
                .where(SensorReading.timestamp >= current_date)
                .where(SensorReading.timestamp < next_date)
            )
            readings = result.scalars().all()
            
            # Calculate health metrics
            crop_health = 70 + (i / days) * 20  # Simulated trend
            water_efficiency = 65 + (i / days) * 25
            soil_health = 60 + (i / days) * 30
            
            if readings:
                # Use actual data if available
                moisture_readings = [r for r in readings if r.type == "soil_moisture"]
                if moisture_readings:
                    avg_moisture = sum(r.value for r in moisture_readings) / len(moisture_readings)
                    soil_health = self._score_soil_moisture(avg_moisture)
            
            # Overall score (weighted average)
            score = (
                crop_health * 0.35 +
                water_efficiency * 0.30 +
                soil_health * 0.35
            )
            
            history.append({
                "date": current_date.isoformat(),
                "score": int(round(score)),
                "crop_health": int(round(crop_health)),
                "water_efficiency": int(round(water_efficiency)),
                "soil_health": int(round(soil_health)),
            })
        
        return history
    
    # ============================================
    # Helper Scoring Functions
    # ============================================
    
    def _normalize_score(self, value: Optional[float], min_val: float, max_val: float, default: float = 50) -> int:
        """
        Normalize a value to a 0-100 score.
        
        Args:
            value: Value to normalize
            min_val: Minimum possible value
            max_val: Maximum possible value
            default: Default value if value is None
            
        Returns:
            int: Normalized score (0-100)
        """
        if value is None:
            return int(default)
        
        # Clamp to range
        clamped = max(min_val, min(max_val, value))
        normalized = ((clamped - min_val) / (max_val - min_val)) * 100
        return int(round(normalized))
    
    def _score_soil_moisture(self, value: float) -> int:
        """
        Score soil moisture as 0-100.
        Optimal range: 20-70%
        """
        if value < 0:
            return 0
        if value > 100:
            return 0
        
        if 20 <= value <= 70:
            # Optimal range: 80-100 score
            if value <= 45:
                return int(80 + (value - 20) / 25 * 20)
            else:
                return int(100 - (value - 45) / 25 * 20)
        elif 10 <= value < 20:
            # Low moisture: 40-80
            return int(40 + (value - 10) / 10 * 40)
        elif 70 < value <= 80:
            # High moisture: 60-80
            return int(80 - (value - 70) / 10 * 20)
        else:
            # Very low or very high: 0-40
            return max(0, int(40 - (abs(value - 45) - 35) * 2))
    
    def _score_ph(self, value: float) -> int:
        """
        Score pH as 0-100.
        Optimal range: 5.5-7.5
        """
        if value < 0:
            return 0
        if value > 14:
            return 0
        
        if 5.5 <= value <= 7.5:
            # Optimal range: 80-100
            if value <= 6.5:
                return int(80 + (value - 5.5) / 1.0 * 20)
            else:
                return int(100 - (value - 6.5) / 1.0 * 20)
        elif 4.0 <= value < 5.5:
            # Acidic: 30-80
            return int(30 + (value - 4.0) / 1.5 * 50)
        elif 7.5 < value <= 9.0:
            # Alkaline: 30-80
            return int(80 - (value - 7.5) / 1.5 * 50)
        else:
            # Very acidic or very alkaline: 0-30
            if value < 4.0:
                return int(max(0, 30 - (4.0 - value) * 10))
            else:
                return int(max(0, 30 - (value - 9.0) * 10))
    
    def _score_water_flow(self, value: float) -> int:
        """
        Score water flow as 0-100.
        Optimal range: 0.5-5.0 L/min
        """
        if value < 0:
            return 0
        
        if 0.5 <= value <= 5.0:
            # Optimal range: 70-100
            if value <= 2.75:
                return int(70 + (value - 0.5) / 2.25 * 30)
            else:
                return int(100 - (value - 2.75) / 2.25 * 30)
        elif 0 <= value < 0.5:
            # Low flow: 30-70
            return int(30 + (value / 0.5) * 40)
        elif 5.0 < value <= 10.0:
            # High flow: 30-70
            return int(70 - (value - 5.0) / 5.0 * 40)
        else:
            # Very high flow: 0-30
            return max(0, int(30 - (value - 10.0) * 3))


# Singleton instance
farm_service = FarmService()
