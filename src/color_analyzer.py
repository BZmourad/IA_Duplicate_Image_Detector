"""
Color analysis module for comparing product colors.
"""

import logging
import cv2
import numpy as np
from typing import List, Tuple, Optional
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)


class ColorAnalyzer:
    """Analyzes and compares colors in images."""
    
    def __init__(self, histogram_bins: int = 32, dominant_colors: int = 5):
        self.histogram_bins = histogram_bins
        self.dominant_colors = dominant_colors
    
    def extract_color_features(self, image: np.ndarray) -> dict:
        """Extract color features from an image."""
        # Convert to HSV and LAB
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab_img = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Remove background (simple thresholding)
        mask = self._create_foreground_mask(image)
        
        # Calculate histograms
        hsv_hist = self._calculate_histogram(hsv_img, mask)
        lab_hist = self._calculate_histogram(lab_img, mask)
        
        # Extract dominant colors
        dominant_colors = self._extract_dominant_colors(image, mask)
        
        return {
            "hsv_hist": hsv_hist,
            "lab_hist": lab_hist,
            "dominant_colors": dominant_colors,
            "mask_ratio": mask.mean() if mask is not None else 0.5
        }
    
    def _create_foreground_mask(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Create a mask for the foreground (non-background) pixels."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Simple threshold to separate background
            _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
            
            # Also remove very dark backgrounds
            _, mask2 = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
            mask = cv2.bitwise_and(mask, mask2)
            
            # Apply morphological operations to clean up
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # If mask is mostly empty, use full image
            if mask.mean() < 0.05:
                return None
            
            return mask
        except Exception as e:
            logger.error(f"Error creating foreground mask: {e}")
            return None
    
    def _calculate_histogram(self, image: np.ndarray, mask: Optional[np.ndarray]) -> np.ndarray:
        """Calculate color histogram."""
        if mask is not None:
            # Use only foreground pixels
            hist = cv2.calcHist([image], [0, 1, 2], mask, 
                               [self.histogram_bins] * 3, [0, 256] * 3)
        else:
            hist = cv2.calcHist([image], [0, 1, 2], None, 
                               [self.histogram_bins] * 3, [0, 256] * 3)
        
        # Normalize histogram
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        return hist.flatten()
    
    def _extract_dominant_colors(self, image: np.ndarray, mask: Optional[np.ndarray]) -> np.ndarray:
        """Extract dominant colors using K-means clustering."""
        try:
            # Reshape image
            pixels = image.reshape(-1, 3)
            
            if mask is not None:
                mask_flat = mask.flatten()
                pixels = pixels[mask_flat > 0]
            
            if len(pixels) < self.dominant_colors:
                return pixels.mean(axis=0) if len(pixels) > 0 else np.zeros(3)
            
            # Apply K-means
            kmeans = KMeans(n_clusters=self.dominant_colors, n_init=10, random_state=42)
            kmeans.fit(pixels)
            
            # Sort by cluster size
            labels, counts = np.unique(kmeans.labels_, return_counts=True)
            sorted_indices = np.argsort(-counts)
            dominant_colors = kmeans.cluster_centers_[sorted_indices]
            
            return dominant_colors
        except Exception as e:
            logger.error(f"Error extracting dominant colors: {e}")
            return np.zeros((self.dominant_colors, 3))
    
    def compare_colors(self, features1: dict, features2: dict) -> float:
        """Compare color features and return similarity score [0, 1]."""
        # Compare histograms
        hsv_similarity = self._compare_histograms(features1["hsv_hist"], features2["hsv_hist"])
        lab_similarity = self._compare_histograms(features1["lab_hist"], features2["lab_hist"])
        
        # Compare dominant colors
        color_similarity = self._compare_dominant_colors(
            features1["dominant_colors"], features2["dominant_colors"]
        )
        
        # Combine scores
        combined_score = 0.4 * hsv_similarity + 0.3 * lab_similarity + 0.3 * color_similarity
        
        return float(np.clip(combined_score, 0, 1))
    
    def _compare_histograms(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """Compare two histograms using correlation."""
        try:
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            return float(max(0, correlation))
        except Exception as e:
            logger.error(f"Error comparing histograms: {e}")
            return 0.0
    
    def _compare_dominant_colors(self, colors1: np.ndarray, colors2: np.ndarray) -> float:
        """Compare dominant colors using LAB color distance."""
        try:
            # Convert to LAB for better color comparison
            lab1 = cv2.cvtColor(colors1.reshape(-1, 1, 3).astype(np.uint8), cv2.COLOR_BGR2LAB)
            lab2 = cv2.cvtColor(colors2.reshape(-1, 1, 3).astype(np.uint8), cv2.COLOR_BGR2LAB)
            
            # Calculate minimum distances between color sets
            min_distances = []
            for color1 in lab1.reshape(-1, 3):
                distances = np.linalg.norm(lab2.reshape(-1, 3) - color1, axis=1)
                min_distances.append(np.min(distances))
            
            # Convert distances to similarity (max LAB distance is ~255*sqrt(3))
            max_distance = 255 * np.sqrt(3)
            similarities = 1 - (np.array(min_distances) / max_distance)
            
            return float(np.mean(similarities))
        except Exception as e:
            logger.error(f"Error comparing dominant colors: {e}")
            return 0.0