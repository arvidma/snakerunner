#!/usr/bin/env python3
"""
Create a placeholder baseline image for visual regression testing.

This creates a minimal baseline image that can be committed to git.
Users should run the actual visual tests to create a real baseline
screenshot from their environment.
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_baseline(output_path, width=800, height=600):
    """Create a placeholder baseline image"""
    # Create image with light gray background
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)

    # Draw a simple border
    border_color = (200, 200, 200)
    draw.rectangle([10, 10, width-10, height-10], outline=border_color, width=2)

    # Add some colored rectangles to simulate squaremap visualization
    colors = [
        (100, 150, 200),  # Blue
        (150, 200, 100),  # Green
        (200, 150, 100),  # Orange
        (180, 100, 150),  # Purple
        (100, 200, 180),  # Teal
    ]

    x, y = 50, 50
    for i, color in enumerate(colors):
        rect_width = 120 + (i * 20)
        rect_height = 80 + (i * 15)
        draw.rectangle([x, y, x + rect_width, y + rect_height],
                      fill=color, outline=(0, 0, 0))
        y += rect_height + 20

    # Add text message
    try:
        # Try to use a basic font
        font = ImageFont.load_default()
    except:
        font = None

    text_lines = [
        "PLACEHOLDER BASELINE IMAGE",
        "",
        "This is a placeholder for visual regression testing.",
        "To create a real baseline:",
        "  1. Install wxPython: pip install wxPython",
        "  2. Run: xvfb-run -a python3 test_visual_profile.py",
        "  3. Commit the generated baseline image",
        "",
        "The real baseline will be a screenshot of the",
        "snakerunner GUI with actual profile visualization."
    ]

    text_y = height - 280
    for line in text_lines:
        if font:
            draw.text((30, text_y), line, fill=(80, 80, 80), font=font)
        text_y += 22

    # Save the image
    img.save(output_path, 'PNG')
    print(f"✓ Created placeholder baseline: {output_path}")
    print(f"  Size: {width}x{height}")
    print(f"  Run visual tests with wxPython to create real baseline")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'visual_test_baseline.png')

    print("Creating placeholder baseline image...")
    create_placeholder_baseline(output_path)
