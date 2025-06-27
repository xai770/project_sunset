#!/usr/bin/env python3
"""
JMFS Pipeline Runner

This script provides a comprehensive interface to run the entire
Job Match Feedback System (JMFS) pipeline from start to finish.
"""
import os
import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import pipeline modules
from run_pipeline.job_matcher.cv_loader import load_cv_text
from run_pipeline.job_matcher.job_processor import process_job, update_job_json
from run_pipeline.export_job_matches import export_job_matches
try:
    from run_pipeline.reset_pipeline import reset_scan_progress, reset_job_evaluations, delete_response_files
    RESET_AVAILABLE = True
except ImportError:
    print("WARNING: Reset functionality not available")
    RESET_AVAILABLE = False

def fetch_jobs():
    """
    Run the job fetching part of the pipeline.
    
    Returns:
        int: Return code from the subprocess
    """
    print("=== FETCHING JOBS ===")
    # Assuming there's a job fetch script - adjust as needed
    fetch_script = os.path.join(PROJECT_ROOT, "run_pipeline", "fetch_jobs.py")
    if not os.path.exists(fetch_script):
        print(f"WARNING: Fetch script not found at {fetch_script}")
        print("Skipping job fetching step")
        return 0
    
    cmd = [sys.executable, fetch_script]
    print(f"Running: {' '.join(cmd)}")
    return subprocess.call(cmd)

def process_jobs(job_ids=None, num_runs=5, dump_input=True, reset=False):
    """
    Process jobs with LLM evaluation.
    
    Args:
        job_ids: List of specific job IDs to process (None for all jobs)
        num_runs: Number of LLM runs per job
        dump_input: Whether to dump the input prompts
        reset: Whether to reset evaluations before processing
        
    Returns:
        list: List of processed job IDs
    """
    print("=== PROCESSING JOBS WITH LLM ===")
    
    # Reset evaluations if requested
    if reset and RESET_AVAILABLE:
        if job_ids:
            reset_job_evaluations(job_ids)
        else:
            reset_job_evaluations()
    
    try:
        # Load CV text
        cv_text = load_cv_text()
        print(f"CV loaded ({len(cv_text)} characters)")
    except Exception as e:
        print(f"ERROR: Failed to load CV: {e}")
        return []
    
    # Determine which jobs to process
    if job_ids:
        # Process specific jobs
        jobs_to_process = job_ids
    else:
        # Process all jobs (load from scan progress)
        scan_progress_path = os.path.join(PROJECT_ROOT, "data", "job_scans", "search_api_scan_progress.json")
        try:
            import json
            with open(scan_progress_path, "r") as f:
                progress_data = json.load(f)
            jobs_to_process = progress_data.get("jobs_processed", [])
            print(f"Found {len(jobs_to_process)} jobs in scan progress")
        except Exception as e:
            print(f"ERROR: Failed to load jobs from scan progress: {e}")
            return []
    
    # Process each job
    processed_jobs = []
    for job_id in jobs_to_process:
        print(f"\nProcessing job {job_id}...")
        try:
            job_result = process_job(str(job_id), cv_text, num_runs=num_runs, dump_input=dump_input)
            if "error" not in job_result:
                update_job_json(str(job_id), job_result)
                processed_jobs.append(job_id)
        except Exception as e:
            print(f"ERROR processing job {job_id}: {e}")
    
    print(f"\nSuccessfully processed {len(processed_jobs)} jobs")
    return processed_jobs

def export_results(processed_jobs=None):
    """
    Export job results to Excel.
    
    Args:
        processed_jobs: List of job IDs to export (None for all)
        
    Returns:
        str: Path to the exported file
    """
    print("=== EXPORTING RESULTS ===")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Set up export arguments
    export_args = {
        "output_format": "excel",
        "feedback_system": True,
        "reviewer_name": "pipeline"
    }
    
    if processed_jobs:
        export_args["job_ids"] = [str(jid) for jid in processed_jobs]
    
    # Export to Excel
    try:
        output_path = export_job_matches(**export_args)
        if output_path:
            print(f"Successfully exported results to: {output_path}")
        else:
            print("No results to export")
        return output_path
    except Exception as e:
        print(f"ERROR: Failed to export results: {e}")
        return None

def run_pipeline(args):
    """
    Run the complete pipeline.
    
    Args:
        args: Command-line arguments
        
    Returns:
        int: Return code (0 for success, non-zero for error)
    """
    start_time = datetime.now()
    print(f"=== STARTING JMFS PIPELINE AT {start_time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    
    # Reset pipeline if requested
    if args.reset_pipeline and RESET_AVAILABLE:
        print("Resetting pipeline state...")
        if args.full_reset:
            # Full reset (scan progress + evaluations)
            reset_scan_progress()
            reset_job_evaluations()
            if args.delete_responses:
                delete_response_files()
        else:
            # Partial reset based on options
            if args.reset_scan:
                reset_scan_progress()
            if args.reset_evaluations:
                reset_job_evaluations(args.job_ids)
            if args.delete_responses:
                delete_response_files()
    
    # Step 1: Fetch jobs
    if args.fetch_jobs:
        fetch_result = fetch_jobs()
        if fetch_result != 0:
            print(f"WARNING: Job fetching returned non-zero code: {fetch_result}")
    
    # Step 2: Process jobs
    processed_jobs = []
    if args.process_jobs:
        processed_jobs = process_jobs(
            job_ids=args.job_ids,
            num_runs=args.num_runs,
            dump_input=args.dump_input,
            reset=args.reset_evaluations
        )
    
    # Step 3: Export results
    if args.export_results:
        export_path = export_results(processed_jobs if processed_jobs else args.job_ids)
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n=== JMFS PIPELINE COMPLETED AT {end_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"Total runtime: {duration}")
    
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the JMFS pipeline")
    
    # Pipeline stages
    parser.add_argument("--fetch-jobs", action="store_true", help="Fetch jobs")
    parser.add_argument("--process-jobs", action="store_true", help="Process jobs")
    parser.add_argument("--export-results", action="store_true", help="Export results")
    parser.add_argument("--run-all", action="store_true", help="Run the complete pipeline")
    
    # Job options
    parser.add_argument("--job-ids", nargs="*", type=str, help="Specific job IDs to process")
    parser.add_argument("--num-runs", type=int, default=5, help="Number of LLM runs per job")
    parser.add_argument("--dump-input", action="store_true", help="Dump input prompts")
    
    # Reset options
    parser.add_argument("--reset-pipeline", action="store_true", help="Reset pipeline state before running")
    parser.add_argument("--reset-scan", action="store_true", help="Reset scan progress")
    parser.add_argument("--reset-evaluations", action="store_true", help="Reset job evaluations")
    parser.add_argument("--delete-responses", action="store_true", help="Delete response files")
    parser.add_argument("--full-reset", action="store_true", help="Full pipeline reset")
    
    args = parser.parse_args()
    
    # Default to run-all if no specific stages are specified
    if not (args.fetch_jobs or args.process_jobs or args.export_results):
        args.run_all = True
    
    # Enable all stages if run-all is specified
    if args.run_all:
        args.fetch_jobs = True
        args.process_jobs = True
        args.export_results = True
    
    sys.exit(run_pipeline(args))
