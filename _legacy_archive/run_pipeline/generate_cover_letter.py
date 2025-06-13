#!/usr/bin/env python3
"""
Cover Letter Generator (migrated to run_pipeline)

This script generates custom cover letters based on a template file,
filling in job-specific details provided by the user.

The functionality is split into several modules in the cover_letter package:
- template_manager: Handles template loading and filling
- profile_manager: Manages user profile data
- skill_library: Provides skill bullets and selection interface
- generator_cli: Command-line interface utilities
"""

import sys
import os
from pathlib import Path
import logging

# Try import from run_pipeline.cover_letter, fallback to direct import from local cover_letter/ directory
try:
    from run_pipeline.cover_letter import template_manager, profile_manager, skill_library, generator_cli
except ImportError:
    import importlib.util
    import importlib.machinery
    import types
    import_path = os.path.join(os.path.dirname(__file__), 'cover_letter')
    sys.path.insert(0, import_path)
    template_manager = importlib.import_module('template_manager')
    profile_manager = importlib.import_module('profile_manager')
    skill_library = importlib.import_module('skill_library')
    generator_cli = importlib.import_module('generator_cli')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "docs", "cover_letters")
DEFAULT_TEMPLATE_PATH = template_manager.find_best_template(SCRIPT_DIR, DEFAULT_OUTPUT_DIR)

def main():
    """Main function to run the cover letter generator"""
    # Parse command line arguments
    args = generator_cli.parse_arguments(DEFAULT_TEMPLATE_PATH, DEFAULT_OUTPUT_DIR)
    
    # Check if template file exists
    if not os.path.exists(args.template):
        logger.error(f"Template file not found: {args.template}")
        print(f"Fehler: Vorlagendatei nicht gefunden: {args.template}")
        return 1
    
    # Load saved profile for defaults
    profile = profile_manager.load_profile(SCRIPT_DIR)
    
    # Get job details either from interactive mode or command line arguments
    if args.interactive or not (args.job_id and args.job_title):
        job_details = generator_cli.interactive_mode(profile)
        
        # Save profile if requested
        profile_manager.prompt_save_profile(job_details, SCRIPT_DIR)
    else:
        # Create job details from command line args with profile defaults
        job_details = {
            "job_id": args.job_id,
            "job_title": args.job_title,
            "reference_number": args.reference or "",
            "company": profile.get("company", "Deutsche Bank AG"),
            "company_address": profile.get("company_address", "60262 Frankfurt"),
            "department": profile.get("department", ""),
            "primary_expertise_area": profile.get("primary_expertise_area", ""),
            "skill_area_1": profile.get("skill_area_1", ""),
            "skill_area_2": profile.get("skill_area_2", ""),
            "skill_bullets": "\n\n".join([
                skill_library.get_available_skills()["platform_management"], 
                skill_library.get_available_skills()["data_analysis"]
            ]),
            "specific_interest": profile.get("specific_interest", ""),
            "relevant_experience": profile.get("relevant_experience", ""),
            "relevant_understanding": profile.get("relevant_understanding", ""),
            "potential_contribution": profile.get("potential_contribution", ""),
            "value_proposition": profile.get("value_proposition", ""),
            "date": template_manager.format_date_german()
        }
    
    # Generate cover letter
    cover_letter_content = template_manager.generate_cover_letter(args.template, job_details)
    
    if cover_letter_content:
        # Save to file
        output_path = template_manager.save_cover_letter(
            cover_letter_content, 
            job_details["job_id"], 
            job_details["job_title"], 
            args.output
        )
        
        if output_path:
            generator_cli.handle_output_display(output_path, cover_letter_content)
    else:
        logger.error("Failed to generate cover letter")
        print("Fehler bei der Generierung des Anschreibens.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
