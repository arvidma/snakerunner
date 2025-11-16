#!/usr/bin/env python3
"""
Automated visual testing of snakerunner profile visualization.

This script loads a cProfile file into snakerunner, captures a screenshot,
and performs visual validation including comparison against a baseline reference.
"""
import os
import sys
import time
import wx
from PIL import Image
import numpy as np
import io

try:
    from skimage.metrics import structural_similarity as ssim
    HAS_SSIM = True
except ImportError:
    HAS_SSIM = False

# Add runsnakerun to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from runsnakerun import runsnake


class VisualTestApp(wx.App):
    """Application for automated visual testing"""

    def __init__(self, profile_path, screenshot_path, baseline_path, *args, **kwargs):
        self.profile_path = profile_path
        self.screenshot_path = screenshot_path
        self.baseline_path = baseline_path
        self.test_results = []
        super().__init__(*args, **kwargs)

    def OnInit(self):
        """Initialize the application and start testing"""
        # Create the main frame
        self.frame = runsnake.MainFrame(config_parser=runsnake.load_config())

        # Set a reasonable window size for screenshots (match typical RunSnakeRun usage)
        self.frame.SetSize((1440, 900))

        self.frame.Show(True)
        self.SetTopWindow(self.frame)

        # Schedule loading the profile and testing
        wx.CallLater(500, self.load_profile)
        return True

    def load_profile(self):
        """Load the profile file"""
        print(f"Loading profile: {self.profile_path}")
        self.frame.load(self.profile_path)

        # Wait for the UI to update and render fully (increased for large window)
        wx.CallLater(2000, self.take_screenshot)

    def take_screenshot(self):
        """Capture a screenshot of the application"""
        print("Capturing screenshot...")

        try:
            # Get the frame's screen rectangle
            rect = self.frame.GetScreenRect()

            # Create a bitmap
            bitmap = wx.Bitmap(rect.width, rect.height)
            memory_dc = wx.MemoryDC(bitmap)

            # Capture the window
            screen_dc = wx.ScreenDC()
            memory_dc.Blit(0, 0, rect.width, rect.height, screen_dc, rect.x, rect.y)

            # Convert to PIL Image for saving
            image = bitmap.ConvertToImage()
            width, height = image.GetWidth(), image.GetHeight()
            pil_image = Image.frombytes('RGB', (width, height), image.GetData())

            # Save the screenshot
            pil_image.save(self.screenshot_path)
            print(f"Screenshot saved to: {self.screenshot_path}")

            # Perform visual validation
            wx.CallLater(100, self.validate_visual, pil_image)

        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            self.test_results.append(('screenshot', False, str(e)))
            wx.CallLater(100, self.finish_tests)

    def validate_visual(self, screenshot):
        """Perform basic visual validation of the screenshot"""
        print("Performing visual validation...")

        width, height = screenshot.size
        pixels = screenshot.load()

        # Test 1: Check that the screenshot is not blank
        non_white_pixels = 0
        total_pixels = width * height

        for x in range(0, width, 10):  # Sample every 10 pixels for speed
            for y in range(0, height, 10):
                r, g, b = pixels[x, y]
                # Check if pixel is not white or very light
                if r < 250 or g < 250 or b < 250:
                    non_white_pixels += 1

        non_white_ratio = non_white_pixels / (total_pixels / 100)  # Adjusted for sampling

        print(f"Non-white pixel ratio: {non_white_ratio:.2%}")
        if non_white_ratio > 0.05:  # At least 5% should have content
            self.test_results.append(('not_blank', True, f'{non_white_ratio:.2%} non-white pixels'))
        else:
            self.test_results.append(('not_blank', False, f'Only {non_white_ratio:.2%} non-white pixels'))

        # Test 2: Check for color variety (profiling visualization should have colors)
        colors_seen = set()
        for x in range(0, width, 20):
            for y in range(0, height, 20):
                colors_seen.add(pixels[x, y])

        print(f"Unique colors detected: {len(colors_seen)}")
        if len(colors_seen) > 10:
            self.test_results.append(('color_variety', True, f'{len(colors_seen)} unique colors'))
        else:
            self.test_results.append(('color_variety', False, f'Only {len(colors_seen)} unique colors'))

        # Test 3: Check that squaremap area has varied colors (indicates rendering)
        # Squaremap should be in the upper-right area of the window
        squaremap_colors = set()
        squaremap_x_start = width // 3
        squaremap_y_end = 2 * height // 3

        for x in range(squaremap_x_start, width, 20):
            for y in range(0, squaremap_y_end, 20):
                if x < width and y < height:
                    squaremap_colors.add(pixels[x, y])

        print(f"Squaremap area colors: {len(squaremap_colors)}")
        if len(squaremap_colors) > 5:
            self.test_results.append(('squaremap_rendered', True, f'{len(squaremap_colors)} colors in squaremap area'))
        else:
            self.test_results.append(('squaremap_rendered', False, f'Only {len(squaremap_colors)} colors in squaremap area'))

        # Test 4: Check if loader was successful
        if self.frame.loader is not None:
            self.test_results.append(('profile_loaded', True, 'Loader initialized'))
        else:
            self.test_results.append(('profile_loaded', False, 'Loader is None'))

        # Test 5: Check if we have profiling data
        if self.frame.loader and hasattr(self.frame.loader, 'rows') and len(self.frame.loader.rows) > 0:
            num_rows = len(self.frame.loader.rows)
            self.test_results.append(('has_data', True, f'{num_rows} profile rows loaded'))
        else:
            self.test_results.append(('has_data', False, 'No profile data loaded'))

        # Test 6: Baseline comparison
        self.compare_with_baseline(screenshot)

        wx.CallLater(100, self.finish_tests)

    def compare_with_baseline(self, screenshot):
        """Compare the screenshot against a baseline reference image"""
        print("\nBaseline Comparison:")

        # Check if baseline exists
        if not os.path.exists(self.baseline_path):
            print(f"⚠ No baseline found at {self.baseline_path}")
            print(f"  Saving current screenshot as baseline for future comparisons")
            screenshot.save(self.baseline_path)
            self.test_results.append(('baseline_comparison', True, 'Baseline created (first run)'))
            return

        # Load baseline
        try:
            baseline = Image.open(self.baseline_path)
        except Exception as e:
            print(f"✗ FAIL: Could not load baseline: {e}")
            self.test_results.append(('baseline_comparison', False, f'Failed to load baseline: {e}'))
            return

        # Check dimensions match
        if screenshot.size != baseline.size:
            msg = f'Size mismatch: current {screenshot.size} vs baseline {baseline.size}'
            print(f"✗ FAIL: {msg}")
            self.test_results.append(('baseline_comparison', False, msg))
            return

        # Convert to numpy arrays for comparison
        screenshot_array = np.array(screenshot)
        baseline_array = np.array(baseline)

        # Calculate pixel difference
        diff = np.abs(screenshot_array.astype(float) - baseline_array.astype(float))
        pixel_diff_mean = np.mean(diff)
        pixel_diff_max = np.max(diff)

        # Calculate percentage of changed pixels (threshold: more than 10 diff in any channel)
        changed_pixels = np.any(diff > 10, axis=2)
        changed_pixel_ratio = np.sum(changed_pixels) / (screenshot.size[0] * screenshot.size[1])

        print(f"  Pixel difference (mean): {pixel_diff_mean:.2f}")
        print(f"  Pixel difference (max): {pixel_diff_max:.0f}")
        print(f"  Changed pixels: {changed_pixel_ratio:.2%}")

        # Calculate SSIM if available
        if HAS_SSIM:
            try:
                # SSIM needs grayscale or we calculate per channel
                ssim_score = ssim(
                    screenshot_array,
                    baseline_array,
                    channel_axis=2,  # RGB channels
                    data_range=255
                )
                print(f"  Structural Similarity (SSIM): {ssim_score:.4f}")

                # SSIM > 0.95 is very similar, > 0.99 is nearly identical
                if ssim_score > 0.90:
                    self.test_results.append((
                        'baseline_comparison',
                        True,
                        f'SSIM={ssim_score:.4f}, mean_diff={pixel_diff_mean:.2f}, changed={changed_pixel_ratio:.2%}'
                    ))
                elif ssim_score > 0.80:
                    self.test_results.append((
                        'baseline_comparison',
                        True,
                        f'Similar but with changes: SSIM={ssim_score:.4f}, mean_diff={pixel_diff_mean:.2f}'
                    ))
                else:
                    self.test_results.append((
                        'baseline_comparison',
                        False,
                        f'Significant difference: SSIM={ssim_score:.4f}, mean_diff={pixel_diff_mean:.2f}'
                    ))
            except Exception as e:
                print(f"  Warning: SSIM calculation failed: {e}")
                # Fall back to simple threshold
                if pixel_diff_mean < 10 and changed_pixel_ratio < 0.10:
                    self.test_results.append((
                        'baseline_comparison',
                        True,
                        f'Similar (no SSIM): mean_diff={pixel_diff_mean:.2f}, changed={changed_pixel_ratio:.2%}'
                    ))
                else:
                    self.test_results.append((
                        'baseline_comparison',
                        False,
                        f'Different (no SSIM): mean_diff={pixel_diff_mean:.2f}, changed={changed_pixel_ratio:.2%}'
                    ))
        else:
            # Simple threshold-based comparison
            print("  (SSIM not available, using simple comparison)")
            if pixel_diff_mean < 10 and changed_pixel_ratio < 0.10:
                self.test_results.append((
                    'baseline_comparison',
                    True,
                    f'Similar: mean_diff={pixel_diff_mean:.2f}, changed={changed_pixel_ratio:.2%}'
                ))
            else:
                self.test_results.append((
                    'baseline_comparison',
                    False,
                    f'Different: mean_diff={pixel_diff_mean:.2f}, changed={changed_pixel_ratio:.2%}'
                ))

        # Save diff image for debugging
        diff_image_path = self.screenshot_path.replace('.png', '_diff.png')
        try:
            # Create a visual diff image
            diff_visual = np.clip(diff.sum(axis=2) * 5, 0, 255).astype(np.uint8)  # Amplify differences
            Image.fromarray(diff_visual).save(diff_image_path)
            print(f"  Diff image saved to: {diff_image_path}")
        except Exception as e:
            print(f"  Warning: Could not save diff image: {e}")

    def finish_tests(self):
        """Print test results and exit"""
        print("\n" + "="*60)
        print("VISUAL TEST RESULTS")
        print("="*60)

        all_passed = True
        for test_name, passed, message in self.test_results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: {test_name} - {message}")
            if not passed:
                all_passed = False

        print("="*60)

        if all_passed:
            print("All tests PASSED!")
            exit_code = 0
        else:
            print("Some tests FAILED!")
            exit_code = 1

        # Exit the application
        wx.CallLater(100, lambda: self.ExitMainLoop())
        wx.CallLater(200, lambda: sys.exit(exit_code))


def main():
    """Main entry point"""
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(script_dir, 'pytest_tests.profile')
    screenshot_path = os.path.join(script_dir, 'visual_test_screenshot.png')
    baseline_path = os.path.join(script_dir, 'visual_test_baseline.png')

    if not os.path.exists(profile_path):
        print(f"Error: Profile file not found: {profile_path}")
        print("Please run run_pytest_with_profiling.py first to generate the profile.")
        sys.exit(1)

    print(f"Starting visual test...")
    print(f"Profile: {profile_path}")
    print(f"Screenshot will be saved to: {screenshot_path}")
    print(f"Baseline reference: {baseline_path}")
    if not os.path.exists(baseline_path):
        print(f"  (No baseline exists yet - will be created on first run)")
    print()

    # Create and run the test app
    app = VisualTestApp(profile_path, screenshot_path, baseline_path)
    app.MainLoop()


if __name__ == '__main__':
    main()
