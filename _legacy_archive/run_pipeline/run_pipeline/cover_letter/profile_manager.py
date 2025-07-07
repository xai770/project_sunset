"""
Profile Manager for Cover Letter Generator

This module handles loading and saving user profile data for the cover letter generator.
It stores preferences like company information and skill descriptions to reuse across
multiple cover letter generation sessions.
"""

import os
import json
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Use absolute imports for all internal modules if needed
# Example: from run_pipeline.cover_letter import skill_library

def get_profile_path(base_dir):
    """
    Get the path to the profile storage file
    
    Args:
        base_dir (str): Base directory for the application
        
    Returns:
        str: Path to the profile JSON file
    """
    return os.path.join(base_dir, "cover_letter_profile.json")

def load_profile(base_dir):
    """
    Load saved profile data if available
    
    Args:
        base_dir (str): Base directory for the application
        
    Returns:
        dict: User profile data or empty dictionary if no profile exists
    """
    profile_path = get_profile_path(base_dir)
    
    if os.path.exists(profile_path):
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                logger.debug(f"Loading profile from {profile_path}")
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load profile from {profile_path}: {e}")
            return {}
    
    logger.debug("No profile file found, using empty profile")
    return {}

def save_profile(profile_data, base_dir):
    """
    Save profile data for future use
    
    Args:
        profile_data (dict): User profile data to save
        base_dir (str): Base directory for the application
        
    Returns:
        bool: True if successful, False if there was an error
    """
    profile_path = get_profile_path(base_dir)
    
    try:
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2)
        logger.info(f"Saved profile to {profile_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving profile to {profile_path}: {e}")
        return False

def extract_profile_from_job_details(job_details):
    """
    Extract profile data from job details
    
    Extracts the reusable fields from job details for saving as a profile
    
    Args:
        job_details (dict): Complete job details dictionary
        
    Returns:
        dict: Profile data suitable for saving
    """
    # Fields to exclude from the profile
    exclude_fields = ["date", "skill_bullets", "job_id", "job_title", "reference_number"]
    
    # Create profile with all fields except excluded ones
    profile = {k: v for k, v in job_details.items() if k not in exclude_fields}
    
    return profile

def prompt_save_profile(job_details, base_dir):
    """
    Prompt the user to save their profile
    
    Args:
        job_details (dict): Job details to extract profile from
        base_dir (str): Base directory for the application
        
    Returns:
        bool: True if profile was saved, False otherwise
    """
    print("\nMöchten Sie diese Einstellungen für zukünftige Anschreiben speichern? (j/n)")
    if input("> ").lower().startswith("j"):
        profile_data = extract_profile_from_job_details(job_details)
        return save_profile(profile_data, base_dir)
    return False