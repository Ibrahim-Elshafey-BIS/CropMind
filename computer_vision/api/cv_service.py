"""
CropMind - Computer Vision Service
FastAPI router for disease detection and crop health analysis

Author: CropMind Team
Date: 2026
"""

from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from computer_vision.utils.predict import predict_disease, _get_detector
from computer_vision.models.crop_health_scorer import CropHealthScorer
from app.core.config import settings

router = APIRouter()
health_scorer = CropHealthScorer()

# Supported crops information
SUPPORTED_CROPS = [
    {"name": "Tomato", "arabic": "طماطم", "diseases": 10},
    {"name": "Potato", "arabic": "بطاطس", "diseases": 3},
    {"name": "Pepper", "arabic": "فلفل", "diseases": 2},
    {"name": "Corn", "arabic": "ذرة", "diseases": 4},
    {"name": "Grape", "arabic": "عنب", "diseases": 4},
]
TOTAL_CLASSES = 23


# ============================================
# POST /analyze - Analyze crop image
# ============================================

@router.post("/analyze")
async def analyze_crop_image(
    image: UploadFile = File(..., description="Crop image (jpg, jpeg, png)")
):
    """
    Analyze a crop image for disease detection.
    
    Args:
        image: Uploaded image file (jpg, jpeg, png)
        
    Returns:
        Dict with disease detection results and health score
    """
    # Validate file format
    allowed_formats = ["jpg", "jpeg", "png"]
    file_extension = image.filename.split(".")[-1].lower() if image.filename else ""
    
    if file_extension not in allowed_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {file_extension}. Supported: {', '.join(allowed_formats)}"
        )
    
    try:
        # Read image bytes
        image_bytes = await image.read()
        
        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty image file"
            )
        
        # Predict disease
        prediction = predict_disease(image_bytes)
        
        if not prediction.get("success", False):
            error_msg = prediction.get("error", "Unknown error occurred")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Disease detection failed: {error_msg}"
            )
        
        # Calculate health score
        health_result = health_scorer.calculate_health_score(prediction)
        
        # Build response
        response = {
            "success": True,
            "disease_name": prediction.get("disease_name", "Unknown"),
            "crop": prediction.get("crop", "Unknown"),
            "confidence": prediction.get("confidence", 0.0),
            "severity": prediction.get("severity", "Unknown"),
            "treatment": prediction.get("treatment", "يوصى باستشارة خبير زراعي"),
            "is_healthy": prediction.get("is_healthy", False),
            "plant_not_recognized": prediction.get("plant_not_recognized", False),
            "health_score": health_result.get("health_score", 0),
            "recommendation": health_result.get("recommendation", "يرجى مراجعة خبير زراعي")
        }
        
        # Add note if plant not recognized
        if response["plant_not_recognized"]:
            response["message"] = "⚠️ الصورة غير واضحة أو النبات غير مدعوم. الثقة أقل من 70%."
        
        return JSONResponse(content=response, status_code=status.HTTP_200_OK)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[CV Service] ❌ Error analyzing image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze image: {str(e)}"
        )


# ============================================
# GET /health - Check service health
# ============================================

@router.get("/health")
async def health_check():
    """
    Check if the computer vision service is ready.
    
    Returns:
        Dict with service status and model information
    """
    try:
        # Use singleton detector from predict.py
        detector = _get_detector()
        
        model_loaded = detector.is_loaded
        total_classes = len(detector.labels) if detector.labels else TOTAL_CLASSES
        
        return {
            "status": "ready" if model_loaded else "unavailable",
            "model_loaded": model_loaded,
            "supported_crops": SUPPORTED_CROPS,
            "total_classes": total_classes,
            "model_path": settings.CV_MODEL_PATH,
            "labels_path": settings.CV_LABELS_PATH
        }
        
    except Exception as e:
        print(f"[CV Service] ❌ Health check error: {e}")
        return {
            "status": "unavailable",
            "model_loaded": False,
            "supported_crops": SUPPORTED_CROPS,
            "total_classes": TOTAL_CLASSES,
            "error": str(e)
        }


# ============================================
# GET /supported-crops - Get supported crops
# ============================================

@router.get("/supported-crops")
async def get_supported_crops():
    """
    Get list of supported crops and their disease counts.
    
    Returns:
        Dict with supported crops and total classes
    """
    return {
        "crops": SUPPORTED_CROPS,
        "total_classes": TOTAL_CLASSES
    }
