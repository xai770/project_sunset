#!/usr/bin/env python3
"""
Main entry point for the job expansion pipeline.
Provides a simple interface for running the complete pipeline.
"""

import sys
import os
import json
from datetime import datetime

# Import required modules for the pipeline
from run_pipeline.config.paths import ensure_directories
from run_pipeline.core.cli_args import parse_args
from run_pipeline.core.pipeline_orchestrator import run_pipeline

def main():
    """
    Main entry point
    """
    # Ensure required directories exist
    ensure_directories()
    
    # Parse command-line arguments
    args = parse_args()
    
    # Handle --reset-progress
    if getattr(args, "reset_progress", False):
        progress_path = os.path.join(os.path.dirname(__file__), '../../data/job_scans/search_api_scan_progress.json')
        progress_path = os.path.abspath(progress_path)
        if os.path.exists(progress_path):
            with open(progress_path, 'w') as f:
                json.dump({
                    "last_page_fetched": 0,
                    "jobs_processed": [],
                    "timestamp": datetime.now().isoformat(),
                    "stats": {
                        "total_jobs_found": 0,
                        "total_jobs_processed": 0,
                        "total_pages_fetched": 0
                    }
                }, f, indent=2)
            print(f"Progress tracker reset: {progress_path}")
        else:
            print(f"Progress tracker file not found: {progress_path}")
        
        # Backup and remove files in data/postings directory
        import shutil
        import glob
        from pathlib import Path
        
        postings_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/postings'))
        backup_dir = os.path.join(os.path.dirname(postings_dir), f"postings_BAK_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if os.path.exists(postings_dir) and os.path.isdir(postings_dir):
            files = glob.glob(os.path.join(postings_dir, "*"))
            if files:
                # Create backup directory if it doesn't exist
                os.makedirs(backup_dir, exist_ok=True)
                
                # Backup files
                print(f"Backing up {len(files)} files from {postings_dir} to {backup_dir}")
                for file_path in files:
                    if os.path.isfile(file_path):
                        shutil.copy2(file_path, backup_dir)
                
                # Remove files
                print(f"Removing {len(files)} files from {postings_dir}")
                for file_path in files:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            else:
                print(f"No files found in {postings_dir}")
    
    # Run the pipeline
    success = run_pipeline(args)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

# Export for external use
__all__ = ['main']

if __name__ == "__main__":
    main()
