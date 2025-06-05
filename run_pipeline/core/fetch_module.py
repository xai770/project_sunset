#!/usr/bin/env python3
"""
Fetch job metadata module for the job expansion pipeline.
Integrated with db_search_api_scanner approach for efficient job retrieval.

This module utilizes the Deutsche Bank career search API to efficiently
find and save job postings. Instead of sequentially checking individual job IDs,
it leverages the search API to retrieve batches of existing jobs directly.

By default, this scanner filters for jobs with Country code 46 (Germany) 
and City code 1698 (Frankfurt). This filtering can be modified using 
parameters to the fetch_job_metadata function.

Features:
- Direct API querying with pagination
- Default filtering for Frankfurt, Germany jobs
- Efficient batch retrieval
- Automated saving of found jobs
- Resumable operation with progress tracking
"""

import os
import sys
import json
import time
import random
import logging
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# Import from submodules
from run_pipeline.core.fetch.api import (
    fetch_job_batch,
    fetch_job_details
)
from run_pipeline.core.fetch.progress import (
    ensure_directories,
    load_progress,
    save_progress
)
from run_pipeline.core.fetch.job_processing import (
    process_and_save_jobs,
    extract_job_id_from_position_id
)

# Import utility modules
from run_pipeline.config.paths import (
    PROJECT_ROOT,
    JOB_DATA_DIR
)

logger = logging.getLogger('fetch_module')

# Default search parameters
DEFAULT_RESULTS_PER_PAGE = 100  # Fetch more results per request
DEFAULT_MAX_PAGES = 10  # Maximum number of pages to fetch
REQUEST_DELAY = 2  # Base delay between requests in seconds


