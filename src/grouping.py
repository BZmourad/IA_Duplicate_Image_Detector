"""
Grouping and clustering of duplicate images.
"""

import logging
import numpy as np
from typing import List, Dict, Set, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class DuplicateGrouper:
    """Groups duplicate images based on pairwise similarities."""
    
    def __init__(self, duplicate_threshold: float = 0.90, review_threshold: float = 0.70):
        self.duplicate_threshold = duplicate_threshold
        self.review_threshold = review_threshold
    
    def create_groups(self, pairs: List[Tuple[str, str, float, float, float]], 
                     file_paths: List[str]) -> Dict[str, List[dict]]:
        """
        Create groups from pairwise similarities.
        
        Args:
            pairs: List of (path1, path2, product_similarity, color_similarity, confidence)
            file_paths: List of all file paths
        
        Returns:
            Dictionary with 'duplicates' and 'review' groups
        """
        # Separate pairs by confidence
        duplicate_pairs = []
        review_pairs = []
        
        for path1, path2, prod_sim, color_sim, confidence in pairs:
            pair_info = {
                "path1": path1,
                "path2": path2,
                "product_similarity": prod_sim,
                "color_similarity": color_sim,
                "confidence": confidence
            }
            
            if confidence >= self.duplicate_threshold:
                duplicate_pairs.append(pair_info)
            elif confidence >= self.review_threshold:
                review_pairs.append(pair_info)
        
        # Create groups
        duplicate_groups = self._create_groups_from_pairs(duplicate_pairs, "DUPLICATE")
        review_groups = self._create_groups_from_pairs(review_pairs, "MANUAL_REVIEW")
        
        return {
            "duplicates": duplicate_groups,
            "review": review_groups
        }
    
    def _create_groups_from_pairs(self, pairs: List[dict], status: str) -> List[dict]:
        """Create groups from pairs using connected components."""
        if not pairs:
            return []
        
        # Build adjacency list
        adjacency = defaultdict(set)
        pair_info_map = {}
        
        for pair in pairs:
            path1, path2 = pair["path1"], pair["path2"]
            adjacency[path1].add(path2)
            adjacency[path2].add(path1)
            
            pair_key = tuple(sorted([path1, path2]))
            pair_info_map[pair_key] = pair
        
        # Find connected components
        visited = set()
        groups = []
        
        for start_node in adjacency:
            if start_node in visited:
                continue
            
            # BFS to find all connected nodes
            component = set()
            stack = [start_node]
            
            while stack:
                node = stack.pop()
                if node not in visited:
                    visited.add(node)
                    component.add(node)
                    stack.extend(adjacency[node] - visited)
            
            if len(component) > 1:  # Only include groups with more than one image
                # Calculate group statistics
                group_pairs = []
                component_list = list(component)
                
                for i in range(len(component_list)):
                    for j in range(i + 1, len(component_list)):
                        pair_key = tuple(sorted([component_list[i], component_list[j]]))
                        if pair_key in pair_info_map:
                            group_pairs.append(pair_info_map[pair_key])
                
                if group_pairs:
                    avg_confidence = np.mean([p["confidence"] for p in group_pairs])
                    avg_product_sim = np.mean([p["product_similarity"] for p in group_pairs])
                    avg_color_sim = np.mean([p["color_similarity"] for p in group_pairs])
                    
                    groups.append({
                        "images": sorted(component_list),
                        "confidence": float(avg_confidence),
                        "product_similarity": float(avg_product_sim),
                        "color_similarity": float(avg_color_sim),
                        "status": status,
                        "num_images": len(component_list)
                    })
        
        # Sort groups by confidence (descending)
        groups.sort(key=lambda x: x["confidence"], reverse=True)
        
        return groups