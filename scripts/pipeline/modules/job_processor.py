#!/usr/bin/env python3
"""
Job Processor Module
====================

Handles job processing using specialists for CV matching and evaluation.
"""

import json
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent


def process_jobs_with_specialists(job_ids=None, force_reprocess=False):
    """Process jobs using the JobMatchingAPI with specialists"""
    logger = logging.getLogger(__name__)
    logger.info("=== PROCESSING JOBS WITH SPECIALISTS (Phase 7) ===")
    
    try:
        # Use the legacy job processing system which calls specialists internally
        from run_pipeline.job_matcher.cv_loader import load_cv_text
        from run_pipeline.job_matcher.job_processor import process_job, update_job_json
        
        # Load CV text
        cv_text = load_cv_text()
        logger.info(f"📋 CV loaded ({len(cv_text)} characters)")
        
        # Determine which jobs to process
        if job_ids:
            jobs_to_process = job_ids
            logger.info(f"📊 Processing {len(jobs_to_process)} specified jobs")
        else:
            # Load jobs from scan progress
            scan_progress_path = project_root / "data" / "job_scans" / "search_api_scan_progress.json"
            try:
                with open(scan_progress_path, "r") as f:
                    progress_data = json.load(f)
                jobs_to_process = progress_data.get("jobs_processed", [])
                logger.info(f"📊 Found {len(jobs_to_process)} jobs in scan progress")
            except Exception as e:
                logger.error(f"❌ Failed to load jobs from scan progress: {e}")
                return []
        
        # Process each job using specialists
        processed_jobs = []
        skipped_jobs = []
        for job_id in jobs_to_process:
            logger.info(f"🔄 Processing job {job_id} with specialists...")
            try:
                job_result = process_job(str(job_id), cv_text, num_runs=3, dump_input=False, force_reprocess=force_reprocess)
                if "error" not in job_result:
                    if job_result.get("from_cache"):
                        skipped_jobs.append(job_id)
                        logger.info(f"⏭️ Job {job_id} already processed - skipped")
                    else:
                        update_job_json(str(job_id), job_result)
                        processed_jobs.append(job_id)
                        logger.info(f"✅ Job {job_id} processed successfully")
                else:
                    logger.warning(f"⚠️ Job {job_id} processing had issues: {job_result.get('error', 'Unknown')}")
            except Exception as e:
                logger.error(f"❌ Error processing job {job_id}: {e}")
        
        logger.info(f"🎉 Successfully processed {len(processed_jobs)} jobs with specialists")
        if skipped_jobs:
            logger.info(f"⏭️ Skipped {len(skipped_jobs)} already processed jobs")
        return processed_jobs
        
    except Exception as e:
        logger.error(f"❌ Error during job processing with specialists: {e}")
        return []
