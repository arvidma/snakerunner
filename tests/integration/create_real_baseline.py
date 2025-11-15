#!/usr/bin/env python3
"""
Create a baseline image for visual regression testing.

IMPORTANT: This script creates a baseline from pytest_tests.profile that our
integration tests actually use. Without wxPython installed, we cannot render
the actual GUI, so this creates an informative placeholder.

To create a REAL baseline that matches the test profile:
1. Install wxPython: pip install wxPython
2. Run: xvfb-run -a python3 test_visual_profile.py
3. This will capture actual pytest profile visualization
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_baseline(output_path, target_size=(800, 600)):
    """Create an informative placeholder baseline"""

    # Create image with light gray background
    img = Image.new('RGB', target_size, color=(240, 240, 240))
    draw = ImageDraw.Draw(img)

    # Draw border
    border_color = (100, 100, 100)
    draw.rectangle([2, 2, target_size[0]-2, target_size[1]-2], outline=border_color, width=3)

    try:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    except:
        font_large = font_small = None

    # Warning message
    messages = [
        ("PLACEHOLDER BASELINE IMAGE", 40, (180, 0, 0)),
        ("", 70, (0, 0, 0)),
        ("This baseline does NOT match pytest_tests.profile used by tests!", 100, (100, 0, 0)),
        ("", 130, (0, 0, 0)),
        ("To create a valid baseline:", 160, (0, 0, 0)),
        ("  1. Install wxPython: pip install wxPython", 190, (50, 50, 50)),
        ("  2. Run: xvfb-run -a python3 test_visual_profile.py", 220, (50, 50, 50)),
        ("  3. Commit the generated visual_test_baseline.png", 250, (50, 50, 50)),
        ("", 280, (0, 0, 0)),
        ("Why this matters:", 310, (0, 0, 0)),
        ("  - Tests use pytest_tests.profile (pytest/pluggy functions)", 340, (50, 50, 50)),
        ("  - Without correct baseline, all visual tests will fail", 370, (50, 50, 50)),
        ("  - Baseline must show pytest visualization, not other profiles", 400, (50, 50, 50)),
        ("", 430, (0, 0, 0)),
        ("This placeholder prevents git errors but should be replaced.", 460, (150, 0, 0)),
        ("Visual regression testing requires a matching baseline image.", 490, (150, 0, 0)),
    ]

    for text, y, color in messages:
        if font_small:
            draw.text((20, y), text, fill=color, font=font_small)

    # Save
    img.save(output_path, 'PNG', optimize=True)
    file_size = os.path.getsize(output_path)

    print(f"✓ Created placeholder baseline: {output_path}")
    print(f"  Size: {target_size[0]}x{target_size[1]}, {file_size:,} bytes")
    print(f"\n⚠ WARNING: This is a PLACEHOLDER")
    print(f"  Visual tests will NOT work correctly without a real baseline!")
    print(f"  Install wxPython and run test_visual_profile.py to create it.")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'visual_test_baseline.png')

    print("="*70)
    print("Creating Placeholder Baseline (wxPython required for real baseline)")
    print("="*70)
    print()

    create_placeholder_baseline(output_path)

    print()
    print("This baseline is a placeholder and should be replaced with a real")
    print("screenshot from test_visual_profile.py using pytest_tests.profile.")
