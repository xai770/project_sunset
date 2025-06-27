#!/usr/bin/env python3
"""
Version definitions for staged job processor components.
These versions are used to track when components have been updated,
allowing the pipeline to determine if jobs need reprocessing.
"""

# Module versions
# Use semantic versioning: MAJOR.MINOR.PATCH
# MAJOR: breaking changes
# MINOR: new features, backward compatible
# PATCH: bug fixes, backward compatible
HTML_CLEANER_VERSION = "1.0.0"  # Initial version
LANGUAGE_HANDLER_VERSION = "1.0.0"  # Initial version
EXTRACTORS_VERSION = "1.0.0"  # Initial version
FILE_HANDLER_VERSION = "1.0.0"  # Initial version
PROCESSOR_VERSION = "1.0.0"  # Initial version

# Overall staged processor package version
# This should be incremented when ANY component is updated
STAGED_PROCESSOR_VERSION = "1.0.0"  # Initial version

# Module dependencies
# These define the ripple effect - if a module is updated, 
# which subsequent modules should be rerun
MODULE_DEPENDENCIES = {
    "html_cleaner": ["language_handler", "extractors", "file_handler"],
    "language_handler": ["extractors", "file_handler"],
    "extractors": ["file_handler"],
    "file_handler": [],
    "processor": ["html_cleaner", "language_handler", "extractors", "file_handler"]
}