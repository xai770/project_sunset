#!/usr/bin/env python3
"""
Job scanner module for discovering new or missing jobs in the job database.
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger('pipeline')

def run_job_scanner(args, job_ids=None, log_dir=None):
    """
    Run job scanner to discover new or missing jobs
    
    Args:
        args: Command line arguments
        job_ids: Specific job IDs to check
        log_dir: Directory for logs
        
    Returns:
        tuple: (success_status, new_job_ids) - success status and list of newly discovered job IDs
    """
    if not getattr(args, 'run_job_scanner', False):
        logger.info("Skipping job scanner as not requested")
        return True, []
        
    logger.info("Running job ID scanner to discover new or missing jobs...")
    discovered_job_ids = []
    
    try:
        from run_pipeline.core.job_id_scanner import scan_specific_ranges, scan_job_range
        
        # Set up additional log handler if log_dir is provided
        if log_dir:
            scanner_log_path = os.path.join(log_dir, "job_id_scanner.log")
            import logging
            scanner_handler = logging.FileHandler(scanner_log_path)
            scanner_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logging.getLogger('job_id_scanner').addHandler(scanner_handler)
            logger.info(f"Added log handler for job scanner. Writing to {scanner_log_path}")
        
        # Run job scanner with default ranges
        if getattr(args, 'scan_specific_ranges', True):
            logger.info("Scanning specific predefined ranges for missing jobs...")
            scanner_results = scan_specific_ranges()
            
            # Extract job IDs from results (scan_specific_ranges returns the list of jobs)
            if isinstance(scanner_results, list):
                discovered_job_ids = [str(job_result["job_id"]) for job_result in scanner_results if job_result.get("is_valid_job", False)]
                logger.info(f"Job scanner discovered {len(discovered_job_ids)} jobs in predefined ranges")
            else:
                logger.warning("scan_specific_ranges() did not return expected list result format")
        
        # Or scan a custom range if specified
        elif hasattr(args, 'scan_start_id') and hasattr(args, 'scan_end_id'):
            logger.info(f"Scanning custom job ID range {args.scan_start_id}-{args.scan_end_id}...")
            scanner_results = scan_job_range(
                args.scan_start_id,
                args.scan_end_id,
                concurrent=getattr(args, 'scan_concurrent', True),
                max_workers=getattr(args, 'scan_workers', 5)
            )
            
            # Extract job IDs from results (scan_job_range returns a dict with 'results' key)
            if isinstance(scanner_results, dict) and 'results' in scanner_results:
                discovered_job_ids = [str(job_result["job_id"]) for job_result in scanner_results['results']]
                logger.info(f"Job scanner processed range {args.scan_start_id}-{args.scan_end_id}")
                logger.info(f"Found {len(discovered_job_ids)} valid jobs in custom range")
            else:
                logger.warning("scan_job_range() did not return expected result format with 'results' key")
        
        if discovered_job_ids:
            logger.info(f"Job scanner successfully discovered {len(discovered_job_ids)} new or existing jobs")
            logger.info(f"Discovered job IDs: {', '.join(discovered_job_ids[:10])}{' and more...' if len(discovered_job_ids) > 10 else ''}")
        else:
            logger.info("Job scanner completed but did not discover any valid jobs")
            
        return True, discovered_job_ids
    except Exception as e:
        logger.error(f"Error running job scanner: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False, []

def reset_progress_tracker():
    """Reset the job scan progress tracker file to initial state."""
    progress_path = os.path.join(os.path.dirname(__file__), '../../data/job_scans/search_api_scan_progress.json')
    progress_path = os.path.abspath(progress_path)
    if os.path.exists(progress_path):
        with open(progress_path, 'w') as f:
            json.dump({
                "last_page_fetched": 0,
                "jobs_processed": [],
                "timestamp": datetime.now().isoformat(),
                "stats": {
                    "total_jobs_found": 0,
                    "total_jobs_processed": 0,
                    "total_pages_fetched": 0
                }
            }, f, indent=2)
        print(f"Progress tracker reset: {progress_path}")
    else:
        print(f"Progress tracker file not found: {progress_path}")

# Export functions
__all__ = ['run_job_scanner', 'reset_progress_tracker']