def fetch_job_metadata(max_jobs, log_dir=None, force_reprocess=False, 
                      country_code=46, city_code=1698, results_per_page=DEFAULT_RESULTS_PER_PAGE):
    """
    Fetch job metadata from the Deutsche Bank careers API.
    Always starts fresh from page 1 since search results change over time.
    
    Args:
        max_jobs (int): Maximum number of jobs to fetch
        log_dir (Path): Directory for log files
        force_reprocess (bool): Whether to reprocess jobs that already exist and clear progress
        country_code (int, optional): Country code to filter by (46=Germany)
        city_code (int, optional): City code to filter by (1698=Frankfurt)
        results_per_page (int, optional): Number of results to fetch per page
        
    Returns:
        bool: Success status
    """
    logger.info(f"Fetching job metadata from Deutsche Bank API (max: {max_jobs} jobs, force_reprocess: {force_reprocess})...")
    
    # Ensure data directory exists
    JOB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Set up additional log handler if log_dir is provided
    if log_dir:
        ensure_log_directory(log_dir)
        fetch_log_path = os.path.join(log_dir, "fetch_module.log")
        fetch_handler = logging.FileHandler(fetch_log_path)
        fetch_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(fetch_handler)
        logger.info(f"Added log handler. Writing to {fetch_log_path}")
    
    try:
        # Calculate max pages based on max_jobs and results per page
        max_pages = (max_jobs + results_per_page - 1) // results_per_page
        
        logger.info(f"Starting search API scan for jobs in Frankfurt, Germany")
        
        # Run the search API scan with specified parameters
        success, jobs = scan_search_api(
            max_pages=max_pages,
            results_per_page=results_per_page,
            country_code=country_code,
            city_code=city_code,
            force_start=force_reprocess  # If true, clear job processing history completely
        )
        
        if not success or not jobs:
            logger.error("Failed to fetch any jobs. Exiting.")
            return False
            
        job_count = len(jobs)
        logger.info(f"Successfully fetched {job_count} jobs from API")
        
        # Convert the dictionary of jobs to a list for processing
        job_list = list(jobs.values())
        
        if not job_list:
            logger.error("Job list is empty after conversion. Exiting.")
            return False
            
        # Process and save jobs
        processed_count, skipped_count = process_and_save_jobs(
            job_list, 
            JOB_DATA_DIR, 
            generate_daily_summary=True,
            force_reprocess=force_reprocess
        )
        
        logger.info(f"Job processing completed. Processed {processed_count} jobs, skipped {skipped_count} jobs")
        logger.info(f"Individual job files saved to {JOB_DATA_DIR}")
        
        return processed_count > 0  # Return success only if we processed at least one job
    except Exception as e:
        logger.error(f"Error in fetch_job_metadata: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def ensure_log_directory(log_dir):
    """Ensure log directory exists."""
    if isinstance(log_dir, str):
        log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def scan_search_api(max_pages=DEFAULT_MAX_PAGES, results_per_page=DEFAULT_RESULTS_PER_PAGE, 
                    country_code=None, city_code=None, delay=REQUEST_DELAY, force_start=False):
    """
    Scan the search API for jobs, processing multiple pages of results.
    Always starts from page 1 regardless of previous progress, as search content changes over time.
    
    Args:
        max_pages (int): Maximum number of pages to fetch
        results_per_page (int): Number of results per page
        country_code (int): Country code filter (optional)
        city_code (int): City code filter (optional)
        delay (float): Delay between requests
        force_start (bool): Force clearing previous progress data completely
        
    Returns:
        tuple: (success, job_dict)
    """
    # Ensure directories exist
    ensure_directories()
    
    # Load progress if exists (force_start will clear job history if true)
    progress = load_progress(force_clear=force_start)
    
    # Always start from page 1 as search pages content changes over time
    current_page = 1
    
    if force_start:
        logger.info("Starting fresh search with cleared job history")
    else:
        logger.info("Starting new search from page 1, keeping previously processed job history")
    
    # Create a session for job details requests
    details_session = requests.Session()
    
    # Track if we've reached the end
    reached_end = False
    total_jobs_found = 0
    total_results = 0
    all_jobs = {}  # Dictionary of job_id -> job_data
    
    # Calculate maximum number of jobs to fetch - use max_pages * results_per_page to get actual job count
    max_jobs_to_fetch = max_pages * results_per_page  # Max number of jobs to fetch
    logger.info(f"Will fetch maximum of {max_jobs_to_fetch} jobs")
    
    try:
        jobs_processed = 0  # Counter for jobs successfully processed in this run
        
        # Stop fetching once we've processed enough jobs or reached other limits
        while current_page <= max_pages and not reached_end and jobs_processed < max_jobs_to_fetch:
            # Fetch the current page of results
            success, job_batch, batch_total = fetch_job_batch(
                page=current_page,
                count_per_page=results_per_page,
                country_code=country_code,
                city_code=city_code
            )
            
            # Update total results if this is the first successful fetch
            if success and total_results == 0:
                total_results = batch_total
                logger.info(f"Total jobs available: {total_results}")
            
            if success and job_batch:
                # Update progress
                progress["last_page_fetched"] = current_page
                progress["stats"]["total_pages_fetched"] += 1
                
                job_batch_count = len(job_batch)
                logger.info(f"Processing {job_batch_count} jobs from page {current_page}")
                
                # Process each job in the batch
                # Break early if we've already reached our job limit
                if jobs_processed >= max_jobs_to_fetch:
                    logger.info(f"Already processed {jobs_processed} jobs, stopping batch processing")
                    reached_end = True
                    break
                    
                for job_index, job_item in enumerate(job_batch):
                    # Break if we've reached our job limit during batch processing
                    if jobs_processed >= max_jobs_to_fetch:
                        logger.info(f"Reached max jobs to fetch ({max_jobs_to_fetch})")
                        reached_end = True
                        break
                        
                    # Extract job ID from the job item
                    matched_object = job_item.get("MatchedObjectDescriptor", {})
                    
                    # Handle case where matched_object could be a list instead of dict
                    if isinstance(matched_object, list):
                        logger.debug("MatchedObjectDescriptor is a list, using first item if available")
                        if matched_object:  # Check if list is not empty
                            matched_object = matched_object[0]
                        else:
                            logger.warning("Empty MatchedObjectDescriptor list, skipping job item")
                            continue
                    
                    # Now get position ID from the matched_object
                    position_id = matched_object.get("PositionID") if isinstance(matched_object, dict) else None
                    job_id = extract_job_id_from_position_id(position_id)
                    
                    if job_id is not None:
                        logger.debug(f"Processing job {job_index+1}/{job_batch_count}: ID {job_id}")
                        
                        # Check if we've already processed this job
                        if job_id in progress["jobs_processed"] and not force_start:
                            logger.debug(f"Skipping already processed job ID {job_id}")
                            continue
                        
                        # Fetch detailed job information
                        detail_success, job_details = fetch_job_details(job_id, details_session)
                        
                        if detail_success and job_details:
                            logger.debug(f"Successfully fetched details for job ID {job_id}")
                            
                            # Create standardized job data structure for processing
                            # Safely access dictionary values with proper type checking
                            job_title = matched_object.get('PositionTitle', '') if isinstance(matched_object, dict) else ''
                            
                            # Handle nested dictionaries with safe access
                            career_level = matched_object.get('CareerLevel', {}) if isinstance(matched_object, dict) else {}
                            job_career_level = career_level.get('Name', '') if isinstance(career_level, dict) else ''
                            
                            job_date_posted = matched_object.get('PublicationStartDate', '') if isinstance(matched_object, dict) else ''
                            
                            # Add job to our collection
                            all_jobs[job_id] = {
                                "job_id": job_id,
                                "title": job_title,
                                "career_level": job_career_level,
                                "date_posted": job_date_posted,
                                "api_details": job_details,
                                "search_details": matched_object
                            }
                            
                            # Update progress and stats
                            if job_id not in progress["jobs_processed"]:
                                progress["jobs_processed"].append(job_id)
                            
                            progress["stats"]["total_jobs_processed"] += 1
                            total_jobs_found += 1
                            jobs_processed += 1
                            
                            # Log progress periodically
                            if total_jobs_found % 10 == 0 or total_jobs_found == 1:
                                logger.info(f"Processed {total_jobs_found} jobs so far")
                            
                            # Save progress periodically
                            if total_jobs_found % 10 == 0:
                                save_progress(progress)
                                
                            # Check if we've reached the max jobs to fetch
                            if jobs_processed >= max_jobs_to_fetch:
                                logger.info(f"Reached max jobs to fetch ({max_jobs_to_fetch})")
                                reached_end = True
                                break
                        else:
                            logger.warning(f"Failed to fetch details for job ID {job_id}")
                        
                        # Add delay between job detail requests
                        sleep_time = delay + (random.random() * delay)
                        time.sleep(sleep_time)
                    else:
                        logger.warning(f"Could not extract job ID from position ID {position_id}")
                
                # After processing the batch, update stats
                logger.info(f"Completed page {current_page}, total jobs processed: {total_jobs_found}")
                
                # Move to the next page
                current_page += 1
                
                # Check if we've reached the end
                if len(job_batch) < results_per_page or current_page > (total_results // results_per_page + 1):
                    logger.info("Reached the end of available results")
                    reached_end = True
                
                # Add delay between page requests
                sleep_time = delay + (random.random() * delay)
                logger.debug(f"Sleeping for {sleep_time:.2f} seconds before next page")
                time.sleep(sleep_time)
            else:
                # No results or fetch failed
                logger.warning(f"Failed to fetch page {current_page} or no results returned")
                
                # Increment page to avoid getting stuck
                current_page += 1
                
                # If several consecutive pages fail, we might have reached the end
                if current_page - progress["last_page_fetched"] > 3:
                    logger.info("Multiple consecutive page failures, assuming end of results")
                    reached_end = True
                
                # Add delay before retry
                time.sleep(delay * 2)
                
    except KeyboardInterrupt:
        logger.info("Scan interrupted by user")
    finally:
        # Update progress stats
        progress["stats"]["total_jobs_found"] = total_jobs_found
        progress["last_page_fetched"] = current_page - 1  # Store the last page we actually fetched
        
        # Save final progress
        save_progress(progress)
        
        # Print summary
        logger.info("\nScan Summary:")
        logger.info(f"Total pages fetched: {progress['stats']['total_pages_fetched']}")
        logger.info(f"Total jobs found: {total_jobs_found}")
        logger.info(f"Total jobs processed: {progress['stats']['total_jobs_processed']}")
        logger.info("Note: Next scan will start fresh from page 1 regardless of progress")
    
    # Check if we found any jobs and return accordingly
    if total_jobs_found > 0:
        logger.info(f"Successfully found and processed {total_jobs_found} jobs")
        return True, all_jobs
    else:
        logger.warning("No jobs were found or processed in this scan")
        return False, {}
