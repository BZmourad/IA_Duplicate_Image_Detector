"""
Visual embedding model using DINOv2.
"""

import logging
import os
import numpy as np
import torch
import torch.nn as nn
from typing import List, Optional, Tuple
import traceback

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Generates visual embeddings using DINOv2."""
    
    def __init__(self, model_name: str = "dinov2_vits14", use_gpu: bool = True):
        self.model_name = model_name
        self.device = self._get_device(use_gpu)
        self.model = None
        self.processor = None
        self.model_type = None  # 'transformers' or 'torchhub'
        self.embedding_dim = None
        
    def _get_device(self, use_gpu: bool) -> torch.device:
        """Determine the device to use."""
        if use_gpu and torch.cuda.is_available():
            logger.info("Using CUDA GPU")
            return torch.device("cuda")
        elif use_gpu and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            logger.info("Using Apple MPS")
            return torch.device("mps")
        else:
            logger.info("Using CPU")
            return torch.device("cpu")
    
    def load_model(self):
        """Load the DINOv2 model."""
        if self.model is not None:
            return
        
        logger.info(f"Loading model {self.model_name}")
        
        # Try loading from torch hub first (more reliable for DINOv2)
        try:
            torch_hub_model = self._get_torch_hub_model_name()
            
            if torch_hub_model:
                logger.info(f"Loading from torch hub: {torch_hub_model}")
                self.model = torch.hub.load('facebookresearch/dinov2', torch_hub_model)
                self.model.to(self.device)
                self.model.eval()
                self.model_type = 'torchhub'
                logger.info(f"Model loaded from torch hub on {self.device}")
                return
        except Exception as e:
            logger.warning(f"Could not load from torch hub: {e}")
            logger.info("Attempting to load from transformers...")
        
        # Try loading from transformers
        try:
            from transformers import AutoImageProcessor, AutoModel
            self.processor = AutoImageProcessor.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            self.model_type = 'transformers'
            logger.info(f"Model loaded from transformers on {self.device}")
            return
        except Exception as e:
            logger.warning(f"Could not load from transformers: {e}")
        
        # Fallback to a simple CNN if DINOv2 fails
        logger.warning("DINOv2 loading failed. Using a simple CNN fallback.")
        self._create_fallback_model()
    
    def _get_torch_hub_model_name(self) -> str:
        """Map model names to torch hub names."""
        mapping = {
            "facebook/dinov2-small": "dinov2_vits14",
            "facebook/dinov2-base": "dinov2_vitb14",
            "facebook/dinov2-large": "dinov2_vitl14",
            "facebook/dinov2-giant": "dinov2_vitg14",
            "dinov2-small": "dinov2_vits14",
            "dinov2-base": "dinov2_vitb14",
            "dinov2_vits14": "dinov2_vits14",
            "dinov2_vitb14": "dinov2_vitb14",
            "dinov2_vitl14": "dinov2_vitl14",
            "dinov2_vitg14": "dinov2_vitg14"
        }
        
        return mapping.get(self.model_name, "dinov2_vits14")
    
    def _create_fallback_model(self):
        """Create a simple CNN fallback model."""
        import torchvision.models as models
        
        # Use ResNet18 as fallback
        self.model = models.resnet18(pretrained=True)
        # Remove the final classification layer
        self.model = nn.Sequential(*list(self.model.children())[:-1])
        self.model.to(self.device)
        self.model.eval()
        self.model_type = 'fallback'
        self.embedding_dim = 512
        logger.info("Using ResNet18 fallback model")
    
    def _extract_features_torchhub(self, batch_tensor: torch.Tensor) -> np.ndarray:
        """Extract features from torch hub DINOv2 model."""
        with torch.no_grad():
            # DINOv2 forward_features returns a dict with 'x_norm_patchtokens'
            if hasattr(self.model, 'forward_features'):
                outputs = self.model.forward_features(batch_tensor)
                
                # Handle different output formats
                if isinstance(outputs, dict):
                    # DINOv2 returns dict with 'x_norm_patchtokens'
                    if 'x_norm_patchtokens' in outputs:
                        features = outputs['x_norm_patchtokens']
                    elif 'x_prenorm' in outputs:
                        features = outputs['x_prenorm']
                    elif 'x_norm_clstoken' in outputs:
                        features = outputs['x_norm_clstoken']
                    else:
                        # Take the first tensor value
                        features = next(iter(outputs.values()))
                    
                    # Global average pooling over patch tokens
                    if len(features.shape) == 3:  # (batch, num_tokens, dim)
                        embeddings = features.mean(dim=1)
                    else:  # Already pooled or CLS token
                        embeddings = features
                else:
                    # If it returns a tensor directly
                    if len(outputs.shape) == 3:
                        embeddings = outputs.mean(dim=1)
                    else:
                        embeddings = outputs
            else:
                # Fallback to regular forward pass
                outputs = self.model(batch_tensor)
                if isinstance(outputs, dict):
                    outputs = next(iter(outputs.values()))
                if len(outputs.shape) == 3:
                    embeddings = outputs.mean(dim=1)
                else:
                    embeddings = outputs
        
        return embeddings.cpu().numpy()
    
    def generate_embeddings(self, images: np.ndarray, batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for a batch of images."""
        if self.model is None:
            self.load_model()
        
        embeddings_list = []
        
        with torch.no_grad():
            for i in range(0, len(images), batch_size):
                batch = images[i:i + batch_size]
                
                if self.model_type == 'torchhub':
                    # Convert to tensor
                    batch_tensor = torch.from_numpy(batch).permute(0, 3, 1, 2).to(self.device)
                    embedding = self._extract_features_torchhub(batch_tensor)
                elif self.model_type == 'transformers':
                    embedding = self._generate_transformers_embedding(batch)
                else:
                    embedding = self._generate_fallback_embedding(batch)
                
                embeddings_list.append(embedding)
        
        return np.vstack(embeddings_list)
    
    def _generate_transformers_embedding(self, batch: np.ndarray) -> np.ndarray:
        """Generate embeddings using transformers model."""
        # Convert to tensor
        batch_tensor = torch.from_numpy(batch).permute(0, 3, 1, 2).to(self.device)
        
        # Generate embeddings
        outputs = self.model(batch_tensor)
        embeddings = outputs.last_hidden_state.mean(dim=1)  # Global average pooling
        
        return embeddings.cpu().numpy()
    
    def _generate_fallback_embedding(self, batch: np.ndarray) -> np.ndarray:
        """Generate embeddings using fallback model."""
        # Convert to tensor
        batch_tensor = torch.from_numpy(batch).permute(0, 3, 1, 2).to(self.device)
        
        # Generate embeddings
        outputs = self.model(batch_tensor)
        embeddings = outputs.squeeze(-1).squeeze(-1)  # Remove spatial dimensions
        
        return embeddings.cpu().numpy()
    
    def generate_single_embedding(self, image: np.ndarray) -> np.ndarray:
        """Generate embedding for a single image."""
        if self.model is None:
            self.load_model()
        
        with torch.no_grad():
            # Add batch dimension
            image_batch = np.expand_dims(image, axis=0)
            
            if self.model_type == 'torchhub':
                image_tensor = torch.from_numpy(image_batch).permute(0, 3, 1, 2).to(self.device)
                embedding = self._extract_features_torchhub(image_tensor)
                return embedding[0]
            elif self.model_type == 'transformers':
                image_tensor = torch.from_numpy(image_batch).permute(0, 3, 1, 2).to(self.device)
                outputs = self.model(image_tensor)
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
                return embedding.cpu().numpy()
            else:
                image_tensor = torch.from_numpy(image_batch).permute(0, 3, 1, 2).to(self.device)
                outputs = self.model(image_tensor)
                embedding = outputs.squeeze()
                return embedding.cpu().numpy()
    
    def get_device_name(self) -> str:
        """Get device name for display."""
        if self.device.type == "cuda":
            return f"NVIDIA GPU ({torch.cuda.get_device_name(0)})"
        elif self.device.type == "mps":
            return "Apple MPS"
        else:
            return "CPU"