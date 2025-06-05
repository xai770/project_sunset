#!/usr/bin/env python3
"""
Script to remove full_description field from all job postings to save space.

This script processes all job files in the data/postings directory
and removes the full_description field from the web_details section.
"""

import os
import json
import sys
import logging
from pathlib import Path
from datetime import datetime

# Get the project root directory
script_path = Path(__file__).resolve()
PROJECT_ROOT = script_path.parent.parent.parent  # Navigate up to sunset directory
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import configuration
from run_pipeline.config.paths import JOB_DATA_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/remove_full_descriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger('remove_full_descriptions')

def main():
    """Process all job files and remove full_description field"""
    job_dir = Path(JOB_DATA_DIR)
    job_files = sorted([f for f in os.listdir(job_dir) if f.startswith('job') and f.endswith('.json')])
    
    logger.info(f"Found {len(job_files)} job files to process")
    
    jobs_processed = 0
    jobs_modified = 0
    space_saved = 0  # In bytes
    
    for job_file in job_files:
        job_path = job_dir / job_file
        
        try:
            # Read job file
            with open(job_path, 'r', encoding='utf-8') as f:
                original_size = os.path.getsize(job_path)
                job_data = json.load(f)
            
            modified = False
            
            # Remove full_description if it exists
            if "web_details" in job_data and "full_description" in job_data["web_details"]:
                # Calculate size of the field to track space savings
                full_desc_size = len(json.dumps(job_data["web_details"]["full_description"]))
                
                # Remove the field
                del job_data["web_details"]["full_description"]
                modified = True
                space_saved += full_desc_size
                
                # Add log entry
                if "log" not in job_data:
                    job_data["log"] = []
                
                job_data["log"].append({
                    "timestamp": datetime.now().isoformat(),
                    "script": "run_pipeline.utils.remove_full_descriptions",
                    "action": "remove_full_description",
                    "message": f"Removed full_description field to save space"
                })
                
                # Write back to file
                with open(job_path, 'w', encoding='utf-8') as f:
                    json.dump(job_data, f, indent=2, ensure_ascii=False)
                
                new_size = os.path.getsize(job_path)
                actual_saved = original_size - new_size
                logger.info(f"Removed full_description from {job_file}, saved {actual_saved} bytes")
                jobs_modified += 1
            
            jobs_processed += 1
            
        except Exception as e:
            logger.error(f"Error processing {job_file}: {str(e)}")
    
    logger.info("=" * 50)
    logger.info("Processing complete")
    logger.info(f"Total jobs processed: {jobs_processed}")
    logger.info(f"Jobs modified: {jobs_modified}")
    logger.info(f"Estimated space saved: {space_saved / (1024*1024):.2f} MB")
    logger.info("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
