#!/usr/bin/env python3
"""
CV Loader utility module for job matching.

This module contains utilities for loading the CV text from various possible
locations to ensure consistent CV handling across the pipeline.
"""
import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

def load_cv_text():
    """
    Load CV text from the config directory.
    
    Returns:
        str: The CV text from config/cv.txt
        
    Raises:
        FileNotFoundError: If the CV file is not found
    """
    # The CV should be located in the config directory
    cv_path = os.path.join(PROJECT_ROOT, "config", "cv.txt")
    
    if os.path.exists(cv_path):
        print(f"Loading CV from: {cv_path}")
        with open(cv_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # If CV not found, raise an error
    raise FileNotFoundError(f"CV file not found at expected location: {cv_path}")

if __name__ == "__main__":
    # Test the CV loader
    cv_text = load_cv_text()
    print(f"CV text loaded ({len(cv_text)} characters)")
    print(cv_text[:200] + "..." if len(cv_text) > 200 else cv_text)
