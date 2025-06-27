#!/usr/bin/env python3
"""
Utility functions for the job expansion pipeline.
Provides helper functions used across different pipeline modules.
"""

import os
import json
import logging
from pathlib import Path
from run_pipeline.config.paths import JOB_DATA_DIR

logger = logging.getLogger('pipeline_utils')

def process_job_ids(job_ids_str):
    """
    Process job IDs string into a list
    
    Args:
        job_ids_str (str): Comma-separated job IDs
        
    Returns:
        list: List of job IDs
    """
    if not job_ids_str:
        return None
        
    return [int(job_id.strip()) for job_id in job_ids_str.split(",") if job_id.strip()]

def check_for_missing_skills(max_jobs=None, job_ids=None):
    """
    Check for jobs with missing skills or zero match percentages.
    
    Args:
        max_jobs (int, optional): Maximum number of jobs to check
        job_ids (list, optional): Specific job IDs to check
        
    Returns:
        tuple: (jobs_without_skills, jobs_with_zero_matches)
    """
    import os
    import json
    from pathlib import Path
    from run_pipeline.config.paths import JOB_DATA_DIR
    
    logger = logging.getLogger('job_pipeline')
    job_dir = Path(JOB_DATA_DIR)
    
    if job_ids:
        job_files = []
        for job_id in job_ids:
            job_file = job_dir / f"job{job_id}.json"
            if job_file.exists():
                job_files.append(job_file)
    else:
        job_files = sorted(list(job_dir.glob("job*.json")))
        if max_jobs and max_jobs < len(job_files):
            job_files = job_files[:max_jobs]
    
    logger.info(f"Checking {len(job_files)} job files for missing skills or zero match percentages")
    
    jobs_without_skills = []
    jobs_with_zero_matches = []
    
    for job_file in job_files:
        job_id = job_file.stem.replace("job", "")
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Check if the job has bucketed skills instead of SDR skills
            if "bucketed_skills" not in job_data or not job_data.get("bucketed_skills"):
                jobs_without_skills.append(job_id)
                continue
                
            # Check if the job has skill matches with valid match percentages
            skill_matches = job_data.get("skill_matches", {})
            if "match_percentage" in skill_matches and skill_matches["match_percentage"] == 0.0:
                # Check if there are actual skills but zero matches
                if job_data.get("bucketed_skills"):
                    jobs_with_zero_matches.append(job_id)
        except Exception as e:
            logger.error(f"Error checking job {job_id}: {str(e)}")
    
    logger.info(f"Found {len(jobs_without_skills)} jobs without skills")
    logger.info(f"Found {len(jobs_with_zero_matches)} jobs with zero match percentages")
    
    return jobs_without_skills, jobs_with_zero_matches

# Export for external use
__all__ = ['process_job_ids', 'check_for_missing_skills']
