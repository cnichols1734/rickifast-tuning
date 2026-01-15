#!/usr/bin/env python3
"""
Test runner script for the Aqua Force CRM application.

This script provides a convenient way to run the integration tests
for the clients route and other parts of the application.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py tests/test_clients_integration.py  # Run specific test file
    python run_tests.py -k test_create     # Run tests matching pattern
"""

import sys
import subprocess
import os


def main():
    """Run pytest with the provided arguments."""
    # Ensure we're in the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Build the pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add any additional arguments passed to this script
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    else:
        # Default: run all tests with coverage
        cmd.extend(['--cov=app', '--cov-report=term-missing'])
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Execute pytest
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 