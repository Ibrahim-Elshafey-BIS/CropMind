"""
CropMind - Resource Optimization Module
Crop recommendation and resource optimization for farm management

Author: CropMind Team
Date: 2026
"""

import os
import pickle
import numpy as np
from typing import Dict, Optional, Tuple, Any


class ResourceOptimizer:
    """
    Resource Optimization class for crop recommendation and planning.
    Provides recommendations for crop selection, irrigation, and fertilization.
    """
    
    def __init__(self, models_path: str = "ml_models/resource_optimization/models"):
        """
        Initialize the ResourceOptimizer and load trained models.
        
        Args:
            models_path: Path to the directory containing model files
        """
        self.models_path = models_path
        self.model = None
        self.feature_names = None
        self.crop_classes = None
        
        # Hardcoded crop requirements (realistic values for Egyptian agriculture)
        self.crop_requirements = {
            "rice": {
                "water_mm": 1200,
                "N_req": 120,
                "P_req": 60,
                "K_req": 60,
                "growing_days": 120,
                "optimal_temp": (20, 35),
                "optimal_humidity": (60, 85),
                "optimal_ph": (6.0, 7.5),
            },
            "wheat": {
                "water_mm": 450,
                "N_req": 120,
                "P_req": 60,
                "K_req": 80,
                "growing_days": 120,
                "optimal_temp": (15, 25),
                "optimal_humidity": (50, 75),
                "optimal_ph": (6.0, 7.5),
            },
            "maize": {
                "water_mm": 500,
                "N_req": 150,
                "P_req": 60,
                "K_req": 120,
                "growing_days": 100,
                "optimal_temp": (20, 32),
                "optimal_humidity": (60, 80),
                "optimal_ph": (5.5, 7.0),
            },
            "potato": {
                "water_mm": 400,
                "N_req": 150,
                "P_req": 80,
                "K_req": 180,
                "growing_days": 90,
                "optimal_temp": (15, 22),
                "optimal_humidity": (70, 85),
                "optimal_ph": (5.5, 6.5),
            },
            "tomato": {
                "water_mm": 600,
                "N_req": 180,
                "P_req": 80,
                "K_req": 200,
                "growing_days": 80,
                "optimal_temp": (20, 28),
                "optimal_humidity": (65, 80),
                "optimal_ph": (6.0, 7.0),
            },
            "onion": {
                "water_mm": 350,
                "N_req": 100,
                "P_req": 50,
                "K_req": 80,
                "growing_days": 120,
                "optimal_temp": (15, 25),
                "optimal_humidity": (60, 75),
                "optimal_ph": (6.0, 7.5),
            },
            "cotton": {
                "water_mm": 600,
                "N_req": 120,
                "P_req": 60,
                "K_req": 120,
                "growing_days": 150,
                "optimal_temp": (25, 35),
                "optimal_humidity": (50, 70),
                "optimal_ph": (6.0, 7.5),
            },
            "sugarcane": {
                "water_mm": 1800,
                "N_req": 200,
                "P_req": 80,
                "K_req": 200,
                "growing_days": 330,
                "optimal_temp": (25, 35),
                "optimal_humidity": (60, 80),
                "optimal_ph": (6.0, 7.5),
            },
            "barley": {
                "water_mm": 350,
                "N_req": 80,
                "P_req": 40,
                "K_req": 60,
                "growing_days": 100,
                "optimal_temp": (15, 25),
                "optimal_humidity": (50, 70),
                "optimal_ph": (6.0, 7.5),
            },
            "chickpea": {
                "water_mm": 300,
                "N_req": 40,
                "P_req": 40,
                "K_req": 40,
                "growing_days": 100,
                "optimal_temp": (20, 30),
                "optimal_humidity": (50, 70),
                "optimal_ph": (6.0, 7.5),
            },
        }
        
        self._load_models()
    
    def _load_models(self) -> None:
        """
        Load trained models from disk.
        """
        model_path = os.path.join(self.models_path, "crop_recommendation_model.pkl")
        features_path = os.path.join(self.models_path, "feature_names.pkl")
        classes_path = os.path.join(self.models_path, "crop_classes.pkl")
        
        try:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print("✅ Crop recommendation model loaded")
            else:
                print("⚠️ Crop recommendation model not found. Using rule-based fallback.")
            
            if os.path.exists(features_path):
                with open(features_path, 'rb') as f:
                    self.feature_names = pickle.load(f)
                print("✅ Feature names loaded")
            
            if os.path.exists(classes_path):
                with open(classes_path, 'rb') as f:
                    self.crop_classes = pickle.load(f)
                print("✅ Crop classes loaded")
                
        except Exception as e:
            print(f"⚠️ Error loading models: {e}")
            self.model = None
    
    def recommend_crop(
        self,
        N: float,
        P: float,
        K: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float
    ) -> Dict[str, Any]:
        """
        Recommend the best crop based on soil and environmental conditions.
        
        Args:
            N: Nitrogen level (ppm)
            P: Phosphorus level (ppm)
            K: Potassium level (ppm)
            temperature: Temperature in Celsius
            humidity: Humidity percentage
            ph: Soil pH level
            rainfall: Rainfall in mm
            
        Returns:
            Dict with recommended crop and confidence score
        """
        # Prepare input features
        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        
        # Check if model is available
        if self.model is not None and self.crop_classes is not None:
            try:
                # Predict using ML model
                prediction = self.model.predict(features)[0]
                probabilities = self.model.predict_proba(features)[0]
                confidence = float(np.max(probabilities) * 100)
                
                # Map prediction to crop name
                if isinstance(self.crop_classes, list):
                    crop_name = self.crop_classes[prediction]
                else:
                    crop_name = str(prediction)
                
                # Get resource requirements
                requirements = self.get_resource_requirements(crop_name)
                
                return {
                    "crop": crop_name,
                    "confidence": round(confidence, 2),
                    "requirements": requirements,
                    "method": "ml_model"
                }
            except Exception as e:
                print(f"⚠️ ML prediction failed: {e}. Using rule-based fallback.")
        
        # Rule-based fallback
        return self._recommend_crop_rules(N, P, K, temperature, humidity, ph, rainfall)
    
    def _recommend_crop_rules(
        self,
        N: float,
        P: float,
        K: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float
    ) -> Dict[str, Any]:
        """
        Rule-based crop recommendation when ML model is not available.
        """
        recommendations = []
        
        for crop_name, req in self.crop_requirements.items():
            score = 0
            score += self._score_condition(ph, req["optimal_ph"][0], req["optimal_ph"][1])
            score += self._score_condition(temperature, req["optimal_temp"][0], req["optimal_temp"][1])
            score += self._score_condition(humidity, req["optimal_humidity"][0], req["optimal_humidity"][1])
            
            # Score based on nutrient availability
            score += self._score_nutrient(N, req["N_req"]) * 0.5
            score += self._score_nutrient(P, req["P_req"]) * 0.5
            score += self._score_nutrient(K, req["K_req"]) * 0.5
            
            # Score based on rainfall match
            if rainfall >= req["water_mm"] * 0.6:
                score += 20
            
            recommendations.append((crop_name, score))
        
        # Sort by score and get best
        recommendations.sort(key=lambda x: x[1], reverse=True)
        best_crop = recommendations[0][0] if recommendations else "wheat"
        max_score = recommendations[0][1] if recommendations else 0
        confidence = min(90, max_score / 200 * 100)
        
        requirements = self.get_resource_requirements(best_crop)
        
        return {
            "crop": best_crop,
            "confidence": round(confidence, 2),
            "requirements": requirements,
            "method": "rule_based"
        }
    
    def _score_condition(self, value: float, min_val: float, max_val: float) -> float:
        """Score how well a value falls within the optimal range."""
        if min_val <= value <= max_val:
            return 100
        elif value < min_val:
            return max(0, 100 - ((min_val - value) / min_val) * 100)
        else:
            return max(0, 100 - ((value - max_val) / max_val) * 100)
    
    def _score_nutrient(self, available: float, requirement: float) -> float:
        """Score nutrient availability compared to requirement."""
        if available <= 0:
            return 0
        ratio = available / requirement
        if ratio >= 1.2:
            return 100
        elif ratio >= 0.8:
            return 80
        elif ratio >= 0.5:
            return 50
        else:
            return max(0, ratio / 0.5 * 50)
    
    def get_resource_requirements(self, crop_name: str) -> Dict[str, Any]:
        """
        Get resource requirements for a specific crop.
        
        Args:
            crop_name: Name of the crop
            
        Returns:
            Dict with water, N, P, K requirements and growing days
        """
        crop_key = crop_name.lower()
        if crop_key in self.crop_requirements:
            return {
                "crop": crop_name,
                **self.crop_requirements[crop_key]
            }
        else:
            # Return default requirements if crop not found
            return {
                "crop": crop_name,
                "water_mm": 500,
                "N_req": 100,
                "P_req": 50,
                "K_req": 80,
                "growing_days": 100,
                "optimal_temp": (20, 30),
                "optimal_humidity": (50, 80),
                "optimal_ph": (6.0, 7.5),
                "note": "Default requirements - crop not found in database"
            }
    
    def optimize_irrigation(
        self,
        crop_name: str,
        current_humidity: float,
        current_rainfall: float
    ) -> Dict[str, Any]:
        """
        Optimize irrigation schedule based on crop requirements and current conditions.
        
        Args:
            crop_name: Name of the crop
            current_humidity: Current humidity percentage
            current_rainfall: Current rainfall in mm (weekly average)
            
        Returns:
            Dict with irrigation recommendations
        """
        requirements = self.get_resource_requirements(crop_name)
        water_needed = requirements.get("water_mm", 500)
        
        # Calculate additional water needed per week
        weekly_rainfall = current_rainfall * 7  # Convert daily average to weekly
        weekly_water_needed = water_needed / requirements.get("growing_days", 100) * 7
        additional_water = max(0, weekly_water_needed - weekly_rainfall)
        
        # Adjust based on humidity
        if current_humidity > 70:
            humidity_factor = 0.8
        elif current_humidity > 50:
            humidity_factor = 1.0
        else:
            humidity_factor = 1.2
        
        adjusted_water = additional_water * humidity_factor
        
        # Determine irrigation frequency
        if adjusted_water <= 0:
            frequency = "No irrigation needed this week"
            daily_amount = 0
        elif adjusted_water < 10:
            frequency = "Light irrigation once this week"
            daily_amount = adjusted_water / 7
        elif adjusted_water < 25:
            frequency = "Irrigate 2-3 times this week"
            daily_amount = adjusted_water / 4
        elif adjusted_water < 50:
            frequency = "Irrigate 4-5 times this week"
            daily_amount = adjusted_water / 5
        else:
            frequency = "Daily irrigation recommended"
            daily_amount = adjusted_water / 7
        
        return {
            "crop": crop_name,
            "water_needed_mm_weekly": round(weekly_water_needed, 1),
            "rainfall_mm_weekly": round(weekly_rainfall, 1),
            "additional_water_needed_mm": round(adjusted_water, 1),
            "frequency": frequency,
            "daily_irrigation_mm": round(daily_amount, 2),
            "days_per_week": min(7, int(round(adjusted_water / 7)) + 1) if adjusted_water > 0 else 0,
            "humidity_factor": humidity_factor,
            "recommendation": "Increase irrigation" if adjusted_water > 25 else "Maintain current" if adjusted_water > 5 else "Reduce irrigation"
        }
    
    def get_fertilizer_plan(
        self,
        crop_name: str,
        N: float,
        P: float,
        K: float
    ) -> Dict[str, Any]:
        """
        Get fertilizer recommendations based on soil nutrient levels and crop requirements.
        
        Args:
            crop_name: Name of the crop
            N: Current Nitrogen level (ppm)
            P: Current Phosphorus level (ppm)
            K: Current Potassium level (ppm)
            
        Returns:
            Dict with fertilizer recommendations
        """
        requirements = self.get_resource_requirements(crop_name)
        
        n_req = requirements.get("N_req", 100)
        p_req = requirements.get("P_req", 50)
        k_req = requirements.get("K_req", 80)
        
        # Calculate deficits
        n_deficit = max(0, n_req - N)
        p_deficit = max(0, p_req - P)
        k_deficit = max(0, k_req - K)
        
        # Convert to kg per feddan
        n_kg = round(n_deficit * 0.5, 1)
        p_kg = round(p_deficit * 0.4, 1)
        k_kg = round(k_deficit * 0.4, 1)
        
        # Generate recommendations
        recommendations = []
        if n_deficit > 10:
            recommendations.append(f"Apply {n_kg} kg/feddan of Nitrogen fertilizer")
        if p_deficit > 5:
            recommendations.append(f"Apply {p_kg} kg/feddan of Phosphorus fertilizer")
        if k_deficit > 10:
            recommendations.append(f"Apply {k_kg} kg/feddan of Potassium fertilizer")
        
        if not recommendations:
            recommendations.append("Soil nutrients are adequate. Maintain current fertilization plan.")
        
        # Determine overall recommendation
        if n_deficit + p_deficit + k_deficit > 50:
            overall = "High nutrient deficit. Apply full recommended fertilizer schedule."
        elif n_deficit + p_deficit + k_deficit > 20:
            overall = "Moderate nutrient deficit. Apply targeted fertilizers."
        else:
            overall = "Nutrient levels adequate. Consider maintenance application."
        
        return {
            "crop": crop_name,
            "current_soil": {"N": round(N, 1), "P": round(P, 1), "K": round(K, 1)},
            "requirements": {"N": n_req, "P": p_req, "K": k_req},
            "deficit": {"N": round(n_deficit, 1), "P": round(p_deficit, 1), "K": round(k_deficit, 1)},
            "recommendations": recommendations,
            "overall": overall,
            "fertilizer_kg_per_feddan": {"N": n_kg, "P": p_kg, "K": k_kg}
        }
    
    def get_nutrient_plan(
        self,
        crop_name: str,
        area: float,
        N: float,
        P: float,
        K: float
    ) -> Dict[str, Any]:
        """
        Get complete nutrient plan for the entire field area.
        
        Args:
            crop_name: Name of the crop
            area: Field area in feddans
            N: Current Nitrogen level (ppm)
            P: Current Phosphorus level (ppm)
            K: Current Potassium level (ppm)
            
        Returns:
            Dict with total fertilizer requirements and schedule
        """
        plan = self.get_fertilizer_plan(crop_name, N, P, K)
        
        # Scale by area
        total_fertilizer = {
            "N": plan["fertilizer_kg_per_feddan"]["N"] * area,
            "P": plan["fertilizer_kg_per_feddan"]["P"] * area,
            "K": plan["fertilizer_kg_per_feddan"]["K"] * area
        }
        
        # Create application schedule
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
            "crop": crop_name,
            "area": area,
            "total_fertilizer_kg": total_fertilizer,
            "schedule": schedule,
            "recommendations": plan["recommendations"],
            "overall": plan["overall"]
        }


# Singleton instance
optimizer = ResourceOptimizer()
