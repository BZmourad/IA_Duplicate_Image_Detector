"""
Cryptographic hash functions for exact duplicate detection.
"""

import logging
import hashlib
from typing import Dict, List, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import calculate_sha256

logger = logging.getLogger(__name__)


class ExactDuplicateDetector:
    """Detects exact duplicates using SHA-256 hashes."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
    
    def calculate_hashes(self, file_paths: List[str]) -> Dict[str, str]:
        """Calculate SHA-256 hash for each file."""
        hash_map = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(calculate_sha256, path): path 
                for path in file_paths
            }
            
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    hash_value = future.result()
                    if hash_value:
                        hash_map[path] = hash_value
                except Exception as e:
                    logger.error(f"Error hashing {path}: {e}")
        
        return hash_map
    
    def find_duplicates(self, hash_map: Dict[str, str]) -> List[List[str]]:
        """Group files by their hash."""
        hash_groups: Dict[str, List[str]] = {}
        
        for file_path, hash_value in hash_map.items():
            if hash_value not in hash_groups:
                hash_groups[hash_value] = []
            hash_groups[hash_value].append(file_path)
        
        # Filter to groups with more than one file
        duplicate_groups = [
            files for files in hash_groups.values() 
            if len(files) > 1
        ]
        
        return duplicate_groups