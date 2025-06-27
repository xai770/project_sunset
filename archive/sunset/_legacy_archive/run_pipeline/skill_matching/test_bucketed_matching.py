#!/usr/bin/env python3
"""
Test script for bucketed skill matching implementation

This script runs the bucketed skill matcher on a specific job ID
and displays the results to verify functionality.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucketed_test")

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import required modules
try:
    from run_pipeline.skill_matching.bucketed_pipeline import run_bucketed_skill_matcher
    from run_pipeline.config.paths import JOB_DATA_DIR
except ImportError:
    logger.error("Failed to import required modules")
    sys.exit(1)

def test_bucketed_matching(job_id: int, max_workers: int = 4):
    """
    Test bucketed skill matching on a specific job
    
    Args:
        job_id: The job ID to test
        max_workers: Number of worker threads to use
    """
    logger.info(f"Testing bucketed skill matching on job {job_id}")
    
    # Check if job file exists
    job_file = Path(JOB_DATA_DIR) / f"job{job_id}.json"
    if not job_file.exists():
        logger.error(f"Job file not found: {job_file}")
        return False
    
    # Load job data before matching
    try:
        with open(job_file, "r", encoding="utf-8") as f:
            job_data_before = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load job file: {e}")
        return False
    
    # Run bucketed matching
    start_time = time.time()
    run_bucketed_skill_matcher(
        job_ids=[job_id],
        batch_size=10,
        max_workers=max_workers
    )
    elapsed_time = time.time() - start_time
    
    # Load job data after matching
    try:
        with open(job_file, "r", encoding="utf-8") as f:
            job_data_after = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load job file after matching: {e}")
        return False
    
    # Check if skill_match field was added/updated
    if "skill_match" not in job_data_after:
        logger.error("No skill_match field found in job data after matching")
        return False
    
    # Print results
    logger.info(f"Bucketed skill matching completed in {elapsed_time:.2f} seconds")
    
    # Check for the presence of bucketed results
    bucket_results = job_data_after.get("skill_match", {}).get("bucket_results", {})
    if not bucket_results:
        logger.error("No bucket results found in job data")
        return False
    
    # Print overall match
    overall_match = job_data_after.get("skill_match", {}).get("overall_match", 0.0)
    logger.info(f"Overall match: {overall_match:.2%}")
    
    # Print bucket results
    logger.info("Bucket results:")
    for bucket, data in bucket_results.items():
        match_percentage = data.get("match_percentage", 0.0)
        weight = data.get("weight", 0.0)
        job_skills = data.get("job_skills", [])
        cv_skills = data.get("cv_skills", [])
        
        logger.info(f"  - {bucket}:")
        logger.info(f"    Match: {match_percentage:.2%}")
        logger.info(f"    Weight: {weight:.2%}")
        logger.info(f"    Job skills: {len(job_skills)} ({', '.join(job_skills[:3])}{'...' if len(job_skills) > 3 else ''})")
        logger.info(f"    CV skills: {len(cv_skills)} ({', '.join(cv_skills[:3])}{'...' if len(cv_skills) > 3 else ''})")
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test bucketed skill matching")
    parser.add_argument("--job-id", type=int, required=True, help="Job ID to test")
    parser.add_argument("--max-workers", type=int, default=4, help="Max worker threads")
    
    args = parser.parse_args()
    
    success = test_bucketed_matching(
        job_id=args.job_id,
        max_workers=args.max_workers
    )
    
    sys.exit(0 if success else 1)
