#!/usr/bin/env python3
"""
Bucketed Skill Matching Module (Fixed Version)

This module provides an optimized approach to skill matching:
1. Group skills into predefined buckets (technical, soft skills, etc.)
2. Compare buckets rather than individual skills using parallel processing
3. Calculate overall match based on bucket-level matching
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
import concurrent.futures
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucketed_skill_matcher")

# Get paths from the main config
try:
    from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR
except ImportError:
    # Fallback if imported outside the pipeline
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    JOB_DATA_DIR = PROJECT_ROOT / "data" / "postings"

# Define paths
YOUR_SKILLS_FILE = PROJECT_ROOT / "profile" / "skills" / "skill_decompositions.json"

# Import from bucket matcher module
from run_pipeline.skill_matching.bucket_matcher_fixed import match_job_to_your_skills
from run_pipeline.skill_matching.bucket_cache import bucket_cache

def process_job_file(job_file: Path, your_skills: Dict, max_workers_per_job: int = 2) -> Tuple[Path, bool]:
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
    match_results = match_job_to_your_skills(
        job_data, 
        your_skills, 
        max_workers=max_workers_per_job
    )
    
    # Update job data with match results
    job_data["skill_match"] = match_results
    
    # Save updated job data
    save_job_data(job_file, job_data)
    
    return job_file, True

def batch_match_all_jobs(
    job_ids: Optional[List[int]] = None,
    batch_size: int = 10,
    max_workers: int = 4,
    force_reprocess: bool = False,
    use_embeddings: bool = True,
    use_confidence_scoring: bool = False
):
    """
    Process all jobs or specified job IDs in parallel
    
    Args:
        job_ids: Optional list of job IDs to process
        batch_size: Batch size for LLM calls
        max_workers: Maximum number of worker threads
        force_reprocess: (ignored in this version)
        use_embeddings: (ignored in this version)
        use_confidence_scoring: (ignored in this version)
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

def load_your_skills() -> Optional[Dict[str, Any]]:
    """Load your skills from the standard location"""
    if not YOUR_SKILLS_FILE.exists():
        logger.error(f"Your skills file not found: {YOUR_SKILLS_FILE}")
        return None
    try:
        with open(YOUR_SKILLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load your skills: {e}")
        return None

def load_job_data(job_path: Path) -> Optional[Dict[str, Any]]:
    """Load job data from a file"""
    try:
        with open(job_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load job file {job_path}: {e}")
        return None

def save_job_data(job_path: Path, job_data: Dict[str, Any]) -> None:
    """Save job data to a file"""
    try:
        with open(job_path, "w", encoding="utf-8") as f:
            json.dump(job_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save job file {job_path}: {e}")

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
