#!/bin/bash
#
# Setup script for snakerunner integration tests
#
# This script:
# 1. Installs required Python dependencies
# 2. Clones pytest repository for test data generation
# 3. Installs system dependencies (Xvfb) if needed
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Snakerunner Test Setup"
echo "========================================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python version: $PYTHON_VERSION"

# Install Python dependencies
echo ""
echo "[1/3] Installing Python dependencies..."
echo "----------------------------------------"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Python dependencies installed"
else
    echo "Warning: requirements.txt not found"
fi

# Clone pytest repository if not exists
echo ""
echo "[2/3] Setting up pytest repository..."
echo "----------------------------------------"
PYTEST_REPO="pytest-repo"

if [ -d "$PYTEST_REPO" ]; then
    echo "✓ pytest-repo already exists"
else
    echo "Cloning pytest repository (this may take a minute)..."
    git clone --depth 1 --branch 8.0.0 https://github.com/pytest-dev/pytest.git "$PYTEST_REPO"
    echo "✓ pytest repository cloned"
fi

# Check for Xvfb (needed for headless GUI testing)
echo ""
echo "[3/3] Checking system dependencies..."
echo "----------------------------------------"
if command -v xvfb-run &> /dev/null; then
    echo "✓ xvfb-run is available"
else
    echo "⚠ xvfb-run not found (needed for headless GUI testing)"
    echo "  To install on Debian/Ubuntu: sudo apt-get install xvfb"
    echo "  To install on Fedora/RHEL: sudo dnf install xorg-x11-server-Xvfb"
    echo "  To install on macOS: not needed (use native display)"
fi

# Check if wxPython installed correctly
echo ""
echo "Verifying wxPython installation..."
if python3 -c "import wx" 2>/dev/null; then
    echo "✓ wxPython is working"
else
    echo "⚠ wxPython import failed"
    echo "  wxPython can be difficult to install. Try:"
    echo "  - pip install wxPython"
    echo "  - Or see: https://wxpython.org/pages/downloads/"
fi

echo ""
echo "========================================"
echo "✓ Setup complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Run all tests: ./run_all_tests.sh"
echo "  2. Or run individual tests:"
echo "     - python3 run_pytest_with_profiling.py"
echo "     - python3 test_profile_loading.py"
echo "     - xvfb-run -a python3 test_visual_profile.py"
echo ""
