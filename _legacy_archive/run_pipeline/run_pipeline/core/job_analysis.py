#!/usr/bin/env python3
"""
Job analysis module for the job expansion pipeline

This module provides functions for analyzing job description files,
identifying jobs without proper descriptions, and generating statistics.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Union

logger = logging.getLogger('cleaner_module.analysis')

def count_placeholder_jobs(job_dir: Union[str, Path]) -> int:
    """
    Count how many jobs have placeholder descriptions or are missing concise descriptions
    
    Args:
        job_dir (Path): Directory containing job files
        
    Returns:
        int: Number of jobs with placeholder descriptions or missing concise descriptions
    """
    job_dir = Path(job_dir)
    placeholder_count = 0
    missing_count = 0
    job_files = [f for f in os.listdir(job_dir) if f.startswith('job') and f.endswith('.json')]
    
    for job_file in job_files:
        job_path = job_dir / job_file
        try:
            with open(job_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Check if concise description exists in web_details
            has_concise = False
            if 'web_details' in job_data and 'concise_description' in job_data['web_details']:
                concise_desc = job_data['web_details']['concise_description']
                if concise_desc and len(concise_desc) > 50:
                    # Check if it's a placeholder
                    if "placeholder for a concise description" in concise_desc:
                        placeholder_count += 1
                    else:
                        has_concise = True
            
            if not has_concise:
                missing_count += 1
                
        except Exception as e:
            logger.error(f"Error checking job file {job_file}: {str(e)}")
            missing_count += 1
    
    logger.info(f"Jobs with placeholder descriptions: {placeholder_count}")
    logger.info(f"Jobs missing concise descriptions: {missing_count}")
    
    return missing_count + placeholder_count


def get_jobs_without_concise_description(job_dir: Union[str, Path]) -> List[str]:
    """
    Get a list of job IDs that don't have concise descriptions
    
    Args:
        job_dir (Path): Directory containing job files
        
    Returns:
        list: List of job IDs without concise descriptions
    """
    job_dir = Path(job_dir)
    jobs_without_concise = []
    job_files = [f for f in os.listdir(job_dir) if f.startswith('job') and f.endswith('.json')]
    
    logger.info(f"Scanning {len(job_files)} jobs for missing concise descriptions")
    
    for job_file in job_files:
        job_id = job_file.replace('job', '').replace('.json', '')
        job_path = job_dir / job_file
        
        try:
            with open(job_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Check if concise description exists and is valid
            has_concise = False
            if 'web_details' in job_data and 'concise_description' in job_data['web_details']:
                concise_desc = job_data['web_details']['concise_description']
                if concise_desc and len(concise_desc) > 50:
                    # Check if it's a placeholder
                    if "placeholder for a concise description" not in concise_desc.lower():
                        has_concise = True
            
            if not has_concise:
                jobs_without_concise.append(job_id)
                
        except Exception as e:
            logger.error(f"Error checking job file {job_file}: {str(e)}")
            jobs_without_concise.append(job_id)
    
    logger.info(f"Found {len(jobs_without_concise)} jobs without valid concise descriptions")
    return jobs_without_concise
