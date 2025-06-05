#!/usr/bin/env python3
"""
Main pipeline orchestration module for the job expansion workflow.
Coordinates the execution of pipeline steps based on user preferences.
"""

import logging
from datetime import datetime

# Import utility modules
from run_pipeline.utils.logging_utils import setup_logger, create_timestamped_dir
from run_pipeline.config.paths import (
    LOG_BASE_DIR,
    ensure_directories
)

# Import pipeline modules
from run_pipeline.core.pipeline_utils import process_job_ids, check_for_missing_skills
from run_pipeline.core.auto_fix import auto_fix_missing_skills_and_matches

# Import core processing modules
from run_pipeline.core.fetch_module import fetch_job_metadata
from run_pipeline.core.cleaner_module import clean_job_descriptions
from run_pipeline.core.status_checker_module import check_job_statuses
from run_pipeline.core.skills_module import process_skills

# Import modular components
from run_pipeline.core.job_scanner import run_job_scanner
from run_pipeline.core.job_matcher import run_job_matcher
from run_pipeline.core.feedback_loop import execute_feedback_loop
from run_pipeline.core.test_integration import process_force_good_matches

logger = logging.getLogger('pipeline')

def process_feedback():
    """
    Process feedback if available
    """
    # Placeholder for feedback processing functionality
    try:
        from run_pipeline.job_matcher.feedback_handler import process_feedback
        return process_feedback()
    except (ImportError, Exception) as e:
        logger.warning(f"Failed to process feedback: {e}")
        return False

