#!/usr/bin/env python3
"""
Prompt Management Utilities

This module provides functions for managing versioned prompts used in the job processing pipeline.
It allows prompts to be centrally stored, versioned, and updated when needed.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

from run_pipeline.config.paths import PROJECT_ROOT

# Define paths
PROMPTS_DIR = PROJECT_ROOT / "run_pipeline" / "config" / "prompts"
JOB_DESCRIPTION_PROMPT_FILE = PROMPTS_DIR / "job_description_prompts.json"

# Set up logging
logger = logging.getLogger("prompt_utils")

def ensure_prompts_dir():
    """Ensure the prompts directory exists"""
    os.makedirs(PROMPTS_DIR, exist_ok=True)
    return PROMPTS_DIR

def get_job_description_prompt():
    """
    Get the current job description prompt
    
    Returns:
        tuple: (prompt_text, prompt_version) 
    """
    # Ensure prompts directory exists
    ensure_prompts_dir()
    
    # Default values if no file exists
    default_prompt = """Extract ONLY the English version of this job description from Deutsche Bank. 

Please:
1. Remove all German text completely
2. Remove all website navigation elements and menus
3. Remove company marketing content and benefits sections
4. Remove all HTML formatting and unnecessary whitespace
5. Preserve the exact original wording of the job title, location, responsibilities, and requirements
6. Maintain the contact information
7. Keep the original structure (headings, bullet points) of the core job description
8. Double check that you remove all sections and wordings discussing the company culture, benefits, values, and mission statement

