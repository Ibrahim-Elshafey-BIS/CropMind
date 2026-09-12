"""
CropMind - DB Query Tool
Standalone utility for data transformation and validation
Used by agents to format raw data from database

Author: CropMind Team
Date: 2026
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class DBQueryTool:
    """
    Data transformation and validation utility for agents.
    Does NOT perform DB queries - only formats raw data for agents.
    """
    
    def __init__(self):
        """Initialize the DBQueryTool."""
        print("[DBQueryTool] ✅ Initialized")
    
    def format_sensor_data(self, raw_readings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format raw sensor readings into a dict for FarmIntelligenceAgent.
        
        Args:
            raw_readings: List of dicts with type, value, timestamp
            
        Returns:
            Dict with sensor_data containing all required fields
        """
        # Initialize with placeholders
        sensor_data = {
            "temperature": None,
            "humidity": None,
            "soil_moisture": None,
            "ph": None,
            # Note: N, P, K, rainfall are placeholders
            # These are not from real sensors - they will be replaced by actual soil sensors
            "N": 45.0,
            "P": 30.0,
            "K": 60.0,
            "rainfall": 5.0
        }
        
        # Group readings by type and find the latest
        latest_by_type = {}
        for reading in raw_readings:
            sensor_type = reading.get("type")
            value = reading.get("value")
            timestamp = reading.get("timestamp")
            
            if sensor_type not in ["temperature", "humidity", "soil_moisture", "ph"]:
                continue
            
            if value is None:
                continue
            
            # Update if newer
            if sensor_type not in latest_by_type:
                latest_by_type[sensor_type] = reading
            else:
                existing_ts = latest_by_type[sensor_type].get("timestamp")
                if timestamp and existing_ts:
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    if isinstance(existing_ts, str):
                        existing_ts = datetime.fromisoformat(existing_ts.replace('Z', '+00:00'))
                    if timestamp > existing_ts:
                        latest_by_type[sensor_type] = reading
        
        # Fill sensor_data with latest values
        for sensor_type, reading in latest_by_type.items():
            sensor_data[sensor_type] = reading.get("value")
        
        return sensor_data
    
    def format_inventory_items(self, raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format raw inventory items for InventoryAgent.
        
        Args:
            raw_items: List of dicts from InventoryItem model
            
        Returns:
            List of formatted inventory items
        """
        formatted_items = []
        
        for item in raw_items:
            formatted_items.append({
                "item_name": item.get("name", ""),
                "quantity": item.get("quantity", 0.0),
                "unit": item.get("unit", "piece"),
                "min_threshold": item.get("min_quantity", 0.0),
                "cost_per_unit": item.get("price_per_unit", 0.0)
            })
        
        return formatted_items
    
    def format_workers(self, raw_workers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format raw workers for WorkforceAgent.
        
        Args:
            raw_workers: List of dicts from Worker model
            
        Returns:
            List of formatted workers
        """
        formatted_workers = []
        
        for worker in raw_workers:
            is_active = worker.get("is_active", True)
            
            # Note: attendance is approximated using is_active as a temporary solution.
            # This is not real attendance data - it will be replaced when IoT check-in is implemented.
            formatted_workers.append({
                "worker_id": worker.get("id", 0),
                "name": worker.get("full_name", ""),
                "role": worker.get("role", "laborer"),
                "attendance": {
                    "today": is_active,
                    "history": []
                },
                "daily_wage": worker.get("daily_wage", 0.0)
            })
        
        return formatted_workers
    
    def format_transactions_to_costs(self, raw_transactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Format raw transactions into cost dict for FinanceAgent.
        
        Args:
            raw_transactions: List of dicts with type, category, amount
            
        Returns:
            Dict with costs by category
        """
        costs = {
            "seed_cost": 0.0,
            "fertilizer_cost": 0.0,
            "labor_cost": 0.0,
            "irrigation_cost": 0.0,
            "other_costs": 0.0
        }
        
        category_mapping = {
            "seeds": "seed_cost",
            "fertilizer": "fertilizer_cost",
            "labor": "labor_cost",
            "irrigation": "irrigation_cost",
        }
        
        for transaction in raw_transactions:
            # Only process expense transactions
            if transaction.get("type") != "expense":
                continue
            
            category = transaction.get("category", "").lower()
            amount = transaction.get("amount", 0.0)
            
            if amount <= 0:
                continue
            
            mapped = category_mapping.get(category, "other_costs")
            costs[mapped] += amount
        
        return costs
    
    def validate_farm_context(self, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean farm data for agents.
        
        Args:
            farm_data: Raw farm data from database
            
        Returns:
            Cleaned farm context dict
        """
        return {
            "farm_id": farm_data.get("id", 0),
            "name": farm_data.get("name", "Unknown"),
            "crop_type": farm_data.get("crop_type") or "general",
            "area": farm_data.get("area", 1.0) if farm_data.get("area", 0) > 0 else 1.0,
            "location": farm_data.get("location") or "Egypt",
            "is_active": farm_data.get("is_active", True)
        }
    
    def build_agent_input(
        self,
        agent_name: str,
        farm_data: Dict[str, Any],
        sensor_data: Dict[str, Any],
        extra: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build input dict for a specific agent.
        
        Args:
            agent_name: Name of the agent
            farm_data: Validated farm context
            sensor_data: Formatted sensor data
            extra: Additional data needed by the agent
            
        Returns:
            Dict with agent-specific input format
        """
        if agent_name == "farm_intelligence":
            return {
                "farm_id": farm_data.get("farm_id"),
                "crop_type": farm_data.get("crop_type"),
                "sensor_data": sensor_data,
                "image_path": extra.get("image_path")
            }
        
        elif agent_name == "resource_optimization":
            return {
                "farm_id": farm_data.get("farm_id"),
                "crop_type": farm_data.get("crop_type"),
                "sensor_data": sensor_data,
                "area": farm_data.get("area"),
                "current_irrigation": extra.get("current_irrigation", 0)
            }
        
        elif agent_name == "market_intelligence":
            return {
                "farm_id": farm_data.get("farm_id"),
                "crop_type": farm_data.get("crop_type"),
                "current_price": extra.get("current_price", 0),
                "quantity": extra.get("quantity", 0),
                "storage_cost": extra.get("storage_cost", 0.5)
            }
        
        elif agent_name == "finance":
            return {
                "farm_id": farm_data.get("farm_id"),
                "crop_type": farm_data.get("crop_type"),
                "area": farm_data.get("area"),
                "costs": extra.get("costs", {}),
                "current_price": extra.get("current_price", 0),
                "season": extra.get("season", "current")
            }
        
        elif agent_name == "inventory":
            return {
                "farm_id": farm_data.get("farm_id"),
                "crop_type": farm_data.get("crop_type"),
                "area": farm_data.get("area"),
                "inventory": extra.get("inventory", [])
            }
        
        elif agent_name == "workforce":
            return {
                "farm_id": farm_data.get("farm_id"),
                "crop_type": farm_data.get("crop_type"),
                "area": farm_data.get("area"),
                "workers": extra.get("workers", []),
                "tasks": []  # Tasks table not yet implemented
            }
        
        else:
            print(f"[DBQueryTool] ⚠️ Unknown agent_name: {agent_name}")
            return {}
