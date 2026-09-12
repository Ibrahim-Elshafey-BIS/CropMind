"""
Training Script for Price Forecasting Models
Trains Prophet for stable commodities and LSTM for volatile commodities
Part of CropMind - Market Intelligence Agent
"""

import os
import pickle
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
from prophet import Prophet
from sklearn.preprocessing import MinMaxScaler

# Import LSTM model
from lstm_model import LSTMPredictor

# ============================================
# 1. CONFIGURATION
# ============================================

# Commodities and their models
COMMODITIES_CONFIG = {
    'Potato': {'model_type': 'prophet', 'price_range': (500, 5000)},
    'Wheat': {'model_type': 'prophet', 'price_range': (1000, 4000)},
    'Brinjal': {'model_type': 'prophet', 'price_range': (500, 6000)},
    'Tomato': {'model_type': 'lstm', 'price_range': (500, 10000)},
    'Onion': {'model_type': 'lstm', 'price_range': (500, 8000)}
}

TEST_SIZE = 90
LOOKBACK = 30

# Base path for models and outputs
BASE_PATH = 'ml_models/price_forecasting'

# ============================================
# 2. DATA LOADING
# ============================================

def load_data_from_kaggle():
    """
    Load data from Kaggle dataset.
    Returns combined DataFrame for 2022-2024.
    """
    import kagglehub
    
    print("📥 Loading data from Kaggle...")
    dataset_path = "khandelwalmanas/daily-commodity-prices-india"
    download_path = kagglehub.dataset_download(dataset_path)
    
    parquet_folder = os.path.join(download_path, 'parquet')
    
    files = ['2022.parquet', '2023.parquet', '2024.parquet']
    dfs = []
    
    for file in files:
        file_path = os.path.join(parquet_folder, file)
        if os.path.exists(file_path):
            df = pd.read_parquet(file_path)
            dfs.append(df)
            print(f"  ✅ {file}: {len(df):,} rows")
    
    df_all = pd.concat(dfs, ignore_index=True)
    print(f"✅ Total data: {len(df_all):,} rows")
    return df_all


def prepare_commodity_data(df_all, commodity, price_range):
    """
    Prepare daily average data for a specific commodity.
    
    Args:
        df_all: Combined DataFrame
        commodity: Commodity name
        price_range: Tuple (min_price, max_price) for filtering outliers
    
    Returns:
        DataFrame with columns ['ds', 'y']
    """
    print(f"\n📊 Preparing: {commodity}")
    
    # Filter commodity
    df_commodity = df_all[df_all['Commodity'] == commodity].copy()
    print(f"  Rows: {len(df_commodity):,}")
    
    # Convert date
    df_commodity['Date'] = pd.to_datetime(df_commodity['Arrival_Date'])
    df_commodity = df_commodity[df_commodity['Modal_Price'] > 0]
    
    # Filter outliers
    min_price, max_price = price_range
    df_clean = df_commodity[
        (df_commodity['Modal_Price'] >= min_price) & 
        (df_commodity['Modal_Price'] <= max_price)
    ]
    
    removed = len(df_commodity) - len(df_clean)
    if removed > 0:
        print(f"  Removed outliers: {removed:,} rows")
    
    # Daily average
    df_daily = df_clean.groupby('Date')['Modal_Price'].mean().reset_index()
    df_daily.columns = ['ds', 'y']
    df_daily = df_daily.sort_values('ds').reset_index(drop=True)
    
    print(f"  Days: {len(df_daily)}")
    print(f"  Range: {df_daily['ds'].min()} to {df_daily['ds'].max()}")
    print(f"  Avg Price: {df_daily['y'].mean():.2f}")
    
    return df_daily

# ============================================
# 3. PROPHET MODEL
# ============================================

