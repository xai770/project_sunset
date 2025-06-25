#!/usr/bin/env python3
"""
Script to remove the 'full_description' field from job role JSONs.
This script reduces file sizes by removing the large, unnecessary text blobs.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('remove_full_description')

# Define job data directory
JOB_DATA_DIR = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/postings'))


def remove_full_description():
    """
    Remove the 'full_description' field from all job JSON files
    """
    # Create a timestamp for the backup directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = JOB_DATA_DIR.parent / f"postings_backup_{timestamp}"
    
    # Ensure the job data directory exists
    if not JOB_DATA_DIR.exists():
        logger.error(f"Job data directory not found: {JOB_DATA_DIR}")
        return False

    # Find all job files
    job_files = sorted(list(JOB_DATA_DIR.glob("job*.json")))
    logger.info(f"Found {len(job_files)} job files to process")
    
    # Create backup directory if any files need modification
    files_to_modify = []
    for job_file in job_files:
        with open(job_file, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
            
        if 'web_details' in job_data and 'full_description' in job_data.get('web_details', {}):
            files_to_modify.append(job_file)
    
    if not files_to_modify:
        logger.info("No files need modification. Exiting.")
        return True
    
    # Create backup directory
    logger.info(f"Creating backup directory: {backup_dir}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files to backup directory before modification
    logger.info(f"Backing up {len(files_to_modify)} files before modification")
    for job_file in files_to_modify:
        backup_file = backup_dir / job_file.name
        with open(job_file, 'r', encoding='utf-8') as src, open(backup_file, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
    
    # Process each job file
    modified_count = 0
    for job_file in files_to_modify:
        try:
            # Read job data
            with open(job_file, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Remove full_description if it exists
            if 'web_details' in job_data and 'full_description' in job_data.get('web_details', {}):
                # Calculate size to report space savings
                full_description = job_data['web_details']['full_description']
                size_before = len(json.dumps(job_data, ensure_ascii=False))
                
                # Remove the field
                del job_data['web_details']['full_description']
                
                # If web_details is now empty, remove it too
                if not job_data['web_details']:
                    del job_data['web_details']
                
                # Calculate size after removal
                size_after = len(json.dumps(job_data, ensure_ascii=False))
                size_reduction = size_before - size_after
                percentage_reduction = (size_reduction / size_before) * 100
                
                # Update metadata to record this change
                if 'metadata' not in job_data:
                    job_data['metadata'] = {}
                
                if 'last_updated' not in job_data['metadata']:
                    job_data['metadata']['last_updated'] = {}
                
                now = datetime.now().isoformat()
                job_data['metadata']['last_updated']['full_description_removed_at'] = now
                
                # Add log entry
                if 'log' not in job_data:
                    job_data['log'] = []
                
                job_data['log'].append({
                    "timestamp": now,
                    "module": "remove_full_description",
                    "action": "remove_full_description",
                    "message": f"Removed full_description field ({len(full_description)} chars, {size_reduction} bytes, {percentage_reduction:.2f}% reduction)"
                })
                
                # Save updated job data
                with open(job_file, 'w', encoding='utf-8') as f:
                    json.dump(job_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Removed full_description from {job_file.name}, saved {size_reduction} bytes ({percentage_reduction:.2f}%)")
                modified_count += 1
                
        except Exception as e:
            logger.error(f"Error processing {job_file}: {str(e)}")
    
    logger.info(f"Processing complete. Modified {modified_count} files. Backup stored in: {backup_dir}")
    return True


if __name__ == "__main__":
    remove_full_description()
