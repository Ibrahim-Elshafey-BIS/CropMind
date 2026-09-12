"""
CropMind - Anomaly Detection Module
Isolation Forest for Sensor Data Anomaly Detection
Part of CropMind AI-Powered Farm Management System

Author: CropMind Team
Date: 2026
"""

import numpy as np
import pandas as pd
import joblib
import os
from typing import Dict, Optional, Tuple, List
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class SensorAnomalyDetector:
    """
    Anomaly Detection using Isolation Forest for IoT Sensor Data.
    Detects anomalies in soil moisture, temperature, humidity, pH, and nitrogen.
    
    Features:
        - soil_moisture: 20-80% (normal), 0-10% (anomaly)
        - temperature: 15-35°C (normal), 45-60°C (anomaly)
        - humidity: 40-80% (normal), 0-15% (anomaly)
        - ph: 6.0-7.5 (normal), 3.0-4.5 (anomaly)
        - nitrogen: 30-60 ppm (normal), 80-100 ppm (anomaly)
    
    Usage:
        detector = SensorAnomalyDetector(contamination=0.05)
        detector.fit(X_train)
        detector.save('models/anomaly_detector.pkl')
        
        # Load and predict
        detector = SensorAnomalyDetector()
        detector.load('models/anomaly_detector.pkl')
        result = detector.is_anomaly(sensor_reading)
    """
    
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        """
        Initialize the anomaly detector.
        
        Args:
            contamination: Expected proportion of outliers (default: 0.05)
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state
        self.model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = [
            'soil_moisture',
            'temperature',
            'humidity',
            'ph',
            'nitrogen'
        ]
        self.is_fitted: bool = False
        
    def fit(self, X: np.ndarray) -> 'SensorAnomalyDetector':
        """
        Train the Isolation Forest model on the provided data.
        
        Args:
            X: Training data of shape (n_samples, n_features)
            
        Returns:
            self: Fitted detector instance
        """
        if X.shape[1] != len(self.feature_names):
            raise ValueError(
                f"Expected {len(self.feature_names)} features, got {X.shape[1]}"
            )
        
        print("🔧 Training Isolation Forest model...")
        
        # Scale the features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Initialize and train Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
            max_samples='auto',
            bootstrap=True,
            warm_start=False
        )
        
        self.model.fit(X_scaled)
        self.is_fitted = True
        
        print(f"✅ Model trained successfully on {X.shape[0]} samples")
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict anomalies for the given data.
        
        Args:
            X: Input data of shape (n_samples, n_features)
            
        Returns:
            np.ndarray: 1 for normal, -1 for anomaly
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Get anomaly scores for the given data.
        More negative scores indicate more anomalous.
        
        Args:
            X: Input data of shape (n_samples, n_features)
            
        Returns:
            np.ndarray: Anomaly scores
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X_scaled = self.scaler.transform(X)
        return self.model.score_samples(X_scaled)
    
    def is_anomaly(self, reading: Dict) -> Dict:
        """
        Analyze a single sensor reading and return detailed results.
        
        Args:
            reading: Dictionary containing sensor readings
                   Example: {
                       'soil_moisture': 45.0,
                       'temperature': 28.5,
                       'humidity': 65.0,
                       'ph': 6.8,
                       'nitrogen': 45.0
                   }
        
        Returns:
            Dict containing:
                - is_anomaly: bool
                - severity: str (Normal/Low/Medium/High)
                - anomaly_score: float
                - confidence: float (0-100)
                - reading: dict (original reading)
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Extract features in correct order
        features = [reading.get(f, 0.0) for f in self.feature_names]
        X = np.array(features).reshape(1, -1)
        
        # Scale and predict
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        score = self.model.score_samples(X_scaled)[0]
        
        # Convert prediction to boolean
        is_anomaly = (prediction == -1)
        
        # Determine severity
        severity = self._calculate_severity(score, is_anomaly)
        
        # Calculate confidence based on score magnitude
        confidence = self._calculate_confidence(score, is_anomaly)
        
        return {
            'is_anomaly': is_anomaly,
            'severity': severity,
            'anomaly_score': float(score),
            'confidence': confidence,
            'reading': reading
        }
    
    def _calculate_severity(self, score: float, is_anomaly: bool) -> str:
        """
        Calculate severity level based on anomaly score.
        
        Args:
            score: Anomaly score from Isolation Forest
            is_anomaly: Whether it's classified as anomaly
            
        Returns:
            str: Severity level (Normal/Low/Medium/High)
        """
        if not is_anomaly:
            return 'Normal'
        
        # More negative = more anomalous
        if score < -0.8:
            return 'High'
        elif score < -0.5:
            return 'Medium'
        else:
            return 'Low'
    
    def _calculate_confidence(self, score: float, is_anomaly: bool) -> float:
        """
        Calculate confidence level based on score magnitude.
        
        Args:
            score: Anomaly score
            is_anomaly: Whether it's classified as anomaly
            
        Returns:
            float: Confidence percentage (0-100)
        """
        # Map score to confidence
        # Normal: positive scores -> higher confidence
        # Anomaly: negative scores -> higher confidence
        if not is_anomaly:
            # For normal: score > 0 means more confident
            if score > 0.5:
                return 95.0
            elif score > 0.2:
                return 80.0
            elif score > 0.0:
                return 65.0
            else:
                return 50.0
        else:
            # For anomaly: score < 0 means more confident
            if score < -0.8:
                return 95.0
            elif score < -0.5:
                return 80.0
            elif score < -0.2:
                return 65.0
            else:
                return 50.0
    
    def save(self, path: str) -> None:
        """
        Save the trained model to disk using joblib.
        
        Args:
            path: File path to save the model
        """
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted model. Call fit() first.")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model and scaler
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'contamination': self.contamination,
            'random_state': self.random_state,
            'is_fitted': self.is_fitted,
            'version': '1.0.0'
        }
        
        joblib.dump(model_data, path)
        print(f"✅ Model saved to: {path}")
    
    def load(self, path: str) -> 'SensorAnomalyDetector':
        """
        Load a trained model from disk.
        
        Args:
            path: File path to load the model from
            
        Returns:
            self: Loaded detector instance
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        # Load model data
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data.get('feature_names', self.feature_names)
        self.contamination = model_data.get('contamination', self.contamination)
        self.random_state = model_data.get('random_state', self.random_state)
        self.is_fitted = model_data.get('is_fitted', True)
        
        print(f"✅ Model loaded from: {path}")
        return self
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance (approximate using standard deviation).
        Higher std means more variation and potential importance.
        
        Returns:
            Dict: Feature importance scores
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        importance = {}
        for i, name in enumerate(self.feature_names):
            # Use scaler's scale (std) as importance indicator
            importance[name] = float(self.scaler.scale_[i])
        
        return importance
    
    def get_model_info(self) -> Dict:
        """
        Get information about the trained model.
        
        Returns:
            Dict: Model information
        """
        return {
            'is_fitted': self.is_fitted,
            'contamination': self.contamination,
            'random_state': self.random_state,
            'feature_names': self.feature_names,
            'n_features': len(self.feature_names),
            'n_estimators': self.model.n_estimators if self.model else None,
            'version': '1.0.0'
        }
    
    def batch_predict(self, readings: List[Dict]) -> List[Dict]:
        """
        Analyze multiple sensor readings in batch.
        
        Args:
            readings: List of sensor reading dictionaries
            
        Returns:
            List[Dict]: List of analysis results
        """
        results = []
        for reading in readings:
            results.append(self.is_anomaly(reading))
        return results


# ============================================
# STANDALONE TESTING
# ============================================

def test_detector():
    """
    Test the anomaly detector with sample data.
    """
    print("="*60)
    print("🧪 Testing SensorAnomalyDetector")
    print("="*60)
    
    # Create sample data
    np.random.seed(42)
    n_samples = 100
    
    # Normal data
    normal_data = np.random.uniform(
        low=[20, 15, 40, 6.0, 30],
        high=[80, 35, 80, 7.5, 60],
        size=(n_samples, 5)
    )
    
    # Anomaly data
    anomaly_data = np.random.uniform(
        low=[0, 45, 0, 3.0, 80],
        high=[10, 60, 15, 4.5, 100],
        size=(int(n_samples * 0.1), 5)
    )
    
    X = np.vstack([normal_data, anomaly_data])
    
    print(f"\n📊 Created {X.shape[0]} samples")
    print(f"   Normal: {normal_data.shape[0]}")
    print(f"   Anomalies: {anomaly_data.shape[0]}")
    
    # Train detector
    detector = SensorAnomalyDetector(contamination=0.1)
    detector.fit(X)
    
    # Predict
    predictions = detector.predict(X)
    anomalies = np.sum(predictions == -1)
    
    print(f"\n📈 Predictions:")
    print(f"   Detected anomalies: {anomalies}")
    print(f"   Normal samples: {len(predictions) - anomalies}")
    
    # Test single reading
    print("\n🔍 Testing single readings:")
    
    # Normal reading
    normal_reading = {
        'soil_moisture': 45.0,
        'temperature': 28.5,
        'humidity': 65.0,
        'ph': 6.8,
        'nitrogen': 45.0
    }
    
    result = detector.is_anomaly(normal_reading)
    print(f"\n   ✅ Normal Reading:")
    print(f"      Result: {'ANOMALY' if result['is_anomaly'] else 'NORMAL'}")
    print(f"      Severity: {result['severity']}")
    print(f"      Score: {result['anomaly_score']:.3f}")
    print(f"      Confidence: {result['confidence']:.1f}%")
    
    # Anomaly reading
    anomaly_reading = {
        'soil_moisture': 5.0,
        'temperature': 50.0,
        'humidity': 10.0,
        'ph': 3.5,
        'nitrogen': 90.0
    }
    
    result = detector.is_anomaly(anomaly_reading)
    print(f"\n   ⚠️ Anomaly Reading:")
    print(f"      Result: {'ANOMALY' if result['is_anomaly'] else 'NORMAL'}")
    print(f"      Severity: {result['severity']}")
    print(f"      Score: {result['anomaly_score']:.3f}")
    print(f"      Confidence: {result['confidence']:.1f}%")
    
    # Feature importance
    print("\n📊 Feature Importance:")
    importance = detector.get_feature_importance()
    for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"   {feature}: {score:.3f}")
    
    # Model info
    print("\n📊 Model Info:")
    info = detector.get_model_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*60)
    print("✅ Test complete!")
    print("="*60)


if __name__ == "__main__":
    test_detector()
