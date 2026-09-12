"""
CropMind - Backend Configuration
Core settings management using pydantic-settings
Author: CropMind Team
Date: 2026
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

# Find .env file in multiple possible locations
_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env_files = (
    os.path.join(_base_dir, ".env"),           # CropMind-main/.env
    os.path.join(_base_dir, "..", ".env"),     # one level up
    ".env",                                     # current directory
    "../.env",                                  # one level up relative
)

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./cropmind.db",
        description="Async SQLite or PostgreSQL connection URL"
    )
    
    # JWT Authentication
    SECRET_KEY: str = Field(
        default="your-secret-key-here-change-in-production",
        description="Secret key for JWT signing",
        min_length=32
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes",
        ge=1
    )
    
    # External APIs
    GROQ_API_KEY: str = Field(
        default="",
        description="Groq API key for Farm Copilot (Llama 3)"
    )
    WEATHER_API_KEY: str = Field(
        default="",
        description="Weather API key for weather data"
    )
    
    # Application
    APP_NAME: str = Field(
        default="CropMind",
        description="Application name"
    )
    DEBUG: bool = Field(
        default=True,
        description="Debug mode flag"
    )
    
    # CORS
    ALLOWED_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
        ],
        description="Allowed CORS origins"
    )
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(
        default=100,
        description="Maximum requests per rate limit window"
    )
    RATE_LIMIT_WINDOW: int = Field(
        default=60,
        description="Rate limit window in seconds"
    )
    
    # Model Paths
    PRICE_FORECASTING_PATH: str = Field(
        default="ml_models/price_forecasting/models",
        description="Path to price forecasting models"
    )
    ANOMALY_DETECTION_PATH: str = Field(
        default="ml_models/anomaly_detection/models",
        description="Path to anomaly detection models"
    )
    CV_MODEL_PATH: str = Field(
        default="computer_vision/models/model_unquant.tflite",
        description="Path to computer vision model"
    )
    CV_LABELS_PATH: str = Field(
        default="computer_vision/models/labels.txt",
        description="Path to computer vision labels"
    )
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Skip validation - handled via .env file"""
        return v
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if v.startswith("sqlite"):
            return v
        if "postgresql+asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://")
        return v
    
    class Config:
        env_file = _env_files
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

# Singleton instance
settings = Settings()