"""
Main application window - Simple and clean design.
"""

import logging
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QProgressBar, 
    QFrame, QMessageBox, QGroupBox, QGridLayout,
    QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QFont, QIcon
from datetime import datetime

from .workers import AnalysisWorker
from .results_widget import ResultsWidget
from .styles import AppTheme
from ..utils import load_config, format_time

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.worker = None
        self.start_time = None
        self.current_results = None
        self.current_processing_time = "00:00:00"
        
        self.init_ui()
        self.apply_theme()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Duplicate Image Detector")
        self.setMinimumSize(900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Duplicate Image Detector")
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Product image duplicate detection")
        subtitle_label.setObjectName("subtitleLabel")
        main_layout.addWidget(subtitle_label)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #D1D5DB;")
        main_layout.addWidget(separator)
        
        # Folder selection
        folder_group = QGroupBox("Folder Selection")
        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(10)
        
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Path to folder containing images...")
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setObjectName("secondaryButton")
        self.browse_button.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(self.folder_input, 1)
        folder_layout.addWidget(self.browse_button)
        
        folder_group.setLayout(folder_layout)
        main_layout.addWidget(folder_group)
        
        # File info
        self.file_info_label = QLabel("")
        self.file_info_label.setObjectName("statusInfo")
        main_layout.addWidget(self.file_info_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.analyze_button = QPushButton("Analyze Images")
        self.analyze_button.setObjectName("primaryButton")
        self.analyze_button.clicked.connect(self.start_analysis)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("secondaryButton")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_analysis)
        
        button_layout.addWidget(self.analyze_button, 1)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Progress section
        self.progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(5)
        
        self.stage_label = QLabel("Ready")
        self.stage_label.setStyleSheet("font-weight: bold;")
        progress_layout.addWidget(self.stage_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusInfo")
        progress_layout.addWidget(self.status_label)
        
        self.device_label = QLabel("")
        self.device_label.setObjectName("statusInfo")
        progress_layout.addWidget(self.device_label)
        
        self.progress_group.setLayout(progress_layout)
        self.progress_group.hide()
        main_layout.addWidget(self.progress_group)
        
        # Results section
        self.results_widget = ResultsWidget()
        main_layout.addWidget(self.results_widget, 1)
        
        # Export buttons
        export_layout = QHBoxLayout()
        export_layout.setSpacing(10)
        
        export_layout.addStretch()
        
        self.export_csv_button = QPushButton("Export CSV")
        self.export_csv_button.setObjectName("secondaryButton")
        self.export_csv_button.setEnabled(False)
        self.export_csv_button.clicked.connect(lambda: self.export_results("csv"))
        export_layout.addWidget(self.export_csv_button)
        
        self.export_excel_button = QPushButton("Export Excel")
        self.export_excel_button.setObjectName("secondaryButton")
        self.export_excel_button.setEnabled(False)
        self.export_excel_button.clicked.connect(lambda: self.export_results("excel"))
        export_layout.addWidget(self.export_excel_button)
        
        main_layout.addLayout(export_layout)
        
        # Connect signals
        self.folder_input.textChanged.connect(self.validate_input)
        
        # Initial validation
        self.validate_input()
    
    def apply_theme(self):
        """Apply the application theme."""
        self.setStyleSheet(AppTheme.get_main_stylesheet())
    
    def browse_folder(self):
        """Open folder selection dialog."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Image Folder",
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly
        )
        
        if folder_path:
            self.folder_input.setText(folder_path)
    
    def validate_input(self):
        """Validate the folder path."""
        folder_path = self.folder_input.text().strip()
        
        if not folder_path:
            self.analyze_button.setEnabled(False)
            self.file_info_label.setText("")
            return
        
        if not os.path.exists(folder_path):
            self.analyze_button.setEnabled(False)
            self.file_info_label.setText("Folder does not exist")
            self.file_info_label.setObjectName("statusError")
            self.file_info_label.style().polish(self.file_info_label)
            return
        
        if not os.path.isdir(folder_path):
            self.analyze_button.setEnabled(False)
            self.file_info_label.setText("Path is not a folder")
            self.file_info_label.setObjectName("statusError")
            self.file_info_label.style().polish(self.file_info_label)
            return
        
        # Count images
        from ..image_loader import ImageLoader
        image_loader = ImageLoader()
        images = image_loader.find_images(folder_path)
        
        if not images:
            self.analyze_button.setEnabled(False)
            self.file_info_label.setText("No images found in this folder")
            self.file_info_label.setObjectName("statusError")
            self.file_info_label.style().polish(self.file_info_label)
            return
        
        self.analyze_button.setEnabled(True)
        self.file_info_label.setText(f"{len(images)} images found")
        self.file_info_label.setObjectName("statusSuccess")
        self.file_info_label.style().polish(self.file_info_label)
    
    def start_analysis(self):
        """Start the analysis process."""
        folder_path = self.folder_input.text().strip()
        
        if not folder_path or not os.path.exists(folder_path):
            QMessageBox.warning(self, "Invalid Folder", "Please select a valid folder.")
            return
        
        # Disable UI during analysis
        self.analyze_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.folder_input.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.export_csv_button.setEnabled(False)
        self.export_excel_button.setEnabled(False)
        
        # Show progress
        self.progress_group.show()
        self.progress_bar.setValue(0)
        self.stage_label.setText("Initializing...")
        self.status_label.setText("Preparing analysis...")
        
        # Clear previous results
        self.results_widget.clear_results()
        
        # Record start time
        self.start_time = datetime.now()
        
        # Create and start worker
        self.worker = AnalysisWorker(folder_path, self.config)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.stage_updated.connect(self.update_stage)
        self.worker.analysis_complete.connect(self.analysis_finished)
        self.worker.analysis_error.connect(self.analysis_failed)
        self.worker.start()
    
    def cancel_analysis(self):
        """Cancel the current analysis."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.status_label.setText("Cancelling...")
            self.cancel_button.setEnabled(False)
    
    def update_progress(self, percentage: int, stage: str):
        """Update progress bar and status."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(stage)
    
    def update_stage(self, current: int, total: int):
        """Update stage information."""
        stages = [
            "Calculating hashes",
            "Perceptual hashes",
            "Generating embeddings",
            "Color analysis",
            "Creating groups"
        ]
        
        stage_name = stages[min(current - 1, len(stages) - 1)]
        self.stage_label.setText(f"Stage {current}/{total}: {stage_name}")
    
    def analysis_finished(self, results: dict):
        """Handle analysis completion."""
        # Re-enable UI
        self.analyze_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.folder_input.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.export_csv_button.setEnabled(True)
        self.export_excel_button.setEnabled(True)
        
        # Calculate processing time
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            processing_time = format_time(elapsed)
        else:
            processing_time = "00:00:00"
        
        # Update results
        self.results_widget.display_results(results, processing_time)
        
        # Update status
        self.status_label.setText("Analysis complete")
        self.status_label.setObjectName("statusSuccess")
        self.status_label.style().polish(self.status_label)
        
        self.device_label.setText(f"Device: {results.get('device', 'CPU')}")
        
        # Store results for export
        self.current_results = results
        self.current_processing_time = processing_time
    
    def analysis_failed(self, error_message: str):
        """Handle analysis failure."""
        # Re-enable UI
        self.analyze_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.folder_input.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        # Show error
        self.status_label.setText("Analysis failed")
        self.status_label.setObjectName("statusError")
        self.status_label.style().polish(self.status_label)
        
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_message}")
    
    def export_results(self, format_type: str):
        """Export results to CSV or Excel."""
        if not self.current_results:
            QMessageBox.warning(self, "No Results", "Please run an analysis first.")
            return
        
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "csv":
            file_path = os.path.join(output_dir, f"duplicates_{timestamp}.csv")
            self._export_to_csv(file_path)
        else:
            file_path = os.path.join(output_dir, f"duplicates_{timestamp}.xlsx")
            self._export_to_excel(file_path)
    
    def _export_to_csv(self, file_path: str):
        """Export results to CSV."""
        from ..report import ReportGenerator
        report_gen = ReportGenerator()
        report_gen.export_to_csv(self.current_results["groups"], file_path)
        
        QMessageBox.information(self, "Export Successful", f"Results exported to:\n{file_path}")
    
    def _export_to_excel(self, file_path: str):
        """Export results to Excel."""
        from ..report import ReportGenerator
        
        summary = {
            "Total Images": self.current_results["total_images"],
            "Exact Duplicates": self.current_results["exact_duplicates"],
            "Duplicate Groups": self.current_results["duplicate_groups"],
            "Manual Review Groups": self.current_results["review_groups"],
            "Processing Time": self.current_processing_time,
            "Device": self.current_results.get("device", "Unknown"),
            "Export Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        report_gen = ReportGenerator()
        report_gen.export_to_excel(self.current_results["groups"], file_path, summary)
        
        QMessageBox.information(self, "Export Successful", f"Results exported to:\n{file_path}")