#!/usr/bin/env python3
"""
Test Utilities for JMFS Pipeline

This module provides utility functions for testing the JMFS pipeline,
particularly for artificially creating test scenarios.
"""

import os
import json
import random
import logging
from pathlib import Path

# Configure logger
logger = logging.getLogger(__name__)

def force_good_match_for_testing(job_id: str) -> dict:
    """
    Take an existing job and override its match level to "Good" for testing.
    Generate application narrative suitable for cover letter generation.
    
    Args:
        job_id (str): The job ID to modify
        
    Returns:
        dict: Modified job data ready for cover letter pipeline
    """
    # Find the job data file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = Path(script_dir).parent.parent
    
    # Try multiple locations
    possible_job_paths = [
        os.path.join(project_root, "data", "postings", f"job{job_id}.json"),
        os.path.join(project_root, "output", "jobs", f"job{job_id}.json"),
        os.path.join(script_dir, "..", "..", "data", "postings", f"job{job_id}.json")
    ]
    
    job_data = None
    job_path = None
    
    for path in possible_job_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                    job_path = path
                    logger.info(f"Found job data at: {path}")
                    break
            except Exception as e:
                logger.error(f"Error loading job data from {path}: {e}")
    
    if not job_data:
        logger.error(f"Could not find job data for job ID: {job_id}")
        return {}
    
    # Create backup of original data
    backup_path = f"{job_path}.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2)
            logger.info(f"Created backup at {backup_path}")
    
    # Override the match level to "Good"
    if 'llama32_evaluation' not in job_data:
        job_data['llama32_evaluation'] = {}
    
    job_data['llama32_evaluation']['cv_to_role_match'] = 'Good'
    
    # Generate a compelling application narrative
    job_title = job_data.get('search_details', {}).get('positiontitle', 'this position')
    skills = job_data.get('llama32_evaluation', {}).get('extracted_skills', [])
    skills_text = ""
    
    if skills and len(skills) > 0:
        # Use actual extracted skills if available
        skills_sample = random.sample(skills, min(3, len(skills)))
        skills_text = ", ".join(skills_sample)
    else:
        # Fallback to generic skills
        skills_text = "project management, data analysis, and technical implementation"
    
    # Generate a compelling narrative
    job_data['llama32_evaluation']['application_narrative'] = (
        f"Based on my review of your CV and the requirements for {job_title}, "
        f"I believe you would be an excellent fit for this role. Your experience with {skills_text} "
        f"directly aligns with the key requirements. Additionally, your background in similar "
        f"environments demonstrates you can quickly add value to the team. I recommend highlighting "
        f"your most relevant projects and quantifiable achievements in your cover letter, while "
        f"expressing enthusiasm about the opportunity to contribute to their specific challenges."
    )
    
    # Save the modified job data back to the file
    if job_path is not None:
        with open(job_path, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2)
            logger.info(f"Updated job {job_id} to 'Good' match with application narrative")
    else:
        logger.error(f"Could not find job data file for job ID: {job_id}")
    
    return job_data

def restore_job_from_backup(job_id: str) -> bool:
    """
    Restore a job's data from backup after testing
    
    Args:
        job_id (str): The job ID to restore
        
    Returns:
        bool: True if successful, False otherwise
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = Path(script_dir).parent.parent
    
    # Try multiple locations
    possible_backup_paths = [
        os.path.join(project_root, "data", "postings", f"job{job_id}.json.bak"),
        os.path.join(project_root, "output", "jobs", f"job{job_id}.json.bak"),
        os.path.join(script_dir, "..", "..", "data", "postings", f"job{job_id}.json.bak")
    ]
    
    for backup_path in possible_backup_paths:
        if os.path.exists(backup_path):
            original_path = backup_path[:-4]  # Remove .bak extension
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    original_data = json.load(f)
                
                with open(original_path, 'w', encoding='utf-8') as f:
                    json.dump(original_data, f, indent=2)
                
                logger.info(f"Successfully restored job {job_id} from backup")
                return True
            except Exception as e:
                logger.error(f"Error restoring job {job_id} from backup: {e}")
                return False
    
    logger.warning(f"No backup found for job {job_id}")
    return False
