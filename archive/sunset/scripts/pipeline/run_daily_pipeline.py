#!/usr/bin/env python3
"""
Daily Pipeline Runner for Project Sunset
========================================

This script runs the complete daily job search and analysis pipeline:
1. Backup existing postings
2. Fetch new jobs from Deutsche Bank (Frankfurt focus)
3. Analyze jobs with LLM specialists
4. Export results to Excel with feedback system format
5. Generate cover letters for good matches
6. Package and email results

Usage:
    python run_daily_pipeline.py [--test] [--max-jobs N] [--no-email]
"""

import sys
import os
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
import shutil

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import pipeline components
from core.enhanced_job_fetcher import EnhancedJobFetcher
from main import load_search_criteria
from run_pipeline.export_job_matches import export_job_matches

def setup_logging():
    """Setup logging for the daily pipeline"""
    log_dir = Path("logs/daily_pipeline")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"daily_pipeline_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def backup_postings():
    """Backup existing job postings"""
    postings_dir = Path("data/postings")
    if not postings_dir.exists():
        postings_dir.mkdir(parents=True, exist_ok=True)
        return None
    
    # Check if directory has any files
    files = list(postings_dir.glob("*.json"))
    if not files:
        return None
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"data/postings_BACKUP_{timestamp}")
    
    shutil.copytree(postings_dir, backup_dir)
    return backup_dir

def clear_postings():
    """Clear existing job postings"""
    postings_dir = Path("data/postings")
    if postings_dir.exists():
        for file in postings_dir.glob("*.json"):
            file.unlink()

def recovery_step(max_recovery=10):
    """Step 0: Auto-recovery of missing jobs"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Step 0: Auto-recovery of missing jobs")
    
    try:
        from main import detect_and_recover_missing_jobs
        recovered = detect_and_recover_missing_jobs(
            max_recovery=max_recovery, 
            enable_recovery=True
        )
        
        if recovered > 0:
            logger.info(f"✅ Auto-recovery successful: {recovered} jobs recovered")
        else:
            logger.info("✅ No missing jobs detected")
        
        return recovered
        
    except Exception as e:
        logger.error(f"❌ Error during auto-recovery: {e}")
        # Don't fail the pipeline if recovery fails
        return 0

def fetch_jobs_step(max_jobs=10, test_mode=False):
    """Step 1: Fetch jobs from Deutsche Bank"""
    logger = logging.getLogger(__name__)
    logger.info("🚀 Step 1: Fetching jobs from Deutsche Bank")
    
    try:
        # Load search criteria
        search_criteria = load_search_criteria('xai_frankfurt_focus')
        
        # Initialize enhanced job fetcher
        fetcher = EnhancedJobFetcher()
        
        # Fetch jobs with Frankfurt filtering
        jobs = fetcher.fetch_jobs(
            max_jobs=max_jobs, 
            quick_mode=test_mode,
            search_criteria=search_criteria
        )
        
        logger.info(f"✅ Successfully fetched {len(jobs)} jobs")
        return jobs
        
    except Exception as e:
        logger.error(f"❌ Error fetching jobs: {e}")
        raise

def analyze_jobs_step():
    """Step 2: Analyze jobs with LLM specialists"""
    logger = logging.getLogger(__name__)
    logger.info("🧠 Step 2: Analyzing jobs with LLM specialists")
    
    try:
        # Import and run job matching
        from main import process_jobs_with_specialists
        result = process_jobs_with_specialists()
        
        logger.info("✅ Job analysis completed")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error analyzing jobs: {e}")
        raise

def export_jobs_step():
    """Step 3: Export jobs to Excel with feedback system format"""
    logger = logging.getLogger(__name__)
    logger.info("📊 Step 3: Exporting jobs to Excel")
    
    try:
        output_file = export_job_matches(
            output_format='excel',
            feedback_system=True,
            reviewer_name="xai"
        )
        
        if output_file:
            logger.info(f"✅ Excel export completed: {output_file}")
            return output_file
        else:
            logger.warning("⚠️ No jobs to export")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error exporting jobs: {e}")
        raise

def generate_cover_letters_step(excel_path):
    """Step 4: Generate cover letters for good matches"""
    logger = logging.getLogger(__name__)
    logger.info("✍️ Step 4: Generating cover letters")
    
    try:
        from main import generate_cover_letters_for_good_matches
        cover_letters = generate_cover_letters_for_good_matches(excel_path)
        
        logger.info(f"✅ Generated {len(cover_letters) if cover_letters else 0} cover letters")
        return cover_letters
        
    except Exception as e:
        logger.error(f"❌ Error generating cover letters: {e}")
        raise

def send_email_step(excel_path, cover_letters, no_email=False):
    """Step 5: Send email package with results"""
    logger = logging.getLogger(__name__)
    logger.info("📧 Step 5: Sending email package")
    
    if no_email:
        logger.info("📧 Email sending skipped (--no-email flag)")
        return
    
    try:
        from main import send_email_package
        result = send_email_package(excel_path, cover_letters)
        
        logger.info("✅ Email package sent successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error sending email: {e}")
        raise

def run_daily_pipeline(max_jobs=10, test_mode=False, no_email=False):
    """Run the complete daily pipeline"""
    logger = setup_logging()
    
    logger.info("🌅 Starting Daily Pipeline for Project Sunset")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    recovered_jobs = 0
    
    try:
        # Step 0: Auto-recovery of missing jobs
        recovered_jobs = recovery_step(max_recovery=10)
        
        # Backup existing postings
        backup_dir = backup_postings()
        if backup_dir:
            logger.info(f"💾 Backed up existing postings to: {backup_dir}")
        
        # Clear postings directory
        clear_postings()
        logger.info("🧹 Cleared postings directory")
        
        # Step 1: Fetch jobs
        jobs = fetch_jobs_step(max_jobs, test_mode)
        
        if not jobs:
            logger.warning("⚠️ No jobs fetched, stopping pipeline")
            return
        
        # Step 2: Analyze jobs
        analyze_jobs_step()
        
        # Step 3: Export to Excel
        excel_path = export_jobs_step()
        
        if not excel_path:
            logger.warning("⚠️ No Excel file generated, stopping pipeline")
            return
        
        # Step 4: Generate cover letters
        cover_letters = generate_cover_letters_step(excel_path)
        
        # Step 5: Send email package
        send_email_step(excel_path, cover_letters, no_email)
        
        # Pipeline completed successfully
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("=" * 60)
        logger.info(f"🎉 Daily Pipeline completed successfully!")
        logger.info(f"⏱️ Total duration: {duration}")
        if recovered_jobs > 0:
            logger.info(f"🔧 Jobs recovered: {recovered_jobs}")
        logger.info(f"📊 Jobs fetched: {len(jobs)}")
        logger.info(f"📄 Excel file: {excel_path}")
        logger.info(f"✍️ Cover letters: {len(cover_letters) if cover_letters else 0}")
        
    except Exception as e:
        logger.error(f"💥 Pipeline failed: {e}")
        raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run the daily job search pipeline")
    parser.add_argument("--test", action="store_true", 
                       help="Run in test mode (fewer jobs, quick processing)")
    parser.add_argument("--max-jobs", type=int, default=10,
                       help="Maximum number of jobs to fetch (default: 10)")
    parser.add_argument("--no-email", action="store_true",
                       help="Skip email sending step")
    
    args = parser.parse_args()
    
    # Run the pipeline
    run_daily_pipeline(
        max_jobs=args.max_jobs,
        test_mode=args.test,
        no_email=args.no_email
    )

if __name__ == "__main__":
    main()