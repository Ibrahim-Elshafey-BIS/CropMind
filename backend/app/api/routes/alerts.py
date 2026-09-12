"""
CropMind - Alerts Routes
FastAPI routes for generating alerts from existing data

Author: CropMind Team
Date: 2026
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ConfigDict

from app.core.database import get_db
from app.models.inventory_item import InventoryItem
from app.models.sensor_reading import SensorReading
from app.models.crop import Crop
from app.models.farm import Farm


# ============================================
# Schemas
# ============================================

class AlertData(BaseModel):
    """Schema for individual alert data."""
    type: str = Field(..., description="Alert type: low_stock, sensor_anomaly, crop_health")
    severity: str = Field(..., description="Alert severity: low, medium, high, critical")
    message: str = Field(..., description="Alert message")
    data: dict = Field(..., description="Additional alert data")


class AlertResponse(BaseModel):
    """Schema for alert response."""
    alerts: List[AlertData] = Field(..., description="List of alerts")
    total_count: int = Field(..., description="Total number of alerts")
    generated_at: datetime = Field(..., description="Alert generation timestamp")

    model_config = ConfigDict(from_attributes=True)


# ============================================
# Alert Generation Functions
# ============================================

async def get_low_stock_alerts(farm_id: int, db: AsyncSession) -> List[AlertData]:
    """
    Generate alerts for low stock inventory items.
    """
    alerts = []
    
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.farm_id == farm_id)
        .where(InventoryItem.quantity < InventoryItem.min_quantity)
    )
    items = result.scalars().all()
    
    for item in items:
        shortage = item.min_quantity - item.quantity
        severity = "critical" if shortage > item.min_quantity * 0.5 else "high"
        
        alerts.append(
            AlertData(
                type="low_stock",
                severity=severity,
                message=f"Low stock: {item.name} ({item.quantity:.2f} {item.unit} remaining, minimum is {item.min_quantity:.2f} {item.unit})",
                data={
                    "item_id": item.id,
                    "item_name": item.name,
                    "category": item.category,
                    "quantity": item.quantity,
                    "min_quantity": item.min_quantity,
                    "unit": item.unit,
                    "shortage": shortage,
                }
            )
        )
    
    return alerts


async def get_anomaly_alerts(farm_id: int, db: AsyncSession) -> List[AlertData]:
    """
    Generate alerts for anomalous sensor readings in the last 24 hours.
    """
    alerts = []
    
    # Get readings from last 24 hours
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    
    result = await db.execute(
        select(SensorReading)
        .where(SensorReading.farm_id == farm_id)
        .where(SensorReading.is_anomaly == True)
        .where(SensorReading.timestamp >= cutoff_time)
        .order_by(SensorReading.timestamp.desc())
    )
    readings = result.scalars().all()
    
    for reading in readings:
        # Determine severity based on sensor type and value
        severity = "high"
        if reading.type in ["temperature", "soil_moisture"]:
            severity = "critical" if abs(reading.value) > 50 else "high"
        
        alerts.append(
            AlertData(
                type="sensor_anomaly",
                severity=severity,
                message=f"Anomalous sensor reading: {reading.type} = {reading.value} {reading.unit} at {reading.timestamp.strftime('%Y-%m-%d %H:%M')}",
                data={
                    "sensor_reading_id": reading.id,
                    "sensor_id": reading.sensor_id,
                    "type": reading.type,
                    "value": reading.value,
                    "unit": reading.unit,
                    "timestamp": reading.timestamp.isoformat(),
                }
            )
        )
    
    return alerts


async def get_crop_health_alerts(farm_id: int, db: AsyncSession) -> List[AlertData]:
    """
    Generate alerts for crops with low health score.
    """
    alerts = []
    
    result = await db.execute(
        select(Crop)
        .where(Crop.farm_id == farm_id)
        .where(Crop.health_score < 50)
        .where(Crop.status == "growing")
        .order_by(Crop.health_score)
    )
    crops = result.scalars().all()
    
    for crop in crops:
        # Determine severity based on health score
        if crop.health_score < 30:
            severity = "critical"
        elif crop.health_score < 40:
            severity = "high"
        else:
            severity = "medium"
        
        alerts.append(
            AlertData(
                type="crop_health",
                severity=severity,
                message=f"Low health score: {crop.name} ({crop.variety or 'Unknown variety'}) - Health Score: {crop.health_score:.1f}/100",
                data={
                    "crop_id": crop.id,
                    "crop_name": crop.name,
                    "variety": crop.variety,
                    "health_score": crop.health_score,
                    "status": crop.status,
                    "planting_date": crop.planting_date.isoformat(),
                }
            )
        )
    
    return alerts


# ============================================
# Router
# ============================================

router = APIRouter()


# ============================================
# GET /farms/{farm_id} - Get all alerts for a farm
# ============================================

@router.get("/farms/{farm_id}", response_model=AlertResponse)
async def get_farm_alerts(
    farm_id: int,
    include_inventory: bool = Query(default=True, description="Include low stock alerts"),
    include_sensors: bool = Query(default=True, description="Include sensor anomaly alerts"),
    include_crops: bool = Query(default=True, description="Include crop health alerts"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all alerts for a specific farm.
    Alerts include: low stock items, anomalous sensor readings, and crops with low health score.
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
    
    alerts = []
    
    # Get low stock alerts
    if include_inventory:
        stock_alerts = await get_low_stock_alerts(farm_id, db)
        alerts.extend(stock_alerts)
    
    # Get sensor anomaly alerts
    if include_sensors:
        anomaly_alerts = await get_anomaly_alerts(farm_id, db)
        alerts.extend(anomaly_alerts)
    
    # Get crop health alerts
    if include_crops:
        crop_alerts = await get_crop_health_alerts(farm_id, db)
        alerts.extend(crop_alerts)
    
    # Sort alerts by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_alerts = sorted(alerts, key=lambda x: severity_order.get(x.severity, 4))
    
    return AlertResponse(
        alerts=sorted_alerts,
        total_count=len(sorted_alerts),
        generated_at=datetime.utcnow(),
    )
