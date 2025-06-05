#!/usr/bin/env python3
"""
Test script for the feedback system components.

This script performs a series of tests to verify that all components
of the feedback system (collection, processing, and prompt updating)
are working correctly.
"""
import os
import sys
import argparse
import json
import pandas as pd
import time
from pathlib import Path
from datetime import datetime

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_excel_export():
    """
    Test that Excel exports have the feedback column.
    
    Returns:
        bool: True if the test passed, False otherwise
    """
    print("\nTesting Excel export with feedback column...")
    
    # Find the most recent Excel file in the workspace
    excel_files = list(PROJECT_ROOT.glob("job_matches_*.xlsx"))
    if not excel_files:
        print("No Excel export files found. Please run export_job_matches.py first.")
        return False
    
    # Sort by modification time, newest first
    excel_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    latest_excel = excel_files[0]
    
    print(f"Found Excel file: {latest_excel}")
    
    # Check if the file contains a Feedback column
    try:
        df = pd.read_excel(latest_excel)
        if "Feedback" in df.columns:
            print("✅ Excel file has Feedback column")
            return True
        else:
            print("❌ Excel file does not have Feedback column")
            return False
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return False

def test_prompt_management():
    """
    Test that the prompt management system is working correctly.
    
    Returns:
        bool: True if the test passed, False otherwise
    """
    print("\nTesting prompt management system...")
    
    try:
        # Try importing the prompt management modules
        from run_pipeline.utils.prompt_manager import get_formatted_prompt, list_available_prompts
        
        # List available prompts
        prompts = list_available_prompts()
        job_matching_prompts = prompts.get('job_matching', [])
        
        # Check if our prompt is available
        llama3_prompt_available = any(name == 'llama3_cv_match' for name, _ in job_matching_prompts)
        
        if llama3_prompt_available:
            print("✅ llama3_cv_match prompt is available in the prompt manager")
            
            # Try loading the prompt
            prompt = get_formatted_prompt('llama3_cv_match', 
                                         category='job_matching', 
                                         cv="SAMPLE_CV_TEXT", 
                                         job="SAMPLE_JOB_TEXT")
            
            if "SAMPLE_CV_TEXT" in prompt and "SAMPLE_JOB_TEXT" in prompt:
                print("✅ Prompt formatting works correctly")
                return True
            else:
                print("❌ Prompt formatting failed")
                return False
        else:
            print("❌ llama3_cv_match prompt is not available in the prompt manager")
            return False
    except Exception as e:
        print(f"❌ Error testing prompt management: {e}")
        return False

def test_feedback_handler():
    """
    Test that the feedback handler is working correctly.
    
    Returns:
        bool: True if the test passed, False otherwise
    """
    print("\nTesting feedback handler...")
    
    try:
        # Try importing the feedback handler
        from job_matcher.feedback_handler import save_feedback, analyze_feedback
        
        # Test saving feedback
        job_id = "test_feedback_job"
        match_level = "Moderate"
        domain_assessment = "The CV shows some experience in financial services but lacks specific hedge fund knowledge."
        feedback_text = "This should be a Low match because the role requires specific hedge fund experience."
        
        result = save_feedback(job_id, match_level, domain_assessment, feedback_text, feedback_source="test")
        
        if result:
            print("✅ Successfully saved test feedback")
            
            # Test feedback analysis (this may take some time)
            print("Testing feedback analysis...")
            analysis = analyze_feedback(job_id, match_level, domain_assessment, feedback_text)
            
            if analysis and "recommendations" in analysis:
                print("✅ Successfully analyzed test feedback")
                return True
            else:
                print("❌ Feedback analysis failed or did not return recommendations")
                return False
        else:
            print("❌ Failed to save test feedback")
            return False
    except Exception as e:
        print(f"❌ Error testing feedback handler: {e}")
        return False

def test_cli_integration():
    """
    Test that the CLI integration is working correctly.
    
    Returns:
        bool: True if the test passed, False otherwise
    """
    print("\nTesting CLI integration...")
    
    try:
        # Check if the CLI module exists and has the necessary components
        from job_matcher.cli import main, parse_job_ids
        
        # Test job ID parsing
        job_ids = parse_job_ids("61691,61692,61693")
        if job_ids == ["61691", "61692", "61693"]:
            print("✅ Job ID parsing works correctly")
        else:
            print("❌ Job ID parsing failed")
            return False
        
        # Test range parsing
        job_ids = parse_job_ids("61691-61693")
        if job_ids == ["61691", "61692", "61693"]:
            print("✅ Job ID range parsing works correctly")
        else:
            print("❌ Job ID range parsing failed")
            return False
            
        print("✅ CLI integration test passed")
        return True
    except Exception as e:
        print(f"❌ Error testing CLI integration: {e}")
        return False

def run_all_tests():
    """
    Run all feedback system tests.
    
    Returns:
        dict: Summary of test results
    """
    results = {
        "excel_export": test_excel_export(),
        "prompt_management": test_prompt_management(),
        "feedback_handler": test_feedback_handler(),
        "cli_integration": test_cli_integration()
    }
    
    # Print summary
    print(f"\n{'='*80}")
    print("Feedback System Test Summary")
    print(f"{'='*80}")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name.ljust(20)} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
    
    return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test the feedback system components")
    parser.add_argument("--excel-only", action="store_true", help="Only test Excel export")
    parser.add_argument("--prompt-only", action="store_true", help="Only test prompt management")
    parser.add_argument("--feedback-only", action="store_true", help="Only test feedback handler")
    parser.add_argument("--cli-only", action="store_true", help="Only test CLI integration")
    
    args = parser.parse_args()
    
    # If no specific test is requested, run all tests
    if not any([args.excel_only, args.prompt_only, args.feedback_only, args.cli_only]):
        results = run_all_tests()
        return 0 if all(results.values()) else 1
        
    # Run requested tests
    all_passed = True
    
    if args.excel_only:
        all_passed = all_passed and test_excel_export()
    
    if args.prompt_only:
        all_passed = all_passed and test_prompt_management()
    
    if args.feedback_only:
        all_passed = all_passed and test_feedback_handler()
    
    if args.cli_only:
        all_passed = all_passed and test_cli_integration()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
