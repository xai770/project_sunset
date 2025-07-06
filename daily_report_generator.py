#!/usr/bin/env python3
"""
Daily Job Analysis Report Generator - Clean Entry Point
=====================================================

Professional 27-Column Excel Reports using modular architecture.
Creates standardized reports following Sandy's Golden Rules.

This is a clean entry point that uses the refactored modular components
from the daily_report_pipeline package.
"""

import sys
import argparse
from pathlib import Path

# Add the sandy root to path for imports
sys.path.append('/home/xai/Documents/sandy')

from daily_report_pipeline.reporting.report_generator import ReportGenerator
from core.enhanced_job_fetcher import EnhancedJobFetcher

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Generate daily job analysis report")
    parser.add_argument('--limit', type=int, default=5,
                      help='Number of jobs to process (default: 5)')
    parser.add_argument('--allow-processed', action='store_true',
                      help='Allow including already processed jobs if needed')
    return parser.parse_args()

def main():
    """Main function for daily report generation"""
    args = parse_args()
    
    print("🚀 Daily Job Analysis Report Generator")
    print("=" * 50)
    print("Using modular architecture from daily_report_pipeline/")
    print("✅ Content Extraction Specialist v3.4")
    print("✅ Location Validation Specialist v2.0 (Enhanced LLM)")
    print("✅ Text Summarization Specialist")
    print("=" * 50)
    
    # Initialize components
    generator = ReportGenerator()
    fetcher = EnhancedJobFetcher()
    
    # Check if we need to fetch more jobs
    available_jobs = generator.count_available_jobs()
    if available_jobs < args.limit:
        needed_jobs = args.limit - available_jobs
        print(f"ℹ️ Only {available_jobs} jobs available, fetching {needed_jobs} more...")
        
        fetched = fetcher.fetch_jobs(
            max_jobs=needed_jobs,
            allow_processed=args.allow_processed
        )
        
        if fetched:
            print(f"✅ Successfully fetched {len(fetched)} new jobs")
        else:
            print("⚠️ Could not fetch additional jobs")
            if not args.allow_processed:
                print("   Try running with --allow-processed to include processed jobs")
    
    # Generate the report
    generator.generate_report(limit=args.limit)

if __name__ == "__main__":
    main()
