#!/usr/bin/env python3
"""
Run pytest's own tests with cProfile to generate a profile for testing snakerunner.

This script runs a subset of pytest's integration tests with profiling enabled,
creating a realistic profile that can be visualized with snakerunner.
"""
import cProfile
import sys
import os

def run_pytest_tests():
    """Run pytest's own tests with a subset of test files"""
    import pytest

    # Select a few test files that have good integration tests from the pytest repo
    # These should be fast enough but generate interesting profiles
    test_files = [
        'testing/test_config.py',
        'testing/test_assertion.py',
        'testing/test_collection.py',
    ]

    pytest_repo = os.path.join(os.path.dirname(__file__), 'pytest-repo')
    test_paths = [os.path.join(pytest_repo, tf) for tf in test_files]

    # Filter to only existing files
    existing_tests = [tp for tp in test_paths if os.path.exists(tp)]

    if not existing_tests:
        print(f"No test files found. Looked in: {pytest_repo}")
        print(f"Files checked: {test_files}")
        return 1

    print(f"Running pytest tests: {existing_tests}")

    # Run pytest with minimal output, limit to first few tests for speed
    return pytest.main([
        '-v',  # verbose
        '--tb=short',  # shorter traceback format
        '-k', 'test_config or test_assertion',  # filter to specific test patterns
        '--maxfail=20',  # stop after 20 failures
        *existing_tests
    ])

if __name__ == '__main__':
    output_file = os.path.join(os.path.dirname(__file__), 'pytest_tests.profile')

    print(f"Profiling pytest tests...")
    print(f"Output will be saved to: {output_file}")

    profiler = cProfile.Profile()
    profiler.enable()

    try:
        exit_code = run_pytest_tests()
    finally:
        profiler.disable()
        profiler.dump_stats(output_file)
        print(f"\nProfile saved to: {output_file}")
        print(f"You can view it with: python -m runsnakerun {output_file}")

    # Always exit successfully - we just need the profile, not passing tests
    # The profile is generated even if some tests fail
    print(f"\nNote: Test exit code was {exit_code}, but profile was generated successfully")
    sys.exit(0)
