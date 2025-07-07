#!/usr/bin/env python3
"""
Skills module for the job expansion pipeline (refactored)

This module orchestrates skill extraction, decomposition, categorization, and importance analysis for job postings.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Import paths
from run_pipeline.config.paths import (
    PROJECT_ROOT,
    JOB_DATA_DIR,
    LOG_BASE_DIR,
    SKILL_DATA_DIR,
    SKILL_DECOMPOSITIONS_FILE,
    ELEMENTARY_SKILLS_FILE,
    SEMANTIC_CACHE_FILE,
    DEFAULT_SIMILARITY_THRESHOLD
)

# Import submodules
from run_pipeline.core.skills_io import process_skills

logger = logging.getLogger('skills_module')

if __name__ == "__main__":
    # Set up basic logging if run directly
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process job skills")
    parser.add_argument("--max-jobs", type=int, help="Maximum number of jobs to process")
    parser.add_argument("--job-ids", type=str, help="Specific job IDs to process (comma-separated)")
    args = parser.parse_args()
    
    # Process job IDs if provided
    job_ids = None
    if args.job_ids:
        job_ids = [job_id.strip() for job_id in args.job_ids.split(",") if job_id.strip()]
    
    # Run the skills processor
    success = process_skills(
        max_jobs=args.max_jobs,
        job_ids=job_ids
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
