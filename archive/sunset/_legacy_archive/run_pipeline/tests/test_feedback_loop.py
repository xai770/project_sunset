#!/usr/bin/env python3
"""
Test script for the migrated job matcher and feedback system.

This script tests the complete feedback loop in the migrated system:
1. Run a job match with the migrated job matcher
2. Process feedback with the migrated feedback system
3. Run an updated job match to see the effects of the feedback

Usage examples:
  ./test_feedback_loop.py 61691 "The match level should be Good instead of Moderate because the CV shows experience in all required domain-specific areas"
  ./test_feedback_loop.py 61692 "The match should be Low due to lack of industry experience" --save
  ./test_feedback_loop.py 61693 "Please improve the domain analysis" --auto-update --output custom_results.json

Options:
  --auto-update: Automatically update prompts based on feedback analysis
  --save: Save results to an automatically named file (includes timestamp)
  --output: Save results to a specific file path
"""
import sys
import argparse
import json
from pathlib import Path
import time

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.job_matcher.job_processor import process_job, process_feedback
from run_pipeline.job_matcher.cv_utils import get_cv_markdown_text
from run_pipeline.job_matcher.feedback_handler import save_feedback, analyze_feedback

def test_feedback_loop(job_id, feedback_text, auto_update=False):
    """Test the complete feedback loop."""
    print(f"\nTesting feedback loop for job ID: {job_id}")
    print("=" * 80)
    
    # Step 1: Run a job match
    print("\nStep 1: Running job match...")
    cv_text = get_cv_markdown_text()
    job_result = process_job(job_id, cv_text=cv_text, num_runs=2)
    
    if "error" in job_result:
        print(f"Error running job match: {job_result.get('error')}")
        return {"error": job_result.get("error")}
    
    # Extract match details
    match_level = job_result.get("cv_to_role_match", "Unknown")
    domain_assessment = job_result.get("domain_knowledge_assessment", "")
    
    print(f"Job match completed: {match_level} match")
    
    # Step 2: Process feedback
    print(f"\nStep 2: Processing feedback: '{feedback_text}'")
    feedback_result = process_feedback(job_id, feedback_text, auto_update=auto_update)
    
    if "error" in feedback_result:
        print(f"Error processing feedback: {feedback_result.get('error')}")
        return {"error": feedback_result.get("error")}
    
    print("Feedback processed successfully")
    
    # Step 3: Run a new job match
    print("\nStep 3: Running job match after feedback...")
    # Sleep briefly to ensure any changes take effect
    time.sleep(1)
    
    new_job_result = process_job(job_id, cv_text=cv_text, num_runs=2)
    
    if "error" in new_job_result:
        print(f"Error running second job match: {new_job_result.get('error')}")
        return {"error": new_job_result.get("error")}
    
    new_match_level = new_job_result.get("cv_to_role_match", "Unknown")
    new_domain_assessment = new_job_result.get("domain_knowledge_assessment", "")
    
    print(f"Updated job match completed: {new_match_level} match")
    
    # Compile results
    results = {
        "job_id": job_id,
        "feedback": feedback_text,
        "original_match": {
            "match_level": match_level,
            "domain_assessment": domain_assessment[:150] + "..." if len(domain_assessment) > 150 else domain_assessment
        },
        "feedback_analysis": feedback_result.get("analysis", {}),
        "updated_match": {
            "match_level": new_match_level,
            "domain_assessment": new_domain_assessment[:150] + "..." if len(new_domain_assessment) > 150 else new_domain_assessment
        },
        "changed": match_level != new_match_level
    }
    
    # Print summary
    print("\nFeedback Loop Summary:")
    print(f"Original match level: {match_level}")
    print(f"Updated match level: {new_match_level}")
    print(f"Match level changed: {match_level != new_match_level}")
    
    return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test migrated feedback loop")
    parser.add_argument("job_id", help="Job ID to test")
    parser.add_argument("feedback", help="Feedback text")
    parser.add_argument("--auto-update", action="store_true", help="Automatically update prompts based on feedback")
    parser.add_argument("--save", action="store_true", help="Save results to file")
    parser.add_argument("--output", help="Specific output file path (default: auto-generated)")
    args = parser.parse_args()
    
    results = test_feedback_loop(args.job_id, args.feedback, args.auto_update)
    
    if "error" not in results:
        print("\n✅ Feedback loop test successful!")
        
        if args.save or args.output:
            # Generate a filename with timestamp if not specified
            if args.output:
                output_file = args.output
            else:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_file = f"feedback_test_job{args.job_id}_{timestamp}.json"
                
            # Ensure the directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(exist_ok=True, parents=True)
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {output_file}")
    else:
        print(f"\n❌ Feedback loop test failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
