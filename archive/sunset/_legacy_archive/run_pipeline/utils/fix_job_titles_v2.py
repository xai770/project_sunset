#!/usr/bin/env python3
"""
Enhanced script to identify and fix job descriptions with missing or malformed titles.
This version directly updates the structured_description titles without regenerating the entire description.
"""

import os
import sys
import json
import logging
import re
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import relevant modules
from run_pipeline.config.paths import JOB_DATA_DIR
from run_pipeline.utils.staged_processor.versions import (
    STAGED_PROCESSOR_VERSION,
    HTML_CLEANER_VERSION,
    LANGUAGE_HANDLER_VERSION,
    EXTRACTORS_VERSION,
    FILE_HANDLER_VERSION,
    PROCESSOR_VERSION
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger('fix_job_titles_v2')

def extract_title_from_html(html_content):
    """Extract job title from HTML content"""
    title_match = re.search(r'<h1>\s*([^<]+)\s*</h1>', html_content)
    if title_match:
        return title_match.group(1).strip()
    return None

def extract_title_from_concise_desc(concise_desc):
    """Extract job title from concise description"""
    if not concise_desc:
        return None
    
    # Try to find a job title in the format "Job Title: Something"
    title_match = re.search(r'(?:Job Title|Title):\s*(.+?)(?:\n|$)', concise_desc)
    if title_match:
        return title_match.group(1).strip()
    
    # Otherwise take the first line if it's not a section header
    first_line = concise_desc.strip().split('\n')[0].strip()
    if first_line and ":" not in first_line and len(first_line) > 3:
        return first_line
    
    return None

def extract_title_from_position_title(position_title):
    """Extract core job title from position title"""
    # Remove common suffixes like (f/m/x), (m/w/d), etc.
    cleaned = re.sub(r'\s*\([^\)]+\)\s*$', '', position_title)
    return cleaned.strip()

def find_jobs_with_title_issues():
    """Find jobs with missing or malformed titles"""
    job_dir = Path(JOB_DATA_DIR)
    jobs_with_issues = []
    
    job_files = sorted([f for f in os.listdir(job_dir) if f.startswith('job') and f.endswith('.json')])
    logger.info(f"Scanning {len(job_files)} jobs for title issues...")
    
    for job_file in job_files:
        job_id = job_file.replace('job', '').replace('.json', '')
        job_path = job_dir / job_file
        
        try:
            with open(job_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Check if structured_description has a proper title
            has_title_issue = False
            
            if "web_details" in job_data:
                web_details = job_data["web_details"]
                
                if "structured_description" in web_details:
                    structured_desc = web_details["structured_description"]
                    
                    if "title" in structured_desc:
                        title = structured_desc["title"]
                        if not title or title == "Responsibilities:":
                            has_title_issue = True
                            logger.info(f"Job {job_id}: Invalid title '{title}' in structured description")
                
                # Also check concise description
                if has_title_issue and "concise_description" in web_details:
                    concise_desc = web_details["concise_description"]
                    first_line = concise_desc.strip().split('\n')[0].strip() if concise_desc else ""
                    if first_line.startswith('Job Title:') and len(first_line) <= 10:
                        logger.info(f"Job {job_id}: Missing job title in concise description")
            
            if has_title_issue:
                jobs_with_issues.append(job_id)
                
        except Exception as e:
            logger.error(f"Error checking job file {job_file}: {str(e)}")
    
    logger.info(f"Found {len(jobs_with_issues)} jobs with title issues")
    return jobs_with_issues

def fix_job_titles(job_ids):
    """Fix job titles by directly updating the structured_description title field"""
    if not job_ids:
        logger.info("No jobs with title issues found. Nothing to fix.")
        return 0, 0
    
    logger.info(f"Fixing titles for {len(job_ids)} jobs...")
    success = 0
    failure = 0
    
    for job_id in job_ids:
        logger.info(f"Processing job {job_id} ({success+failure+1} of {len(job_ids)})")
        
        try:
            job_path = Path(JOB_DATA_DIR) / f"job{job_id}.json"
            
            with open(job_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            title_found = None
            
            # 1. Try to get title from position_title
            if "web_details" in job_data and "position_title" in job_data["web_details"]:
                title_found = extract_title_from_position_title(job_data["web_details"]["position_title"])
                logger.info(f"Found title from position_title: {title_found}")
            
            # 2. Try to get title from HTML content
            if not title_found and "api_details" in job_data and "html" in job_data["api_details"]:
                title_found = extract_title_from_html(job_data["api_details"]["html"])
                if title_found:
                    logger.info(f"Found title from HTML content: {title_found}")
            
            # 3. Try to get title from concise description
            if not title_found and "web_details" in job_data and "concise_description" in job_data["web_details"]:
                title_found = extract_title_from_concise_desc(job_data["web_details"]["concise_description"])
                if title_found:
                    logger.info(f"Found title from concise description: {title_found}")
            
            # 4. If still no title, use a generic one based on the job ID
            if not title_found:
                title_found = f"Professional Position {job_id}"
                logger.warning(f"No title found, using generic: {title_found}")
            
            # Update the structured description
            if "web_details" in job_data and "structured_description" in job_data["web_details"]:
                job_data["web_details"]["structured_description"]["title"] = title_found
                logger.info(f"Updated structured description title to: {title_found}")
                
                # Add log entry
                if "log" not in job_data:
                    job_data["log"] = []
                
                # Create log entry with version information
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "script": "fix_job_titles_v2",
                    "action": "fix_job_title",
                    "message": f"Fixed missing job title for job ID {job_id}",
                    "staged_processor_version": STAGED_PROCESSOR_VERSION,
                }
                
                # Add version info for all modules
                log_entry["html_cleaner_version"] = HTML_CLEANER_VERSION
                log_entry["language_handler_version"] = LANGUAGE_HANDLER_VERSION
                log_entry["extractors_version"] = EXTRACTORS_VERSION
                log_entry["file_handler_version"] = FILE_HANDLER_VERSION
                log_entry["processor_version"] = PROCESSOR_VERSION
                    
                job_data["log"].append(log_entry)
                
                # Save the updated job data
                with open(job_path, 'w', encoding='utf-8') as f:
                    json.dump(job_data, f, indent=2, ensure_ascii=False)
                
                success += 1
                logger.info(f"Successfully fixed job {job_id}")
            else:
                logger.warning(f"Job {job_id} doesn't have structured_description, skipping")
                failure += 1
                
        except Exception as e:
            logger.error(f"Error fixing job {job_id}: {str(e)}")
            failure += 1
    
    return success, failure

def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("JOB TITLE FIX UTILITY V2")
    logger.info("=" * 80)
    logger.info("Finding jobs with missing or malformed titles...")
    
    # Find jobs with title issues
    jobs_with_title_issues = find_jobs_with_title_issues()
    
    if jobs_with_title_issues:
        # Fix the issues by directly updating the titles
        success, failure = fix_job_titles(jobs_with_title_issues)
        
        # Log summary
        logger.info("=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total jobs with title issues: {len(jobs_with_title_issues)}")
        logger.info(f"Successfully fixed: {success}")
        logger.info(f"Failed to fix: {failure}")
        
        return 0 if failure == 0 else 1
    else:
        logger.info("No jobs with title issues found. All good!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
