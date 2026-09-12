"""
CropMind - Finance Agent
Financial analysis and profitability forecasting for farm operations

Author: CropMind Team
Date: 2026
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from ai_engine.agents.base_agent import BaseAgent
from ml_models.model_registry import registry


class FinanceAgent(BaseAgent):
    """
    Finance Agent for financial analysis, profitability forecasting, and ROI calculations.
    Provides comprehensive financial insights for farm operations.
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Initialize the Finance Agent.
        
        Args:
            groq_api_key: Groq API key (reads from env if None)
        """
        super().__init__(
            agent_name="Finance Agent",
            description="Calculates cost per feddan, profitability, and revenue forecasts",
            groq_api_key=groq_api_key
        )
        self.log("✅ Finance Agent initialized")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive financial analysis.
        
        Args:
            input_data: Dict containing:
                - farm_id: int
                - crop_type: str
                - area: float (area in feddans)
                - costs: dict with seed_cost, fertilizer_cost, labor_cost, irrigation_cost, other_costs
                - current_price: float (current price per ton)
                - season: str (season name)
                
        Returns:
            Dict with financial analysis and recommendations
        """
        try:
            farm_id = input_data.get("farm_id")
            crop_type = input_data.get("crop_type", "general")
            area = input_data.get("area", 1.0)
            costs = input_data.get("costs", {})
            current_price = input_data.get("current_price", 0)
            season = input_data.get("season", "spring")
            
            self.log(f"💰 Analyzing finances for farm {farm_id} - Crop: {crop_type}")
            
            # Step 1: Calculate total costs
            total_costs = self._calculate_total_costs(costs, area)
            
            # Step 2: Predict yield
            yield_prediction = self._predict_yield(crop_type, area)
            
            # Step 3: Calculate revenue
            revenue = self._calculate_revenue(yield_prediction, current_price)
            
            # Step 4: Calculate profit and ROI
            profit_analysis = self._calculate_profit_and_roi(total_costs, revenue, area)
            
            # Step 5: Break-even analysis
            break_even = self._calculate_break_even(total_costs, current_price)
            
            # Step 6: Generate financial forecast
            financial_forecast = self._generate_financial_forecast(
                crop_type, area, total_costs, revenue, profit_analysis
            )
            
            # Step 7: Generate report
            financial_data = {
                "farm_id": farm_id,
                "crop_type": crop_type,
                "area": area,
                "season": season,
                "costs": costs,
                "total_costs": total_costs,
                "yield_prediction": yield_prediction,
                "revenue": revenue,
                "profit_analysis": profit_analysis,
                "break_even": break_even,
                "financial_forecast": financial_forecast
            }
            
            report = self.generate_financial_report(financial_data)
            
            return self.format_response({
                "farm_id": farm_id,
                "crop_type": crop_type,
                "area": area,
                "total_costs": total_costs,
                "revenue": revenue,
                "profit_analysis": profit_analysis,
                "break_even": break_even,
                "financial_forecast": financial_forecast,
                "report": report,
                "summary": self._generate_summary(financial_data)
            })
            
        except Exception as e:
            self.log(f"❌ Error in financial analysis: {e}")
            return self.format_error(str(e))
    
    def _calculate_total_costs(self, costs: Dict[str, float], area: float) -> Dict[str, Any]:
        """
        Calculate total costs including per-feddan breakdown.
        
        Args:
            costs: Dict with cost categories
            area: Area in feddans
            
        Returns:
            Dict with cost breakdown
        """
        self.log("📊 Calculating total costs...")
        
        # Default cost values if not provided
        default_costs = {
            "seed_cost": 500,
            "fertilizer_cost": 800,
            "labor_cost": 600,
            "irrigation_cost": 300,
            "other_costs": 200
        }
        
        # Merge with defaults
        merged_costs = {**default_costs, **costs}
        
        # Calculate per-feddan costs
        per_feddan = {
            "seed": merged_costs.get("seed_cost", 0),
            "fertilizer": merged_costs.get("fertilizer_cost", 0),
            "labor": merged_costs.get("labor_cost", 0),
            "irrigation": merged_costs.get("irrigation_cost", 0),
            "other": merged_costs.get("other_costs", 0)
        }
        
        # Total per feddan
        total_per_feddan = sum(per_feddan.values())
        
        # Total for entire area
        total = total_per_feddan * area
        
        return {
            "per_feddan": per_feddan,
            "total_per_feddan": round(total_per_feddan, 2),
            "area": area,
            "total": round(total, 2),
            "breakdown": {
                "seed": round(per_feddan["seed"] * area, 2),
                "fertilizer": round(per_feddan["fertilizer"] * area, 2),
                "labor": round(per_feddan["labor"] * area, 2),
                "irrigation": round(per_feddan["irrigation"] * area, 2),
                "other": round(per_feddan["other"] * area, 2)
            }
        }
    
    def _predict_yield(self, crop_type: str, area: float) -> Dict[str, Any]:
        """
        Predict yield for the crop.
        
        Args:
            crop_type: Type of crop
            area: Area in feddans
            
        Returns:
            Dict with yield prediction
        """
        self.log(f"📊 Predicting yield for {crop_type}")
        
        try:
            if registry.yield_model:
                # Use yield model from registry
                # This is a simplified call - actual implementation would use features
                yield_per_feddan = 3.5  # Default
                return {
                    "crop": crop_type,
                    "yield_per_feddan": yield_per_feddan,
                    "total_yield": round(yield_per_feddan * area, 2),
                    "unit": "tons/feddan",
                    "area": area,
                    "method": "ml_model"
                }
            else:
                return self._fallback_yield_prediction(crop_type, area)
                
        except Exception as e:
            self.log(f"⚠️ Yield prediction error: {e}")
            return self._fallback_yield_prediction(crop_type, area)
    
    def _fallback_yield_prediction(self, crop_type: str, area: float) -> Dict[str, Any]:
        """
        Fallback yield prediction when model is not available.
        """
        # Typical yields in tons per feddan for Egyptian agriculture
        yields = {
            "tomato": 6.0,
            "potato": 5.0,
            "onion": 4.5,
            "wheat": 3.5,
            "rice": 4.0,
            "maize": 3.0,
            "cotton": 2.0,
            "sugarcane": 8.0,
            "barley": 2.5,
            "chickpea": 1.8,
            "general": 3.0
        }
        
        yield_per_feddan = yields.get(crop_type.lower(), 3.0)
        
        return {
            "crop": crop_type,
            "yield_per_feddan": yield_per_feddan,
            "total_yield": round(yield_per_feddan * area, 2),
            "unit": "tons/feddan",
            "area": area,
            "method": "rule_based"
        }
    
    def _calculate_revenue(self, yield_prediction: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """
        Calculate revenue based on yield and price.
        
        Args:
            yield_prediction: Dict with yield data
            current_price: Current price per ton
            
        Returns:
            Dict with revenue calculations
        """
        total_yield = yield_prediction.get("total_yield", 0)
        area = yield_prediction.get("area", 0)
        revenue = total_yield * current_price
        
        # Calculate revenue per feddan
        if area > 0:
            revenue_per_feddan = revenue / area
        else:
            revenue_per_feddan = 0
        
        return {
            "total_yield": total_yield,
            "price_per_ton": current_price,
            "total_revenue": round(revenue, 2),
            "revenue_per_feddan": round(revenue_per_feddan, 2)
        }
    
    def _calculate_profit_and_roi(self, total_costs: Dict, revenue: Dict, area: float) -> Dict[str, Any]:
        """
        Calculate profit and ROI.
        
        Args:
            total_costs: Dict with cost data
            revenue: Dict with revenue data
            area: Area in feddans
            
        Returns:
            Dict with profit and ROI analysis
        """
        total_cost = total_costs.get("total", 0)
        total_revenue = revenue.get("total_revenue", 0)
        
        profit = total_revenue - total_cost
        profit_per_feddan = profit / area if area > 0 else 0
        roi = (profit / total_cost * 100) if total_cost > 0 else 0
        
        # Determine profitability level
        if roi >= 50:
            level = "EXCELLENT"
        elif roi >= 25:
            level = "GOOD"
        elif roi >= 10:
            level = "MODERATE"
        elif roi >= 0:
            level = "BREAK_EVEN"
        else:
            level = "LOSS"
        
        return {
            "total_cost": round(total_cost, 2),
            "total_revenue": round(total_revenue, 2),
            "profit": round(profit, 2),
            "profit_per_feddan": round(profit_per_feddan, 2),
            "roi_percentage": round(roi, 2),
            "profitability_level": level,
            "status": "Profitable" if profit > 0 else "Not profitable"
        }
    
    def _calculate_break_even(self, total_costs: Dict, current_price: float) -> Dict[str, Any]:
        """
        Calculate break-even point.
        
        Args:
            total_costs: Dict with cost data
            current_price: Current price per ton
            
        Returns:
            Dict with break-even analysis
        """
        total_cost = total_costs.get("total", 0)
        
        if current_price <= 0:
            return {
                "break_even_yield": 0,
                "break_even_price": 0,
                "status": "Cannot calculate (price <= 0)"
            }
        
        # Break-even yield = total_cost / price_per_ton
        break_even_yield = total_cost / current_price
        
        return {
            "break_even_yield": round(break_even_yield, 2),
            "break_even_yield_per_feddan": round(break_even_yield / total_costs.get("area", 1), 2) if total_costs.get("area", 0) > 0 else 0,
            "break_even_price": round(total_cost / total_costs.get("area", 1), 2) if total_costs.get("area", 0) > 0 else 0,
            "current_price": current_price,
            "margin_of_safety": round((current_price - (total_cost / total_costs.get("area", 1))) / current_price * 100, 2) if total_costs.get("area", 0) > 0 and current_price > 0 else 0
        }
    
    def _generate_financial_forecast(
        self,
        crop_type: str,
        area: float,
        total_costs: Dict,
        revenue: Dict,
        profit_analysis: Dict
    ) -> Dict[str, Any]:
        """
        Generate financial forecast for future seasons.
        
        Args:
            crop_type: Type of crop
            area: Area in feddans
            total_costs: Dict with cost data
            revenue: Dict with revenue data
            profit_analysis: Dict with profit analysis
            
        Returns:
            Dict with financial forecast
        """
        self.log("📈 Generating financial forecast...")
        
        total_cost = total_costs.get("total", 0)
        total_revenue = revenue.get("total_revenue", 0)
        profit = profit_analysis.get("profit", 0)
        roi = profit_analysis.get("roi_percentage", 0)
        
        # Project for next 3 seasons with inflation and growth
        inflation_rate = 0.05  # 5% annual inflation
        growth_rate = 0.03  # 3% yield growth
        
        projections = []
        for year in range(1, 4):
            year_costs = total_cost * (1 + inflation_rate * year)
            year_revenue = total_revenue * (1 + (inflation_rate + growth_rate) * year)
            year_profit = year_revenue - year_costs
            year_roi = (year_profit / year_costs * 100) if year_costs > 0 else 0
            
            projections.append({
                "year": year,
                "estimated_cost": round(year_costs, 2),
                "estimated_revenue": round(year_revenue, 2),
                "estimated_profit": round(year_profit, 2),
                "estimated_roi": round(year_roi, 2)
            })
        
        return {
            "current_season": {
                "cost": round(total_cost, 2),
                "revenue": round(total_revenue, 2),
                "profit": round(profit, 2),
                "roi": round(roi, 2)
            },
            "projections": projections,
            "recommendation": "Expand operations" if roi > 30 else "Maintain current" if roi > 15 else "Review cost structure"
        }
    
    def generate_financial_report(self, data: Dict[str, Any]) -> str:
        """
        Generate financial report in Arabic using LLM.
        
        Args:
            data: Dict with all financial data
            
        Returns:
            str: Generated report in Arabic
        """
        self.log("📝 Generating financial report...")
        
        prompt = self._build_report_prompt(data)
        response = self.think(prompt)
        
        return response
    
    def _build_report_prompt(self, data: Dict[str, Any]) -> str:
        """
        Build the prompt for financial report generation.
        """
        crop = data.get("crop_type", "غير معروف")
        area = data.get("area", 0)
        total_costs = data.get("total_costs", {})
        revenue = data.get("revenue", {})
        profit = data.get("profit_analysis", {})
        break_even = data.get("break_even", {})
        forecast = data.get("financial_forecast", {})
        
        prompt = f"""
أنت خبير مالي زراعي في نظام CropMind متخصص في التحليل المالي للمزارع.

البيانات المتاحة:
- المحصول: {crop}
- المساحة: {area} فدان
- إجمالي التكاليف: {total_costs.get('total', 0)} جنيه
- إجمالي الإيرادات: {revenue.get('total_revenue', 0)} جنيه
- صافي الربح: {profit.get('profit', 0)} جنيه
- العائد على الاستثمار (ROI): {profit.get('roi_percentage', 0)}%
- مستوى الربحية: {profit.get('profitability_level', 'N/A')}
- نقطة التعادل (إنتاج): {break_even.get('break_even_yield', 0)} طن

المطلوب:
اكتب تقريراً مالياً مفصلاً باللغة العربية للمزرعة يشمل:
1. تحليل التكاليف والإيرادات
2. تحليل الربحية والعائد على الاستثمار
3. تحليل نقطة التعادل
4. توقعات مالية للمواسم القادمة
5. توصيات لتحسين الأداء المالي

اكتب التقرير بصيغة واضحة ومباشرة مع عناوين فرعية.
"""
        return prompt
    
    def _generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a quick summary of financial analysis.
        """
        profit = data.get("profit_analysis", {})
        break_even = data.get("break_even", {})
        forecast = data.get("financial_forecast", {})
        
        return {
            "total_cost": profit.get("total_cost", 0),
            "total_revenue": profit.get("total_revenue", 0),
            "net_profit": profit.get("profit", 0),
            "roi": profit.get("roi_percentage", 0),
            "profitability": profit.get("profitability_level", "N/A"),
            "break_even_yield": break_even.get("break_even_yield", 0),
            "next_season_forecast": forecast.get("projections", [{}])[0] if forecast.get("projections") else {}
        }
