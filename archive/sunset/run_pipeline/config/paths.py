#!/usr/bin/env python3
"""
Configuration module for the job expansion pipeline
"""

import os
from pathlib import Path

# Determine the project root directory
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Directory paths
JOB_DATA_DIR = PROJECT_ROOT / "data" / "postings"  # Single source of truth for job files

LOG_BASE_DIR = PROJECT_ROOT / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SKILL_DATA_DIR = PROJECT_ROOT / "skills" / "data"

# Subprocess timeout values
DEFAULT_TIMEOUT = 60  # seconds
FIREFOX_TIMEOUT = 30  # seconds

# Default values
DEFAULT_MAX_JOBS = 500
DEFAULT_MODEL = "llama3.2:latest"
DEFAULT_SIMILARITY_THRESHOLD = 0.75  # For skill matching

# Skill file paths
SKILL_DECOMPOSITIONS_FILE = SKILL_DATA_DIR / "skill_decompositions.json"
ELEMENTARY_SKILLS_FILE = SKILL_DATA_DIR / "elementary_skills.json"
SEMANTIC_CACHE_FILE = SKILL_DATA_DIR / "semantic_cache.json"

# Note: All functionality is now directly in core modules:
# - fetch_module.py for fetching job metadata
# - scraper_module.py for scraping job details
# - cleaner_module.py for cleaning job descriptions

# Ensure all necessary directories exist
def ensure_directories():
    """Ensure all necessary directories exist"""
    JOB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_BASE_DIR.mkdir(parents=True, exist_ok=True)
    SKILL_DATA_DIR.mkdir(parents=True, exist_ok=True)
