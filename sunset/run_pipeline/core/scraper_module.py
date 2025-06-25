#!/usr/bin/env python3
"""
Job scraping module for the job expansion pipeline
"""

import os
import sys
import logging
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Import utility modules
from run_pipeline.utils.firefox_utils import check_firefox_installed, ensure_firefox_running
from run_pipeline.config.paths import (
    PROJECT_ROOT, 
    JOB_DATA_DIR
)

logger = logging.getLogger('scraper_module')

# Constants
CAREERS_BASE_URL = "https://careers.db.com/professionals/search-roles/#/professional/job/"
PAGE_LOAD_WAIT = 5  # Seconds to wait for page to load
KEY_PRESS_WAIT = 1  # Seconds to wait after key presses

# Firefox tab management functions
def is_firefox_running():
    """Check if Firefox is already running"""
    try:
        result = subprocess.run(['pgrep', '-f', 'firefox'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error checking if Firefox is running: {str(e)}")
        return False

def open_url_in_firefox(url):
    """Open a URL in Firefox in a new tab"""
    try:
        if not url:
            logger.error("No URL provided")
            return False
            
        # Use xdg-open which will open in a new tab if Firefox is already running
        logger.info(f"Opening URL in Firefox: {url}")
        subprocess.run(['xdg-open', url])
        
        # Give browser time to open the tab
        time.sleep(2)
        return True
    except Exception as e:
        logger.error(f"Error opening URL in Firefox: {str(e)}")
        return False

def close_current_tab():
    """Close the current tab in Firefox using keyboard shortcut Ctrl+W"""
    try:
        logger.info("Closing current Firefox tab")
        subprocess.run(['xdotool', 'key', 'ctrl+w'])
        return True
    except Exception as e:
        logger.error(f"Error closing tab: {str(e)}")
        return False

def extract_job_with_firefox_tab(job_id, save_html=True, max_retries=3, retry_delay=2):
    """
    Extract job details using Firefox tab management approach
    
    Args:
        job_id (str): Job ID to extract
        save_html (bool): Whether to save the HTML content to file
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Delay in seconds between retries
        
    Returns:
        dict: Dictionary containing job details
    """
    # Create HTML content directory if it doesn't exist
    if save_html:
        output_dir = JOB_DATA_DIR / "html_content"
        output_dir.mkdir(parents=True, exist_ok=True)
        
    # Construct full URL
    url = f"{CAREERS_BASE_URL}{job_id}"
    
    # Check if Firefox is running
    if not is_firefox_running():
        logger.error("Firefox is not running. Please start Firefox first!")
        return None
    
    logger.info(f"Extracting job details for job ID: {job_id} from URL: {url}")
    
    # Initialize retry counter
    retry_count = 0
    
    # Try to open the URL with retries
    while retry_count < max_retries:
        # Open the job page in a new Firefox tab
        logger.debug(f"Opening URL in Firefox: {url} (Attempt {retry_count+1}/{max_retries})")
        if not open_url_in_firefox(url):
            logger.warning(f"Failed to open URL in Firefox: {url} (Attempt {retry_count+1}/{max_retries})")
            retry_count += 1
            if retry_count < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Failed to open URL after {max_retries} attempts")
                return None
        else:
            # Successfully opened URL
            break
    
    # Wait for the page to load properly
    logger.debug(f"Waiting {PAGE_LOAD_WAIT} seconds for page to fully load...")
    time.sleep(PAGE_LOAD_WAIT)
    
    # Extract content using keyboard shortcuts and clipboard with retries
    extracted_content = None
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Select all text (Ctrl+A)
            logger.debug(f"Selecting all text with Ctrl+A... (Attempt {retry_count+1}/{max_retries})")
            subprocess.run(['xdotool', 'key', 'ctrl+a'])
            time.sleep(KEY_PRESS_WAIT)
            
            # Copy selected text (Ctrl+C)
            logger.debug(f"Copying text with Ctrl+C... (Attempt {retry_count+1}/{max_retries})")
            subprocess.run(['xdotool', 'key', 'ctrl+c'])
            time.sleep(KEY_PRESS_WAIT)
            
            # Get clipboard content
            logger.debug("Getting clipboard content...")
            clipboard_content = subprocess.run(['xclip', '-o', '-selection', 'clipboard'], 
                                           capture_output=True, 
                                           text=True).stdout
            
            # Check if we have meaningful content (more than just a few characters)
            if clipboard_content and len(clipboard_content) > 100:
                # Save the extracted content
                extracted_content = clipboard_content
                
                # Save HTML content to file if requested
                if save_html and extracted_content:
                    output_file = output_dir / f"db_job_{job_id}_content.txt"
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(clipboard_content)
                        
                    logger.debug(f"Saved HTML content to: {output_file}")
                
                # Successfully extracted content, break out of retry loop
                break
            else:
                # Not enough content, try again
                logger.warning(f"Extracted content too short ({len(clipboard_content) if clipboard_content else 0} chars)")
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"Retrying extraction in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed to extract meaningful content after {max_retries} attempts")
                
        except Exception as e:
            logger.warning(f"Error extracting content (Attempt {retry_count+1}/{max_retries}): {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                logger.info(f"Retrying extraction in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to extract content after {max_retries} attempts: {str(e)}")
        
    # Close the tab but keep Firefox running
    logger.debug("Closing tab while keeping Firefox running...")
    if not close_current_tab():
        logger.warning("Failed to close tab")
    
    # If we didn't get any content, return None
    if not extracted_content:
        logger.error("Failed to extract content")
        return None
    
    # Parse the extracted content
    full_description = extracted_content
    
    # Extract sections (this is a simplified version)
    sections = {}
    
    # Create the job details dictionary
    job_details = {
        'job_id': job_id,
        'raw_content': extracted_content,
        # Don't include full_description to reduce file size
        'sections': sections,
        'extraction_method': 'firefox_tab_manager'
    }
    
    logger.info(f"Successfully extracted {len(extracted_content)} bytes of content for job ID: {job_id}")
    return job_details

def scrape_job_details(max_jobs=None, job_ids=None, skip_firefox_check=False, log_dir=None, only_missing_html=False):
    """
    Scrape job details using Firefox automation
    
    Args:
        max_jobs (int): Maximum number of jobs to process
        job_ids (list): Specific job IDs to process
        skip_firefox_check (bool): Whether to skip Firefox check
        log_dir (Path): Directory for log files
        only_missing_html (bool): Only process jobs without HTML content
        
    Returns:
        bool: Success status
    """
    logger.info("Scraping job details using Firefox automation...")
    
    # Set up additional log handler if log_dir is provided
    if log_dir:
        scrape_log_path = os.path.join(log_dir, "job_detail_scraping.log")
        scrape_handler = logging.FileHandler(scrape_log_path)
        scrape_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(scrape_handler)
    
    # Check for Firefox if not skipped
    if not skip_firefox_check:
        if not check_firefox_installed():
            logger.error("Firefox is required for job scraping but was not found.")
            return False
            
        if not ensure_firefox_running():
            logger.error("Could not ensure Firefox is running. Job scraping requires Firefox.")
            return False
    
    # Set up job directory
    job_directory = JOB_DATA_DIR
    
    # If only_missing_html is True, get job IDs of jobs without HTML content
    if only_missing_html:
        missing_html_ids = get_jobs_without_html_content(job_directory)
        if missing_html_ids:
            logger.info(f"Found {len(missing_html_ids)} jobs missing HTML content")
            job_ids = missing_html_ids
        else:
            logger.info("No jobs missing HTML content found")
            return True  # Success, nothing to do
    
    # Get job files to process
    if job_ids:
        job_files = []
        for job_id in job_ids:
            job_file = job_directory / f"job{job_id}.json"
            if job_file.exists():
                job_files.append(job_file)
            else:
                logger.warning(f"Job file for ID {job_id} not found at {job_file}")
    else:
        job_files = sorted(list(job_directory.glob("job*.json")))
        
    # Filter to jobs that haven't been scraped yet (unless only_missing_html is True)
    jobs_to_scrape = []
    if not only_missing_html:
        for job_file in job_files:
            try:
                with open(job_file, 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                    
                # Check if job has already been scraped
                # We check for HTML content files instead of full_description in the JSON
                html_content_file = JOB_DATA_DIR / "html_content" / f"db_job_{job_file.stem.replace('job', '')}_content.txt"
                if html_content_file.exists():
                    logger.info(f"Job {job_file.name} already scraped (HTML content found), skipping")
                    continue
                    
                jobs_to_scrape.append(job_file)
            except Exception as e:
                logger.error(f"Error processing {job_file}: {str(e)}")
    else:
        # If only_missing_html is True, we've already filtered for jobs without HTML content
        jobs_to_scrape = job_files
    
    # Limit to max jobs if specified
    if max_jobs is not None and len(jobs_to_scrape) > max_jobs:
        jobs_to_scrape = jobs_to_scrape[:max_jobs]
    
    logger.info(f"Found {len(jobs_to_scrape)} job files to scrape")
    
    # Initialize Firefox and scrape each job
    success_count = 0
    failure_count = 0
    
    # Process each job
    for job_file in jobs_to_scrape:
        try:
            job_id = job_file.stem.replace('job', '')
            logger.info(f"Processing job ID: {job_id}")
            
            # Extract job details
            job_details = extract_job_with_firefox_tab(job_id)
            
            if job_details and job_details.get('raw_content'):
                # Read existing job data
                with open(job_file, 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                
                # Update job data with scraped content
                # We no longer store the full_description field
                # to reduce file size and unnecessary data storage
                
                # Update metadata
                if 'metadata' not in job_data:
                    job_data['metadata'] = {}
                
                now = datetime.now().isoformat()
                if 'last_updated' not in job_data['metadata']:
                    job_data['metadata']['last_updated'] = {}
                job_data['metadata']['last_updated']['scraped_at'] = now
                
                # Add log entry
                if 'log' not in job_data:
                    job_data['log'] = []
                
                job_data['log'].append({
                    "timestamp": now,
                    "module": "run_pipeline.core.scraper_module",
                    "action": "scrape_job_details",
                    "message": f"Scraped job details for job ID {job_id}"
                })
                
                # Save updated job data
                with open(job_file, 'w', encoding='utf-8') as f:
                    json.dump(job_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Successfully scraped job details for job ID {job_id}")
                success_count += 1
            else:
                logger.error(f"Failed to extract content for job ID {job_id}")
                failure_count += 1
        except Exception as e:
            logger.error(f"Error processing job file {job_file}: {str(e)}")
            failure_count += 1
    
    logger.info(f"Job scraping complete. Success: {success_count}, Failure: {failure_count}")
    # Always return True to continue pipeline - we don't want to fail the entire pipeline
    # because we couldn't scrape some jobs
    return True

def get_jobs_without_html_content(job_dir):
    """
    Get a list of job IDs that don't have HTML content
    
    Args:
        job_dir (Path): Directory containing job files
        
    Returns:
        list: List of job IDs without HTML content
    """
    job_dir = Path(job_dir)
    jobs_without_html = []
    html_content_dir = job_dir / "html_content"
    job_files = sorted(list(job_dir.glob("job*.json")))
    
    logger.info(f"Scanning {len(job_files)} jobs for missing HTML content")
    
    for job_file in job_files:
        try:
            job_id = job_file.stem.replace('job', '')
            
            # Check if job has HTML content in any of these places:
            # 1. web_details.full_description in the job JSON
            # 2. html_content directory
            
            has_html = False
            
            # Check job JSON first (note: we no longer store full_description in the JSON)
            # Check only for HTML content files instead
            has_html = False
            
            # If not in job JSON, check html_content directory
            if not has_html:
                html_content_file = html_content_dir / f"db_job_{job_id}_content.txt"
                if html_content_file.exists():
                    has_html = True
            
            if not has_html:
                jobs_without_html.append(job_id)
                
        except Exception as e:
            logger.error(f"Error checking job file {job_file}: {str(e)}")
            jobs_without_html.append(job_file.stem.replace('job', ''))
    
    logger.info(f"Found {len(jobs_without_html)} jobs without HTML content")
    return jobs_without_html
