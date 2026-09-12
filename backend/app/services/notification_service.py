"""
CropMind - Notification Service
Handles real-time notifications via WebSocket

Author: CropMind Team
Date: 2026
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.api.websockets.realtime import manager


class NotificationService:
    """
    Service class for sending real-time notifications via WebSocket.
    Provides formatted messages for alerts, sensor updates, and system status.
    """
    
    async def send_alert(
        self,
        farm_id: int,
        severity: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Send an alert to all WebSocket connections for a farm.
        
        Args:
            farm_id: Farm ID
            severity: Alert severity (low, medium, high, critical)
            message: Alert message
            data: Additional alert data
            
        Returns:
            int: Number of connections that received the alert
        """
        payload = {
            "type": "alert",
            "farm_id": farm_id,
            "severity": severity,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        return await manager.send_to_farm(farm_id, payload)
    
    async def send_sensor_update(
        self,
        farm_id: int,
        sensor_data: Dict[str, Any]
    ) -> int:
        """
        Send a sensor update to all WebSocket connections for a farm.
        
        Args:
            farm_id: Farm ID
            sensor_data: Sensor data dictionary
            
        Returns:
            int: Number of connections that received the update
        """
        payload = {
            "type": "sensor_update",
            "farm_id": farm_id,
            "data": sensor_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await manager.send_to_farm(farm_id, payload)
    
    async def send_agent_insight(
        self,
        farm_id: int,
        agent: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Send an agent insight to all WebSocket connections for a farm.
        
        Args:
            farm_id: Farm ID
            agent: Agent name (e.g., "Market Intelligence", "Farm Intelligence")
            message: Insight message
            data: Additional insight data
            
        Returns:
            int: Number of connections that received the insight
        """
        payload = {
            "type": "agent_insight",
            "farm_id": farm_id,
            "agent": agent,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        return await manager.send_to_farm(farm_id, payload)
    
    async def send_low_stock_alert(
        self,
        farm_id: int,
        item_name: str,
        quantity: float,
        min_quantity: float,
        unit: str
    ) -> int:
        """
        Send a formatted low stock alert.
        
        Args:
            farm_id: Farm ID
            item_name: Inventory item name
            quantity: Current quantity
            min_quantity: Minimum required quantity
            unit: Unit of measurement
            
        Returns:
            int: Number of connections that received the alert
        """
        shortage = min_quantity - quantity
        severity = "critical" if shortage > min_quantity * 0.5 else "high"
        
        message = (
            f"⚠️ Low stock alert: {item_name} "
            f"({quantity:.1f} {unit} remaining, "
            f"minimum is {min_quantity:.1f} {unit})"
        )
        
        data = {
            "item_name": item_name,
            "quantity": quantity,
            "min_quantity": min_quantity,
            "unit": unit,
            "shortage": shortage,
            "type": "low_stock"
        }
        
        return await self.send_alert(farm_id, severity, message, data)
    
    async def send_anomaly_alert(
        self,
        farm_id: int,
        sensor_type: str,
        value: float,
        unit: str
    ) -> int:
        """
        Send a formatted sensor anomaly alert.
        
        Args:
            farm_id: Farm ID
            sensor_type: Type of sensor (temperature, humidity, soil_moisture, ph)
            value: Sensor value
            unit: Unit of measurement
            
        Returns:
            int: Number of connections that received the alert
        """
        severity = "critical" if abs(value) > 50 else "high"
        
        message = (
            f"🔴 Anomaly detected: {sensor_type} = {value:.1f} {unit}"
        )
        
        data = {
            "sensor_type": sensor_type,
            "value": value,
            "unit": unit,
            "type": "anomaly"
        }
        
        return await self.send_alert(farm_id, severity, message, data)
    
    async def send_crop_health_alert(
        self,
        farm_id: int,
        crop_name: str,
        health_score: float
    ) -> int:
        """
        Send a formatted crop health alert.
        
        Args:
            farm_id: Farm ID
            crop_name: Crop name
            health_score: Health score (0-100)
            
        Returns:
            int: Number of connections that received the alert
        """
        if health_score >= 50:
            return 0  # No alert needed
        
        if health_score < 30:
            severity = "critical"
        elif health_score < 40:
            severity = "high"
        else:
            severity = "medium"
        
        message = (
            f"🌱 Crop health alert: {crop_name} "
            f"health score is {health_score:.1f}/100"
        )
        
        data = {
            "crop_name": crop_name,
            "health_score": health_score,
            "type": "crop_health"
        }
        
        return await self.send_alert(farm_id, severity, message, data)
    
    async def broadcast_system_status(
        self,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Broadcast system status to all connected clients.
        
        Args:
            status: System status (online, maintenance, error)
            details: Additional details
            
        Returns:
            int: Number of connections that received the broadcast
        """
        payload = {
            "type": "system_status",
            "status": status,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        return await manager.broadcast(payload)
    
    async def send_weather_update(
        self,
        farm_id: int,
        weather_data: Dict[str, Any]
    ) -> int:
        """
        Send a weather update to a farm.
        
        Args:
            farm_id: Farm ID
            weather_data: Weather data dictionary
            
        Returns:
            int: Number of connections that received the update
        """
        payload = {
            "type": "weather_update",
            "farm_id": farm_id,
            "data": weather_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await manager.send_to_farm(farm_id, payload)
    
    async def send_farm_dna_update(
        self,
        farm_id: int,
        dna_data: Dict[str, Any]
    ) -> int:
        """
        Send Farm DNA Score update to a farm.
        
        Args:
            farm_id: Farm ID
            dna_data: DNA score data
            
        Returns:
            int: Number of connections that received the update
        """
        payload = {
            "type": "farm_dna_update",
            "farm_id": farm_id,
            "data": dna_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await manager.send_to_farm(farm_id, payload)
    
    async def send_forecast_update(
        self,
        farm_id: int,
        forecast_data: Dict[str, Any]
    ) -> int:
        """
        Send a price/production forecast update to a farm.
        
        Args:
            farm_id: Farm ID
            forecast_data: Forecast data
            
        Returns:
            int: Number of connections that received the update
        """
        payload = {
            "type": "forecast_update",
            "farm_id": farm_id,
            "data": forecast_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await manager.send_to_farm(farm_id, payload)
    
    async def send_task_update(
        self,
        farm_id: int,
        task_data: Dict[str, Any]
    ) -> int:
        """
        Send a task/worker update to a farm.
        
        Args:
            farm_id: Farm ID
            task_data: Task data
            
        Returns:
            int: Number of connections that received the update
        """
        payload = {
            "type": "task_update",
            "farm_id": farm_id,
            "data": task_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await manager.send_to_farm(farm_id, payload)


# Singleton instance
notification_service = NotificationService()
