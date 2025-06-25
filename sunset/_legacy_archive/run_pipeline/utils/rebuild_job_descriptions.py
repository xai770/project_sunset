#!/usr/bin/env python3
"""
Rebuild Job Descriptions Utility

This script identifies job postings with missing or placeholder descriptions and 
regenerates them using the cleaner module with proper HTML content parsing.

Usage:
  python rebuild_job_descriptions.py [--batch-size BATCH_SIZE] [--model MODEL] [--dry-run]

Options:
  --batch-size BATCH_SIZE   Number of jobs to process in each batch (default: 10)
  --model MODEL             Model to use for cleaning (default: llama3.2:latest)
  --dry-run                 Only identify jobs needing processing without making changes
  --verbose                 Show detailed information about processing
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime
import concurrent.futures

# Add the project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from run_pipeline.config.paths import (
    PROJECT_ROOT,
    JOB_DATA_DIR
)

from run_pipeline.core.cleaner_module import (
    extract_concise_description,
    clean_llm_artifacts
)

# Set up logging
log_file = f"rebuild_descriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)

logger = logging.getLogger('rebuild_job_descriptions')

def get_jobs_needing_processing():
    """
    Identify jobs that need their descriptions regenerated
    
    Returns:
        list: List of job IDs that need processing
    """
    jobs_to_process = []
    job_files = sorted([f for f in os.listdir(JOB_DATA_DIR) if f.startswith('job') and f.endswith('.json')])
    
    logger.info(f"Scanning {len(job_files)} job files for missing or placeholder descriptions...")
    
    # Get current prompt version for comparison
    current_prompt_version = None
    try:
        # Import here to avoid circular imports
        sys.path.append(str(PROJECT_ROOT))
        from run_pipeline.core.cleaner_module import get_current_prompt
        _, current_prompt_version = get_current_prompt()
        logger.info(f"Current prompt version is {current_prompt_version}")
    except Exception as e:
        logger.warning(f"Could not get current prompt version: {str(e)}")
    
    for job_file in job_files:
        job_id = job_file.replace('job', '').replace('_removed', '').replace('.json', '')
        job_path = JOB_DATA_DIR / job_file
        
        try:
            with open(job_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            needs_processing = False
            reason = None
            
            # Check if the job has a concise description
            if 'web_details' not in job_data or 'concise_description' not in job_data['web_details']:
                needs_processing = True
                reason = "Missing concise description"
            else:
                concise_desc = job_data['web_details']['concise_description']
                
                # Check if it's a placeholder by metadata
                if ('description_metadata' in job_data['web_details'] and 
                    job_data['web_details']['description_metadata'].get('is_placeholder', False)):
                    needs_processing = True
                    reason = "Placeholder (identified by metadata)"
                
                # Check if it's a placeholder by content
                elif "placeholder for a concise description" in concise_desc.lower():
                    needs_processing = True
                    reason = "Placeholder (identified by content)"
                
                # Check if it needs reprocessing due to prompt version update
                elif current_prompt_version and 'description_metadata' in job_data['web_details']:
                    metadata = job_data['web_details']['description_metadata']
                    job_prompt_version = metadata.get('prompt_version')
                    
                    if not job_prompt_version:
                        # If no prompt version in metadata, it was created before versioning
                        needs_processing = True
                        reason = "Missing prompt version in metadata"
                    elif job_prompt_version != current_prompt_version:
                        # Compare versions
                        try:
                            job_v = [int(i) for i in job_prompt_version.split('.')]
                            current_v = [int(i) for i in current_prompt_version.split('.')]
                            
                            if current_v > job_v:
                                needs_processing = True
                                reason = f"Outdated prompt version ({job_prompt_version} < {current_prompt_version})"
                        except Exception as e:
                            logger.warning(f"Error comparing prompt versions for job {job_id}: {str(e)}")
            
            # Check if the job has valid HTML content for processing
            has_content = False
            if 'api_details' in job_data and 'html' in job_data['api_details'] and job_data['api_details']['html']:
                has_content = True
            
            if needs_processing:
                if has_content:
                    jobs_to_process.append({
                        'job_id': job_id,
                        'file': job_file,
                        'reason': reason,
                        'has_content': has_content
                    })
                else:
                    logger.warning(f"Job {job_id} needs processing but has no HTML content")
        
        except Exception as e:
            logger.error(f"Error checking job {job_id}: {str(e)}")
    
    logger.info(f"Found {len(jobs_to_process)} jobs that need description regeneration")
    
    # Group and count by reason
    reason_counts = {}
    for job in jobs_to_process:
        reason = job['reason']
        if reason not in reason_counts:
            reason_counts[reason] = 0
        reason_counts[reason] += 1
    
    for reason, count in reason_counts.items():
        logger.info(f"- {reason}: {count} jobs")
    
    return jobs_to_process

def process_job(job_info, model, dry_run=False):
    """
    Process a single job to regenerate its description
    
    Args:
        job_info (dict): Job information including job_id and file
        model (str): Model to use for cleaning
        dry_run (bool): If True, don't make any changes
        
    Returns:
        dict: Processing result information
    """
    job_id = job_info['job_id']
    job_file = job_info['file']
    job_path = JOB_DATA_DIR / job_file
    
    result = {
        'job_id': job_id,
        'success': False,
        'is_dry_run': dry_run,
        'reason': job_info['reason']
    }
    
    try:
        # Read job data
        with open(job_path, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
        
        # Get job title
        job_title = job_data.get("title", "")
        if not job_title and 'web_details' in job_data and 'position_title' in job_data['web_details']:
            job_title = job_data['web_details']['position_title']
        if not job_title:
            job_title = f"Job {job_id}"
        
        # Get HTML content from api_details.html
        job_content = ""
        if "api_details" in job_data and "html" in job_data["api_details"]:
            job_content = job_data["api_details"]["html"]
        
        if not job_content:
            result['error'] = "No HTML content found"
            return result
        
        # If this is a dry run, just return with success
        if dry_run:
            result['success'] = True
            result['message'] = f"Would process job {job_id} (dry run)"
            return result
        
        # Extract concise job description - set parameter to not save separate output files
        concise_description, extraction_status, error_message = extract_concise_description(
            job_content, job_title, job_id, model
        )
        
        # Check if extraction was successful
        if extraction_status == "success" or extraction_status == "test_mode":
            # Create or update web_details
            if 'web_details' not in job_data:
                job_data['web_details'] = {}
            
            # Get current prompt version
            try:
                from run_pipeline.core.cleaner_module import get_current_prompt
                _, prompt_version = get_current_prompt()
            except Exception as e:
                logger.warning(f"Could not get prompt version: {str(e)}")
                prompt_version = "1.1"  # Default to our new version
            
            # Add the description and metadata
            job_data['web_details']['concise_description'] = concise_description
            job_data['web_details']['description_metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'model_used': model,
                'is_placeholder': False,
                'extraction_status': extraction_status,
                'prompt_version': prompt_version  # Add prompt version
            }
            
            # Add log entry
            if 'log' not in job_data:
                job_data['log'] = []
            
            job_data['log'].append({
                "timestamp": datetime.now().isoformat(),
                "script": "run_pipeline.utils.rebuild_job_descriptions",
                "action": "regenerate_concise_description",
                "message": f"Regenerated concise job description for job ID {job_id}"
            })
            
            # Save updated job data
            with open(job_path, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            
            result['success'] = True
            result['message'] = f"Successfully regenerated description for job {job_id}"
        else:
            result['success'] = False
            result['error'] = error_message
    
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        logger.error(f"Error processing job {job_id}: {str(e)}")
    
    return result

def process_jobs_in_batches(jobs_to_process, batch_size, model, dry_run=False):
    """
    Process jobs in batches
    
    Args:
        jobs_to_process (list): List of jobs to process
        batch_size (int): Number of jobs to process in each batch
        model (str): Model to use for cleaning
        dry_run (bool): If True, don't make any changes
    """
    total_jobs = len(jobs_to_process)
    successful = 0
    failed = 0
    
    for i in range(0, total_jobs, batch_size):
        batch = jobs_to_process[i:i+batch_size]
        batch_start_time = time.time()
        
        logger.info(f"Processing batch {i//batch_size + 1}/{(total_jobs + batch_size - 1)//batch_size} ({len(batch)} jobs)")
        
        results = []
        for job_info in batch:
            result = process_job(job_info, model, dry_run)
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
                
            # Brief pause between jobs to avoid rate limiting
            time.sleep(0.5)
        
        batch_time = time.time() - batch_start_time
        logger.info(f"Batch completed in {batch_time:.2f} seconds")
        logger.info(f"Progress: {i + len(batch)}/{total_jobs} jobs processed ({successful} successful, {failed} failed)")
        
        # Save batch results
        batch_results = {
            'timestamp': datetime.now().isoformat(),
            'batch_number': i//batch_size + 1,
            'jobs_processed': len(batch),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }
        
        # Save batch results to file
        batch_dir = PROJECT_ROOT / "data" / "rebuild_results"
        os.makedirs(batch_dir, exist_ok=True)
        batch_file = batch_dir / f"batch_{i//batch_size + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, indent=2, ensure_ascii=False)
        
        # Pause between batches to allow the model to cool down
        if i + batch_size < total_jobs:
            pause_time = min(30, batch_time * 0.2)  # Pause for 20% of batch processing time, max 30 seconds
            logger.info(f"Pausing for {pause_time:.2f} seconds before next batch...")
            time.sleep(pause_time)
    
    # Log final summary
    logger.info("=" * 50)
    logger.info("Job Description Regeneration Summary")
    logger.info("=" * 50)
    logger.info(f"Total jobs processed: {total_jobs}")
    logger.info(f"Successfully processed: {successful}")
    logger.info(f"Failed to process: {failed}")
    logger.info("=" * 50)
    
    return successful, failed

def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(description="Rebuild job descriptions for placeholders")
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of jobs to process in each batch (default: 10)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="llama3.2:latest",
        help="Model to use for cleaning (default: llama3.2:latest)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only identify jobs needing processing without making changes"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information about processing"
    )
    
    parser.add_argument(
        "--max-jobs",
        type=int,
        help="Maximum number of jobs to process"
    )
    
    parser.add_argument(
        "--job-id",
        type=str,
        help="Specific job ID to process (e.g. 55025)"
    )
    
    args = parser.parse_args()
    
    # Set verbose logging if requested
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Handle specific job ID if provided
    if args.job_id:
        job_file = f"job{args.job_id}.json"
        job_path = JOB_DATA_DIR / job_file
        
        if not job_path.exists():
            logger.error(f"Job {args.job_id} not found at {job_path}")
            return
            
        logger.info(f"Processing specific job: {args.job_id}")
        jobs_to_process = [{
            'job_id': args.job_id,
            'file': job_file,
            'reason': "User-requested reprocessing",
            'has_content': True
        }]
    else:
        # Get all jobs that need processing
        jobs_to_process = get_jobs_needing_processing()
        
        if not jobs_to_process:
            logger.info("No jobs need processing. Exiting.")
            return
        
        # Apply max_jobs limit if specified
        if args.max_jobs and len(jobs_to_process) > args.max_jobs:
            logger.info(f"Limiting to {args.max_jobs} jobs as requested (out of {len(jobs_to_process)} total)")
            jobs_to_process = jobs_to_process[:args.max_jobs]
    
    if args.dry_run:
        logger.info("Dry run mode - no changes will be made")
        logger.info(f"Would process {len(jobs_to_process)} jobs with {args.model} model in batches of {args.batch_size}")
        return
    
    # Process jobs in batches
    successful, failed = process_jobs_in_batches(
        jobs_to_process, 
        args.batch_size, 
        args.model,
        args.dry_run
    )
    
    logger.info(f"Job description regeneration completed: {successful} successful, {failed} failed")
    
    # If we processed a specific job, let's check its metadata
    if args.job_id:
        try:
            job_file = JOB_DATA_DIR / f"job{args.job_id}.json"
            with open(job_file, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
                
            if 'web_details' in job_data and 'description_metadata' in job_data['web_details']:
                logger.info("Job metadata after processing:")
                logger.info(json.dumps(job_data['web_details']['description_metadata'], indent=2))
            else:
                logger.info("No description metadata found in processed job")
        except Exception as e:
            logger.error(f"Error checking job metadata: {str(e)}")

if __name__ == "__main__":
    main()
