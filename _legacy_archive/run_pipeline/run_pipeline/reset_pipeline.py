#!/usr/bin/env python3
"""
Reset utility for the job matching pipeline.

This script allows resetting various parts of the pipeline state
to enable rerunning the pipeline from scratch.
"""
import os
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path
import sys

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import paths
from run_pipeline.config.paths import JOB_DATA_DIR

def reset_scan_progress():
    """
    Reset the search API scan progress file to empty state.
    
    Returns:
        bool: True if reset successful, False otherwise
    """
    scan_progress_path = os.path.join(PROJECT_ROOT, "data", "job_scans", "search_api_scan_progress.json")
    
    if os.path.exists(scan_progress_path):
        # Create backup of current file
        backup_path = scan_progress_path + f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(scan_progress_path, backup_path)
        print(f"Backup created: {backup_path}")
        
        # Reset to initial state
        initial_state = {
            "last_page_fetched": 0,
            "jobs_processed": [],
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "total_jobs_found": 0,
                "total_jobs_processed": 0,
                "total_pages_fetched": 0
            }
        }
        
        with open(scan_progress_path, "w", encoding="utf-8") as f:
            json.dump(initial_state, f, indent=2)
        
        print(f"Scan progress reset: {scan_progress_path}")
        return True
    else:
        print(f"Scan progress file not found: {scan_progress_path}")
        return False

def reset_job_evaluations(job_ids=None):
    """
    Reset LLM evaluations for specific jobs or all jobs.
    
    Args:
        job_ids: List of job IDs to reset (None for all jobs)
        
    Returns:
        int: Number of jobs reset
    """
    reset_count = 0
    
    if job_ids:
        # Reset specific jobs
        for job_id in job_ids:
            job_path = os.path.join(JOB_DATA_DIR, f"job{job_id}.json")
            if os.path.exists(job_path):
                try:
                    with open(job_path, "r", encoding="utf-8") as f:
                        job_data = json.load(f)
                    
                    # Remove LLM evaluation
                    if "llama32_evaluation" in job_data:
                        del job_data["llama32_evaluation"]
                        
                        with open(job_path, "w", encoding="utf-8") as f:
                            json.dump(job_data, f, indent=2)
                        
                        reset_count += 1
                        print(f"Reset evaluation for job {job_id}")
                except Exception as e:
                    print(f"Error resetting job {job_id}: {e}")
    else:
        # Reset all jobs
        job_files = list(Path(JOB_DATA_DIR).glob("job*.json"))
        for job_file in job_files:
            try:
                with open(job_file, "r", encoding="utf-8") as f:
                    job_data = json.load(f)
                
                # Remove LLM evaluation
                if "llama32_evaluation" in job_data:
                    del job_data["llama32_evaluation"]
                    
                    with open(job_file, "w", encoding="utf-8") as f:
                        json.dump(job_data, f, indent=2)
                    
                    reset_count += 1
                    job_id = job_file.stem.replace("job", "")
                    print(f"Reset evaluation for job {job_id}")
            except Exception as e:
                print(f"Error resetting {job_file}: {e}")
    
    print(f"Reset {reset_count} job evaluations")
    return reset_count

def delete_response_files():
    """
    Delete all LLM response files to free up space.
    
    Returns:
        int: Number of files deleted
    """
    pattern_list = [
        "*_llm_input.txt",
        "*_all_llm_responses.txt",
        "*_llm_output.txt"
    ]
    
    file_count = 0
    for pattern in pattern_list:
        files = list(Path(JOB_DATA_DIR).glob(pattern))
        for file_path in files:
            try:
                os.remove(file_path)
                file_count += 1
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    
    print(f"Deleted {file_count} LLM response files")
    return file_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset utility for the job matching pipeline")
    parser.add_argument("--reset-scan-progress", action="store_true", help="Reset the search API scan progress")
    parser.add_argument("--reset-job-evaluations", action="store_true", help="Reset all job evaluations")
    parser.add_argument("--job-ids", nargs="*", type=str, help="Specific job IDs to reset")
    parser.add_argument("--delete-response-files", action="store_true", help="Delete all LLM response files")
    parser.add_argument("--full-reset", action="store_true", help="Perform full reset (scan progress + all evaluations)")
    
    args = parser.parse_args()
    
    # Check if any actions were specified
    if not (args.reset_scan_progress or args.reset_job_evaluations or args.job_ids or args.delete_response_files or args.full_reset):
        parser.print_help()
        sys.exit(1)
    
    # Handle full reset
    if args.full_reset:
        print("Performing full reset...")
        reset_scan_progress()
        reset_job_evaluations()
        delete_response_files()
        print("Full reset completed")
        sys.exit(0)
    
    # Individual actions
    if args.reset_scan_progress:
        reset_scan_progress()
    
    if args.reset_job_evaluations:
        reset_job_evaluations(args.job_ids)
    
    if args.delete_response_files:
        delete_response_files()
