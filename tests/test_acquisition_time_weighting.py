#!/usr/bin/env python3
"""
Test script for acquisition time weighting in job matching

This script demonstrates how the acquisition time weighting affects job matching scores.
It compares the regular matching approach with the acquisition time weighted approach.
"""

import sys
import os
import json
import logging
import prettytable
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import skill decomposer modules
from scripts.utils.skill_decomposer.matching import find_skill_matches
from scripts.utils.skill_decomposer.scorer import calculate_acquisition_time_weighted_match_score
from scripts.utils.skill_decomposer.acquisition_time import evaluate_skill_acquisition_time

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   datefmt='%Y-%m-%d %H:%M:%S')

# Test jobs to analyze
TEST_JOBS = [
    # Tax job: Has domain-specific skills that take long to acquire
    "61964",  # Tax Senior Analyst
    # Procurement job: Mix of management skills with different acquisition times
    "63141",  # Senior Procurement Manager
    # Software job: Technical skills with medium acquisition time
    "61951",  # Cloud Engineer
]

def evaluate_skill_acquisition_times(job_id, job_title):
    """
    Evaluate acquisition times for skills in a job
    """
    try:
        # Load job data
        job_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              'data', 'postings', f'job{job_id}.json')
        
        with open(job_file, 'r') as f:
            job_data = json.load(f)
            
        # Get requirements from the job
        requirements = job_data.get('requirements', [])
        if not requirements:
            print(f"No requirements found for job {job_id}")
            return
            
        # Create a table for acquisition times
        table = prettytable.PrettyTable()
        table.field_names = ["Requirement", "Acquisition Time", "Est. Months", "Match Threshold"]
        table.align = "l"
        
        # Evaluate acquisition time for each requirement
        for req_name in requirements:
            acquisition_data = evaluate_skill_acquisition_time(job_title, req_name)
            table.add_row([
                req_name,
                acquisition_data["acquisition_time"].upper(),
                acquisition_data["months_estimate"],
                f"{acquisition_data['match_threshold']:.2f}"
            ])
        
        print(table)
    except Exception as e:
        print(f"Error evaluating skill acquisition times: {e}")

def run_acquisition_time_test(job_id):
    """
    Run a comparison test between regular matching and acquisition time weighted matching
    """
    try:
        # Get job details
        job_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              'data', 'postings', f'job{job_id}.json')
        
        with open(job_file, 'r') as f:
            job_data = json.load(f)
            
        job_title = job_data.get('title', f"Job {job_id}")
        print(f"Job Title: {job_title}")
        
        # Run match with regular scoring
        print("Running match with regular scoring...")
        regular_match = find_skill_matches(
            job_id=job_id,
            use_criticality_weighting=True,
            use_acquisition_time_weighting=False
        )
        if not regular_match:
            print(f"Error running regular match for job {job_id}")
            return
        
        # Run match with acquisition time weighted scoring
        print("Running match with acquisition time weighted scoring...")
        acquisition_match = find_skill_matches(
            job_id=job_id,
            use_criticality_weighting=True,
            use_acquisition_time_weighting=True
        )
        if not acquisition_match:
            print(f"Error running acquisition time match for job {job_id}")
            return
        
        # Compare scores
        regular_score = regular_match.get("enhanced_match", 0.0)
        acquisition_score = acquisition_match.get("enhanced_match", 0.0)
        score_diff = acquisition_score - regular_score
        percent_diff = score_diff * 100
        
        print("\n--- Match Scores ---")
        print(f"Regular Match Score: {regular_match.get('overall_match', 0.0):.2f}")
        print(f"Regular Enhanced Score: {regular_score:.2f}")
        print(f"Acquisition Time Weighted Score: {acquisition_score:.2f}")
        print(f"\nScore difference: {score_diff:.2f} ({percent_diff:.1f}%)")
        
        # Display acquisition time adjustments
        if "acquisition_time_analysis" in acquisition_match:
            adjustments = acquisition_match["acquisition_time_analysis"].get("acquisition_time_adjustments", [])
            if adjustments:
                print("\n--- Acquisition Time Adjustments ---")
                table = prettytable.PrettyTable()
                table.field_names = ["Requirement", "Original Match", "Adjusted Match", "Acquisition Time", "Months"]
                table.align = "l"
                
                for adj in adjustments:
                    table.add_row([
                        adj["requirement"],
                        f"{adj['original_match']:.2f}",
                        f"{adj['adjusted_match']:.2f}",
                        adj["acquisition_time"].upper(),
                        adj["months_estimate"]
                    ])
                
                print(table)
        
        # Get all requirements with acquisition time info
        print("\n--- Requirements by Acquisition Time ---")
        
        # Load job data again to ensure we have the latest matches
        with open(job_file, 'r') as f:
            job_data = json.load(f)
        
        if "requirements" in job_data and "matches" in job_data:
            requirements = job_data.get('requirements', [])
            matches = job_data.get('matches', {}).get('requirements_match_data', [])
            
            table = prettytable.PrettyTable()
            table.field_names = ["Requirement", "Match", "Acquisition Time", "Months", "Threshold"]
            table.align = "l"
            
            for req in matches:
                # Skip blacklisted requirements
                if req.get("blacklisted", False):
                    continue
                    
                req_name = req["requirement"]
                acquisition_data = evaluate_skill_acquisition_time(job_title, req_name)
                
                # Get best match strength
                match_strength = 0.0
                matched_with = ""
                if req["matches"]:
                    best_match = max(req["matches"], key=lambda m: m.get("match_strength", 0))
                    match_strength = best_match.get("match_strength", 0)
                    matched_with = best_match.get("your_skill", "")
                    
                table.add_row([
                    req_name,
                    f"{match_strength:.2f}",
                    acquisition_data["acquisition_time"].upper(),
                    acquisition_data["months_estimate"],
                    f"{acquisition_data['match_threshold']:.2f}"
                ])
            
            print(table)
            
    except Exception as e:
        print(f"Error running acquisition time test: {e}")

def main():
    """Main test function"""
    print("=" * 50)
    print("Test script for acquisition time-weighted job matching")
    print("=" * 50)
    
    print("\nComparing match scoring for test jobs with different acquisition time profiles...")
    
    for job_id in TEST_JOBS:
        print(f"\n{'-' * 40}")
        print(f"Analyzing job {job_id}...")
        print(f"{'-' * 40}")
        run_acquisition_time_test(job_id)
        
if __name__ == "__main__":
    main()