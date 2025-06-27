"""
Template Manager for Cover Letter Generator

This module handles finding, loading, and filling cover letter templates with job-specific details.
"""

import os
import re
import logging
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

# Use absolute imports for all internal modules if needed
# Example: from run_pipeline.cover_letter import profile_manager

def find_best_template(script_dir, default_output_dir):
    """
    Find the best available cover letter template file
    
    Searches in multiple locations for a template file
    
    Args:
        script_dir (str): Directory of the script
        default_output_dir (str): Default output directory
        
    Returns:
        str: Path to the best available template
    """
    # Add logging to show where we're looking
    logger.info(f"Looking for cover letter template...")
    
    # First check in templates directory (recommended location)
    # Try multiple ways to find the project root to be more robust
    possible_project_roots = [
        os.path.dirname(os.path.dirname(os.path.dirname(script_dir))),  # Current method
        os.path.dirname(os.path.dirname(script_dir)),  # Alternative
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".."),  # From module
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")),  # Absolute path
    ]
    
    # Add a direct path to the project root if we can determine it
    if os.path.exists("/home/xai/Documents/sunset"):
        possible_project_roots.append("/home/xai/Documents/sunset")
    
    # Check all possible project roots
    for project_root in possible_project_roots:
        templates_dir = os.path.join(project_root, "templates")
        templates_dir_template = os.path.join(templates_dir, "cover_letter_template.md")
        logger.info(f"Checking {templates_dir_template}")
        if os.path.exists(templates_dir_template):
            logger.info(f"Using template from templates directory: {templates_dir_template}")
            return templates_dir_template
        
    # Then check the script directory
    script_template = os.path.join(script_dir, "cover_letter_template.md")
    logger.info(f"Checking {script_template}")
    if os.path.exists(script_template):
        logger.info(f"Using template from script directory: {script_template}")
        return script_template
    
    # Then check the cover letter module directory
    module_template = os.path.join(os.path.dirname(__file__), "cover_letter_template.md")
    logger.info(f"Checking {module_template}")
    if os.path.exists(module_template):
        logger.info(f"Using template from module directory: {module_template}")
        return module_template
    
    # Then check the output directory
    output_dir_template = os.path.join(default_output_dir, "cover_letter_template.md")
    logger.info(f"Checking {output_dir_template}")
    if os.path.exists(output_dir_template):
        logger.info(f"Using template from output directory: {output_dir_template}")
        return output_dir_template
    
    # Finally check the parent directory
    parent_template = os.path.join(os.path.dirname(script_dir), "cover_letter_template.md")
    logger.info(f"Checking {parent_template}")
    if os.path.exists(parent_template):
        logger.info(f"Using template from parent directory: {parent_template}")
        return parent_template
    
    # Default to the script directory, but it will fail if not found
    logger.warning(f"No template found, defaulting to {script_template}")
    return script_template

