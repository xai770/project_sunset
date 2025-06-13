#!/usr/bin/env python3
"""
File handling utilities for staged job processing
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any, List, Tuple, Union

from run_pipeline.config.paths import JOB_DATA_DIR
from run_pipeline.utils.staged_processor.utils import logger
from run_pipeline.utils.staged_processor.extractors import convert_to_json

# Import version information
try:
    from run_pipeline.utils.staged_processor.versions import (
        HTML_CLEANER_VERSION,
        LANGUAGE_HANDLER_VERSION,
        EXTRACTORS_VERSION,
        FILE_HANDLER_VERSION,
        PROCESSOR_VERSION,
        STAGED_PROCESSOR_VERSION,
        MODULE_DEPENDENCIES
    )
except ImportError:
    # Default versions if imports fail (backward compatibility)
    HTML_CLEANER_VERSION = "1.0.0"
    LANGUAGE_HANDLER_VERSION = "1.0.0"
    EXTRACTORS_VERSION = "1.0.0"
    FILE_HANDLER_VERSION = "1.0.0"
    PROCESSOR_VERSION = "1.0.0"
    STAGED_PROCESSOR_VERSION = "1.0.0"
    MODULE_DEPENDENCIES = {}

# Module-specific version constants
MODULE_VERSIONS = {
    "html_cleaner": HTML_CLEANER_VERSION,
    "language_handler": LANGUAGE_HANDLER_VERSION,
    "extractors": EXTRACTORS_VERSION,
    "file_handler": FILE_HANDLER_VERSION,
    "processor": PROCESSOR_VERSION
}

def check_version_and_needs_processing(job_data: Dict[str, Any], module_name: Optional[str] = None) -> Tuple[bool, str]:
    """
    Check if job needs processing based on version information
    
    Args:
        job_data: Job data dictionary
        module_name: Specific module to check (or None for any)
        
    Returns:
        Tuple[bool, str]: (needs_processing, reason)
    """
    # If no log entries, job always needs processing
    if "log" not in job_data or not job_data["log"]:
        return True, "No processing history found"
    
    # Get the versions from the latest log entry for this job
    latest_version = None
    latest_entry = None
    
    # Find the latest staged_processor entry in the log
    for entry in reversed(job_data["log"]):
        if "script" in entry and entry["script"] == "run_pipeline.utils.staged_job_description_processor":
            latest_entry = entry
            break
            
    if not latest_entry:
        return True, "No previous staged processor entries found"
        
    # Check for version information
    if "staged_processor_version" not in latest_entry:
        return True, "No version information in latest log entry"
        
    latest_version = latest_entry.get("staged_processor_version", "0.0.0")
    
    # Compare with current version
    if latest_version != STAGED_PROCESSOR_VERSION:
        return True, f"Job was processed with version {latest_version}, current version is {STAGED_PROCESSOR_VERSION}"
    
    # If checking a specific module
    if module_name:
        module_version_name = f"{module_name}_version"
        current_module_version = MODULE_VERSIONS.get(module_name, "0.0.0")
        
        if module_version_name in latest_entry:
            module_version = latest_entry[module_version_name]
            if module_version != current_module_version:
                return True, f"Module {module_name} version changed from {module_version} to {current_module_version}"
        else:
            # If no specific module version in entry, process if it's not set
            return True, f"No version information for module {module_name}"
            
    # Check all module versions
    for module, current_version in MODULE_VERSIONS.items():
        module_version_name = f"{module}_version"
        if module_version_name in latest_entry:
            saved_version = latest_entry[module_version_name]
            if saved_version != current_version:
                return True, f"Module {module} version changed from {saved_version} to {current_version}"
    
    # Check for good existing description - if not present or malformed, needs processing
    if "web_details" not in job_data:
        return True, "Missing web_details section"
        
    if "concise_description" not in job_data["web_details"]:
        return True, "Missing concise_description"
        
    concise_desc = job_data["web_details"]["concise_description"]
    if not concise_desc or len(concise_desc) < 500:
        return True, "Concise description too short or empty"
        
    # Check for key sections expected in a well-formed job description
    if "Responsibilities:" not in concise_desc or "Requirements:" not in concise_desc:
        return True, "Concise description missing key sections"
    
    # Check structured description if available    
    if "structured_description" in job_data["web_details"]:
        structured_desc = job_data["web_details"]["structured_description"]
        
        # Check if job title is missing or is incorrectly set to "Responsibilities:"
        if "title" in structured_desc and (not structured_desc["title"] or structured_desc["title"] == "Responsibilities:"):
            return True, "Structured description has invalid job title"
        
        # Check for missing job title in concise_description
        first_line = concise_desc.strip().split('\n')[0].strip()
        if first_line.startswith('Job Title:') and len(first_line) <= 10:
            return True, "Job title missing in concise description"
    
    # If everything is up to date and good quality, no need for processing
    return False, "Job already processed with current version and has good quality description"

def load_job_data(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Load job data from file
    
    Args:
        job_id: Job ID to load
        
    Returns:
        Job data dictionary or None if failed
    """
    job_path = Path(JOB_DATA_DIR) / f"job{job_id}.json"
    try:
        with open(job_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading job {job_id}: {str(e)}")
        return None


def get_job_html_content(job_data: Dict[str, Any]) -> Optional[str]:
    """
    Get HTML content from job data
    
    Args:
        job_data: Job data dictionary
        
    Returns:
        HTML content or None if not found
    """
    # First check api_details.html
    if "api_details" in job_data and "html" in job_data["api_details"]:
        return job_data["api_details"]["html"]
    
    # Then check web_details.full_description
    if "web_details" in job_data and "full_description" in job_data["web_details"]:
        return job_data["web_details"]["full_description"]
    
    # Finally check for html_content field
    if "html_content" in job_data:
        return job_data["html_content"]
    
    return None


def save_processed_job(job_data: Dict[str, Any], processed_result: str, job_id: str,
                       original_lang: str, output_format: str) -> None:
    """
    Save processed job description back to job file
    
    Args:
        job_data: Job data dictionary
        processed_result: Processed description
        job_id: Job ID
        original_lang: Original language of content
        output_format: Output format ('text' or 'json')
    """
    # Ensure web_details exists
    if "web_details" not in job_data:
        job_data["web_details"] = {}
        
    # Remove full_description to save space if it exists
    if "full_description" in job_data["web_details"]:
        del job_data["web_details"]["full_description"]
    
    # Skip updating content if we're using an existing good description
    if original_lang == "en_existing":
        logger.info(f"Using existing good description for job {job_id} - no content update needed")
    else:
        # Update job data with processed description
        job_data["web_details"]["concise_description"] = processed_result
        
        # Add metadata
        job_data["web_details"]["description_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "model_used": "llama3.2:latest",  # This could be parameterized
            "is_placeholder": False,
            "extraction_status": "success",
            "prompt_version": "staged-1.0",
            "original_language": original_lang
        }
        
        # Add JSON structure if in text format
        if output_format == "text":
            job_data["web_details"]["structured_description"] = json.loads(convert_to_json(processed_result))
    
    # Add log entry
    if "log" not in job_data:
        job_data["log"] = []
    
    # Create log entry with detailed version information
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "script": "run_pipeline.utils.staged_job_description_processor",
        "action": "process_job_description",
        "message": f"Processed job description for job ID {job_id} using staged approach",
        "staged_processor_version": STAGED_PROCESSOR_VERSION,
    }
    
    # Add version info for all modules
    for module, version in MODULE_VERSIONS.items():
        log_entry[f"{module}_version"] = version
        
    job_data["log"].append(log_entry)
    
    # Save updated job data
    job_path = Path(JOB_DATA_DIR) / f"job{job_id}.json"
    with open(job_path, 'w', encoding='utf-8') as f:
        json.dump(job_data, f, indent=2, ensure_ascii=False)
