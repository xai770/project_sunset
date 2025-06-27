#!/usr/bin/env python3
"""
Bucketed Skill Matching Module

This module provides a simplified approach to skill matching:
1. Group skills into predefined buckets (technical, soft skills, etc.)
2. Compare buckets rather than individual skills
3. Calculate overall match based on bucket-level matching

This approach is significantly faster than enrichment-based matching
while still providing valuable insights into job-CV fit.

The code is split across multiple files for better maintainability:
- bucketed_cache.py: Caching mechanisms for bucket matching
- bucketed_utils.py: Utility functions for skill extraction and bucketing
- bucketed_llm.py: LLM interaction for skill matching
- bucketed_weights.py: Calculation of bucket weights for matching
"""

import os
import time
import logging
import concurrent.futures
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import requests

# Import from utility modules
from run_pipeline.skill_matching.bucketed_cache import BucketMatchCache
from run_pipeline.skill_matching.bucketed_utils import (
    categorize_skill, extract_cv_skills, extract_job_skills,
    extract_percentage, load_your_skills, load_job_data, save_job_data,
    SKILL_BUCKETS, PROJECT_ROOT, JOB_DATA_DIR, YOUR_SKILLS_FILE
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucketed_skill_matcher")

# Define paths
CACHE_DIR = PROJECT_ROOT / "data" / "skill_match_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
BUCKET_CACHE_FILE = CACHE_DIR / "bucket_match_cache.json"

# Ollama settings
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")

# Initialize cache
bucket_cache = BucketMatchCache(cache_file=BUCKET_CACHE_FILE)

# Import LLM comparison function
from run_pipeline.skill_matching.bucketed_llm import compare_skill_buckets_llm

# Import weights calculation function
from run_pipeline.skill_matching.bucketed_weights import calculate_bucket_weights

def match_job_to_your_skills(job_data: Dict[str, Any], your_skills: Dict[str, Any]) -> Dict[str, Any]:
    """
    Match job skills to your skills using the bucketed approach
    
    Args:
        job_data: Job data structure
        your_skills: Your skills data structure
    
    Returns:
        Dict[str, Any]: Match results
    """
    # Extract and bucket skills
    job_skills_buckets = extract_job_skills(job_data)
    cv_skills_buckets = extract_cv_skills(your_skills)
    
    # Calculate bucket weights based on job requirements
    bucket_weights = calculate_bucket_weights(job_skills_buckets)
    
    # Compare buckets
    bucket_results: Dict[str, Dict[str, Any]] = {}
    for bucket in SKILL_BUCKETS.keys():
        job_bucket_skills = job_skills_buckets.get(bucket, [])
        cv_bucket_skills = cv_skills_buckets.get(bucket, [])
        
        # Skip empty buckets
        if not job_bucket_skills:
            bucket_results[bucket] = {
                "match_percentage": 0.0,
                "weight": bucket_weights.get(bucket, 0.0),
                "job_skills": job_bucket_skills,
                "cv_skills": cv_bucket_skills
            }
            continue
        
        # Compare skills in this bucket (pass cache to the function)
        match_percentage = compare_skill_buckets_llm(
            bucket, job_bucket_skills, cv_bucket_skills, bucket_cache=bucket_cache
        )
        
        bucket_results[bucket] = {
            "match_percentage": match_percentage,
            "weight": bucket_weights.get(bucket, 0.0),
            "job_skills": job_bucket_skills,
            "cv_skills": cv_bucket_skills
        }
    
    # Calculate weighted average for overall match
    overall_match = 0.0
    for bucket, result in bucket_results.items():
        try:
            match_pct = result["match_percentage"]
            if isinstance(match_pct, (str, int, float)):
                try:
                    match_percentage = float(match_pct)
                except (ValueError, TypeError):
                    match_percentage = 0.0
            else:
                match_percentage = 0.0

            weight = result["weight"]
            if isinstance(weight, (str, int, float)):
                try:
                    weight_value = float(weight)
                except (ValueError, TypeError):
                    weight_value = 0.0
            else:
                weight_value = 0.0

            overall_match += match_percentage * weight_value
        except (ValueError, TypeError, KeyError):
            # Skip invalid values
            continue

    return {
        "overall_match": overall_match,
        "bucket_results": bucket_results,
        "timestamp": datetime.now().isoformat()
    }

def process_job_file(job_file: Path, your_skills: Dict, max_workers_per_job: int = 2):
    """
    Process a single job file
    
    Args:
        job_file: Path to job file
        your_skills: Your skills data
        max_workers_per_job: Maximum number of workers for bucket processing
        
    Returns:
        Tuple[Path, bool]: Job file path and success status
    """
    job_data = load_job_data(job_file)
    if not job_data:
        return job_file, False
    
    # Match job to your skills with optimized parallel processing
    # Fix the function call around line 555 (in batch_match_all_jobs or similar)
    # Replace max_workers parameter with max_workers_per_job which is used in the function
    match_results = match_job_to_your_skills(
        job_data, 
        your_skills
        # Remove the max_workers parameter
    )
    
    # Update job data with match results
    job_data["skill_match"] = match_results
    
    # Save updated job data
    save_job_data(job_file, job_data)
    
    return job_file, True

def batch_match_all_jobs(job_ids: Optional[List[int]] = None, batch_size: int = 10, max_workers: int = 4):
    """
    Process all jobs or specified job IDs in parallel
    
    Args:
        job_ids: Optional list of job IDs to process
        batch_size: Batch size for LLM calls
        max_workers: Maximum number of worker threads
    """
    start_time = time.time()
    
    # Load your skills
    your_skills = load_your_skills()
    if not your_skills:
        logger.error("Failed to load your skills")
        return
    
    # Find job files
    if job_ids:
        job_files = [JOB_DATA_DIR / f"job{job_id}.json" for job_id in job_ids]
        job_files = [f for f in job_files if f.exists()]
        logger.info(f"Found {len(job_files)} job files matching the specified IDs.")
    else:
        job_files = list(JOB_DATA_DIR.glob("job*.json"))
        logger.info(f"Found {len(job_files)} total job files.")
    
    # Calculate optimal worker distribution
    # Use 1-2 workers per job for bucket processing, rest for job parallelism
    max_workers_per_job = max(1, min(2, max_workers // 2))
    job_parallelism = max(1, max_workers // max_workers_per_job)
    
    logger.info(f"Using {job_parallelism} parallel jobs with {max_workers_per_job} workers each")
    
    # Process jobs in parallel
    processed_count = 0
    updated_count = 0
    
    # Create a thread pool for processing jobs
    with concurrent.futures.ThreadPoolExecutor(max_workers=job_parallelism) as executor:
        # Submit all jobs for processing
        future_to_job = {
            executor.submit(process_job_file, job_file, your_skills, max_workers_per_job): job_file
            for job_file in job_files
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_job):
            job_file = future_to_job[future]
            
            try:
                _, success = future.result()
                processed_count += 1
                
                if success:
                    updated_count += 1
                
                # Log progress
                if processed_count % 5 == 0 or processed_count == len(job_files):
                    elapsed = time.time() - start_time
                    avg_time = elapsed / processed_count if processed_count > 0 else 0
                    remaining = avg_time * (len(job_files) - processed_count)
                    logger.info(
                        f"Processed {processed_count}/{len(job_files)} job files "
                        f"({updated_count} updated) in {elapsed:.1f}s "
                        f"(avg: {avg_time:.1f}s/job, est. remaining: {remaining:.1f}s)"
                    )
            except Exception as e:
                logger.error(f"Error processing job {job_file}: {str(e)}")
    
    # Save cache at the end
    bucket_cache.save_cache()
    
    total_time = time.time() - start_time
    avg_time_per_job = total_time / len(job_files) if job_files else 0
    logger.info(
        f"Bucketed skill matching complete. Updated {updated_count}/{len(job_files)} "
        f"job files in {total_time:.1f}s (avg: {avg_time_per_job:.1f}s/job)"
    )

# These functions are now imported from bucketed_utils.py

def main():
    """Main function for direct script execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Match job skills to your skills using bucketed approach")
    parser.add_argument("--job-ids", type=int, nargs="+", help="Job IDs to process")
    parser.add_argument("--batch-size", type=int, default=10, 
                        help="Batch size for LLM calls (default: 10)")
    parser.add_argument("--max-workers", type=int, default=4, 
                        help="Maximum worker threads (default: 4)")
    
    args = parser.parse_args()
    
    batch_match_all_jobs(
        job_ids=args.job_ids,
        batch_size=args.batch_size,
        max_workers=args.max_workers
    )

if __name__ == "__main__":
    main()
