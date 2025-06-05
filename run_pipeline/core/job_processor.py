#!/usr/bin/env python3
"""
Job processing module for the job expansion pipeline

This module handles the processing of job files, extracting HTML content,
and updating job data with concise descriptions.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional, Union

# Import from other modules
from run_pipeline.core.cleaning_utils import clean_llm_artifacts

logger = logging.getLogger('cleaner_module.processor')

def process_job_files(job_dir: Union[str, Path], max_jobs: Optional[int] = None, 
                      model: str = "phi3", specific_job_ids: Optional[List[str]] = None) -> Tuple[int, int, int]:
    """
    Process job files and update with concise descriptions
    
    Args:
        job_dir (Path): Directory containing job files
        max_jobs (int): Maximum number of jobs to process
        model (str): Ollama model to use
        specific_job_ids (list): List of specific job IDs to process
        
    Returns:
        tuple: (processed_count, success_count, failure_count)
    """
    # Import here to avoid circular imports
    from run_pipeline.core.cleaner_module import get_cleaner_instance
    
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
                logger.warning(f"Job file not found: {job_file}")
    else:
        job_files = sorted([f for f in os.listdir(job_dir) 
                   if f.startswith('job') and f.endswith('.json')])
    
    logger.info(f"Found {len(job_files)} job files")
    
    # Process counters
    processed = 0
    success = 0
    failure = 0
    
    # Create cleaner instance
    cleaner = get_cleaner_instance(model)
    
    # Process each job file
    for job_file in job_files:
        job_id = job_file.replace('job', '').replace('.json', '')
        job_path = job_dir / job_file
        
        logger.info(f"Processing job ID {job_id} ({processed+1} of {len(job_files)})")
        
        try:
            # Read job data
            with open(job_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Get job title
            job_title = job_data.get("title", f"Job {job_id}")
            
            # Get HTML content (from various possible sources)
            job_content = get_job_html_content(job_data, job_dir, job_id)
            if not job_content:
                # Handle case where no content is found
                handle_missing_content(job_data, job_path, job_title, job_id)
                processed += 1
                failure += 1
                continue
            
            # Process job content
            logger.info(f"Job title: {job_title}")
            logger.info(f"Raw content length: {len(job_content)} characters")
            
            # Extract concise job description using Ollama
            logger.info(f"Sending request to Ollama using {model} model...")
            
            try:
                # Attempt to extract concise description
                concise_description = cleaner.extract_concise_description(job_content, job_title, job_id)
                
                # Clean up any LLM artifacts in the response
                if concise_description:
                    concise_description = clean_llm_artifacts(concise_description)
            except Exception as e:
                logger.error(f"Ollama extraction error: {str(e)}")
                concise_description = None
            
            # If extraction failed, use a placeholder
            if not concise_description:
                logger.warning(f"Using placeholder description for job {job_id}")
                concise_description = f"Job Title: {job_title}\n\nThis is a placeholder for a concise description that could not be generated."
            
            logger.info(f"Concise description length: {len(concise_description)} characters")
            
            # Update job data with the concise description
            update_job_with_concise_description(job_data, job_path, job_id, concise_description)
            
            success += 1
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            failure += 1
        
        processed += 1
        
        # Check if we've reached the maximum
        if max_jobs and processed >= max_jobs:
            logger.info(f"Reached maximum number of jobs to process ({max_jobs})")
            break
    
    logger.info(f"Processing complete. Total: {processed}, Success: {success}, Failure: {failure}")
    return (processed, success, failure)


def get_job_html_content(job_data: dict, job_dir: Path, job_id: str) -> Optional[str]:
    """
    Get HTML content for a job from various possible sources
    
    Args:
        job_data (dict): Job data dictionary
        job_dir (Path): Directory containing job files
        job_id (str): Job ID
        
    Returns:
        str: HTML content or None if not found
    """
    # Prioritize getting HTML content from web_details.full_description
    if "web_details" in job_data and "full_description" in job_data["web_details"]:
        logger.info(f"Found HTML content in web_details.full_description for job {job_id}")
        return job_data["web_details"]["full_description"]
    
    # If no full_description, check for direct html_content field
    content = job_data.get("html_content", "")
    if content:
        logger.info(f"Found HTML content in html_content field for job {job_id}")
        return content
    
    # As a last resort, check for external HTML file
    logger.warning(f"Job {job_id} has no HTML content in job data, checking for external content file")
    
    # Look for HTML content in the html_content directory
    html_content_dir = job_dir.parent / "postings" / "html_content"
    html_content_file = html_content_dir / f"db_job_{job_id}_content.txt"
    
    if os.path.exists(html_content_file):
        logger.info(f"Found external HTML content file for job {job_id}, loading content")
        with open(html_content_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    logger.warning(f"Job {job_id} has no HTML content available")
    return None


def handle_missing_content(job_data: dict, job_path: Path, job_title: str, job_id: str) -> None:
    """
    Handle case where no job content is found by adding a placeholder
    
    Args:
        job_data (dict): Job data dictionary
        job_path (Path): Path to the job file
        job_title (str): Job title
        job_id (str): Job ID
    """
    placeholder = f"Job Title: {job_title}\n\nThis is a placeholder for a concise description that could not be generated."
    
    # Add placeholder to web_details
    if "web_details" in job_data:
        job_data["web_details"]["concise_description"] = placeholder
    else:
        job_data["web_details"] = {"concise_description": placeholder}
    
    # Save updated job data with placeholder
    with open(job_path, 'w', encoding='utf-8') as f:
        json.dump(job_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Added placeholder description for job {job_id} (no HTML content available)")


def update_job_with_concise_description(job_data: dict, job_path: Path, 
                                       job_id: str, concise_description: str) -> None:
    """
    Update job data with concise description and save to file
    
    Args:
        job_data (dict): Job data dictionary
        job_path (Path): Path to the job file
        job_id (str): Job ID
        concise_description (str): Concise description to add
    """
    # Add concise description to web_details
    if "web_details" in job_data:
        job_data["web_details"]["concise_description"] = concise_description
    else:
        # Create web_details if it doesn't exist
        job_data["web_details"] = {"concise_description": concise_description}
        
    logger.info("Added concise_description to web_details")
    
    # Remove full_description from web_details after processing to reduce file size
    # since we've now created the concise version
    if "web_details" in job_data and "full_description" in job_data["web_details"]:
        full_desc_size = len(job_data["web_details"]["full_description"])
        del job_data["web_details"]["full_description"]
        logger.info(f"Successfully processed HTML content and removed full_description to save space (saved {full_desc_size} characters)")
    
    # Add log entry
    if 'log' not in job_data:
        job_data['log'] = []
    
    job_data['log'].append({
        "timestamp": datetime.now().isoformat(),
        "script": "run_pipeline.core.cleaner_module",
        "action": "add_concise_description",
        "message": f"Added concise job description for job ID {job_id}"
    })
    
    # Save updated job data
    with open(job_path, 'w', encoding='utf-8') as f:
        json.dump(job_data, f, indent=2, ensure_ascii=False)
