"""
CropMind - Agent Router
Routes incoming requests to the appropriate AI agent

Author: CropMind Team
Date: 2026
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.farm import Farm
from app.models.sensor_reading import SensorReading
from app.models.transaction import Transaction
from app.models.inventory_item import InventoryItem
from app.models.worker import Worker
from app.models.market_price import MarketPrice

from ai_engine.agents.farm_intelligence_agent import FarmIntelligenceAgent
from ai_engine.agents.resource_optimization_agent import ResourceOptimizationAgent
from ai_engine.agents.market_intelligence_agent import MarketIntelligenceAgent
from ai_engine.agents.finance_agent import FinanceAgent
from ai_engine.agents.inventory_agent import InventoryAgent
from ai_engine.agents.workforce_agent import WorkforceAgent

from ai_engine.tools.db_query_tool import DBQueryTool
from ai_engine.tools.alert_tool import AlertTool


class AgentRouter:
    """
    Routes incoming requests to the appropriate AI agent.
    Acts as a single entry point instead of calling agents directly.
    """
    
    def __init__(self):
        """Initialize the AgentRouter with tools."""
        self.db_tool = DBQueryTool()
        self.alert_tool = AlertTool()
        print("[AgentRouter] ✅ Initialized")
    
    async def route(
        self,
        agent_name: str,
        farm_id: int,
        db: AsyncSession,
        extra: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """
        Main routing method. Routes to the correct agent.
        
        Args:
            agent_name: farm_intelligence, resource_optimization, market_intelligence,
                       finance, inventory, workforce
            farm_id: Farm ID
            db: AsyncSession
            extra: Additional data needed by the agent
            
        Returns:
            Dict with agent result
        """
        try:
            # Get farm data
            farm = await self._get_farm(farm_id, db)
            if farm is None:
                return {
                    "error": "Farm not found",
                    "farm_id": farm_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Validate farm context
            farm_data = self.db_tool.validate_farm_context(farm)
            
            # Route to specific agent
            result = {}
            
            if agent_name == "farm_intelligence":
                result = await self._route_farm_intelligence(farm_id, farm_data, db)
            
            elif agent_name == "resource_optimization":
                result = await self._route_resource_optimization(farm_id, farm_data, db)
            
            elif agent_name == "market_intelligence":
                result = await self._route_market_intelligence(farm_id, farm_data, db, extra)
            
            elif agent_name == "finance":
                result = await self._route_finance(farm_id, farm_data, db)
            
            elif agent_name == "inventory":
                result = await self._route_inventory(farm_id, farm_data, db)
            
            elif agent_name == "workforce":
                result = await self._route_workforce(farm_id, farm_data, db)
            
            else:
                print(f"[AgentRouter] ⚠️ Unknown agent_name: {agent_name}")
                return {
                    "error": f"Unknown agent: {agent_name}",
                    "farm_id": farm_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "agent": agent_name,
                "farm_id": farm_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[AgentRouter] ❌ Error in route: {e}")
            return {
                "error": str(e),
                "agent": agent_name,
                "farm_id": farm_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_farm(self, farm_id: int, db: AsyncSession) -> Optional[Dict]:
        """Get farm by ID."""
        try:
            result = await db.execute(
                select(Farm).where(Farm.id == farm_id)
            )
            farm = result.scalar_one_or_none()
            if farm:
                return {
                    "id": farm.id,
                    "name": farm.name,
                    "location": farm.location,
                    "area": farm.area,
                    "crop_type": farm.crop_type,
                    "is_active": farm.is_active
                }
            return None
        except Exception as e:
            print(f"[AgentRouter] ⚠️ Error fetching farm {farm_id}: {e}")
            return None
    
    async def _get_sensor_data(self, farm_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Get latest sensor readings for a farm."""
        try:
            raw_readings = []
            sensor_types = ["temperature", "humidity", "soil_moisture", "ph"]
            
            for sensor_type in sensor_types:
                result = await db.execute(
                    select(SensorReading)
                    .where(SensorReading.farm_id == farm_id)
                    .where(SensorReading.type == sensor_type)
                    .order_by(desc(SensorReading.timestamp))
                    .limit(1)
                )
                reading = result.scalar_one_or_none()
                if reading:
                    raw_readings.append({
                        "type": reading.type,
                        "value": reading.value,
                        "timestamp": reading.timestamp.isoformat() if reading.timestamp else None
                    })
            
            return self.db_tool.format_sensor_data(raw_readings)
        except Exception as e:
            print(f"[AgentRouter] ⚠️ Error fetching sensor data: {e}")
            return {}
    
    async def _get_costs(self, farm_id: int, db: AsyncSession) -> Dict[str, float]:
        """Get costs from farm transactions."""
        try:
            result = await db.execute(
                select(Transaction)
                .where(Transaction.farm_id == farm_id)
                .where(Transaction.type == "expense")
            )
            transactions = result.scalars().all()
            
            raw_transactions = [
                {
                    "type": t.type,
                    "category": t.category,
                    "amount": t.amount
                }
                for t in transactions
            ]
            
            return self.db_tool.format_transactions_to_costs(raw_transactions)
        except Exception as e:
            print(f"[AgentRouter] ⚠️ Error fetching costs: {e}")
            return {}
    
    async def _get_inventory(self, farm_id: int, db: AsyncSession) -> List[Dict]:
        """Get inventory items for a farm."""
        try:
            result = await db.execute(
                select(InventoryItem).where(InventoryItem.farm_id == farm_id)
            )
            items = result.scalars().all()
            
            raw_items = [
                {
                    "name": item.name,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "min_quantity": item.min_quantity,
                    "price_per_unit": item.price_per_unit
                }
                for item in items
            ]
            
            return self.db_tool.format_inventory_items(raw_items)
        except Exception as e:
            print(f"[AgentRouter] ⚠️ Error fetching inventory: {e}")
            return []
    
    async def _get_workers(self, farm_id: int, db: AsyncSession) -> List[Dict]:
        """Get workers for a farm."""
        try:
            result = await db.execute(
                select(Worker).where(Worker.farm_id == farm_id)
            )
            workers = result.scalars().all()
            
            raw_workers = [
                {
                    "id": w.id,
                    "full_name": w.full_name,
                    "role": w.role,
                    "is_active": w.is_active,
                    "daily_wage": w.daily_wage
                }
                for w in workers
            ]
            
            return self.db_tool.format_workers(raw_workers)
        except Exception as e:
            print(f"[AgentRouter] ⚠️ Error fetching workers: {e}")
            return []
    
    async def _get_market_price(self, commodity: str, db: AsyncSession) -> float:
        """Get latest market price for a commodity."""
        if not commodity:
            return 0.0
        
        try:
            result = await db.execute(
                select(MarketPrice.price)
                .where(MarketPrice.commodity.ilike(f"%{commodity}%"))
                .order_by(desc(MarketPrice.date))
                .limit(1)
            )
            price = result.scalar_one_or_none()
            return float(price) if price else 0.0
        except Exception as e:
            print(f"[AgentRouter] ⚠️ Error fetching market price: {e}")
            return 0.0
    
    async def _route_farm_intelligence(
        self,
        farm_id: int,
        farm_data: Dict,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Route to FarmIntelligenceAgent."""
        try:
            sensor_data = await self._get_sensor_data(farm_id, db)
            
            input_data = self.db_tool.build_agent_input(
                agent_name="farm_intelligence",
                farm_data=farm_data,
                sensor_data=sensor_data,
                extra={}
            )
            
            agent = FarmIntelligenceAgent()
            result = agent.run(input_data)
            return result
        except Exception as e:
            print(f"[AgentRouter] ❌ Farm Intelligence error: {e}")
            return {"error": str(e)}
    
    async def _route_resource_optimization(
        self,
        farm_id: int,
        farm_data: Dict,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Route to ResourceOptimizationAgent."""
        try:
            sensor_data = await self._get_sensor_data(farm_id, db)
            
            input_data = self.db_tool.build_agent_input(
                agent_name="resource_optimization",
                farm_data=farm_data,
                sensor_data=sensor_data,
                extra={"current_irrigation": 0}
            )
            
            agent = ResourceOptimizationAgent()
            result = agent.run(input_data)
            return result
        except Exception as e:
            print(f"[AgentRouter] ❌ Resource Optimization error: {e}")
            return {"error": str(e)}
    
    async def _route_market_intelligence(
        self,
        farm_id: int,
        farm_data: Dict,
        db: AsyncSession,
        extra: Dict
    ) -> Dict[str, Any]:
        """Route to MarketIntelligenceAgent."""
        try:
            current_price = extra.get("current_price") or await self._get_market_price(
                farm_data.get("crop_type"), db
            )
            
            input_data = self.db_tool.build_agent_input(
                agent_name="market_intelligence",
                farm_data=farm_data,
                sensor_data={},
                extra={
                    "current_price": current_price,
                    "quantity": extra.get("quantity", 0),
                    "storage_cost": extra.get("storage_cost", 0.5)
                }
            )
            
            agent = MarketIntelligenceAgent()
            result = agent.run(input_data)
            return result
        except Exception as e:
            print(f"[AgentRouter] ❌ Market Intelligence error: {e}")
            return {"error": str(e)}
    
    async def _route_finance(
        self,
        farm_id: int,
        farm_data: Dict,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Route to FinanceAgent."""
        try:
            costs = await self._get_costs(farm_id, db)
            
            input_data = self.db_tool.build_agent_input(
                agent_name="finance",
                farm_data=farm_data,
                sensor_data={},
                extra={
                    "costs": costs,
                    "current_price": 0,
                    "season": "current"
                }
            )
            
            agent = FinanceAgent()
            result = agent.run(input_data)
            return result
        except Exception as e:
            print(f"[AgentRouter] ❌ Finance error: {e}")
            return {"error": str(e)}
    
    async def _route_inventory(
        self,
        farm_id: int,
        farm_data: Dict,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Route to InventoryAgent."""
        try:
            inventory = await self._get_inventory(farm_id, db)
            
            input_data = self.db_tool.build_agent_input(
                agent_name="inventory",
                farm_data=farm_data,
                sensor_data={},
                extra={"inventory": inventory}
            )
            
            agent = InventoryAgent()
            result = agent.run(input_data)
            return result
        except Exception as e:
            print(f"[AgentRouter] ❌ Inventory error: {e}")
            return {"error": str(e)}
    
    async def _route_workforce(
        self,
        farm_id: int,
        farm_data: Dict,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Route to WorkforceAgent."""
        try:
            workers = await self._get_workers(farm_id, db)
            
            input_data = self.db_tool.build_agent_input(
                agent_name="workforce",
                farm_data=farm_data,
                sensor_data={},
                extra={"workers": workers}
            )
            
            agent = WorkforceAgent()
            result = agent.run(input_data)
            return result
        except Exception as e:
            print(f"[AgentRouter] ❌ Workforce error: {e}")
            return {"error": str(e)}
    
    async def run_with_alerts(
        self,
        agent_name: str,
        farm_id: int,
        db: AsyncSession,
        extra: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """
        Runs agent and checks alerts on the result.
        
        Args:
            agent_name: Name of the agent to run
            farm_id: Farm ID
            db: AsyncSession
            extra: Additional data
            
        Returns:
            Dict with agent result and alerts
        """
        result = await self.route(agent_name, farm_id, db, extra)
        
        if "error" in result:
            return result
        
        alerts = []
        result_data = result.get("result", {})
        data = result_data.get("data", {})
        
        # Check sensor alerts - fetch sensor data directly from DB
        if agent_name in ["farm_intelligence", "resource_optimization"]:
            sensor_data = await self._get_sensor_data(farm_id, db)
            sensor_alerts = self.alert_tool.check_sensor_alerts(farm_id, sensor_data)
            alerts.extend(sensor_alerts)
        
        # Check crop health alert
        if agent_name == "farm_intelligence":
            health_score = data.get("health_score")
            crop_type = data.get("crop_type")
            if health_score is not None and crop_type:
                crop_alert = self.alert_tool.check_crop_health_alert(
                    farm_id, crop_type, health_score
                )
                if crop_alert:
                    alerts.append(crop_alert)
        
        # Check inventory alerts
        if agent_name == "inventory":
            inventory_items = data.get("inventory", [])
            if inventory_items:
                inventory_alerts = self.alert_tool.check_inventory_alerts(farm_id, inventory_items)
                alerts.extend(inventory_alerts)
        
        # Add alerts to result
        if alerts:
            result["alerts"] = alerts
            result["alert_summary"] = self.alert_tool.get_alert_summary(alerts)
        
        return result
