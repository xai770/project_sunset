#!/usr/bin/env python3
"""
Job status checker module for the job expansion pipeline

This module checks if job postings are still available online and updates
their status accordingly. It adds a status field to the job JSON and optionally
renames files to indicate removed jobs.
"""

import os
import sys
import json
import time
import random
import logging
import requests
from pathlib import Path
from datetime import datetime
import shutil

# Import utility modules
from run_pipeline.config.paths import (
    PROJECT_ROOT,
    JOB_DATA_DIR,
    DEFAULT_TIMEOUT
)

logger = logging.getLogger('status_checker_module')

# Define job status constants
JOB_STATUS_ACTIVE = "active"
JOB_STATUS_REMOVED = "removed"
JOB_STATUS_ERROR = "check_error"
JOB_STATUS_UNKNOWN = "unknown"

def check_job_availability(url, timeout=DEFAULT_TIMEOUT, retries=2):
    """
    Check if a job posting is still available online by making a request to its URL
    
    Args:
        url (str): URL of the job posting
        timeout (int): Request timeout in seconds
        retries (int): Number of retry attempts
        
    Returns:
        tuple: (is_available, status_code, error_message)
    """
    if not url or not url.startswith("http"):
        return False, None, "Invalid URL"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            
            # Check if the page was found
            if response.status_code == 200:
                # Check if the page contains indicators that the job is no longer available
                # This is site-specific and may need customization
                content_lower = response.text.lower()
                removed_indicators = [
                    "job is no longer available",
                    "position has been filled",
                    "position is no longer open",
                    "job posting not found",
                    "has been closed",
                    "has been filled",
                    "is no longer accepting applications",
                    "job nicht mehr verfügbar",
                    "stelle wurde besetzt",
                    "position ist nicht mehr vakant",
                ]
                
                for indicator in removed_indicators:
                    if indicator in content_lower:
                        return False, response.status_code, f"Job posting page contains indicator: '{indicator}'"
                
                # If we reach here, the job appears to be available
                return True, response.status_code, None
            
            elif response.status_code == 404:
                return False, response.status_code, "Job posting page not found (404)"
            
            elif response.status_code in (301, 302, 307, 308):
                # Handle redirects - some job sites redirect to home page when job is no longer available
                location = response.headers.get('Location', '')
                if 'home' in location.lower() or 'search' in location.lower() or 'index' in location.lower():
                    return False, response.status_code, f"Redirected to non-job page: {location}"
                else:
                    # Follow the redirect manually and check the final page
                    redirect_url = response.headers.get('Location')
                    if redirect_url:
                        redirect_response = requests.get(redirect_url, headers=headers, timeout=timeout)
                        if redirect_response.status_code == 200:
                            return True, redirect_response.status_code, None
            
            # For other status codes, consider the job as potentially removed
            return False, response.status_code, f"Unexpected status code: {response.status_code}"
            
        except requests.exceptions.RequestException as e:
            if attempt < retries:
                # Wait before retry with exponential backoff
                wait_time = 2 ** attempt + random.uniform(0, 1)
                logger.warning(f"Request failed, retrying in {wait_time:.2f} seconds. Error: {str(e)}")
                time.sleep(wait_time)
            else:
                return False, None, f"Request failed after {retries + 1} attempts: {str(e)}"
                
    # Should not reach here, but just in case
    return False, None, "Unknown error checking job availability"