def run_pipeline(args):
    """
    JMFS-compliant pipeline:
    0. Process feedback if present (never exit early)
    1-6. Job processing pipeline (fetch, clean, match, etc.)
    7. Export Excel with A-R columns
    8. Generate cover letters for 'Good' matches
    9. Email Excel + cover letters to reviewer
    10. Process returned feedback with LLM dispatcher
    """
    # Create log directory with timestamp
    log_dir = create_timestamped_dir(LOG_BASE_DIR, "job_workflow")
    
    # Set up logger
    logger, log_file = setup_logger('job_pipeline', log_dir)
    
    # Process job IDs if provided
    job_ids = process_job_ids(args.job_ids) if args.job_ids else None
    
    logger.info("=" * 50)
    logger.info("Starting JMFS Job Expansion Pipeline")
    logger.info("=" * 50)
    logger.info(f"Max jobs: {args.max_jobs}")
    logger.info(f"Model: {args.model}")
    logger.info(f"Job IDs: {job_ids if job_ids else 'All'}")
    logger.info(f"Output format: {args.output_format}")
    logger.info(f"Skip fetch: {args.skip_fetch}")
    logger.info(f"Skip status check: {args.skip_status_check}")
    logger.info(f"Skip skills processing: {args.skip_skills}")
    logger.info(f"Force reprocess: {args.force_reprocess}")
    logger.info(f"Rename removed jobs: {args.rename_removed_jobs}")
    logger.info(f"Auto-fix missing skills/matches: {args.auto_fix_missing}")
    logger.info(f"Enable feedback loop: {getattr(args, 'enable_feedback_loop', False)}")
    logger.info(f"Log directory: {log_dir}")
    logger.info("=" * 50)

    # Ensure feedback loop is enabled by default unless explicitly set
    if not hasattr(args, 'enable_feedback_loop'):
        args.enable_feedback_loop = True
    elif args.enable_feedback_loop is None:
        args.enable_feedback_loop = True

    # Process any forced good matches for testing
    if getattr(args, 'force_good_match', None) or getattr(args, 'force_good_matches', None):
        process_force_good_matches(args)
    
    # Ensure required directories exist
    ensure_directories()
    
    # Step 0: Process feedback if requested (even if pipeline is skipped)
    try:
        if getattr(args, 'enable_feedback_processing', False) or getattr(args, 'enable_feedback_loop', False):
            logger.info("Step 0: Processing feedback (if any) before main pipeline...")
            feedback_processed = process_feedback()
            if feedback_processed:
                logger.info("Feedback processed successfully.")
            else:
                logger.info("No feedback to process or nothing changed.")
    except Exception as e:
        logger.warning(f"Feedback processing failed or not implemented: {e}")

    # Step 1: Fetch job postings
    logger.info("Step 1: Fetching job postings...")
    if not args.skip_fetch:
        if not fetch_job_metadata(args.max_jobs, log_dir, args.force_reprocess):
            logger.warning("Fetch job metadata failed, continuing pipeline anyway.")
    else:
        logger.info("Step 1: Skipping job metadata fetch as requested")

    # Step 2: Process jobs (clean, status, skills, match)
    logger.info("Step 2: Processing jobs (cleaning, status check, skills, matching)...")
    
    # Step 2.1: Run job ID scanner if requested
    scanner_success, discovered_job_ids = run_job_scanner(args, job_ids, log_dir)
    
    # Step 2.2: Check status of existing jobs and also newly discovered jobs if any
    if not args.skip_status_check:
        # Prepare job IDs list for status check, combining original and newly discovered
        status_check_job_ids = job_ids
        if scanner_success and discovered_job_ids:
            if status_check_job_ids:
                status_check_job_ids = list(set(status_check_job_ids + discovered_job_ids))
                logger.info(f"Checking status of {len(status_check_job_ids)} jobs (original + newly discovered)")
            else:
                status_check_job_ids = discovered_job_ids
                logger.info(f"Checking status of {len(status_check_job_ids)} newly discovered jobs")
            
        if not check_job_statuses(
            max_jobs=args.max_jobs,
            job_ids=status_check_job_ids,
            log_dir=log_dir,
            rename_removed_files=args.rename_removed_jobs
        ):
            logger.warning("Some jobs could not be checked for online availability")
            # Continue anyway, don't fail the pipeline for this
    else:
        logger.info("Step 2/7: Skipping job availability check as requested")
        
    # Process any discovered jobs for cleaning too, even if original job_ids was specified
    if discovered_job_ids and not args.skip_clean:
        logger.info(f"Ensuring newly discovered jobs ({len(discovered_job_ids)}) will be included in cleaning step")

    # Step 3: Clean job descriptions for newly processed jobs
    if not args.skip_clean:
        logger.info("Step 3/7: Cleaning job descriptions for newly processed jobs...")
        
        # If we discovered new jobs from scanner, make sure they're processed
        clean_job_ids = job_ids
        if scanner_success and discovered_job_ids:
            if clean_job_ids:
                # Add newly discovered jobs to the list if we had specific job IDs
                clean_job_ids = list(set(clean_job_ids + discovered_job_ids))
                logger.info(f"Cleaning {len(clean_job_ids)} jobs (original + newly discovered)")
            else:
                # If no specific job IDs, use max_jobs limit with newly discovered included
                clean_job_ids = discovered_job_ids
                logger.info(f"No specific job IDs provided, including {len(discovered_job_ids)} newly discovered jobs")
                
        if not clean_job_descriptions(
            max_jobs=args.max_jobs if not clean_job_ids else None,
            job_ids=clean_job_ids,
            model=args.model,
            log_dir=log_dir,
            output_format=args.output_format
        ):
            return False
    else:
        logger.info("Step 3/7: Skipping job description cleaning as requested")

    # Step 4: Ensure all jobs have concise descriptions
    if not args.skip_clean:
        logger.info("Ensuring all jobs have concise descriptions...")
        if not clean_job_descriptions(
            max_jobs=args.max_jobs,
            job_ids=None,
            model=args.model,
            log_dir=log_dir,
            only_missing=True,
            output_format=args.output_format
        ):
            logger.warning("Some jobs could not be processed for concise descriptions")
            # Continue anyway, don't fail the pipeline for this

    # Step 5: Process skills
    logger.info("Step 5/7: Processing skills...")
    if not args.skip_skills:
        if not process_skills(job_ids=job_ids):
            return False
        # Check for missing skills and auto-fix if needed
        if args.auto_fix_missing:
            missing_job_skills = check_for_missing_skills(job_ids)
            if missing_job_skills:
                logger.info(f"Found {len(missing_job_skills)} jobs with missing skills")
                auto_fix_missing_skills_and_matches(missing_job_skills)
            else:
                logger.info("No jobs with missing skills found")
    else:
        logger.info("Skipping skills processing as requested")

    # Step 6: Generate match percentage and cover letter using llama3.2 job_matcher
    run_job_matcher(args, job_ids)
    
    # Steps 7-10: JMFS Feedback Loop (if enabled)
    if getattr(args, 'enable_feedback_loop', False):
        execute_feedback_loop(args, log_dir)
    else:
        logger.info("JMFS feedback loop not enabled. Use --enable-feedback-loop to activate.")

    logger.info("JMFS Pipeline completed successfully!")
    return True

# Export for external use
__all__ = ['run_pipeline']
