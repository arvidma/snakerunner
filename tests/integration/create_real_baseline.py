#!/usr/bin/env python3
"""
Create a real baseline image from the existing snakerunner screenshot.

This takes the existing screenshot.png from the project root and processes
it to create a proper baseline image for visual regression testing.
"""
from PIL import Image
import os

def create_baseline_from_screenshot(screenshot_path, output_path, target_size=(800, 600)):
    """Create baseline from existing screenshot"""
    print(f"Loading screenshot from: {screenshot_path}")

    # Load the screenshot
    img = Image.open(screenshot_path)
    original_size = img.size
    print(f"  Original size: {original_size[0]}x{original_size[1]}")

    # Calculate aspect-preserving resize
    aspect = original_size[0] / original_size[1]
    if aspect > (target_size[0] / target_size[1]):
        # Width is limiting factor
        new_width = target_size[0]
        new_height = int(new_width / aspect)
    else:
        # Height is limiting factor
        new_height = target_size[1]
        new_width = int(new_height * aspect)

    print(f"  Resizing to: {new_width}x{new_height}")

    # Resize with high quality
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # If the resized image is smaller than target, create a canvas and center it
    if new_width < target_size[0] or new_height < target_size[1]:
        canvas = Image.new('RGB', target_size, color=(240, 240, 240))
        offset_x = (target_size[0] - new_width) // 2
        offset_y = (target_size[1] - new_height) // 2
        canvas.paste(img_resized, (offset_x, offset_y))
        img_final = canvas
    else:
        img_final = img_resized

    # Save as baseline
    img_final.save(output_path, 'PNG', optimize=True)
    file_size = os.path.getsize(output_path)

    print(f"\n✓ Created baseline from real screenshot")
    print(f"  Output: {output_path}")
    print(f"  Size: {img_final.size[0]}x{img_final.size[1]}")
    print(f"  File size: {file_size:,} bytes")
    print(f"\nThis baseline shows actual snakerunner visualization with:")
    print(f"  - Real squaremap rendering")
    print(f"  - Actual profile data display")
    print(f"  - Genuine UI elements and colors")

if __name__ == '__main__':
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.join(script_dir, '..', '..')
    screenshot_path = os.path.join(repo_root, 'screenshot.png')
    output_path = os.path.join(script_dir, 'visual_test_baseline.png')

    if not os.path.exists(screenshot_path):
        print(f"Error: Screenshot not found at {screenshot_path}")
        print("Please ensure screenshot.png exists in the repository root")
        exit(1)

    print("="*60)
    print("Creating Real Baseline from Screenshot")
    print("="*60)

    create_baseline_from_screenshot(screenshot_path, output_path)

    print("\nThis baseline represents real snakerunner output and can be")
    print("used for visual regression testing to detect UI changes.")
