"""
CropMind - Farm Intelligence Agent
Analyzes farm health, detects anomalies, diseases, and predicts yield

Author: CropMind Team
Date: 2026
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from ai_engine.agents.base_agent import BaseAgent
from ml_models.model_registry import registry


class FarmIntelligenceAgent(BaseAgent):
    """
    Farm Intelligence Agent for comprehensive farm health analysis.
    Integrates disease detection, anomaly detection, and yield prediction.
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Initialize the Farm Intelligence Agent.
        
        Args:
            groq_api_key: Groq API key (reads from env if None)
        """
        super().__init__(
            agent_name="Farm Intelligence Agent",
            description="Analyzes crop health, field data, and weather to generate Farm Health Score",
            groq_api_key=groq_api_key
        )
        self.log("✅ Farm Intelligence Agent initialized")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive farm health analysis.
        
        Args:
            input_data: Dict containing:
                - farm_id: int
                - crop_type: str
                - sensor_data: dict with N, P, K, temperature, humidity, ph, rainfall
                - image_path: Optional[str] path to crop image
                
        Returns:
            Dict with farm health report and recommendations
        """
        try:
            farm_id = input_data.get("farm_id")
            crop_type = input_data.get("crop_type", "general")
            sensor_data = input_data.get("sensor_data", {})
            image_path = input_data.get("image_path")
            
            self.log(f"🔍 Analyzing farm {farm_id} - Crop: {crop_type}")
            
            # Step 1: Anomaly Detection
            anomaly_result = self._detect_anomalies(sensor_data)
            
            # Step 2: Disease Detection (if image provided)
            disease_result = None
            if image_path and os.path.exists(image_path):
                disease_result = self._detect_disease(image_path)
            
            # Step 3: Yield Prediction
            yield_prediction = self._predict_yield(crop_type, sensor_data)
            
            # Step 4: Calculate Farm Health Score
            health_score = self.get_farm_health_score(
                sensor_data=sensor_data,
                disease_result=disease_result,
                anomaly_result=anomaly_result
            )
            
            # Step 5: Generate Report
            farm_data = {
                "farm_id": farm_id,
                "crop_type": crop_type,
                "sensor_data": sensor_data,
                "anomaly_result": anomaly_result,
                "disease_result": disease_result,
                "yield_prediction": yield_prediction,
                "health_score": health_score
            }
            
            report = self.generate_health_report(farm_data)
            
            return self.format_response({
                "farm_id": farm_id,
                "health_score": health_score,
                "anomalies": anomaly_result,
                "disease_detection": disease_result,
                "yield_prediction": yield_prediction,
                "report": report,
                "recommendations": self._generate_recommendations(
                    anomaly_result, disease_result, health_score
                )
            })
            
        except Exception as e:
            self.log(f"❌ Error in farm analysis: {e}")
            return self.format_error(str(e))
    
    def _detect_anomalies(self, sensor_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Detect anomalies in sensor data.
        
        Args:
            sensor_data: Dict with N, P, K, temperature, humidity, ph, rainfall
            
        Returns:
            Dict with anomaly detection results
        """
        self.log("🔍 Detecting sensor anomalies...")
        
        try:
            # Prepare reading for anomaly detector
            reading = {
                "soil_moisture": sensor_data.get("soil_moisture", 45.0),
                "temperature": sensor_data.get("temperature", 25.0),
                "humidity": sensor_data.get("humidity", 60.0),
                "ph": sensor_data.get("ph", 6.8),
                "nitrogen": sensor_data.get("N", 45.0)
            }
            
            # Use anomaly detector from registry
            if registry.anomaly:
                result = registry.anomaly.is_anomaly(reading)
                return {
                    "is_anomaly": result.get("is_anomaly", False),
                    "severity": result.get("severity", "Normal"),
                    "confidence": result.get("confidence", 95.0),
                    "anomaly_score": result.get("anomaly_score", 0.0),
                    "details": result
                }
            else:
                # Fallback - simple rule-based detection
                return self._rule_based_anomaly(reading)
                
        except Exception as e:
            self.log(f"⚠️ Anomaly detection error: {e}")
            return {
                "is_anomaly": False,
                "severity": "Unknown",
                "confidence": 0,
                "error": str(e)
            }
    
    def _rule_based_anomaly(self, reading: Dict[str, float]) -> Dict[str, Any]:
        """
        Rule-based anomaly detection fallback.
        """
        anomalies = []
        
        # Check each parameter
        if reading.get("soil_moisture", 50) < 20:
            anomalies.append("soil_moisture_low")
        if reading.get("soil_moisture", 50) > 80:
            anomalies.append("soil_moisture_high")
        if reading.get("temperature", 25) < 10 or reading.get("temperature", 25) > 40:
            anomalies.append("temperature_extreme")
        if reading.get("ph", 6.8) < 5.0 or reading.get("ph", 6.8) > 8.0:
            anomalies.append("ph_extreme")
        if reading.get("humidity", 60) < 20 or reading.get("humidity", 60) > 90:
            anomalies.append("humidity_extreme")
        
        is_anomaly = len(anomalies) > 0
        severity = "High" if len(anomalies) > 2 else "Medium" if len(anomalies) > 0 else "Normal"
        
        return {
            "is_anomaly": is_anomaly,
            "severity": severity,
            "confidence": 80.0 if is_anomaly else 95.0,
            "anomaly_score": -0.5 if is_anomaly else 0.3,
            "detected_anomalies": anomalies,
            "method": "rule_based"
        }
    
    def _detect_disease(self, image_path: str) -> Dict[str, Any]:
        """
        Detect disease in crop image.
        
        Args:
            image_path: Path to the crop image
            
        Returns:
            Dict with disease detection results
        """
        self.log(f"🔬 Detecting disease in image: {image_path}")
        
        try:
            if registry.disease:
                result = registry.disease.predict(image_path)
                return {
                    "disease_detected": result.get("disease_name", "None"),
                    "confidence": result.get("confidence", 0.0),
                    "severity": result.get("severity", "Unknown"),
                    "recommendation": result.get("treatment", "No treatment needed")
                }
            else:
                return {
                    "disease_detected": "Unknown",
                    "confidence": 0.0,
                    "severity": "Unknown",
                    "recommendation": "Disease detection model not available"
                }
                
        except Exception as e:
            self.log(f"⚠️ Disease detection error: {e}")
            return {
                "disease_detected": "Error",
                "confidence": 0.0,
                "severity": "Unknown",
                "error": str(e)
            }
    
    def _predict_yield(self, crop_type: str, sensor_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict crop yield based on sensor data.
        
        Args:
            crop_type: Type of crop
            sensor_data: Dict with soil and environmental data
            
        Returns:
            Dict with yield prediction
        """
        self.log(f"📊 Predicting yield for {crop_type}")
        
        try:
            if registry.yield_model:
                # Prepare features for prediction
                # This assumes the model expects features in a specific order
                features = [
                    sensor_data.get("N", 0),
                    sensor_data.get("P", 0),
                    sensor_data.get("K", 0),
                    sensor_data.get("temperature", 25),
                    sensor_data.get("humidity", 60),
                    sensor_data.get("ph", 6.8),
                    sensor_data.get("rainfall", 500)
                ]
                
                # Reshape for prediction
                import numpy as np
                features_array = np.array(features).reshape(1, -1)
                
                prediction = registry.yield_model.predict(features_array)
                yield_value = float(prediction[0])
                
                return {
                    "crop": crop_type,
                    "predicted_yield": round(yield_value, 2),
                    "unit": "tons/feddan",
                    "confidence": "high",
                    "method": "ml_model"
                }
            else:
                # Fallback - simple rule-based estimation
                base_yield = {
                    "wheat": 3.5,
                    "rice": 4.0,
                    "maize": 3.0,
                    "tomato": 6.0,
                    "potato": 5.0,
                    "onion": 4.5,
                    "cotton": 2.0,
                    "sugarcane": 8.0
                }
                base = base_yield.get(crop_type.lower(), 3.0)
                
                # Adjust based on conditions
                adjustment = 1.0
                if sensor_data.get("soil_moisture", 50) < 30:
                    adjustment -= 0.2
                if sensor_data.get("soil_moisture", 50) > 70:
                    adjustment += 0.1
                if sensor_data.get("temperature", 25) > 35:
                    adjustment -= 0.3
                if sensor_data.get("ph", 6.8) < 5.5 or sensor_data.get("ph", 6.8) > 7.5:
                    adjustment -= 0.2
                
                yield_value = base * max(0.5, adjustment)
                
                return {
                    "crop": crop_type,
                    "predicted_yield": round(yield_value, 2),
                    "unit": "tons/feddan",
                    "confidence": "medium",
                    "method": "rule_based"
                }
                
        except Exception as e:
            self.log(f"⚠️ Yield prediction error: {e}")
            return {
                "crop": crop_type,
                "predicted_yield": 0.0,
                "unit": "tons/feddan",
                "confidence": "low",
                "error": str(e)
            }
    
    def get_farm_health_score(
        self,
        sensor_data: Dict[str, float],
        disease_result: Optional[Dict[str, Any]],
        anomaly_result: Dict[str, Any]
    ) -> float:
        """
        Calculate farm health score (0-100) based on all factors.
        
        Args:
            sensor_data: Dict with sensor readings
            disease_result: Disease detection results
            anomaly_result: Anomaly detection results
            
        Returns:
            float: Health score (0-100)
        """
        score = 80.0  # Start with baseline
        
        # Adjust based on soil metrics
        if sensor_data.get("soil_moisture", 50):
            if 25 <= sensor_data["soil_moisture"] <= 60:
                score += 5
            elif sensor_data["soil_moisture"] < 15 or sensor_data["soil_moisture"] > 70:
                score -= 10
        
        if sensor_data.get("ph", 6.8):
            if 5.5 <= sensor_data["ph"] <= 7.5:
                score += 5
            elif sensor_data["ph"] < 4.5 or sensor_data["ph"] > 8.5:
                score -= 10
        
        if sensor_data.get("temperature", 25):
            if 15 <= sensor_data["temperature"] <= 30:
                score += 5
            elif sensor_data["temperature"] > 40 or sensor_data["temperature"] < 5:
                score -= 10
        
        # Adjust based on anomalies
        if anomaly_result.get("is_anomaly", False):
            severity = anomaly_result.get("severity", "Medium")
            if severity == "High":
                score -= 25
            elif severity == "Medium":
                score -= 15
            else:
                score -= 5
        
        # Adjust based on disease
        if disease_result:
            confidence = disease_result.get("confidence", 0)
            if confidence > 80:
                score -= 20
            elif confidence > 50:
                score -= 10
            
            if disease_result.get("severity") == "High":
                score -= 15
        
        # Clamp score between 0 and 100
        return max(0, min(100, score))
    
    def generate_health_report(self, farm_data: Dict[str, Any]) -> str:
        """
        Generate a comprehensive health report in Arabic using LLM.
        
        Args:
            farm_data: Dict with all farm analysis data
            
        Returns:
            str: Generated report in Arabic
        """
        self.log("📝 Generating health report...")
        
        # Build prompt
        prompt = self._build_report_prompt(farm_data)
        
        # Get LLM response
        response = self.think(prompt)
        
        return response
    
    def _build_report_prompt(self, farm_data: Dict[str, Any]) -> str:
        """
        Build the prompt for health report generation.
        """
        health_score = farm_data.get("health_score", 0)
        crop_type = farm_data.get("crop_type", "غير معروف")
        anomalies = farm_data.get("anomaly_result", {})
        disease = farm_data.get("disease_result", {})
        yield_pred = farm_data.get("yield_prediction", {})
        
        prompt = f"""
أنت خبير زراعي ذكي في نظام CropMind. قم بإنشاء تقرير صحي مفصل باللغة العربية للفارم التالي:

المحصول: {crop_type}
درجة الصحة العامة: {health_score:.1f}/100

بيانات الحساسات:
- درجة الحرارة: {farm_data.get('sensor_data', {}).get('temperature', 'N/A')}°C
- الرطوبة: {farm_data.get('sensor_data', {}).get('humidity', 'N/A')}%
- رطوبة التربة: {farm_data.get('sensor_data', {}).get('soil_moisture', 'N/A')}%
- درجة الحموضة (pH): {farm_data.get('sensor_data', {}).get('ph', 'N/A')}
- النيتروجين: {farm_data.get('sensor_data', {}).get('N', 'N/A')} ppm

نتائج التحليل:
- الحالات الشاذة: {'موجودة' if anomalies.get('is_anomaly', False) else 'غير موجودة'}
- الأمراض: {disease.get('disease_detected', 'غير مكتشفة')}
- إنتاجية متوقعة: {yield_pred.get('predicted_yield', 'N/A')} طن/فدان

المطلوب:
1. تقييم الحالة الصحية العامة للفارم
2. تحديد المشاكل المحتملة
3. تقديم توصيات عملية للتحسين
4. خطة عمل مقترحة للأيام القادمة

اكتب التقرير بصيغة احترافية واضحة مع عناوين فرعية.
"""
        return prompt
    
    def _generate_recommendations(
        self,
        anomaly_result: Dict[str, Any],
        disease_result: Optional[Dict[str, Any]],
        health_score: float
    ) -> Dict[str, Any]:
        """
        Generate actionable recommendations based on analysis.
        
        Returns:
            Dict with categorized recommendations
        """
        recommendations = {
            "urgent": [],
            "short_term": [],
            "long_term": []
        }
        
        # Urgent recommendations
        if anomaly_result.get("is_anomaly", False):
            severity = anomaly_result.get("severity", "Medium")
            if severity == "High":
                recommendations["urgent"].append("⚡ عمل فوري: هناك حالة شاذة خطيرة في بيانات الحساسات")
            
            for anomaly in anomaly_result.get("detected_anomalies", []):
                if "soil_moisture" in anomaly:
                    recommendations["urgent"].append("💧 نظام الري يحتاج تعديل فوري")
                if "temperature" in anomaly:
                    recommendations["urgent"].append("🌡️ درجة الحرارة خارج النطاق الطبيعي")
                if "ph" in anomaly:
                    recommendations["urgent"].append("🧪 حموضة التربة تحتاج معالجة عاجلة")
        
        if disease_result and disease_result.get("confidence", 0) > 70:
            recommendations["urgent"].append(f"🦠 تم اكتشاف مرض: {disease_result.get('disease_detected', 'Unknown')}")
        
        # Short term recommendations
        if health_score < 70:
            recommendations["short_term"].append("📋 جدولة فحص شامل للفارم خلال 48 ساعة")
        
        if health_score < 50:
            recommendations["short_term"].append("🚨 استشارة خبير زراعي خلال 24 ساعة")
        
        # Long term recommendations
        if health_score > 80:
            recommendations["long_term"].append("✅ المحافظة على الممارسات الحالية، الفارم في حالة جيدة")
        else:
            recommendations["long_term"].append("📊 تطبيق نظام مراقبة يومي للتحسين المستمر")
        
        return recommendations
