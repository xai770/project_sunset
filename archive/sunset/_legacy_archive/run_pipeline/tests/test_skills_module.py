#!/usr/bin/env python3
"""
Test script for the skills module
"""

import sys
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the skills module
from run_pipeline.core.skills_module import process_skills
from run_pipeline.config.paths import ensure_directories

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def main():
    """
    Main entry point
    """
    try:
        # Ensure required directories exist
        ensure_directories()
        
        # Process skills for a specific job ID (modify as needed)
        job_ids = ["61691"]  # Example job ID
        
        print(f"Starting skill processing for job IDs: {job_ids}")
        
        # Run the skills processor
        success = process_skills(job_ids=job_ids)
        
        print(f"Skill processing completed with status: {success}")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error in test_skills_module: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
