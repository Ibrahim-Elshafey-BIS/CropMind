"""
CropMind - Weather Tool
Standalone utility for fetching weather data and generating agricultural advice

Author: CropMind Team
Date: 2026
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class WeatherTool:
    """
    Weather tool for fetching current weather, forecasts, and agricultural advice.
    Uses OpenWeatherMap API with fallback to default values when API key is not available.
    """
    
    def __init__(self):
        """
        Initialize the WeatherTool with API key from settings.
        """
        self.api_key = None
        
        # Try to import from app settings first
        try:
            from app.core.config import settings
            self.api_key = settings.WEATHER_API_KEY
        except ImportError:
            self.api_key = os.getenv("WEATHER_API_KEY", "")
        
        if not self.api_key:
            print("[WeatherTool] ⚠️ WEATHER_API_KEY not configured. Using fallback data.")
        else:
            print("[WeatherTool] ✅ Weather API key loaded")
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """
        Get current weather for a location from OpenWeatherMap API.
        
        Args:
            location: City name (e.g., "Cairo", "Alexandria")
            
        Returns:
            Dict with current weather data
        """
        if not self.api_key:
            print(f"[WeatherTool] ⚠️ No API key, returning fallback for {location}")
            return self._fallback_weather(location)
        
        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "lang": "ar"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant data
            weather = {
                "location": data.get("name", location),
                "temperature": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity": round(data["main"]["humidity"], 1),
                "pressure": round(data["main"]["pressure"], 1),
                "wind_speed": round(data["wind"]["speed"] * 3.6, 1),  # Convert m/s to km/h
                "description": data["weather"][0]["description"] if data.get("weather") else "صحو",
                "visibility": round(data.get("visibility", 10000) / 1000, 1),  # Convert m to km
                "timestamp": datetime.now().isoformat(),
                "source": "openweathermap"
            }
            
            print(f"[WeatherTool] ✅ Current weather fetched for {location}")
            return weather
            
        except requests.exceptions.Timeout:
            print(f"[WeatherTool] ⚠️ Timeout fetching weather for {location}")
            return self._fallback_weather(location)
        except requests.exceptions.RequestException as e:
            print(f"[WeatherTool] ⚠️ API error for {location}: {e}")
            return self._fallback_weather(location)
        except (KeyError, ValueError) as e:
            print(f"[WeatherTool] ⚠️ Parse error for {location}: {e}")
            return self._fallback_weather(location)
    
    def get_weather_forecast(self, location: str, days: int = 7) -> Dict[str, Any]:
        """
        Get weather forecast for a location from OpenWeatherMap API.
        
        Args:
            location: City name (e.g., "Cairo", "Alexandria")
            days: Number of days to forecast (max 5)
            
        Returns:
            Dict with forecast data
        """
        if not self.api_key:
            print(f"[WeatherTool] ⚠️ No API key, returning fallback forecast for {location}")
            return self._fallback_forecast(location, days)
        
        try:
            # OpenWeatherMap 5-day forecast (3-hour intervals)
            url = "http://api.openweathermap.org/data/2.5/forecast"
            cnt = min(days * 8, 40)  # 8 readings per day, max 40
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "lang": "ar",
                "cnt": cnt
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Group by day
            forecast_by_day = {}
            for item in data.get("list", []):
                dt = datetime.fromtimestamp(item["dt"])
                date_key = dt.strftime("%Y-%m-%d")
                
                if date_key not in forecast_by_day:
                    forecast_by_day[date_key] = {
                        "temps": [],
                        "humidities": [],
                        "descriptions": []
                    }
                
                forecast_by_day[date_key]["temps"].append(item["main"]["temp"])
                forecast_by_day[date_key]["humidities"].append(item["main"]["humidity"])
                if item.get("weather"):
                    forecast_by_day[date_key]["descriptions"].append(item["weather"][0]["description"])
            
            # Build final forecast list
            forecast_list = []
            for date_key, day_data in forecast_by_day.items():
                forecast_list.append({
                    "date": date_key,
                    "temp_min": round(min(day_data["temps"]), 1),
                    "temp_max": round(max(day_data["temps"]), 1),
                    "humidity": round(sum(day_data["humidities"]) / len(day_data["humidities"]), 1),
                    "description": day_data["descriptions"][0] if day_data["descriptions"] else "صحو"
                })
            
            # Sort by date
            forecast_list.sort(key=lambda x: x["date"])
            
            result = {
                "location": data.get("city", {}).get("name", location),
                "days": len(forecast_list),
                "forecast": forecast_list,
                "source": "openweathermap"
            }
            
            print(f"[WeatherTool] ✅ Forecast fetched for {location} ({len(forecast_list)} days)")
            return result
            
        except requests.exceptions.Timeout:
            print(f"[WeatherTool] ⚠️ Timeout fetching forecast for {location}")
            return self._fallback_forecast(location, days)
        except requests.exceptions.RequestException as e:
            print(f"[WeatherTool] ⚠️ API error for {location}: {e}")
            return self._fallback_forecast(location, days)
        except (KeyError, ValueError) as e:
            print(f"[WeatherTool] ⚠️ Parse error for {location}: {e}")
            return self._fallback_forecast(location, days)
    
    def get_agricultural_advice(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate agricultural advice based on current weather data.
        
        Args:
            weather_data: Dict from get_current_weather
            
        Returns:
            Dict with advice and recommendations
        """
        advice = []
        
        # Extract values with fallbacks
        temperature = weather_data.get("temperature", 28)
        humidity = weather_data.get("humidity", 45)
        wind_speed = weather_data.get("wind_speed", 12)
        description = weather_data.get("description", "").lower()
        
        # Check for rain in description
        is_rainy = any(word in description for word in ["مطر", "رش", "زخات", "عاصفة"])
        
        # Irrigation advice
        irrigation_needed = humidity < 40 or temperature > 35
        if irrigation_needed:
            if temperature > 35:
                advice.append("🌡️ يوصى بالري اليوم بسبب ارتفاع درجة الحرارة عن 35 درجة مئوية")
            else:
                advice.append("💧 الرطوبة منخفضة، يُنصح بالري اليوم")
        
        # Frost risk
        frost_risk = temperature < 4
        if frost_risk:
            advice.append("❄️ تحذير: خطر الصقيع، قم بتغطية المحاصيل الحساسة")
        
        # Spray suitability
        spray_suitable = wind_speed < 15 and not is_rainy
        if not spray_suitable:
            if wind_speed >= 15:
                advice.append("💨 لا يُنصح بالرش اليوم بسبب الرياح العالية")
            if is_rainy:
                advice.append("🌧️ لا يُنصح بالرش اليوم بسبب توقع هطول الأمطار")
        else:
            advice.append("✅ الظروف مناسبة للرش اليوم")
        
        # Field work suitability
        field_work_suitable = not is_rainy and 10 <= temperature <= 40
        if field_work_suitable:
            advice.append("👨‍🌾 الظروف مناسبة للأعمال الحقلية اليوم")
        else:
            if not is_rainy:
                advice.append("🌡️ درجة الحرارة غير مناسبة للأعمال الحقلية (يُفضل بين 10-40 درجة)")
            else:
                advice.append("🌧️ يُفضل تأجيل الأعمال الحقلية بسبب توقع الأمطار")
        
        return {
            "irrigation_needed": irrigation_needed,
            "frost_risk": frost_risk,
            "spray_suitable": spray_suitable,
            "field_work_suitable": field_work_suitable,
            "advice": advice,
            "source": "rule_based",
            "timestamp": datetime.now().isoformat()
        }
    
    def _fallback_weather(self, location: str) -> Dict[str, Any]:
        """
        Fallback weather data when API is unavailable.
        """
        return {
            "location": location,
            "temperature": 28.0,
            "feels_like": 30.0,
            "humidity": 45.0,
            "pressure": 1013.0,
            "wind_speed": 12.0,
            "description": "صحو",
            "visibility": 10.0,
            "timestamp": datetime.now().isoformat(),
            "source": "fallback",
            "note": "بيانات تقريبية، WEATHER_API_KEY غير متوفر"
        }
    
    def _fallback_forecast(self, location: str, days: int) -> Dict[str, Any]:
        """
        Fallback forecast data when API is unavailable.
        """
        forecast_list = []
        today = datetime.now().date()
        
        for i in range(min(days, 7)):
            date = today + timedelta(days=i)
            forecast_list.append({
                "date": date.strftime("%Y-%m-%d"),
                "temp_min": 22.0,
                "temp_max": 32.0,
                "humidity": 45.0,
                "description": "صحو جزئي"
            })
        
        return {
            "location": location,
            "days": len(forecast_list),
            "forecast": forecast_list,
            "source": "fallback",
            "note": "بيانات تقريبية، WEATHER_API_KEY غير متوفر"
        }
