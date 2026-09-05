#!/usr/bin/env python3
"""
Test dataset generation script.
Creates a diverse test dataset for evaluating the duplicate detector.
"""

import os
import shutil
import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

def create_test_dataset(output_dir="test_dataset"):
    """Create a test dataset with various duplicate scenarios."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create synthetic product images
    create_sofa_images(output_dir)
    create_chair_images(output_dir)
    create_table_images(output_dir)
    create_miscellaneous_images(output_dir)
    
    print(f"Test dataset created in {output_dir}")

def create_sofa_images(output_dir):
    """Create sofa product images."""
    sofa_dir = os.path.join(output_dir, "sofas")
    os.makedirs(sofa_dir, exist_ok=True)
    
    # Create base sofa images in different colors
    colors = {
        "gray": (128, 128, 128),
        "blue": (100, 100, 200),
        "beige": (200, 180, 150),
        "green": (100, 150, 100)
    }
    
    for color_name, color in colors.items():
        # Create base image
        base_img = create_sofa_image(color)
        base_path = os.path.join(sofa_dir, f"sofa_{color_name}.jpg")
        cv2.imwrite(base_path, base_img)
        
        # Create exact duplicate
        shutil.copy2(base_path, os.path.join(sofa_dir, f"sofa_{color_name}_exact.jpg"))
        
        # Create resized version
        resized = cv2.resize(base_img, (300, 200))
        cv2.imwrite(os.path.join(sofa_dir, f"sofa_{color_name}_resized.jpg"), resized)
        
        # Create compressed version
        compressed_path = os.path.join(sofa_dir, f"sofa_{color_name}_compressed.jpg")
        cv2.imwrite(compressed_path, base_img, [cv2.IMWRITE_JPEG_QUALITY, 30])
        
        # Create version with watermark
        watermarked = add_watermark(base_img, "SAMPLE")
        cv2.imwrite(os.path.join(sofa_dir, f"sofa_{color_name}_watermarked.jpg"), watermarked)
        
        # Create different angle (simulated rotation/perspective)
        angle_img = simulate_different_angle(base_img)
        cv2.imwrite(os.path.join(sofa_dir, f"sofa_{color_name}_angle.jpg"), angle_img)
        
        # Create different background
        bg_img = change_background(base_img, (200, 200, 200))
        cv2.imwrite(os.path.join(sofa_dir, f"sofa_{color_name}_bg.jpg"), bg_img)
        
        # Create different lighting
        light_img = change_lighting(base_img, 1.3)
        cv2.imwrite(os.path.join(sofa_dir, f"sofa_{color_name}_lighting.jpg"), light_img)

def create_sofa_image(color):
    """Create a simple sofa image."""
    img = np.ones((400, 600, 3), dtype=np.uint8) * 255  # White background
    
    # Draw sofa body
    cv2.rectangle(img, (100, 150), (500, 350), color, -1)
    
    # Draw sofa arms
    cv2.rectangle(img, (70, 120), (130, 350), color, -1)
    cv2.rectangle(img, (470, 120), (530, 350), color, -1)
    
    # Draw sofa back
    cv2.rectangle(img, (100, 80), (500, 180), color, -1)
    
    # Draw cushions
    cushion_color = tuple(min(255, c + 30) for c in color)
    cv2.rectangle(img, (120, 160), (240, 330), cushion_color, -1)
    cv2.rectangle(img, (260, 160), (380, 330), cushion_color, -1)
    
    # Draw legs
    leg_color = (50, 50, 50)
    cv2.rectangle(img, (110, 350), (130, 400), leg_color, -1)
    cv2.rectangle(img, (470, 350), (490, 400), leg_color, -1)
    
    return img

def create_chair_images(output_dir):
    """Create chair product images."""
    chair_dir = os.path.join(output_dir, "chairs")
    os.makedirs(chair_dir, exist_ok=True)
    
    colors = {
        "brown": (139, 69, 19),
        "black": (50, 50, 50),
        "white": (240, 240, 240)
    }
    
    for color_name, color in colors.items():
        base_img = create_chair_image(color)
        base_path = os.path.join(chair_dir, f"chair_{color_name}.jpg")
        cv2.imwrite(base_path, base_img)
        
        # Create variations
        shutil.copy2(base_path, os.path.join(chair_dir, f"chair_{color_name}_exact.jpg"))
        
        resized = cv2.resize(base_img, (320, 240))
        cv2.imwrite(os.path.join(chair_dir, f"chair_{color_name}_resized.jpg"), resized)
        
        angle_img = simulate_different_angle(base_img)
        cv2.imwrite(os.path.join(chair_dir, f"chair_{color_name}_angle.jpg"), angle_img)

def create_chair_image(color):
    """Create a simple chair image."""
    img = np.ones((400, 400, 3), dtype=np.uint8) * 255
    
    # Draw chair seat
    cv2.rectangle(img, (120, 200), (280, 250), color, -1)
    
    # Draw chair back
    cv2.rectangle(img, (150, 80), (250, 220), color, -1)
    
    # Draw legs
    leg_color = (60, 60, 60)
    cv2.rectangle(img, (130, 250), (145, 380), leg_color, -1)
    cv2.rectangle(img, (255, 250), (270, 380), leg_color, -1)
    cv2.rectangle(img, (130, 250), (145, 280), leg_color, -1)
    cv2.rectangle(img, (255, 250), (270, 280), leg_color, -1)
    
    return img

def create_table_images(output_dir):
    """Create table product images."""
    table_dir = os.path.join(output_dir, "tables")
    os.makedirs(table_dir, exist_ok=True)
    
    # Create different table styles
    tables = [
        ("modern", (150, 120, 100)),
        ("classic", (120, 80, 40)),
        ("glass", (200, 200, 200))
    ]
    
    for name, color in tables:
        base_img = create_table_image(color, name)
        base_path = os.path.join(table_dir, f"table_{name}.jpg")
        cv2.imwrite(base_path, base_img)
        
        # Create variations
        shutil.copy2(base_path, os.path.join(table_dir, f"table_{name}_exact.jpg"))
        
        compressed_path = os.path.join(table_dir, f"table_{name}_compressed.jpg")
        cv2.imwrite(compressed_path, base_img, [cv2.IMWRITE_JPEG_QUALITY, 40])

def create_table_image(color, style):
    """Create a simple table image."""
    img = np.ones((350, 500, 3), dtype=np.uint8) * 255
    
    # Draw table top
    cv2.rectangle(img, (100, 100), (400, 120), color, -1)
    
    # Draw legs
    leg_color = tuple(min(255, c - 30) for c in color)
    cv2.rectangle(img, (120, 120), (140, 320), leg_color, -1)
    cv2.rectangle(img, (360, 120), (380, 320), leg_color, -1)
    
    if style == "modern":
        # Add cross bar
        cv2.rectangle(img, (140, 250), (360, 270), leg_color, -1)
    
    return img

def create_miscellaneous_images(output_dir):
    """Create miscellaneous unrelated images."""
    misc_dir = os.path.join(output_dir, "miscellaneous")
    os.makedirs(misc_dir, exist_ok=True)
    
    # Create random shapes
    for i in range(5):
        img = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        cv2.imwrite(os.path.join(misc_dir, f"random_{i}.jpg"), img)
    
    # Create simple shapes
    shapes = ["circle", "triangle", "rectangle", "star"]
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    
    for shape, color in zip(shapes, colors):
        img = np.ones((300, 300, 3), dtype=np.uint8) * 255
        
        if shape == "circle":
            cv2.circle(img, (150, 150), 100, color, -1)
        elif shape == "triangle":
            pts = np.array([[150, 50], [50, 250], [250, 250]])
            cv2.fillPoly(img, [pts], color)
        elif shape == "rectangle":
            cv2.rectangle(img, (50, 100), (250, 200), color, -1)
        
        cv2.imwrite(os.path.join(misc_dir, f"{shape}.jpg"), img)

def add_watermark(image, text):
    """Add watermark to image."""
    img = image.copy()
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    # Add semi-transparent text
    draw.text((50, 50), text, fill=(128, 128, 128, 128), font=font)
    
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def simulate_different_angle(image):
    """Simulate different angle with perspective transform."""
    h, w = image.shape[:2]
    
    # Create perspective transform
    pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    pts2 = np.float32([[20, 10], [w-30, 0], [0, h-20], [w-10, h]])
    
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(image, matrix, (w, h))
    
    return result

def change_background(image, new_bg_color):
    """Change background color."""
    # Simple approach: threshold white background and replace
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    mask = cv2.bitwise_not(mask)
    
    result = image.copy()
    result[mask > 0] = new_bg_color
    
    return result

def change_lighting(image, factor):
    """Change image brightness."""
    result = cv2.convertScaleAbs(image, alpha=factor, beta=0)
    return result

if __name__ == "__main__":
    create_test_dataset()