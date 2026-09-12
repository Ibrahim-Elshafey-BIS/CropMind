"""
CropMind - Agent Scheduler
Schedules periodic agent tasks as FastAPI background tasks

Author: CropMind Team
Date: 2026
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.farm import Farm
from ai_engine.agents.farm_copilot import FarmCopilot
from ai_engine.orchestrator.agent_router import AgentRouter


class AgentScheduler:
    """
    Schedules periodic agent tasks as FastAPI background tasks.
    """
    
    def __init__(self):
        """Initialize the AgentScheduler with router."""
        self.router = AgentRouter()
        self.is_running = False
        print("[AgentScheduler] ✅ Initialized")
    
    async def run_daily_summary(
        self,
        farm_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Runs FarmCopilot.generate_daily_summary for a farm.
        Called once daily.
        
        Args:
            farm_id: Farm ID
            db: AsyncSession
            
        Returns:
            Dict with daily summary
        """
        try:
            # Get farm
            result = await db.execute(
                select(Farm).where(Farm.id == farm_id)
            )
            farm = result.scalar_one_or_none()
            
            if not farm:
                return {
                    "error": "Farm not found",
                    "farm_id": farm_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Build farm context
            farm_context = {
                "farm_id": farm.id,
                "name": farm.name,
                "crop_type": farm.crop_type or "general",
                "area": farm.area,
                "location": farm.location or "Egypt",
                "is_active": farm.is_active
            }
            
            # Generate daily summary
            copilot = FarmCopilot()
            summary = copilot.generate_daily_summary(farm_context)
            
            print(f"[AgentScheduler] ✅ Daily summary generated for farm {farm_id}")
            
            return {
                "farm_id": farm_id,
                "farm_name": farm.name,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[AgentScheduler] ❌ Error generating daily summary: {e}")
            return {
                "error": str(e),
                "farm_id": farm_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_health_check(
        self,
        farm_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Runs FarmIntelligenceAgent for a farm.
        Called every few hours.
        
        Args:
            farm_id: Farm ID
            db: AsyncSession
            
        Returns:
            Dict with health check results and alerts
        """
        try:
            result = await self.router.run_with_alerts(
                "farm_intelligence",
                farm_id,
                db
            )
            
            print(f"[AgentScheduler] ✅ Health check completed for farm {farm_id}")
            
            return {
                "farm_id": farm_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[AgentScheduler] ❌ Error running health check: {e}")
            return {
                "error": str(e),
                "farm_id": farm_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_all_farms_health_check(
        self,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Runs health check for ALL active farms.
        
        Args:
            db: AsyncSession
            
        Returns:
            List of health check results
        """
        try:
            # Get all active farms
            result = await db.execute(
                select(Farm).where(Farm.is_active == True)
            )
            farms = result.scalars().all()
            
            print(f"[AgentScheduler] 🔍 Running health check for {len(farms)} farms")
            
            results = []
            for farm in farms:
                health_result = await self.run_health_check(farm.id, db)
                results.append(health_result)
            
            return results
            
        except Exception as e:
            print(f"[AgentScheduler] ❌ Error running all farms health check: {e}")
            return []
    
    async def schedule_background_task(
        self,
        background_tasks: BackgroundTasks,
        task_name: str,
        farm_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Adds a task to FastAPI BackgroundTasks.
        
        Args:
            background_tasks: FastAPI BackgroundTasks instance
            task_name: daily_summary, health_check, market_update
            farm_id: Farm ID
            db: AsyncSession
            
        Returns:
            Dict with task status
        """
        try:
            if task_name == "daily_summary":
                background_tasks.add_task(
                    self.run_daily_summary,
                    farm_id,
                    db
                )
                print(f"[AgentScheduler] 📋 Scheduled daily_summary for farm {farm_id}")
                
            elif task_name == "health_check":
                background_tasks.add_task(
                    self.run_health_check,
                    farm_id,
                    db
                )
                print(f"[AgentScheduler] 🏥 Scheduled health_check for farm {farm_id}")
                
            elif task_name == "market_update":
                background_tasks.add_task(
                    self.router.route,
                    "market_intelligence",
                    farm_id,
                    db,
                    {}
                )
                print(f"[AgentScheduler] 📊 Scheduled market_update for farm {farm_id}")
                
            else:
                print(f"[AgentScheduler] ⚠️ Unknown task_name: {task_name}")
                return {
                    "error": f"Unknown task: {task_name}",
                    "farm_id": farm_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "task": task_name,
                "farm_id": farm_id,
                "status": "scheduled",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[AgentScheduler] ❌ Error scheduling task: {e}")
            return {
                "error": str(e),
                "task": task_name,
                "farm_id": farm_id,
                "timestamp": datetime.now().isoformat()
            }
