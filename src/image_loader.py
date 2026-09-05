"""
Image loading and preprocessing utilities.
"""

import logging
import os
from typing import List, Optional, Tuple
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from .utils import get_supported_extensions

logger = logging.getLogger(__name__)


class ImageLoader:
    """Handles image loading and preprocessing."""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
        self.supported_extensions = get_supported_extensions()
    
    def find_images(self, folder_path: str) -> List[str]:
        """Find all supported image files in a folder."""
        image_files = []
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if self.is_supported_image(file):
                        image_files.append(os.path.join(root, file))
        except Exception as e:
            logger.error(f"Error scanning folder {folder_path}: {e}")
            
        return sorted(image_files)
    
    def is_supported_image(self, filename: str) -> bool:
        """Check if file is a supported image."""
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.supported_extensions
    
    def load_image(self, file_path: str) -> Optional[np.ndarray]:
        """Load image using OpenCV."""
        try:
            # Try OpenCV first
            img = cv2.imread(file_path)
            if img is not None:
                return img
            
            # Fallback to PIL
            pil_img = Image.open(file_path)
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            return img
        except Exception as e:
            logger.error(f"Error loading image {file_path}: {e}")
            return None
    
    def preprocess_for_embedding(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for embedding model."""
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize
        img_resized = cv2.resize(img_rgb, self.target_size, interpolation=cv2.INTER_AREA)
        
        # Normalize to [0, 1]
        img_normalized = img_resized.astype(np.float32) / 255.0
        
        return img_normalized
    
    def load_and_preprocess(self, file_path: str) -> Optional[np.ndarray]:
        """Load and preprocess image for embedding."""
        image = self.load_image(file_path)
        if image is not None:
            return self.preprocess_for_embedding(image)
        return None
    
    def load_thumbnail(self, file_path: str, size: Tuple[int, int] = (150, 150)) -> Optional[np.ndarray]:
        """Load image as thumbnail for display."""
        image = self.load_image(file_path)
        if image is not None:
            # Convert to RGB for Qt display
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img_rgb, size, interpolation=cv2.INTER_AREA)
            return img_resized
        return None