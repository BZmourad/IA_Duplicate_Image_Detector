#!/usr/bin/env python3
"""
Convert PNG icon to ICO format for Windows executable.
"""

import os
from PIL import Image
from pathlib import Path

def convert_png_to_ico(png_path, output_dir="assets"):
    """Convert PNG to ICO format."""
    
    # Check if input file exists
    if not os.path.exists(png_path):
        print(f"Error: {png_path} not found")
        return False
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the PNG image
    img = Image.open(png_path)
    
    # Convert to RGBA if necessary
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Create multiple sizes for the ICO file
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # Save as ICO
    ico_path = os.path.join(output_dir, "logo.ico")
    img.save(ico_path, format='ICO', sizes=sizes)
    
    print(f"ICO file created: {ico_path}")
    return True

if __name__ == "__main__":
    # Convert the logo
    png_path = "assets/logo.png"
    
    if os.path.exists(png_path):
        convert_png_to_ico(png_path)
    else:
        print(f"Error: {png_path} not found")
        print("Please add your logo at assets/logo.png")