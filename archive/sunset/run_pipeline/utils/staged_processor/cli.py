#!/usr/bin/env python3
"""
Command-line interface for staged job description processing

Usage:
  python -m run_pipeline.utils.staged_processor.cli [--job-ids JOB_IDS] [--model MODEL]
                                                 [--dry-run] [--output-format FORMAT]

Options:
  --job-ids JOB_IDS      Comma-separated list of job IDs to process
  --model MODEL          Model to use for extraction (default: llama3.2:latest)
  --dry-run              Identify and report issues without making changes
  --output-format        Format for output: 'text' or 'json' (default: text)
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Add the project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

# Import the main processor functions
from run_pipeline.utils.staged_processor.processor import process_jobs
from run_pipeline.utils.staged_processor.utils import logger

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Process job descriptions in stages"
    )
    parser.add_argument(
        "--job-ids",
        type=str,
        help="Comma-separated list of job IDs to process"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="llama3.2:latest",
        help="Model to use for extraction"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Identify and report issues without making changes"
    )
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Format for output"
    )
    
    args = parser.parse_args()
    
    # Parse job IDs
    job_ids = None
    if args.job_ids:
        job_ids = args.job_ids.split(',')
    
    logger.info(f"Starting staged job description processing with model {args.model}")
    if args.dry_run:
        logger.info("Dry run mode: No changes will be made")
    
    processed, success, failure = process_jobs(
        job_ids=job_ids,
        model=args.model,
        dry_run=args.dry_run,
        output_format=args.output_format
    )
    
    logger.info(f"Job processing summary:")
    logger.info(f"- Total jobs processed: {processed}")
    logger.info(f"- Successfully processed: {success}")
    logger.info(f"- Failed to process: {failure}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
