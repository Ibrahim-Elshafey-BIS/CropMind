"""
CropMind - Image Preprocessor
Utility for preprocessing images for disease detection

Author: CropMind Team
Date: 2026
"""

import os
import io
import numpy as np
from PIL import Image
from typing import Optional, Tuple, Dict, Any


class ImagePreprocessor:
    """
    Image preprocessing utility for disease detection model.
    Handles loading, resizing, normalization, and validation of images.
    """
    
    def __init__(self):
        """Initialize the ImagePreprocessor."""
        self.supported_formats = ['.jpg', '.jpeg', '.png']
        print("[ImagePreprocessor] ✅ Initialized")
    
    def process(self, image_path: str, input_size: int = 224) -> Optional[np.ndarray]:
        """
        Load and preprocess an image from file path.
        
        Args:
            image_path: Path to the image file
            input_size: Target size for the model input (default: 224)
            
        Returns:
            np.ndarray: Preprocessed image array (input_size, input_size, 3) with dtype float32
            None: If preprocessing fails
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                print(f"[ImagePreprocessor] ⚠️ File not found: {image_path}")
                return None
            
            # Check if file is empty
            if os.path.getsize(image_path) == 0:
                print(f"[ImagePreprocessor] ⚠️ File is empty: {image_path}")
                return None
            
            # Check file extension
            ext = os.path.splitext(image_path)[1].lower()
            if ext not in self.supported_formats:
                print(f"[ImagePreprocessor] ⚠️ Unsupported format: {ext}. Supported: {self.supported_formats}")
                return None
            
            # Load image with PIL
            image = Image.open(image_path)
            
            # Convert to RGB if not already
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize
            image = image.resize((input_size, input_size), Image.Resampling.LANCZOS)
            
            # Convert to numpy array
            image_array = np.array(image, dtype=np.float32)
            
            # Normalize to [0, 1]
            image_array = image_array / 255.0
            
            print(f"[ImagePreprocessor] ✅ Image processed: {image_path} -> {image_array.shape}")
            return image_array
            
        except FileNotFoundError:
            print(f"[ImagePreprocessor] ❌ File not found: {image_path}")
            return None
        except IOError as e:
            print(f"[ImagePreprocessor] ❌ IOError reading image: {e}")
            return None
        except Exception as e:
            print(f"[ImagePreprocessor] ❌ Error processing image: {e}")
            return None
    
    def load_from_bytes(self, image_bytes: bytes, input_size: int = 224) -> Optional[np.ndarray]:
        """
        Load and preprocess an image from bytes.
        
        Args:
            image_bytes: Image data as bytes
            input_size: Target size for the model input (default: 224)
            
        Returns:
            np.ndarray: Preprocessed image array (input_size, input_size, 3) with dtype float32
            None: If preprocessing fails
        """
        try:
            if not image_bytes:
                print("[ImagePreprocessor] ⚠️ No bytes provided")
                return None
            
            # Load image from bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if not already
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize
            image = image.resize((input_size, input_size), Image.Resampling.LANCZOS)
            
            # Convert to numpy array
            image_array = np.array(image, dtype=np.float32)
            
            # Normalize to [0, 1]
            image_array = image_array / 255.0
            
            print(f"[ImagePreprocessor] ✅ Image processed from bytes -> {image_array.shape}")
            return image_array
            
        except Exception as e:
            print(f"[ImagePreprocessor] ❌ Error processing image from bytes: {e}")
            return None
    
    def validate_image(self, image_path: str) -> Dict[str, Any]:
        """
        Validate an image file and return its metadata.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict with validation results
        """
        result = {
            "is_valid": False,
            "format": None,
            "size": None,
            "mode": None,
            "file_size_kb": 0.0,
            "error": None
        }
        
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                result["error"] = f"File not found: {image_path}"
                return result
            
            # Check if file is empty
            file_size = os.path.getsize(image_path)
            result["file_size_kb"] = round(file_size / 1024, 2)
            
            if file_size == 0:
                result["error"] = "File is empty"
                return result
            
            # Check file extension
            ext = os.path.splitext(image_path)[1].lower()
            if ext not in self.supported_formats:
                result["error"] = f"Unsupported format: {ext}. Supported: {self.supported_formats}"
                return result
            
            # Load image with PIL
            image = Image.open(image_path)
            
            result["format"] = image.format.lower() if image.format else ext[1:]
            result["size"] = image.size
            result["mode"] = image.mode
            result["is_valid"] = True
            
            print(f"[ImagePreprocessor] ✅ Image validated: {image_path} - {result}")
            return result
            
        except Exception as e:
            result["error"] = str(e)
            print(f"[ImagePreprocessor] ❌ Error validating image: {e}")
            return result
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Get detailed image information without full validation.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict with image info
        """
        try:
            if not os.path.exists(image_path):
                return {"error": "File not found"}
            
            image = Image.open(image_path)
            
            return {
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
                "format": image.format,
                "file_size_kb": round(os.path.getsize(image_path) / 1024, 2)
            }
            
        except Exception as e:
            return {"error": str(e)}
