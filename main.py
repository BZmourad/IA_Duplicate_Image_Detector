#!/usr/bin/env python3
"""
Duplicate Product Image Detector - Main Entry Point
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.gui.main_window import MainWindow
from src.utils import setup_logging
from src.app_config import app_config
import logging

logger = logging.getLogger(__name__)

def main():
    """Application entry point."""
    try:
        # Setup logging
        setup_logging()
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName(app_config.get_app_name())
        app.setApplicationVersion(app_config.get_app_version())
        app.setOrganizationName("ImageDedup")
        
        # Set application icon
        try:
            icon_path = app_config.get_app_icon_path()
            if os.path.exists(icon_path):
                app.setWindowIcon(QIcon(icon_path))
                logger.info(f"Application icon loaded: {icon_path}")
            else:
                logger.warning(f"Icon not found: {icon_path}")
        except Exception as e:
            logger.warning(f"Could not load application icon: {e}")
        
        # Create and show main window
        window = MainWindow()
        
        # Set window icon
        try:
            icon_path = app_config.get_app_icon_path()
            if os.path.exists(icon_path):
                window.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            logger.warning(f"Could not set window icon: {e}")
        
        # Set window title with app name
        window.setWindowTitle(app_config.get_app_name())
        
        window.show()
        
        # Run application
        return app.exec()
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Show error dialog if possible
        try:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Error", f"Fatal error: {str(e)}")
        except:
            pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())