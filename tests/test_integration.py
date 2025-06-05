#!/usr/bin/env python3
"""
Integration Test for Enhanced Bucketed Skill Matching with Confidence Scoring

This script tests the end-to-end integration of the bucketed skill matching
system with confidence scoring in the main pipeline.
"""

import os
import sys
import json
import logging
import argparse
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("integration_test")

# Get the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import pipeline integration
try:
    from run_pipeline.skill_matching.bucketed_pipeline_enhanced import run_bucketed_skill_matcher
    HAS_ENHANCED = True
except ImportError:
    HAS_ENHANCED = False
    logger.error("Enhanced bucketed skill matcher not found")
    sys.exit(1)

# Import confidence scoring
try:
    from run_pipeline.skill_matching.confidence_scorer import (
        calculate_confidence_score,
        get_confidence_level
    )
    HAS_CONFIDENCE = True
except ImportError:
    HAS_CONFIDENCE = False
    logger.error("Confidence scoring module not found")
    sys.exit(1)

def test_job_confidence_scores(job_ids=None, threshold=0.5):
    """
    Test confidence scores for processed jobs
    
    Args:
        job_ids: Optional list of job IDs to check
        threshold: Minimum acceptable confidence score
    
    Returns:
        tuple: (success, results)
    """
    from run_pipeline.config.paths import JOB_DATA_DIR
    
    job_dir = Path(JOB_DATA_DIR)
    results = {
        "passed": [],
        "failed": [],
        "skipped": [],
        "stats": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "avg_confidence": 0.0
        }
    }
    
    # Get job files
    if job_ids:
        job_files = []
        for job_id in job_ids:
            job_file = job_dir / f"job{job_id}.json"
            if job_file.exists():
                job_files.append(job_file)
    else:
        job_files = sorted(list(job_dir.glob("job*.json")))[:10]  # Test first 10 jobs by default
    
    total_confidence = 0.0
    results["stats"]["total"] = len(job_files)
    
    for job_file in job_files:
        job_id = job_file.stem.replace("job", "")
        
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
                
            # Check if job has skill match data with confidence scores
            skill_match = job_data.get("skill_match", {})
            
            if not skill_match:
                logger.warning(f"Job {job_id} has no skill matches")
                results["skipped"].append({
                    "job_id": job_id,
                    "reason": "No skill matches found"
                })
                results["stats"]["skipped"] += 1
                continue
            
            # Check if confidence scores are present
            if "confidence_score" not in skill_match:
                logger.warning(f"Job {job_id} has no confidence scores")
                results["skipped"].append({
                    "job_id": job_id,
                    "reason": "No confidence scores found"
                })
                results["stats"]["skipped"] += 1
                continue
            
            # Extract confidence score and check against threshold
            confidence_score = skill_match.get("confidence_score", 0.0)
            confidence_level = get_confidence_level(confidence_score)
            total_confidence += confidence_score
            
            if confidence_score >= threshold:
                results["passed"].append({
                    "job_id": job_id,
                    "confidence_score": confidence_score,
                    "confidence_level": confidence_level,
                    "match_percentage": skill_match.get("overall_match", 0.0)
                })
                results["stats"]["passed"] += 1
            else:
                results["failed"].append({
                    "job_id": job_id,
                    "confidence_score": confidence_score,
                    "confidence_level": confidence_level,
                    "match_percentage": skill_match.get("overall_match", 0.0)
                })
                results["stats"]["failed"] += 1
                
        except Exception as e:
            logger.error(f"Error testing job {job_id}: {str(e)}")
            results["skipped"].append({
                "job_id": job_id,
                "reason": f"Error: {str(e)}"
            })
            results["stats"]["skipped"] += 1
    
    # Calculate average confidence
    if results["stats"]["passed"] + results["stats"]["failed"] > 0:
        results["stats"]["avg_confidence"] = total_confidence / (results["stats"]["passed"] + results["stats"]["failed"])
    
    return results["stats"]["failed"] == 0, results

def run_integration_test(job_ids=None, batch_size=5, max_workers=2, force_reprocess=True):
    """
    Run the integration test
    
    Args:
        job_ids: Optional list of job IDs to process
        batch_size: Batch size for LLM calls
        max_workers: Maximum worker threads
        force_reprocess: Force reprocessing of jobs
    """
    logger.info("Starting integration test for enhanced bucketed skill matching with confidence scoring")
    
    start_time = time.time()
    
    # Step 1: Run the bucketed skill matcher
    logger.info("Step 1: Running enhanced bucketed skill matcher")
    run_bucketed_skill_matcher(
        job_ids=job_ids,
        batch_size=batch_size,
        max_workers=max_workers,
        force_reprocess=force_reprocess,
        use_embeddings=True
    )
    
    # Step 2: Test confidence scores
    logger.info("Step 2: Testing confidence scores")
    success, results = test_job_confidence_scores(job_ids)
    
    # Step 3: Report results
    end_time = time.time()
    logger.info(f"Test completed in {end_time - start_time:.2f} seconds")
    
    logger.info("=" * 50)
    logger.info("INTEGRATION TEST RESULTS")
    logger.info("=" * 50)
    logger.info(f"Total jobs tested: {results['stats']['total']}")
    logger.info(f"Jobs with valid confidence scores: {results['stats']['passed'] + results['stats']['failed']}")
    logger.info(f"Jobs skipped: {results['stats']['skipped']}")
    logger.info(f"Average confidence score: {results['stats']['avg_confidence']:.2f}")
    logger.info(f"Jobs passing confidence threshold: {results['stats']['passed']}")
    logger.info(f"Jobs failing confidence threshold: {results['stats']['failed']}")
    logger.info("=" * 50)
    
    if success:
        logger.info("✅ INTEGRATION TEST PASSED")
        return True
    else:
        logger.warning("⚠️ INTEGRATION TEST FAILED")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Integration test for enhanced bucketed skill matching")
    parser.add_argument("--job-ids", type=int, nargs="+", help="Job IDs to process")
    parser.add_argument("--batch-size", type=int, default=5, help="Batch size for LLM calls")
    parser.add_argument("--max-workers", type=int, default=2, help="Max worker threads")
    parser.add_argument("--force-reprocess", action="store_true", help="Force reprocessing")
    parser.add_argument("--threshold", type=float, default=0.5, help="Confidence score threshold")
    
    args = parser.parse_args()
    
    if not HAS_ENHANCED or not HAS_CONFIDENCE:
        logger.error("Required modules not available")
        return 1
    
    success = run_integration_test(
        job_ids=args.job_ids,
        batch_size=args.batch_size,
        max_workers=args.max_workers,
        force_reprocess=args.force_reprocess
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
