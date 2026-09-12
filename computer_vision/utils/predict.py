"""
CropMind - Disease Prediction Wrapper
Simple wrapper for disease detection using the DiseaseDetector

Author: CropMind Team
Date: 2026
"""

import os
import tempfile
import numpy as np
from PIL import Image
from typing import Dict, Union, Optional

from computer_vision.models.disease_detector import DiseaseDetector
from computer_vision.utils.image_preprocessor import ImagePreprocessor


# Initialize detector (lazy loading)
_detector = None
_preprocessor = None


def _get_detector() -> DiseaseDetector:
    """Get or initialize the DiseaseDetector singleton."""
    global _detector
    if _detector is None:
        _detector = DiseaseDetector()
    return _detector


def _get_preprocessor() -> ImagePreprocessor:
    """Get or initialize the ImagePreprocessor singleton."""
    global _preprocessor
    if _preprocessor is None:
        _preprocessor = ImagePreprocessor()
    return _preprocessor


def predict_disease(
    image_input: Union[str, bytes]
) -> Dict[str, Union[bool, str, float, Optional[str]]]:
    """
    Predict disease from an image file path or bytes.
    
    Args:
        image_input: Either a file path (str) or image bytes
        
    Returns:
        Dict with prediction results:
            - success: bool
            - disease_name: str
            - crop: str
            - confidence: float
            - severity: str
            - treatment: str
            - is_healthy: bool
            - plant_not_recognized: bool (True if confidence < 70%)
            - error: Optional[str]
    """
    detector = _get_detector()
    preprocessor = _get_preprocessor()
    
    # Validate detector
    if not detector.is_loaded:
        return {
            "success": False,
            "disease_name": "Unknown",
            "crop": "Unknown",
            "confidence": 0.0,
            "severity": "Unknown",
            "treatment": "Model not loaded. Please try again later.",
            "is_healthy": False,
            "plant_not_recognized": False,
            "error": "Disease detection model is not loaded"
        }
    
    try:
        # Handle different input types
        if isinstance(image_input, bytes):
            # Image bytes from API
            processed = preprocessor.load_from_bytes(image_input)
            if processed is None:
                return {
                    "success": False,
                    "disease_name": "Unknown",
                    "crop": "Unknown",
                    "confidence": 0.0,
                    "severity": "Unknown",
                    "treatment": "Unable to process image bytes",
                    "is_healthy": False,
                    "plant_not_recognized": False,
                    "error": "Failed to preprocess image bytes"
                }
            
            # Save processed image to temporary file for detector
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                # Convert normalized array back to image
                image_array = (processed * 255).astype(np.uint8)
                img = Image.fromarray(image_array)
                img.save(tmp_file.name)
                temp_path = tmp_file.name
            
            try:
                result = detector.predict(temp_path)
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        else:
            # Image path
            result = detector.predict(str(image_input))
        
        # Check if prediction was successful
        if result.get("disease_name") == "Unknown" and result.get("confidence", 0) == 0:
            return {
                "success": False,
                "disease_name": "Unknown",
                "crop": "Unknown",
                "confidence": 0.0,
                "severity": "Unknown",
                "treatment": "Prediction failed",
                "is_healthy": False,
                "plant_not_recognized": False,
                "error": "Failed to get prediction from model"
            }
        
        # Extract results
        disease_name = result.get("disease_name", "Unknown")
        crop = result.get("crop", "Unknown")
        confidence = result.get("confidence", 0.0)
        severity = result.get("severity", "Unknown")
        treatment = result.get("treatment", "يوصى باستشارة خبير زراعي")
        is_healthy = result.get("is_healthy", False)
        
        # Override severity if healthy
        if is_healthy:
            severity = "Healthy"
        
        # Check if confidence is too low
        plant_not_recognized = confidence < 70.0 and not is_healthy
        
        return {
            "success": True,
            "disease_name": disease_name,
            "crop": crop,
            "confidence": round(confidence, 2),
            "severity": severity,
            "treatment": treatment,
            "is_healthy": is_healthy,
            "plant_not_recognized": plant_not_recognized,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "disease_name": "Unknown",
            "crop": "Unknown",
            "confidence": 0.0,
            "severity": "Unknown",
            "treatment": "An error occurred during prediction",
            "is_healthy": False,
            "plant_not_recognized": False,
            "error": str(e)
        }
