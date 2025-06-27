#!/usr/bin/env python3
"""
Test script to verify that our fixes to the LLM job evaluation bug work correctly.
This script will evaluate the problematic job IDs mentioned in the bug report
and print out the results.
"""
import sys
import json
import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.job_matcher.job_processor import process_job, update_job_json
from run_pipeline.export_job_matches import export_job_matches

# Test problematic job IDs
TEST_JOB_IDS = [61907, 63587, 63625]

def run_tests():
    """Run tests on the problematic job IDs"""
    print(f"Testing fixes on {len(TEST_JOB_IDS)} problematic job IDs...")
    
    # Load CV text using the cv_loader module
    from run_pipeline.job_matcher.cv_loader import load_cv_text
    cv_text = load_cv_text()
    
    results = {}
    
    # Process each job
    for job_id in TEST_JOB_IDS:
        print(f"\n\nProcessing job {job_id}...")
        job_result = process_job(str(job_id), cv_text, num_runs=3, dump_input=True)
        
        # Store results
        results[job_id] = {
            "cv_to_role_match": job_result.get("cv_to_role_match", "Unknown"),
            "domain_knowledge_assessment": job_result.get("domain_knowledge_assessment", "")
        }
        
        # Add narrative or rationale
        if job_result.get("Application narrative"):
            results[job_id]["narrative"] = job_result.get("Application narrative")
        elif job_result.get("No-go rationale"):
            results[job_id]["rationale"] = job_result.get("No-go rationale")
        
        # Update job JSON
        update_job_json(str(job_id), job_result)
    
    # Print summary
    print("\n\n=== TEST RESULTS SUMMARY ===")
    for job_id, result in results.items():
        print(f"Job {job_id}: {result.get('cv_to_role_match')} match")
    
    # Export results to Excel
    print("\nExporting results to Excel...")
    output_path = export_job_matches(
        output_format='excel',
        job_ids=[str(jid) for jid in TEST_JOB_IDS],
        feedback_system=True,
        reviewer_name="test_fix"
    )
    print(f"Exported to: {output_path}")

if __name__ == "__main__":
    run_tests()
