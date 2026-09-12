import React, { useState, useEffect } from 'react';
import { FiCloud, FiWind, FiDroplet, FiThermometer, FiAlertCircle } from 'react-icons/fi';

const WeatherWidget = () => {
  const [weatherData, setWeatherData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Cairo coordinates
  const LATITUDE = 30.06;
  const LONGITUDE = 31.25;

  // Weather code to emoji mapping
  const getWeatherEmoji = (code) => {
    if (code === 0) return '☀️';
    if (code >= 1 && code <= 3) return '🌤️';
    if (code >= 45 && code <= 48) return '🌫️';
    if (code >= 51 && code <= 67) return '🌧️';
    if (code >= 71 && code <= 77) return '❄️';
    if (code >= 80 && code <= 82) return '🌦️';
    if (code >= 95 && code <= 99) return '⛈️';
    return '🌡️';
  };

  const getWeatherDescription = (code) => {
    if (code === 0) return 'Clear';
    if (code >= 1 && code <= 3) return 'Partly Cloudy';
    if (code >= 45 && code <= 48) return 'Foggy';
    if (code >= 51 && code <= 67) return 'Rainy';
    if (code >= 71 && code <= 77) return 'Snowy';
    if (code >= 80 && code <= 82) return 'Showers';
    if (code >= 95 && code <= 99) return 'Thunderstorm';
    return 'Unknown';
  };

  useEffect(() => {
    const fetchWeather = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const url = `https://api.open-meteo.com/v1/forecast?latitude=${LATITUDE}&longitude=${LONGITUDE}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&daily=temperature_2m_max,temperature_2m_min,weather_code&timezone=Africa/Cairo&forecast_days=5`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`Weather API error: ${response.status}`);
        }

        const data = await response.json();
        setWeatherData(data);
      } catch (err) {
        console.error('Error fetching weather:', err);
        setError('Failed to load weather data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchWeather();
  }, []);

  // Format date
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  // Skeleton loader
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <div className="h-6 bg-gray-200 rounded w-32 animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded w-20 animate-pulse"></div>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gray-200 rounded-full animate-pulse"></div>
            <div>
              <div className="h-8 bg-gray-200 rounded w-20 animate-pulse mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-24 animate-pulse"></div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded w-20 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-20 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-20 animate-pulse"></div>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-5 gap-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="bg-gray-100 rounded-lg p-2 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-full mb-1"></div>
              <div className="h-6 bg-gray-200 rounded w-full"></div>
              <div className="h-3 bg-gray-200 rounded w-full mt-1"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <div className="flex items-center gap-3 text-red-600">
          <FiAlertCircle className="text-2xl" />
          <div>
            <h4 className="font-medium">Weather Unavailable</h4>
            <p className="text-sm text-gray-500">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // No data state
  if (!weatherData) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 text-center">
        <FiCloud className="text-4xl text-gray-300 mx-auto mb-2" />
        <p className="text-gray-500">No weather data available</p>
      </div>
    );
  }

  const { current, daily } = weatherData;
  const currentTemp = current?.temperature_2m;
  const humidity = current?.relative_humidity_2m;
  const windSpeed = current?.wind_speed_10m;
  const weatherCode = current?.weather_code;
  const weatherEmoji = getWeatherEmoji(weatherCode);
  const weatherDesc = getWeatherDescription(weatherCode);

  // Format daily forecast
  const forecastDays = daily?.time?.map((date, index) => ({
    date: formatDate(date),
    max: daily.temperature_2m_max?.[index],
    min: daily.temperature_2m_min?.[index],
    emoji: getWeatherEmoji(daily.weather_code?.[index]),
    code: daily.weather_code?.[index],
  })) || [];

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Weather</h3>
        <span className="text-xs text-gray-400">Cairo, Egypt</span>
      </div>

      {/* Current Weather */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="text-5xl">{weatherEmoji}</div>
          <div>
            <div className="text-3xl font-bold text-gray-800">
              {currentTemp !== undefined ? `${currentTemp}°C` : '—'}
            </div>
            <div className="text-sm text-gray-500">{weatherDesc}</div>
          </div>
        </div>
        <div className="space-y-1 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <FiDroplet className="text-blue-500" />
            <span>{humidity !== undefined ? `${humidity}%` : '—'}</span>
          </div>
          <div className="flex items-center gap-2">
            <FiWind className="text-cyan-500" />
            <span>{windSpeed !== undefined ? `${windSpeed} km/h` : '—'}</span>
          </div>
          <div className="flex items-center gap-2">
            <FiThermometer className="text-red-500" />
            <span>Feels like {currentTemp !== undefined ? `${currentTemp}°C` : '—'}</span>
          </div>
        </div>
      </div>

      {/* 5-Day Forecast */}
      <div className="mt-4 grid grid-cols-5 gap-2">
        {forecastDays.slice(0, 5).map((day, index) => (
          <div
            key={index}
            className="bg-gray-50 rounded-lg p-2 text-center hover:bg-gray-100 transition-colors"
          >
            <div className="text-xs text-gray-500 font-medium truncate">{day.date}</div>
            <div className="text-2xl my-0.5">{day.emoji}</div>
            <div className="text-sm font-semibold text-gray-800">
              {day.max !== undefined ? `${Math.round(day.max)}°` : '—'}
            </div>
            <div className="text-xs text-gray-400">
              {day.min !== undefined ? `${Math.round(day.min)}°` : '—'}
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-3 pt-3 border-t border-gray-100 text-center">
        <span className="text-xs text-gray-400">Powered by Open-Meteo</span>
      </div>
    </div>
  );
};

export default WeatherWidget;
