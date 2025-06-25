#!/usr/bin/env python3
"""
Script to identify and fix job descriptions with missing or malformed titles
by using our new versioning system to trigger reprocessing.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import relevant modules
from run_pipeline.config.paths import JOB_DATA_DIR
from run_pipeline.utils.staged_processor.processor import process_jobs

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger('fix_job_titles')

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
            
            # Check if concise description has a proper title
            has_title_issue = False
            
            # Check web_details and structured_description
            if "web_details" in job_data and "concise_description" in job_data["web_details"]:
                concise_desc = job_data["web_details"]["concise_description"]
                
                # Check if the first line has a job title
                if concise_desc:
                    first_line = concise_desc.strip().split('\n')[0].strip()
                    if first_line == "Job Title:" or not first_line:
                        has_title_issue = True
                        logger.info(f"Job {job_id}: Missing job title in concise description")
            
                # Check structured description if available
                if "structured_description" in job_data["web_details"]:
                    structured_desc = job_data["web_details"]["structured_description"]
                    
                    if "title" in structured_desc:
                        title = structured_desc["title"]
                        if not title or title == "Responsibilities:":
                            has_title_issue = True
                            logger.info(f"Job {job_id}: Invalid title '{title}' in structured description")
            
            if has_title_issue:
                jobs_with_issues.append(job_id)
                
        except Exception as e:
            logger.error(f"Error checking job file {job_file}: {str(e)}")
    
    logger.info(f"Found {len(jobs_with_issues)} jobs with title issues")
    return jobs_with_issues

def fix_jobs_with_title_issues(job_ids, model="llama3.2:latest"):
    """Fix jobs with title issues by reprocessing them"""
    if not job_ids:
        logger.info("No jobs with title issues found. Nothing to fix.")
        return
    
    logger.info(f"Fixing {len(job_ids)} jobs with title issues...")
    processed, success, failure = process_jobs(
        job_ids=job_ids,
        model=model,
        dry_run=False,
        output_format="text"
    )
    
    logger.info(f"Successfully fixed {success} out of {processed} jobs with title issues")
    if failure > 0:
        logger.warning(f"Failed to fix {failure} jobs")
        
    return success, failure

def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("JOB TITLE FIX UTILITY")
    logger.info("=" * 80)
    logger.info("Finding jobs with missing or malformed titles...")
    
    # Find jobs with title issues
    jobs_with_title_issues = find_jobs_with_title_issues()
    
    if jobs_with_title_issues:
        # Fix the issues by reprocessing
        success, failure = fix_jobs_with_title_issues(jobs_with_title_issues)
        
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
