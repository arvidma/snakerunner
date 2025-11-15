# Snakerunner Integration Tests

This directory contains integration tests for snakerunner that verify the profile visualization system works correctly end-to-end.

## Overview

The integration test suite:
1. Downloads and uses pytest as a test subject
2. Runs pytest's own tests with cProfile profiling
3. Loads the generated profile into snakerunner
4. Verifies the profile data is correctly parsed and structured
5. (Optionally) Validates the visual rendering with screenshots

## Test Philosophy

**Why pytest?** Testing pytest's tests with profiling creates a realistic, complex profile with:
- Thousands of function calls (2,500+ function records)
- Deep call hierarchies
- Both Python standard library and third-party code
- Realistic execution patterns

This provides much better test coverage than synthetic test data.

## Files

- `setup_tests.sh` - Automated setup script (installs dependencies, clones pytest)
- `requirements.txt` - Python dependencies for integration tests
- `run_all_tests.sh` - Master script that runs the complete test suite
- `run_pytest_with_profiling.py` - Generates profile by running pytest tests (with auto-clone)
- `generate_sample_profile.py` - Fallback profile generator (no external deps needed)
- `create_placeholder_baseline.py` - Creates placeholder baseline image for visual regression testing
- `create_real_baseline.py` - Creates real baseline from existing snakerunner screenshot
- `test_profile_loading.py` - Tests profile loading without GUI (no wxPython needed)
- `test_visual_profile.py` - Tests GUI rendering (requires wxPython)
- `visual_test_baseline.png` - Baseline reference image (real snakerunner screenshot, 800x600)
- `pytest-repo/` - Cloned pytest repository (test subject, auto-cloned if missing)

## Quick Start (Recommended)

### Automated Setup

```bash
# One-command setup - installs all dependencies and clones pytest repo
./setup_tests.sh

# Then run all tests
./run_all_tests.sh
```

The setup script will:
- Install Python dependencies (pytest, wxPython, etc.)
- Clone pytest repository for realistic test data
- Check for system dependencies (Xvfb)

### Manual Setup

If you prefer manual setup:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Clone pytest repo (optional - fallback generator used if not present)
git clone --depth 1 --branch 8.0.0 https://github.com/pytest-dev/pytest.git pytest-repo

