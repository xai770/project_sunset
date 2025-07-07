#!/usr/bin/env python3
"""
Enhanced Pipeline Integration for Bucketed Skill Matching with Confidence Scoring

This provides a comprehensive integration of the bucketed skill matcher
with confidence scoring into the main pipeline.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced_bucketed_pipeline")

# Get paths from the main config
try:
    from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR
except ImportError:
    # Fallback if imported outside the pipeline
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    JOB_DATA_DIR = PROJECT_ROOT / "data" / "postings"

def run_bucketed_skill_matcher(
    job_ids: Optional[List[int]] = None,
    batch_size: int = 10,
    max_workers: int = 4,
    force_reprocess: bool = False,
    use_embeddings: bool = True
):
    """
    Run the enhanced bucketed skill matcher from the main pipeline
    
    Args:
        job_ids: Optional list of job IDs to process
        batch_size: Batch size for LLM calls
        max_workers: Maximum worker threads for parallel processing
        force_reprocess: Whether to reprocess jobs even if they already have matches
        use_embeddings: Whether to use embeddings for similarity scoring
    """
    logger.info("Running enhanced bucketed skill matcher with confidence scoring")
    
    # Dynamically import the best available implementation
    try:
        if use_embeddings:
            # Try to use the enhanced version with embedding similarity
            try:
                from run_pipeline.skill_matching.bucketed_skill_matcher_enhanced import batch_match_all_jobs
                logger.info("Using enhanced implementation with embedding similarity")
            except ImportError:
                from run_pipeline.skill_matching.bucketed_skill_matcher import batch_match_all_jobs
                logger.info("Using standard implementation (enhanced version not available)")
        else:
            # Use standard implementation without embeddings
            from run_pipeline.skill_matching.bucketed_skill_matcher import batch_match_all_jobs
            logger.info("Using standard implementation (embeddings disabled)")
    except ImportError:
        logger.error("Failed to import bucketed skill matcher implementation")
        return
    
    # Run the matcher
    logger.info(f"Using {max_workers} workers for parallel processing")
    batch_match_all_jobs(
        job_ids=job_ids,
        batch_size=batch_size,
        max_workers=max_workers,
        force_reprocess=force_reprocess
    )
    
    logger.info("Enhanced bucketed skill matching complete")

def enhanced_fix(
    missing_skill_jobs=None,
    zero_match_jobs=None,
    args=None
):
    """
    Fix jobs with missing SDR skills or zero match percentages using the enhanced approach
    
    Args:
        missing_skill_jobs (list, optional): List of job IDs missing SDR skills
        zero_match_jobs (list, optional): List of job IDs with zero match percentages
        args (argparse.Namespace, optional): Command line arguments
        
    Returns:
        bool: Success status
    """
    logger = logging.getLogger('job_pipeline')
    success = True
    
    # Use default values if args is None
    if args is None:
        from argparse import Namespace
        args = Namespace(
            batch_size=10, 
            max_workers=4, 
            no_embeddings=False, 
            force_reprocess=True
        )
    
    # Fix jobs without SDR skills
    if missing_skill_jobs and len(missing_skill_jobs) > 0:
        logger.info(f"Fixing {len(missing_skill_jobs)} jobs without SDR skills using enhanced approach")
        # Run SDR implementation specifically for these jobs
        job_ids = [int(job_id) for job_id in missing_skill_jobs]
        try:
            from run_pipeline.skill_matching.run_enhanced_sdr import run_sdr_implementation
            
            enriched_skills, relationships, visualizations = run_sdr_implementation(
                use_llm=True,
                max_skills=50,
                validate_enrichment=False,
                test_matching=False,
                apply_feedback=False,
                generate_visualizations=False,
                update_job_files=True,
                job_ids=job_ids,
                force_reprocess=True
            )
            logger.info(f"Enhanced SDR implementation completed for {len(missing_skill_jobs)} jobs")
        except Exception as e:
            logger.error(f"Error during enhanced SDR implementation: {str(e)}")
            success = False
    
    # Fix jobs with zero match percentages
    if zero_match_jobs and len(zero_match_jobs) > 0 and success:
        logger.info(f"Fixing {len(zero_match_jobs)} jobs with zero match percentages using enhanced bucketed approach")
        # Run batch skill matching for these jobs
        job_ids = [int(job_id) for job_id in zero_match_jobs]
        try:
            run_bucketed_skill_matcher(
                job_ids=job_ids,
                batch_size=getattr(args, 'batch_size', 10),
                max_workers=getattr(args, 'max_workers', 4),
                force_reprocess=getattr(args, 'force_reprocess', True),
                use_embeddings=not getattr(args, 'no_embeddings', False)
            )
            logger.info(f"Enhanced bucketed skill matching completed for {len(zero_match_jobs)} jobs")
        except Exception as e:
            logger.error(f"Error during enhanced bucketed skill matching: {str(e)}")
            success = False
    
    return success

def main():
    """Direct script execution"""
    parser = argparse.ArgumentParser(description="Run the enhanced bucketed skill matcher")
    parser.add_argument("--job-ids", type=int, nargs="+", help="Job IDs to process")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for LLM calls")
    parser.add_argument("--max-workers", type=int, default=4, help="Max worker threads")
    parser.add_argument("--force-reprocess", action="store_true", help="Force reprocessing")
    parser.add_argument("--no-embeddings", action="store_true", help="Disable embedding similarity")
    
    args = parser.parse_args()
    
    run_bucketed_skill_matcher(
        job_ids=args.job_ids,
        batch_size=args.batch_size,
        max_workers=args.max_workers,
        force_reprocess=args.force_reprocess,
        use_embeddings=not args.no_embeddings
    )

if __name__ == "__main__":
    main()
