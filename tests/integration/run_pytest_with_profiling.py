#!/usr/bin/env python3
"""
Run pytest's own tests with cProfile to generate a profile for testing snakerunner.

This script runs a subset of pytest's integration tests with profiling enabled,
creating a realistic profile that can be visualized with snakerunner.

If pytest-repo is not available, it will automatically use the fallback generator.
"""
import cProfile
import sys
import os
import subprocess

def clone_pytest_repo():
    """Clone pytest repository if not present"""
    pytest_repo = os.path.join(os.path.dirname(__file__), 'pytest-repo')

    if os.path.exists(pytest_repo):
        print(f"✓ pytest-repo already exists")
        return True

    print("pytest-repo not found. Attempting to clone...")
    try:
        subprocess.run([
            'git', 'clone',
            '--depth', '1',
            '--branch', '8.0.0',
            'https://github.com/pytest-dev/pytest.git',
            pytest_repo
        ], check=True, capture_output=True, text=True)
        print(f"✓ pytest repository cloned successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to clone pytest repo: {e}")
        print(f"  Will use fallback profile generator instead")
        return False
    except FileNotFoundError:
        print("✗ git command not found")
        print(f"  Will use fallback profile generator instead")
        return False

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
        print(f"No test files found in {pytest_repo}")
        print(f"Files checked: {test_files}")
        return 1

    print(f"Running pytest tests from: {pytest_repo}")
    print(f"Test files: {len(existing_tests)}")

    # Run pytest with minimal output, limit to first few tests for speed
    return pytest.main([
        '-v',  # verbose
        '--tb=short',  # shorter traceback format
        '-k', 'test_config or test_assertion',  # filter to specific test patterns
        '--maxfail=20',  # stop after 20 failures
        *existing_tests
    ])

def run_fallback_generator():
    """Run the fallback profile generator"""
    print("Using fallback profile generator...")
    script_path = os.path.join(os.path.dirname(__file__), 'generate_sample_profile.py')

    if not os.path.exists(script_path):
        print(f"Error: Fallback generator not found at {script_path}")
        return 1

    # Execute the fallback generator
    result = subprocess.run([sys.executable, script_path], check=False)
    return result.returncode

if __name__ == '__main__':
    output_file = os.path.join(os.path.dirname(__file__), 'pytest_tests.profile')

    print("=" * 60)
    print("Profile Generation for Snakerunner Tests")
    print("=" * 60)
    print(f"Output will be saved to: {output_file}")
    print("")

    # Try to use pytest repo, fallback to sample generator if not available
    use_pytest = clone_pytest_repo()

    if use_pytest:
        print("\nProfiling pytest tests...")
        profiler = cProfile.Profile()
        profiler.enable()

        try:
            exit_code = run_pytest_tests()
        finally:
            profiler.disable()
            profiler.dump_stats(output_file)
            print(f"\n✓ Profile saved to: {output_file}")
            print(f"  You can view it with: python -m runsnakerun {output_file}")

        # Always exit successfully - we just need the profile, not passing tests
        # The profile is generated even if some tests fail
        if exit_code != 0:
            print(f"\nNote: pytest exit code was {exit_code}, but profile was generated successfully")

    else:
        # Use fallback generator
        print("")
        exit_code = run_fallback_generator()

        if exit_code != 0:
            print(f"\n✗ Fallback generator failed with exit code {exit_code}")
            sys.exit(1)

    # Verify profile was created
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"\n✓ Profile file created: {file_size:,} bytes")
        print("")
        sys.exit(0)
    else:
        print(f"\n✗ Error: Profile file was not created")
        sys.exit(1)