# Run tests
./run_all_tests.sh
```

## Running the Tests

### Run All Tests

```bash
./run_all_tests.sh
```

This runs all tests in sequence. The visual test is skipped if wxPython is not installed.

### Individual Tests

Run just the profile generation:
```bash
python3 run_pytest_with_profiling.py
```
**Note:** This will automatically clone pytest-repo if needed, or use the fallback generator if cloning fails.

Run just the loading test:
```bash
python3 test_profile_loading.py
```

Run the visual test (requires wxPython and X server):
```bash
xvfb-run -a python3 test_visual_profile.py
```

## Test Details

### Test 1: Profile Generation

**File:** `run_pytest_with_profiling.py`

- **Automatically clones pytest-repo** if not present (requires git)
- **Falls back to `generate_sample_profile.py`** if cloning fails
- Runs a subset of pytest's integration tests (if using pytest-repo)
- Uses Python's built-in cProfile
- Generates `pytest_tests.profile`
- Typical profile size: ~400KB, 2,500+ functions, 1-2 seconds execution time

**Fallback Generator:** `generate_sample_profile.py`

If pytest-repo cannot be cloned (no git, no network), the fallback generator creates a comprehensive profile by:
- Executing recursive algorithms (fibonacci)
- Simulating data processing with deep call hierarchies
- Performing file I/O operations
- JSON serialization/deserialization
- String and path operations
- Creating realistic nested call stacks

The fallback profile is smaller but still provides good test coverage for snakerunner's visualization.

### Test 2: Profile Loading

**File:** `test_profile_loading.py`

Tests without requiring wxPython:
1. ✓ Profile file loads successfully
2. ✓ Profile contains expected number of rows (2,500+)
3. ✓ Root node is created correctly
4. ✓ Cumulative time is calculated
5. ✓ Tree structure (parent/child relationships) is valid
6. ✓ Location view (directory hierarchy) is built
7. ✓ Sample data looks correct
8. ✓ pytest-related functions are present in profile

**Dependencies:** None (uses only stdlib and runsnakerun modules)

### Test 3: Visual Rendering (Optional)

**File:** `test_visual_profile.py`

Tests GUI rendering with wxPython:
1. Loads profile into full wxPython GUI
2. Captures screenshot of visualization
3. Validates rendering:
   - Screenshot is not blank
   - Has color variety (visualization has colors)
   - Squaremap area shows content
   - Profile data loaded correctly
   - Data structures initialized
4. **Baseline comparison** (regression detection):
   - Compares against reference image (`visual_test_baseline.png`)
   - Calculates SSIM (Structural Similarity Index) - measures perceptual similarity
   - Calculates pixel difference metrics (mean, max, changed ratio)
   - Creates visual diff image highlighting changes
   - On first run, creates baseline for future comparisons

**Baseline Comparison Metrics:**
- **SSIM Score**: 0.90-1.00 = Very similar, 0.80-0.90 = Similar with changes, <0.80 = Significant difference
- **Mean Pixel Diff**: Average color difference per pixel (lower is better)
- **Changed Pixels**: Percentage of pixels with >10 unit difference in any channel
- **Diff Image**: Visual representation showing where changes occurred (amplified 5x for visibility)

**Dependencies:** wxPython, Pillow, scikit-image (for SSIM), numpy, Xvfb (for headless)

**Output Files:**
- `visual_test_screenshot.png` - Current screenshot (gitignored)
- `visual_test_baseline.png` - Reference baseline (committed to git)
- `visual_test_screenshot_diff.png` - Visual diff highlighting changes (gitignored)

## Requirements

### Minimal (for basic tests)
- Python 3.11+
- pytest==8.0.0 (installed automatically)

### Full (for visual tests with baseline comparison)
- wxPython 4.2.2+
- Pillow
- scikit-image (for SSIM calculation)
- numpy
- Xvfb (for headless GUI testing)

## Expected Output

Successful test run:
```
========================================
Snakerunner Integration Test Suite
========================================

[1/2] Generating profile from pytest tests...
----------------------------------------
Profiling pytest tests...
Profile saved to: pytest_tests.profile

[2/2] Testing profile loading...
----------------------------------------
Test 1: Loading profile...
✓ PASS: Profile loaded successfully

Test 2: Checking profile data...
✓ PASS: Loaded 2936 profile rows

...

All tests PASSED!

Profile statistics:
  - Total function records: 2936
  - Total execution time: 1.554s
  - Direct children of root: 2
  - Location hierarchy items: 22
