#!/usr/bin/env python3
"""
Job matching module for the pipeline. 
Handles the core job matching process using llama3.2
"""

import os
import json
import logging
from datetime import datetime

from run_pipeline.config.paths import JOB_DATA_DIR
from run_pipeline.job_matcher.job_processor import process_job
from run_pipeline.job_matcher.cv_utils import get_cv_markdown_text

logger = logging.getLogger('pipeline')

def run_job_matcher(args, job_ids=None):
    """
    Run the job matcher to generate match percentage and cover letter using llama3.2
    
    Args:
        args: Command line arguments
        job_ids: Specific job IDs to process
        
    Returns:
        bool: Success status
    """
    step_number = "1/1" if getattr(args, 'only_regenerate_llama3', False) else "6/7"
    logger.info(f"Step {step_number}: Generating match percentage and cover letter using llama3.2 job_matcher...")

    # Get job files
    job_dir = JOB_DATA_DIR
    job_files = [f for f in os.listdir(job_dir) if f.startswith("job") and f.endswith(".json")]

    # Filter by job_ids if specified
    if job_ids:
        logger.info(f"Filtering to only process job IDs: {job_ids}")
        str_job_ids = [str(jid) for jid in job_ids]
        logger.info(f"String job IDs for filtering: {str_job_ids}")
        logger.info(f"Available job files before filtering: {job_files[:10]}...")
        job_files = [f for f in job_files if f.replace("job", "").replace(".json", "") in str_job_ids]
        logger.info(f"Filtered job files: {job_files}")

    # Limit by max_jobs if specified
    if args.max_jobs and len(job_files) > args.max_jobs:
        logger.info(f"Limiting to {args.max_jobs} jobs")
        job_files = job_files[:args.max_jobs]
        
    total_jobs = len(job_files)
    logger.info(f"Processing {total_jobs} jobs with llama3.2 job_matcher...")

    cv_text = get_cv_markdown_text()

    # Process each job
    for i, job_file in enumerate(job_files):
        job_path = os.path.join(job_dir, job_file)
        try:
            with open(job_path, "r", encoding="utf-8") as jf:
                job_data = json.load(jf)

            # Skip if llama32_evaluation already exists and force_reprocess is not set
            if not args.force_reprocess and "llama32_evaluation" in job_data:
                logger.info(f"Skipping {job_file} - llama32_evaluation already exists (use --force-reprocess to override)")
                continue

            logger.info(f"Processing {job_file} with llama3.2 job_matcher ({i+1}/{total_jobs})...")

            job_id = str(job_data.get("job_id") or job_file.replace("job", "").replace(".json", ""))
            results = process_job(job_id, cv_text, num_runs=5)

            # Store the results under 'llama32_evaluation'
            job_data["llama32_evaluation"] = results
            job_data["llama32_evaluation"]["processed_at"] = datetime.now().isoformat()

            # Save the updated job data
            with open(job_path, "w", encoding="utf-8") as jf:
                json.dump(job_data, jf, indent=2, ensure_ascii=False)

            logger.info(f"Updated {job_file} with llama32_evaluation: {results}")

        except Exception as e:
            logger.error(f"Error processing {job_file}: {str(e)}")
            # Continue with next job

    final_step = "Pipeline completed successfully!" if not getattr(args, 'only_regenerate_llama3', False) else "llama3.2 regeneration completed successfully!"
    logger.info(f"Step 7/7: {final_step}" if not getattr(args, 'only_regenerate_llama3', False) else f"Step 1/1: {final_step}")
    return True

# Export functions
__all__ = ['run_job_matcher']
