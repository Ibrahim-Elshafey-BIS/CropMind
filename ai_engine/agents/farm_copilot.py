"""
CropMind - Farm Copilot
Arabic conversational AI assistant for farmers

Author: CropMind Team
Date: 2026
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from ai_engine.agents.base_agent import BaseAgent
from ai_engine.agents.farm_intelligence_agent import FarmIntelligenceAgent
from ai_engine.agents.resource_optimization_agent import ResourceOptimizationAgent
from ai_engine.agents.market_intelligence_agent import MarketIntelligenceAgent
from ai_engine.agents.finance_agent import FinanceAgent
from ai_engine.agents.inventory_agent import InventoryAgent
from ai_engine.agents.workforce_agent import WorkforceAgent


class FarmCopilot(BaseAgent):
    """
    Farm Copilot - Arabic conversational AI for farmers.
    The central AI agent that orchestrates all other agents based on user queries.
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Initialize the Farm Copilot.
        
        Args:
            groq_api_key: Groq API key (reads from env if None)
        """
        super().__init__(
            agent_name="Farm Copilot",
            description="Arabic-language conversational AI assistant for farmers",
            groq_api_key=groq_api_key
        )
        
        # Initialize sub-agents (lazy loading)
        self._farm_agent = None
        self._resource_agent = None
        self._market_agent = None
        self._finance_agent = None
        self._inventory_agent = None
        self._workforce_agent = None
        
        self.log("✅ Farm Copilot initialized")
    
    @property
    def farm_agent(self):
        if self._farm_agent is None:
            self._farm_agent = FarmIntelligenceAgent(self.groq_api_key)
        return self._farm_agent
    
    @property
    def resource_agent(self):
        if self._resource_agent is None:
            self._resource_agent = ResourceOptimizationAgent(self.groq_api_key)
        return self._resource_agent
    
    @property
    def market_agent(self):
        if self._market_agent is None:
            self._market_agent = MarketIntelligenceAgent(self.groq_api_key)
        return self._market_agent
    
    @property
    def finance_agent(self):
        if self._finance_agent is None:
            self._finance_agent = FinanceAgent(self.groq_api_key)
        return self._finance_agent
    
    @property
    def inventory_agent(self):
        if self._inventory_agent is None:
            self._inventory_agent = InventoryAgent(self.groq_api_key)
        return self._inventory_agent
    
    @property
    def workforce_agent(self):
        if self._workforce_agent is None:
            self._workforce_agent = WorkforceAgent(self.groq_api_key)
        return self._workforce_agent
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the Farm Copilot with a user message.
        
        Args:
            input_data: Dict containing:
                - farm_id: int
                - message: str (user message in Arabic)
                - conversation_history: List[Dict] (optional)
                - farm_context: Dict (farm data)
                
        Returns:
            Dict with copilot response
        """
        try:
            farm_id = input_data.get("farm_id")
            message = input_data.get("message", "")
            conversation_history = input_data.get("conversation_history", [])
            farm_context = input_data.get("farm_context", {})
            
            if not message.strip():
                return self.format_response({
                    "response": "مرحباً! كيف يمكنني مساعدتك اليوم؟",
                    "intent": "greeting"
                })
            
            self.log(f"💬 User message: {message[:50]}...")
            
            # Detect intent
            intent = self.detect_intent(message)
            self.log(f"🎯 Detected intent: {intent}")
            
            # Process based on intent
            if intent == "greeting":
                response = self._handle_greeting()
                
            elif intent == "farm_health":
                response = self._handle_farm_health(farm_id, farm_context)
                
            elif intent == "market":
                response = self._handle_market(farm_id, farm_context)
                
            elif intent == "resources":
                response = self._handle_resources(farm_id, farm_context)
                
            elif intent == "finance":
                response = self._handle_finance(farm_id, farm_context)
                
            elif intent == "inventory":
                response = self._handle_inventory(farm_id, farm_context)
                
            elif intent == "workforce":
                response = self._handle_workforce(farm_id, farm_context)
                
            else:
                # General query - use LLM directly
                response = self._handle_general_query(message, farm_context, conversation_history)
            
            return self.format_response({
                "response": response,
                "intent": intent,
                "farm_id": farm_id,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.log(f"❌ Error in Farm Copilot: {e}")
            return self.format_error(str(e))
    
    def detect_intent(self, message: str) -> str:
        """
        Detect the intent of the user message.
        
        Args:
            message: User message in Arabic
            
        Returns:
            str: Detected intent
        """
        message = message.lower()
        
        # Greeting patterns
        greetings = ["مرحب", "اهلا", "سلام", "صباح", "مساء", "السلام", "حيا"]
        if any(g in message for g in greetings) and len(message.split()) < 5:
            return "greeting"
        
        # Farm health patterns
        health_keywords = ["صحة", "مرض", "محصول", "نبات", "ورقة", "حشرة", "فطر", "إنتاج", "نمو"]
        if any(k in message for k in health_keywords):
            return "farm_health"
        
        # Market patterns
        market_keywords = ["سعر", "بيع", "شراء", "سوق", "طلب", "عرض", "تسويق", "ربح", "خسارة"]
        if any(k in message for k in market_keywords):
            return "market"
        
        # Resource patterns
        resource_keywords = ["ري", "ماء", "سماد", "تربة", "مياه", "زراعة", "أسمدة", "ري"]
        if any(k in message for k in resource_keywords):
            return "resources"
        
        # Finance patterns
        finance_keywords = ["تكلفة", "مبلغ", "حساب", "ميزانية", "مال", "أموال", "فوائد", "قرض"]
        if any(k in message for k in finance_keywords):
            return "finance"
        
        # Inventory patterns
        inventory_keywords = ["مخزون", "تخزين", "مستلزمات", "مواد", "أدوات", "آلات", "معدات"]
        if any(k in message for k in inventory_keywords):
            return "inventory"
        
        # Workforce patterns
        workforce_keywords = ["عمال", "موظف", "إدارة", "مهام", "عمل", "ساعات", "أجور", "حضور"]
        if any(k in message for k in workforce_keywords):
            return "workforce"
        
        return "general"
    
    def _handle_greeting(self) -> str:
        """Handle greeting intent."""
        greetings = [
            "مرحباً بك في نظام CropMind! كيف يمكنني مساعدتك في مزرعتك اليوم؟ 🌱",
            "أهلاً وسهلاً! أنا مساعدك الزراعي الذكي. كيف هي حالة المزرعة اليوم؟",
            "السلام عليكم! CropMind في خدمتك. ماذا تريد أن تعرف عن مزرعتك؟"
        ]
        import random
        return random.choice(greetings)
    
    def _handle_farm_health(self, farm_id: int, farm_context: Dict) -> str:
        """Handle farm health intent using FarmIntelligenceAgent."""
        try:
            # Prepare data for farm agent
            input_data = {
                "farm_id": farm_id,
                "crop_type": farm_context.get("crop_type", "general"),
                "sensor_data": farm_context.get("sensor_data", {}),
                "image_path": farm_context.get("image_path")
            }
            
            result = self.farm_agent.run(input_data)
            
            if result.get("status") == "success":
                data = result.get("data", {})
                health_score = data.get("health_score", 0)
                report = data.get("report", "")
                recommendations = data.get("recommendations", {})
                
                response = f"🌿 **تقرير صحة المزرعة**\n\n"
                response += f"درجة الصحة العامة: **{health_score:.1f}/100**\n\n"
                
                if health_score >= 80:
                    response += "✅ حالة المزرعة ممتازة! استمر في الممارسات الحالية.\n\n"
                elif health_score >= 60:
                    response += "⚠️ المزرعة بحالة جيدة ولكن هناك بعض النقاط التي تحتاج تحسين.\n\n"
                else:
                    response += "🔴 المزرعة بحاجة إلى اهتمام فوري. يرجى متابعة التوصيات أدناه.\n\n"
                
                if report:
                    response += f"📋 **التقرير التفصيلي:**\n{report}\n\n"
                
                # Add urgent recommendations
                urgent = recommendations.get("urgent", [])
                if urgent:
                    response += "⚡ **توصيات عاجلة:**\n"
                    for rec in urgent[:3]:
                        response += f"- {rec}\n"
                
                return response
            else:
                return "عذراً، حدث خطأ في تحليل صحة المزرعة. يرجى المحاولة مرة أخرى."
                
        except Exception as e:
            self.log(f"❌ Farm health error: {e}")
            return "عذراً، لا أستطيع الوصول إلى بيانات صحة المزرعة حالياً. يرجى التحقق من اتصالك."
    
    def _handle_market(self, farm_id: int, farm_context: Dict) -> str:
        """Handle market intent using MarketIntelligenceAgent."""
        try:
            input_data = {
                "farm_id": farm_id,
                "crop_type": farm_context.get("crop_type", "general"),
                "current_price": farm_context.get("current_price", 0),
                "quantity": farm_context.get("quantity", 0),
                "storage_cost": farm_context.get("storage_cost", 0.5)
            }
            
            result = self.market_agent.run(input_data)
            
            if result.get("status") == "success":
                data = result.get("data", {})
                report = data.get("report", "")
                recommendation = data.get("recommendation", {})
                summary = data.get("summary", {})
                
                response = f"📊 **تحليل السوق**\n\n"
                response += f"المحصول: {farm_context.get('crop_type', 'غير معروف')}\n"
                response += f"السعر الحالي: {farm_context.get('current_price', 0)} جنيه/طن\n"
                response += f"**التوصية:** {recommendation.get('action', 'N/A')}\n\n"
                
                if report:
                    response += f"📋 **التقرير التفصيلي:**\n{report}\n\n"
                
                response += f"💡 **ملخص:**\n"
                response += f"- السعر المتوقع الأعلى: {summary.get('expected_high_price', 0)} جنيه\n"
                response += f"- أفضل وقت للبيع: بعد {summary.get('weeks_to_peak', 0)} أسبوع\n"
                response += f"- الربح المتوقع: {summary.get('expected_profit', 0)} جنيه\n"
                
                return response
            else:
                return "عذراً، حدث خطأ في تحليل السوق. يرجى المحاولة مرة أخرى."
                
        except Exception as e:
            self.log(f"❌ Market error: {e}")
            return "عذراً، لا أستطيع الوصول إلى بيانات السوق حالياً."
    
    def _handle_resources(self, farm_id: int, farm_context: Dict) -> str:
        """Handle resource optimization intent using ResourceOptimizationAgent."""
        try:
            input_data = {
                "farm_id": farm_id,
                "crop_type": farm_context.get("crop_type", "general"),
                "sensor_data": farm_context.get("sensor_data", {}),
                "area": farm_context.get("area", 1.0),
                "current_irrigation": farm_context.get("current_irrigation", 0)
            }
            
            result = self.resource_agent.run(input_data)
            
            if result.get("status") == "success":
                data = result.get("data", {})
                report = data.get("report", "")
                water_opt = data.get("water_optimization", {})
                summary = data.get("summary", {})
                
                response = f"💧 **تحسين الموارد**\n\n"
                response += f"المياه الإضافية المطلوبة: {water_opt.get('additional_water_needed_mm', 0)} مم\n"
                response += f"جدول الري: {water_opt.get('frequency', 'N/A')}\n"
                response += f"توفير المياه المتوقع: {summary.get('water_savings_percent', 0)}%\n\n"
                
                if report:
                    response += f"📋 **التقرير التفصيلي:**\n{report}\n\n"
                
                response += f"📋 **خطة التسميد:**\n"
                fertilizer = data.get("fertilizer_schedule", {})
                for item in fertilizer.get("schedule", [])[:5]:
                    response += f"- {item.get('week')}: {item.get('fertilizer')} ({item.get('amount')} كجم)\n"
                
                return response
            else:
                return "عذراً، حدث خطأ في تحسين الموارد. يرجى المحاولة مرة أخرى."
                
        except Exception as e:
            self.log(f"❌ Resource error: {e}")
            return "عذراً، لا أستطيع الوصول إلى بيانات الموارد حالياً."
    
    def _handle_finance(self, farm_id: int, farm_context: Dict) -> str:
        """Handle finance intent using FinanceAgent."""
        try:
            input_data = {
                "farm_id": farm_id,
                "crop_type": farm_context.get("crop_type", "general"),
                "area": farm_context.get("area", 1.0),
                "costs": farm_context.get("costs", {}),
                "current_price": farm_context.get("current_price", 0),
                "season": farm_context.get("season", "spring")
            }
            
            result = self.finance_agent.run(input_data)
            
            if result.get("status") == "success":
                data = result.get("data", {})
                report = data.get("report", "")
                summary = data.get("summary", {})
                
                response = f"💰 **التحليل المالي**\n\n"
                response += f"إجمالي التكاليف: {summary.get('total_cost', 0)} جنيه\n"
                response += f"إجمالي الإيرادات: {summary.get('total_revenue', 0)} جنيه\n"
                response += f"صافي الربح: {summary.get('net_profit', 0)} جنيه\n"
                response += f"العائد على الاستثمار: {summary.get('roi', 0)}%\n"
                response += f"الربحية: {summary.get('profitability', 'N/A')}\n\n"
                
                if report:
                    response += f"📋 **التقرير التفصيلي:**\n{report}\n\n"
                
                return response
            else:
                return "عذراً، حدث خطأ في التحليل المالي. يرجى المحاولة مرة أخرى."
                
        except Exception as e:
            self.log(f"❌ Finance error: {e}")
            return "عذراً، لا أستطيع الوصول إلى البيانات المالية حالياً."
    
    def _handle_inventory(self, farm_id: int, farm_context: Dict) -> str:
        """Handle inventory intent using InventoryAgent."""
        try:
            input_data = {
                "farm_id": farm_id,
                "inventory": farm_context.get("inventory", []),
                "crop_type": farm_context.get("crop_type", "general"),
                "area": farm_context.get("area", 1.0)
            }
            
            result = self.inventory_agent.run(input_data)
            
            if result.get("status") == "success":
                data = result.get("data", {})
                report = data.get("report", "")
                summary = data.get("summary", {})
                
                response = f"📦 **تقرير المخزون**\n\n"
                response += f"إجمالي العناصر: {summary.get('total_items', 0)}\n"
                response += f"العناصر منخفضة المخزون: {summary.get('low_stock_items', 0)}\n"
                response += f"العناصر الحرجة: {summary.get('critical_items', 0)}\n"
                response += f"تكلفة إعادة الطلب: {summary.get('estimated_reorder_cost', 0)} جنيه\n\n"
                
                if report:
                    response += f"📋 **التقرير التفصيلي:**\n{report}\n\n"
                
                # Add purchase recommendations
                recommendations = data.get("purchase_recommendations", [])
                if recommendations:
                    response += f"🛒 **توصيات الشراء:**\n"
                    for rec in recommendations[:5]:
                        response += f"- {rec.get('item')}: {rec.get('quantity')} {rec.get('unit')} (أولوية {rec.get('priority')})\n"
                
                return response
            else:
                return "عذراً، حدث خطأ في تحليل المخزون. يرجى المحاولة مرة أخرى."
                
        except Exception as e:
            self.log(f"❌ Inventory error: {e}")
            return "عذراً، لا أستطيع الوصول إلى بيانات المخزون حالياً."
    
    def _handle_workforce(self, farm_id: int, farm_context: Dict) -> str:
        """Handle workforce intent using WorkforceAgent."""
        try:
            input_data = {
                "farm_id": farm_id,
                "workers": farm_context.get("workers", []),
                "tasks": farm_context.get("tasks", []),
                "crop_type": farm_context.get("crop_type", "general"),
                "area": farm_context.get("area", 1.0)
            }
            
            result = self.workforce_agent.run(input_data)
            
            if result.get("status") == "success":
                data = result.get("data", {})
                report = data.get("report", "")
                summary = data.get("summary", {})
                
                response = f"👥 **تقرير القوى العاملة**\n\n"
                response += f"العمال الحاضرون: {summary.get('active_workers', 0)}\n"
                response += f"نسبة الحضور: {summary.get('attendance_rate', 0)}%\n"
                response += f"المهام المكتملة: {summary.get('tasks_completed', 0)}\n"
                response += f"المهام المتأخرة: {summary.get('tasks_overdue', 0)}\n"
                response += f"تكلفة العمالة اليومية: {summary.get('daily_labor_cost', 0)} جنيه\n"
                response += f"كفاءة العمال: {summary.get('efficiency_score', 0)}%\n\n"
                
                if report:
                    response += f"📋 **التقرير التفصيلي:**\n{report}\n\n"
                
                return response
            else:
                return "عذراً، حدث خطأ في تحليل القوى العاملة. يرجى المحاولة مرة أخرى."
                
        except Exception as e:
            self.log(f"❌ Workforce error: {e}")
            return "عذراً، لا أستطيع الوصول إلى بيانات القوى العاملة حالياً."
    
    def _handle_general_query(
        self,
        message: str,
        farm_context: Dict,
        conversation_history: List
    ) -> str:
        """Handle general queries using LLM directly."""
        self.log("💬 Handling general query with LLM")
        
        # Build context from farm data
        context_str = json.dumps(farm_context, ensure_ascii=False)[:500]
        
        # Build conversation history
        history_str = ""
        if conversation_history:
            recent = conversation_history[-3:]  # Last 3 messages
            history_str = "\n".join([
                f"{'مزارع' if h.get('role') == 'user' else 'مساعد'}: {h.get('content', '')}"
                for h in recent
            ])
        
        prompt = f"""
أنت مساعد زراعي ذكي باللغة العربية اسمه "كروب مايند" (CropMind). أنت تتحدث مع مزارع مصري.

بيانات المزرعة الحالية:
{context_str}

محادثة سابقة:
{history_str}

سؤال المزارع:
{message}

المطلوب:
قدم رداً مفيداً ومباشراً باللغة العربية الفصحى أو العامية المصرية (حسب سؤال المزارع).
كن ودوداً ومتفهماً. قدم معلومات دقيقة ومفيدة. إذا كان السؤال خارج نطاق الزراعة، اعتذر بلطف واقترح أسئلة زراعية.

الرد:
"""
        
        response = self.think(prompt)
        return response
    
    def generate_daily_summary(self, farm_context: Dict) -> str:
        """
        Generate a daily summary of the farm.
        
        Args:
            farm_context: Dict with farm data
            
        Returns:
            str: Daily summary in Arabic
        """
        self.log("📝 Generating daily summary")
        
        prompt = f"""
أنت مساعد زراعي ذكي في نظام CropMind.

بيانات المزرعة الحالية:
{json.dumps(farm_context, ensure_ascii=False)[:1000]}

المطلوب:
قم بإنشاء ملخص يومي للمزرعة باللغة العربية يشمل:
1. حالة المحاصيل اليوم
2. حالة الري والموارد
3. نشاط العمال
4. أي توصيات عاجلة
5. خطة العمل للغد

اكتب الملخص بصيغة واضحة ومباشرة مع عناوين فرعية.
"""
        
        summary = self.think(prompt)
        return summary
    
    def chat(
        self,
        message: str,
        farm_context: Dict,
        history: List = None
    ) -> Dict[str, Any]:
        """
        Main chat function for the Farm Copilot.
        
        Args:
            message: User message
            farm_context: Farm data
            history: Conversation history
            
        Returns:
            Dict with response and metadata
        """
        input_data = {
            "farm_id": farm_context.get("farm_id"),
            "message": message,
            "conversation_history": history or [],
            "farm_context": farm_context
        }
        
        result = self.run(input_data)
        
        return {
            "response": result.get("data", {}).get("response", ""),
            "intent": result.get("data", {}).get("intent", ""),
            "timestamp": result.get("data", {}).get("timestamp", "")
        }
