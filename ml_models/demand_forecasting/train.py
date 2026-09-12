"""
CropMind - Demand Forecasting Training Script
Trains Prophet and GBM models for crop demand forecasting

Author: CropMind Team
Date: 2026
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')


# ============================================
# Configuration
# ============================================

DATA_PATH = "data/demand_data.csv"
MODELS_PATH = "ml_models/demand_forecasting/models"
PROPHET_CROPS = ["cotton", "rice", "sugarcane", "wheat"]
GBM_CROPS = ["onion", "potato", "tomato", "maize"]
TEST_SIZE = 0.2
RANDOM_STATE = 42


# ============================================
# Data Loading
# ============================================

def load_data():
    """
    Load demand data from CSV file.
    """
    if not os.path.exists(DATA_PATH):
        print(f"❌ Data file not found: {DATA_PATH}")
        print("📝 Generating synthetic data for training...")
        return generate_synthetic_data()
    
    df = pd.read_csv(DATA_PATH)
    print(f"✅ Data loaded: {len(df)} rows")
    return df


def generate_synthetic_data():
    """
    Generate synthetic demand data for training purposes.
    """
    np.random.seed(RANDOM_STATE)
    
    crops = ["cotton", "rice", "sugarcane", "wheat", "onion", "potato", "tomato", "maize"]
    
    # Generate dates from 2010 to 2025
    dates = pd.date_range(start="2010-01-01", end="2025-12-01", freq="MS")
    
    data = []
    
    for crop in crops:
        # Base demand pattern
        base_demand = {
            "cotton": 200,
            "rice": 1200,
            "sugarcane": 300,
            "wheat": 1000,
            "onion": 400,
            "potato": 450,
            "tomato": 500,
            "maize": 800
        }
        
        base = base_demand.get(crop, 500)
        
        for date in dates:
            # Add seasonal pattern
            month = date.month
            year = date.year
            
            # Seasonal factor (sine wave)
            seasonal = 1 + 0.3 * np.sin(2 * np.pi * (month - 6) / 12)
            
            # Trend factor (slight increase over time)
            trend = 1 + 0.02 * (year - 2010) / 15
            
            # Random noise
            noise = 1 + np.random.normal(0, 0.05)
            
            # Anomalies (2020 was a special year)
            if 2020 <= year <= 2021:
                anomaly_factor = 0.7 + np.random.uniform(0, 0.2)
            else:
                anomaly_factor = 1.0
            
            demand = base * seasonal * trend * noise * anomaly_factor
            
            data.append({
                "date": date,
                "crop": crop,
                "demand": round(max(10, demand), 2)
            })
    
    df = pd.DataFrame(data)
    
    # Save generated data
    os.makedirs("data", exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"✅ Synthetic data generated and saved to {DATA_PATH}")
    
    return df


# ============================================
# Data Preprocessing
# ============================================

def preprocess_data(df, crop):
    """
    Preprocess data for a specific crop.
    - Remove 2020-2021 data (anomaly years)
    - Apply log transformation
    
    Args:
        df: Full dataframe
        crop: Crop name
        
    Returns:
        Preprocessed dataframe
    """
    # Filter for specific crop
    crop_df = df[df["crop"] == crop].copy()
    
    # Remove 2020-2021 data (anomaly years)
    crop_df["year"] = pd.to_datetime(crop_df["date"]).dt.year
    crop_df = crop_df[~crop_df["year"].isin([2020, 2021])]
    
    # Sort by date
    crop_df = crop_df.sort_values("date").reset_index(drop=True)
    
    # Create time index
    crop_df["time_idx"] = range(len(crop_df))
    
    # Log transform for GBM
    crop_df["demand_log"] = np.log1p(crop_df["demand"])
    
    return crop_df


# ============================================
# Prophet Training
# ============================================

def train_prophet(crop, df):
    """
    Train Prophet model for a stable crop.
    """
    print(f"\n🔄 Training Prophet for {crop}...")
    
    # Prepare Prophet data
    prophet_df = df[["date", "demand"]].rename(columns={"date": "ds", "demand": "y"})
    
    # Split data
    train_size = int(len(prophet_df) * (1 - TEST_SIZE))
    train = prophet_df[:train_size]
    test = prophet_df[train_size:]
    
    # Train Prophet
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        changepoint_prior_scale=0.05
    )
    model.fit(train)
    
    # Predict on test
    future = model.make_future_dataframe(periods=len(test), include_history=False)
    forecast = model.predict(future)
    
    # Evaluate
    y_true = test["y"].values
    y_pred = forecast["yhat"].values
    
    mae = mean_absolute_error(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100
    
    print(f"   ✅ MAE: {mae:.2f}")
    print(f"   ✅ MAPE: {mape:.2f}%")
    
    return model, {"mae": mae, "mape": mape}


# ============================================
# GBM Training
# ============================================

def train_gbm(crop, df):
    """
    Train GradientBoostingRegressor for a volatile crop.
    """
    print(f"\n🔄 Training GBM for {crop}...")
    
    # Prepare features
    gbm_df = df.copy()
    gbm_df["month"] = pd.to_datetime(gbm_df["date"]).dt.month
    gbm_df["year"] = pd.to_datetime(gbm_df["date"]).dt.year
    
    # Create lag features
    for lag in [1, 3, 6, 12]:
        gbm_df[f"demand_lag_{lag}"] = gbm_df["demand"].shift(lag)
    
    gbm_df = gbm_df.dropna()
    
    # Features and target
    feature_cols = ["time_idx", "month", "year"]
    for lag in [1, 3, 6, 12]:
        feature_cols.append(f"demand_lag_{lag}")
    
    X = gbm_df[feature_cols]
    y = gbm_df["demand"]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, shuffle=False
    )
    
    # Train GBM
    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=RANDOM_STATE
    )
    model.fit(X_train, y_train)
    
    # Predict
    y_pred = model.predict(X_test)
    
    # Evaluate
    mae = mean_absolute_error(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred) * 100
    
    print(f"   ✅ MAE: {mae:.2f}")
    print(f"   ✅ MAPE: {mape:.2f}%")
    
    return model, {"mae": mae, "mape": mape, "feature_names": feature_cols}


# ============================================
# Save Models
# ============================================

def save_models(prophet_models, gbm_models, metadata):
    """
    Save all trained models to disk.
    """
    os.makedirs(MODELS_PATH, exist_ok=True)
    
    # Save Prophet models
    for crop, model in prophet_models.items():
        with open(os.path.join(MODELS_PATH, f"{crop.capitalize()}_prophet.pkl"), "wb") as f:
            pickle.dump(model, f)
        print(f"   ✅ Saved {crop.capitalize()}_prophet.pkl")
    
    # Save GBM models
    for crop, model in gbm_models.items():
        with open(os.path.join(MODELS_PATH, f"{crop.capitalize()}_gbm.pkl"), "wb") as f:
            pickle.dump(model, f)
        print(f"   ✅ Saved {crop.capitalize()}_gbm.pkl")
    
    # Save metadata
    metadata_path = os.path.join(MODELS_PATH, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✅ Saved metadata.json")


# ============================================
# Main Training Pipeline
# ============================================

def main():
    """
    Main training pipeline.
    """
    print("="*60)
    print("🌾 CropMind - Demand Forecasting Training")
    print("="*60)
    
    # Load data
    print("\n📊 Loading data...")
    df = load_data()
    
    prophet_models = {}
    gbm_models = {}
    metadata = {
        "train_date": datetime.now().isoformat(),
        "prophet_crops": [],
        "gbm_crops": [],
        "metrics": {}
    }
    
    # Train Prophet for stable crops
    print("\n" + "="*60)
    print("🤖 Training Prophet Models (Stable Crops)")
    print("="*60)
    
    for crop in PROPHET_CROPS:
        crop_df = preprocess_data(df, crop)
        model, metrics = train_prophet(crop, crop_df)
        prophet_models[crop] = model
        metadata["prophet_crops"].append(crop)
        metadata["metrics"][f"{crop}_prophet"] = metrics
    
    # Train GBM for volatile crops
    print("\n" + "="*60)
    print("🧠 Training GBM Models (Volatile Crops)")
    print("="*60)
    
    for crop in GBM_CROPS:
        crop_df = preprocess_data(df, crop)
        model, metrics = train_gbm(crop, crop_df)
        gbm_models[crop] = model
        metadata["gbm_crops"].append(crop)
        metadata["metrics"][f"{crop}_gbm"] = metrics
    
    # Save models
    print("\n" + "="*60)
    print("💾 Saving Models")
    print("="*60)
    save_models(prophet_models, gbm_models, metadata)
    
    # Final summary
    print("\n" + "="*60)
    print("📊 Training Summary")
    print("="*60)
    
    for crop in PROPHET_CROPS:
        metrics = metadata["metrics"][f"{crop}_prophet"]
        print(f"   {crop.capitalize():15} (Prophet) - MAPE: {metrics['mape']:.2f}%")
    
    for crop in GBM_CROPS:
        metrics = metadata["metrics"][f"{crop}_gbm"]
        print(f"   {crop.capitalize():15} (GBM)     - MAPE: {metrics['mape']:.2f}%")
    
    print("\n" + "="*60)
    print("✅ Training Complete!")
    print(f"📁 Models saved to: {MODELS_PATH}")
    print("="*60)


if __name__ == "__main__":
    main()
