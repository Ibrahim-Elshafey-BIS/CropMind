"""
CropMind - Agents Routes
FastAPI routes for AI Agent endpoints with real agent integration

Author: CropMind Team
Date: 2026
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ConfigDict

from app.core.database import get_db
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.sensor_reading import SensorReading
from app.models.transaction import Transaction
from app.models.inventory_item import InventoryItem
from app.models.worker import Worker
from app.models.market_price import MarketPrice

# Import AI Agents
from ai_engine.agents.farm_copilot import FarmCopilot
from ai_engine.agents.farm_intelligence_agent import FarmIntelligenceAgent
from ai_engine.agents.resource_optimization_agent import ResourceOptimizationAgent
from ai_engine.agents.market_intelligence_agent import MarketIntelligenceAgent
from ai_engine.agents.finance_agent import FinanceAgent
from ai_engine.agents.inventory_agent import InventoryAgent
from ai_engine.agents.workforce_agent import WorkforceAgent


# ============================================
# Schemas
# ============================================

class CopilotRequest(BaseModel):
    """Schema for Farm Copilot chat request."""
    message: str = Field(..., description="User message to the copilot", min_length=1)
    farm_id: int = Field(..., description="Farm ID for context")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for maintaining context")

    model_config = ConfigDict(from_attributes=True)


class CopilotResponse(BaseModel):
    """Schema for Farm Copilot response."""
    response: str = Field(..., description="Copilot response message")
    conversation_id: str = Field(..., description="Conversation ID for context")
    suggestions: Optional[List[str]] = Field(default=None, description="Suggested follow-up questions")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    model_config = ConfigDict(from_attributes=True)


class AgentResponse(BaseModel):
    """Schema for general agent response."""
    status: str = Field(..., description="Status: ok, error, processing")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Response data payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    model_config = ConfigDict(from_attributes=True)


# ============================================
# In-Memory Conversation Store
# ============================================

_conversation_store: Dict[str, List[Dict]] = {}
"""
In-memory store for conversation history.
Key: conversation_id, Value: List of {"role": "user"|"assistant", "content": str}
Note: This is ephemeral and resets on server restart. Acceptable for demo.
"""


# ============================================
# Helper Functions
# ============================================

async def get_farm_or_404(farm_id: int, db: AsyncSession) -> Farm:
    """Get farm by ID or raise 404."""
    result = await db.execute(
        select(Farm).where(Farm.id == farm_id)
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found"
        )
    return farm


def get_conversation_history(conversation_id: str) -> List[Dict]:
    """Get conversation history from store."""
    return _conversation_store.get(conversation_id, [])


def save_conversation_message(conversation_id: str, role: str, content: str) -> None:
    """Save a message to conversation history."""
    if conversation_id not in _conversation_store:
        _conversation_store[conversation_id] = []
    _conversation_store[conversation_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })


async def get_latest_sensor_readings(farm_id: int, db: AsyncSession) -> Dict[str, float]:
    """
    Get the latest sensor reading for each sensor type.
    """
    sensor_data = {
        "temperature": None,
        "humidity": None,
        "soil_moisture": None,
        "ph": None,
        "N": None,
        "P": None,
        "K": None,
        "rainfall": None
    }
    
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
            sensor_data[sensor_type] = reading.value
    
    # Note: N, P, K, rainfall are not available in SensorReading currently.
    # Using placeholder values. In production, these would come from soil sensors.
    if sensor_data["soil_moisture"] is not None:
        # Approximate N, P, K from soil moisture (placeholder logic)
        sensor_data["N"] = 45.0  # Placeholder
        sensor_data["P"] = 30.0  # Placeholder
        sensor_data["K"] = 60.0  # Placeholder
        sensor_data["rainfall"] = 5.0  # Placeholder
    
    return {k: v for k, v in sensor_data.items() if v is not None}


async def get_farm_transactions_costs(farm_id: int, db: AsyncSession) -> Dict[str, float]:
    """
    Get costs by category from farm transactions.
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
    
    result = await db.execute(
        select(Transaction.category, func.sum(Transaction.amount))
        .where(Transaction.farm_id == farm_id)
        .where(Transaction.type == "expense")
        .group_by(Transaction.category)
    )
    
    for category, total in result.all():
        mapped = category_mapping.get(category.lower(), "other_costs")
        costs[mapped] += float(total) if total else 0.0
    
    return costs


async def get_farm_inventory_items(farm_id: int, db: AsyncSession) -> List[Dict]:
    """
    Get inventory items for a farm, mapped to agent expected format.
    """
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.farm_id == farm_id)
    )
    items = result.scalars().all()
    
    return [
        {
            "item_name": item.name,
            "quantity": item.quantity,
            "unit": item.unit,
            "min_threshold": item.min_quantity,
            "cost_per_unit": item.price_per_unit
        }
        for item in items
    ]


async def get_farm_workers(farm_id: int, db: AsyncSession) -> List[Dict]:
    """
    Get workers for a farm, mapped to agent expected format.
    Note: attendance is approximated using is_active as a temporary solution.
    """
    result = await db.execute(
        select(Worker).where(Worker.farm_id == farm_id)
    )
    workers = result.scalars().all()
    
    return [
        {
            "worker_id": worker.id,
            "name": worker.full_name,
            "role": worker.role,
            # Temporary: using is_active as a proxy for attendance
            "attendance": {"today": worker.is_active, "history": []},
            "daily_wage": worker.daily_wage
        }
        for worker in workers
    ]


async def get_latest_market_price(commodity: str, db: AsyncSession) -> Optional[float]:
    """
    Get the latest market price for a commodity.
    """
    if not commodity:
        return None
    
    result = await db.execute(
        select(MarketPrice.price)
        .where(MarketPrice.commodity.ilike(f"%{commodity}%"))
        .order_by(desc(MarketPrice.date))
        .limit(1)
    )
    price = result.scalar_one_or_none()
    return float(price) if price else None


# ============================================
# Router
# ============================================

router = APIRouter()


# ============================================
# GET /status - Get all agents status
# ============================================

