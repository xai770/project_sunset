#!/usr/bin/env python3
"""
Test script for the refactored pipeline modules.
This script verifies that the refactored pipeline works correctly.
"""

import os
import sys
import argparse
import logging

# Add the project root to the path (if needed)
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(os.path.dirname(current_dir))
# sys.path.append(project_root)

# Import refactored modules
from run_pipeline.core.cli_args import parse_args
from run_pipeline.core.pipeline_orchestrator import run_pipeline
from run_pipeline.core.pipeline_utils import process_job_ids, check_for_missing_sdr_skills
from run_pipeline.core.auto_fix import auto_fix_missing_skills_and_matches
from run_pipeline.core.skill_matching_orchestrator import run_skill_matching

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_refactored_pipeline')

def create_test_args():
    """
    Create a test arguments object
    
    Returns:
        argparse.Namespace: Test arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-jobs", type=int, default=10)
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo")
    parser.add_argument("--job-ids", type=str, default=None)
    parser.add_argument("--skip-fetch", action="store_true", default=True)
    parser.add_argument("--skip-clean", action="store_true", default=True)
    parser.add_argument("--skip-status-check", action="store_true", default=True)
    parser.add_argument("--skip-skills", action="store_true", default=False)
    parser.add_argument("--clean-missing-only", action="store_true", default=False)
    parser.add_argument("--output-format", type=str, default="text")
    parser.add_argument("--force-reprocess", action="store_true", default=False)
    parser.add_argument("--rename-removed-jobs", action="store_true", default=False)
    parser.add_argument("--no-firefox-check", action="store_true", default=True)
    parser.add_argument("--use-sdr", action="store_true", default=False)
    parser.add_argument("--run-skill-matching", action="store_true", default=True)
    parser.add_argument("--auto-fix-missing", action="store_true", default=False)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--enhanced", action="store_true", default=False)
    parser.add_argument("--bucketed", action="store_true", default=True)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--no-embeddings", action="store_true", default=False)
    parser.add_argument("--confidence-scoring", action="store_true", default=True)
    
    # SDR specific arguments
    parser.add_argument("--sdr-use-llm", action="store_true", default=False)
    parser.add_argument("--sdr-max-skills", type=int, default=50)
    parser.add_argument("--sdr-validate", action="store_true", default=False)
    parser.add_argument("--sdr-test-matching", action="store_true", default=False)
    parser.add_argument("--sdr-apply-feedback", action="store_true", default=False)
    parser.add_argument("--sdr-generate-visualizations", action="store_true", default=False)
    parser.add_argument("--sdr-force-reprocess", action="store_true", default=False)
    
    return parser.parse_args([])  # Parse empty args list, we're setting defaults

def test_process_job_ids():
    """Test the process_job_ids function"""
    logger.info("Testing process_job_ids...")
    
    # Test with None
    result1 = process_job_ids(None)
    assert result1 is None, f"Expected None, got {result1}"
    
    # Test with empty string
    result2 = process_job_ids("")
    assert result2 is None, f"Expected None, got {result2}"
    
    # Test with valid job IDs
    result3 = process_job_ids("12345,67890")
    assert result3 == [12345, 67890], f"Expected [12345, 67890], got {result3}"
    
    logger.info("process_job_ids tests passed!")

def test_skill_matching_orchestrator():
    """Test the skill matching orchestrator"""
    logger.info("Testing skill matching orchestrator...")
    
    args = create_test_args()
    # Set minimum number of jobs to process and configure for bucketed matching
    args.max_jobs = 3
    args.bucketed = True
    args.run_skill_matching = True
    
    try:
        results = run_skill_matching(args)
        assert "matcher_used" in results, "Expected matcher_used in results"
        assert "bucketed" in results["matcher_used"], f"Expected bucketed matcher, got {results['matcher_used']}"
        logger.info(f"Skill matching test used: {results['matcher_used']}")
        logger.info("Skill matching orchestrator test passed!")
    except Exception as e:
        logger.error(f"Skill matching orchestrator test failed: {str(e)}")
        raise

def run_all_tests():
    """Run all tests for the refactored pipeline"""
    logger.info("Running tests for refactored pipeline...")
    
    # Test utility functions
    test_process_job_ids()
    
    # Test skill matching orchestrator (only if not running in CI environment)
    if not os.environ.get("CI", False):
        test_skill_matching_orchestrator()
    
    logger.info("All tests passed!")

if __name__ == "__main__":
    run_all_tests()
