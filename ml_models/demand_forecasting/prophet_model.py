"""
CropMind - Demand Forecasting Module
Prophet and GBM models for crop demand forecasting

Author: CropMind Team
Date: 2026
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import warnings
warnings.filterwarnings('ignore')


class DemandForecaster:
    """
    Demand Forecasting class for agricultural crops.
    Uses Prophet for time series and GBM for regression-based forecasting.
    """
    
    def __init__(self, models_path: str = "ml_models/demand_forecasting/models"):
        """
        Initialize the DemandForecaster and load trained models.
        
        Args:
            models_path: Path to the directory containing model files
        """
        self.models_path = models_path
        self.prophet_models = {}
        self.gbm_models = {}
        self.metadata = {}
        self.crop_categories = {}
        
        # Hardcoded crop information
        self.crop_info = {
            "wheat": {"category": "grain", "base_demand": 1000, "price_elasticity": 0.3},
            "rice": {"category": "grain", "base_demand": 1200, "price_elasticity": 0.2},
            "maize": {"category": "grain", "base_demand": 800, "price_elasticity": 0.4},
            "tomato": {"category": "vegetable", "base_demand": 500, "price_elasticity": 0.6},
            "potato": {"category": "vegetable", "base_demand": 450, "price_elasticity": 0.5},
            "onion": {"category": "vegetable", "base_demand": 400, "price_elasticity": 0.7},
            "cotton": {"category": "cash_crop", "base_demand": 200, "price_elasticity": 0.8},
            "sugarcane": {"category": "cash_crop", "base_demand": 300, "price_elasticity": 0.4},
            "barley": {"category": "grain", "base_demand": 600, "price_elasticity": 0.5},
            "chickpea": {"category": "pulse", "base_demand": 350, "price_elasticity": 0.6},
        }
        
        self._load_models()
    
    def _load_models(self) -> None:
        """
        Load all trained models from disk.
        """
        # Prophet models
        prophet_crops = ["wheat", "rice", "sugarcane", "cotton"]
        for crop in prophet_crops:
            model_path = os.path.join(self.models_path, f"{crop.capitalize()}_prophet.pkl")
            try:
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.prophet_models[crop] = pickle.load(f)
                    print(f"✅ {crop.capitalize()} Prophet model loaded")
                else:
                    print(f"⚠️ {crop.capitalize()} Prophet model not found")
            except Exception as e:
                print(f"⚠️ Error loading {crop} Prophet model: {e}")
        
        # GBM models
        gbm_crops = ["onion", "potato", "tomato", "maize"]
        for crop in gbm_crops:
            model_path = os.path.join(self.models_path, f"{crop.capitalize()}_gbm.pkl")
            try:
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.gbm_models[crop] = pickle.load(f)
                    print(f"✅ {crop.capitalize()} GBM model loaded")
                else:
                    print(f"⚠️ {crop.capitalize()} GBM model not found")
            except Exception as e:
                print(f"⚠️ Error loading {crop} GBM model: {e}")
        
        # Load metadata
        metadata_path = os.path.join(self.models_path, "metadata.json")
        try:
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                print("✅ Metadata loaded")
            else:
                print("⚠️ Metadata file not found")
        except Exception as e:
            print(f"⚠️ Error loading metadata: {e}")
    
    def forecast(self, crop: str, years: int = 3) -> Dict[str, Any]:
        """
        Generate demand forecast for a specific crop.
        
        Args:
            crop: Name of the crop (e.g., "wheat", "tomato")
            years: Number of years to forecast (default: 3)
            
        Returns:
            Dict with forecast data including yearly predictions and trend
        """
        crop = crop.lower()
        
        if crop in self.prophet_models:
            return self._forecast_prophet(crop, years)
        elif crop in self.gbm_models:
            return self._forecast_gbm(crop, years)
        else:
            return self._forecast_fallback(crop, years)
    
    def _forecast_prophet(self, crop: str, years: int) -> Dict[str, Any]:
        """
        Generate forecast using Prophet model.
        """
        model = self.prophet_models[crop]
        
        try:
            # Create future dataframe
            future = model.make_future_dataframe(periods=years * 12, freq='M')
            forecast = model.predict(future)
            
            # Extract yearly predictions
            yearly_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(years * 12)
            
            # Group by year
            yearly_predictions = []
            yearly_data['year'] = pd.to_datetime(yearly_data['ds']).dt.year
            yearly_group = yearly_data.groupby('year').agg({
                'yhat': 'mean',
                'yhat_lower': 'mean',
                'yhat_upper': 'mean'
            }).reset_index()
            
            for _, row in yearly_group.iterrows():
                yearly_predictions.append({
                    "year": int(row['year']),
                    "forecast": float(row['yhat']),
                    "lower_bound": float(row['yhat_lower']),
                    "upper_bound": float(row['yhat_upper'])
                })
            
            # Calculate trend direction
            if len(yearly_predictions) >= 2:
                first = yearly_predictions[0]['forecast']
                last = yearly_predictions[-1]['forecast']
                trend = "increasing" if last > first else "decreasing" if last < first else "stable"
                change_percent = ((last - first) / first * 100) if first > 0 else 0
            else:
                trend = "stable"
                change_percent = 0
            
            return {
                "crop": crop,
                "method": "prophet",
                "yearly_forecast": yearly_predictions,
                "trend": trend,
                "change_percent": round(change_percent, 2),
                "next_year_forecast": yearly_predictions[0] if yearly_predictions else None,
                "avg_demand": float(yearly_data['yhat'].mean()) if not yearly_data.empty else 0
            }
            
        except Exception as e:
            print(f"⚠️ Prophet forecast error for {crop}: {e}")
            return self._forecast_fallback(crop, years)
    
    def _forecast_gbm(self, crop: str, years: int) -> Dict[str, Any]:
        """
        Generate forecast using GBM model (regression-based).
        """
        model = self.gbm_models[crop]
        
        try:
            # Generate future features (simple linear projection)
            future_years = []
            future_predictions = []
            
            current_year = datetime.now().year
            for i in range(years):
                year = current_year + i + 1
                future_years.append(year)
                
                # Use GBM to predict (simplified - would need proper features)
                # In practice, we'd create appropriate feature vectors
                # Here we use a simplified approach based on historical trend
                base_pred = model.predict([[year, i]])[0] if hasattr(model, 'predict') else 100 + i * 10
                future_predictions.append(float(base_pred))
            
            # Calculate trend
            if len(future_predictions) >= 2:
                first = future_predictions[0]
                last = future_predictions[-1]
                trend = "increasing" if last > first else "decreasing" if last < first else "stable"
                change_percent = ((last - first) / first * 100) if first > 0 else 0
            else:
                trend = "stable"
                change_percent = 0
            
            yearly_predictions = []
            for year, pred in zip(future_years, future_predictions):
                yearly_predictions.append({
                    "year": year,
                    "forecast": pred,
                    "lower_bound": pred * 0.9,
                    "upper_bound": pred * 1.1
                })
            
            return {
                "crop": crop,
                "method": "gbm",
                "yearly_forecast": yearly_predictions,
                "trend": trend,
                "change_percent": round(change_percent, 2),
                "next_year_forecast": yearly_predictions[0] if yearly_predictions else None,
                "avg_demand": np.mean(future_predictions) if future_predictions else 0
            }
            
        except Exception as e:
            print(f"⚠️ GBM forecast error for {crop}: {e}")
            return self._forecast_fallback(crop, years)
    
    def _forecast_fallback(self, crop: str, years: int) -> Dict[str, Any]:
        """
        Generate forecast using rule-based fallback when models are not available.
        """
        crop_info = self.crop_info.get(crop, {})
        base_demand = crop_info.get("base_demand", 500)
        
        current_year = datetime.now().year
        yearly_predictions = []
        
        # Simple growth/decline pattern
        growth_rate = 0.03  # 3% annual growth
        for i in range(years):
            year = current_year + i + 1
            forecast = base_demand * (1 + growth_rate * (i + 1))
            yearly_predictions.append({
                "year": year,
                "forecast": round(forecast, 2),
                "lower_bound": round(forecast * 0.85, 2),
                "upper_bound": round(forecast * 1.15, 2)
            })
        
        return {
            "crop": crop,
            "method": "fallback",
            "yearly_forecast": yearly_predictions,
            "trend": "increasing",
            "change_percent": round(growth_rate * 100 * years, 2),
            "next_year_forecast": yearly_predictions[0] if yearly_predictions else None,
            "avg_demand": sum(p['forecast'] for p in yearly_predictions) / len(yearly_predictions) if yearly_predictions else 0,
            "note": "Fallback method - trained models not available"
        }
    
    def get_demand_signal(self, crop: str) -> Dict[str, Any]:
        """
        Get demand signal (HIGH, MEDIUM, LOW) for a crop based on forecast.
        
        Args:
            crop: Name of the crop
            
        Returns:
            Dict with signal level and explanation
        """
        crop = crop.lower()
        
        # Get forecast for next year
        result = self.forecast(crop, years=1)
        next_year = result.get("next_year_forecast", {})
        forecast_value = next_year.get("forecast", 0)
        
        # Get base demand for comparison
        crop_info = self.crop_info.get(crop, {})
        base_demand = crop_info.get("base_demand", 500)
        
        if forecast_value > base_demand * 1.3:
            signal = "HIGH"
            explanation = f"Demand is expected to be {forecast_value:.0f}, which is {((forecast_value/base_demand - 1) * 100):.0f}% above baseline"
        elif forecast_value > base_demand * 0.8:
            signal = "MEDIUM"
            explanation = f"Demand is stable at {forecast_value:.0f}, close to baseline of {base_demand:.0f}"
        else:
            signal = "LOW"
            explanation = f"Demand is expected to be {forecast_value:.0f}, which is {((1 - forecast_value/base_demand) * 100):.0f}% below baseline"
        
        return {
            "crop": crop,
            "signal": signal,
            "forecast_value": round(forecast_value, 2),
            "baseline": base_demand,
            "explanation": explanation,
            "trend": result.get("trend", "stable"),
            "change_percent": result.get("change_percent", 0)
        }
    
    def best_crop_to_grow(self, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend the best crop to grow based on conditions.
        
        Args:
            conditions: Dict with soil and environmental conditions
                - soil_type: str (sandy, clay, loam)
                - water_availability: float (mm/year)
                - temperature: float (°C)
                - market_demand_preference: str (grain, vegetable, cash_crop, pulse)
                
        Returns:
            Dict with recommended crop and reasoning
        """
        # Get all crop scores
        scores = []
        water_avail = conditions.get("water_availability", 500)
        temp = conditions.get("temperature", 25)
        market_pref = conditions.get("market_demand_preference", "")
        soil_type = conditions.get("soil_type", "loam")
        
        for crop_name, info in self.crop_info.items():
            # Get demand signal
            demand = self.get_demand_signal(crop_name)
            demand_score = 0
            if demand["signal"] == "HIGH":
                demand_score = 30
            elif demand["signal"] == "MEDIUM":
                demand_score = 15
            
            # Water requirement score
            req = self._get_water_requirement(crop_name)
            if water_avail >= req:
                water_score = 20
            elif water_avail >= req * 0.6:
                water_score = 10
            else:
                water_score = 0
            
            # Temperature score
            if info.get("category") in ["vegetable", "cash_crop"]:
                temp_score = 20 if 20 <= temp <= 30 else 10
            else:
                temp_score = 20 if 15 <= temp <= 25 else 10
            
            # Market preference score
            pref_score = 0
            if market_pref:
                if info.get("category") == market_pref:
                    pref_score = 30
                elif market_pref == "all":
                    pref_score = 15
            
            total_score = demand_score + water_score + temp_score + pref_score
            scores.append({
                "crop": crop_name,
                "score": total_score,
                "demand_signal": demand["signal"],
                "details": {
                    "demand_score": demand_score,
                    "water_score": water_score,
                    "temp_score": temp_score,
                    "pref_score": pref_score
                }
            })
        
        # Sort by score
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "recommended_crop": scores[0]["crop"] if scores else "wheat",
            "score": scores[0]["score"] if scores else 0,
            "all_scores": scores[:5],
            "conditions_used": conditions,
            "reasoning": "Based on demand signal, water availability, temperature, and market preference"
        }
    
    def _get_water_requirement(self, crop: str) -> float:
        """Get water requirement for a crop in mm/year."""
        crop_info = {
            "wheat": 450,
            "rice": 1200,
            "maize": 500,
            "tomato": 600,
            "potato": 400,
            "onion": 350,
            "cotton": 600,
            "sugarcane": 1800,
            "barley": 350,
            "chickpea": 300
        }
        return crop_info.get(crop, 500)
    
    def get_all_forecasts(self, years: int = 1) -> Dict[str, Any]:
        """
        Get forecasts for all available crops.
        
        Args:
            years: Number of years to forecast (default: 1)
            
        Returns:
            Dict with forecasts for all crops
        """
        all_crops = list(self.crop_info.keys())
        all_forecasts = {}
        signals = {}
        
        for crop in all_crops:
            forecast_data = self.forecast(crop, years)
            all_forecasts[crop] = forecast_data
            signals[crop] = self.get_demand_signal(crop)
        
        # Determine best crops
        best_signal = [crop for crop, signal in signals.items() if signal["signal"] == "HIGH"]
        medium_signal = [crop for crop, signal in signals.items() if signal["signal"] == "MEDIUM"]
        
        return {
            "forecasts": all_forecasts,
            "signals": signals,
            "summary": {
                "high_demand": best_signal,
                "medium_demand": medium_signal,
                "low_demand": [crop for crop, signal in signals.items() if signal["signal"] == "LOW"],
                "total_crops": len(all_crops)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_market_opportunities(self) -> Dict[str, Any]:
        """
        Identify market opportunities based on demand forecasts.
        
        Returns:
            Dict with market opportunities and recommendations
        """
        forecasts = self.get_all_forecasts(years=1)
        high_demand = forecasts["summary"]["high_demand"]
        medium_demand = forecasts["summary"]["medium_demand"]
        
        opportunities = []
        
        for crop in high_demand:
            signal = forecasts["signals"][crop]
            opportunities.append({
                "crop": crop,
                "opportunity": "HIGH_DEMAND",
                "recommendation": f"Consider increasing {crop} production",
                "demand_gap": f"{signal['forecast_value'] - signal['baseline']:.0f} units",
                "priority": 1
            })
        
        for crop in medium_demand:
            opportunities.append({
                "crop": crop,
                "opportunity": "MEDIUM_DEMAND",
                "recommendation": f"Maintain current {crop} production levels",
                "priority": 2
            })
        
        return {
            "opportunities": opportunities,
            "total_opportunities": len(opportunities),
            "highest_priority": opportunities[0] if opportunities else None
        }


# Singleton instance
forecaster = DemandForecaster()