def update_job_status(job_data, job_id, is_available, status_code=None, error_message=None):
    """
    Update job data with status information
    
    Args:
        job_data (dict): Job data dictionary
        job_id (str/int): Job ID
        is_available (bool): Whether the job is available
        status_code (int): HTTP status code
        error_message (str): Error message if any
        
    Returns:
        dict: Updated job data
    """
    # Create status object
    status_obj = {
        "checked_at": datetime.now().isoformat(),
        "is_available": is_available,
        "http_status": status_code
    }
    
    if is_available:
        status_obj["status"] = JOB_STATUS_ACTIVE
        status_obj["message"] = "Job posting is active and available online"
    elif error_message and "error" in error_message.lower():
        status_obj["status"] = JOB_STATUS_ERROR
        status_obj["message"] = error_message
    else:
        status_obj["status"] = JOB_STATUS_REMOVED
        status_obj["message"] = error_message or "Job posting is no longer available online"
    
    # Add status to job data
    job_data["status"] = status_obj
    
    # Update metadata if it exists
    if "metadata" in job_data:
        job_data["metadata"]["last_updated"]["status_checked_at"] = datetime.now().isoformat()
    
    # Add log entry
    if "log" not in job_data:
        job_data["log"] = []
    
    job_data["log"].append({
        "timestamp": datetime.now().isoformat(),
        "script": "run_pipeline.core.status_checker_module",
        "action": "check_job_status",
        "message": status_obj["message"]
    })
    
    return job_data

def rename_job_file(job_path, job_id, status):
    """
    Rename job file to indicate its status
    
    Args:
        job_path (Path): Path to job file
        job_id (str/int): Job ID
        status (str): Job status
        
    Returns:
        Path: New file path
    """
    # Only rename if job is removed
    if status != JOB_STATUS_REMOVED:
        return job_path
        
    directory = job_path.parent
    new_filename = f"job{job_id}_removed.json"
    new_path = directory / new_filename
    
    try:
        # Rename the file
        job_path.rename(new_path)
        logger.info(f"Renamed job file from {job_path.name} to {new_filename}")
        return new_path
    except Exception as e:
        logger.error(f"Error renaming job file {job_path}: {str(e)}")
        return job_path

