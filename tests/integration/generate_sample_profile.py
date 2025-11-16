#!/usr/bin/env python3
"""
Fallback profile generator that creates realistic profiling data without external dependencies.

This script generates a comprehensive profile by executing various computational tasks
that create a realistic call tree suitable for testing snakerunner.
"""
import cProfile
import time
import os
import sys
import hashlib
import json
from pathlib import Path


def fibonacci(n):
    """Recursive fibonacci - creates deep call stacks"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def process_data(items, depth=0):
    """Simulates data processing with varying call depths"""
    if depth > 5:
        return [sum(items)]

    results = []
    for item in items:
        # Add some computation
        result = analyze_item(item)
        result = transform_item(result, depth)
        results.append(result)

    if depth < 3:
        deeper_results = process_data(results[:5], depth + 1)
        results.extend(deeper_results)

    return results


def analyze_item(item):
    """Analyzes an item - simulates work"""
    # Some string operations
    str_item = str(item)
    hash_val = hashlib.md5(str_item.encode()).hexdigest()
    return len(hash_val) + item


def transform_item(item, depth):
    """Transforms an item based on depth"""
    if depth % 2 == 0:
        return item * 2
    else:
        return item + depth


def file_operations():
    """Simulates file I/O operations"""
    temp_file = "/tmp/snakerunner_test_profile_data.txt"

    # Write operations
    with open(temp_file, 'w') as f:
        for i in range(100):
            f.write(f"Line {i}: " + "x" * 100 + "\n")

    # Read operations
    with open(temp_file, 'r') as f:
        lines = f.readlines()
        process_lines(lines)

    # Cleanup
    os.unlink(temp_file)


def process_lines(lines):
    """Process text lines"""
    results = []
    for line in lines:
        results.append(parse_line(line))
    return results


def parse_line(line):
    """Parse a single line"""
    return len(line.strip())


def json_operations():
    """Simulates JSON serialization/deserialization"""
    data = {
        'users': [
            {'id': i, 'name': f'User{i}', 'score': i * 10}
            for i in range(100)
        ],
        'metadata': {
            'version': '1.0',
            'timestamp': time.time()
        }
    }

    # Serialize
    json_str = json.dumps(data, indent=2)

    # Deserialize
    loaded = json.loads(json_str)

    # Process
    return sum(user['score'] for user in loaded['users'])


def path_operations():
    """Simulates path operations"""
    paths = [f"/usr/lib/python3/site-packages/module{i}" for i in range(50)]

    results = []
    for path_str in paths:
        p = Path(path_str)
        results.append(len(p.parts))
        results.append(len(p.name))
        results.append(process_path(p))

    return sum(results)


def process_path(path):
    """Process a path object"""
    return len(str(path))


def string_operations():
    """Simulates string processing"""
    text = "The quick brown fox jumps over the lazy dog" * 100

    results = []
    results.append(text.upper())
    results.append(text.lower())
    results.append(text.replace('fox', 'cat'))
    results.append(''.join(reversed(text)))

    # Split and join
    words = text.split()
    results.append(' '.join(sorted(words)))

    return len(''.join(results))


def nested_calls_level_1():
    """Creates nested call hierarchy"""
    result = 0
    for i in range(10):
        result += nested_calls_level_2(i)
    return result


def nested_calls_level_2(n):
    """Level 2 nested calls"""
    result = 0
    for i in range(5):
        result += nested_calls_level_3(n, i)
    return result


def nested_calls_level_3(a, b):
    """Level 3 nested calls"""
    result = 0
    for i in range(3):
        result += nested_calls_level_4(a, b, i)
    return result


def nested_calls_level_4(a, b, c):
    """Level 4 nested calls (deepest)"""
    return (a * b * c) % 1000


def main_workload():
    """
    Main workload that exercises various code paths.
    This creates a realistic profile with:
    - Deep call hierarchies
    - Varied execution times
    - Different types of operations
    """
    print("Generating comprehensive profile...")

    results = []

    # Phase 1: Recursive computations
    print("  Phase 1/7: Recursive computations...")
    for i in range(5, 15):
        results.append(fibonacci(i))

    # Phase 2: Data processing
    print("  Phase 2/7: Data processing...")
    test_data = list(range(100))
    results.append(sum(process_data(test_data)))

    # Phase 3: File operations
    print("  Phase 3/7: File I/O...")
    file_operations()

    # Phase 4: JSON operations
    print("  Phase 4/7: JSON serialization...")
    results.append(json_operations())

    # Phase 5: Path operations
    print("  Phase 5/7: Path operations...")
    results.append(path_operations())

    # Phase 6: String operations
    print("  Phase 6/7: String processing...")
    results.append(string_operations())

    # Phase 7: Nested calls
    print("  Phase 7/7: Nested call hierarchies...")
    results.append(nested_calls_level_1())

    print("Profile generation complete!")
    return sum(results)


if __name__ == '__main__':
    output_file = os.path.join(os.path.dirname(__file__), 'pytest_tests.profile')

    print("=" * 60)
    print("Fallback Profile Generator")
    print("=" * 60)
    print(f"Output: {output_file}")
    print("")

    # Create profiler
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        result = main_workload()
        print(f"\nWorkload result: {result}")
    finally:
        profiler.disable()
        profiler.dump_stats(output_file)

    print(f"\n✓ Profile saved to: {output_file}")
    print(f"  You can view it with: python -m runsnakerun {output_file}")
    print("")

    # Print stats
    import pstats
    stats = pstats.Stats(output_file)
    print("Profile statistics:")
    print(f"  Total function calls: {stats.total_calls}")
    print("")
