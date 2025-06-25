#!/usr/bin/env python3
"""
Command line argument parsing module for the job expansion pipeline.
Provides a centralized place for defining and parsing command line arguments.
"""

import argparse
from run_pipeline.config.paths import DEFAULT_MAX_JOBS, DEFAULT_MODEL

def parse_args():
    """
    Parse command-line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Job Expansion Pipeline")
    
    parser.add_argument(
        "--max-jobs", 
        type=int, 
        default=DEFAULT_MAX_JOBS,
        help=f"Maximum number of jobs to process in one run (default: {DEFAULT_MAX_JOBS})"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        default=DEFAULT_MODEL,
        help=f"The model to use for concise description generation (default: {DEFAULT_MODEL})"
    )
    
    parser.add_argument(
        "--job-ids",
        type=str,
        help="Specific job IDs to process (comma-separated)"
    )
    
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Skip the job metadata fetching step"
    )
    
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Skip the job detail scraping step (deprecated - scraping is now bypassed by default)"
    )
    
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="Skip the job description cleaning step"
    )
    
    parser.add_argument(
        "--skip-status-check",
        action="store_true",
        help="Skip checking if job postings are still available online"
    )
    
    parser.add_argument(
        "--skip-skills",
        action="store_true",
        help="Skip the skills extraction and processing step"
    )
    
    parser.add_argument(
        "--clean-missing-only",
        action="store_true",
        help="Only clean job descriptions that are missing concise descriptions"
    )
    
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Format for job description output ('text' or 'json')"
    )
    
    parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Force reprocessing of jobs even if they already exist"
    )
    
    parser.add_argument(
        "--rename-removed-jobs",
        action="store_true",
        help="Rename files for jobs that are no longer available online (e.g., job12345_removed.json)"
    )
    
    parser.add_argument(
        "--no-firefox-check",
        action="store_true",
        help="Skip checking for Firefox (deprecated - Firefox is no longer required)"
    )
    
    # Skill matching arguments
    parser.add_argument(
        "--run-skill-matching",
        action="store_true",
        help="Run the bucketed skill matcher as part of the pipeline"
    )

    parser.add_argument(
        "--auto-fix-missing",
        action="store_true",
        help="Automatically check and fix jobs with missing SDR skills or zero match percentages"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size for LLM calls when processing skills (default: 10)"
    )
    
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of parallel workers for skill matching (default: 4)"
    )
    
    parser.add_argument(
        "--no-embeddings",
        action="store_true",
        help="Disable embedding-based skill matching in the bucketed matcher"
    )
    
    parser.add_argument(
        "--confidence-scoring",
        action="store_true",
        help="Enable confidence scoring in bucketed skill matching"
    )
    
    # Phi3 LLM matching arguments
    parser.add_argument(
        "--only-regenerate-phi3",
        action="store_true",
        help="Only regenerate phi3 match percentage and cover letter fields, skipping other pipeline steps"
    )
    
    # Feedback system arguments
    parser.add_argument(
        "--enable-feedback-processing", 
        action="store_true",
        help="Enable Step 10: Process returned Excel feedback emails"
    )
    
    parser.add_argument(
        "--enable-feedback-loop", 
        action="store_true",
        help="Enable JMFS Steps 7-10: Excel export, cover letters, email delivery, feedback processing"
    )
    
    parser.add_argument(
        "--force-good-match", 
        type=str,
        help="Force a specific job ID to have a 'Good' match for testing cover letter generation"
    )
    
    parser.add_argument(
        "--force-good-matches", 
        type=str,
        help="Force multiple job IDs to have 'Good' matches (comma-separated)"
    )
    
    parser.add_argument(
        "--demo-mode",
        action="store_true",
        help="Enable demo mode for generating cover letters for HR testing"
    )
    
    parser.add_argument(
        "--reviewer-name", 
        default="xai",
        help="Name of reviewer for email and feedback processing (default: xai)"
    )
    
    parser.add_argument(
        "--reviewer-email",
        help="Email address of reviewer (overrides config)"
    )
    
    parser.add_argument(
        "--feedback-daemon", 
        action="store_true",
        help="Run feedback processing as daemon (continuous monitoring)"
    )
    
    parser.add_argument(
        "--feedback-interval", 
        type=int, 
        default=15,
        help="Check interval in minutes for daemon mode (default: 15)"
    )
    
    # Job scanner arguments
    parser.add_argument(
        "--run-job-scanner",
        action="store_true",
        help="Run job ID scanner to discover new or missing jobs"
    )
    
    parser.add_argument(
        "--scan-specific-ranges",
        action="store_true",
        help="Scan specific job ID ranges that are likely to contain missing jobs"
    )
    
    parser.add_argument(
        "--scan-start-id",
        type=int,
        help="Start ID for custom job scanner range"
    )
    
    parser.add_argument(
        "--scan-end-id",
        type=int,
        help="End ID for custom job scanner range"
    )
    
    parser.add_argument(
        "--scan-concurrent",
        action="store_true",
        help="Use concurrent processing for job scanning"
    )
    
    parser.add_argument(
        "--scan-workers",
        type=int,
        default=5,
        help="Maximum number of concurrent workers for job scanning (default: 5)"
    )
    
    parser.add_argument(
        "--reset-progress",
        action="store_true",
        help="Reset the job scan progress tracker before running the pipeline."
    )
    
    return parser.parse_args()

# Export for external use
__all__ = ['parse_args']
