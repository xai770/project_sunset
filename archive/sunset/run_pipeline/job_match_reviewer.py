#!/usr/bin/env python3
"""
Job Match Reviewer

This script analyzes job matches and generates a CSV with job titles and match percentages.
It also can enrich job files with SDR skills if they are missing.
"""

import os
import sys
import json
import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("job_match_reviewer")

# Paths
JOB_DATA_DIR = Path(project_root) / "data" / "postings"
OUTPUT_DIR = Path(project_root) / "docs" / "skill_matching"

def get_job_files() -> List[Path]:
    """Get all job files"""
    return sorted(JOB_DATA_DIR.glob("job*.json"))

def load_job_data(job_path: Path) -> Optional[Dict[str, Any]]:
    """Load job data from file"""
    try:
        with open(job_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load job file {job_path}: {e}")
        return None

def get_job_title_and_match(job_data: Dict[str, Any]) -> Tuple[str, float]:
    """Get job title and match percentage"""
    job_title = job_data.get("web_details", {}).get("position_title", "Unknown Title")
    match_percentage = job_data.get("skill_matches", {}).get("match_percentage", 0.0)
    return job_title, match_percentage * 100  # Convert to percentage

def generate_match_csv(output_path: Path) -> None:
    """Generate CSV with job titles and match percentages"""
    job_files = get_job_files()
    job_matches = []
    
    logger.info(f"Processing {len(job_files)} job files...")
    
    for job_path in job_files:
        job_data = load_job_data(job_path)
        if not job_data:
            continue
            
        job_id = job_path.stem.replace("job", "")
        job_title, match_percentage = get_job_title_and_match(job_data)
        
        job_matches.append({
            "job_id": job_id,
            "job_title": job_title,
            "match_percentage": f"{match_percentage:.1f}%"
        })
    
    # Sort by match percentage (descending)
    job_matches.sort(key=lambda x: float(x["match_percentage"].replace("%", "")), reverse=True)
    
    # Write to CSV
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["job_id", "job_title", "match_percentage"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for job_match in job_matches:
            writer.writerow(job_match)
    
    logger.info(f"CSV file generated at {output_path}")

def main():
    """Main function"""
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"job_matches_{timestamp}.csv"
    generate_match_csv(output_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