def train_prophet(df_daily, commodity):
    """
    Train Prophet model for stable commodities.
    """
    print(f"\n🤖 Training Prophet: {commodity}")
    
    # Split data
    train = df_daily[:-TEST_SIZE]
    test = df_daily[-TEST_SIZE:]
    
    # Build model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        seasonality_mode='multiplicative',
        changepoint_prior_scale=0.05
    )
    
    model.fit(train)
    
    # Predict on test
    future_test = model.make_future_dataframe(periods=len(test), include_history=False)
    forecast_test = model.predict(future_test)
    
    y_true = test['y'].values
    y_pred = forecast_test['yhat'].values[:len(test)]
    
    # Handle negative predictions
    y_pred = np.maximum(y_pred, 0)
    
    # Calculate metrics
    mae = mean_absolute_error(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    print(f"  ✅ MAE: {mae:.2f}")
    print(f"  ✅ MAPE: {mape:.2f}%")
    
    return model, test, y_true, y_pred, mae, mape


def forecast_prophet(model, df_daily, commodity, mape):
    """
    Generate 90-day forecast and plot.
    """
    print(f"\n📈 Forecasting: {commodity}")
    
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(df_daily['ds'], df_daily['y'], label='Historical', color='blue', alpha=0.7)
    ax.plot(forecast['ds'], forecast['yhat'], label='Forecast', color='red', linestyle='--')
    ax.fill_between(
        forecast['ds'],
        forecast['yhat_lower'],
        forecast['yhat_upper'],
        color='red', alpha=0.2, label='Uncertainty'
    )
    ax.axvline(x=df_daily['ds'].max(), color='green', linestyle=':', label='Today')
    
    ax.set_title(f'{commodity} Price Forecast (MAPE: {mape:.2f}%)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save in the new path
    output_path = f'{BASE_PATH}/outputs'
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(f'{output_path}/{commodity}_forecast.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return forecast

# ============================================
# 4. LSTM MODEL
# ============================================

def train_lstm(df_daily, commodity):
    """
    Train LSTM model for volatile commodities.
    """
    print(f"\n🧠 Training LSTM: {commodity}")
    
    # Prepare data
    data = df_daily['y'].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    
    # Split
    train_data = data_scaled[:-TEST_SIZE]
    test_data = data_scaled[-TEST_SIZE:]
    
    # Create sequences
    lstm = LSTMPredictor(lookback=LOOKBACK)
    X_train, y_train = lstm.create_sequences(train_data)
    X_test, y_test = lstm.create_sequences(test_data)
    
    # Reshape for LSTM
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
    
    # Build and train
    lstm.build_model()
    split = int(0.8 * len(X_train))
    lstm.train(
        X_train[:split], y_train[:split],
        X_val=X_train[split:], y_val=y_train[split:],
        epochs=50, batch_size=32
    )
    
    # Predict
    y_pred_scaled = lstm.predict(X_test)
    y_pred = scaler.inverse_transform(y_pred_scaled)
    
    y_true = df_daily['y'].values[-len(y_pred):]
    y_pred = y_pred.flatten()
    
    # Calculate metrics
    mae = mean_absolute_error(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    print(f"  ✅ MAE: {mae:.2f}")
    print(f"  ✅ MAPE: {mape:.2f}%")
    
    return lstm, scaler, test_data, y_true, y_pred, mae, mape


def forecast_lstm(lstm, scaler, df_daily, commodity, mape):
    """
    Generate 90-day forecast using LSTM.
    """
    print(f"\n📈 Forecasting: {commodity}")
    
    # Get last sequence
    data = df_daily['y'].values.reshape(-1, 1)
    data_scaled = scaler.transform(data)
    last_seq = data_scaled[-LOOKBACK:].flatten()
    
    # Predict future
    future_scaled = lstm.predict_future(last_seq, steps=90)
    future = scaler.inverse_transform(future_scaled.reshape(-1, 1))
    
    # Generate dates
    last_date = df_daily['ds'].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=90)
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(df_daily['ds'], df_daily['y'], label='Historical', color='blue', alpha=0.7)
    ax.plot(future_dates, future, label='LSTM Forecast', color='red', linestyle='--')
    ax.axvline(x=last_date, color='green', linestyle=':', label='Today')
    
    ax.set_title(f'{commodity} Price Forecast (LSTM, MAPE: {mape:.2f}%)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save in the new path
    output_path = f'{BASE_PATH}/outputs'
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(f'{output_path}/{commodity}_forecast.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return future

# ============================================
# 5. SAVE MODELS
# ============================================

def save_models(models_data):
    """
    Save all trained models.
    
    Args:
        models_data: Dict with commodity as key and model data as value
    """
    # New path for models
    models_path = f'{BASE_PATH}/models'
    os.makedirs(models_path, exist_ok=True)
    
    for commodity, data in models_data.items():
        model_type = data['type']
        
        if model_type == 'prophet':
            # Save Prophet model
            with open(f'{models_path}/{commodity}_prophet.pkl', 'wb') as f:
                pickle.dump(data['model'], f)
            print(f"  ✅ {commodity}_prophet.pkl")
        
        elif model_type == 'lstm':
            # Save LSTM model and scaler (.h5 format)
            data['model'].save_model(f'{models_path}/{commodity}_lstm')
            print(f"  ✅ {commodity}_lstm.h5")
            print(f"  ✅ {commodity}_lstm_scaler.pkl")

# ============================================
# 6. MAIN TRAINING PIPELINE
# ============================================

def main():
    """
    Main training pipeline for all commodities.
    """
    print("="*60)
    print("🌾 CropMind - Price Forecasting Training")
    print("="*60)
    
    # Load data
    df_all = load_data_from_kaggle()
    
    # Results storage
    all_models = {}
    all_results = {}
    
    # Train for each commodity
    for commodity, config in COMMODITIES_CONFIG.items():
        print("\n" + "="*60)
        print(f"📊 Training: {commodity} ({config['model_type'].upper()})")
        print("="*60)
        
        # Prepare data
        df_daily = prepare_commodity_data(df_all, commodity, config['price_range'])
        
        # Train based on model type
        if config['model_type'] == 'prophet':
            model, test, y_true, y_pred, mae, mape = train_prophet(df_daily, commodity)
            forecast = forecast_prophet(model, df_daily, commodity, mape)
            
            all_models[commodity] = {
                'type': 'prophet',
                'model': model,
                'data': df_daily
            }
            
        elif config['model_type'] == 'lstm':
            model, scaler, test_data, y_true, y_pred, mae, mape = train_lstm(df_daily, commodity)
            forecast = forecast_lstm(model, scaler, df_daily, commodity, mape)
            
            all_models[commodity] = {
                'type': 'lstm',
                'model': model,
                'scaler': scaler,
                'data': df_daily
            }
        
        # Store results
        all_results[commodity] = {
            'mae': mae,
            'mape': mape
        }
    
    # Save all models
    print("\n" + "="*60)
    print("💾 Saving models...")
    print("="*60)
    save_models(all_models)
    
    # Final summary
    print("\n" + "="*60)
    print("📊 Final Results Summary")
    print("="*60)
    
    for commodity, results in all_results.items():
        status = "✅ PASS" if results['mape'] < 10 else "⚠️ NEEDS WORK"
        print(f"  {commodity:15} MAPE: {results['mape']:6.2f}%  {status}")
    
    print("\n" + "="*60)
    print("✅ Training Complete!")
    print(f"📁 Models saved in: {BASE_PATH}/models/")
    print(f"📁 Forecasts saved in: {BASE_PATH}/outputs/")
    print("="*60)


if __name__ == "__main__":
    main()