@router.get("/status", response_model=Dict[str, Any])
async def get_agents_status():
    """
    Get the status of all AI Agents by attempting to instantiate each.
    Returns availability and health status.
    """
    agents_status = []
    
    agent_classes = [
        ("Farm Copilot", FarmCopilot),
        ("Farm Intelligence Agent", FarmIntelligenceAgent),
        ("Resource Optimization Agent", ResourceOptimizationAgent),
        ("Market Intelligence Agent", MarketIntelligenceAgent),
        ("Finance Agent", FinanceAgent),
        ("Inventory Agent", InventoryAgent),
        ("Workforce Agent", WorkforceAgent),
    ]
    
    for name, agent_class in agent_classes:
        try:
            # Try to instantiate the agent
            agent = agent_class()
            agent_status = "available"
            error = None
        except Exception as e:
            agent_status = "unavailable"
            error = str(e)
        
        agents_status.append({
            "name": name,
            "status": agent_status,
            "description": agent_class.__doc__.strip().split("\n")[0] if agent_class.__doc__ else "",
            "error": error
        })
    
    return {
        "status": "ok",
        "agents": agents_status,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================
# POST /copilot - Farm Copilot chat
# ============================================

@router.post("/copilot", response_model=CopilotResponse)
async def chat_copilot(
    request: CopilotRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the Farm Copilot AI assistant.
    Returns an AI-generated response with farming advice.
    """
    try:
        # Verify farm exists
        farm = await get_farm_or_404(request.farm_id, db)
        
        # Get or create conversation_id
        conversation_id = request.conversation_id or f"conv_{datetime.utcnow().timestamp()}"
        
        # Get conversation history
        history = get_conversation_history(conversation_id)
        
        # Build farm context
        # Note: farm_context is intentionally minimal (crop_type, area, location, name, is_active)
        # to reduce LLM token usage. For detailed sensor/price data, use the dedicated agent endpoints.
        # If user asks about health/price in chat, FarmCopilot will call sub-agents with defaults.
        farm_context = {
            "farm_id": farm.id,
            "crop_type": farm.crop_type or "general",
            "area": farm.area,
            "location": farm.location,
            "name": farm.name,
            "is_active": farm.is_active
        }
        
        # Instantiate and run Farm Copilot
        copilot = FarmCopilot()
        result = copilot.chat(
            message=request.message,
            farm_context=farm_context,
            history=history
        )
        
        # Save conversation to store
        save_conversation_message(conversation_id, "user", request.message)
        save_conversation_message(conversation_id, "assistant", result.get("response", ""))
        
        # Suggestions
        suggestions = [
            "ما هي حالة المحاصيل اليوم؟",
            "متى أنسب وقت للري؟",
            "كيف يمكنني زيادة الإنتاجية؟",
            "ما هي الأسعار المتوقعة للطماطم؟"
        ]
        
        return CopilotResponse(
            response=result.get("response", "عذراً، حدث خطأ في معالجة طلبك."),
            conversation_id=conversation_id,
            suggestions=suggestions,
            timestamp=result.get("timestamp", datetime.utcnow())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Copilot error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Copilot failed: {str(e)}"
        )


# ============================================
# POST /analyze/{farm_id} - Farm Intelligence Agent
# ============================================

@router.post("/analyze/{farm_id}", response_model=AgentResponse)
async def analyze_farm(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Run Farm Intelligence Agent analysis on a specific farm.
    Analyzes crop health, field data, and weather.
    """
    try:
        farm = await get_farm_or_404(farm_id, db)
        
        # Get latest sensor readings
        sensor_data = await get_latest_sensor_readings(farm_id, db)
        
        # Prepare input
        input_data = {
            "farm_id": farm_id,
            "crop_type": farm.crop_type or "general",
            "sensor_data": sensor_data,
            "image_path": None
        }
        
        # Run agent
        agent = FarmIntelligenceAgent()
        result = agent.run(input_data)
        
        return AgentResponse(
            status="ok",
            message="Farm analysis completed",
            data=result.get("data", {}),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Farm Intelligence error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Farm analysis failed: {str(e)}"
        )


# ============================================
# POST /optimize/{farm_id} - Resource Optimization Agent
# ============================================

@router.post("/optimize/{farm_id}", response_model=AgentResponse)
async def optimize_resources(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Run Resource Optimization Agent on a specific farm.
    Analyzes water and fertilizer usage for efficiency.
    """
    try:
        farm = await get_farm_or_404(farm_id, db)
        
        # Get latest sensor readings
        sensor_data = await get_latest_sensor_readings(farm_id, db)
        
        # NOTE: current_irrigation is not available from database yet.
        # Using 0 as placeholder until IoT sensor integration is complete.
        input_data = {
            "farm_id": farm_id,
            "crop_type": farm.crop_type or "general",
            "sensor_data": sensor_data,
            "area": farm.area,
            "current_irrigation": 0  # Placeholder
        }
        
        # Run agent
        agent = ResourceOptimizationAgent()
        result = agent.run(input_data)
        
        return AgentResponse(
            status="ok",
            message="Resource optimization completed",
            data=result.get("data", {}),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Resource Optimization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resource optimization failed: {str(e)}"
        )


# ============================================
# POST /market-intel/{farm_id} - Market Intelligence Agent
# ============================================

@router.post("/market-intel/{farm_id}", response_model=AgentResponse)
async def get_market_intelligence(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Run Market Intelligence Agent on a specific farm.
    Provides price forecasts and market recommendations.
    """
    try:
        farm = await get_farm_or_404(farm_id, db)
        
        # Get latest market price for the farm's primary crop
        current_price = await get_latest_market_price(farm.crop_type, db)
        
        # NOTE: quantity and storage_cost are not available from database yet.
        # Using placeholder values until inventory/warehouse tracking is implemented.
        input_data = {
            "farm_id": farm_id,
            "crop_type": farm.crop_type or "general",
            "current_price": current_price if current_price is not None else 0.0,
            "quantity": 0,  # Placeholder - needs inventory/sales data
            "storage_cost": 0.5  # Placeholder - needs actual storage cost data
        }
        
        # Run agent
        agent = MarketIntelligenceAgent()
        result = agent.run(input_data)
        
        return AgentResponse(
            status="ok",
            message="Market intelligence report generated",
            data=result.get("data", {}),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Market Intelligence error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market intelligence failed: {str(e)}"
        )


# ============================================
# POST /finance/{farm_id} - Finance Agent
# ============================================

@router.post("/finance/{farm_id}", response_model=AgentResponse)
async def analyze_finance(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Run Finance Agent on a specific farm.
    Provides financial analysis, profitability, and ROI calculations.
    """
    try:
        farm = await get_farm_or_404(farm_id, db)
        
        # Get costs from transactions
        costs = await get_farm_transactions_costs(farm_id, db)
        
        # NOTE: current_price is not available from database yet.
        # Using 0 as placeholder until market price integration is complete.
        input_data = {
            "farm_id": farm_id,
            "crop_type": farm.crop_type or "general",
            "area": farm.area,
            "costs": costs,
            "current_price": 0,  # Placeholder - needs market price data
            "season": "current"
        }
        
        # Run agent
        agent = FinanceAgent()
        result = agent.run(input_data)
        
        return AgentResponse(
            status="ok",
            message="Financial analysis completed",
            data=result.get("data", {}),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Finance Agent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Financial analysis failed: {str(e)}"
        )


# ============================================
# POST /inventory/{farm_id} - Inventory Agent
# ============================================

@router.post("/inventory/{farm_id}", response_model=AgentResponse)
async def analyze_inventory(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Run Inventory Agent on a specific farm.
    Analyzes inventory levels and generates purchase recommendations.
    """
    try:
        farm = await get_farm_or_404(farm_id, db)
        
        # Get inventory items
        inventory_items = await get_farm_inventory_items(farm_id, db)
        
        input_data = {
            "farm_id": farm_id,
            "inventory": inventory_items,
            "crop_type": farm.crop_type or "general",
            "area": farm.area
        }
        
        # Run agent
        agent = InventoryAgent()
        result = agent.run(input_data)
        
        return AgentResponse(
            status="ok",
            message="Inventory analysis completed",
            data=result.get("data", {}),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Inventory Agent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inventory analysis failed: {str(e)}"
        )


# ============================================
# POST /workforce/{farm_id} - Workforce Agent
# ============================================

@router.post("/workforce/{farm_id}", response_model=AgentResponse)
async def analyze_workforce(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Run Workforce Agent on a specific farm.
    Analyzes workers, attendance, and tasks.
    """
    try:
        farm = await get_farm_or_404(farm_id, db)
        
        # Get workers with attendance proxy
        workers = await get_farm_workers(farm_id, db)
        
        # NOTE: Tasks table does not exist in the database yet.
        # Using empty list as placeholder until task management is implemented.
        input_data = {
            "farm_id": farm_id,
            "workers": workers,
            "tasks": [],  # Placeholder - tasks table not yet implemented
            "crop_type": farm.crop_type or "general",
            "area": farm.area
        }
        
        # Run agent
        agent = WorkforceAgent()
        result = agent.run(input_data)
        
        return AgentResponse(
            status="ok",
            message="Workforce analysis completed",
            data=result.get("data", {}),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Workforce Agent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workforce analysis failed: {str(e)}"
        )
