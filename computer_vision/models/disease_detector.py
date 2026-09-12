"""
CropMind - Disease Detector
TFLite model for plant disease detection from images

Author: CropMind Team
Date: 2026
"""

import os
import numpy as np
import tensorflow as tf
from typing import Dict, Any, Optional, Tuple

from computer_vision.utils.image_preprocessor import ImagePreprocessor


class DiseaseDetector:
    """
    Disease detection using TFLite model trained on PlantVillage dataset.
    Supports 23 disease classes across 5 crops.
    """
    
    # Treatment recommendations in Arabic for each disease class
    TREATMENTS = {
        "Tomato___Bacterial_spot": "استخدم مبيدات النحاس، تجنب الري العلوي، أزل الأوراق المصابة، واستخدم أصناف مقاومة",
        "Tomato___Early_blight": "استخدم مبيدات فطرية (مانكوزيب، كلوروثالونيل)، أزل الأوراق المصابة، وحسن التهوية",
        "Tomato___Late_blight": "استخدم مبيدات فطرية جهازية (ميتالاكسيل)، أزل النباتات المصابة، وتجنب الرطوبة العالية",
        "Tomato___Leaf_Mold": "حسن التهوية، قلل الرطوبة، استخدم مبيدات فطرية (كلوروثالونيل)، وأزل الأوراق المصابة",
        "Tomato___Septoria_leaf_spot": "استخدم مبيدات فطرية وقائية (مانكوزيب)، أزل الأوراق المصابة، وتجنب الري العلوي",
        "Tomato___Spider_mites Two-spotted_spider_mite": "استخدم مبيدات حشرية (أبامكتين)، زد الرطوبة حول النبات، وأزل الأوراق المصابة",
        "Tomato___Target_Spot": "استخدم مبيدات فطرية (أزوكسيستروبيون)، أزل الأوراق المصابة، وحسن التهوية",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "استخدم مبيدات حشرية للقضاء على الناقل (الذبابة البيضاء)، أزل النباتات المصابة، واستخدم شباك حماية",
        "Tomato___Tomato_mosaic_virus": "أزل النباتات المصابة، طهر الأدوات، استخدم أصناف مقاومة، وتجنب التعامل مع النباتات الرطبة",
        "Tomato___healthy": "المحصول بصحة جيدة، استمر في الرعاية الحالية وبرنامج المكافحة الوقائية",
        "Potato___Early_blight": "استخدم مبيدات فطرية وقائية (مانكوزيب)، أزل الأوراق المصابة، وحسن التهوية",
        "Potato___Late_blight": "استخدم مبيدات فطرية جهازية (ميتالاكسيل-مانكوزيب)، أزل النباتات المصابة، وتجنب الرطوبة العالية",
        "Potato___healthy": "المحصول بصحة جيدة، استمر في برنامج المكافحة الوقائية والري المنتظم",
        "Pepper,_bell___Bacterial_spot": "استخدم مبيدات النحاس، تجنب الري العلوي، أزل الأوراق المصابة، واستخدم أصناف مقاومة",
        "Pepper,_bell___healthy": "المحصول بصحة جيدة، استمر في الرعاية الوقائية والمكافحة المتكاملة",
        "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "استخدم مبيدات فطرية (أزوكسيستروبيون)، أزل الأوراق المصابة، وزد التهوية بين النباتات",
        "Corn_(maize)___Common_rust_": "استخدم مبيدات فطرية (بروبيكونازول)، ازرع أصناف مقاومة، وحسن التهوية",
        "Corn_(maize)___Northern_Leaf_Blight": "استخدم مبيدات فطرية وقائية، ازرع أصناف مقاومة، وأزل بقايا المحاصيل",
        "Corn_(maize)___healthy": "المحصول بصحة جيدة، استمر في برنامج المكافحة الوقائية والتسميد المنتظم",
        "Grape___Black_rot": "استخدم مبيدات فطرية (مانكوزيب، مايكلوبوتانيل)، أزل الأجزاء المصابة، وحسن التهوية",
        "Grape___Esca_(Black_Measles)": "لا يوجد علاج فعال، أزل الكروم المصابة، طهر أدوات التقليم، وازرع أصناف مقاومة",
        "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "استخدم مبيدات فطرية (بوردو، كلوروثالونيل)، أزل الأوراق المصابة، وحسن التهوية",
        "Grape___healthy": "المحصول بصحة جيدة، استمر في برنامج المكافحة الوقائية والتقليم المنتظم",
    }
    
    # Crop mapping
    CROP_MAPPING = {
        "Tomato": "طماطم",
        "Potato": "بطاطس",
        "Pepper,_bell": "فلفل",
        "Corn_(maize)": "ذرة",
        "Grape": "عنب"
    }
    
    def __init__(
        self,
        model_path: str = "computer_vision/models/model_unquant.tflite",
        labels_path: str = "computer_vision/models/labels.txt"
    ):
        """
        Initialize the DiseaseDetector with TFLite model and labels.
        
        Args:
            model_path: Path to the TFLite model file
            labels_path: Path to the labels file
        """
        self.model_path = model_path
        self.labels_path = labels_path
        self.input_size = 224
        self.is_loaded = False
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.labels = []
        
        self._load_model()
        self._load_labels()
        
        if self.is_loaded:
            print("[DiseaseDetector] ✅ Model loaded successfully")
        else:
            print("[DiseaseDetector] ⚠️ Model not loaded. Running in fallback mode.")
    
    def _load_model(self) -> None:
        """Load TFLite model from disk."""
        try:
            if not os.path.exists(self.model_path):
                print(f"[DiseaseDetector] ⚠️ Model file not found: {self.model_path}")
                return
            
            self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            self.is_loaded = True
            print(f"[DiseaseDetector] ✅ Model loaded from {self.model_path}")
            
        except Exception as e:
            print(f"[DiseaseDetector] ❌ Error loading model: {e}")
            self.is_loaded = False
    
    def _load_labels(self) -> None:
        """Load labels from labels.txt file."""
        try:
            if not os.path.exists(self.labels_path):
                print(f"[DiseaseDetector] ⚠️ Labels file not found: {self.labels_path}")
                return
            
            with open(self.labels_path, 'r', encoding='utf-8') as f:
                self.labels = [line.strip() for line in f.readlines() if line.strip()]
            
            print(f"[DiseaseDetector] ✅ Loaded {len(self.labels)} labels")
            
        except Exception as e:
            print(f"[DiseaseDetector] ❌ Error loading labels: {e}")
            self.labels = []
    
    def predict(self, image_path: str) -> Dict[str, Any]:
        """
        Predict disease from image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict with prediction results
        """
        if not self.is_loaded or self.interpreter is None:
            print("[DiseaseDetector] ⚠️ Model not loaded, using fallback")
            return self._fallback_prediction()
        
        try:
            # Preprocess image
            preprocessor = ImagePreprocessor()
            preprocessed_image = preprocessor.process(image_path, self.input_size)
            
            if preprocessed_image is None:
                print("[DiseaseDetector] ⚠️ Image preprocessing failed")
                return self._fallback_prediction()
            
            # Prepare input for inference
            input_tensor = np.expand_dims(preprocessed_image, axis=0).astype(np.float32)
            
            # Run inference
            self.interpreter.set_tensor(self.input_details[0]['index'], input_tensor)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            # Get prediction
            confidence_scores = output[0]
            predicted_index = np.argmax(confidence_scores)
            confidence = float(np.max(confidence_scores) * 100)
            
            # Get label
            if predicted_index < len(self.labels):
                raw_label = self.labels[predicted_index]
                disease_name = self._format_disease_name(raw_label)
                crop = self._extract_crop(raw_label)
                is_healthy = "healthy" in raw_label.lower()
            else:
                raw_label = "unknown"
                disease_name = "Unknown"
                crop = "Unknown"
                is_healthy = False
            
            # Determine severity
            severity = self._determine_severity(raw_label, confidence)
            
            # Get treatment
            treatment = self.TREATMENTS.get(raw_label, "يوصى باستشارة خبير زراعي")
            
            return {
                "disease_name": disease_name,
                "raw_label": raw_label,
                "crop": crop,
                "confidence": round(confidence, 2),
                "severity": severity,
                "treatment": treatment,
                "is_healthy": is_healthy
            }
            
        except Exception as e:
            print(f"[DiseaseDetector] ❌ Prediction error: {e}")
            return self._fallback_prediction()
    
    def _format_disease_name(self, raw_label: str) -> str:
        """
        Format disease name for display.
        """
        # Remove crop prefix and clean up
        parts = raw_label.split("___")
        if len(parts) > 1:
            disease_part = parts[1]
            # Clean up special characters
            disease_part = disease_part.replace("_", " ")
            disease_part = disease_part.replace("(", "")
            disease_part = disease_part.replace(")", "")
            # Capitalize properly
            return disease_part.title()
        return raw_label.replace("_", " ").title()
    
    def _extract_crop(self, raw_label: str) -> str:
        """
        Extract crop name from label.
        """
        parts = raw_label.split("___")
        if len(parts) > 0:
            crop_key = parts[0]
            return self.CROP_MAPPING.get(crop_key, crop_key)
        return "Unknown"
    
    def _determine_severity(self, raw_label: str, confidence: float) -> str:
        """
        Determine severity based on label and confidence.
        """
        if "healthy" in raw_label.lower():
            return "Healthy"
        elif confidence < 60:
            return "Low"
        elif confidence < 80:
            return "Medium"
        else:
            return "High"
    
    def _fallback_prediction(self) -> Dict[str, Any]:
        """
        Fallback prediction when model is not available.
        """
        return {
            "disease_name": "Unknown",
            "raw_label": "unknown",
            "crop": "Unknown",
            "confidence": 0.0,
            "severity": "Unknown",
            "treatment": "تعذر تحليل الصورة، يرجى المحاولة مرة أخرى",
            "is_healthy": False,
            "note": "Model not loaded"
        }
