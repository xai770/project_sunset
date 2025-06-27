#!/usr/bin/env python3
"""
Test script for the migrated job matcher.

This script tests the migrated job matcher with a real job ID.
"""
import sys
import argparse
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.job_matcher.job_processor import process_job
from run_pipeline.job_matcher.cv_utils import get_cv_markdown_text

def test_job_match(job_id):
    """Run a job match with the migrated job matcher."""
    print(f"\nTesting job match for job ID: {job_id}")
    print("=" * 80)
    
    # Get the CV text
    cv_text = get_cv_markdown_text()
    
    # Process the job
    result = process_job(job_id, num_runs=1, dump_input=False, cv_text=cv_text)
    
    # Print the results
    print("\nResults:")
    print(f"Match level: {result.get('cv_to_role_match', 'Unknown')}")
    print(f"Domain assessment: {result.get('domain_knowledge_assessment', '')[:150]}...")
    
    if 'Application narrative' in result:
        print(f"Application narrative: {result['Application narrative'][:150]}...")
    elif 'No-go rationale' in result:
        print(f"No-go rationale: {result['No-go rationale'][:150]}...")
    
    return result

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test migrated job matcher")
    parser.add_argument("job_id", help="Job ID to test")
    args = parser.parse_args()
    
    result = test_job_match(args.job_id)
    
    if result and 'error' not in result:
        print("\n✅ Job match test successful!")
    else:
        print(f"\n❌ Job match test failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
