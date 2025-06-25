#!/usr/bin/env python3
"""
Prompt Manager Utility

This module provides utilities for managing, versioning, and retrieving LLM prompts.
It allows for tracking prompt versions, retrieving the latest or specific versions,
and determining if a job needs reprocessing based on prompt changes.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

from run_pipeline.config.paths import PROJECT_ROOT

# Define prompts directory path
PROMPTS_DIR = PROJECT_ROOT / "run_pipeline" / "config" / "prompts"

logger = logging.getLogger('prompt_manager')

def ensure_prompts_dir():
    """Ensure prompts directory exists"""
    os.makedirs(PROMPTS_DIR, exist_ok=True)
    return PROMPTS_DIR


def load_prompt_file(prompt_type):
    """
    Load a prompt file for a specific prompt type
    
    Args:
        prompt_type (str): The type of prompt (e.g., 'job_description')
        
    Returns:
        dict: The prompt data or empty dict if not found
    """
    prompt_file = PROMPTS_DIR / f"{prompt_type}_prompts.json"
    
    if not prompt_file.exists():
        logger.debug(f"Prompt file {prompt_file} not found")
        return {}
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Error loading prompt file {prompt_file}: {str(e)}")
        return {}


def save_prompt_file(prompt_type, data):
    """
    Save prompt data to a file
    
    Args:
        prompt_type (str): The type of prompt
        data (dict): The prompt data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    ensure_prompts_dir()
    prompt_file = PROMPTS_DIR / f"{prompt_type}_prompts.json"
    
    try:
        with open(prompt_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving prompt file {prompt_file}: {str(e)}")
        return False


def get_latest_prompt_version(prompt_type):
    """
    Get the latest version number for a prompt type
    
    Args:
        prompt_type (str): The type of prompt
        
    Returns:
        str: The latest version number or None if no versions exist
    """
    data = load_prompt_file(prompt_type)
    
    if not data or 'versions' not in data or not data['versions']:
        return None
    
    # Find the active version
    if 'active_version' in data and data['active_version'] in data['versions']:
        return data['active_version']
    
    # Otherwise return the highest version
    versions = sorted(data['versions'].keys(), key=lambda x: [int(i) for i in x.split('.')])
    return versions[-1] if versions else None


def get_prompt(prompt_type, version=None):
    """
    Get a prompt for a specific type and version
    
    Args:
        prompt_type (str): The type of prompt
        version (str, optional): The specific version to retrieve
                               If None, returns the active/latest version
        
    Returns:
        tuple: (prompt_text, version, metadata) or (None, None, None) if not found
    """
    data = load_prompt_file(prompt_type)
    
    if not data or 'versions' not in data or not data['versions']:
        logger.warning(f"No prompt versions found for {prompt_type}")
        return None, None, None
    
    # If no version specified, use active or latest
    if not version:
        version = get_latest_prompt_version(prompt_type)
        if not version:
            return None, None, None
    
    # Check if the requested version exists
    if version not in data['versions']:
        logger.warning(f"Prompt version {version} not found for {prompt_type}")
        return None, None, None
    
    prompt_data = data['versions'][version]
    prompt_text = prompt_data.get('prompt')
    metadata = {
        'version': version,
        'created_at': prompt_data.get('created_at'),
        'description': prompt_data.get('description'),
        'author': prompt_data.get('author')
    }
    
    return prompt_text, version, metadata


def add_prompt_version(prompt_type, prompt_text, description=None, author=None, set_active=True):
    """
    Add a new prompt version
    
    Args:
        prompt_type (str): The type of prompt
        prompt_text (str): The actual prompt text
        description (str, optional): Description of the prompt or changes
        author (str, optional): Author of the prompt
        set_active (bool): Whether to set this as the active version
        
    Returns:
        str: The new version number
    """
    data = load_prompt_file(prompt_type)
    
    if not data:
        # Initialize new prompt file
        data = {
            'type': prompt_type,
            'versions': {},
            'active_version': None
        }
    
    # Calculate new version number
    versions = list(data['versions'].keys()) if 'versions' in data else []
    if not versions:
        new_version = "1.0"
    else:
        latest = sorted(versions, key=lambda x: [int(i) for i in x.split('.')])[-1]
        major, minor = map(int, latest.split('.'))
        new_version = f"{major}.{minor + 1}"
    
    # Add new version
    if 'versions' not in data:
        data['versions'] = {}
    
    data['versions'][new_version] = {
        'prompt': prompt_text,
        'created_at': datetime.now().isoformat(),
        'description': description or f"Prompt version {new_version}",
        'author': author or "system"
    }
    
    # Set as active if requested
    if set_active:
        data['active_version'] = new_version
    
    # Save the updated data
    save_prompt_file(prompt_type, data)
    logger.info(f"Added new prompt version {new_version} for {prompt_type}")
    
    return new_version


def set_active_prompt_version(prompt_type, version):
    """
    Set the active version for a prompt type
    
    Args:
        prompt_type (str): The type of prompt
        version (str): The version to set as active
        
    Returns:
        bool: True if successful, False otherwise
    """
    data = load_prompt_file(prompt_type)
    
    if not data or 'versions' not in data or version not in data['versions']:
        logger.warning(f"Cannot set active version. Version {version} not found for {prompt_type}")
        return False
    
    data['active_version'] = version
    save_prompt_file(prompt_type, data)
    logger.info(f"Set active version to {version} for {prompt_type}")
    
    return True


def list_prompt_versions(prompt_type):
    """
    List all available versions for a prompt type
    
    Args:
        prompt_type (str): The type of prompt
        
    Returns:
        list: List of version information dictionaries
    """
    data = load_prompt_file(prompt_type)
    
    if not data or 'versions' not in data:
        return []
    
    active_version = data.get('active_version')
    result = []
    
    for version, info in data['versions'].items():
        result.append({
            'version': version,
            'is_active': version == active_version,
            'created_at': info.get('created_at'),
            'description': info.get('description'),
            'author': info.get('author')
        })
    
    # Sort by version number
    result.sort(key=lambda x: [int(i) for i in x['version'].split('.')])
    return result


def needs_reprocessing(job_metadata, prompt_type):
    """
    Check if a job needs reprocessing based on prompt version
    
    Args:
        job_metadata (dict): Job metadata containing description_metadata
        prompt_type (str): The type of prompt to check
        
    Returns:
        bool: True if reprocessing is needed, False otherwise
    """
    # If no description_metadata, it needs reprocessing
    if 'web_details' not in job_metadata or 'description_metadata' not in job_metadata['web_details']:
        return True
    
    description_meta = job_metadata['web_details']['description_metadata']
    
    # If it's a placeholder, it needs reprocessing
    if description_meta.get('is_placeholder', False):
        return True
    
    # If no prompt_version in metadata, it was created before versioning
    if 'prompt_version' not in description_meta:
        return True
    
    # Check if current active version is newer than the one used
    job_prompt_version = description_meta['prompt_version']
    current_version = get_latest_prompt_version(prompt_type)
    
    # If no current version, something's wrong - default to not reprocessing
    if not current_version:
        return False
    
    # Compare version numbers
    job_version_parts = [int(i) for i in job_prompt_version.split('.')]
    current_version_parts = [int(i) for i in current_version.split('.')]
    
    return current_version_parts > job_version_parts


def initialize_default_prompts():
    """
    Initialize the system with default prompts if they don't exist
    
    Returns:
        bool: True if initialization was needed, False if already initialized
    """
    ensure_prompts_dir()
    
    # Default job description prompt
    job_desc_data = load_prompt_file("job_description")
    if not job_desc_data:
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

The result should be a clean, professional job description in English only, with all the essential information about the position preserved exactly as written.

Job posting content:
{job_content}"""
        
        add_prompt_version(
            "job_description", 
            default_prompt, 
            "Initial job description extraction prompt",
            "system",
            True
        )
        logger.info("Initialized default job description prompt")
        return True
    
    return False


# Initialize prompts when the module is imported
initialize_default_prompts()
