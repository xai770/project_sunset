#!/usr/bin/env python3
"""
Test script for enhanced job matching algorithm.
This script recalculates match scores using the new advanced matching algorithm
and compares them with the original scores.
"""

import json
import os
import sys
from pathlib import Path

# Import our matching functions
from scripts.utils.skill_decomposer.matching import calculate_advanced_match_score

def test_enhanced_matching(job_id):
    """Test the enhanced matching algorithm on a specific job."""
    # Define the job file path
    job_file = Path(f"/home/xai/Documents/sunset/data/postings/job{job_id}.json")
    
    if not job_file.exists():
        print(f"Error: Job file not found: {job_file}")
        return
    
    # Load the job data
    with open(job_file, 'r') as f:
        job_data = json.load(f)
    
    # Check if match data exists
    if "matches" not in job_data:
        print(f"Error: No match data found in {job_file}")
        return
    
    matches = job_data["matches"]
    requirement_matches = matches.get("requirement_matches", [])
    job_title = job_data.get("title", f"Job {job_id}")
    
    # Calculate the advanced match score
    advanced_score = calculate_advanced_match_score(requirement_matches, job_title)
    original_score = matches.get("overall_match", 0)
    
    # Print the results
    print(f"\nJob ID: {job_id}")
    print(f"Job Title: {job_title}")
    print(f"Original Match Score: {original_score:.2f} ({original_score*100:.0f}%)")
    print(f"Advanced Match Score: {advanced_score:.2f} ({advanced_score*100:.0f}%)")
    
    # Analyze the difference
    diff = advanced_score - original_score
    if diff > 0.05:
        print(f"Significant INCREASE: +{diff:.2f} (+{diff*100:.0f}%)")
        print("The hiring manager would likely rate you HIGHER than the original algorithm suggests.")
    elif diff < -0.05:
        print(f"Significant DECREASE: {diff:.2f} ({diff*100:.0f}%)")
        print("The hiring manager would likely rate you LOWER than the original algorithm suggests.")
    else:
        print(f"Similar score: {diff:.2f} ({diff*100:.0f}%)")
        print("The hiring manager would likely rate you SIMILAR to the original algorithm.")
    
    # Explain why the score changed
    print("\nKey factors affecting the hiring manager's evaluation:")
    
    # Check if this is a technical, management, or analyst role
    job_title_lower = job_title.lower()
    role_type = "general"
    if any(term in job_title_lower for term in ["engineer", "developer", "architect", "devops", "technical"]):
        role_type = "technical"
    elif any(term in job_title_lower for term in ["manager", "lead", "director", "head", "chief"]):
        role_type = "management"
    elif "analyst" in job_title_lower:
        role_type = "analyst"
    
    print(f"- Role type: {role_type.upper()}")
    
    # Find critical requirements (those mentioned in job title)
    critical_reqs = []
    for req in requirement_matches:
        req_name = req.get("requirement", "").lower()
        if req_name in job_title_lower:
            critical_reqs.append(req.get("requirement"))
    
    if critical_reqs:
        print("- Critical requirements (mentioned in job title):")
        for req in critical_reqs:
            print(f"  * {req}")
    
    # Check for moderate matches that would get penalties
    moderate_matches = []
    for req in requirement_matches:
        if not req.get("matches"):
            continue
        
        best_match = max(req.get("matches", []), key=lambda x: x.get("match_strength", 0))
        match_strength = best_match.get("match_strength", 0)
        
        if 0.6 <= match_strength < 0.8:
            moderate_matches.append((req.get("requirement"), match_strength))
    
    if moderate_matches:
        print("- Moderate matches (hiring managers view these more critically):")
        for req, strength in moderate_matches:
            print(f"  * {req}: {strength:.2f} match strength")
    
    return advanced_score, original_score

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_enhanced_matching.py <job_id>")
        sys.exit(1)
    
    job_id = sys.argv[1]
    test_enhanced_matching(job_id)