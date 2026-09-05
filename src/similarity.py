"""
Similarity calculation and candidate verification.
"""

import logging
import numpy as np
from typing import List, Tuple, Dict
import faiss
from .utils import normalize_embedding, cosine_similarity

logger = logging.getLogger(__name__)


class SimilarityCalculator:
    """Calculates similarities between images."""
    
    def __init__(self, top_k: int = 10):
        self.top_k = top_k
    
    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Build FAISS index for efficient similarity search."""
        # Normalize embeddings
        normalized = embeddings.copy()
        faiss.normalize_L2(normalized)
        
        # Create index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity for normalized vectors)
        
        # Add embeddings to index
        index.add(normalized)
        
        return index
    
    def find_similar_pairs(self, embeddings: np.ndarray, file_paths: List[str], 
                          similarity_threshold: float) -> List[Tuple[str, str, float]]:
        """Find similar image pairs using FAISS."""
        if len(embeddings) == 0:
            return []
        
        # Build FAISS index
        index = self.build_faiss_index(embeddings)
        
        # Search for nearest neighbors
        normalized = embeddings.copy()
        faiss.normalize_L2(normalized)
        
        k = min(self.top_k + 1, len(embeddings))  # +1 because self will be included
        distances, indices = index.search(normalized, k)
        
        similar_pairs = []
        seen_pairs = set()
        
        for i in range(len(indices)):
            for j_idx, idx in enumerate(indices[i]):
                if idx == i:  # Skip self
                    continue
                
                similarity = float(distances[i][j_idx])
                
                if similarity >= similarity_threshold:
                    # Create unique pair key
                    pair_key = tuple(sorted([i, idx]))
                    
                    if pair_key not in seen_pairs:
                        seen_pairs.add(pair_key)
                        similar_pairs.append((file_paths[i], file_paths[idx], similarity))
        
        return similar_pairs
    
    def calculate_product_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate product similarity using cosine similarity."""
        return cosine_similarity(emb1, emb2)