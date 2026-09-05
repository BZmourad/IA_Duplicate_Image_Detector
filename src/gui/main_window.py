"""
Main application window.
"""

import logging
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QProgressBar, 
    QScrollArea, QFrame, QMessageBox, QSplitter, QTabWidget,
    QTextEdit, QGroupBox, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QImage, QFont
import cv2
import numpy as np
from datetime import datetime

from .workers import AnalysisWorker
from .results_widget import ResultsWidget
from ..utils import load_config, format_time

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.worker = None
        self.start_time = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Duplicate Product Image Detector")
        self.setMinimumSize(900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Duplicate Product Image Detector")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Images folder:")
        folder_label.setMinimumWidth(100)
        
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select a folder containing images...")
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_input, 1)
        folder_layout.addWidget(self.browse_button)
        
        main_layout.addLayout(folder_layout)
        
        # Analyze button
        self.analyze_button = QPushButton("ANALYZE IMAGES")
        self.analyze_button.setMinimumHeight(50)
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.analyze_button.clicked.connect(self.start_analysis)
        main_layout.addWidget(self.analyze_button)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_analysis)
        main_layout.addWidget(self.cancel_button)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.stage_label = QLabel("Ready")
        self.stage_label.setStyleSheet("font-weight: bold;")
        progress_layout.addWidget(self.stage_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        progress_layout.addWidget(self.status_label)
        
        self.device_label = QLabel("Device: Not initialized")
        progress_layout.addWidget(self.device_label)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Results section
        self.results_widget = ResultsWidget()
        main_layout.addWidget(self.results_widget, 1)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        self.export_csv_button = QPushButton("Export CSV")
        self.export_csv_button.setEnabled(False)
        self.export_csv_button.clicked.connect(lambda: self.export_results("csv"))
        
        self.export_excel_button = QPushButton("Export Excel")
        self.export_excel_button.setEnabled(False)
        self.export_excel_button.clicked.connect(lambda: self.export_results("excel"))
        
        export_layout.addStretch()
        export_layout.addWidget(self.export_csv_button)
        export_layout.addWidget(self.export_excel_button)
        
        main_layout.addLayout(export_layout)
        
        # Connect signals
        self.folder_input.textChanged.connect(self.validate_input)
        
        # Initial validation
        self.validate_input()
    
    def browse_folder(self):
        """Open folder selection dialog."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Image Folder",
            os.path.expanduser("~")
        )
        
        if folder_path:
            self.folder_input.setText(folder_path)
    
    def validate_input(self):
        """Validate the folder path."""
        folder_path = self.folder_input.text().strip()
        
        if not folder_path:
            self.analyze_button.setEnabled(False)
            return
        
        if not os.path.exists(folder_path):
            self.analyze_button.setEnabled(False)
            self.status_label.setText("Folder does not exist")
            self.status_label.setStyleSheet("color: red;")
            return
        
        if not os.path.isdir(folder_path):
            self.analyze_button.setEnabled(False)
            self.status_label.setText("Selected path is not a folder")
            self.status_label.setStyleSheet("color: red;")
            return
        
        self.analyze_button.setEnabled(True)
        self.status_label.setText("")
    
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
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.stage_label.setText("Starting analysis...")
        self.status_label.setText("Initializing...")
        
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
        """Update progress bar and stage label."""
        self.progress_bar.setValue(percentage)
        self.stage_label.setText(stage)
        self.status_label.setText(stage)
    
    def update_stage(self, current: int, total: int):
        """Update stage information."""
        self.stage_label.setText(f"Stage {current}/{total}")
    
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
        self.status_label.setText("Analysis complete!")
        self.device_label.setText(f"Device: {results.get('device', 'Unknown')}")
        
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
        self.status_label.setStyleSheet("color: red;")
        QMessageBox.critical(self, "Analysis Error", error_message)
    
    def export_results(self, format_type: str):
        """Export results to CSV or Excel."""
        if not hasattr(self, 'current_results'):
            return
        
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "csv":
            file_path = os.path.join(output_dir, f"duplicates_{timestamp}.csv")
            self._export_to_csv(file_path)
        else:  # excel
            file_path = os.path.join(output_dir, f"duplicates_{timestamp}.xlsx")
            self._export_to_excel(file_path)
    
    def _export_to_csv(self, file_path: str):
        """Export results to CSV."""
        from ..report import ReportGenerator
        report_gen = ReportGenerator()
        report_gen.export_to_csv(self.current_results["groups"], file_path)
        
        QMessageBox.information(
            self,
            "Export Complete",
            f"Results exported to:\n{file_path}"
        )
    
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
        
        QMessageBox.information(
            self,
            "Export Complete",
            f"Results exported to:\n{file_path}"
        )