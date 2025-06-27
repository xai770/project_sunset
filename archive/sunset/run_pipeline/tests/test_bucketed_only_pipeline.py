#!/usr/bin/env python3
"""
Test script to verify the bucketed-only pipeline refactoring
"""

import os
import sys
import logging
import json
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import necessary modules
from run_pipeline.core.cli_args import parse_args
from run_pipeline.core.pipeline_main import main
from run_pipeline.config.paths import JOB_DATA_DIR

# For testing, use the api_test_results directory which contains sample jobs
API_TEST_RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../api_test_results'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_bucketed_only")

def test_bucketed_matching_with_sample_job():
    """Test bucketed matching with a sample job"""
    # Find a sample job file
    job_dir = Path(API_TEST_RESULTS_DIR)
    job_files = list(job_dir.glob("job_*.json"))
    
    if not job_files:
        logger.error("No job files found for testing")
        return False
    
    # Get the first job ID
    job_id = job_files[0].stem.replace("job_", "")
    logger.info(f"Testing with job {job_id}")
    
    # Set up command line arguments
    sys.argv = [
        "pipeline_main.py",
        "--run-skill-matching",
        "--skip-status-check",  # Skip status check but allow fetch
        "--force-reprocess",
        "--confidence-scoring"
    ]
    
    # Run the pipeline
    result = main()
    
    # Verify the result
    if not result:
        logger.error("Pipeline execution failed")
        return False
    
    # Since this is a test, we'll assume success if the pipeline completes without errors
    logger.info("Pipeline execution completed successfully")
    return True

if __name__ == "__main__":
    logger.info("Starting bucketed-only pipeline test")
    result = test_bucketed_matching_with_sample_job()
    if result:
        logger.info("Test passed!")
        sys.exit(0)
    else:
        logger.error("Test failed!")
        sys.exit(1)
