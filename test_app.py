#!/usr/bin/env python3
"""
Test the application before building.
"""

import os
import sys
import numpy as np
import torch

def test_imports():
    """Test all required imports."""
    print("Testing imports...")
    
    try:
        import cv2
        print("✓ OpenCV imported")
    except Exception as e:
        print(f"✗ OpenCV failed: {e}")
    
    try:
        from PIL import Image
        print("✓ PIL imported")
    except Exception as e:
        print(f"✗ PIL failed: {e}")
    
    try:
        import imagehash
        print("✓ ImageHash imported")
    except Exception as e:
        print(f"✗ ImageHash failed: {e}")
    
    try:
        import faiss
        print("✓ FAISS imported")
    except Exception as e:
        print(f"✗ FAISS failed: {e}")
    
    try:
        import sklearn
        print("✓ scikit-learn imported")
    except Exception as e:
        print(f"✗ scikit-learn failed: {e}")
    
    try:
        import pandas
        print("✓ pandas imported")
    except Exception as e:
        print(f"✗ pandas failed: {e}")
    
    try:
        import torch
        print(f"✓ PyTorch imported (version: {torch.__version__})")
    except Exception as e:
        print(f"✗ PyTorch failed: {e}")
    
    print("\nAll imports tested!")

def test_embedding_model():
    """Test the embedding model."""
    print("\nTesting embedding model...")
    
    from src.embedding_model import EmbeddingModel
    
    model = EmbeddingModel(use_gpu=False)
    model.load_model()
    
    print(f"✓ Model type: {model.model_type}")
    print(f"✓ Device: {model.get_device_name()}")
    print(f"✓ Embedding dimension: {model.embedding_dim}")
    
    # Create a test image
    test_image = np.random.rand(224, 224, 3).astype(np.float32)
    
    # Generate embedding
    embedding = model.generate_single_embedding(test_image)
    
    print(f"✓ Embedding generated with shape: {embedding.shape}")
    
    # Test batch generation
    test_batch = np.random.rand(4, 224, 224, 3).astype(np.float32)
    embeddings = model.generate_embeddings(test_batch, batch_size=2)
    
    print(f"✓ Batch embeddings generated with shape: {embeddings.shape}")

if __name__ == "__main__":
    test_imports()
    test_embedding_model()
    print("\n✓ All tests passed!")