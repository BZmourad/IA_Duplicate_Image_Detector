"""
Embedding cache management.
"""

import logging
import os
import json
import numpy as np
from typing import List, Dict, Optional
from .utils import get_file_info

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Manages caching of embeddings."""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.embeddings_file = os.path.join(cache_dir, "embeddings.npy")
        self.metadata_file = os.path.join(cache_dir, "metadata.json")
        
        os.makedirs(cache_dir, exist_ok=True)
    
    def load_cache(self) -> Optional[Dict]:
        """Load cached embeddings and metadata."""
        try:
            if not os.path.exists(self.embeddings_file) or not os.path.exists(self.metadata_file):
                return None
            
            embeddings = np.load(self.embeddings_file)
            
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            return {
                "embeddings": embeddings,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return None
    
    def save_cache(self, embeddings: np.ndarray, metadata: List[Dict]):
        """Save embeddings and metadata to cache."""
        try:
            np.save(self.embeddings_file, embeddings)
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Cache saved: {len(metadata)} items")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def validate_cache(self, file_paths: List[str], metadata: List[Dict]) -> List[int]:
        """
        Validate cache against current files.
        Returns indices of files that need new embeddings.
        """
        current_info = {}
        for path in file_paths:
            info = get_file_info(path)
            if info:
                current_info[path] = info
        
        cached_info = {item["path"]: item for item in metadata}
        
        # Find files that need updating
        indices_to_update = []
        valid_indices = []
        
        for idx, path in enumerate(file_paths):
            if path not in cached_info:
                # New file
                indices_to_update.append(idx)
            elif path not in current_info:
                # File deleted
                indices_to_update.append(idx)
            else:
                # Check if file changed
                cached = cached_info[path]
                current = current_info[path]
                
                if (cached["size"] != current["size"] or 
                    cached["modified_time"] != current["modified_time"] or
                    cached["hash"] != current["hash"]):
                    # File changed
                    indices_to_update.append(idx)
                else:
                    valid_indices.append(idx)
        
        return valid_indices
    
    def clear_cache(self):
        """Clear all cached data."""
        try:
            if os.path.exists(self.embeddings_file):
                os.remove(self.embeddings_file)
            if os.path.exists(self.metadata_file):
                os.remove(self.metadata_file)
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")