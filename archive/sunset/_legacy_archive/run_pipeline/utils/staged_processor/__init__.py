#!/usr/bin/env python3
"""
Staged Job Description Processing Package

This package processes job descriptions in stages:
1. Clean HTML formatting
2. Handle language (remove German if English exists, or translate)
3. Extract and format job details using LLM

The package is split into logical modules:
- processor.py: Main processor class and job processing functions
- html_cleaner.py: HTML cleaning functionality
- language_handler.py: Language detection and translation
- extractors.py: Text extraction and structured format conversion
- file_handler.py: File loading and saving utilities
- utils.py: Common utilities and helper functions
"""

# Setup package-level logger
import logging
logger = logging.getLogger('staged_job_processor')

# Define version
__version__ = "1.0.0"

# Import StagedJobProcessor and process_jobs lazily for backward compatibility
# while avoiding circular imports on module initialization
from importlib import import_module

def __getattr__(name):
    """
    Lazily import attributes to avoid circular imports.
    This function is called when an attribute is accessed that doesn't exist in this module.
    """
    if name in ["StagedJobProcessor", "process_jobs"]:
        # Only import from processor when these specific attributes are requested
        processor_module = import_module("run_pipeline.utils.staged_processor.processor")
        return getattr(processor_module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
