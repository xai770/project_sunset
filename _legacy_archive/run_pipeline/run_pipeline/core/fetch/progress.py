#!/usr/bin/env python3
"""
Progress tracking functions for the fetch module.
Contains functions for loading, saving, and managing progress.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from run_pipeline.config.paths import PROJECT_ROOT

logger = logging.getLogger('fetch_module.progress')

# Progress tracking file
PROGRESS_FILE = PROJECT_ROOT / "data" / "job_scans" / "search_api_scan_progress.json"

def ensure_directories():
    """Ensure all required directories exist."""
    from run_pipeline.config.paths import JOB_DATA_DIR
    
    JOB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "data" / "job_scans").mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured necessary directories exist in {PROJECT_ROOT / 'data'}")


def load_progress(force_clear=False):
    """
    Load progress from file if it exists.
    
    Args:
        force_clear (bool): If True, clear job history but keep stats
        
    Returns:
        dict: Progress data
    """
    progress_data = {
        "last_page_fetched": 0,
        "jobs_processed": [],
        "timestamp": datetime.now().isoformat(),
        "stats": {
            "total_jobs_found": 0,
            "total_jobs_processed": 0,
            "total_pages_fetched": 0
        }
    }
    
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r') as f:
                loaded_data = json.load(f)
                
                # Always reset last_page_fetched since we always start from page 1
                loaded_data["last_page_fetched"] = 0
                
                # If force_clear is True, reset jobs_processed list
                if force_clear:
                    loaded_data["jobs_processed"] = []
                    logger.info("Forced reset of job processing history")
                
                return loaded_data
                
        except Exception as e:
            logger.error(f"Error loading progress file: {e}")
    
    # Return default progress data
    return progress_data


def save_progress(progress_data):
    """
    Save progress to file.
    
    Args:
        progress_data (dict): Progress data to save
    """
    # Update timestamp
    progress_data["timestamp"] = datetime.now().isoformat()
    
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress_data, f, indent=2)
        logger.debug("Progress saved successfully")
    except Exception as e:
        logger.error(f"Error saving progress file: {e}")
        
        
def update_progress_stats(progress_data, new_jobs_count, new_pages_count=1):
    """
    Update progress statistics.
    
    Args:
        progress_data (dict): Progress data to update
        new_jobs_count (int): Number of new jobs found
        new_pages_count (int): Number of new pages fetched
    
    Returns:
        dict: Updated progress data
    """
    progress_data["stats"]["total_jobs_found"] += new_jobs_count
    progress_data["stats"]["total_jobs_processed"] += new_jobs_count
    progress_data["stats"]["total_pages_fetched"] += new_pages_count
    
    return progress_data
