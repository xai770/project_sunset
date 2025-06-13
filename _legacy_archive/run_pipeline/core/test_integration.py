#!/usr/bin/env python3
"""
Test integration module for the pipeline with utilities 
for testing and development purposes.
"""

import logging

logger = logging.getLogger('pipeline')

def process_force_good_matches(args):
    """
    Process forced good matches for testing cover letter generation
    """
    from run_pipeline.core.test_utils import force_good_match_for_testing
    
    # Handle single job ID
    if getattr(args, 'force_good_match', None):
        job_id = args.force_good_match
        logger.info(f"Forcing job {job_id} to have a 'Good' match for testing...")
        try:
            job_data = force_good_match_for_testing(job_id)
            if job_data:
                logger.info(f"Successfully forced job {job_id} to 'Good' match with application narrative")
            else:
                logger.error(f"Failed to force job {job_id} to 'Good' match")
        except Exception as e:
            logger.error(f"Error forcing job {job_id} to 'Good' match: {e}")
    
    # Handle comma-separated list of job IDs
    if getattr(args, 'force_good_matches', None):
        job_ids = args.force_good_matches.split(',')
        logger.info(f"Forcing jobs {job_ids} to have 'Good' matches for testing...")
        for job_id in job_ids:
            job_id = job_id.strip()
            try:
                job_data = force_good_match_for_testing(job_id)
                if job_data:
                    logger.info(f"Successfully forced job {job_id} to 'Good' match with application narrative")
                else:
                    logger.error(f"Failed to force job {job_id} to 'Good' match")
            except Exception as e:
                logger.error(f"Error forcing job {job_id} to 'Good' match: {e}")

# Export functions
__all__ = ['process_force_good_matches']
