"""
CropMind - Price Fetcher Tool
Standalone utility for fetching price forecasts and demand signals

Author: CropMind Team
Date: 2026
"""

from typing import Dict, Any, Optional


class PriceFetcherTool:
    """
    Price fetching tool for commodity price forecasts and demand signals.
    Uses ModelRegistry to access PriceForecaster and DemandForecaster.
    """
    
    def __init__(self):
        """
        Initialize the PriceFetcherTool and load registry.
        """
        self.registry = None
        
        try:
            from ml_models.model_registry import registry
            self.registry = registry
            print("[PriceFetcherTool] ✅ Registry loaded")
        except ImportError as e:
            print(f"[PriceFetcherTool] ⚠️ Registry not available: {e}")
            self.registry = None
    
    def get_price_forecast(self, crop: str, days: int = 30) -> Dict[str, Any]:
        """
        Get price forecast for a crop.
        
        Args:
            crop: Name of the crop
            days: Number of days to forecast
            
        Returns:
            Dict with price forecast data
        """
        try:
            if self.registry and hasattr(self.registry, 'price') and self.registry.price:
                result = self.registry.price.forecast_commodity(crop, days=days)
                result["source"] = "ml_model"
                print(f"[PriceFetcherTool] ✅ Price forecast fetched for {crop}")
                return result
            else:
                print(f"[PriceFetcherTool] ⚠️ Price model not available, using fallback for {crop}")
                return self._fallback_price_forecast(crop, days)
        except Exception as e:
            print(f"[PriceFetcherTool] ⚠️ Error fetching price forecast for {crop}: {e}")
            return self._fallback_price_forecast(crop, days)
    
    def get_demand_signal(self, crop: str) -> Dict[str, Any]:
        """
        Get demand signal for a crop.
        
        Args:
            crop: Name of the crop
            
        Returns:
            Dict with demand signal data
        """
        try:
            if self.registry and hasattr(self.registry, 'demand') and self.registry.demand:
                result = self.registry.demand.get_demand_signal(crop)
                result["source"] = "ml_model"
                print(f"[PriceFetcherTool] ✅ Demand signal fetched for {crop}")
                return result
            else:
                print(f"[PriceFetcherTool] ⚠️ Demand model not available, using fallback for {crop}")
                return self._fallback_demand_signal(crop)
        except Exception as e:
            print(f"[PriceFetcherTool] ⚠️ Error fetching demand signal for {crop}: {e}")
            return self._fallback_demand_signal(crop)
    
    def get_market_summary(self, crop: str, current_price: float) -> Dict[str, Any]:
        """
        Get comprehensive market summary with recommendation.
        
        Args:
            crop: Name of the crop
            current_price: Current market price
            
        Returns:
            Dict with market summary and recommendation
        """
        # Get price forecast
        price_forecast = self.get_price_forecast(crop, days=90)
        forecast_30d = price_forecast.get("forecast_30d", current_price)
        trend = price_forecast.get("trend", "stable")
        source = price_forecast.get("source", "fallback")
        
        # Get demand signal
        demand_signal = self.get_demand_signal(crop)
        signal = demand_signal.get("signal", "MEDIUM")
        
        # Calculate price change percentage
        if current_price > 0:
            price_change_percent = ((forecast_30d - current_price) / current_price) * 100
        else:
            price_change_percent = 0
        
        # Determine recommendation
        if trend == "decreasing" or signal == "LOW":
            recommendation = "SELL"
        elif price_change_percent > 10 and signal == "HIGH":
            recommendation = "BUY"
        elif trend == "increasing" and signal in ["HIGH", "MEDIUM"]:
            recommendation = "HOLD"
        else:
            recommendation = "HOLD"
        
        # Generate Arabic summary
        summary_ar = self._generate_summary_ar(
            crop=crop,
            price_change=price_change_percent,
            signal=signal,
            recommendation=recommendation
        )
        
        return {
            "crop": crop,
            "current_price": round(current_price, 2),
            "forecast_30d": round(forecast_30d, 2),
            "price_change_percent": round(price_change_percent, 2),
            "trend": trend,
            "demand_signal": signal,
            "recommendation": recommendation,
            "summary_ar": summary_ar,
            "source": source
        }
    
    def _generate_summary_ar(
        self,
        crop: str,
        price_change: float,
        signal: str,
        recommendation: str
    ) -> str:
        """
        Generate Arabic summary based on market conditions.
        """
        crop_names = {
            "tomato": "الطماطم",
            "onion": "البصل",
            "potato": "البطاطس",
            "wheat": "القمح",
            "cotton": "القطن",
            "sugarcane": "قصب السكر",
            "rice": "الأرز",
            "maize": "الذرة",
            "brinjal": "الباذنجان"
        }
        crop_name = crop_names.get(crop, crop)
        
        if recommendation == "SELL":
            if price_change < -10:
                return f"⚠️ سعر {crop_name} في انخفاض حاد، يوصى بالبيع الفوري لتجنب الخسائر."
            else:
                return f"📉 سعر {crop_name} في انخفاض، يوصى بالبيع الآن."
        
        elif recommendation == "BUY":
            return f"📈 سعر {crop_name} في ارتفاع مع طلب مرتفع، فرصة جيدة للشراء."
        
        elif recommendation == "HOLD" and signal == "HIGH":
            return f"✅ سوق {crop_name} قوي مع طلب مرتفع، يوصى بالاحتفاظ بالمحصول."
        
        elif recommendation == "HOLD" and signal == "MEDIUM":
            return f"⚖️ سوق {crop_name} مستقر مع طلب متوسط، يمكن الاحتفاظ بالمحصول."
        
        else:
            return f"ℹ️ سوق {crop_name} مستقر، يوصى بمراقبة الأسعار واتخاذ القرار المناسب."
    
    def _fallback_price_forecast(self, crop: str, days: int) -> Dict[str, Any]:
        """
        Fallback price forecast when ML model is not available.
        """
        # Default prices (EGP/ton)
        default_prices = {
            "tomato": 35.0,
            "onion": 25.0,
            "potato": 18.0,
            "wheat": 15.0,
            "cotton": 55.0,
            "sugarcane": 12.0,
            "rice": 22.0,
            "maize": 16.0,
            "brinjal": 22.0
        }
        base_price = default_prices.get(crop.lower(), 20.0)
        
        # Weekly forecast with 2% weekly increase
        weeks = max(1, days // 7)
        weekly_forecast = []
        from datetime import datetime, timedelta
        start_date = datetime.now()
        
        for i in range(weeks):
            week_date = start_date + timedelta(weeks=i)
            price = base_price * (1 + 0.02 * i)
            weekly_forecast.append({
                "date": week_date.strftime("%Y-%m-%d"),
                "price": round(price, 2)
            })
        
        return {
            "crop": crop,
            "days": days,
            "current_price": round(base_price, 2),
            "forecast_7d": round(base_price * 1.02, 2),
            "forecast_30d": round(base_price * 1.08, 2),
            "forecast_90d": round(base_price * 1.26, 2),
            "weekly_forecast": weekly_forecast,
            "trend": "stable",
            "confidence": 50.0,
            "source": "fallback"
        }
    
    def _fallback_demand_signal(self, crop: str) -> Dict[str, Any]:
        """
        Fallback demand signal when ML model is not available.
        """
        return {
            "crop": crop,
            "signal": "MEDIUM",
            "forecast_value": 500.0,
            "baseline": 500.0,
            "change_percent": 0.0,
            "explanation": "بيانات تقديرية - النموذج غير متاح",
            "source": "fallback"
        }
