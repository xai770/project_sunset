#!/usr/bin/env python3
"""
Job ID Scanner Module

This module systematically scans for job IDs in a specified range and attempts to
identify valid jobs that might not be accessible through the API. It uses a hybrid
approach of API checking and direct URL access.
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
from bs4 import BeautifulSoup
import concurrent.futures

# Add project root to path to allow importing modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR
from run_pipeline.utils.process_utils import run_process

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('job_id_scanner')

# Constants
JOB_URL_TEMPLATE = "https://careers.db.com/professionals/search-roles/#/professional/job/{job_id}"
JOB_ALT_URL_TEMPLATE = "https://careers.db.com/index.php?ac=jobad&id={job_id}"
API_URL_TEMPLATE = "https://api-deutschebank.beesite.de/search/v2/"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def check_api_for_job(job_id, session=None):
    """
    Check if a job ID is available via the API.
    
    Args:
        job_id (int): The job ID to check
        session (requests.Session): Session object
        
    Returns:
        dict: API response or None
    """
    if session is None:
        session = requests.Session()
    
    try:
        logger.debug(f"Checking API for job ID {job_id}...")
        
        # Create API request body
        api_body = {
            "PositionID": str(job_id)
        }
        
        # Try V2 API
        response = session.post(
            API_URL_TEMPLATE,
            headers=API_HEADERS,
            json=api_body,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Check if we got any results
            search_result = response_data.get("SearchResult", {})
            result_items = search_result.get("SearchResultItems", [])
            
            if result_items:
                for item in result_items:
                    if item.get("MatchedObjectId") == str(job_id):
                        logger.info(f"Found job ID {job_id} in API response")
                        return item
            
            logger.debug(f"Job ID {job_id} not found in API response")
            return None
        else:
            logger.warning(f"API returned status code {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error checking API for job ID {job_id}: {e}")
        return None

def check_job_url(job_id, session=None):
    """
    Check if a job URL is accessible.
    
    Args:
        job_id (int): The job ID to check
        session (requests.Session): Session object
        
    Returns:
        dict: Result of URL check
    """
    result = {
        "job_id": job_id,
        "accessible": False,
        "status_code": None,
        "redirected": False,
        "final_url": None,
        "has_job_content": False,
        "title": None,
        "location": None
    }
    
    if session is None:
        session = requests.Session()
    
    url = JOB_URL_TEMPLATE.format(job_id=job_id)
    
    try:
        logger.debug(f"Checking URL for job ID {job_id}: {url}")
        
        response = session.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        result["status_code"] = response.status_code
        result["final_url"] = response.url
        
        # Check if there was a redirect
        if response.url != url:
            result["redirected"] = True
            
        # If we got a success response, check the content
        if response.status_code == 200:
            result["accessible"] = True
            
            # Check if the content contains job-specific information
            html_content = response.text
            has_job_content = check_for_job_content(html_content, job_id)
            
            if has_job_content:
                result["has_job_content"] = True
                # Extract job title and location
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract title
                title_tag = soup.find('h1', class_='position-title')
                if title_tag:
                    result["title"] = title_tag.get_text(strip=True)
                    
                # Extract location
                location_tag = soup.find('div', class_='location') or soup.find('span', class_='location')
                if location_tag:
                    result["location"] = location_tag.get_text(strip=True)
                    
        return result
                
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error accessing URL for job ID {job_id}: {e}")
        return result

def check_for_job_content(html_content, job_id):
    """
    Check if HTML content contains job-specific information.
    
    Args:
        html_content (str): HTML content to check
        job_id (int): Job ID
        
    Returns:
        bool: True if content appears to be for a specific job
    """
    # Simple heuristics to determine if this is a real job page
    # and not just the generic search page
    
    # Check if the job ID appears in the content
    if str(job_id) in html_content:
        return True
        
    # Look for job detail container
    if '<div class="job-detail">' in html_content or '<div id="job-detail">' in html_content:
        return True
        
    # Look for job title heading
    if '<h1 class="position-title">' in html_content:
        return True
        
    return False

def save_discovered_job(job_id, job_data, output_dir):
    """
    Save discovered job data to a JSON file.
    
    Args:
        job_id (int): Job ID
        job_data (dict): Job data to save
        output_dir (Path): Output directory
        
    Returns:
        bool: Success status
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Define output file path
        output_file = os.path.join(output_dir, f"job{job_id}.json")
        
        # Check if file already exists
        if os.path.exists(output_file):
            # Read existing data
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                
            # Update existing data
            existing_data["discovery_update"] = {
                "timestamp": datetime.now().isoformat(),
                "method": "job_id_scanner",
                "data": job_data
            }
            
            # Add log entry
            if "log" not in existing_data:
                existing_data["log"] = []
                
            existing_data["log"].append({
                "timestamp": datetime.now().isoformat(),
                "module": "job_id_scanner",
                "action": "update_job_data",
                "message": f"Updated job data for job ID {job_id}"
            })
            
            # Save updated data
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Updated existing job data file: {output_file}")
            
        else:
            # Create new job entry
            job_entry = {
                "job_id": job_id,
                "title": job_data.get("title", ""),
                "url": JOB_URL_TEMPLATE.format(job_id=job_id),
                "detail_url": f"https://careers.db.com/professionals/search-roles/#/professional/job/{job_id}",
                "api_found": job_data.get("api_found", False),
                "discovery_method": "job_id_scanner",
                "discovery_timestamp": datetime.now().isoformat(),
                "discovery_data": job_data,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": {
                        "discovered_at": datetime.now().isoformat()
                    }
                },
                "log": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "module": "job_id_scanner",
                        "action": "create_job_data",
                        "message": f"Created job data for job ID {job_id}"
                    }
                ]
            }
            
            # Save new data
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(job_entry, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Created new job data file: {output_file}")
            
        return True
            
    except Exception as e:
        logger.error(f"Error saving job data for job ID {job_id}: {e}")
        return False

def scan_job_id(job_id, output_dir=None):
    """
    Scan a specific job ID using multiple methods.
    
    Args:
        job_id (int): Job ID to scan
        output_dir (str): Output directory for job data
        
    Returns:
        dict: Scan results
    """
    if output_dir is None:
        output_dir = JOB_DATA_DIR
        
    session = requests.Session()
    result = {
        "job_id": job_id,
        "api_found": False,
        "url_accessible": False,
        "has_job_content": False,
        "is_valid_job": False,
        "title": None,
        "location": None,
        "saved": False
    }
    
    # First check via API (faster and more reliable)
    api_result = check_api_for_job(job_id, session)
    if api_result:
        result["api_found"] = True
        
        # Extract title and other details from API
        if "MatchedObjectDescriptor" in api_result:
            descriptor = api_result["MatchedObjectDescriptor"]
            result["title"] = descriptor.get("PositionTitle", "").replace("&amp;", "&")
            
            # Extract locations
            locations = []
            if "PositionLocation" in descriptor:
                for loc in descriptor["PositionLocation"]:
                    city = loc.get("CityName", "").strip()
                    country = loc.get("CountryName", "").strip()
                    locations.append(f"{city}, {country}")
                    
            result["location"] = "; ".join(locations)
            
        # API found the job, it's valid
        result["is_valid_job"] = True
        
        # Save the discovered job
        job_data = {
            "api_found": True,
            "title": result["title"],
            "location": result["location"],
            "api_data": api_result,
            "url_check": None  # We don't need to check URL if API found it
        }
        
        result["saved"] = save_discovered_job(job_id, job_data, output_dir)
        
        logger.info(f"Job ID {job_id} found via API: {result['title']}")
        return result
    
    # If not found via API, check URL
    url_result = check_job_url(job_id, session)
    result["url_accessible"] = url_result["accessible"]
    result["has_job_content"] = url_result["has_job_content"]
    
    if url_result["has_job_content"]:
        result["is_valid_job"] = True
        result["title"] = url_result["title"]
        result["location"] = url_result["location"]
        
        # Save the discovered job
        job_data = {
            "api_found": False,
            "title": result["title"],
            "location": result["location"],
            "api_data": None,
            "url_check": url_result
        }
        
        result["saved"] = save_discovered_job(job_id, job_data, output_dir)
        
        logger.info(f"Job ID {job_id} found via URL (not in API): {result['title']}")
    else:
        logger.debug(f"Job ID {job_id} not found via API or URL")
    
    return result

def scan_job_range(start_id, end_id, output_dir=None, delay=1, concurrent=False, save_results=True, max_workers=5):
    """
    Scan a range of job IDs.
    
    Args:
        start_id (int): Starting job ID
        end_id (int): Ending job ID
        output_dir (str): Output directory for job data
        delay (float): Delay between requests in seconds
        concurrent (bool): Whether to use concurrent processing
        save_results (bool): Whether to save overall results
        max_workers (int): Maximum number of concurrent workers
        
    Returns:
        dict: Scan statistics and results
    """
    if output_dir is None:
        output_dir = JOB_DATA_DIR
        
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create results directory if saving results
    results_dir = os.path.join(output_dir, "scan_results")
    if save_results:
        os.makedirs(results_dir, exist_ok=True)
    
    # Initialize stats
    stats = {
        "start_time": datetime.now().isoformat(),
        "start_id": start_id,
        "end_id": end_id,
        "total_ids": end_id - start_id + 1,
        "found_jobs": 0,
        "api_found": 0,
        "url_found": 0,
        "potential_frankfurt_jobs": 0
    }
    
    # Store all scan results
    all_results = []
    
    logger.info(f"Starting scan of job IDs from {start_id} to {end_id}")
    
    if concurrent:
        # Use concurrent processing for faster scanning
        logger.info(f"Using concurrent processing with {max_workers} workers")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a mapping of futures to job IDs
            future_to_job_id = {
                executor.submit(scan_job_id, job_id, output_dir): job_id
                for job_id in range(start_id, end_id + 1)
            }
            
            # Process results as they complete
            for i, future in enumerate(concurrent.futures.as_completed(future_to_job_id)):
                job_id = future_to_job_id[future]
                try:
                    result = future.result()
                    all_results.append(result)
                    
                    # Update statistics
                    if result["is_valid_job"]:
                        stats["found_jobs"] += 1
                        if result["api_found"]:
                            stats["api_found"] += 1
                        else:
                            stats["url_found"] += 1
                            
                        # Check if the job might be in Frankfurt
                        if result["location"] and "frankfurt" in result["location"].lower():
                            stats["potential_frankfurt_jobs"] += 1
                    
                    # Log progress periodically
                    if (i + 1) % 10 == 0 or (i + 1) == stats["total_ids"]:
                        progress_pct = round((i + 1) / stats["total_ids"] * 100, 1)
                        logger.info(f"Progress: {i + 1}/{stats['total_ids']} ({progress_pct}%) - Found {stats['found_jobs']} jobs so far")
                        
                except Exception as e:
                    logger.error(f"Error processing job ID {job_id}: {e}")
    else:
        # Use sequential processing
        for i, job_id in enumerate(range(start_id, end_id + 1)):
            try:
                # Scan this job ID
                result = scan_job_id(job_id, output_dir)
                all_results.append(result)
                
                # Update statistics
                if result["is_valid_job"]:
                    stats["found_jobs"] += 1
                    if result["api_found"]:
                        stats["api_found"] += 1
                    else:
                        stats["url_found"] += 1
                        
                    # Check if the job might be in Frankfurt
                    if result["location"] and "frankfurt" in result["location"].lower():
                        stats["potential_frankfurt_jobs"] += 1
                
                # Log progress periodically
                if (i + 1) % 10 == 0 or (i + 1) == stats["total_ids"]:
                    progress_pct = round((i + 1) / stats["total_ids"] * 100, 1)
                    logger.info(f"Progress: {i + 1}/{stats['total_ids']} ({progress_pct}%) - Found {stats['found_jobs']} jobs so far")
                    
                # Add random delay between requests
                if i < stats["total_ids"] - 1:  # No delay after the last item
                    time.sleep(delay * (0.5 + random.random()))
                    
            except Exception as e:
                logger.error(f"Error processing job ID {job_id}: {e}")
    
    # Complete stats
    stats["end_time"] = datetime.now().isoformat()
    duration_seconds = (datetime.fromisoformat(stats["end_time"]) - 
                       datetime.fromisoformat(stats["start_time"])).total_seconds()
    stats["duration_seconds"] = duration_seconds
    stats["jobs_per_second"] = round(stats["total_ids"] / duration_seconds, 2) if duration_seconds > 0 else 0
    
    # Save overall results if requested
    if save_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f"job_scan_{start_id}_to_{end_id}_{timestamp}.json"
        results_path = os.path.join(results_dir, results_filename)
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump({
                "stats": stats,
                "results": [r for r in all_results if r["is_valid_job"]]  # Only save valid jobs
            }, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved scan results to {results_path}")
    
    # Log summary
    logger.info("Scan complete! Summary:")
    logger.info(f"  Total IDs scanned: {stats['total_ids']}")
    logger.info(f"  Jobs found: {stats['found_jobs']} ({round(stats['found_jobs']/stats['total_ids']*100, 1)}%)")
    logger.info(f"  API found: {stats['api_found']}")
    logger.info(f"  URL found (not in API): {stats['url_found']}")
    logger.info(f"  Potential Frankfurt jobs: {stats['potential_frankfurt_jobs']}")
    logger.info(f"  Duration: {duration_seconds} seconds ({stats['jobs_per_second']} jobs/second)")
    
    return {
        "stats": stats,
        "results": [r for r in all_results if r["is_valid_job"]]  # Only return valid jobs
    }

def scan_specific_ranges():
    """
    Scan specific ranges that are likely to contain missing jobs.
    Based on our analysis, we know that job ID 58005 exists but isn't in the API.
    """
    # Define ranges to scan
    ranges_to_scan = [
        (57900, 58100),  # Around the known missing job 58005
        (58200, 58400),  # Extend further in case there are more
    ]
    
    all_stats = []
    all_results = []
    
    for start_id, end_id in ranges_to_scan:
        logger.info(f"Scanning range {start_id} to {end_id}")
        result = scan_job_range(start_id, end_id)
        all_stats.append(result["stats"])
        all_results.extend(result["results"])
    
    # Summarize all ranges
    total_scanned = sum(stat["total_ids"] for stat in all_stats)
    total_found = sum(stat["found_jobs"] for stat in all_stats)
    total_api = sum(stat["api_found"] for stat in all_stats)
    total_url = sum(stat["url_found"] for stat in all_stats)
    total_frankfurt = sum(stat["potential_frankfurt_jobs"] for stat in all_stats)
    
    logger.info("Overall Summary:")
    logger.info(f"  Total IDs scanned: {total_scanned}")
    logger.info(f"  Jobs found: {total_found} ({round(total_found/total_scanned*100, 1)}%)")
    logger.info(f"  API found: {total_api}")
    logger.info(f"  URL found (not in API): {total_url}")
    logger.info(f"  Potential Frankfurt jobs: {total_frankfurt}")
    
    return all_results

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Job ID Scanner')
    parser.add_argument('--start', type=int, help='Starting job ID')
    parser.add_argument('--end', type=int, help='Ending job ID')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds')
    parser.add_argument('--concurrent', action='store_true', help='Use concurrent processing')
    parser.add_argument('--workers', type=int, default=5, help='Maximum number of concurrent workers')
    parser.add_argument('--output-dir', type=str, help='Output directory for job data')
    parser.add_argument('--specific-ranges', action='store_true', help='Scan specific ranges likely to contain missing jobs')
    parser.add_argument('--specific-id', type=int, help='Scan a specific job ID')
    parser.add_argument('--log-file', type=str, help='Log to file')
    
    args = parser.parse_args()
    
    # Configure file logging if requested
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)
    
    # Determine output directory
    output_dir = args.output_dir if args.output_dir else JOB_DATA_DIR
    
    if args.specific_id:
        # Scan a single job ID
        logger.info(f"Scanning job ID {args.specific_id}")
        result = scan_job_id(args.specific_id, output_dir)
        
        if result["is_valid_job"]:
            logger.info(f"Job ID {args.specific_id} is a valid job:")
            logger.info(f"  Title: {result['title']}")
            logger.info(f"  Location: {result['location']}")
            logger.info(f"  Found via API: {result['api_found']}")
        else:
            logger.info(f"Job ID {args.specific_id} is not a valid job")
            
    elif args.specific_ranges:
        # Scan specific ranges
        scan_specific_ranges()
        
    elif args.start is not None and args.end is not None:
        # Scan a custom range
        scan_job_range(
            args.start,
            args.end,
            output_dir=output_dir,
            delay=args.delay,
            concurrent=args.concurrent,
            max_workers=args.workers
        )
    else:
        # No range specified
        parser.print_help()
        logger.error("Please specify --specific-ranges, --specific-id, or both --start and --end")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
