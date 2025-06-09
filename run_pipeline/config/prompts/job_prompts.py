#!/usr/bin/env python3
"""
Job Description Prompts

This module provides centralized storage and versioning for job description prompts.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Get the parent directory for the config
CONFIG_DIR = Path(__file__).resolve().parent.parent
PROMPTS_FILE = CONFIG_DIR / "prompts" / "job_description_prompts.json"

logger = logging.getLogger("job_prompts")

# Default job description prompt
DEFAULT_JOB_DESCRIPTION_PROMPT = """Extract ONLY the English version of this job description from Deutsche Bank. 

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

def get_prompts_file():
    """Get the path to the prompts file, creating parent directories if needed"""
    os.makedirs(PROMPTS_FILE.parent, exist_ok=True)
    return PROMPTS_FILE

def load_prompts():
    """Load prompts from JSON file"""
    prompts_file = get_prompts_file()
    
    if not prompts_file.exists():
        # Initialize with default values
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "job_description": {
                "prompt": DEFAULT_JOB_DESCRIPTION_PROMPT,
                "description": "Default job description extraction prompt"
            }
        }
        save_prompts(data)
        return data
    
    try:
        with open(prompts_file, 'r', encoding='utf-8') as f:
            return json.load(f)  # type: ignore
    except Exception as e:
        logger.error(f"Error loading prompts: {str(e)}")
        return {
            "version": "error",
            "updated_at": datetime.now().isoformat(),
            "job_description": {
                "prompt": DEFAULT_JOB_DESCRIPTION_PROMPT,
                "description": "Fallback prompt due to error loading prompts file"
            }
        }

def save_prompts(data):
    """Save prompts to JSON file"""
    prompts_file = get_prompts_file()
    try:
        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving prompts: {str(e)}")
        return False

def get_job_description_prompt():
    """Get the current job description prompt"""
    prompts = load_prompts()
    return prompts.get("job_description", {}).get("prompt", DEFAULT_JOB_DESCRIPTION_PROMPT)

def get_prompt_version():
    """Get the current version of the prompts"""
    prompts = load_prompts()
    return prompts.get("version", "1.0")

def update_job_description_prompt(new_prompt, description=None):
    """Update the job description prompt with a new version"""
    prompts = load_prompts()
    
    # Increment version
    current_version = prompts.get("version", "1.0")
    version_parts = current_version.split(".")
    new_version = f"{version_parts[0]}.{int(version_parts[1]) + 1}"
    
    prompts["version"] = new_version
    prompts["updated_at"] = datetime.now().isoformat()
    prompts["job_description"] = {
        "prompt": new_prompt,
        "description": description or f"Updated job description prompt (v{new_version})",
        "updated_at": datetime.now().isoformat()
    }
    
    save_prompts(prompts)
    return new_version

def job_needs_reprocessing(job_metadata):
    """Check if a job needs reprocessing based on prompt version"""
    # If the job has no metadata or is a placeholder, it needs reprocessing
    if not job_metadata or "web_details" not in job_metadata:
        return True
    
    job_details = job_metadata["web_details"]
    
    if "description_metadata" not in job_details:
        return True
    
    description_meta = job_details["description_metadata"]
    
    # If it's a placeholder, it definitely needs reprocessing
    if description_meta.get("is_placeholder", False):
        return True
    
    # If the job doesn't have a prompt version in metadata, it was created before versioning
    if "prompt_version" not in description_meta:
        return True
    
    # Check if the current version is newer than the job's version
    job_prompt_version = description_meta["prompt_version"]
    current_version = get_prompt_version()
    
    # Compare version numbers
    try:
        job_version_parts = [int(i) for i in job_prompt_version.split('.')]
        current_version_parts = [int(i) for i in current_version.split('.')]
        
        # If the current version is higher, the job needs reprocessing
        return current_version_parts > job_version_parts
    except:
        # If there's any error parsing versions, default to reprocessing
        return True
