#!/usr/bin/env python3
"""
JMFS Pipeline CLI Argument Update Script

This script adds the force-good-match and force-good-matches arguments to the pipeline CLI.
"""

import os
import sys
import re
from pathlib import Path

def add_force_good_match_arguments():
    """Add force-good-match CLI arguments to the pipeline CLI parser"""
    cli_args_file = os.path.join("run_pipeline", "core", "cli_args.py")
    
    if not os.path.exists(cli_args_file):
        print(f"Error: Could not find {cli_args_file}")
        return False
    
    with open(cli_args_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if arguments already exist
    if "--force-good-match" in content:
        print("force-good-match arguments already added.")
        return True
    
    # Find the right spot to add the arguments, after the enable-feedback-loop argument
    pattern = r'(--enable-feedback-loop"\s*,\s*action\s*=\s*"store_true".*?\))'
    
    replacement = r'\1\n\n    parser.add_argument(\n        "--force-good-match", \n        type=str,\n        help="Force a specific job ID to have a \'Good\' match for testing cover letter generation"\n    )\n    \n    parser.add_argument(\n        "--force-good-matches", \n        type=str,\n        help="Force multiple job IDs to have \'Good\' matches (comma-separated)"\n    )'
    
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if updated_content == content:
        print("Could not find the right spot to insert arguments.")
        return False
    
    with open(cli_args_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Added force-good-match arguments to CLI parser.")
    return True

def add_process_force_good_matches_function():
    """Add process_force_good_matches function to pipeline orchestrator"""
    orchestrator_file = os.path.join("run_pipeline", "core", "pipeline_orchestrator.py")
    
    if not os.path.exists(orchestrator_file):
        print(f"Error: Could not find {orchestrator_file}")
        return False
    
    with open(orchestrator_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if function already exists
    if "def process_force_good_matches" in content:
        print("process_force_good_matches function already added.")
        return True
    
    # Find the run_excel_export_step function
    pattern = r'(def run_excel_export_step\(args, log_dir\):)'
    
    replacement = r'''def process_force_good_matches(args):
    """
    Process forced good matches for testing cover letter generation
    """
    try:
        from run_pipeline.core.test_utils import force_good_match_for_testing
        
        # Handle single job ID
        if getattr(args, 'force_good_match', None):
            job_id = args.force_good_match
            logger.info(f"Forcing job {job_id} to have a 'Good' match for testing...")
            try:
                job_data = force_good_match_for_testing(job_id)
                if job_data:
                    logger.info(f"Successfully forced job {job_id} to 'Good' match with application narrative")
                else:
                    logger.error(f"Failed to force job {job_id} to 'Good' match")
            except Exception as e:
                logger.error(f"Error forcing job {job_id} to 'Good' match: {e}")
        
        # Handle comma-separated list of job IDs
        if getattr(args, 'force_good_matches', None):
            job_ids = args.force_good_matches.split(',')
            logger.info(f"Forcing jobs {job_ids} to have 'Good' matches for testing...")
            for job_id in job_ids:
                job_id = job_id.strip()
                try:
                    job_data = force_good_match_for_testing(job_id)
                    if job_data:
                        logger.info(f"Successfully forced job {job_id} to 'Good' match with application narrative")
                    else:
                        logger.error(f"Failed to force job {job_id} to 'Good' match")
                except Exception as e:
                    logger.error(f"Error forcing job {job_id} to 'Good' match: {e}")
    except ImportError:
        logger.warning("Could not import force_good_match_for_testing function - skipping force good matches")
        return
    except Exception as e:
        logger.error(f"Error processing force good matches: {e}")
        return

\g<1>'''
    
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if updated_content == content:
        print("Could not find the right spot to insert function.")
        return False
    
    with open(orchestrator_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Added process_force_good_matches function to pipeline orchestrator.")
    return True

def add_call_to_process_force_good_matches():
    """Add call to process_force_good_matches in the main pipeline function"""
    orchestrator_file = os.path.join("run_pipeline", "core", "pipeline_orchestrator.py")
    
    if not os.path.exists(orchestrator_file):
        print(f"Error: Could not find {orchestrator_file}")
        return False
    
    with open(orchestrator_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if call already exists
    if "process_force_good_matches(args)" in content:
        print("Call to process_force_good_matches already added.")
        return True
    
    # Find the ensure_directories() call
    pattern = r'(# Ensure required directories exist\s*ensure_directories\(\))'
    
    replacement = r'\1\n\n    # Process forced good matches for testing\n    if getattr(args, "force_good_match", None) or getattr(args, "force_good_matches", None):\n        process_force_good_matches(args)'
    
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if updated_content == content:
        print("Could not find the right spot to insert call.")
        return False
    
    with open(orchestrator_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Added call to process_force_good_matches in pipeline.")
    return True

if __name__ == "__main__":
    print("Updating JMFS Pipeline CLI arguments...")
    success1 = add_force_good_match_arguments()
    success2 = add_process_force_good_matches_function()
    success3 = add_call_to_process_force_good_matches()
    
    if success1 and success2 and success3:
        print("\nSuccessfully updated pipeline to support force-good-match!")
        print("\nYou can now run tests with:")
        print("python run_pipeline/core/pipeline_main.py --max-jobs 5 --enable-feedback-loop --force-good-match 12345")
        print("python test_cover_letter_generation.py --job-id 12345")
        sys.exit(0)
    else:
        print("\nFailed to update all components.")
        print("Please see the detailed output above.")
        sys.exit(1)
