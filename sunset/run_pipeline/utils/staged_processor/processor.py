#!/usr/bin/env python3
"""
Main processor module for staged job description processing
"""

import os
import sys
import json
import logging
import argparse
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

from run_pipeline.config.paths import JOB_DATA_DIR

# Import from other package modules
from run_pipeline.utils.staged_processor.utils import logger
from run_pipeline.utils.staged_processor.html_cleaner import clean_html
from run_pipeline.utils.staged_processor.language_handler import handle_language
from run_pipeline.utils.staged_processor.extractors import extract_job_details
from run_pipeline.utils.staged_processor.file_handler import (
    load_job_data, get_job_html_content, save_processed_job
)

class StagedJobProcessor:
    """
    Process job descriptions in stages:
    1. Clean HTML
    2. Handle language (remove German if English exists, or translate)
    3. Extract formatted job details
    """
    
    def __init__(self, model: str = "llama3.2:latest"):
        """
        Initialize the processor
        
        Args:
            model: LLM model to use
        """
        self.model = model
        
        # Dynamic import to avoid circular dependency
        cleaner_module = importlib.import_module("run_pipeline.core.cleaner_module")
        get_cleaner_instance = getattr(cleaner_module, "get_cleaner_instance")
        self.cleaner = get_cleaner_instance(model)
    
    def process_job(self, job_id: str, dry_run: bool = False, 
                   output_format: str = "text") -> Optional[Dict[str, Any]]:
        """
        Process a job through all stages
        
        Args:
            job_id: Job ID to process
            dry_run: If True, don't save changes
            output_format: Format for output ('text' or 'json')
            
        Returns:
            Job data with processed description if successful
        """
        # 1. Load job data
        job_data = load_job_data(job_id)
        if not job_data:
            return None
            
        # 1a. Check if processing is needed based on versions
        from run_pipeline.utils.staged_processor.file_handler import check_version_and_needs_processing
        needs_processing, reason = check_version_and_needs_processing(job_data)
        
        if not needs_processing and not dry_run:
            logger.info(f"Skipping job {job_id} - {reason}")
            return job_data
        else:
            logger.info(f"Processing job {job_id} - {reason}")
        
        # 2. Get HTML content
        html_content = get_job_html_content(job_data)
        if not html_content:
            logger.warning(f"No HTML content found for job {job_id}")
            return None
        
        # Log original content size
        logger.info(f"Original HTML content size: {len(html_content)} characters")
        
        # 3. Clean HTML
        cleaned_text = clean_html(html_content)
        logger.info(f"Cleaned text size: {len(cleaned_text)} characters")
        logger.info(f"HTML cleaning reduced content by {(len(html_content) - len(cleaned_text)) / len(html_content) * 100:.1f}%")
        
        # 4. Handle language
        english_text, original_lang = handle_language(cleaned_text, job_id, self.model, self.cleaner)
        if not english_text:
            logger.warning(f"Failed to process language for job {job_id}")
            return None
        
        # If we're using an existing good description, skip extraction
        if original_lang == "en_existing":
            logger.info(f"Used existing English description for job {job_id} - skipping extraction")
            job_details = english_text  # Use the existing description directly
            if not job_details:  # This should not happen, but adding a safeguard
                logger.warning(f"Failed to get existing description for job {job_id}")
                return None
        else:
            # 5. Extract job details only if we don't already have a good description
            job_details_result = extract_job_details(english_text, job_id, output_format, self.model, self.cleaner)
            if not job_details_result:
                logger.warning(f"Failed to extract job details for job {job_id}")
                return None
            job_details = job_details_result
                
            # Log appropriate message based on the language handling that occurred
            if original_lang == "bilingual":
                logger.info(f"Extracted English portion from bilingual content for job {job_id}")
            elif original_lang != "en":
                logger.info(f"Translated job description from {original_lang} to English for job {job_id}")
        
        # 6. Save results if not in dry run mode
        if not dry_run:
            save_processed_job(job_data, job_details, job_id, original_lang, output_format)
            logger.info(f"Successfully processed and saved job {job_id}")
        
        return job_data


def process_jobs(job_ids: Optional[List[str]] = None, model: str = "llama3.2:latest", 
                dry_run: bool = False, output_format: str = "text") -> Tuple[int, int, int]:
    """
    Process multiple jobs
    
    Args:
        job_ids: Specific job IDs to process, or None for all
        model: LLM model to use
        dry_run: If True, don't save changes
        output_format: Format for output ('text' or 'json')
        
    Returns:
        tuple: (processed_count, success_count, failure_count)
    """
    # Get job IDs if not provided
    if not job_ids:
        job_dir = Path(JOB_DATA_DIR)
        job_files = sorted([f for f in os.listdir(job_dir) if f.startswith('job') and f.endswith('.json')])
        job_ids = [f.replace('job', '').replace('.json', '') for f in job_files]
    
    # Initialize processor
    processor = StagedJobProcessor(model=model)
    
    # Process counters
    processed = 0
    success = 0
    failure = 0
    
    # Process each job
    for job_id in job_ids:
        logger.info(f"Processing job {job_id} ({processed+1} of {len(job_ids)})")
        
        try:
            result = processor.process_job(job_id, dry_run, output_format)
            
            if result:
                success += 1
                logger.info(f"Successfully processed job {job_id}")
            else:
                failure += 1
                logger.warning(f"Failed to process job {job_id}")
        
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            failure += 1
        
        processed += 1
    
    return processed, success, failure
