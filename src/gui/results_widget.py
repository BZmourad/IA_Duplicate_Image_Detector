"""
Results display widget.
"""

import logging
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QTabWidget, QGridLayout, QSizePolicy,
    QMessageBox
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QImage, QFont, QIcon
import cv2
import numpy as np
import subprocess
import sys

logger = logging.getLogger(__name__)


class ResultsWidget(QWidget):
    """Widget for displaying analysis results."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Summary section
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.StyledPanel)
        summary_layout = QGridLayout()
        
        self.total_images_label = QLabel("Total images: -")
        self.exact_duplicates_label = QLabel("Exact duplicates: -")
        self.duplicate_groups_label = QLabel("Duplicate groups: -")
        self.review_groups_label = QLabel("Manual review: -")
        self.processing_time_label = QLabel("Processing time: -")
        
        summary_layout.addWidget(self.total_images_label, 0, 0)
        summary_layout.addWidget(self.exact_duplicates_label, 0, 1)
        summary_layout.addWidget(self.duplicate_groups_label, 1, 0)
        summary_layout.addWidget(self.review_groups_label, 1, 1)
        summary_layout.addWidget(self.processing_time_label, 2, 0, 1, 2)
        
        summary_frame.setLayout(summary_layout)
        layout.addWidget(summary_frame)
        
        # Results tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Duplicate groups tab
        self.duplicates_scroll = QScrollArea()
        self.duplicates_widget = QWidget()
        self.duplicates_layout = QVBoxLayout()
        self.duplicates_widget.setLayout(self.duplicates_layout)
        self.duplicates_scroll.setWidget(self.duplicates_widget)
        self.duplicates_scroll.setWidgetResizable(True)
        self.tabs.addTab(self.duplicates_scroll, "Duplicate Groups")
        
        # Manual review tab
        self.review_scroll = QScrollArea()
        self.review_widget = QWidget()
        self.review_layout = QVBoxLayout()
        self.review_widget.setLayout(self.review_layout)
        self.review_scroll.setWidget(self.review_widget)
        self.review_scroll.setWidgetResizable(True)
        self.tabs.addTab(self.review_scroll, "Manual Review")
        
        self.setLayout(layout)
    
    def clear_results(self):
        """Clear all results."""
        # Clear duplicate groups
        while self.duplicates_layout.count():
            item = self.duplicates_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Clear review groups
        while self.review_layout.count():
            item = self.review_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Reset labels
        self.total_images_label.setText("Total images: -")
        self.exact_duplicates_label.setText("Exact duplicates: -")
        self.duplicate_groups_label.setText("Duplicate groups: -")
        self.review_groups_label.setText("Manual review: -")
        self.processing_time_label.setText("Processing time: -")
    
    def display_results(self, results: dict, processing_time: str):
        """Display analysis results."""
        self.clear_results()
        
        # Update summary labels
        self.total_images_label.setText(f"Total images: {results['total_images']}")
        self.exact_duplicates_label.setText(f"Exact duplicates: {results['exact_duplicates']}")
        self.duplicate_groups_label.setText(f"Duplicate groups: {results['duplicate_groups']}")
        self.review_groups_label.setText(f"Manual review: {results['review_groups']}")
        self.processing_time_label.setText(f"Processing time: {processing_time}")
        
        # Display duplicate groups
        self._display_groups(results["groups"]["duplicates"], self.duplicates_layout, "Group")
        
        # Display review groups
        self._display_groups(results["groups"]["review"], self.review_layout, "Candidate Group")
        
        # Update tab labels
        self.tabs.setTabText(0, f"Duplicate Groups ({results['duplicate_groups']})")
        self.tabs.setTabText(1, f"Manual Review ({results['review_groups']})")
    
    def _display_groups(self, groups: list, layout: QVBoxLayout, prefix: str):
        """Display groups in the given layout."""
        for idx, group in enumerate(groups, 1):
            group_frame = QFrame()
            group_frame.setFrameStyle(QFrame.StyledPanel)
            group_layout = QVBoxLayout()
            
            # Group header
            header_layout = QHBoxLayout()
            
            group_label = QLabel(f"{prefix} #{idx}")
            group_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            
            confidence_label = QLabel(f"Confidence: {group['confidence']*100:.1f}%")
            confidence_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            images_label = QLabel(f"Images: {group['num_images']}")
            
            header_layout.addWidget(group_label)
            header_layout.addWidget(confidence_label)
            header_layout.addWidget(images_label)
            header_layout.addStretch()
            
            group_layout.addLayout(header_layout)
            
            # Similarity details
            if prefix == "Candidate Group":
                details_label = QLabel(
                    f"Similarity: {group['product_similarity']*100:.1f}% | "
                    f"Color similarity: {group['color_similarity']*100:.1f}%"
                )
                details_label.setStyleSheet("color: #666;")
                group_layout.addWidget(details_label)
            
            # Image thumbnails
            thumbnails_layout = QHBoxLayout()
            thumbnails_layout.setSpacing(10)
            
            for image_path in group["images"]:
                thumbnail = self._create_thumbnail(image_path)
                if thumbnail:
                    thumbnails_layout.addWidget(thumbnail)
            
            group_layout.addLayout(thumbnails_layout)
            
            group_frame.setLayout(group_layout)
            layout.addWidget(group_frame)
        
        # Add stretch at the end
        layout.addStretch()
    
    def _create_thumbnail(self, image_path: str) -> QWidget:
        """Create a thumbnail widget for an image."""
        from ..image_loader import ImageLoader
        
        image_loader = ImageLoader()
        
        thumbnail_widget = QWidget()
        thumbnail_layout = QVBoxLayout()
        thumbnail_layout.setContentsMargins(5, 5, 5, 5)
        
        # Load thumbnail
        thumbnail_img = image_loader.load_thumbnail(image_path, (150, 150))
        
        if thumbnail_img is not None:
            # Convert numpy array to QImage
            height, width, channels = thumbnail_img.shape
            bytes_per_line = channels * width
            q_image = QImage(thumbnail_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Create pixmap
            pixmap = QPixmap.fromImage(q_image)
            
            # Create label for image
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setFixedSize(160, 160)
            image_label.setStyleSheet("border: 1px solid #ccc; border-radius: 5px;")
            
            # Make image clickable
            image_label.mousePressEvent = lambda event, path=image_path: self._open_image(path)
            image_label.setCursor(Qt.PointingHandCursor)
            image_label.setToolTip("Click to open image")
            
            thumbnail_layout.addWidget(image_label)
        
        # Filename label
        filename = os.path.basename(image_path)
        if len(filename) > 20:
            filename = filename[:17] + "..."
        
        filename_label = QLabel(filename)
        filename_label.setAlignment(Qt.AlignCenter)
        filename_label.setMaximumWidth(160)
        filename_label.setWordWrap(True)
        
        thumbnail_layout.addWidget(filename_label)
        
        thumbnail_widget.setLayout(thumbnail_layout)
        return thumbnail_widget
    
    def _open_image(self, image_path: str):
        """Open image with default viewer."""
        try:
            if sys.platform == 'win32':
                os.startfile(image_path)
            elif sys.platform == 'darwin':
                subprocess.call(['open', image_path])
            else:
                subprocess.call(['xdg-open', image_path])
        except Exception as e:
            logger.error(f"Error opening image: {e}")
            QMessageBox.warning(self, "Error", f"Could not open image: {e}")