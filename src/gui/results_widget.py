"""
Results display widget - Simple and clean.
"""

import logging
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QTabWidget, QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage

logger = logging.getLogger(__name__)


class ResultsWidget(QWidget):
    """Widget for displaying analysis results."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(10)
        
        # Summary
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.StyledPanel)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
            }
        """)
        
        summary_layout = QGridLayout()
        summary_layout.setSpacing(10)
        
        self.total_label = QLabel("Images: 0")
        self.duplicates_label = QLabel("Duplicates: 0")
        self.groups_label = QLabel("Groups: 0")
        self.review_label = QLabel("To Review: 0")
        self.time_label = QLabel("Time: 00:00:00")
        
        for label in [self.total_label, self.duplicates_label, 
                     self.groups_label, self.review_label, self.time_label]:
            label.setStyleSheet("font-weight: bold; padding: 5px;")
        
        summary_layout.addWidget(self.total_label, 0, 0)
        summary_layout.addWidget(self.duplicates_label, 0, 1)
        summary_layout.addWidget(self.groups_label, 1, 0)
        summary_layout.addWidget(self.review_label, 1, 1)
        summary_layout.addWidget(self.time_label, 2, 0, 1, 2)
        
        summary_frame.setLayout(summary_layout)
        layout.addWidget(summary_frame)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Duplicates tab
        self.duplicates_scroll = QScrollArea()
        self.duplicates_scroll.setWidgetResizable(True)
        self.duplicates_widget = QWidget()
        self.duplicates_layout = QVBoxLayout()
        self.duplicates_layout.setSpacing(10)
        self.duplicates_widget.setLayout(self.duplicates_layout)
        self.duplicates_scroll.setWidget(self.duplicates_widget)
        self.tabs.addTab(self.duplicates_scroll, "Detected Duplicates")
        
        # Review tab
        self.review_scroll = QScrollArea()
        self.review_scroll.setWidgetResizable(True)
        self.review_widget = QWidget()
        self.review_layout = QVBoxLayout()
        self.review_layout.setSpacing(10)
        self.review_widget.setLayout(self.review_layout)
        self.review_scroll.setWidget(self.review_widget)
        self.tabs.addTab(self.review_scroll, "Manual Review")
        
        self.setLayout(layout)
    
    def clear_results(self):
        """Clear all results."""
        # Clear layouts
        for layout in [self.duplicates_layout, self.review_layout]:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        # Reset labels
        self.total_label.setText("Images: 0")
        self.duplicates_label.setText("Duplicates: 0")
        self.groups_label.setText("Groups: 0")
        self.review_label.setText("To Review: 0")
        self.time_label.setText("Time: 00:00:00")
        
        # Reset tab titles
        self.tabs.setTabText(0, "Detected Duplicates")
        self.tabs.setTabText(1, "Manual Review")
    
    def display_results(self, results: dict, processing_time: str):
        """Display analysis results."""
        self.clear_results()
        
        # Update summary
        self.total_label.setText(f"Images: {results['total_images']}")
        self.duplicates_label.setText(f"Duplicates: {results['exact_duplicates']}")
        self.groups_label.setText(f"Groups: {results['duplicate_groups']}")
        self.review_label.setText(f"To Review: {results['review_groups']}")
        self.time_label.setText(f"Time: {processing_time}")
        
        # Display groups
        self._display_groups(results["groups"]["duplicates"], 
                            self.duplicates_layout, "Group")
        self._display_groups(results["groups"]["review"], 
                            self.review_layout, "Candidate")
        
        # Update tab titles
        self.tabs.setTabText(0, f"Detected Duplicates ({results['duplicate_groups']})")
        self.tabs.setTabText(1, f"Manual Review ({results['review_groups']})")
    
    def _display_groups(self, groups: list, layout: QVBoxLayout, prefix: str):
        """Display groups in layout."""
        for idx, group in enumerate(groups, 1):
            group_frame = self._create_group_frame(group, idx, prefix)
            layout.addWidget(group_frame)
        
        layout.addStretch()
    
    def _create_group_frame(self, group: dict, idx: int, prefix: str) -> QFrame:
        """Create a group frame."""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
            }
        """)
        
        frame_layout = QVBoxLayout()
        frame_layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel(f"{prefix} #{idx}")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(title)
        
        header.addStretch()
        
        confidence = QLabel(f"Confidence: {group['confidence']*100:.1f}%")
        confidence.setStyleSheet("""
            color: #16A34A;
            font-weight: bold;
            padding: 5px 10px;
            background-color: #F0FDF4;
            border-radius: 4px;
        """)
        header.addWidget(confidence)
        
        images_count = QLabel(f"{group['num_images']} images")
        images_count.setStyleSheet("color: #6B7280;")
        header.addWidget(images_count)
        
        frame_layout.addLayout(header)
        
        # Similarity info for review groups
        if prefix == "Candidate":
            info = QLabel(
                f"Product similarity: {group['product_similarity']*100:.1f}% | "
                f"Color similarity: {group['color_similarity']*100:.1f}%"
            )
            info.setStyleSheet("color: #6B7280; font-size: 12px;")
            frame_layout.addWidget(info)
        
        # Thumbnails
        thumbnails = QHBoxLayout()
        thumbnails.setSpacing(10)
        
        for image_path in group["images"]:
            thumbnail = self._create_thumbnail(image_path)
            if thumbnail:
                thumbnails.addWidget(thumbnail)
        
        thumbnails.addStretch()
        frame_layout.addLayout(thumbnails)
        
        frame.setLayout(frame_layout)
        return frame
    
    def _create_thumbnail(self, image_path: str) -> QWidget:
        """Create thumbnail widget."""
        from ..image_loader import ImageLoader
        
        image_loader = ImageLoader()
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Load thumbnail
        img = image_loader.load_thumbnail(image_path, (120, 120))
        
        if img is not None:
            height, width, channels = img.shape
            bytes_per_line = channels * width
            q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setFixedSize(130, 130)
            image_label.setStyleSheet("""
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                background-color: white;
            """)
            image_label.mousePressEvent = lambda event, path=image_path: self._open_image(path)
            image_label.setCursor(Qt.PointingHandCursor)
            image_label.setToolTip("Click to open")
            
            layout.addWidget(image_label)
        
        # Filename
        filename = os.path.basename(image_path)
        if len(filename) > 18:
            filename = filename[:15] + "..."
        
        name_label = QLabel(filename)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setMaximumWidth(130)
        name_label.setStyleSheet("font-size: 11px; color: #6B7280;")
        
        layout.addWidget(name_label)
        
        widget.setLayout(layout)
        return widget
    
    def _open_image(self, image_path: str):
        """Open image with default viewer."""
        import subprocess
        import sys
        
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