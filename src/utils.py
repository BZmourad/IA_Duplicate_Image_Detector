"""
Utility functions for the duplicate image detector.
"""

import os
import logging
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import List, Set, Optional
import yaml
import numpy as np


def setup_logging(log_dir: str = "logs"):
    """Setup logging configuration."""
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "application.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        logging.warning(f"Config file not found: {config_path}. Using defaults.")
        return get_default_config()
    except Exception as e:
        logging.error(f"Error loading config: {e}. Using defaults.")
        return get_default_config()


def get_default_config() -> dict:
    """Get default configuration."""
    return {
        "embedding": {
            "model_name": "facebook/dinov2-small",
            "similarity_threshold": 0.88,
            "top_k": 10,
            "batch_size": 32,
            "image_size": 224
        },
        "color": {
            "similarity_threshold": 0.85,
            "histogram_bins": 32,
            "dominant_colors": 5
        },
        "confidence": {
            "product_weight": 0.70,
            "color_weight": 0.30
        },
        "classification": {
            "duplicate_threshold": 0.90,
            "review_threshold": 0.70
        },
        "processing": {
            "max_workers": 4,
            "use_gpu": True,
            "cache_enabled": True
        },
        "perceptual": {
            "phash_threshold": 6,
            "dhash_threshold": 6
        }
    }


def get_supported_extensions() -> Set[str]:
    """Get supported image file extensions."""
    return {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'}


def calculate_sha256(file_path: str, chunk_size: int = 8192) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating hash for {file_path}: {e}")
        return ""


def format_time(seconds: float) -> str:
    """Format time in HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_file_info(file_path: str) -> dict:
    """Get file information for caching."""
    try:
        stat = os.stat(file_path)
        return {
            "path": file_path,
            "size": stat.st_size,
            "modified_time": stat.st_mtime,
            "hash": calculate_sha256(file_path)
        }
    except Exception as e:
        logging.error(f"Error getting file info for {file_path}: {e}")
        return {}


def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """Normalize embedding vector."""
    norm = np.linalg.norm(embedding)
    if norm > 0:
        return embedding / norm
    return embedding


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))