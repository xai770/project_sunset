#!/usr/bin/env python3
"""
Test script for the migrated feedback system.

This script tests the migrated feedback system with a real job ID.
"""
import sys
import argparse
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.job_matcher.job_processor import process_job, process_feedback
from run_pipeline.job_matcher.cv_utils import get_cv_markdown_text

def test_feedback(job_id, feedback_text):
    """Test the feedback system."""
    print(f"\nTesting feedback system for job ID: {job_id}")
    print("=" * 80)
    print(f"Feedback: {feedback_text}")
    
    # Process the feedback
    result = process_feedback(job_id, feedback_text, auto_update=False)
    
    # Print the results
    print("\nAnalysis Results:")
    if 'analysis' in result and isinstance(result['analysis'], dict):
        analysis = result['analysis']
        print(f"Analysis: {analysis.get('analysis', '')[:200]}...")
        print(f"Recommendations: {analysis.get('recommendations', '')[:200]}...")
        print(f"Prompt changes: {analysis.get('prompt_changes', '')[:200]}...")
    else:
        print(f"Raw result: {result}")
    
    return result

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test migrated feedback system")
    parser.add_argument("job_id", help="Job ID to test")
    parser.add_argument("feedback", help="Feedback text")
    args = parser.parse_args()
    
    result = test_feedback(args.job_id, args.feedback)
    
    if result and 'error' not in result:
        print("\n✅ Feedback test successful!")
    else:
        print(f"\n❌ Feedback test failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
