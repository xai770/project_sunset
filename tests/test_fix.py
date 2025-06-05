#!/usr/bin/env python3
"""
Test script for skill_decomposer.matching.find_skill_matches
"""
from scripts.utils.skill_decomposer.matching import find_skill_matches
import os
import json

def get_job_with_requirements():
    """Find a job file that contains requirements data."""
    job_dir = "/home/xai/Documents/sunset/data/postings"
    
    for filename in os.listdir(job_dir):
        if filename.startswith("job") and filename.endswith(".json"):
            job_id = filename.replace("job", "").replace(".json", "")
            job_path = os.path.join(job_dir, filename)
            
            # Check if this job has requirements data
            try:
                with open(job_path, 'r') as f:
                    job_data = json.load(f)
                
                # Look for requirements in various possible locations in the job data
                has_requirements = False
                if "sections" in job_data:
                    for section in job_data["sections"]:
                        if section.get("type") == "requirements" or "requirement" in section.get("title", "").lower():
                            has_requirements = True
                            break
                
                if has_requirements:
                    print(f"Found job {job_id} with requirements")
                    return job_id
            except Exception as e:
                print(f"Error checking job {job_id}: {e}")
                continue
    
    return "62118"  # Default fallback job ID

def main():
    print("Testing find_skill_matches with our fix...")
    
    # Try to find a job with requirements
    job_id = get_job_with_requirements()
    
    print(f"Running find_skill_matches for job {job_id}...")
    result = find_skill_matches(job_id, analyze_cv=True, use_semantic=True)
    
    if result:
        print(f"Success! Match score: {result.get('overall_match')}")
        return 0
    else:
        print("Error: find_skill_matches returned None")
        return 1

if __name__ == "__main__":
    main()
