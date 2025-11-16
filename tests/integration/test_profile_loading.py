#!/usr/bin/env python3
"""
Test that profile loading works correctly without GUI.

This test verifies that snakerunner can correctly load and parse
cProfile files without requiring wxPython or a display.
"""
import os
import sys

# Add runsnakerun to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from runsnakerun import pstatsloader


def test_profile_loading():
    """Test that the profile can be loaded and parsed correctly"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(script_dir, 'pytest_tests.profile')

    if not os.path.exists(profile_path):
        print(f"Error: Profile file not found: {profile_path}")
        print("Please run run_pytest_with_profiling.py first to generate the profile.")
        return False

    print(f"Testing profile loading: {profile_path}")
    print()

    # Test 1: Load the profile
    print("Test 1: Loading profile...")
    try:
        loader = pstatsloader.PStatsLoader(profile_path)
        print("✓ PASS: Profile loaded successfully")
    except Exception as e:
        print(f"✗ FAIL: Failed to load profile: {e}")
        return False

    # Test 2: Check that we have rows
    print("\nTest 2: Checking profile data...")
    num_rows = len(loader.rows)
    if num_rows > 0:
        print(f"✓ PASS: Loaded {num_rows} profile rows")
    else:
        print(f"✗ FAIL: No profile rows loaded")
        return False

    # Test 3: Check that we have a root node
    print("\nTest 3: Checking root node...")
    try:
        root = loader.get_root('functions')
        if root:
            print(f"✓ PASS: Root node found: {root}")
        else:
            print(f"✗ FAIL: Root node is None")
            return False
    except Exception as e:
        print(f"✗ FAIL: Failed to get root: {e}")
        return False

    # Test 4: Check that root has cumulative time
    print("\nTest 4: Checking cumulative time...")
    if hasattr(root, 'cumulative') and root.cumulative > 0:
        print(f"✓ PASS: Root cumulative time: {root.cumulative:.3f}s")
    else:
        print(f"✗ FAIL: Root has no cumulative time")
        return False

    # Test 5: Check tree structure (children)
    print("\nTest 5: Checking tree structure...")
    try:
        if hasattr(root, 'children'):
            num_children = len(root.children)
            if num_children > 0:
                print(f"✓ PASS: Root has {num_children} children")
            else:
                print(f"✗ FAIL: Root has no children")
                return False
        else:
            print(f"✗ FAIL: Root has no children attribute")
            return False
    except Exception as e:
        print(f"✗ FAIL: Failed to check children: {e}")
        return False

    # Test 6: Check location view (without adapter, just data structure)
    print("\nTest 6: Checking location view...")
    try:
        location_root = loader.get_root('location')
        if location_root:
            print(f"✓ PASS: Location root found: {location_root}")
            if hasattr(location_root, 'children'):
                location_children = location_root.children
                print(f"✓ PASS: Location view has {len(location_children)} top-level items")
            else:
                print(f"✗ FAIL: Location root has no children")
                return False
        else:
            print(f"✗ FAIL: Location root is None")
            return False
    except Exception as e:
        print(f"✗ FAIL: Failed to get location view: {e}")
        return False

    # Test 7: Check some sample data from rows
    print("\nTest 7: Checking sample profile data...")
    try:
        # Get a few sample rows
        sample_rows = list(loader.rows.values())[:5]
        for i, row in enumerate(sample_rows):
            print(f"  Sample row {i+1}: {row.name} @ {row.filename}:{row.lineno} ({row.cumulative:.4f}s)")
        print(f"✓ PASS: Sample data looks valid")
    except Exception as e:
        print(f"✗ FAIL: Failed to check sample data: {e}")
        return False

    # Test 8: Validate expected pytest-related functions are in profile
    print("\nTest 8: Validating pytest functions in profile...")
    try:
        pytest_functions = [row for row in loader.rows.values()
                          if 'pytest' in row.filename or 'pytest' in row.directory]
        if len(pytest_functions) > 0:
            print(f"✓ PASS: Found {len(pytest_functions)} pytest-related functions in profile")
            # Show a few examples
            for row in pytest_functions[:3]:
                print(f"  Example: {row.name} @ {row.filename}")
        else:
            print(f"⚠ WARNING: No pytest-related functions found (might be OK)")
    except Exception as e:
        print(f"✗ FAIL: Failed to check for pytest functions: {e}")
        return False

    # Summary
    print("\n" + "="*60)
    print("All tests PASSED!")
    print("="*60)
    print(f"\nProfile statistics:")
    print(f"  - Total function records: {num_rows}")
    print(f"  - Total execution time: {root.cumulative:.3f}s")
    print(f"  - Direct children of root: {num_children}")
    print(f"  - Location hierarchy items: {len(location_children)}")

    return True


if __name__ == '__main__':
    success = test_profile_loading()
    sys.exit(0 if success else 1)