The result should be a clean, professional job description in English only, with all the essential information about the position preserved exactly as written."""
    default_version = "1.0"
    
    # Try to load from file
    if not JOB_DESCRIPTION_PROMPT_FILE.exists():
        # Create default file if it doesn't exist
        data = {
            "version": default_version,
            "updated_at": datetime.now().isoformat(),
            "active_version": default_version,
            "versions": {
                default_version: {
                    "prompt": default_prompt,
                    "created_at": datetime.now().isoformat(),
                    "description": "Default job description prompt",
                    "author": "system"
                }
            }
        }
        try:
            with open(JOB_DESCRIPTION_PROMPT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Created default prompt file at {JOB_DESCRIPTION_PROMPT_FILE}")
        except Exception as e:
            logger.error(f"Error creating prompt file: {str(e)}")
        return default_prompt, default_version
    
    # Load existing file
    try:
        with open(JOB_DESCRIPTION_PROMPT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        active_version = data.get("active_version", default_version)
        if active_version not in data.get("versions", {}):
            logger.warning(f"Active version {active_version} not found in prompt file")
            return default_prompt, default_version
        
        prompt = data["versions"][active_version].get("prompt", default_prompt)
        return prompt, active_version
    except Exception as e:
        logger.error(f"Error loading prompt file: {str(e)}")
        return default_prompt, default_version

def add_job_description_prompt(prompt_text, description=None, author=None):
    """
    Add a new job description prompt version
    
    Args:
        prompt_text (str): The new prompt text
        description (str): Description of the changes
        author (str): Name of the author making the change
        
    Returns:
        str: New version number
    """
    # Ensure prompts directory exists
    ensure_prompts_dir()
    
    # Load existing data or create new data structure
    if JOB_DESCRIPTION_PROMPT_FILE.exists():
        try:
            with open(JOB_DESCRIPTION_PROMPT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading prompt file: {str(e)}")
            data = {"version": "1.0", "versions": {}}
    else:
        data = {"version": "1.0", "versions": {}}
    
    # Calculate new version
    if "versions" not in data or not data["versions"]:
        new_version = "1.0"
    else:
        # Find highest version
        versions = [v.split('.') for v in data["versions"].keys()]
        versions.sort(key=lambda x: (int(x[0]), int(x[1])))
        latest = versions[-1]
        
        # Increment minor version
        new_version = f"{latest[0]}.{int(latest[1]) + 1}"
    
    # Add new version
    if "versions" not in data:
        data["versions"] = {}
    
    data["versions"][new_version] = {
        "prompt": prompt_text,
        "created_at": datetime.now().isoformat(),
        "description": description or f"Updated prompt version {new_version}",
        "author": author or "system"
    }
    
    # Update file metadata
    data["version"] = new_version
    data["updated_at"] = datetime.now().isoformat()
    data["active_version"] = new_version
    
    # Save to file
    try:
        with open(JOB_DESCRIPTION_PROMPT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Added new prompt version {new_version}")
        return new_version
    except Exception as e:
        logger.error(f"Error saving prompt file: {str(e)}")
        return "error"

def job_needs_reprocessing(job_metadata):
    """
    Check if a job needs reprocessing based on prompt version
    
    Args:
        job_metadata (dict): Job metadata containing description_metadata
        
    Returns:
        bool: True if reprocessing is needed
    """
    # Get current prompt version
    _, current_version = get_job_description_prompt()
    
    # If job has no metadata or no description_metadata, it needs reprocessing
    if not job_metadata or "web_details" not in job_metadata:
        return True
    
    web_details = job_metadata["web_details"]
    if "description_metadata" not in web_details:
        return True
    
    # If job is a placeholder, it needs reprocessing
    desc_metadata = web_details["description_metadata"]
    if desc_metadata.get("is_placeholder", False):
        return True
    
    # If job has no prompt_version, it was created before versioning
    if "prompt_version" not in desc_metadata:
        return True
    
    # Compare versions
    job_version = desc_metadata["prompt_version"]
    
    # Parse version numbers
    try:
        job_v = [int(x) for x in job_version.split('.')]
        current_v = [int(x) for x in current_version.split('.')]
        
        # Compare versions, return True if current is newer
        return current_v > job_v
    except Exception as e:
        logger.error(f"Error comparing versions: {str(e)}")
        return True

def set_job_description_prompt(version):
    """
    Set the active job description prompt version
    
    Args:
        version (str): Version to set as active
        
    Returns:
        bool: Success status
    """
    # Ensure prompts directory exists
    ensure_prompts_dir()
    
    # Load existing data
    if not JOB_DESCRIPTION_PROMPT_FILE.exists():
        logger.error(f"Prompt file not found: {JOB_DESCRIPTION_PROMPT_FILE}")
        return False
    
    try:
        with open(JOB_DESCRIPTION_PROMPT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if version exists
        if version not in data.get("versions", {}):
            logger.error(f"Version {version} not found in prompt file")
            return False
        
        # Update active version
        data["active_version"] = version
        data["updated_at"] = datetime.now().isoformat()
        
        # Save to file
        with open(JOB_DESCRIPTION_PROMPT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Set active prompt version to {version}")
        return True
    
    except Exception as e:
        logger.error(f"Error setting active prompt version: {str(e)}")
        return False

def list_prompt_versions():
    """
    List all available prompt versions
    
    Returns:
        dict: Dictionary with version information
    """
    # Ensure prompts directory exists
    ensure_prompts_dir()
    
    # Load existing data
    if not JOB_DESCRIPTION_PROMPT_FILE.exists():
        logger.error(f"Prompt file not found: {JOB_DESCRIPTION_PROMPT_FILE}")
        return {"active_version": "1.0", "versions": {}}
    
    try:
        with open(JOB_DESCRIPTION_PROMPT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract version information
        active_version = data.get("active_version", "1.0")
        versions_info = {}
        
        for version, info in data.get("versions", {}).items():
            versions_info[version] = {
                "created_at": info.get("created_at", ""),
                "description": info.get("description", ""),
                "author": info.get("author", ""),
                "is_active": version == active_version
            }
        
        result = {
            "active_version": active_version,
            "versions": versions_info,
            "count": len(versions_info)
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error listing prompt versions: {str(e)}")
        return {"active_version": "1.0", "versions": {}, "error": str(e)}

# Alias for backward compatibility
list_available_prompt_versions = list_prompt_versions
