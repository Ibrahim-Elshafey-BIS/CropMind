"""
CropMind - Market Intelligence Agent
Analyzes market conditions, forecasts prices, and provides selling recommendations

Author: CropMind Team
Date: 2026
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ai_engine.agents.base_agent import BaseAgent
from ml_models.model_registry import registry


class MarketIntelligenceAgent(BaseAgent):
    """
    Market Intelligence Agent for price forecasting and market recommendations.
    Provides sell/hold/store decisions based on market analysis.
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Initialize the Market Intelligence Agent.
        
        Args:
            groq_api_key: Groq API key (reads from env if None)
        """
        super().__init__(
            agent_name="Market Intelligence Agent",
            description="Monitors commodity prices; recommends optimal sell, store, or produce decisions",
            groq_api_key=groq_api_key
        )
        self.log("✅ Market Intelligence Agent initialized")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive market intelligence analysis.
        
        Args:
            input_data: Dict containing:
                - farm_id: int
                - crop_type: str
                - current_price: float (current market price)
                - quantity: float (available quantity in tons)
                - storage_cost: float (daily storage cost per ton)
                - harvest_date: Optional[str] (expected harvest date)
                
        Returns:
            Dict with market recommendations and forecasts
        """
        try:
            farm_id = input_data.get("farm_id")
            crop_type = input_data.get("crop_type")
            current_price = input_data.get("current_price", 0)
            quantity = input_data.get("quantity", 0)
            storage_cost = input_data.get("storage_cost", 0.5)
            harvest_date = input_data.get("harvest_date")
            
            self.log(f"📊 Analyzing market for {crop_type} (Farm {farm_id})")
            
            # Step 1: Get price forecast
            price_forecast = self._get_price_forecast(crop_type)
            
            # Step 2: Get demand signal
            demand_signal = self._get_demand_signal(crop_type)
            
            # Step 3: Get sell recommendation
            sell_recommendation = self.get_sell_recommendation(
                crop=crop_type,
                current_price=current_price,
                quantity=quantity,
                storage_cost=storage_cost,
                price_forecast=price_forecast
            )
            
            # Step 4: Analyze market trends
            market_trends = self.analyze_market_trends(crop_type)
            
            # Step 5: Generate report
            market_data = {
                "farm_id": farm_id,
                "crop_type": crop_type,
                "current_price": current_price,
                "quantity": quantity,
                "storage_cost": storage_cost,
                "harvest_date": harvest_date,
                "price_forecast": price_forecast,
                "demand_signal": demand_signal,
                "sell_recommendation": sell_recommendation,
                "market_trends": market_trends
            }
            
            report = self.generate_market_report(market_data)
            
            return self.format_response({
                "farm_id": farm_id,
                "crop_type": crop_type,
                "current_price": current_price,
                "price_forecast": price_forecast,
                "demand_signal": demand_signal,
                "recommendation": sell_recommendation,
                "market_trends": market_trends,
                "report": report,
                "summary": self._generate_summary(market_data)
            })
            
        except Exception as e:
            self.log(f"❌ Error in market analysis: {e}")
            return self.format_error(str(e))
    
    def _get_price_forecast(self, crop: str) -> Dict[str, Any]:
        """
        Get price forecast for a crop using PriceForecaster.
        
        Args:
            crop: Crop name
            
        Returns:
            Dict with price forecast
        """
        self.log(f"📈 Getting price forecast for {crop}")
        
        try:
            if registry.price:
                # Use PriceForecaster
                forecast = registry.price.forecast_commodity(crop, days=90)
                return forecast
            else:
                return self._fallback_price_forecast(crop)
                
        except Exception as e:
            self.log(f"⚠️ Price forecast error: {e}")
            return self._fallback_price_forecast(crop)
    
    def _fallback_price_forecast(self, crop: str) -> Dict[str, Any]:
        """
        Fallback price forecast when model is not available.
        """
        base_prices = {
            "tomato": 35,
            "onion": 25,
            "potato": 18,
            "wheat": 15,
            "cotton": 55,
            "sugarcane": 12,
            "rice": 22,
            "maize": 16,
            "general": 20
        }
        
        base = base_prices.get(crop.lower(), 20)
        
        # Generate 12-week forecast with seasonal pattern
        weekly_forecast = []
        for i in range(12):
            week = i + 1
            # Simple seasonal pattern
            seasonal = 1 + 0.15 * (1 + i % 4) / 4
            price = base * seasonal * (1 + 0.02 * (i / 6))
            weekly_forecast.append({
                "week": week,
                "price": round(price, 2),
                "week_start": (datetime.now() + timedelta(days=week*7)).strftime("%Y-%m-%d")
            })
        
        # Determine trend
        if weekly_forecast:
            first = weekly_forecast[0]["price"]
            last = weekly_forecast[-1]["price"]
            trend = "increasing" if last > first else "decreasing" if last < first else "stable"
            max_price = max(w["price"] for w in weekly_forecast)
            max_week = next((w["week"] for w in weekly_forecast if w["price"] == max_price), 6)
        else:
            trend = "stable"
            max_price = base
            max_week = 6
        
        return {
            "crop": crop,
            "weekly_forecast": weekly_forecast,
            "trend": trend,
            "max_expected_price": round(max_price, 2),
            "max_week": max_week,
            "current_price": base,
            "method": "fallback"
        }
    
    def _get_demand_signal(self, crop: str) -> Dict[str, Any]:
        """
        Get demand signal for a crop using DemandForecaster.
        
        Args:
            crop: Crop name
            
        Returns:
            Dict with demand signal
        """
        self.log(f"📊 Getting demand signal for {crop}")
        
        try:
            if registry.demand:
                signal = registry.demand.get_demand_signal(crop)
                return signal
            else:
                return self._fallback_demand_signal(crop)
                
        except Exception as e:
            self.log(f"⚠️ Demand signal error: {e}")
            return self._fallback_demand_signal(crop)
    
    def _fallback_demand_signal(self, crop: str) -> Dict[str, Any]:
        """
        Fallback demand signal when model is not available.
        """
        base_demand = {
            "tomato": 500,
            "onion": 400,
            "potato": 450,
            "wheat": 1000,
            "cotton": 200,
            "sugarcane": 300,
            "rice": 1200,
            "maize": 800,
            "general": 500
        }
        
        base = base_demand.get(crop.lower(), 500)
        
        # Simulate demand signal
        import random
        random.seed(hash(crop) % 1000)
        variation = 0.8 + 0.4 * random.random()
        forecast_value = base * variation
        
        if forecast_value > base * 1.3:
            signal = "HIGH"
            explanation = f"High demand expected for {crop}"
        elif forecast_value > base * 0.8:
            signal = "MEDIUM"
            explanation = f"Stable demand for {crop}"
        else:
            signal = "LOW"
            explanation = f"Low demand expected for {crop}"
        
        return {
            "crop": crop,
            "signal": signal,
            "forecast_value": round(forecast_value, 2),
            "baseline": base,
            "explanation": explanation,
            "trend": "stable",
            "change_percent": round((forecast_value / base - 1) * 100, 2)
        }
    
    def get_sell_recommendation(
        self,
        crop: str,
        current_price: float,
        quantity: float,
        storage_cost: float,
        price_forecast: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get sell/hold/store recommendation based on market analysis.
        
        Args:
            crop: Crop name
            current_price: Current market price per ton
            quantity: Available quantity in tons
            storage_cost: Daily storage cost per ton
            price_forecast: Price forecast data
            
        Returns:
            Dict with recommendation
        """
        self.log(f"💰 Generating sell recommendation for {crop}")
        
        if price_forecast is None:
            price_forecast = self._get_price_forecast(crop)
        
        # Get demand signal
        demand_signal = self._get_demand_signal(crop)
        demand_level = demand_signal.get("signal", "MEDIUM")
        
        # Extract forecast data
        weekly_forecast = price_forecast.get("weekly_forecast", [])
        max_price = price_forecast.get("max_expected_price", current_price)
        max_week = price_forecast.get("max_week", 6)
        trend = price_forecast.get("trend", "stable")
        
        # Calculate storage cost for 12 weeks
        total_storage_cost = storage_cost * quantity * 12
        
        # Calculate potential gain if holding
        price_gain = max(0, max_price - current_price) * quantity
        net_gain = price_gain - total_storage_cost
        
        # Make recommendation
        if demand_level == "HIGH" and trend == "increasing" and net_gain > 0:
            recommendation = "HOLD"
            action = "⏳ Hold for better prices"
            reasoning = f"Demand is HIGH and prices are trending up. Potential gain: {net_gain:.2f} EGP"
        elif trend == "decreasing" or demand_level == "LOW":
            recommendation = "SELL"
            action = "💰 Sell now"
            reasoning = f"Prices are trending down or demand is LOW. Current price: {current_price:.2f} EGP/ton"
        elif net_gain > 0 and max_week <= 8:
            recommendation = "STORE"
            action = "📦 Store temporarily"
            reasoning = f"Prices expected to peak in {max_week} weeks. Net gain: {net_gain:.2f} EGP"
        else:
            recommendation = "SELL"
            action = "💸 Sell now (limited gain potential)"
            reasoning = f"Storage costs outweigh potential price gains. Current price: {current_price:.2f} EGP/ton"
        
        # Calculate optimal sell time
        optimal_week = max_week if recommendation != "SELL" else 1
        
        # Calculate expected profit
        expected_price = max_price if recommendation != "SELL" else current_price
        expected_revenue = expected_price * quantity
        storage_cost_actual = storage_cost * quantity * (optimal_week - 1) if optimal_week > 1 else 0
        expected_profit = expected_revenue - storage_cost_actual
        
        return {
            "crop": crop,
            "recommendation": recommendation,
            "action": action,
            "reasoning": reasoning,
            "optimal_sell_week": optimal_week,
            "optimal_sell_price": round(expected_price, 2),
            "current_price": current_price,
            "quantity": quantity,
            "expected_revenue": round(expected_revenue, 2),
            "storage_cost": round(storage_cost_actual, 2),
            "expected_profit": round(expected_profit, 2),
            "net_gain_vs_sell_now": round(net_gain, 2),
            "demand_signal": demand_level,
            "market_trend": trend
        }
    
    def analyze_market_trends(self, crop: str) -> Dict[str, Any]:
        """
        Analyze market trends for a crop.
        
        Args:
            crop: Crop name
            
        Returns:
            Dict with market trend analysis
        """
        self.log(f"📊 Analyzing market trends for {crop}")
        
        # Get price forecast
        price_forecast = self._get_price_forecast(crop)
        
        # Get demand signal
        demand_signal = self._get_demand_signal(crop)
        
        # Analyze seasonality
        import random
        random.seed(hash(crop + "season") % 1000)
        seasonal_pattern = {
            "peak_months": [1, 2, 3, 7, 8, 9],
            "low_months": [4, 5, 6, 10, 11, 12],
            "peak_factor": 1.25,
            "low_factor": 0.75
        }
        
        # Determine market sentiment
        trend = price_forecast.get("trend", "stable")
        demand = demand_signal.get("signal", "MEDIUM")
        
        if trend == "increasing" and demand in ["HIGH", "MEDIUM"]:
            sentiment = "BULLISH"
            sentiment_text = "Strong market conditions. Prices expected to rise."
        elif trend == "decreasing" or demand == "LOW":
            sentiment = "BEARISH"
            sentiment_text = "Weak market conditions. Prices expected to decline."
        else:
            sentiment = "NEUTRAL"
            sentiment_text = "Stable market conditions."
        
        return {
            "crop": crop,
            "sentiment": sentiment,
            "sentiment_text": sentiment_text,
            "trend": trend,
            "demand_signal": demand,
            "seasonal_pattern": seasonal_pattern,
            "price_forecast_summary": {
                "expected_high": price_forecast.get("max_expected_price", 0),
                "expected_low": price_forecast.get("current_price", 0),
                "weeks_to_peak": price_forecast.get("max_week", 6)
            },
            "risk_level": "LOW" if sentiment == "BULLISH" else "HIGH" if sentiment == "BEARISH" else "MEDIUM"
        }
    
    def generate_market_report(self, data: Dict[str, Any]) -> str:
        """
        Generate market report in Arabic using LLM.
        
        Args:
            data: Dict with all market data
            
        Returns:
            str: Generated report in Arabic
        """
        self.log("📝 Generating market report...")
        
        prompt = self._build_report_prompt(data)
        response = self.think(prompt)
        
        return response
    
    def _build_report_prompt(self, data: Dict[str, Any]) -> str:
        """
        Build the prompt for market report generation.
        """
        crop = data.get("crop_type", "غير معروف")
        current_price = data.get("current_price", 0)
        recommendation = data.get("sell_recommendation", {})
        forecast = data.get("price_forecast", {})
        demand = data.get("demand_signal", {})
        trends = data.get("market_trends", {})
        max_price = forecast.get("max_expected_price", current_price)
        max_week = forecast.get("max_week", 6)
        
        prompt = f"""
أنت خبير أسواق زراعية ذكي في نظام CropMind متخصص في تحليل الأسواق وتقديم توصيات البيع.

البيانات المتاحة:
- المحصول: {crop}
- السعر الحالي: {current_price} جنيه/طن
- السعر المتوقع الأعلى: {max_price} جنيه/طن (بعد {max_week} أسبوع)
- اتجاه السوق: {trends.get('sentiment', 'NEUTRAL')}
- إشارة الطلب: {demand.get('signal', 'MEDIUM')}
- التوصية: {recommendation.get('action', 'N/A')}
- سبب التوصية: {recommendation.get('reasoning', 'N/A')}
- الربح المتوقع: {recommendation.get('expected_profit', 0)} جنيه

المطلوب:
اكتب تقريراً مفصلاً باللغة العربية عن وضع السوق للمحصول {crop} يشمل:
1. تحليل اتجاهات السوق الحالية
2. توقعات الأسعار للأشهر القادمة
3. تحليل الطلب والعرض
4. توصية واضحة: هل يبيع المزارع الآن أم يحتفظ بالمحصول
5. خطة عمل مقترحة لتحقيق أقصى ربح

اكتب التقرير بصيغة واضحة ومباشرة مع عناوين فرعية.
"""
        return prompt
    
    def _generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a quick summary of market analysis.
        """
        recommendation = data.get("sell_recommendation", {})
        forecast = data.get("price_forecast", {})
        demand = data.get("demand_signal", {})
        
        return {
            "current_price": data.get("current_price", 0),
            "expected_high_price": forecast.get("max_expected_price", 0),
            "weeks_to_peak": forecast.get("max_week", 6),
            "demand_signal": demand.get("signal", "MEDIUM"),
            "recommendation": recommendation.get("recommendation", "SELL"),
            "expected_profit": recommendation.get("expected_profit", 0),
            "action": recommendation.get("action", "Sell now")
        }
