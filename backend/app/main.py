"""
CropMind - Main Application
FastAPI application entry point
Author: CropMind Team
Date: 2026
"""
from dotenv import load_dotenv
import pathlib
load_dotenv(pathlib.Path(__file__).parent.parent.parent / ".env")

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db
import logging
logging.basicConfig(level=logging.DEBUG)

from app.api.routes import (
    farms, crops, finance, inventory,
    irrigation, market, workforce,
    alerts, agents, auth,
)
from app.api.websockets import realtime
from computer_vision.api.cv_service import router as cv_router

# ============================================
# Lifespan Manager
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting CropMind API...")
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("🛑 Shutting down CropMind API...")
    await close_db()
    print("✅ Database connections closed")


# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Farm Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ============================================
# CORS Middleware
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Include Routers
# ============================================

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(farms.router, prefix="/api/farms", tags=["Farms"])
app.include_router(crops.router, prefix="/api/crops", tags=["Crops"])
app.include_router(finance.router, prefix="/api/finance", tags=["Finance"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(irrigation.router, prefix="/api/irrigation", tags=["Irrigation"])
app.include_router(market.router, prefix="/api/market", tags=["Market"])
app.include_router(workforce.router, prefix="/api/workforce", tags=["Workforce"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(agents.router, prefix="/api/agents", tags=["AI Agents"])
app.include_router(cv_router, prefix="/api/cv", tags=["Computer Vision"])
app.include_router(realtime.router, tags=["WebSocket"])


# ============================================
# Health Check
# ============================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns application status.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "debug": settings.DEBUG,
    }


# ============================================
# Root Endpoint
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }