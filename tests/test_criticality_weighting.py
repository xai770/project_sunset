#!/usr/bin/env python3
"""
Test script to compare regular matching vs. criticality-weighted matching.
This script compares how job requirements are scored with and without
criticality weighting to demonstrate the impact on overall match scores.
"""

import os
import sys
import json
from pprint import pprint
from tabulate import tabulate

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import relevant modules
from scripts.utils.skill_decomposer.matching import find_skill_matches
from scripts.utils.skill_decomposer.criticality import evaluate_requirement_criticality
from scripts.utils.skill_decomposer.persistence import load_job_data

def compare_match_scoring(job_id):
    """
    Compare regular vs. criticality-weighted scoring for a job.
    
    Args:
        job_id: ID of the job to compare
    """
    print(f"\nComparing match scoring methods for job {job_id}...")
    
    # Get job details
    job_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'data', 'postings', f'job{job_id}.json'
    )
    
    job_title = "Unknown Job"
    job_description = "No description available"
    
    try:
        with open(job_file_path, 'r') as f:
            job_data = json.load(f)
            job_title = job_data.get('title', 'Unknown Job')
            
            # Try to get a useful description
            if 'sections' in job_data:
                for section in job_data['sections']:
                    if section.get('type') in ['job_description', 'description', 'about_role', 'responsibilities']:
                        job_description = section.get('content', '')[:300]  # Truncate for API context limits
                        break
    except Exception as e:
        print(f"Error loading job details: {e}")
    
    print(f"Job Title: {job_title}")
    
    # Run matching with regular scoring
    print("Running match with regular scoring...")
    matches_regular = find_skill_matches(
        job_id=job_id,
        analyze_cv=True,
        use_semantic=True,
        use_domain_aware=True,
        domain_overlap_weight=0.5,
        use_criticality_weighting=False  # Disable criticality weighting
    )
    
    # Run matching with criticality-weighted scoring
    print("Running match with criticality-weighted scoring...")
    matches_weighted = find_skill_matches(
        job_id=job_id,
        analyze_cv=True,
        use_semantic=True,
        use_domain_aware=True,
        domain_overlap_weight=0.5,
        use_criticality_weighting=True  # Enable criticality weighting
    )
    
    if not matches_regular or not matches_weighted:
        print("Error: Failed to generate one or both match results")
        return
    
    # Report basic match scores
    print("\n--- Match Scores ---")
    print(f"Regular Match Score: {matches_regular['overall_match']:.2f}")
    print(f"Regular Enhanced Score: {matches_regular['enhanced_match']:.2f}")
    print(f"Criticality-Weighted Score: {matches_weighted['enhanced_match']:.2f}")
    
    # Calculate and show the impact of the different scoring methods
    score_difference = matches_weighted['enhanced_match'] - matches_regular['enhanced_match']
    print(f"\nScore difference: {score_difference:.2f} ({score_difference*100:.1f}%)")
    
    # Show criticality analysis results
    if "criticality_analysis" in matches_weighted:
        print("\n--- Requirement Criticality Breakdown ---")
        crit_analysis = matches_weighted["criticality_analysis"]
        
        print(f"Critical Requirements: {crit_analysis['critical_requirements_count']}")
        print(f"Important Requirements: {crit_analysis['important_requirements_count']}")
        print(f"Nice-to-Have Requirements: {crit_analysis['nice_to_have_requirements_count']}")
        print(f"Missing Critical Requirements: {crit_analysis['missing_critical_requirements_count']}")
        print(f"Has Critical Failures: {'Yes' if crit_analysis['has_critical_failures'] else 'No'}")
    
    # Get requirements with criticality assessment
    job_data = load_job_data(job_id)
    if job_data and "requirements" in job_data and "complex_requirements" in job_data["requirements"]:
        requirements = []
        
        for req in job_data["requirements"]["complex_requirements"]:
            req_name = req.get('name', '')
            if not req_name:
                continue
                
            # Get match strength (if any)
            match_strength = 0.0
            matched_with = ""
            
            for match_data in matches_weighted["requirements_match_data"]:
                if match_data["requirement"] == req_name and match_data["matches"]:
                    best_match = max(match_data["matches"], key=lambda m: m.get("match_strength", 0))
                    match_strength = best_match.get("match_strength", 0)
                    matched_with = best_match.get("your_skill", "")
                    break
            
            # Evaluate criticality
            criticality = evaluate_requirement_criticality(job_title, job_description, req_name)
            
            # Store requirement data
            requirements.append({
                "name": req_name,
                "criticality": criticality["classification"],
                "weight": criticality["weight"],
                "score": criticality["criticality_score"],
                "match_strength": match_strength,
                "matched_with": matched_with
            })
        
        # Sort by criticality score (highest to lowest)
        requirements.sort(key=lambda x: x["score"], reverse=True)
        
        # Display requirement table
        print("\n--- Requirements by Criticality ---")
        table_data = [[
            r["name"], 
            r["criticality"], 
            r["weight"], 
            f"{r['score']:.2f}", 
            f"{r['match_strength']:.2f}" if r["match_strength"] > 0 else "No match", 
            r["matched_with"] if r["matched_with"] else "-"
        ] for r in requirements]
        
        headers = ["Requirement", "Classification", "Weight", "Crit. Score", "Match Strength", "Matched With"]
        print(tabulate(table_data, headers=headers, tablefmt="pretty"))
        
        # Calculate weighted score manually to show the math
        total_weighted_points = 0
        total_weighted_possible = 0
        
        for r in requirements:
            total_weighted_points += r["weight"] * r["match_strength"]
            total_weighted_possible += r["weight"]
        
        weighted_score = total_weighted_points / total_weighted_possible if total_weighted_possible > 0 else 0
        
        # Apply penalty for missing critical requirements
        has_missing_critical = any(r["criticality"] == "CRITICAL" and r["match_strength"] == 0 for r in requirements)
        final_score = min(weighted_score, 0.5) if has_missing_critical else weighted_score
        
        print("\n--- Weighted Score Calculation ---")
        print(f"Total Weighted Points: {total_weighted_points:.2f}")
        print(f"Total Weighted Possible: {total_weighted_possible:.2f}")
        print(f"Weighted Score: {weighted_score:.2f}")
        print(f"Missing Critical Requirements: {'Yes' if has_missing_critical else 'No'}")
        print(f"Final Score After Critical Penalties: {final_score:.2f}")
        

if __name__ == "__main__":
    # Set environment variables for LLM API
    os.environ["LLM_API_ENABLED"] = "true"
    os.environ["LLM_API_URL"] = "http://localhost:11434/api/generate"
    os.environ["LLM_API_MODEL"] = "llama3"
    
    print("Test script for criticality-weighted job matching")
    print("================================================")
    
    # Process command line arguments
    if len(sys.argv) > 1:
        job_id = sys.argv[1]
        compare_match_scoring(job_id)
    else:
        print("Comparing match scoring for tax job (61964) and other jobs...")
        # Test with tax role that requires specialized knowledge
        compare_match_scoring("61964")  # Tax role
        # Test with another job for comparison
        compare_match_scoring("63141")  # Another job (likely a non-tax role)