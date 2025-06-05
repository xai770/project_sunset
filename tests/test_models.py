#!/usr/bin/env python3
"""
Test script for consensus-based job detail extraction

This script tests the consensus job extractor on multiple job postings
and evaluates its effectiveness.
"""

import os
import sys
import json
import logging
import argparse
import random
from typing import List, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('consensus_extractor_test')

# Enable more verbose logging
logging.getLogger('consensus_job_extractor').setLevel(logging.DEBUG)

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# For testing without LLM dependencies, use the mock extractor
from mock_consensus_extractor import mock_consensus_extraction as extract_job_details_consensus

def get_job_ids(num_jobs: int = 5, specific_ids: List[str] = None) -> List[str]:
    """
    Get job IDs for testing
    
    Args:
        num_jobs: Number of random jobs to select if no specific IDs provided
        specific_ids: List of specific job IDs to test
        
    Returns:
        List of job IDs
    """
    if specific_ids:
        return specific_ids
        
    # Get available job IDs from the postings directory
    job_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                          'data', 'postings')
    
    if not os.path.exists(job_dir):
        logger.error(f"Job directory not found: {job_dir}")
        return []
    
    job_files = [f for f in os.listdir(job_dir) if f.startswith('job') and f.endswith('.json')]
    
    if not job_files:
        logger.error("No job files found")
        return []
    
    # Extract job IDs from filenames
    all_job_ids = [f.replace('job', '').replace('.json', '') for f in job_files]
    
    # Select random subset if we have more than requested
    if len(all_job_ids) > num_jobs:
        return random.sample(all_job_ids, num_jobs)
    
    return all_job_ids

def run_consensus_test(job_ids: List[str], output_file: str = None) -> Dict[str, Any]:
    """
    Run consensus extraction tests on multiple jobs
    
    Args:
        job_ids: List of job IDs to test
        output_file: Optional file to save test results
        
    Returns:
        Dictionary with test results
    """
    if not job_ids:
        logger.error("No job IDs provided for testing")
        return {"error": "No job IDs provided"}
    
    # Track results
    results = {
        "test_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "jobs_tested": len(job_ids),
        "successful_extractions": 0,
        "consensus_reached": 0,
        "test_details": []
    }
    
    # Process each job
    for job_id in job_ids:
        logger.info(f"Testing extraction for job {job_id}")
        
        try:
            # Run consensus extraction
            extraction_results = extract_job_details_consensus(job_id)
            
            if "error" in extraction_results:
                logger.warning(f"Error extracting job {job_id}: {extraction_results['error']}")
                results["test_details"].append({
                    "job_id": job_id,
                    "success": False,
                    "error": extraction_results["error"]
                })
            else:
                # Successful extraction
                results["successful_extractions"] += 1
                
                # Check if consensus was reached
                if extraction_results.get("consensus_reached", False):
                    results["consensus_reached"] += 1
                
                # Add to test details
                results["test_details"].append({
                    "job_id": job_id,
                    "success": True,
                    "consensus_reached": extraction_results.get("consensus_reached", False),
                    "model_used": extraction_results["extraction_model"],
                    "extraction_time": extraction_results["extraction_time"],
                    "content_length": len(extraction_results["extracted_text"]),
                    "original_title": extraction_results.get("original_title", "Unknown")
                })
                
                logger.info(f"Job {job_id} extracted successfully using {extraction_results['extraction_model']}")
                if extraction_results.get("consensus_reached", False):
                    logger.info(f"Consensus reached with similarity {extraction_results.get('consensus_similarity', 0):.2f}")
                else:
                    logger.info("No consensus reached between models")
                    
        except Exception as e:
            logger.error(f"Exception testing job {job_id}: {str(e)}")
            results["test_details"].append({
                "job_id": job_id,
                "success": False,
                "error": str(e)
            })
    
    # Calculate success rates
    if results["jobs_tested"] > 0:
        results["extraction_success_rate"] = results["successful_extractions"] / results["jobs_tested"]
        
        if results["successful_extractions"] > 0:
            results["consensus_rate"] = results["consensus_reached"] / results["successful_extractions"]
        else:
            results["consensus_rate"] = 0
    
    # Save results if output file specified
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Test results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving test results: {str(e)}")
    
    # Return the results summary
    return results

def main():
    """Main function for the test script"""
    parser = argparse.ArgumentParser(description="Test consensus-based job detail extraction")
    parser.add_argument("--jobs", help="Number of random jobs to test", type=int, default=5)
    parser.add_argument("--ids", help="Comma-separated list of specific job IDs to test", default="")
    parser.add_argument("--output", help="Output file path for test results", default="")
    args = parser.parse_args()
    
    # Get job IDs to test
    specific_ids = [id.strip() for id in args.ids.split(",") if id.strip()] if args.ids else None
    job_ids = get_job_ids(args.jobs, specific_ids)
    
    if not job_ids:
        logger.error("No jobs available for testing")
        sys.exit(1)
    
    logger.info(f"Testing consensus extraction on {len(job_ids)} jobs")
    
    # Set up output file path if provided
    output_file = None
    if args.output:
        output_file = args.output
    else:
        # Default output location
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                 'data', 'test_results')
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f'consensus_test_results_{timestamp}.json')
    
    # Run tests
    results = run_consensus_test(job_ids, output_file)
    
    # Display summary
    print("\nTest Results Summary:")
    print(f"Jobs tested: {results['jobs_tested']}")
    print(f"Successful extractions: {results['successful_extractions']}")
    print(f"Success rate: {results.get('extraction_success_rate', 0):.2%}")
    print(f"Consensus reached: {results['consensus_reached']}")
    print(f"Consensus rate: {results.get('consensus_rate', 0):.2%}")
    print(f"Detailed results saved to: {output_file}")

if __name__ == "__main__":
    main()
