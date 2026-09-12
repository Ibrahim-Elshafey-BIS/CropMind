"""
CropMind - Model Registry
Central entry point for all ML models in the CropMind system

Author: CropMind Team
Date: 2026
"""

import os
import warnings
import joblib
from typing import Optional, Dict, Any

warnings.filterwarnings('ignore')


class ModelRegistry:
    """
    Central registry for all ML models in CropMind.
    Lazy loading ensures models are only loaded when needed.
    """
    
    def __init__(self):
        self._demand = None
        self._price = None
        self._optimizer = None
        self._anomaly = None
        self._yield_model = None
        self._disease = None
        self._model_status = {}
    
    @property
    def demand(self):
        """DemandForecaster instance for crop demand forecasting."""
        if self._demand is None:
            try:
                from ml_models.demand_forecasting.prophet_model import DemandForecaster
                self._demand = DemandForecaster()
                self._model_status['demand'] = 'loaded'
            except Exception as e:
                self._model_status['demand'] = f'failed: {str(e)}'
                warnings.warn(f"⚠️ Failed to load DemandForecaster: {e}")
        return self._demand
    
    @property
    def price(self):
        """PriceForecaster instance for commodity price forecasting."""
        if self._price is None:
            try:
                from ml_models.price_forecasting.predict import PriceForecaster
                self._price = PriceForecaster()
                self._model_status['price'] = 'loaded'
            except Exception as e:
                self._model_status['price'] = f'failed: {str(e)}'
                warnings.warn(f"⚠️ Failed to load PriceForecaster: {e}")
        return self._price
    
    @property
    def optimizer(self):
        """ResourceOptimizer instance for crop and resource optimization."""
        if self._optimizer is None:
            try:
                from ml_models.resource_optimization.optimizer import ResourceOptimizer
                self._optimizer = ResourceOptimizer()
                self._model_status['optimizer'] = 'loaded'
            except Exception as e:
                self._model_status['optimizer'] = f'failed: {str(e)}'
                warnings.warn(f"⚠️ Failed to load ResourceOptimizer: {e}")
        return self._optimizer
    
    @property
    def anomaly(self):
        """AnomalyDetector instance for sensor data anomaly detection."""
        if self._anomaly is None:
            try:
                from ml_models.anomaly_detection.isolation_forest import SensorAnomalyDetector
                self._anomaly = SensorAnomalyDetector()
                # Load the trained model
                model_path = "ml_models/anomaly_detection/models/anomaly_detector.pkl"
                if os.path.exists(model_path):
                    self._anomaly.load(model_path)
                    self._model_status['anomaly'] = 'loaded'
                else:
                    self._model_status['anomaly'] = 'model_file_not_found'
                    warnings.warn(f"⚠️ Anomaly detection model not found at {model_path}")
            except Exception as e:
                self._model_status['anomaly'] = f'failed: {str(e)}'
                warnings.warn(f"⚠️ Failed to load AnomalyDetector: {e}")
        return self._anomaly
    
    @property
    def yield_model(self):
        """Yield prediction model loaded from joblib."""
        if self._yield_model is None:
            try:
                model_path = "ml_models/yield_prediction/yield_model.pkl"
                if os.path.exists(model_path):
                    self._yield_model = joblib.load(model_path)
                    self._model_status['yield'] = 'loaded'
                else:
                    self._model_status['yield'] = 'model_file_not_found'
                    warnings.warn(f"⚠️ Yield model not found at {model_path}")
            except Exception as e:
                self._model_status['yield'] = f'failed: {str(e)}'
                warnings.warn(f"⚠️ Failed to load yield model: {e}")
        return self._yield_model
    
    @property
    def disease(self):
        """DiseaseDetector instance for plant disease detection."""
        if self._disease is None:
            try:
                from computer_vision.models.disease_detector import DiseaseDetector
                self._disease = DiseaseDetector()
                self._model_status['disease'] = 'loaded'
            except Exception as e:
                self._model_status['disease'] = f'failed: {str(e)}'
                warnings.warn(f"⚠️ Failed to load DiseaseDetector: {e}")
        return self._disease
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check health status of all registered models.
        
        Returns:
            Dict with status of each model
        """
        # Trigger loading of all models if not already loaded
        # Access each property to trigger lazy loading
        _ = self.demand
        _ = self.price
        _ = self.optimizer
        _ = self.anomaly
        _ = self.yield_model
        _ = self.disease
        
        # Count loaded models
        loaded = sum(1 for status in self._model_status.values() if status == 'loaded')
        total = len(self._model_status)
        
        return {
            "status": "healthy" if loaded == total and total > 0 else "degraded",
            "loaded_models": loaded,
            "total_models": total,
            "models": self._model_status,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
    
    def reload_model(self, model_name: str) -> bool:
        """
        Reload a specific model by name.
        
        Args:
            model_name: Name of the model to reload (demand, price, optimizer, anomaly, yield, disease)
            
        Returns:
            bool: True if reloaded successfully
        """
        model_map = {
            'demand': '_demand',
            'price': '_price',
            'optimizer': '_optimizer',
            'anomaly': '_anomaly',
            'yield': '_yield_model',
            'disease': '_disease'
        }
        
        if model_name not in model_map:
            return False
        
        # Reset the model
        setattr(self, model_map[model_name], None)
        if model_name in self._model_status:
            del self._model_status[model_name]
        
        # Trigger reload by accessing property
        try:
            getattr(self, model_name)
            return self._model_status.get(model_name) == 'loaded'
        except Exception:
            return False


# Singleton instance
registry = ModelRegistry()
