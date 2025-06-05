#!/usr/bin/env python3
"""
Wrapper script for backward compatibility with the original test_llama32.py.

This script imports and runs the refactored job matcher CLI to maintain
backward compatibility with existing workflows that use test_llama32.py.
"""
import sys
import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the refactored CLI module
try:
    from job_matcher.cli import main
except ImportError as e:
    print(f"Error importing job matcher CLI: {e}")
    print("Make sure the job_matcher package is correctly installed")
    sys.exit(1)

if __name__ == "__main__":
    # Maintain backward compatibility by running the new CLI
    sys.exit(main())
