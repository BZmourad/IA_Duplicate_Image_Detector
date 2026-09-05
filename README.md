# Duplicate Product Image Detector

A professional desktop application for detecting duplicate product images using advanced computer vision techniques.

## Features

- **Exact Duplicate Detection**: SHA-256 hash-based detection
- **Perceptual Hashing**: Detects near-duplicates with minor modifications
- **Visual Embeddings**: DINOv2-based deep learning embeddings
- **Color Verification**: Ensures different colors aren't marked as duplicates
- **Efficient Search**: FAISS-powered similarity search for large datasets
- **User-Friendly GUI**: PySide6-based desktop interface
- **Export Results**: CSV and Excel export with detailed reports
- **Caching**: Embedding cache for faster re-analysis
- **Progress Tracking**: Real-time progress updates

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Setup

1. Clone or download the repository

2. Create a virtual environment:
python -m venv .venv

3. Activate the virtual environment:
Windows:
.venv\Scripts\activate
Linux/Mac:
source .venv/bin/activate

4. Install dependencies:
pip install -r requirements.txt

5. Run the application:
python main.py