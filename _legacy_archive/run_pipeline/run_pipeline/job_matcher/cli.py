#!/usr/bin/env python3
"""
Main CLI for job matching.

This script provides a command line interface for running job matching evaluations.
It is a refactored version of the original test_llama32.py script.
"""
import sys
import argparse
import time
from pathlib import Path
from typing import List

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import local modules
from run_pipeline.job_matcher.cv_utils import get_cv_markdown_text
from run_pipeline.job_matcher.job_processor import process_job, process_feedback, update_job_json
from run_pipeline.config.paths import JOB_DATA_DIR

def parse_job_ids(job_ids_arg: str) -> List[str]:
    """
    Parse job IDs from command line argument.
    
    Args:
        job_ids_arg: Job IDs as string (comma-separated or range with dash)
        
    Returns:
        A list of job IDs
    """
    if "-" in job_ids_arg:
        # Handle range of job IDs
        start_id, end_id = job_ids_arg.split("-")
        try:
            return [str(i) for i in range(int(start_id), int(end_id) + 1)]
        except ValueError:
            print(f"Invalid job ID range: {job_ids_arg}")
            return []
    else:
        # Handle comma-separated list of job IDs
        return [jid.strip() for jid in job_ids_arg.split(",")]

def main():
    """Main function for command line interface."""
    parser = argparse.ArgumentParser(description="Run llama3.2 job matching for specific jobs")
    parser.add_argument("--job-ids", default="61691", 
                        help="Job IDs to process (comma-separated or range with dash, e.g., '61691,61692,61693' or '61691-61695')")
    parser.add_argument("--force", action="store_true", 
                        help="Force reprocessing even if llama32_evaluation already exists")
    parser.add_argument("--dump-input", action="store_true", 
                        help="Dump the LLM input to a text file")
    parser.add_argument("--num-runs", type=int, default=5, 
                        help="Number of times to run the LLM (default: 5)")
    parser.add_argument("--skip-update", action="store_true",
                        help="Skip updating the job JSON files")
    parser.add_argument("--feedback", action="store_true",
                        help="Process feedback for the jobs")
    parser.add_argument("--feedback-text", type=str,
                       help="Feedback text to process (required with --feedback)")
    parser.add_argument("--auto-update", action="store_true",
                       help="Automatically update prompts based on feedback analysis")
    args = parser.parse_args()
    
    # Validate feedback arguments
    if args.feedback and not args.feedback_text:
        print("Error: --feedback-text is required when --feedback is specified")
        return 1
    
    # Parse job IDs
    job_ids = parse_job_ids(args.job_ids)
    if not job_ids:
        return 1
    
    # Get CV text once for all jobs (not needed for feedback processing)
    cv_text = None
    if not args.feedback:
        cv_text = get_cv_markdown_text()
    
    # Process each job
    successful_jobs = 0
    skipped_jobs = 0
    failed_jobs = 0
    
    start_time = time.time()
    
    print(f"Processing {len(job_ids)} job(s): {', '.join(job_ids)}")
    
    for job_id in job_ids:
        # Check if we should skip this job (only for regular processing)
        if not args.feedback and not args.force:
            import os
            import json
            job_path = os.path.join(JOB_DATA_DIR, f"job{job_id}.json")
            try:
                with open(job_path, "r", encoding="utf-8") as jf:
                    job_data = json.load(jf)
                if "llama32_evaluation" in job_data:
                    print(f"Skipping job {job_id} - llama32_evaluation already exists (use --force to override)")
                    skipped_jobs += 1
                    continue
            except Exception:
                # If there's an error reading the file, we'll process it anyway
                pass
        
        # Process the job
        try:
            if args.feedback:
                # Process feedback instead of running the job
                print(f"Processing feedback for job {job_id}...")
                results = process_feedback(job_id, args.feedback_text, args.auto_update)
                
                if "error" in results:
                    print(f"Error processing feedback for job {job_id}: {results['error']}")
                    failed_jobs += 1
                else:
                    print(f"Successfully processed feedback for job {job_id}")
                    if args.auto_update and results.get("analysis", {}).get("prompt_updated"):
                        print(f"Updated prompt to version {results['analysis']['new_prompt_version']}")
                    successful_jobs += 1
            else:
                # Run normal job processing
                results = process_job(job_id, args.num_runs, args.dump_input, cv_text)
                
                if "error" in results:
                    print(f"Job {job_id} processing failed: {results['error']}")
                    failed_jobs += 1
                    continue
                
                # Update the job JSON file
                if not args.skip_update:
                    if update_job_json(job_id, results):
                        successful_jobs += 1
                    else:
                        failed_jobs += 1
                else:
                    print(f"Skipping update of job {job_id} JSON (--skip-update flag set)")
                    successful_jobs += 1
                    
        except Exception as e:
            print(f"Error processing job {job_id}: {e}")
            failed_jobs += 1
    
    # Print summary
    elapsed_time = time.time() - start_time
    print(f"\n{'='*80}\nSummary\n{'='*80}")
    print(f"Processed {len(job_ids)} jobs in {elapsed_time:.1f} seconds")
    print(f"Successful: {successful_jobs}")
    print(f"Skipped: {skipped_jobs}")
    print(f"Failed: {failed_jobs}")
    
    if failed_jobs > 0:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
