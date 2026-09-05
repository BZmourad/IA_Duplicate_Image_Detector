"""
Worker threads for background processing.
"""

import logging
from PySide6.QtCore import QThread, Signal
from typing import List, Dict
import numpy as np
import traceback

from ..image_loader import ImageLoader
from ..hashing import ExactDuplicateDetector
from ..perceptual_hash import PerceptualHashDetector
from ..embedding_model import EmbeddingModel
from ..color_analyzer import ColorAnalyzer
from ..similarity import SimilarityCalculator
from ..grouping import DuplicateGrouper
from ..cache import EmbeddingCache
from ..utils import load_config, normalize_embedding

logger = logging.getLogger(__name__)


class AnalysisWorker(QThread):
    """Worker thread for image analysis."""
    
    progress_updated = Signal(int, str)  # progress percentage, stage description
    analysis_complete = Signal(dict)  # results
    analysis_error = Signal(str)  # error message
    stage_updated = Signal(int, int)  # current stage, total stages
    
    def __init__(self, folder_path: str, config: dict):
        super().__init__()
        self.folder_path = folder_path
        self.config = config
        self.is_cancelled = False
    
    def run(self):
        """Main processing pipeline."""
        try:
            # Initialize components
            image_loader = ImageLoader()
            exact_detector = ExactDuplicateDetector()
            perceptual_detector = PerceptualHashDetector(
                phash_threshold=self.config["perceptual"]["phash_threshold"],
                dhash_threshold=self.config["perceptual"]["dhash_threshold"]
            )
            embedding_model = EmbeddingModel(
                model_name=self.config["embedding"]["model_name"],
                use_gpu=self.config["processing"]["use_gpu"]
            )
            color_analyzer = ColorAnalyzer(
                histogram_bins=self.config["color"]["histogram_bins"],
                dominant_colors=self.config["color"]["dominant_colors"]
            )
            similarity_calculator = SimilarityCalculator(
                top_k=self.config["embedding"]["top_k"]
            )
            grouper = DuplicateGrouper(
                duplicate_threshold=self.config["classification"]["duplicate_threshold"],
                review_threshold=self.config["classification"]["review_threshold"]
            )
            
            # Stage 1: Find images and calculate hashes
            self.stage_updated.emit(1, 5)
            self.progress_updated.emit(5, "Finding images...")
            
            file_paths = image_loader.find_images(self.folder_path)
            
            if not file_paths:
                self.analysis_error.emit("No supported images found in the selected folder.")
                return
            
            if self.is_cancelled:
                return
            
            # Calculate exact hashes
            self.progress_updated.emit(10, "Calculating file hashes...")
            hash_map = exact_detector.calculate_hashes(file_paths)
            exact_duplicates = exact_detector.find_duplicates(hash_map)
            
            if self.is_cancelled:
                return
            
            # Stage 2: Perceptual hashing
            self.stage_updated.emit(2, 5)
            self.progress_updated.emit(25, "Calculating perceptual hashes...")
            perceptual_hashes = perceptual_detector.calculate_hashes(file_paths)
            perceptual_pairs = perceptual_detector.find_similar_pairs(perceptual_hashes)
            
            if self.is_cancelled:
                return
            
            # Stage 3: Generate embeddings
            self.stage_updated.emit(3, 5)
            self.progress_updated.emit(35, "Loading embedding model...")
            embedding_model.load_model()
            
            self.progress_updated.emit(45, "Generating visual embeddings...")
            
            # Check cache
            cache = EmbeddingCache()
            embeddings = None
            metadata = None
            
            if self.config["processing"]["cache_enabled"]:
                cached_data = cache.load_cache()
                if cached_data:
                    valid_indices = cache.validate_cache(file_paths, cached_data["metadata"])
                    if len(valid_indices) == len(file_paths):
                        # All embeddings are cached
                        embeddings = cached_data["embeddings"]
                        metadata = cached_data["metadata"]
                        self.progress_updated.emit(55, "Using cached embeddings...")
            
            if embeddings is None:
                # Generate new embeddings
                images = []
                valid_paths = []
                
                for path in file_paths:
                    img = image_loader.load_and_preprocess(path)
                    if img is not None:
                        images.append(img)
                        valid_paths.append(path)
                    else:
                        logger.warning(f"Could not load image: {path}")
                
                if not images:
                    self.analysis_error.emit("Could not load any images.")
                    return
                
                # Generate embeddings in batches
                images_array = np.array(images)
                embeddings = embedding_model.generate_embeddings(
                    images_array, 
                    batch_size=self.config["embedding"]["batch_size"]
                )
                
                # Normalize embeddings
                embeddings = np.array([normalize_embedding(e) for e in embeddings])
                
                # Create metadata
                metadata = []
                for path in valid_paths:
                    from ..utils import get_file_info
                    info = get_file_info(path)
                    if info:
                        metadata.append(info)
                
                # Save to cache
                if self.config["processing"]["cache_enabled"]:
                    cache.save_cache(embeddings, metadata)
                
                file_paths = valid_paths
            
            if self.is_cancelled:
                return
            
            self.progress_updated.emit(70, "Finding similar images...")
            
            # Stage 4: Similarity search
            self.stage_updated.emit(4, 5)
            similar_pairs = similarity_calculator.find_similar_pairs(
                embeddings,
                file_paths,
                self.config["embedding"]["similarity_threshold"]
            )
            
            # Combine with perceptual pairs
            perceptual_pair_set = {(p1, p2) for p1, p2, _ in perceptual_pairs}
            
            self.progress_updated.emit(80, "Verifying candidates...")
            
            # Stage 5: Color verification and grouping
            self.stage_updated.emit(5, 5)
            
            # Verify candidates with color analysis
            verified_pairs = []
            image_cache = {}
            
            for path1, path2, product_similarity in similar_pairs:
                if self.is_cancelled:
                    return
                
                # Load images for color analysis
                if path1 not in image_cache:
                    img1 = image_loader.load_image(path1)
                    if img1 is not None:
                        image_cache[path1] = color_analyzer.extract_color_features(img1)
                
                if path2 not in image_cache:
                    img2 = image_loader.load_image(path2)
                    if img2 is not None:
                        image_cache[path2] = color_analyzer.extract_color_features(img2)
                
                if path1 in image_cache and path2 in image_cache:
                    color_similarity = color_analyzer.compare_colors(
                        image_cache[path1], 
                        image_cache[path2]
                    )
                    
                    # Calculate confidence
                    confidence = (
                        self.config["confidence"]["product_weight"] * product_similarity +
                        self.config["confidence"]["color_weight"] * color_similarity
                    )
                    
                    verified_pairs.append((path1, path2, product_similarity, color_similarity, confidence))
            
            self.progress_updated.emit(90, "Creating groups...")
            
            # Create groups
            groups = grouper.create_groups(verified_pairs, file_paths)
            
            # Prepare results
            results = {
                "total_images": len(file_paths),
                "exact_duplicates": sum(len(g) for g in exact_duplicates),
                "duplicate_groups": len(groups["duplicates"]),
                "review_groups": len(groups["review"]),
                "groups": groups,
                "device": embedding_model.get_device_name()
            }
            
            self.progress_updated.emit(100, "Analysis complete!")
            self.analysis_complete.emit(results)
            
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            logger.error(traceback.format_exc())
            self.analysis_error.emit(f"Error during analysis: {str(e)}")
    
    def cancel(self):
        """Cancel the analysis."""
        self.is_cancelled = True