"""
Perceptual hash functions for near-duplicate detection.
"""

import logging
import imagehash
from PIL import Image
from typing import Dict, List, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class PerceptualHashDetector:
    """Detects near-duplicates using perceptual hashes."""
    
    def __init__(self, phash_threshold: int = 6, dhash_threshold: int = 6, max_workers: int = 4):
        self.phash_threshold = phash_threshold
        self.dhash_threshold = dhash_threshold
        self.max_workers = max_workers
    
    def calculate_hashes(self, file_paths: List[str]) -> Dict[str, Dict[str, imagehash.ImageHash]]:
        """Calculate perceptual hashes for each file."""
        hash_map = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(self._calculate_single_hash, path): path 
                for path in file_paths
            }
            
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    hashes = future.result()
                    if hashes:
                        hash_map[path] = hashes
                except Exception as e:
                    logger.error(f"Error calculating perceptual hash for {path}: {e}")
        
        return hash_map
    
    def _calculate_single_hash(self, file_path: str) -> Dict[str, imagehash.ImageHash]:
        """Calculate perceptual hashes for a single image."""
        try:
            with Image.open(file_path) as img:
                phash = imagehash.phash(img)
                dhash = imagehash.dhash(img)
                return {"phash": phash, "dhash": dhash}
        except Exception as e:
            logger.error(f"Error opening {file_path}: {e}")
            return {}
    
    def find_similar_pairs(self, hash_map: Dict[str, Dict[str, imagehash.ImageHash]]) -> List[Tuple[str, str, float]]:
        """Find pairs of images with similar perceptual hashes."""
        similar_pairs = []
        file_paths = list(hash_map.keys())
        
        for i in range(len(file_paths)):
            for j in range(i + 1, len(file_paths)):
                path1, path2 = file_paths[i], file_paths[j]
                
                if path1 not in hash_map or path2 not in hash_map:
                    continue
                
                hashes1 = hash_map[path1]
                hashes2 = hash_map[path2]
                
                phash_distance = hashes1["phash"] - hashes2["phash"]
                dhash_distance = hashes1["dhash"] - hashes2["dhash"]
                
                # Calculate similarity score
                phash_similar = phash_distance <= self.phash_threshold
                dhash_similar = dhash_distance <= self.dhash_threshold
                
                if phash_similar or dhash_similar:
                    # Calculate combined similarity
                    max_phash_bits = 64  # For 64-bit hashes
                    max_dhash_bits = 64
                    
                    phash_similarity = 1 - (phash_distance / max_phash_bits)
                    dhash_similarity = 1 - (dhash_distance / max_dhash_bits)
                    
                    similarity = max(phash_similarity, dhash_similarity)
                    similar_pairs.append((path1, path2, similarity))
        
        return similar_pairs