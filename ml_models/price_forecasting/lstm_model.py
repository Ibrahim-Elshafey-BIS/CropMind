"""
LSTM Model for Price Forecasting
Used for volatile commodities like Tomato and Onion
Part of CropMind - Market Intelligence Agent
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
import pickle
import os


class LSTMPredictor:
    """
    LSTM model for time series price forecasting.
    Handles volatile commodities with high price fluctuations.
    """
    
    def __init__(self, lookback=30, units=50, dropout=0.2):
        """
        Initialize LSTM model.
        
        Args:
            lookback (int): Number of previous days to use for prediction
            units (int): Number of LSTM units in each layer
            dropout (float): Dropout rate for regularization
        """
        self.lookback = lookback
        self.units = units
        self.dropout = dropout
        self.model = None
        self.scaler = MinMaxScaler()
        self.history = None
        
    def create_sequences(self, data):
        """
        Create sequences for LSTM training.
        
        Args:
            data (np.array): Scaled time series data of shape (n_samples, 1)
            
        Returns:
            X (np.array): Input sequences of shape (n_samples-lookback, lookback, 1)
            y (np.array): Target values of shape (n_samples-lookback, 1)
        """
        X, y = [], []
        for i in range(self.lookback, len(data)):
            X.append(data[i-self.lookback:i, 0])
            y.append(data[i, 0])
        return np.array(X), np.array(y)
    
    def build_model(self):
        """
        Build LSTM model architecture with two LSTM layers.
        
        Returns:
            Sequential: Compiled Keras model
        """
        self.model = Sequential([
            LSTM(self.units, return_sequences=True, input_shape=(self.lookback, 1)),
            Dropout(self.dropout),
            LSTM(self.units, return_sequences=False),
            Dropout(self.dropout),
            Dense(25, activation='relu'),
            Dense(1)
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        return self.model
    
    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=50, batch_size=32):
        """
        Train the LSTM model with early stopping.
        
        Args:
            X_train (np.array): Training input sequences
            y_train (np.array): Training target values
            X_val (np.array, optional): Validation input sequences
            y_val (np.array, optional): Validation target values
            epochs (int): Maximum number of epochs
            batch_size (int): Batch size for training
            
        Returns:
            History: Training history object
        """
        callbacks = []
        
        if X_val is not None and y_val is not None:
            callbacks.append(
                EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                )
            )
            validation_data = (X_val, y_val)
        else:
            validation_data = None
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks if callbacks else None,
            verbose=1
        )
        return self.history
    
    def predict(self, X):
        """
        Make predictions on new data.
        
        Args:
            X (np.array): Input sequences
            
        Returns:
            np.array: Predicted values
        """
        return self.model.predict(X, verbose=0)
    
    def predict_future(self, last_sequence, steps=90):
        """
        Predict multiple future steps recursively.
        
        Args:
            last_sequence (np.array): Last 'lookback' values (scaled)
            steps (int): Number of future steps to predict
            
        Returns:
            np.array: Predicted future values (scaled)
        """
        predictions = []
        current_seq = last_sequence.copy()
        
        for _ in range(steps):
            # Reshape for prediction
            input_seq = current_seq.reshape(1, self.lookback, 1)
            pred = self.predict(input_seq)
            predictions.append(pred[0, 0])
            
            # Update sequence (shift and add prediction)
            current_seq = np.roll(current_seq, -1)
            current_seq[-1] = pred[0, 0]
        
        return np.array(predictions)
    
    def save_model(self, path_prefix):
        """
        Save model weights and scaler.
        
        Args:
            path_prefix (str): Path prefix for saving files
                              e.g., 'ml_models/price_forecasting/models/tomato_lstm'
        """
        os.makedirs(os.path.dirname(path_prefix), exist_ok=True)
        
        # Save model in HDF5 format (.h5)
        self.model.save(f'{path_prefix}.h5')
        
        # Save scaler
        with open(f'{path_prefix}_scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"✅ Model saved to {path_prefix}.h5")
        print(f"✅ Scaler saved to {path_prefix}_scaler.pkl")
    
    def load_model(self, path_prefix):
        """
        Load model weights and scaler.
        
        Args:
            path_prefix (str): Path prefix for loading files
                              e.g., 'ml_models/price_forecasting/models/tomato_lstm'
        """
        # Load model
        self.model = tf.keras.models.load_model(f'{path_prefix}.h5')
        
        # Load scaler
        with open(f'{path_prefix}_scaler.pkl', 'rb') as f:
            self.scaler = pickle.load(f)
        
        print(f"✅ Model loaded from {path_prefix}.h5")
        print(f"✅ Scaler loaded from {path_prefix}_scaler.pkl")
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model on test data.
        
        Args:
            X_test (np.array): Test input sequences
            y_test (np.array): Test target values
            
        Returns:
            dict: Evaluation metrics (loss, mae)
        """
        loss, mae = self.model.evaluate(X_test, y_test, verbose=0)
        return {'loss': loss, 'mae': mae}
