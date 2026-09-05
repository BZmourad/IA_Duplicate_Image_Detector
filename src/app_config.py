"""
Application configuration from .env file.
"""

import os
import sys  # Ajout de l'import manquant
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AppConfig:
    """Application configuration."""
    
    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "IA Duplicate Image Detector")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.app_icon = os.getenv("APP_ICON", "assets/logo.png")
    
    def get_app_name(self) -> str:
        """Get application name."""
        return self.app_name
    
    def get_app_version(self) -> str:
        """Get application version."""
        return self.app_version
    
    def get_app_icon_path(self) -> str:
        """Get application icon path."""
        # Check if running as script or frozen exe
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            base_path = sys._MEIPASS
        else:
            # Running as script
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        icon_path = os.path.join(base_path, self.app_icon)
        
        # Fallback to looking in current directory
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.getcwd(), self.app_icon)
        
        # Fallback to looking in assets directory
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.getcwd(), 'assets', 'logo.png')
        
        return icon_path

# Singleton instance
app_config = AppConfig()