```

## How It Works

### Profile Generation Flow

```
pytest-repo/testing/*.py
    ↓ (run with cProfile)
pytest_tests.profile
    ↓ (load with pstats)
PStatsLoader
    ↓ (parse and build tree)
Profile Tree Structure
```

### Visual Validation Flow

```
pytest_tests.profile
    ↓
SnakeRunner MainFrame
    ↓ (render with wxPython)
Squaremap Visualization
    ↓ (capture screenshot)
visual_test_screenshot.png
    ↓ (analyze pixels)
Visual Validation Results
```

## Design Decisions

1. **Why pytest as test subject?**
   - Well-known, stable codebase
   - Complex enough to generate interesting profiles
   - Self-contained (tests its own tests)
   - Predictable structure

2. **Why separate GUI and non-GUI tests?**
   - Non-GUI tests can run anywhere (CI/CD friendly)
   - GUI tests require display server (heavier dependencies)
   - Profile loading is core functionality, rendering is presentation

3. **Why fuzzy visual validation?**
   - Exact pixel matching is fragile
   - We care about "is there content?" not "is this pixel #FF0000?"
   - Statistical validation (color variety, non-blank ratio) is robust

## Troubleshooting

**Profile generation fails:**
- Check that pytest is installed: `pip install pytest==8.0.0`
- Some pytest tests may fail - this is OK, profile is still generated

**Visual test fails:**
- Ensure wxPython is installed (complex, may need system libraries)
- Ensure Xvfb is available: `which xvfb-run`
- Visual test is optional - core functionality tested without it

**Integration test takes too long:**
- Reduce test scope in `run_pytest_with_profiling.py`
- Adjust `-k` filter to run fewer tests
- Profile generation is the slowest part

**Baseline image management:**
- **Real baseline included**: The repo includes a real baseline created from the project's screenshot.png
- **Baseline shows**: Actual snakerunner squaremap visualization with real profile data (psycopg2 profiling)
- **Update baseline**: Run `python3 create_real_baseline.py` to recreate from screenshot.png, or run visual tests with wxPython to capture fresh baseline
- **Compare manually**: Use image diff tools to compare baseline vs screenshot
- **Diff too sensitive**: Adjust thresholds in `compare_with_baseline()` method
- **Environment differences**: Different OS/wxPython versions may produce different rendering - the SSIM threshold (0.90) accounts for this

**Note**: The included baseline was created from the repository's existing screenshot.png (macOS Mojave with Python 3.7). Visual tests on different environments may show variations in font rendering, colors, or layout - this is expected and accounted for in the comparison thresholds.

**Understanding baseline comparison results:**
- SSIM = 1.0: Identical images
- SSIM > 0.95: Visually identical (minor antialiasing differences)
- SSIM 0.90-0.95: Very similar (acceptable variation)
- SSIM 0.80-0.90: Similar but with noticeable changes
- SSIM < 0.80: Significant visual differences (likely a regression)

## Creating and Updating Baseline Images

The repository includes a real baseline image created from the project's existing screenshot.png.

### Option 1: Recreate from screenshot.png (Recommended)

```bash
# Uses the existing screenshot.png from the repo
python3 create_real_baseline.py
```

This is useful if screenshot.png is updated or if you want to regenerate the baseline at a different size.

### Option 2: Capture from live visual test (Requires wxPython)

```bash
# 1. Install wxPython (may require system libraries)
pip install wxPython

# 2. Run visual tests to capture a fresh screenshot
xvfb-run -a python3 test_visual_profile.py

# 3. If satisfied with the screenshot, commit it as new baseline
git add visual_test_baseline.png
git commit -m "Update visual test baseline for [your environment]"
```

### Understanding Environment Differences

Different environments produce slightly different rendering:
- **Font rendering**: Varies between Linux, macOS, Windows
- **Color management**: Different display profiles affect colors
- **wxPython versions**: UI element styling changes between versions
- **Window manager**: Different compositing and antialiasing

The SSIM threshold (0.90) is set to tolerate these minor differences while still catching genuine visual regressions.

## Future Improvements

- [ ] Add performance benchmarks (load time, memory usage)
- [ ] Test with different profile sizes (small, medium, large)
- [ ] Test edge cases (empty profile, single function, circular calls)
- [x] Automated visual regression testing with baseline screenshots (DONE)
- [x] Placeholder baseline image for initial setup (DONE)
- [ ] Test multiple Python versions
- [ ] Add stress tests with very large profiles (100K+ functions)
- [ ] Add command-line flag to force baseline update
- [ ] Generate HTML report with side-by-side baseline/current/diff images
- [ ] Support multiple baseline images for different environments (Linux/macOS/Windows)

## Contributing

To add new tests:
1. Create test script in this directory
2. Add to `run_all_tests.sh`
3. Update this README
4. Ensure tests are self-contained and repeatable

## License

Same as parent project (BSD).
