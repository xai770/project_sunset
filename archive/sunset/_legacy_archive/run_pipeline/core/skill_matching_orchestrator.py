#!/usr/bin/env python3
"""
Skill matching orchestration module for the job expansion pipeline.
Coordinates skill matching based on user preferences, focusing exclusively on
the quick and effective bucketed skill matching approach.
"""

import logging

# Import bucketed pipeline
try:
    # Try to import the enhanced version with confidence scoring first
    from run_pipeline.skill_matching.bucketed_pipeline_enhanced import run_bucketed_skill_matcher
    BUCKETED_MATCHER_VERSION = "enhanced"
except ImportError:
    try:
        # Fall back to fixed version
        from run_pipeline.skill_matching.bucketed_pipeline_fixed import run_bucketed_skill_matcher
        BUCKETED_MATCHER_VERSION = "fixed"
    except ImportError:
        # Fall back to original version
        from run_pipeline.skill_matching.bucketed_pipeline import run_bucketed_skill_matcher
        BUCKETED_MATCHER_VERSION = "original"

logger = logging.getLogger('skill_matcher')

def run_skill_matching(args, job_ids=None):
    """
    Coordinate the skill matching based on command line arguments.
    This implementation focuses exclusively on the bucket-based matching approach
    which provides faster and more reliable results.
    
    Args:
        args: Command line arguments
        job_ids (list, optional): Specific job IDs to process
        
    Returns:
        dict: Results from the skill matching process
    """
    results = {
        "success": True,
        "matcher_used": None
    }
    
    logger.info(f"Using bucketed matcher version: {BUCKETED_MATCHER_VERSION}")
    
    # Run bucketed skill matching
    if args.run_skill_matching:
        logger.info("Running bucket-based skill matching...")
        run_bucketed_skill_matcher(
            job_ids=job_ids,
            batch_size=args.batch_size,
            max_workers=args.max_workers,
            force_reprocess=args.force_reprocess if hasattr(args, 'force_reprocess') else False,
            use_embeddings=not getattr(args, 'no_embeddings', False),
            use_confidence_scoring=getattr(args, 'confidence_scoring', False)
        )
        logger.info("Bucket-based skill matching complete.")
        results["matcher_used"] = f"bucketed_{BUCKETED_MATCHER_VERSION}"
    else:
        logger.info("Skill matching was not requested.")
    
    return results

# Export for external use
__all__ = ['run_skill_matching']
