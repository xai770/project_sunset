#!/usr/bin/env python3
"""
Test script for the Enhanced Bucket-Based Skill Matching system

This script allows you to test the enhanced bucket-based skill matching system
with a small number of jobs to verify its functionality.
"""

import os
import sys
import json
import time
import random
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucket_test")

# Get project root
try:
    from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR
except ImportError:
    # Fallback if imported outside the pipeline
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    JOB_DATA_DIR = PROJECT_ROOT / "data" / "postings"

# Add project root to path if needed
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def get_job_ids(count: int = 5) -> List[int]:
    """Get a list of random job IDs from the data directory"""
    job_files = list(JOB_DATA_DIR.glob("job*.json"))
    
    if not job_files:
        logger.error(f"No job files found in {JOB_DATA_DIR}")
        return []
        
    # Randomly select jobs
    selected_files = random.sample(job_files, min(count, len(job_files)))
    
    # Extract job IDs from filenames
    job_ids = []
    for job_file in selected_files:
        try:
            job_id = int(job_file.stem.replace("job", ""))
            job_ids.append(job_id)
        except ValueError:
            continue
    
    return job_ids


def test_bucket_matcher(job_ids: Optional[List[int]] = None, max_workers: int = 4):
    """Test the enhanced bucket matcher with the specified job IDs"""
    if not job_ids:
        # Get random job IDs if none specified
        job_ids = get_job_ids(5)
        
    if not job_ids:
        logger.error("No job IDs found for testing")
        return False
        
    logger.info(f"Testing with job IDs: {job_ids}")
    
    try:
        # Try to import the enhanced version first
        try:
            from run_pipeline.skill_matching.run_bucket_matcher import run_enhanced_bucket_matcher
            logger.info("Using run_bucket_matcher integration")
            
            # Run the enhanced bucket matcher
            run_enhanced_bucket_matcher(
                job_ids=job_ids,
                batch_size=5,
                max_workers=max_workers,
                force_reprocess=True
            )
            
        except ImportError:
            # Fall back to direct import
            try:
                from run_pipeline.skill_matching.bucketed_skill_matcher_enhanced import batch_match_all_jobs
                logger.info("Using enhanced implementation directly")
                
                # Run the enhanced bucket matcher
                batch_match_all_jobs(
                    job_ids=job_ids,
                    batch_size=5,
                    max_workers=max_workers,
                    force_reprocess=True
                )
                
            except ImportError:
                # Fall back to original version
                from run_pipeline.skill_matching.bucketed_skill_matcher import batch_match_all_jobs
                logger.info("Using original implementation")
                
                # Run the original bucket matcher
                batch_match_all_jobs(
                    job_ids=job_ids,
                    batch_size=5,
                    max_workers=max_workers
                )
        
        # Verify results
        success_count = 0
        for job_id in job_ids:
            job_file = JOB_DATA_DIR / f"job{job_id}.json"
            if not job_file.exists():
                continue
                
            try:
                with open(job_file, "r", encoding="utf-8") as f:
                    job_data = json.load(f)
                    
                # Check for skill match data
                if "skill_match" in job_data and job_data["skill_match"].get("overall_match") is not None:
                    logger.info(f"Job {job_id} successfully processed with match score: {job_data['skill_match'].get('overall_match'):.2f}")
                    
                    # Show bucket results
                    for bucket, result in job_data["skill_match"].get("bucket_results", {}).items():
                        match_percent = result.get("match_percentage", 0)
                        weight = result.get("weight", 0)
                        num_job_skills = len(result.get("job_skills", []))
                        num_cv_skills = len(result.get("cv_skills", []))
                        
                        logger.info(f"  {bucket}: {match_percent:.2f} (weight: {weight:.2f}, job skills: {num_job_skills}, CV skills: {num_cv_skills})")
                        
                    success_count += 1
                else:
                    logger.warning(f"Job {job_id} does not have valid skill match data")
                    
            except Exception as e:
                logger.error(f"Error checking job {job_id}: {str(e)}")
        
        logger.info(f"Successfully processed {success_count}/{len(job_ids)} jobs")
        return success_count == len(job_ids)
        
    except Exception as e:
        logger.error(f"Error testing bucket matcher: {str(e)}")
        return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the enhanced bucket-based skill matching system")
    
    parser.add_argument(
        "--job-ids", 
        type=int, 
        nargs="+", 
        help="Specific job IDs to test (default: 5 random jobs)"
    )
    
    parser.add_argument(
        "--max-workers", 
        type=int, 
        default=4, 
        help="Maximum worker threads (default: 4)"
    )
    
    args = parser.parse_args()
    
    start_time = time.time()
    success = test_bucket_matcher(
        job_ids=args.job_ids,
        max_workers=args.max_workers
    )
    total_time = time.time() - start_time
    
    logger.info(f"Test completed in {total_time:.1f} seconds")
    logger.info(f"Overall success: {success}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
