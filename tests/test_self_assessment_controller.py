#!/usr/bin/env python3
"""
Test script for the self-assessment controller.
This script tests the functionality of the self-assessment controller by:
1. Using an existing job with match data
2. Generating a self-assessment for that job
3. Verifying the self-assessment was created correctly
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add the parent directory to sys.path to import modules from the main project
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger('test_self_assessment')

# Define paths
SUNSET_ROOT = Path(__file__).parent.parent
postings_DIR = SUNSET_ROOT / "data" / "postings"
ASSESSMENTS_DIR = SUNSET_ROOT / "data" / "assessments"

def test_job_has_matches(job_id):
    """Verify that the job has match data."""
    job_file = postings_DIR / f"job{job_id}.json"
    if not job_file.exists():
        logger.error(f"Job file not found: {job_file}")
        return False
    
    try:
        with open(job_file, 'r') as f:
            job_data = json.load(f)
            
        if "matches" not in job_data:
            logger.error(f"Job {job_id} has no match data")
            return False
            
        if job_data.get("metadata", {}).get("has_matches") != True:
            logger.error(f"Job {job_id} metadata does not indicate it has matches")
            return False
            
        logger.info(f"Job {job_id} has match data")
        return True
    except Exception as e:
        logger.error(f"Error checking job match data: {e}")
        return False

def test_assessment_generation(job_id):
    """Generate a self-assessment for the job and verify it was created correctly."""
    from scripts.utils.self_assessment.generator import SelfAssessmentGenerator
    
    logger.info(f"Testing assessment generation for job {job_id}")
    
    # Create the generator
    generator = SelfAssessmentGenerator(job_id)
    
    # Load data
    if not generator.load_data():
        logger.error(f"Failed to load data for job {job_id}")
        return False
    
    logger.info(f"Successfully loaded data for job {job_id}")
    
    # Generate assessment
    assessment = generator.generate_assessment()
    if not assessment:
        logger.error(f"Failed to generate assessment for job {job_id}")
        return False
    
    logger.info(f"Successfully generated assessment for job {job_id}")
    logger.info(f"Assessment sections: {list(assessment.keys())}")
    logger.info(f"Overall match score: {assessment.get('overall_match_score', 'Not found')}")
    
    # Add to job profile (we only store assessments in the job file, not as separate files)
    if not generator.add_to_job_profile():
        logger.error("Failed to add assessment to job profile")
        return False
    
    logger.info("Successfully added assessment to job profile")
    
    # Verify assessment in job file
    job_file = postings_DIR / f"job{job_id}.json"
    try:
        with open(job_file, 'r') as f:
            job_data = json.load(f)
            
        if "self_assessment" not in job_data:
            logger.error("Self-assessment not added to job data")
            return False
            
        if job_data.get("metadata", {}).get("has_self_assessment") != True:
            logger.warning("Job metadata does not indicate it has a self-assessment")
        
        logger.info("Self-assessment found in job data")
        return True
    except Exception as e:
        logger.error(f"Error verifying job assessment: {e}")
        return False

def main():
    """Main test function."""
    # Check if job ID was provided
    if len(sys.argv) > 1:
        job_id = sys.argv[1]
    else:
        # Use the job ID we just tested with matching
        job_id = "62177"
    
    logger.info(f"Testing self-assessment for job {job_id}")
    
    # Step 1: Verify job has match data
    if not test_job_has_matches(job_id):
        logger.error("Job does not have match data, cannot proceed with testing")
        sys.exit(1)
    
    # Step 2: Generate and verify self-assessment
    if test_assessment_generation(job_id):
        logger.info("✅ Self-assessment test PASSED")
    else:
        logger.error("❌ Self-assessment test FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
