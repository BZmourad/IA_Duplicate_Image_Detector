#!/usr/bin/env python3
"""
Create a default logo for the application if none exists.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_default_logo(output_path="assets/logo.png"):
    """Create a default logo."""
    
    # Create assets directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create a new image with a gradient background
    width, height = 256, 256
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a rounded rectangle background
    draw.rounded_rectangle(
        [10, 10, 246, 246],
        radius=30,
        fill=(52, 152, 219, 255)  # Blue
    )
    
    # Draw a smaller rounded rectangle
    draw.rounded_rectangle(
        [30, 30, 226, 226],
        radius=25,
        fill=(41, 128, 185, 255)  # Darker blue
    )
    
    # Draw two overlapping rectangles to represent duplicate images
    # First rectangle (back)
    draw.rectangle(
        [70, 70, 170, 170],
        outline=(255, 255, 255, 255),
        width=5
    )
    
    # Second rectangle (front, offset)
    draw.rectangle(
        [90, 90, 190, 190],
        outline=(255, 255, 255, 200),
        width=5
    )
    
    # Draw a checkmark
    draw.line([110, 140, 130, 160, 170, 110], fill=(46, 204, 113, 255), width=8)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((80, 200), "DUP", fill=(255, 255, 255, 255), font=font)
    
    # Save the image
    img.save(output_path, format='PNG')
    print(f"Default logo created: {output_path}")

if __name__ == "__main__":
    create_default_logo()