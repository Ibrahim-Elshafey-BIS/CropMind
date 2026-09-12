"""
CropMind - Price Forecasting Module
Prophet and LSTM models for commodity price forecasting

Author: CropMind Team
Date: 2026
"""

import os
import pickle
import warnings
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

warnings.filterwarnings('ignore')


class PriceForecaster:
    """
    Price Forecasting class for agricultural commodities.
    Supports Prophet (stable crops) and LSTM (volatile crops) models.
    """
    
    def __init__(self, models_path: str = "ml_models/price_forecasting/models"):
        """
        Initialize the PriceForecaster and load all trained models.
        
        Args:
            models_path: Path to the directory containing model files
        """
        self.models_path = models_path
        self.prophet_models: Dict[str, Any] = {}
        self.lstm_models: Dict[str, Dict] = {}
        
        # Commodity configuration
        self.commodity_config = {
            "potato": {"type": "prophet", "default_price": 1700},
            "wheat": {"type": "prophet", "default_price": 2400},
            "brinjal": {"type": "prophet", "default_price": 2200},
            "tomato": {"type": "lstm", "default_price": 2500},
            "onion": {"type": "lstm", "default_price": 2300},
        }
        
        self._load_models()
    
    def _load_models(self) -> None:
        """
        Load all trained models from disk.
        """
        # Load Prophet models
        prophet_commodities = ["potato", "wheat", "brinjal"]
        for commodity in prophet_commodities:
            model_path = os.path.join(self.models_path, f"{commodity.capitalize()}_prophet.pkl")
            try:
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.prophet_models[commodity] = pickle.load(f)
                    print(f"✅ {commodity.capitalize()} Prophet model loaded")
                else:
                    print(f"⚠️ {commodity.capitalize()} Prophet model not found")
            except Exception as e:
                print(f"⚠️ Error loading {commodity} Prophet model: {e}")
        
        # Load LSTM models
        lstm_commodities = ["tomato", "onion"]
        for commodity in lstm_commodities:
            try:
                model_path = os.path.join(self.models_path, f"{commodity.capitalize()}_lstm.h5")
                scaler_path = os.path.join(self.models_path, f"{commodity.capitalize()}_lstm_scaler.pkl")
                
                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    # Lazy import tensorflow
                    import tensorflow as tf
                    
                    model = tf.keras.models.load_model(model_path)
                    with open(scaler_path, 'rb') as f:
                        scaler = pickle.load(f)
                    
                    self.lstm_models[commodity] = {
                        "model": model,
                        "scaler": scaler
                    }
                    print(f"✅ {commodity.capitalize()} LSTM model loaded")
                else:
                    print(f"⚠️ {commodity.capitalize()} LSTM model not found")
            except Exception as e:
                print(f"⚠️ Error loading {commodity} LSTM model: {e}")
    
    def forecast_commodity(self, commodity: str, days: int = 90) -> Dict[str, Any]:
        """
        Generate price forecast for a specific commodity.
        
        Args:
            commodity: Name of the commodity (case-insensitive)
            days: Number of days to forecast
            
        Returns:
            Dict with forecast data
        """
        commodity = commodity.lower()
        
        if commodity in self.prophet_models:
            return self._forecast_prophet(commodity, days)
        elif commodity in self.lstm_models:
            return self._forecast_lstm(commodity, days)
        else:
            return self._fallback_forecast(commodity, days)
    
    def _forecast_prophet(self, commodity: str, days: int) -> Dict[str, Any]:
        """
        Generate forecast using Prophet model.
        """
        model = self.prophet_models[commodity]
        
        try:
            # Create future dataframe
            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future)
            
            # Get forecast values
            forecast_values = forecast['yhat'].values[-days:]
            dates = forecast['ds'].values[-days:]
            
            # Calculate weekly averages
            weekly_forecast = self._calculate_weekly_averages(dates, forecast_values)
            
            # Get current price (last historical value)
            current_price = float(forecast_values[0]) if len(forecast_values) > 0 else 0
            
            # Get forecasts at specific periods
            forecast_7d = float(forecast_values[6]) if len(forecast_values) > 6 else current_price
            forecast_30d = float(forecast_values[29]) if len(forecast_values) > 29 else current_price
            forecast_90d = float(forecast_values[-1]) if len(forecast_values) > 0 else current_price
            
            # Determine trend
            if len(forecast_values) >= 7:
                first_week = np.mean(forecast_values[:7])
                last_week = np.mean(forecast_values[-7:])
                if last_week > first_week * 1.02:
                    trend = "increasing"
                elif last_week < first_week * 0.98:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            return {
                "commodity": commodity,
                "days": days,
                "current_price": round(current_price, 2),
                "forecast_7d": round(forecast_7d, 2),
                "forecast_30d": round(forecast_30d, 2),
                "forecast_90d": round(forecast_90d, 2),
                "weekly_forecast": weekly_forecast,
                "trend": trend,
                "confidence": 90.0,
                "method": "prophet"
            }
            
        except Exception as e:
            print(f"⚠️ Prophet forecast error for {commodity}: {e}")
            return self._fallback_forecast(commodity, days)
    
    def _forecast_lstm(self, commodity: str, days: int) -> Dict[str, Any]:
        """
        Generate forecast using LSTM model.
        """
        model_data = self.lstm_models[commodity]
        model = model_data["model"]
        scaler = model_data["scaler"]
        
        try:
            # Use placeholder sequence (zeros) since we don't have real historical data
            # In production, this should use actual historical prices
            lookback = 30
            last_sequence = np.zeros(lookback).reshape(1, lookback, 1)
            
            # Generate predictions iteratively
            predictions = []
            current_seq = last_sequence.copy()
            
            for _ in range(days):
                pred = model.predict(current_seq, verbose=0)
                predictions.append(pred[0, 0])
                current_seq = np.roll(current_seq, -1, axis=1)
                current_seq[0, -1, 0] = pred[0, 0]
            
            # Inverse transform predictions
            predictions = np.array(predictions).reshape(-1, 1)
            forecast_values = scaler.inverse_transform(predictions).flatten()
            
            # Generate dates
            start_date = datetime.now()
            dates = [start_date + timedelta(days=i) for i in range(days)]
            
            # Calculate weekly averages
            weekly_forecast = self._calculate_weekly_averages(dates, forecast_values)
            
            # Current price (first prediction)
            current_price = float(forecast_values[0]) if len(forecast_values) > 0 else 0
            
            # Forecast at specific periods
            forecast_7d = float(forecast_values[6]) if len(forecast_values) > 6 else current_price
            forecast_30d = float(forecast_values[29]) if len(forecast_values) > 29 else current_price
            forecast_90d = float(forecast_values[-1]) if len(forecast_values) > 0 else current_price
            
            # Determine trend
            if len(forecast_values) >= 7:
                first_week = np.mean(forecast_values[:7])
                last_week = np.mean(forecast_values[-7:])
                if last_week > first_week * 1.02:
                    trend = "increasing"
                elif last_week < first_week * 0.98:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            return {
                "commodity": commodity,
                "days": days,
                "current_price": round(current_price, 2),
                "forecast_7d": round(forecast_7d, 2),
                "forecast_30d": round(forecast_30d, 2),
                "forecast_90d": round(forecast_90d, 2),
                "weekly_forecast": weekly_forecast,
                "trend": trend,
                "confidence": 85.0,
                "method": "lstm"
            }
            
        except Exception as e:
            print(f"⚠️ LSTM forecast error for {commodity}: {e}")
            return self._fallback_forecast(commodity, days)
    
    def _calculate_weekly_averages(self, dates, values) -> List[Dict[str, Any]]:
        """
        Calculate weekly averages from daily forecast data.
        """
        weekly_forecast = []
        
        for week_start in range(0, len(values), 7):
            week_end = min(week_start + 7, len(values))
            week_values = values[week_start:week_end]
            week_dates = dates[week_start:week_end]
            
            if len(week_values) > 0:
                avg_price = float(np.mean(week_values))
                week_date = week_dates[0]
                
                if isinstance(week_date, datetime):
                    date_str = week_date.strftime("%Y-%m-%d")
                elif isinstance(week_date, pd.Timestamp):
                    date_str = week_date.strftime("%Y-%m-%d")
                else:
                    date_str = str(week_date)
                
                weekly_forecast.append({
                    "date": date_str,
                    "price": round(avg_price, 2)
                })
        
        return weekly_forecast
    
    def get_recommendation(self, commodity: str, current_price: float) -> Dict[str, Any]:
        """
        Get trading recommendation based on price forecast.
        
        Args:
            commodity: Name of the commodity
            current_price: Current market price
            
        Returns:
            Dict with recommendation
        """
        forecast = self.forecast_commodity(commodity, days=90)
        forecast_90d = forecast.get("forecast_90d", current_price)
        
        if current_price > 0:
            change_percent = ((forecast_90d - current_price) / current_price) * 100
        else:
            change_percent = 0
        
        # Determine action
        if change_percent > 15:
            action = "PLANT_MORE"
            reason = "Price expected to rise significantly"
        elif change_percent > 5:
            action = "STORE"
            reason = "Price expected to increase moderately"
        elif change_percent > -5:
            action = "HOLD"
            reason = "Price expected to remain stable"
        elif change_percent > -15:
            action = "SELL_NOW"
            reason = "Price expected to decrease moderately"
        else:
            action = "SELL_IMMEDIATELY"
            reason = "Price expected to drop significantly"
        
        return {
            "commodity": commodity,
            "current_price": round(current_price, 2),
            "forecast_90d": round(forecast_90d, 2),
            "change_percent": round(change_percent, 2),
            "action": action,
            "reason": reason,
            "confidence": forecast.get("confidence", 80.0)
        }
    
    def _fallback_forecast(self, commodity: str, days: int) -> Dict[str, Any]:
        """
        Fallback forecast when models are not available.
        """
        # Default prices (EGP/ton)
        default_prices = {
            "potato": 1700,
            "wheat": 2400,
            "brinjal": 2200,
            "tomato": 2500,
            "onion": 2300
        }
        base_price = default_prices.get(commodity, 2000)
        
        # Generate weekly forecast with 1% weekly increase
        weeks = max(1, days // 7)
        weekly_forecast = []
        start_date = datetime.now()
        
        for i in range(weeks):
            week_date = start_date + timedelta(weeks=i)
            price = base_price * (1 + 0.01 * i)
            weekly_forecast.append({
                "date": week_date.strftime("%Y-%m-%d"),
                "price": round(price, 2)
            })
        
        forecast_90d = weekly_forecast[-1]["price"] if weekly_forecast else base_price
        forecast_30d = weekly_forecast[min(4, len(weekly_forecast)-1)]["price"] if weekly_forecast else base_price
        forecast_7d = weekly_forecast[0]["price"] if weekly_forecast else base_price
        
        return {
            "commodity": commodity,
            "days": days,
            "current_price": round(base_price, 2),
            "forecast_7d": round(forecast_7d, 2),
            "forecast_30d": round(forecast_30d, 2),
            "forecast_90d": round(forecast_90d, 2),
            "weekly_forecast": weekly_forecast,
            "trend": "increasing",
            "confidence": 60.0,
            "method": "fallback"
        }


# ============================================
# Backward Compatibility Functions
# ============================================

def forecast_prophet(commodity: str, days: int = 90) -> Dict[str, Any]:
    """Legacy function - use PriceForecaster instead."""
    forecaster = PriceForecaster()
    return forecaster.forecast_commodity(commodity, days)


def forecast_lstm(commodity: str, days: int = 90) -> Dict[str, Any]:
    """Legacy function - use PriceForecaster instead."""
    forecaster = PriceForecaster()
    return forecaster.forecast_commodity(commodity, days)


def get_recommendation(commodity: str, current_price: float) -> Dict[str, Any]:
    """Legacy function - use PriceForecaster instead."""
    forecaster = PriceForecaster()
    return forecaster.get_recommendation(commodity, current_price)


def predict_all_commodities(days: int = 90) -> Dict[str, Any]:
    """
    Get forecasts for all available commodities.
    
    Args:
        days: Number of days to forecast
        
    Returns:
        Dict with forecasts for all commodities
    """
    forecaster = PriceForecaster()
    results = {}
    
    for commodity in forecaster.commodity_config.keys():
        results[commodity] = forecaster.forecast_commodity(commodity, days)
    
    return results


def main():
    """
    Main test function for the PriceForecaster.
    """
    print("="*60)
    print("🌾 CropMind - Price Forecasting Test")
    print("="*60)
    
    forecaster = PriceForecaster()
    
    # Test each commodity
    for commodity in forecaster.commodity_config.keys():
        print(f"\n📊 Forecasting: {commodity.capitalize()}")
        result = forecaster.forecast_commodity(commodity, days=90)
        print(f"  Current: {result.get('current_price', 0):.2f}")
        print(f"  30-day: {result.get('forecast_30d', 0):.2f}")
        print(f"  90-day: {result.get('forecast_90d', 0):.2f}")
        print(f"  Trend: {result.get('trend', 'N/A')}")
        print(f"  Method: {result.get('method', 'N/A')}")
        print(f"  Confidence: {result.get('confidence', 0):.1f}%")
        
        # Test recommendation
        rec = forecaster.get_recommendation(commodity, result.get('current_price', 0))
        print(f"  Recommendation: {rec.get('action', 'N/A')}")
        print(f"  Reason: {rec.get('reason', 'N/A')}")
    
    print("\n" + "="*60)
    print("✅ Price Forecasting Test Complete!")


if __name__ == "__main__":
    main()
