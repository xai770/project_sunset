#!/usr/bin/env python3
"""
Test script to run the pipeline with only phi3 generation for specific jobs.
"""
import sys
import os
import argparse
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent

# Add the project root to path if needed
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.core.pipeline_orchestrator import run_pipeline
from run_pipeline.core.cli_args import parse_args

def main():
    # Define our own argument parser to handle positional arguments better
    parser = argparse.ArgumentParser(description="Run phi3 generation for specific jobs")
    parser.add_argument("--job-id", default="61691", 
                       help="Job ID to process (defaults to 61691 if not provided)")
    parser.add_argument("--force", action="store_true", 
                       help="Force reprocessing even if phi3 fields already exist")
    parser.add_argument("--dump-input", action="store_true", help="Dump the LLM input to a text file and exit")
    
    # Parse our arguments
    our_args = parser.parse_args()
    job_id = our_args.job_id
    dump_input = our_args.dump_input
    
    print(f"Running pipeline with only-regenerate-phi3 on job ID {job_id}")
    
    # Remove --dump-input from sys.argv before calling parse_args()
    filtered_argv = [arg for arg in sys.argv if arg != '--dump-input']
    sys.argv = filtered_argv
    # Create a custom Namespace for the pipeline using default args
    args = parse_args()  # Start with default args
    
    # Modify args to run phi3 regeneration only
    args.job_ids = job_id
    args.only_regenerate_phi3 = True
    args.skip_fetch = True  # Skip fetching as we only want to regenerate phi3 fields
    args.skip_status_check = True  # Skip status check
    args.skip_skills = True  # Skip skills processing
    args.force_reprocess = True  # Force reprocess phi3 fields

    # If --dump-input is set, load the job file and dump the LLM input
    if dump_input:
        from run_pipeline.config.paths import JOB_DATA_DIR
        from run_pipeline.core.cv_embeddings import get_cv_json_text
        import json
        import os
        job_path = os.path.join(JOB_DATA_DIR, f"job{job_id}.json")
        with open(job_path, "r", encoding="utf-8") as jf:
            job_data = json.load(jf)
        web_details = job_data.get("web_details")
        if not web_details:
            print(f"No web_details found in {job_path}")
            return 1
        job_title = web_details.get("position_title", "")
        concise_desc = web_details.get("concise_description", "")
        job_description = f"Position Title: {job_title}\n\n{concise_desc}"
        cv_text = get_cv_json_text(force_regenerate=False)
        from run_pipeline.core.phi3_match_and_cover import PROMPT_TEMPLATE
        prompt = PROMPT_TEMPLATE.format(cv=cv_text, job=job_description)
        dump_path = os.path.join(os.path.dirname(job_path), f"job{job_id}_llm_input.txt")
        with open(dump_path, "w", encoding="utf-8") as outf:
            # First include the full prompt (which already contains the CV and job details)
            # Then add the job information after the separator for easier reference
            outf.write(f"PROMPT SENT TO LLM:\n\n{prompt}\n\n---\n\njob_title: {job_title}\n\nconcise_desc:\n{concise_desc}\n\njob_description:\n{job_description}\n")
        print(f"LLM input dumped to {dump_path}")
        return 0

    # Run the pipeline
    success = run_pipeline(args)
    
    # Print completion message
    if success:
        print(f"\nPhi3 regeneration completed successfully for job ID {job_id}")
    else:
        print(f"\nPhi3 regeneration encountered errors for job ID {job_id}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
