#!/usr/bin/env python3
"""
Generate CSV of job titles and match percentages
"""

import os
import sys
import csv
import json
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

# Paths
postings_DIR = Path(project_root) / "data" / "postings"
OUTPUT_FILE = Path(project_root) / "docs" / "skill_matching" / "job_matches_summary.csv"

def extract_job_matches():
    """Extract job titles and match percentages from job files"""
    job_files = sorted(postings_DIR.glob("job*.json"))
    job_matches = []
    
    print(f"Processing {len(job_files)} job files...")
    
    for job_path in job_files:
        try:
            with open(job_path, "r", encoding="utf-8") as f:
                job_data = json.load(f)
                
            job_id = job_path.stem.replace("job", "")
            job_title = job_data.get("web_details", {}).get("position_title", f"Job {job_id}")
            
            # Get match percentage
            match_percentage = job_data.get("skill_matches", {}).get("match_percentage", 0.0)
            
            # Convert to percentage display (0.75 -> 75%)
            match_percentage_display = f"{match_percentage * 100:.1f}%"
            
            job_matches.append({
                "job_id": job_id,
                "job_title": job_title,
                "match_percentage": match_percentage,
                "match_percentage_display": match_percentage_display
            })
            
        except Exception as e:
            print(f"Error processing {job_path}: {e}")
    
    # Sort by match percentage (highest first)
    job_matches.sort(key=lambda x: x["match_percentage"], reverse=True)
    
    return job_matches

def save_to_csv(job_matches):
    """Save job matches to CSV file"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["job_id", "job_title", "match_percentage_display"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for job in job_matches:
            writer.writerow({
                "job_id": job["job_id"],
                "job_title": job["job_title"],
                "match_percentage_display": job["match_percentage_display"]
            })
    
    print(f"CSV file generated: {OUTPUT_FILE}")

def main():
    job_matches = extract_job_matches()
    save_to_csv(job_matches)
    
    # Print summary to console
    print("\nTop 10 Job Matches:")
    print("{:<8} {:<50} {:<10}".format("Job ID", "Job Title", "Match %"))
    print("-" * 70)
    
    for job in job_matches[:10]:
        print("{:<8} {:<50} {:<10}".format(
            job["job_id"], 
            job["job_title"][:47] + "..." if len(job["job_title"]) > 50 else job["job_title"], 
            job["match_percentage_display"]
        ))

if __name__ == "__main__":
    main()
