"""
CropMind - Alert Tool
Standalone utility for building, classifying, and prioritizing alerts

Author: CropMind Team
Date: 2026
"""

from datetime import datetime
from typing import Dict, Any, List, Optional


class AlertTool:
    """
    Alert building and classification utility for agents.
    Does NOT send WebSocket messages - only builds alert payloads.
    """
    
    def __init__(self):
        """Initialize the AlertTool with severity thresholds."""
        self.thresholds = {
            "temperature": {"min": 10, "max": 40},
            "humidity": {"min": 20, "max": 90},
            "soil_moisture": {"min": 20, "max": 80},
            "ph": {"min": 5.0, "max": 8.0},
        }
        print("[AlertTool] ✅ Initialized")
    
    def create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        farm_id: int,
        data: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """
        Create a standardized alert payload.
        
        Args:
            alert_type: Type of alert (sensor_anomaly, low_stock, etc.)
            severity: low, medium, high, critical
            message: Alert message
            farm_id: Farm ID
            data: Additional alert data
            
        Returns:
            Dict with alert payload
        """
        timestamp_ms = int(datetime.now().timestamp() * 1000)
        
        return {
            "alert_id": f"alert_{farm_id}_{timestamp_ms}",
            "farm_id": farm_id,
            "type": alert_type,
            "severity": severity,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "is_read": False,
            "requires_action": severity in ["high", "critical"]
        }
    
    def check_sensor_alerts(
        self,
        farm_id: int,
        sensor_data: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Check sensor readings against thresholds and generate alerts.
        
        Args:
            farm_id: Farm ID
            sensor_data: Dict with sensor readings
            
        Returns:
            List of alert dicts
        """
        alerts = []
        
        if not sensor_data:
            return alerts
        
        for sensor_type, value in sensor_data.items():
            if value is None:
                continue
            
            if sensor_type not in self.thresholds:
                continue
            
            threshold = self.thresholds[sensor_type]
            min_val = threshold["min"]
            max_val = threshold["max"]
            
            # Check if value is outside range
            if value < min_val:
                diff_percent = (min_val - value) / min_val * 100
                
                if diff_percent > 20:
                    severity = "critical"
                elif diff_percent > 10:
                    severity = "high"
                else:
                    severity = "medium"
                
                message = f"⚠️ {self._get_sensor_name(sensor_type)} منخفضة جداً: {value:.1f} (الحد الأدنى {min_val})"
                
                alerts.append(self.create_alert(
                    alert_type="sensor_anomaly",
                    severity=severity,
                    message=message,
                    farm_id=farm_id,
                    data={
                        "sensor_type": sensor_type,
                        "value": value,
                        "threshold_min": min_val,
                        "threshold_max": max_val,
                        "direction": "below"
                    }
                ))
                
            elif value > max_val:
                diff_percent = (value - max_val) / max_val * 100
                
                if diff_percent > 20:
                    severity = "critical"
                elif diff_percent > 10:
                    severity = "high"
                else:
                    severity = "medium"
                
                message = f"⚠️ {self._get_sensor_name(sensor_type)} مرتفعة جداً: {value:.1f} (الحد الأقصى {max_val})"
                
                alerts.append(self.create_alert(
                    alert_type="sensor_anomaly",
                    severity=severity,
                    message=message,
                    farm_id=farm_id,
                    data={
                        "sensor_type": sensor_type,
                        "value": value,
                        "threshold_min": min_val,
                        "threshold_max": max_val,
                        "direction": "above"
                    }
                ))
        
        return alerts
    
    def _get_sensor_name(self, sensor_type: str) -> str:
        """Get Arabic name for sensor type."""
        names = {
            "temperature": "درجة الحرارة",
            "humidity": "الرطوبة",
            "soil_moisture": "رطوبة التربة",
            "ph": "درجة الحموضة"
        }
        return names.get(sensor_type, sensor_type)
    
    def check_inventory_alerts(
        self,
        farm_id: int,
        inventory: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Check inventory items against minimum thresholds and generate alerts.
        
        Args:
            farm_id: Farm ID
            inventory: List of inventory items
            
        Returns:
            List of alert dicts
        """
        alerts = []
        
        if not inventory:
            return alerts
        
        for item in inventory:
            quantity = item.get("quantity", 0)
            min_threshold = item.get("min_threshold", 0)
            item_name = item.get("item_name", "Unknown")
            unit = item.get("unit", "piece")
            
            if quantity <= min_threshold:
                # Determine severity
                if quantity == 0:
                    severity = "critical"
                elif quantity <= min_threshold * 0.5:
                    severity = "high"
                else:
                    severity = "medium"
                
                message = f"📦 مخزون {item_name} منخفض: {quantity} {unit} (الحد الأدنى {min_threshold} {unit})"
                
                alerts.append(self.create_alert(
                    alert_type="low_stock",
                    severity=severity,
                    message=message,
                    farm_id=farm_id,
                    data={
                        "item_name": item_name,
                        "quantity": quantity,
                        "min_threshold": min_threshold,
                        "unit": unit
                    }
                ))
        
        return alerts
    
    def check_crop_health_alert(
        self,
        farm_id: int,
        crop_name: str,
        health_score: float
    ) -> Optional[Dict[str, Any]]:
        """
        Check crop health score and generate alert if needed.
        
        Args:
            farm_id: Farm ID
            crop_name: Name of the crop
            health_score: Health score (0-100)
            
        Returns:
            Alert dict or None
        """
        if health_score >= 50:
            return None
        
        # Determine severity
        if health_score < 30:
            severity = "critical"
        elif health_score < 40:
            severity = "high"
        else:
            severity = "medium"
        
        message = f"🌱 صحة محصول {crop_name}: {health_score:.1f}/100"
        
        return self.create_alert(
            alert_type="crop_health",
            severity=severity,
            message=message,
            farm_id=farm_id,
            data={
                "crop_name": crop_name,
                "health_score": health_score
            }
        )
    
    def check_disease_alert(
        self,
        farm_id: int,
        disease_name: str,
        confidence: float,
        crop_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check disease detection and generate alert if confidence is high.
        
        Args:
            farm_id: Farm ID
            disease_name: Name of the detected disease
            confidence: Detection confidence (0-100)
            crop_name: Name of the affected crop
            
        Returns:
            Alert dict or None
        """
        if confidence < 50:
            return None
        
        # Determine severity
        if confidence >= 85:
            severity = "critical"
        elif confidence >= 70:
            severity = "high"
        else:
            severity = "medium"
        
        message = f"🦠 تم اكتشاف {disease_name} في {crop_name} بثقة {confidence:.0f}%"
        
        return self.create_alert(
            alert_type="disease_detected",
            severity=severity,
            message=message,
            farm_id=farm_id,
            data={
                "disease_name": disease_name,
                "confidence": confidence,
                "crop_name": crop_name
            }
        )
    
    def prioritize_alerts(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort alerts by severity and timestamp.
        
        Args:
            alerts: List of alert dicts
            
        Returns:
            Sorted list of alerts
        """
        if not alerts:
            return alerts
        
        severity_order = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3
        }
        
        # Sort by severity (critical first) and then by timestamp (newest first)
        def sort_key(alert):
            severity_value = severity_order.get(alert.get("severity", "low"), 3)
            timestamp_str = alert.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(timestamp_str)
                timestamp_value = -ts.timestamp()  # negative = newest first
            except (ValueError, TypeError):
                timestamp_value = 0
            return (severity_value, timestamp_value)
            
        return sorted(alerts, key=sort_key)
    
    def get_alert_summary(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of alerts.
        
        Args:
            alerts: List of alert dicts
            
        Returns:
            Dict with alert summary
        """
        if not alerts:
            return {
                "total": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "requires_action": 0,
                "top_alert": None
            }
        
        # Prioritize alerts
        prioritized = self.prioritize_alerts(alerts)
        
        # Count by severity
        critical = sum(1 for a in alerts if a.get("severity") == "critical")
        high = sum(1 for a in alerts if a.get("severity") == "high")
        medium = sum(1 for a in alerts if a.get("severity") == "medium")
        low = sum(1 for a in alerts if a.get("severity") == "low")
        requires_action = sum(1 for a in alerts if a.get("requires_action", False))
        
        return {
            "total": len(alerts),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "requires_action": requires_action,
            "top_alert": prioritized[0] if prioritized else None
        }
