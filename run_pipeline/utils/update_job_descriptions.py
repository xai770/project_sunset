#!/usr/bin/env python3
"""
Utility for maintaining and updating concise job descriptions

This script identifies job postings that are missing concise descriptions
or have placeholder descriptions, and processes them to generate proper
concise descriptions using the configured Ollama model.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import List, Optional, Tuple

# Add project root to path if running as standalone script
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

# Import modules
from run_pipeline.utils.logging_utils import setup_logger, create_timestamped_dir
from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR, LOG_BASE_DIR
from run_pipeline.core.cleaner_module import clean_job_descriptions, process_job_files, count_placeholder_jobs

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('job_description_updater')

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Update Job Descriptions Utility")
    
    parser.add_argument(
        "--job-ids",
        type=str,
        default=None,
        help="Specific job IDs to process (comma-separated). If not provided, will find and process all jobs needing descriptions."
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="llama3.2:latest",
        help="Model to use for extraction (default: llama3.2:latest)"
    )
    
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=None,
        help="Maximum number of jobs to process (default: process all)"
    )
    
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode with mock responses"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only identify jobs needing updates without processing them"
    )
    
    return parser.parse_args()

def find_jobs_needing_descriptions() -> List[str]:
    """
    Find all job IDs that need concise descriptions
    
    Returns:
        List[str]: List of job IDs needing concise descriptions
    """
    job_dir = Path(JOB_DATA_DIR)
    jobs_to_process = []
    job_files = sorted([f for f in os.listdir(job_dir) 
                if f.startswith('job') and f.endswith('.json')])
    
    logger.info(f"Scanning {len(job_files)} job files for missing or placeholder descriptions...")
    
    for job_file in job_files:
        job_id = job_file.replace('job', '').replace('.json', '')
        job_path = job_dir / job_file
        
        try:
            with open(job_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Check if concise description exists and is not a placeholder
            has_valid_description = False
            if 'web_details' in job_data and 'concise_description' in job_data['web_details']:
                concise_desc = job_data['web_details']['concise_description']
                if concise_desc and len(concise_desc) > 50:
                    if "placeholder for a concise description" not in concise_desc:
                        has_valid_description = True
            
            if not has_valid_description:
                jobs_to_process.append(job_id)
                
        except Exception as e:
            logger.error(f"Error checking job {job_id}: {str(e)}")
            # Include jobs with errors as they might need processing
            jobs_to_process.append(job_id)
    
    return jobs_to_process

def update_job_descriptions(job_ids: Optional[List[str]] = None, 
                            model: str = "llama3.2:latest",
                            max_jobs: Optional[int] = None,
                            test_mode: bool = False,
                            dry_run: bool = False) -> Tuple[int, int, int]:
    """
    Update concise descriptions for job postings
    
    Args:
        job_ids (List[str], optional): Specific job IDs to process
        model (str): Model to use for extraction
        max_jobs (int, optional): Maximum number of jobs to process
        test_mode (bool): Whether to run in test mode with mock responses
        dry_run (bool): Only identify jobs needing updates without processing them
        
    Returns:
        Tuple[int, int, int]: (total_jobs_found, total_processed, total_successful)
    """
    # Set up logging
    log_dir = create_timestamped_dir(LOG_BASE_DIR, "job_description_update")
    logger, log_file = setup_logger("job_description_updater", log_dir)
    
    # Set test mode if requested
    if test_mode:
        logger.info("Running in TEST_MODE with mock LLM responses")
        os.environ["TEST_MODE"] = "1"
    
    # Find jobs that need descriptions if not specified
    if not job_ids:
        job_ids = find_jobs_needing_descriptions()
    
    total_jobs = len(job_ids)
    logger.info(f"Found {total_jobs} jobs that need concise descriptions")
    
    if dry_run:
        logger.info("Dry run requested - not processing any jobs")
        if job_ids:
            logger.info(f"Jobs that would be processed: {', '.join(job_ids[:10])}" + 
                       f"{' and more...' if len(job_ids) > 10 else ''}")
        return total_jobs, 0, 0
    
    # Limit the number of jobs if max_jobs is specified
    if max_jobs and len(job_ids) > max_jobs:
        logger.info(f"Limiting to {max_jobs} jobs as requested")
        job_ids = job_ids[:max_jobs]
    
    # Process the jobs
    logger.info(f"Processing {len(job_ids)} jobs using {model} model")
    processed = 0
    success = 0
    
    try:
        result = clean_job_descriptions(job_ids=job_ids, model=model)
        if result:
            logger.info("✓ Job description updating completed successfully!")
            
            # Check for any remaining placeholder jobs
            placeholder_count = count_placeholder_jobs(JOB_DATA_DIR)
            if placeholder_count > 0:
                logger.info(f"Note: {placeholder_count} jobs still need valid concise descriptions")
                
            # The clean_job_descriptions function doesn't return specific counts,
            # so we'll estimate based on the result
            return total_jobs, len(job_ids), len(job_ids)
        else:
            logger.error("✗ Job description updating failed")
            return total_jobs, len(job_ids), 0
    except Exception as e:
        logger.error(f"Error processing jobs: {str(e)}")
        return total_jobs, 0, 0

def main():
    """Main entry point"""
    # Parse arguments
    args = parse_args()
    
    # Process job IDs if provided
    job_ids = None
    if args.job_ids:
        job_ids = [job_id.strip() for job_id in args.job_ids.split(',') if job_id.strip()]
    
    print(f"Job Description Update Utility")
    print(f"==============================")
    
    # Check if Ollama is available
    if not args.test_mode:
        import subprocess
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            print(f"Available models: {result.stdout.strip()}")
        except Exception as e:
            print(f"Warning: Ollama may not be installed or accessible: {str(e)}")
            print("You can install Ollama from: https://ollama.com/")
            print("Running in test mode instead...")
            args.test_mode = True
    
    # Run the update
    total_jobs, processed, success = update_job_descriptions(
        job_ids=job_ids,
        model=args.model,
        max_jobs=args.max_jobs,
        test_mode=args.test_mode,
        dry_run=args.dry_run
    )
    
    # Print summary
    print("\nJob Description Update Summary")
    print("==============================")
    print(f"Total jobs needing updates: {total_jobs}")
    if args.dry_run:
        print("No jobs processed (dry run)")
    else:
        print(f"Jobs processed: {processed}")
        print(f"Successfully updated: {success}")
        print(f"Failed updates: {processed - success}")

    # Return appropriate exit code
    if args.dry_run or success > 0:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
