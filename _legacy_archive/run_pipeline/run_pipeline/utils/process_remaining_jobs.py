#!/usr/bin/env python3
"""
Process all remaining job postings that haven't been processed with 
the staged job description processor yet.

Usage:
  python process_remaining_jobs.py [--model MODEL] [--batch-size BATCH_SIZE]

Options:
  --model MODEL            Model to use for extraction (default: llama3.2:latest)
  --batch-size BATCH_SIZE  Number of jobs to process in one batch (default: 50)
  --dry-run                Only print what would be done, don't actually process
"""

import os
import sys
import json
import argparse
from pathlib import Path
import logging
from datetime import datetime

# Add the project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from run_pipeline.config.paths import JOB_DATA_DIR
from run_pipeline.utils.staged_job_description_processor import process_jobs

# Set up logging
log_dir = Path("/home/xai/Documents/sunset/logs")
os.makedirs(log_dir, exist_ok=True)
log_file = log_dir / f"process_remaining_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)

logger = logging.getLogger('process_remaining_jobs')

def find_unprocessed_jobs():
    """
    Find all job IDs that haven't been processed with the staged approach yet
    
    Returns:
        list: List of job IDs that need processing
    """
    jobs_to_process = []
    processed_count = 0
    total_count = 0
    
    # Get all job files
    job_dir = Path(JOB_DATA_DIR)
    job_files = [f for f in os.listdir(job_dir) if f.startswith('job') and f.endswith('.json')]
    
    logger.info(f"Found {len(job_files)} total job files")
    
    # Check each job file
    for job_file in job_files:
        total_count += 1
        job_path = job_dir / job_file
        
        try:
            with open(job_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
                
                # Check if job has already been processed with staged approach
                already_processed = False
                
                if "log" in job_data:
                    for log_entry in job_data["log"]:
                        if (log_entry.get("script") == "run_pipeline.utils.staged_job_description_processor" and
                            log_entry.get("action") == "process_job_description"):
                            already_processed = True
                            processed_count += 1
                            break
                
                # If not processed, add to the list
                if not already_processed:
                    job_id = job_file.replace('job', '').replace('.json', '')
                    jobs_to_process.append(job_id)
                    
        except Exception as e:
            logger.error(f"Error processing {job_file}: {str(e)}")
    
    logger.info(f"Found {len(jobs_to_process)} jobs that need processing")
    logger.info(f"{processed_count} jobs have already been processed")
    
    return jobs_to_process

def process_in_batches(jobs_to_process, batch_size, model, dry_run=False):
    """
    Process jobs in batches
    
    Args:
        jobs_to_process (list): List of job IDs to process
        batch_size (int): Size of each batch
        model (str): Model to use for extraction
        dry_run (bool): If True, don't make any changes
    """
    total_jobs = len(jobs_to_process)
    total_processed = 0
    total_success = 0
    total_failure = 0
    
    # Process in batches
    for i in range(0, len(jobs_to_process), batch_size):
        batch = jobs_to_process[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1} of {(len(jobs_to_process) + batch_size - 1) // batch_size}")
        logger.info(f"Batch contains {len(batch)} jobs")
        
        if dry_run:
            logger.info(f"DRY RUN: Would process job IDs: {', '.join(batch)}")
            continue
        
        # Process this batch
        processed, success, failure = process_jobs(
            job_ids=batch,
            model=model,
            dry_run=False,
            output_format="text"
        )
        
        # Update totals
        total_processed += processed
        total_success += success
        total_failure += failure
        
        # Log batch results
        logger.info(f"Batch {i//batch_size + 1} results:")
        logger.info(f"- Jobs processed: {processed}")
        logger.info(f"- Success: {success}")
        logger.info(f"- Failure: {failure}")
        logger.info(f"Progress: {total_processed}/{total_jobs} ({total_processed/total_jobs*100:.1f}%)")

    # Log overall results
    logger.info(f"Overall processing complete:")
    logger.info(f"- Total jobs processed: {total_processed}")
    logger.info(f"- Successfully processed: {total_success}")
    logger.info(f"- Failed to process: {total_failure}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Process all remaining job postings with the staged job description processor"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="llama3.2:latest",
        help="Model to use for extraction"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of jobs to process in one batch"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print what would be done, don't actually process"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting to process remaining jobs with model {args.model}")
    if args.dry_run:
        logger.info("DRY RUN MODE: No changes will be made")
    
    # Find unprocessed jobs
    jobs_to_process = find_unprocessed_jobs()
    
    if not jobs_to_process:
        logger.info("No jobs need processing. All jobs have already been processed.")
        return 0
    
    # Process in batches
    process_in_batches(jobs_to_process, args.batch_size, args.model, args.dry_run)
    
    logger.info("Processing complete")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
