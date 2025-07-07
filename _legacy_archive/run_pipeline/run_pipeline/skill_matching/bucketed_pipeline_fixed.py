#!/usr/bin/env python3
"""
Pipeline integration module for bucketed skill matching

This provides a single point of integration for the bucketed skill matcher
into the main pipeline.
"""

import logging
import argparse
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucketed_pipeline_integration")

def run_bucketed_skill_matcher(
    job_ids: Optional[List[int]] = None,
    batch_size: int = 10,
    max_workers: int = 4,
    force_reprocess: bool = False,
    use_embeddings: bool = True,
    use_confidence_scoring: bool = False
):
    """
    Run the bucketed skill matcher from the main pipeline
    
    Args:
        job_ids: Optional list of job IDs to process
        batch_size: Batch size for LLM calls
        max_workers: Maximum worker threads
        force_reprocess: (ignored in this version)
        use_embeddings: (ignored in this version)
        use_confidence_scoring: (ignored in this version)
    """
    from run_pipeline.skill_matching.bucketed_skill_matcher_fixed import batch_match_all_jobs
    
    logger.info("Running bucketed skill matcher")
    batch_match_all_jobs(
        job_ids=job_ids,
        batch_size=batch_size,
        max_workers=max_workers,
        force_reprocess=force_reprocess,
        use_embeddings=use_embeddings,
        use_confidence_scoring=use_confidence_scoring
    )
    logger.info("Bucketed skill matching complete")

def main():
    """Direct script execution"""
    parser = argparse.ArgumentParser(description="Run the bucketed skill matcher")
    parser.add_argument("--job-ids", type=int, nargs="+", help="Job IDs to process")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for LLM calls")
    parser.add_argument("--max-workers", type=int, default=4, help="Max worker threads")
    
    args = parser.parse_args()
    
    run_bucketed_skill_matcher(
        job_ids=args.job_ids,
        batch_size=args.batch_size,
        max_workers=args.max_workers
    )

if __name__ == "__main__":
    main()
