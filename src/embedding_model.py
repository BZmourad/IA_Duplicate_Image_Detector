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
    
    def __init__(self, model_name: str = "facebook/dinov2-small", use_gpu: bool = True):
        self.model_name = model_name
        self.device = self._get_device(use_gpu)
        self.model = None
        self.processor = None
        self.model_type = None  # 'transformers' or 'torchhub' or 'fallback' or 'simple'
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
        if self.model is not None or self.model_type == 'simple':
            return
        
        logger.info(f"Loading model {self.model_name}")
        
        # Try loading from torch hub first (more reliable for DINOv2)
        try:
            torch_hub_model = self._get_torch_hub_model_name()
            
            if torch_hub_model:
                logger.info(f"Loading from torch hub: {torch_hub_model}")
                
                # Set torch hub directory
                torch.hub.set_dir(os.path.expanduser("~/.cache/torch/hub"))
                
                self.model = torch.hub.load('facebookresearch/dinov2', torch_hub_model)
                self.model.to(self.device)
                self.model.eval()
                self.model_type = 'torchhub'
                self.embedding_dim = 384  # DINOv2 small has 384 dimensions
                logger.info(f"Model loaded from torch hub on {self.device}")
                return
        except Exception as e:
            logger.warning(f"Could not load from torch hub: {e}")
            logger.debug(traceback.format_exc())
        
        # Try loading from transformers
        try:
            from transformers import AutoImageProcessor, AutoModel
            self.processor = AutoImageProcessor.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            self.model_type = 'transformers'
            self.embedding_dim = 384
            logger.info(f"Model loaded from transformers on {self.device}")
            return
        except Exception as e:
            logger.warning(f"Could not load from transformers: {e}")
        
        # Fallback to simple CNN (using only torch, no torchvision)
        logger.warning("DINOv2 loading failed. Using simple CNN fallback.")
        self._create_simple_fallback_model()
    
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
            "dinov2_vitb14": "dinov2_vitb14"
        }
        
        return mapping.get(self.model_name, "dinov2_vits14")
    
    def _create_simple_fallback_model(self):
        """Create a simple CNN fallback model using only torch (no torchvision)."""
        try:
            # Simple CNN using only torch
            class SimpleCNN(nn.Module):
                def __init__(self, embedding_dim=512):
                    super(SimpleCNN, self).__init__()
                    self.features = nn.Sequential(
                        nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3),
                        nn.ReLU(inplace=True),
                        nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
                        nn.Conv2d(64, 128, kernel_size=3, padding=1),
                        nn.ReLU(inplace=True),
                        nn.MaxPool2d(kernel_size=2, stride=2),
                        nn.Conv2d(128, 256, kernel_size=3, padding=1),
                        nn.ReLU(inplace=True),
                        nn.Conv2d(256, 256, kernel_size=3, padding=1),
                        nn.ReLU(inplace=True),
                        nn.MaxPool2d(kernel_size=2, stride=2),
                        nn.Conv2d(256, 512, kernel_size=3, padding=1),
                        nn.ReLU(inplace=True),
                        nn.AdaptiveAvgPool2d((1, 1))
                    )
                    self.embedding_dim = embedding_dim
                
                def forward(self, x):
                    x = self.features(x)
                    x = x.view(x.size(0), -1)
                    return x
            
            self.model = SimpleCNN()
            self.model.to(self.device)
            self.model.eval()
            self.model_type = 'fallback'
            self.embedding_dim = 512
            logger.info("Using simple CNN fallback model (torch only)")
        except Exception as e:
            logger.error(f"Error creating fallback model: {e}")
            # Even simpler fallback - just use color histograms
            self.model = None
            self.model_type = 'simple'
            self.embedding_dim = 102  # 32*3 histogram bins + 3 mean + 3 std
            logger.info("Using simple color histogram as embedding")
    
    def generate_embeddings(self, images: np.ndarray, batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for a batch of images."""
        if self.model is None and self.model_type not in ['simple', 'fallback']:
            self.load_model()
        
        embeddings_list = []
        
        with torch.no_grad():
            for i in range(0, len(images), batch_size):
                batch = images[i:i + batch_size]
                
                if self.model_type == 'torchhub':
                    embedding = self._generate_torchhub_embedding(batch)
                elif self.model_type == 'transformers':
                    embedding = self._generate_transformers_embedding(batch)
                elif self.model_type == 'fallback':
                    embedding = self._generate_fallback_embedding(batch)
                else:  # simple
                    embedding = self._generate_simple_embedding(batch)
                
                embeddings_list.append(embedding)
        
        return np.vstack(embeddings_list)
    
    def generate_single_embedding(self, image: np.ndarray) -> np.ndarray:
        """Generate embedding for a single image."""
        # Add batch dimension
        image_batch = np.expand_dims(image, axis=0)
        
        # Generate embedding
        embeddings = self.generate_embeddings(image_batch, batch_size=1)
        
        # Return single embedding
        return embeddings[0]
    
    def _generate_torchhub_embedding(self, batch: np.ndarray) -> np.ndarray:
        """Generate embeddings using torch hub model."""
        batch_tensor = torch.from_numpy(batch).permute(0, 3, 1, 2).to(self.device)
        
        with torch.no_grad():
            if hasattr(self.model, 'forward_features'):
                outputs = self.model.forward_features(batch_tensor)
                
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
    
    def _generate_transformers_embedding(self, batch: np.ndarray) -> np.ndarray:
        """Generate embeddings using transformers model."""
        batch_tensor = torch.from_numpy(batch).permute(0, 3, 1, 2).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(batch_tensor)
            embeddings = outputs.last_hidden_state.mean(dim=1)
        
        return embeddings.cpu().numpy()
    
    def _generate_fallback_embedding(self, batch: np.ndarray) -> np.ndarray:
        """Generate embeddings using fallback CNN model."""
        batch_tensor = torch.from_numpy(batch).permute(0, 3, 1, 2).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(batch_tensor)
        
        return outputs.cpu().numpy()
    
    def _generate_simple_embedding(self, batch: np.ndarray) -> np.ndarray:
        """Generate simple embeddings using color histograms."""
        batch_size = batch.shape[0]
        features = []
        
        for i in range(batch_size):
            img = batch[i]
            
            # Calculate color histograms for each channel
            hist_features = []
            for channel in range(3):
                hist, _ = np.histogram(img[:, :, channel], bins=32, range=(0, 1))
                hist_features.extend(hist)
            
            # Add basic statistics
            mean_colors = img.mean(axis=(0, 1))
            std_colors = img.std(axis=(0, 1))
            
            features.append(np.concatenate([hist_features, mean_colors, std_colors]))
        
        return np.array(features, dtype=np.float32)
    
    def get_device_name(self) -> str:
        """Get device name for display."""
        if self.device.type == "cuda":
            return f"NVIDIA GPU ({torch.cuda.get_device_name(0)})"
        elif self.device.type == "mps":
            return "Apple MPS"
        else:
            return "CPU"