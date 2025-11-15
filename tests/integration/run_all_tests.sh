#!/bin/bash
#
# Master test script for snakerunner integration tests
#
# This script runs the complete integration test suite:
# 1. Generates a profile by running pytest's own tests with cProfile
# 2. Tests that the profile can be loaded and parsed correctly
# 3. (Optional) Tests visual rendering with wxPython if available
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Snakerunner Integration Test Suite"
echo "========================================"
echo ""

# Step 1: Generate profile
echo "[1/2] Generating profile from pytest tests..."
echo "----------------------------------------"
python3 run_pytest_with_profiling.py
echo ""

# Step 2: Test profile loading
echo "[2/2] Testing profile loading..."
echo "----------------------------------------"
python3 test_profile_loading.py
TEST_EXIT_CODE=$?
echo ""

# Optional: Visual test (requires wxPython)
if python3 -c "import wx" 2>/dev/null; then
    echo "[BONUS] Running visual test with wxPython..."
    echo "----------------------------------------"
    xvfb-run -a python3 test_visual_profile.py || echo "Visual test failed (this is optional)"
    echo ""
else
    echo "[SKIP] Visual test requires wxPython (not installed)"
    echo ""
fi

# Summary
echo "========================================"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✓ ALL TESTS PASSED!"
else
    echo "✗ SOME TESTS FAILED"
fi
echo "========================================"
echo ""
echo "Generated files:"
echo "  - pytest_tests.profile              (cProfile output)"
echo "  - visual_test_screenshot.png        (current screenshot, if visual test ran)"
echo "  - visual_test_baseline.png          (baseline reference, created on first run)"
echo "  - visual_test_screenshot_diff.png   (visual diff, if baseline exists)"
echo ""

exit $TEST_EXIT_CODE
