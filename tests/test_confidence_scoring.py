#!/usr/bin/env python3
"""
Test script for the confidence scoring implementation in bucketed skill matching

This script tests the confidence scoring functionality by running a match
on a specific job and analyzing the confidence scores.
"""

import os
import sys
import json
import logging
from pathlib import Path
from pprint import pprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("confidence_test")

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import required modules
try:
    from run_pipeline.config.paths import JOB_DATA_DIR, PROJECT_ROOT
    from run_pipeline.skill_matching.bucket_matcher import match_job_to_your_skills
    from run_pipeline.skill_matching.bucket_cache import bucket_cache
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def test_confidence_scoring(job_id: int):
    """
    Test the confidence scoring functionality
    
    Args:
        job_id: The job ID to test
    """
    logger.info(f"Testing confidence scoring for job {job_id}")
    
    # Load job data
    job_file = Path(JOB_DATA_DIR) / f"job{job_id}.json"
    if not job_file.exists():
        logger.error(f"Job file not found: {job_file}")
        return False
    
    try:
        with open(job_file, "r", encoding="utf-8") as f:
            job_data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load job file: {e}")
        return False
    
    # Load your skills data
    your_skills_file = PROJECT_ROOT / "profile" / "skills" / "skill_decompositions.json"
    if not your_skills_file.exists():
        logger.error(f"Your skills file not found: {your_skills_file}")
        return False
    
    try:
        with open(your_skills_file, "r", encoding="utf-8") as f:
            your_skills = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load your skills: {e}")
        return False
    
    # Clear cache to ensure fresh confidence calculations
    bucket_cache.cache = {}
    
    # Run match with confidence scoring
    logger.info("Running match with confidence scoring...")
    match_result = match_job_to_your_skills(job_data, your_skills, max_workers=4)
    
    # Analyze results
    logger.info("\n=== MATCH RESULTS ===")
    logger.info(f"Overall match: {match_result.get('overall_match', 0.0) * 100:.1f}%")
    
    if "overall_confidence" in match_result:
        logger.info(f"Overall confidence: {match_result['overall_confidence'] * 100:.1f}%")
        logger.info(f"Confidence level: {match_result.get('confidence_level', 'Unknown')}")
    else:
        logger.info("No overall confidence score available")
    
    # Print detailed bucket results
    logger.info("\n=== BUCKET RESULTS ===")
    for bucket, result in match_result.get("bucket_results", {}).items():
        logger.info(f"\nBucket: {bucket}")
        logger.info(f"Match: {result.get('match_percentage', 0.0) * 100:.1f}%")
        logger.info(f"Weight: {result.get('weight', 0.0) * 100:.1f}%")
        
        if "confidence" in result:
            confidence = result["confidence"]
            logger.info("\nConfidence details:")
            logger.info(f"- Confidence score: {confidence.get('confidence_score', 'N/A')}")
            logger.info(f"- Confidence level: {confidence.get('confidence_level', 'N/A')}")
            logger.info(f"- Embedding similarity: {confidence.get('embedding_similarity', 'N/A')}")
            logger.info(f"- Bucket relevance: {confidence.get('bucket_relevance', 'N/A')}")
            logger.info(f"- LLM confidence: {confidence.get('llm_confidence', 'N/A')}")
        
        # Print a few skills from each bucket
        job_skills = result.get("job_skills", [])
        cv_skills = result.get("cv_skills", [])
        
        logger.info(f"\nJob skills: {len(job_skills)}")
        for skill in job_skills[:3]:
            logger.info(f"- {skill}")
        if len(job_skills) > 3:
            logger.info("- ...")
        
        logger.info(f"\nCV skills: {len(cv_skills)}")
        for skill in cv_skills[:3]:
            logger.info(f"- {skill}")
        if len(cv_skills) > 3:
            logger.info("- ...")
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test confidence scoring in bucketed skill matching")
    parser.add_argument("--job-id", type=int, required=True, help="Job ID to test")
    
    args = parser.parse_args()
    
    success = test_confidence_scoring(args.job_id)
    
    sys.exit(0 if success else 1)
