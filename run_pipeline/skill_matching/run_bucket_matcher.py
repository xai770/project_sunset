#!/usr/bin/env python3
"""
Enhanced Bucket-Based Skill Matching Integration

This script serves as the entry point for running the enhanced bucket-based
skill matching system. It provides options for both direct use and integration
with the main pipeline.
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucketed_integration")

# Get project root
try:
    from run_pipeline.config.paths import PROJECT_ROOT
except ImportError:
    # Fallback if imported outside the pipeline
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def run_enhanced_bucket_matcher(
    job_ids: Optional[List[int]] = None,
    batch_size: int = 10,
    max_workers: int = 6,
    force_reprocess: bool = False
):
    """
    Run the enhanced bucket-based skill matcher
    
    Args:
        job_ids: Optional list of job IDs to process
        batch_size: Batch size for processing
        max_workers: Maximum worker threads
        force_reprocess: Whether to reprocess jobs even if they already have matches
    """
    try:
        # Try to import the enhanced version first
        from run_pipeline.skill_matching.bucketed_skill_matcher_enhanced import batch_match_all_jobs
        logger.info("Using enhanced bucket matcher implementation")
    except ImportError:
        # Fall back to fixed version
        try:
            from run_pipeline.skill_matching.bucketed_skill_matcher_fixed import batch_match_all_jobs
            logger.info("Using fixed bucket matcher implementation")
        except ImportError:
            # Fall back to original version
            from run_pipeline.skill_matching.bucketed_skill_matcher import batch_match_all_jobs
            logger.info("Using original bucket matcher implementation")
    
    start_time = time.time()
    
    # Run the bucket matcher
    batch_match_all_jobs(
        job_ids=job_ids,
        batch_size=batch_size,
        max_workers=max_workers,
        force_reprocess=force_reprocess
    )
    
    total_time = time.time() - start_time
    logger.info(f"Bucket matching completed in {total_time:.1f} seconds")


def detect_and_fix_issues(
    job_ids: Optional[List[int]] = None,
    batch_size: int = 10,
    max_workers: int = 6
):
    """
    Detect and fix issues with job skills and matches
    
    Args:
        job_ids: Optional list of job IDs to process
        batch_size: Batch size for processing
        max_workers: Maximum worker threads
    """
    try:
        # Try to import the enhanced version first
        from run_pipeline.skill_matching.bucketed_pipeline_enhanced import detect_and_fix_missing_matches
        logger.info("Using enhanced pipeline integration")
    except ImportError:
        # Fall back to using the fixed version directly
        logger.info("Enhanced pipeline integration not available")
        logger.info("Running enhanced bucket matcher directly")
        run_enhanced_bucket_matcher(
            job_ids=job_ids,
            batch_size=batch_size,
            max_workers=max_workers,
            force_reprocess=True
        )
        return
    
    # Create a namespace for arguments
    from argparse import Namespace
    args = Namespace(
        batch_size=batch_size,
        max_workers=max_workers,
        enhanced=False,
        bucketed=True,
        no_embeddings=False
    )
    
    # Run the detection and fix
    success, missing_skills, zero_matches = detect_and_fix_missing_matches(
        job_ids=job_ids,
        args=args
    )
    
    if success:
        logger.info("Successfully fixed all detected issues")
        if missing_skills:
            logger.info(f"Fixed {len(missing_skills)} jobs without skills")
        if zero_matches:
            logger.info(f"Fixed {len(zero_matches)} jobs with zero matches")
    else:
        logger.warning("Some issues could not be fixed automatically")


def generate_benchmarks(
    job_ids: Optional[List[int]] = None,
    max_workers: int = 6
):
    """
    Generate benchmarks comparing different skill matching approaches
    
    Args:
        job_ids: Optional list of job IDs to process
        max_workers: Maximum worker threads
    """
    logger.info("Running bucketed skill matching benchmarks")
    
    # Import the benchmark module
    try:
        from run_pipeline.skill_matching.bucketed_benchmark import run_benchmarks
        
        # Run benchmarks
        run_benchmarks(job_ids=job_ids, max_workers=max_workers)
        
    except ImportError:
        logger.error("Benchmark module not available")
        logger.info("Running enhanced bucket matcher directly instead")
        run_enhanced_bucket_matcher(
            job_ids=job_ids,
            max_workers=max_workers
        )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced bucket-based skill matching system"
    )
    
    parser.add_argument(
        "--job-ids", 
        type=int, 
        nargs="+", 
        help="Specific job IDs to process"
    )
    
    parser.add_argument(
        "--batch-size", 
        type=int, 
        default=10, 
        help="Batch size for processing (default: 10)"
    )
    
    parser.add_argument(
        "--max-workers", 
        type=int, 
        default=6, 
        help="Maximum worker threads (default: 6)"
    )
    
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force reprocessing even if jobs already have matches"
    )
    
    parser.add_argument(
        "--fix-issues", 
        action="store_true", 
        help="Detect and fix issues with job skills and matches"
    )
    
    parser.add_argument(
        "--benchmark", 
        action="store_true", 
        help="Generate benchmarks comparing different skill matching approaches"
    )
    
    args = parser.parse_args()
    
    if args.benchmark:
        # Run benchmarks
        generate_benchmarks(
            job_ids=args.job_ids,
            max_workers=args.max_workers
        )
    elif args.fix_issues:
        # Detect and fix issues
        detect_and_fix_issues(
            job_ids=args.job_ids,
            batch_size=args.batch_size,
            max_workers=args.max_workers
        )
    else:
        # Run bucket matcher
        run_enhanced_bucket_matcher(
            job_ids=args.job_ids,
            batch_size=args.batch_size,
            max_workers=args.max_workers,
            force_reprocess=args.force
        )


if __name__ == "__main__":
    main()