def process_job_files(job_dir, max_jobs=None, specific_job_ids=None, rename_removed_files=False):
    """
    Process job files and update status
    
    Args:
        job_dir (Path): Directory containing job files
        max_jobs (int): Maximum number of jobs to process
        specific_job_ids (list): List of specific job IDs to process
        rename_removed_files (bool): Whether to rename files for removed jobs
        
    Returns:
        tuple: (processed_count, active_count, removed_count, error_count)
    """
    # Convert job_dir to Path object if it's not already
    job_dir = Path(job_dir)
    
    # Get job files
    if specific_job_ids:
        job_files = []
        for job_id in specific_job_ids:
            job_file = f"job{job_id}.json"
            if (job_dir / job_file).exists():
                job_files.append(job_file)
            else:
                # Also check for renamed files
                removed_file = f"job{job_id}_removed.json"
                if (job_dir / removed_file).exists():
                    job_files.append(removed_file)
    else:
        # Get all job files, including already renamed ones
        job_files = sorted([f for f in os.listdir(job_dir) 
                   if f.startswith('job') and f.endswith('.json')])
    
    logger.info(f"Found {len(job_files)} job files to check")
    
    # Process counters
    processed = 0
    active = 0
    removed = 0
    error = 0
    
    # Process each job file
    for job_file in job_files:
        # Extract job_id from filename, handling both normal and renamed files
        if '_removed' in job_file:
            job_id = job_file.replace('job', '').replace('_removed.json', '')
        else:
            job_id = job_file.replace('job', '').replace('.json', '')
            
        job_path = job_dir / job_file
        
        logger.info(f"Processing job ID {job_id} ({processed+1} of {len(job_files)})")
        
        try:
            # Read job data
            with open(job_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Skip if already marked as removed and has been checked in the last 24 hours
            if "status" in job_data and job_data["status"]["status"] == JOB_STATUS_REMOVED:
                last_checked = datetime.fromisoformat(job_data["status"]["checked_at"])
                now = datetime.now()
                hours_since_check = (now - last_checked).total_seconds() / 3600
                
                if hours_since_check < 24:
                    logger.info(f"Skipping job {job_id} - already marked as removed within 24 hours")
                    processed += 1
                    removed += 1
                    continue
            
            # Get job URL from web_details
            job_url = None
            if "web_details" in job_data and "url" in job_data["web_details"]:
                job_url = job_data["web_details"]["url"]
            
            if not job_url:
                # No URL to check
                job_data = update_job_status(job_data, job_id, False, None, "No URL available to check job status")
                error += 1
            else:
                # Check if job is available
                is_available, status_code, error_message = check_job_availability(job_url)
                
                # Update job data with status
                job_data = update_job_status(job_data, job_id, is_available, status_code, error_message)
                
                if is_available:
                    active += 1
                else:
                    if error_message and "error" in error_message.lower():
                        error += 1
                    else:
                        removed += 1
            
            # Save updated job data
            with open(job_path, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            
            # Rename file if requested and job is removed
            if rename_removed_files and job_data["status"]["status"] == JOB_STATUS_REMOVED:
                job_path = rename_job_file(job_path, job_id, JOB_STATUS_REMOVED)
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            error += 1
        
        processed += 1
        
        # Check if we've reached the maximum
        if max_jobs and processed >= max_jobs:
            logger.info(f"Reached maximum number of jobs to process ({max_jobs})")
            break
            
        # Add small delay between requests to avoid overloading servers
        time.sleep(random.uniform(0.5, 2.0))
    
    logger.info(f"Processing complete. Total: {processed}, Active: {active}, Removed: {removed}, Error: {error}")
    return (processed, active, removed, error)

def check_job_statuses(max_jobs=None, job_ids=None, log_dir=None, rename_removed_files=False):
    """
    Check job statuses and update job files
    
    Args:
        max_jobs (int): Maximum number of jobs to check
        job_ids (list): Specific job IDs to check
        log_dir (Path): Directory for log files
        rename_removed_files (bool): Whether to rename files for removed jobs
        
    Returns:
        bool: Success status
    """
    logger.info(f"Checking job posting statuses...")
    
    # Set up additional log handler if log_dir is provided
    if log_dir:
        status_log_path = os.path.join(log_dir, "status_checker_module.log")
        status_handler = logging.FileHandler(status_log_path)
        status_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(status_handler)
        logger.info(f"Added log handler. Writing to {status_log_path}")
    
    try:
        # Process job files directly
        processed, active, removed, error = process_job_files(
            job_dir=JOB_DATA_DIR,
            max_jobs=max_jobs,
            specific_job_ids=job_ids,
            rename_removed_files=rename_removed_files
        )
        
        # Generate summary report
        logger.info("=" * 50)
        logger.info("Job Status Check Summary")
        logger.info("=" * 50)
        logger.info(f"Total jobs processed: {processed}")
        logger.info(f"Active jobs: {active}")
        logger.info(f"Removed jobs: {removed}")
        logger.info(f"Error checking jobs: {error}")
        logger.info("=" * 50)
        
        # Consider the operation successful if we processed at least one job
        return processed > 0
        
    except Exception as e:
        logger.error(f"Critical error in job status checking: {str(e)}")
        return False

if __name__ == "__main__":
    # Set up basic logging if run directly
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Parse command line arguments if run directly
    import argparse
    parser = argparse.ArgumentParser(description="Check job posting availability")
    parser.add_argument("--max-jobs", type=int, help="Maximum number of jobs to process")
    parser.add_argument("--job-ids", type=str, help="Specific job IDs to process (comma-separated)")
    parser.add_argument("--rename-removed", action="store_true", help="Rename files for removed jobs")
    
    args = parser.parse_args()
    
    # Process job IDs if provided
    job_ids = None
    if args.job_ids:
        job_ids = [job_id.strip() for job_id in args.job_ids.split(",") if job_id.strip()]
    
    # Run the status checker
    success = check_job_statuses(
        max_jobs=args.max_jobs,
        job_ids=job_ids,
        rename_removed_files=args.rename_removed
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
