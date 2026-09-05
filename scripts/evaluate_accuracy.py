#!/usr/bin/env python3
"""
Accuracy evaluation script for the duplicate detector.
"""

import os
import sys
import numpy as np
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.image_loader import ImageLoader
from src.hashing import ExactDuplicateDetector
from src.perceptual_hash import PerceptualHashDetector
from src.embedding_model import EmbeddingModel
from src.color_analyzer import ColorAnalyzer
from src.similarity import SimilarityCalculator
from src.grouping import DuplicateGrouper
from src.utils import load_config, normalize_embedding

def evaluate_test_dataset(test_dir="test_dataset", config_path="config.yaml"):
    """Evaluate the detector on test dataset."""
    
    config = load_config(config_path)
    
    # Initialize components
    image_loader = ImageLoader()
    exact_detector = ExactDuplicateDetector()
    perceptual_detector = PerceptualHashDetector()
    embedding_model = EmbeddingModel(use_gpu=config["processing"]["use_gpu"])
    color_analyzer = ColorAnalyzer()
    similarity_calculator = SimilarityCalculator(top_k=config["embedding"]["top_k"])
    grouper = DuplicateGrouper()
    
    # Load model
    embedding_model.load_model()
    
    # Find all images
    file_paths = image_loader.find_images(test_dir)
    
    # Calculate exact hashes
    hash_map = exact_detector.calculate_hashes(file_paths)
    exact_duplicates = exact_detector.find_duplicates(hash_map)
    
    # Generate embeddings
    print("Generating embeddings...")
    images = []
    valid_paths = []
    
    for path in file_paths:
        img = image_loader.load_and_preprocess(path)
        if img is not None:
            images.append(img)
            valid_paths.append(path)
    
    images_array = np.array(images)
    embeddings = embedding_model.generate_embeddings(images_array, batch_size=32)
    embeddings = np.array([normalize_embedding(e) for e in embeddings])
    
    # Find similar pairs
    similar_pairs = similarity_calculator.find_similar_pairs(
        embeddings,
        valid_paths,
        config["embedding"]["similarity_threshold"]
    )
    
    # Verify with color analysis
    print("Verifying candidates with color analysis...")
    verified_pairs = []
    image_cache = {}
    
    for path1, path2, product_similarity in similar_pairs:
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
            
            confidence = (
                config["confidence"]["product_weight"] * product_similarity +
                config["confidence"]["color_weight"] * color_similarity
            )
            
            verified_pairs.append((path1, path2, product_similarity, color_similarity, confidence))
    
    # Create groups
    groups = grouper.create_groups(verified_pairs, valid_paths)
    
    # Evaluate results
    print("\n=== Evaluation Results ===")
    print(f"Total images: {len(valid_paths)}")
    print(f"Exact duplicate groups: {len(exact_duplicates)}")
    print(f"Duplicate groups: {len(groups['duplicates'])}")
    print(f"Review groups: {len(groups['review'])}")
    
    # For precision/recall, we need ground truth
    # This would require manual labeling or known test cases
    
    print("\nNote: For full precision/recall evaluation,")
    print("please provide ground truth labels for the test dataset.")
    
    return groups

if __name__ == "__main__":
    evaluate_test_dataset()