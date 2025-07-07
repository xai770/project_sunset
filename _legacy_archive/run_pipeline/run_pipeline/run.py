#!/usr/bin/env python3
"""
Main entry point for the job expansion pipeline.
This script runs the pipeline without a job limit, processing all available jobs.
"""

import sys
import os
from pathlib import Path
import argparse

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Add the project root to path if needed
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.core.pipeline_main import main
from run_pipeline.core.cli_args import parse_args
from run_pipeline.core.pipeline_orchestrator import run_pipeline
from run_pipeline.config.paths import ensure_directories
from run_pipeline.job_matcher.job_processor import process_job, process_feedback
from run_pipeline.job_matcher.cv_utils import get_cv_markdown_text

def run_full_pipeline():
    """
    Run the pipeline with no job limit and default settings optimized for processing all jobs.
    This is a convenience wrapper around the main pipeline processing function.
    """
    # Ensure required directories exist
    ensure_directories()
    
    # Create a parser with the same arguments as the original one
    parser = argparse.ArgumentParser(description="Job Expansion Pipeline")
    temp_args = parse_args()
    
    # Get all attributes from temp_args and create a dictionary
    args_dict = vars(temp_args)
    
    # Set max_jobs to a very high number to effectively remove the limit
    args_dict['max_jobs'] = 99999  # Extremely high number to process all jobs
    
    # Enable skill matching by default
    args_dict['run_skill_matching'] = True
    
    # Run the pipeline with our custom arguments
    success = run_pipeline(argparse.Namespace(**args_dict))
    
    # Exit with appropriate code
    return 0 if success else 1

def run_feedback_loop(job_id, feedback_text, auto_update=False, save_path=None):
    """Run the feedback loop: job match, feedback, re-match."""
    print(f"\n[Feedback Loop] Running for job ID: {job_id}")
    cv_text = get_cv_markdown_text()
    job_result = process_job(job_id, cv_text=cv_text, num_runs=2)
    if "error" in job_result:
        print(f"Error running job match: {job_result.get('error')}")
        return
    match_level = job_result.get("cv_to_role_match", "Unknown")
    print(f"Initial match: {match_level}")
    feedback_result = process_feedback(job_id, feedback_text, auto_update=auto_update)
    if "error" in feedback_result:
        print(f"Error processing feedback: {feedback_result.get('error')}")
        return
    print("Feedback processed.")
    new_job_result = process_job(job_id, cv_text=cv_text, num_runs=2)
    new_match_level = new_job_result.get("cv_to_role_match", "Unknown")
    print(f"Updated match: {new_match_level}")
    results = {
        "job_id": job_id,
        "feedback": feedback_text,
        "original_match": match_level,
        "updated_match": new_match_level,
        "changed": match_level != new_match_level,
        "feedback_analysis": feedback_result.get("analysis", {})
    }
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            import json
            json.dump(results, f, indent=2)
        print(f"Results saved to {save_path}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job Expansion Pipeline with Feedback Loop Option")
    parser.add_argument("--feedback-loop", action="store_true", help="Run the feedback loop instead of the main pipeline")
    parser.add_argument("--job-id", help="Job ID for feedback loop")
    parser.add_argument("--feedback", help="Feedback text for feedback loop")
    parser.add_argument("--auto-update", action="store_true", help="Auto-update prompt in feedback loop")
    parser.add_argument("--save", help="Save feedback loop results to file")
    parser.add_argument("--cover-letter", action="store_true", help="Run the cover letter generator (CLI)")
    parser.add_argument("--cover-letter-args", nargs=argparse.REMAINDER, help="Arguments to pass to the cover letter generator CLI")
    args, unknown = parser.parse_known_args()
    if args.feedback_loop:
        if not args.job_id or not args.feedback:
            print("--job-id and --feedback are required for --feedback-loop mode.")
            sys.exit(1)
        run_feedback_loop(args.job_id, args.feedback, auto_update=args.auto_update, save_path=args.save)
    elif args.cover_letter:
        # Import and run the cover letter generator CLI
        from run_pipeline.generate_cover_letter import main as cover_letter_main
        import sys
        # If extra args are provided, patch sys.argv
        if args.cover_letter_args:
            sys.argv = ["generate_cover_letter.py"] + args.cover_letter_args
        else:
            sys.argv = ["generate_cover_letter.py"]
        sys.exit(cover_letter_main())
    else:
        sys.exit(run_full_pipeline())