def generate_cover_letter(template_path, job_details):
    """
    Generate a cover letter by filling the template with job details
    
    Args:
        template_path (str): Path to the template file
        job_details (dict): Dictionary with job details to fill the template
        
    Returns:
        str: Filled cover letter content or None if there was an error
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as template_file:
            template = template_file.read()
            
        # Handle special visual elements
        has_skill_chart = "skill_match_chart" in job_details
        has_qualification_summary = "qualification_summary" in job_details
        has_achievements = "quantifiable_achievements" in job_details
        has_skill_timeline = "skill_progression_timeline" in job_details
        
        # Debug outputs to help diagnose issues
        print(f"Has skill chart: {has_skill_chart}")
        print(f"Has qualification summary: {has_qualification_summary}")
        print(f"Has achievements: {has_achievements}")
        print(f"Has skill timeline: {has_skill_timeline}")
        
        # Replace placeholders with job details
        for key, value in job_details.items():
            placeholder = "{" + key + "}"
            # All placeholders use the same format now
            if value is not None:  # Only replace if value exists
                template = template.replace(placeholder, str(value))
                print(f"Replaced placeholder '{placeholder}' with content of length {len(str(value))}")
            else:
                print(f"Warning: No value for placeholder '{placeholder}'")
            
            # Also check for HTML comment-style placeholders for backward compatibility
            comment_placeholder = f"<!-- {key.upper()} -->"
            if comment_placeholder in template and value is not None:
                template = template.replace(comment_placeholder, str(value))
        
        # Double-check that all special placeholders are replaced
        if "{skill_match_chart}" in template and has_skill_chart:
            print(f"Warning: skill_match_chart placeholder still present after replacement")
            # Force direct replacement for special elements
            template = template.replace("{skill_match_chart}", job_details.get("skill_match_chart", ""))
            
        if "{qualification_summary}" in template and has_qualification_summary:
            print(f"Warning: qualification_summary placeholder still present after replacement")
            # Force direct replacement for special elements
            template = template.replace("{qualification_summary}", job_details.get("qualification_summary", ""))
            
        if "{quantifiable_achievements}" in template and has_achievements:
            print(f"Warning: quantifiable_achievements placeholder still present after replacement")
            # Force direct replacement for special elements
            template = template.replace("{quantifiable_achievements}", job_details.get("quantifiable_achievements", ""))
            
        if "{skill_progression_timeline}" in template and has_skill_timeline:
            print(f"Warning: skill_progression_timeline placeholder still present after replacement")
            # Force direct replacement for special elements
            template = template.replace("{skill_progression_timeline}", job_details.get("skill_progression_timeline", ""))
            
        # Add quantifiable achievements before the closing paragraph if not replaced by placeholder
        if has_achievements and "{quantifiable_achievements}" not in template:
            # Find closing paragraph to insert achievements before
            closing_section = re.search(r'I am motivated.*?interview', template, re.DOTALL)
            if closing_section:
                closing_start = closing_section.start()
                achievements_section = f"{job_details.get('quantifiable_achievements', '')}\n\n"
                template = template[:closing_start] + achievements_section + template[closing_start:]
        
        # Handle skill progression timeline
        if has_skill_timeline:
            # Directly insert the skill progression timeline where the placeholder is
            template = template.replace("{skill_progression_timeline}", job_details.get("skill_progression_timeline", ""))
        else:
            # If no timeline provided, remove the placeholder to avoid empty section
            template = template.replace("{skill_progression_timeline}", "")
        
        logger.info(f"Successfully generated enhanced cover letter from template: {template_path}")
        return template
    except Exception as e:
        logger.error(f"Error generating cover letter: {e}")
        return None

def sanitize_filename(text):
    """
    Convert a string to a valid filename by replacing invalid characters
    
    Args:
        text (str): Text to sanitize
        
    Returns:
        str: Sanitized text suitable for a filename
    """
    # Replace spaces and special characters with underscores
    return re.sub(r'[^\w\-]', '_', text)

def format_date_german():
    """
    Return the current date in German format
    
    Returns:
        str: Current date formatted in German style
    """
    today = datetime.now()
    return today.strftime("%d. %B %Y").replace("January", "Januar")\
                                      .replace("February", "Februar")\
                                      .replace("March", "März")\
                                      .replace("April", "April")\
                                      .replace("May", "Mai")\
                                      .replace("June", "Juni")\
                                      .replace("July", "Juli")\
                                      .replace("August", "August")\
                                      .replace("September", "September")\
                                      .replace("October", "Oktober")\
                                      .replace("November", "November")\
                                      .replace("December", "Dezember")

def save_cover_letter(content, job_id, job_title, output_dir, custom_filename=None):
    """
    Save the generated cover letter to a file
    
    Args:
        content (str): Cover letter content
        job_id (str): Job ID
        job_title (str): Job title
        output_dir (str): Output directory
        custom_filename (str, optional): Custom filename to use instead of the generated one
        
    Returns:
        str: Path to the saved file or None if there was an error
    """
    if custom_filename:
        filename = custom_filename
    else:
        sanitized_title = sanitize_filename(job_title)
        filename = f"Cover_Letter_{job_id}_{sanitized_title}.md"
    filepath = os.path.join(output_dir, filename)
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as output_file:
            output_file.write(content)
        logger.info(f"Cover letter saved to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving cover letter: {e}")
        return None