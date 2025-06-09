#!/usr/bin/env python3
"""
Test script for the updated qualification narrative generator
"""
import os
import json
import logging
from scripts.utils.self_assessment.narrative_generator import NarrativeGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_narrative')

def load_job_data(job_id="61951"):
    """Load a specific job posting data"""
    job_path = f"/home/xai/Documents/sunset/data/postings/job{job_id}.json"
    
    try:
        with open(job_path, 'r') as f:
            return json.load(f)  # type: ignore
    except Exception as e:
        logger.error(f"Failed to load job {job_id}: {e}")
        return None

def test_narrative_generation():
    """Test the updated narrative generator with the Tax Senior Specialist job"""
    job_data = load_job_data("61951")  # Tax Senior Specialist job
    
    if not job_data:
        logger.error("Failed to load job data")
        return
    
    job_title = job_data.get("title", "Tax Senior Specialist")
    
    # Use the match score from the job data
    match_score = job_data.get("matches", {}).get("overall_match", 0.333)
    logger.info(f"Job match score: {match_score:.2%}")
    
    # Get missing skills from the job data
    missing_skills = []
    if "matches" in job_data and "summary" in job_data["matches"]:
        missing_skills = job_data["matches"]["summary"].get("missing_requirements", [])
    
    # Test with no matches (realistic for this job)
    strong_matches = []
    moderate_matches = []
    weak_matches = []
    
    # Check current narrative if available
    if "self_assessment" in job_data and "qualification_narrative" in job_data["self_assessment"]:
        current_narrative = job_data["self_assessment"]["qualification_narrative"]
        logger.info(f"Current narrative: {current_narrative}")
    
    # Generate new narrative with our updated code
    new_narrative = NarrativeGenerator.generate_narrative(
        job_title, match_score, strong_matches, moderate_matches, weak_matches, missing_skills
    )
    
    logger.info(f"New narrative: {new_narrative}")
    
    # Check match level directly
    match_level = NarrativeGenerator._get_match_level(match_score)
    logger.info(f"Match level with score {match_score:.2%}: {match_level}")

if __name__ == "__main__":
    logger.info("Testing updated narrative generator...")
    test_narrative_generation()
    logger.info("Test complete")