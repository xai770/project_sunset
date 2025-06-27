#!/usr/bin/env python3
"""
Auto-fix module for the job expansion pipeline.
Provides functionality to automatically fix jobs with missing skills or zero match percentages.
"""

import logging
from argparse import Namespace

# Import bucketed pipeline if available
try:
    # Try to use enhanced detection and fixing
    from run_pipeline.skill_matching.bucketed_pipeline_enhanced import fix_missing_skills_and_matches as enhanced_fix
    from run_pipeline.skill_matching.bucketed_pipeline_enhanced import run_bucketed_skill_matcher
    HAS_ENHANCED_BUCKETED = True
except ImportError:
    # Fall back to standard approach
    from run_pipeline.skill_matching.bucketed_pipeline import run_bucketed_skill_matcher
    HAS_ENHANCED_BUCKETED = False

logger = logging.getLogger('job_pipeline')

def auto_fix_missing_skills_and_matches(missing_skill_jobs=None, zero_match_jobs=None, args=None):
    """
    Fix jobs with missing skills or zero match percentages
    
    Args:
        missing_skill_jobs (list, optional): List of job IDs missing skills
        zero_match_jobs (list, optional): List of job IDs with zero match percentages
        args (argparse.Namespace, optional): Command line arguments
        
    Returns:
        bool: Success status
    """
    success = True
    
    # Use default values if args is None
    if args is None:
        args = Namespace(
            batch_size=10, 
            max_workers=4, 
            no_embeddings=False,
            force_reprocess=False
        )
    
    # Check if we have any jobs to fix
    if not missing_skill_jobs and not zero_match_jobs:
        logger.info("No jobs to fix")
        return True
    
    # Handle enhanced bucketed approach if available
    if HAS_ENHANCED_BUCKETED:
        logger.info("Using enhanced bucketed skill matcher for auto-fixing")
        return enhanced_fix(
            missing_skill_jobs=missing_skill_jobs,
            zero_match_jobs=zero_match_jobs,
            args=args
        )
    
    # Standard approach using the bucketed matcher
    if missing_skill_jobs and len(missing_skill_jobs) > 0:
        logger.info(f"Fixing {len(missing_skill_jobs)} jobs missing skills")
        job_ids = [int(job_id) for job_id in missing_skill_jobs]
        try:
            run_bucketed_skill_matcher(
                job_ids=job_ids,
                batch_size=getattr(args, 'batch_size', 10),
                max_workers=getattr(args, 'max_workers', 4),
                force_reprocess=True,
                use_embeddings=not getattr(args, 'no_embeddings', False),
                use_confidence_scoring=getattr(args, 'confidence_scoring', False)
            )
            logger.info(f"Bucketed skill matching completed for {len(missing_skill_jobs)} jobs")
        except Exception as e:
            logger.error(f"Error during bucketed skill matching: {str(e)}")
            success = False
    
    # Fix jobs with zero match percentages
    if zero_match_jobs and len(zero_match_jobs) > 0 and success:
        logger.info(f"Fixing {len(zero_match_jobs)} jobs with zero match percentages")
        job_ids = [int(job_id) for job_id in zero_match_jobs]
        try:
            run_bucketed_skill_matcher(
                job_ids=job_ids,
                batch_size=getattr(args, 'batch_size', 10),
                max_workers=getattr(args, 'max_workers', 4),
                force_reprocess=True,
                use_embeddings=not getattr(args, 'no_embeddings', False),
                use_confidence_scoring=getattr(args, 'confidence_scoring', False)
            )
            logger.info(f"Bucketed skill matching completed for {len(zero_match_jobs)} jobs")
        except Exception as e:
            logger.error(f"Error during bucketed skill matching: {str(e)}")
            success = False
    
    return success

# Export for external use
__all__ = ['auto_fix_missing_skills_and_matches']
