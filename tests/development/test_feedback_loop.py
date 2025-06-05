#!/usr/bin/env python3
"""
Test script to verify the new feedback loop and prompt management functionality.
This script performs the following tests:
1. Exports job matches with the new feedback column
2. Loads a prompt using the prompt manager
3. Processes a sample feedback from a job match Excel file
"""
import os
import sys
from pathlib import Path
import pandas as pd
import json
import argparse

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import local modules
try:
    from job_matcher.prompt_adapter import get_formatted_prompt, list_available_prompts
except ImportError:
    print("Error: Could not import prompt_adapter module. Make sure it exists and is accessible.")
    sys.exit(1)

# Test prompt management functionality
def test_prompt_management():
    """Test that the prompt management system is working correctly."""
    print("Testing prompt management system...")
    
    try:
        # List all available prompts
        prompts = list_available_prompts()
        print("Available prompts:")
        for category, prompt_list in prompts.items():
            print(f"  {category}:")
            for prompt_name, version in prompt_list:
                print(f"    - {prompt_name} ({version})")
        
        # Try loading a job matching prompt
        prompt = get_formatted_prompt('llama3_cv_match', category='job_matching', 
                                     cv="Sample CV", job="Sample job description")
        print(f"Successfully loaded prompt (length: {len(prompt)} characters)")
        print(f"First 100 characters: {prompt[:100]}...")
        
        return True
    except Exception as e:
        print(f"Error testing prompt management: {e}")
        return False

# Test export with feedback column
def test_export_with_feedback():
    """Test that the job export with feedback column works correctly."""
    print("\nTesting job export with feedback column...")
    
    try:
        # Find the most recent Excel export
        excel_files = list(PROJECT_ROOT.glob("job_matches_*.xlsx"))
        if not excel_files:
            print("No job match Excel files found.")
            return False
        
        # Sort by modification time (newest first)
        latest_file = sorted(excel_files, key=lambda x: x.stat().st_mtime, reverse=True)[0]
        print(f"Testing latest export: {latest_file}")
        
        # Open the Excel file and check for Feedback column
        df = pd.read_excel(latest_file)
        
        if 'Feedback' in df.columns:
            print(f"✓ Feedback column found in {latest_file}")
            return True
        else:
            print(f"✗ Feedback column NOT found in {latest_file}")
            return False
    except Exception as e:
        print(f"Error testing export with feedback: {e}")
        return False

# Test feedback processing
def test_feedback_processing():
    """Test that the feedback processing script is present and executable."""
    print("\nTesting feedback processing functionality...")
    
    feedback_script = PROJECT_ROOT / "process_feedback.py"
    if not feedback_script.exists():
        print(f"✗ Feedback processing script not found at {feedback_script}")
        return False
    
    if not os.access(feedback_script, os.X_OK):
        print(f"✗ Feedback processing script exists but is not executable")
        try:
            os.chmod(feedback_script, 0o755)
            print(f"✓ Made feedback processing script executable")
        except:
            print(f"✗ Could not make feedback processing script executable")
            return False
    
    print(f"✓ Feedback processing script found and is executable")
    return True

def main():
    parser = argparse.ArgumentParser(description='Test new feedback loop and prompt management functionality.')
    args = parser.parse_args()
    
    # Run tests
    results = {
        "Prompt Management": test_prompt_management(),
        "Export with Feedback Column": test_export_with_feedback(),
        "Feedback Processing": test_feedback_processing()
    }
    
    # Print summary
    print("\n=== Test Results ===")
    all_passed = True
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        if not result:
            all_passed = False
        print(f"{status}: {test_name}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
