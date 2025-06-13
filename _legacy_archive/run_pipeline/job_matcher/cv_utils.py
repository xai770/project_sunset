#!/usr/bin/env python3
"""
CV Utilities module for job matching.

This module contains utility functions for working with CV data.
"""
import os
from pathlib import Path
import sys

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

def get_cv_markdown_text():
    """
    Get the CV text from the Markdown file.
    
    Returns:
        The CV text as a string
        
    Raises:
        FileNotFoundError: If the CV file does not exist
    """
    cv_path = os.path.join(PROJECT_ROOT, "profile", "cv", "Gershons_concise_cv.md")
    try:
        with open(cv_path, "r", encoding="utf-8") as cf:
            return cf.read()
    except FileNotFoundError:
        print(f"CV file not found at {cv_path}")
        sys.exit(1)
