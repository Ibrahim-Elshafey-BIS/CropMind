"""
CropMind - Resource Optimization Agent
Optimizes water, fertilizer, and crop selection for resource efficiency

Author: CropMind Team
Date: 2026
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from ai_engine.agents.base_agent import BaseAgent
from ml_models.model_registry import registry


class ResourceOptimizationAgent(BaseAgent):
    """
    Resource Optimization Agent for water, fertilizer, and crop selection.
    Provides recommendations to reduce resource waste and increase efficiency.
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Initialize the Resource Optimization Agent.
        
        Args:
            groq_api_key: Groq API key (reads from env if None)
        """
        super().__init__(
            agent_name="Resource Optimization Agent",
            description="Reduces water and fertilizer waste through real-time consumption analysis",
            groq_api_key=groq_api_key
        )
        self.log("✅ Resource Optimization Agent initialized")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive resource optimization analysis.
        
        Args:
            input_data: Dict containing:
                - farm_id: int
                - crop_type: str
                - sensor_data: dict with N, P, K, temperature, humidity, ph, rainfall, soil_moisture
                - area: float (area in feddans)
                - current_irrigation: float (current irrigation in mm)
                
        Returns:
            Dict with optimization recommendations
        """
        try:
            farm_id = input_data.get("farm_id")
            crop_type = input_data.get("crop_type", "general")
            sensor_data = input_data.get("sensor_data", {})
            area = input_data.get("area", 1.0)
            current_irrigation = input_data.get("current_irrigation", 0)
            
            self.log(f"🔍 Optimizing resources for farm {farm_id} - Crop: {crop_type}")
            
            # Step 1: Crop recommendation
            crop_recommendation = self._recommend_crop(sensor_data)
            
            # Step 2: Optimize water usage
            water_optimization = self.optimize_water_usage(
                crop_type, sensor_data, current_irrigation
            )
            
            # Step 3: Generate fertilizer schedule
            fertilizer_schedule = self.generate_fertilizer_schedule(
                crop_type, area, sensor_data
            )
            
            # Step 4: Calculate savings
            water_savings = self._calculate_water_savings(
                current_irrigation, water_optimization.get("additional_water_needed_mm", 0)
            )
            
            # Step 5: Generate report
            optimization_data = {
                "farm_id": farm_id,
                "crop_type": crop_type,
                "sensor_data": sensor_data,
                "area": area,
                "crop_recommendation": crop_recommendation,
                "water_optimization": water_optimization,
                "fertilizer_schedule": fertilizer_schedule,
                "water_savings": water_savings
            }
            
            report = self.generate_optimization_report(optimization_data)
            
            return self.format_response({
                "farm_id": farm_id,
                "crop_recommendation": crop_recommendation,
                "water_optimization": water_optimization,
                "fertilizer_schedule": fertilizer_schedule,
                "water_savings": water_savings,
                "report": report,
                "summary": self._generate_summary(optimization_data)
            })
            
        except Exception as e:
            self.log(f"❌ Error in resource optimization: {e}")
            return self.format_error(str(e))
    
    def _recommend_crop(self, sensor_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Recommend the best crop for current conditions.
        
        Args:
            sensor_data: Dict with soil and environmental data
            
        Returns:
            Dict with crop recommendation
        """
        self.log("🌱 Recommending crop...")
        
        try:
            if registry.optimizer:
                # Prepare conditions
                conditions = {
                    "N": sensor_data.get("N", 0),
                    "P": sensor_data.get("P", 0),
                    "K": sensor_data.get("K", 0),
                    "temperature": sensor_data.get("temperature", 25),
                    "humidity": sensor_data.get("humidity", 60),
                    "ph": sensor_data.get("ph", 6.8),
                    "rainfall": sensor_data.get("rainfall", 500)
                }
                
                result = registry.optimizer.recommend_crop(
                    N=conditions["N"],
                    P=conditions["P"],
                    K=conditions["K"],
                    temperature=conditions["temperature"],
                    humidity=conditions["humidity"],
                    ph=conditions["ph"],
                    rainfall=conditions["rainfall"]
                )
                
                return {
                    "recommended_crop": result.get("crop", "wheat"),
                    "confidence": result.get("confidence", 80.0),
                    "requirements": result.get("requirements", {}),
                    "method": result.get("method", "ml_model")
                }
            else:
                # Fallback: simple rule-based recommendation
                return self._rule_based_crop_recommendation(sensor_data)
                
        except Exception as e:
            self.log(f"⚠️ Crop recommendation error: {e}")
            return self._rule_based_crop_recommendation(sensor_data)
    
    def _rule_based_crop_recommendation(self, sensor_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Rule-based crop recommendation fallback.
        """
        rainfall = sensor_data.get("rainfall", 500)
        temperature = sensor_data.get("temperature", 25)
        
        if rainfall > 1000:
            crop = "rice"
        elif rainfall > 600:
            crop = "sugarcane"
        elif rainfall > 400:
            crop = "maize" if temperature > 25 else "wheat"
        else:
            crop = "cotton" if temperature > 28 else "barley"
        
        return {
            "recommended_crop": crop,
            "confidence": 70.0,
            "requirements": {
                "water_mm": 500,
                "N_req": 100,
                "P_req": 50,
                "K_req": 80,
                "growing_days": 100
            },
            "method": "rule_based"
        }
    
    def optimize_water_usage(
        self,
        crop_type: str,
        sensor_data: Dict[str, float],
        current_irrigation: float
    ) -> Dict[str, Any]:
        """
        Optimize water usage for the crop.
        
        Args:
            crop_type: Type of crop
            sensor_data: Dict with soil and environmental data
            current_irrigation: Current irrigation amount in mm
            
        Returns:
            Dict with water optimization recommendations
        """
        self.log(f"💧 Optimizing water usage for {crop_type}")
        
        try:
            if registry.optimizer:
                result = registry.optimizer.optimize_irrigation(
                    crop_name=crop_type,
                    current_humidity=sensor_data.get("humidity", 60),
                    current_rainfall=sensor_data.get("rainfall", 0) / 7  # Daily average
                )
                return result
            else:
                # Fallback: simple water optimization
                return self._rule_based_water_optimization(crop_type, sensor_data, current_irrigation)
                
        except Exception as e:
            self.log(f"⚠️ Water optimization error: {e}")
            return self._rule_based_water_optimization(crop_type, sensor_data, current_irrigation)
    
    def _rule_based_water_optimization(
        self,
        crop_type: str,
        sensor_data: Dict[str, float],
        current_irrigation: float
    ) -> Dict[str, Any]:
        """
        Rule-based water optimization fallback.
        """
        # Water requirements by crop (mm per week)
        water_requirements = {
            "rice": 35,
            "wheat": 25,
            "maize": 30,
            "tomato": 20,
            "potato": 25,
            "onion": 20,
            "cotton": 25,
            "sugarcane": 40,
            "general": 25
        }
        
        required = water_requirements.get(crop_type.lower(), 25)
        rainfall = sensor_data.get("rainfall", 0) / 7  # Weekly average
        humidity = sensor_data.get("humidity", 60)
        
        # Adjust for humidity
        if humidity > 70:
            humidity_factor = 0.7
        elif humidity > 50:
            humidity_factor = 0.9
        else:
            humidity_factor = 1.2
        
        recommended = max(0, required - rainfall * 0.7) * humidity_factor
        
        # Generate recommendations
        if recommended <= 0:
            frequency = "No irrigation needed this week"
        elif recommended < 5:
            frequency = "Light irrigation once"
        elif recommended < 15:
            frequency = "Irrigate 2-3 times"
        elif recommended < 25:
            frequency = "Irrigate 3-4 times"
        else:
            frequency = "Daily irrigation recommended"
        
        return {
            "crop": crop_type,
            "water_needed_mm_weekly": round(required, 1),
            "rainfall_mm_weekly": round(rainfall * 7, 1),
            "additional_water_needed_mm": round(recommended, 1),
            "frequency": frequency,
            "daily_irrigation_mm": round(recommended / 7, 2),
            "days_per_week": min(7, int(round(recommended / 5)) + 1) if recommended > 0 else 0,
            "humidity_factor": humidity_factor,
            "recommendation": "Increase irrigation" if recommended > 20 else "Maintain current" if recommended > 5 else "Reduce irrigation",
            "method": "rule_based"
        }
    
    def generate_fertilizer_schedule(
        self,
        crop_type: str,
        area: float,
        sensor_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Generate a detailed fertilizer schedule.
        
        Args:
            crop_type: Type of crop
            area: Area in feddans
            sensor_data: Dict with soil nutrient data
            
        Returns:
            Dict with fertilizer schedule
        """
        self.log(f"🧪 Generating fertilizer schedule for {crop_type}")
        
        try:
            if registry.optimizer:
                result = registry.optimizer.get_nutrient_plan(
                    crop_name=crop_type,
                    area=area,
                    N=sensor_data.get("N", 0),
                    P=sensor_data.get("P", 0),
                    K=sensor_data.get("K", 0)
                )
                return result
            else:
                return self._rule_based_fertilizer_schedule(crop_type, area, sensor_data)
                
        except Exception as e:
            self.log(f"⚠️ Fertilizer schedule error: {e}")
            return self._rule_based_fertilizer_schedule(crop_type, area, sensor_data)
    
    def _rule_based_fertilizer_schedule(
        self,
        crop_type: str,
        area: float,
        sensor_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Rule-based fertilizer schedule fallback.
        """
        # Requirements per feddan
        requirements = {
            "wheat": {"N": 120, "P": 60, "K": 80},
            "rice": {"N": 120, "P": 60, "K": 60},
            "maize": {"N": 150, "P": 60, "K": 120},
            "tomato": {"N": 180, "P": 80, "K": 200},
            "potato": {"N": 150, "P": 80, "K": 180},
            "onion": {"N": 100, "P": 50, "K": 80},
            "cotton": {"N": 120, "P": 60, "K": 120},
            "sugarcane": {"N": 200, "P": 80, "K": 200},
            "general": {"N": 120, "P": 60, "K": 80}
        }
        
        req = requirements.get(crop_type.lower(), requirements["general"])
        
        # Calculate deficits
        n_deficit = max(0, req["N"] - sensor_data.get("N", 0) * 0.5)
        p_deficit = max(0, req["P"] - sensor_data.get("P", 0) * 0.4)
        k_deficit = max(0, req["K"] - sensor_data.get("K", 0) * 0.4)
        
        # Scale by area
        total_fertilizer = {
            "N": n_deficit * 0.5 * area,
            "P": p_deficit * 0.4 * area,
            "K": k_deficit * 0.4 * area
        }
        
        # Generate schedule
        schedule = []
        if total_fertilizer["N"] > 0:
            schedule.append({
                "week": "Week 1",
                "fertilizer": "Nitrogen",
                "amount": round(total_fertilizer["N"] * 0.5, 1),
                "method": "Broadcast application"
            })
            schedule.append({
                "week": "Week 5",
                "fertilizer": "Nitrogen",
                "amount": round(total_fertilizer["N"] * 0.5, 1),
                "method": "Side dressing"
            })
        
        if total_fertilizer["P"] > 0:
            schedule.append({
                "week": "Week 1",
                "fertilizer": "Phosphorus",
                "amount": round(total_fertilizer["P"], 1),
                "method": "Broadcast before planting"
            })
        
        if total_fertilizer["K"] > 0:
            schedule.append({
                "week": "Week 2",
                "fertilizer": "Potassium",
                "amount": round(total_fertilizer["K"] * 0.6, 1),
                "method": "Broadcast application"
            })
            schedule.append({
                "week": "Week 6",
                "fertilizer": "Potassium",
                "amount": round(total_fertilizer["K"] * 0.4, 1),
                "method": "Side dressing"
            })
        
        return {
            "crop": crop_type,
            "area": area,
            "current_soil": {
                "N": round(sensor_data.get("N", 0), 1),
                "P": round(sensor_data.get("P", 0), 1),
                "K": round(sensor_data.get("K", 0), 1)
            },
            "requirements": req,
            "total_fertilizer_kg": total_fertilizer,
            "schedule": schedule,
            "method": "rule_based"
        }
    
    def _calculate_water_savings(self, current: float, recommended: float) -> Dict[str, Any]:
        """
        Calculate potential water savings.
        
        Args:
            current: Current irrigation amount in mm
            recommended: Recommended irrigation amount in mm
            
        Returns:
            Dict with savings calculations
        """
        if current <= 0:
            return {
                "savings_percentage": 0,
                "savings_mm": 0,
                "status": "No current data"
            }
        
        savings = max(0, current - recommended)
        savings_percentage = (savings / current) * 100 if current > 0 else 0
        
        return {
            "savings_percentage": round(savings_percentage, 1),
            "savings_mm": round(savings, 1),
            "current_usage": round(current, 1),
            "recommended_usage": round(recommended, 1),
            "status": "High savings potential" if savings_percentage > 30 else "Moderate savings" if savings_percentage > 15 else "Low savings"
        }
    
    def generate_optimization_report(self, data: Dict[str, Any]) -> str:
        """
        Generate optimization report in Arabic using LLM.
        
        Args:
            data: Dict with all optimization data
            
        Returns:
            str: Generated report in Arabic
        """
        self.log("📝 Generating optimization report...")
        
        prompt = self._build_report_prompt(data)
        response = self.think(prompt)
        
        return response
    
    def _build_report_prompt(self, data: Dict[str, Any]) -> str:
        """
        Build the prompt for optimization report generation.
        """
        crop = data.get("crop_type", "غير معروف")
        area = data.get("area", 0)
        water_opt = data.get("water_optimization", {})
        fertilizer = data.get("fertilizer_schedule", {})
        savings = data.get("water_savings", {})
        
        prompt = f"""
أنت خبير زراعي ذكي في نظام CropMind متخصص في تحسين الموارد الزراعية.

البيانات المتاحة:
- المحصول الحالي: {crop}
- المساحة: {area} فدان
- الاحتياج المائي: {water_opt.get('water_needed_mm_weekly', 'N/A')} مم/أسبوع
- الأمطار: {water_opt.get('rainfall_mm_weekly', 'N/A')} مم/أسبوع
- المياه الإضافية المطلوبة: {water_opt.get('additional_water_needed_mm', 'N/A')} مم
- جدول الري المقترح: {water_opt.get('frequency', 'N/A')}
- توفير المياه المتوقع: {savings.get('savings_percentage', 0)}%

المطلوب:
اكتب تقريراً مفصلاً باللغة العربية عن تحسين الموارد للمزرعة يشمل:
1. تحليل الوضع الحالي للموارد
2. خطة تحسين الري المقترحة
3. خطة التسميد المقترحة
4. التوفير المتوقع في المياه والأسمدة
5. خطوات تنفيذية عملية للمزارع

اكتب التقرير بصيغة واضحة ومباشرة مع نصائح عملية.
"""
        return prompt
    
    def _generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a quick summary of optimization results.
        """
        water_opt = data.get("water_optimization", {})
        fertilizer = data.get("fertilizer_schedule", {})
        savings = data.get("water_savings", {})
        
        return {
            "recommended_water_mm": water_opt.get("additional_water_needed_mm", 0),
            "irrigation_frequency": water_opt.get("frequency", "N/A"),
            "fertilizer_total_kg": fertilizer.get("total_fertilizer_kg", {}),
            "water_savings_percent": savings.get("savings_percentage", 0),
            "status": "Optimized" if savings.get("savings_percentage", 0) > 10 else "Needs improvement"
        }
