#!/usr/bin/env python3
"""
Simple Pipeline Orchestrator

A simplified version that orchestrates the pipeline steps without complex imports.
This acts as a clean interface to the existing functionality.
"""

import logging
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

def run_complete_pipeline(args) -> int:
    """Run the complete Phase 7 pipeline using existing functions"""
    start_time = datetime.now()
    logger.info(f"=== STARTING PROJECT SUNSET PHASE 7 COMPLETE PIPELINE ===")
    logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = True
    excel_path = None
    cover_letters = []
    email_success = False
    recovered_jobs = 0
    
    try:
        # Import all functions locally to avoid import issues
        from scripts.pipeline.modules.health_check import health_check
        
        # Health check first
        if not health_check():
            logger.error("❌ Health check failed, aborting pipeline")
            return 1
        
        # Step 0: Auto-recovery of missing jobs (always enabled unless disabled)
        if not getattr(args, 'no_recovery', False):
            from scripts.pipeline.modules.job_recovery import detect_and_recover_missing_jobs
            logger.info("🔧 Starting automatic missing job recovery...")
            recovery_limit = getattr(args, 'max_recovery', 25)
            recovered_jobs = detect_and_recover_missing_jobs(
                max_recovery=recovery_limit, 
                enable_recovery=True
            )
            if recovered_jobs > 0:
                logger.info(f"🎉 Auto-recovery successful: {recovered_jobs} jobs recovered")
            else:
                logger.info("✅ No missing jobs detected")
        
        # Step 1: Fetch jobs if requested
        if args.fetch_jobs:
            from scripts.pipeline.modules.job_fetcher import fetch_jobs
            force_reprocess = getattr(args, 'force_reprocess', False)
            jobs_fetched = fetch_jobs(
                max_jobs=args.max_jobs, 
                quick=args.quick, 
                profile_name=args.profile,
                force_reprocess=force_reprocess
            )
            if jobs_fetched == 0:
                logger.warning("⚠️ No jobs fetched")
                success = False
        
        # Step 2: Process jobs with specialists if requested
        if args.process_jobs:
            from scripts.pipeline.modules.job_processor import process_jobs_with_specialists
            processed_jobs = process_jobs_with_specialists(job_ids=args.job_ids)
            if not processed_jobs:
                logger.error("❌ Job processing with specialists failed")
                success = False
        
        # Step 3: Export to Excel if requested
        if args.export_excel:
            # Bridge job data structure for compatibility
            from scripts.pipeline.modules.data_bridge import bridge_job_data_structure
            bridge_job_data_structure()
            
            from scripts.pipeline.modules.excel_exporter import export_jobs_to_excel
            excel_path = export_jobs_to_excel(feedback_system=True, reviewer_name="xai")
            if not excel_path:
                logger.error("❌ Excel export failed")
                success = False
        
        # Step 4: Generate cover letters if requested and we have Excel
        if args.generate_cover_letters and excel_path:
            from scripts.pipeline.modules.cover_letter_generator import generate_cover_letters_for_good_matches
            cover_letter_result = generate_cover_letters_for_good_matches(excel_path)
            # Ensure cover_letters is always a list for type safety
            if isinstance(cover_letter_result, list):
                cover_letters = cover_letter_result
            else:
                cover_letters = []  # If it returned an int (count), use empty list
            # Note: Cover letters are optional, so don't fail pipeline if none generated
        else:
            cover_letters = []
        
        # Step 5: Send email if requested and we have something to send
        if args.send_email and excel_path:
            from scripts.pipeline.modules.email_sender import send_email_package
            email_success = send_email_package(excel_path, cover_letters)
            if not email_success:
                logger.warning("⚠️ Email delivery failed, but pipeline continues")
        else:
            email_success = False
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if success:
            logger.info(f"✅ PHASE 7 COMPLETE PIPELINE FINISHED SUCCESSFULLY")
            logger.info(f"📊 Results:")
            if recovered_jobs > 0:
                logger.info(f"  🔧 Recovery: {recovered_jobs} missing jobs recovered")
            if excel_path:
                logger.info(f"  📋 Excel file: {excel_path}")
            if cover_letters:
                # Handle both integer count and list types
                if isinstance(cover_letters, int):
                    logger.info(f"  ✍️ Cover letters: {cover_letters} generated")
                else:
                    logger.info(f"  ✍️ Cover letters: {len(cover_letters)} generated")
            if args.send_email:
                logger.info(f"  📧 Email delivery: {'✅ Sent' if email_success else '⚠️ Failed'}")
        else:
            logger.error(f"❌ PHASE 7 PIPELINE COMPLETED WITH ERRORS")
        
        logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Total runtime: {duration}")
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed with exception: {e}")
        return 1

def run_pipeline(args):
    """Compatibility wrapper for legacy run_pipeline function"""
    logger.info("🔄 Running pipeline in compatibility mode...")
    
    # If run-all is specified, enable all Phase 7 steps
    if args.run_all:
        args.fetch_jobs = True
        args.process_jobs = True
        args.export_excel = True
        args.generate_cover_letters = True
        args.send_email = True
    
    return run_complete_pipeline(args)

def main():
    """Main entry point for Project Sunset Phase 7 with beautiful CLI"""
    
    # Display beautiful banner
    from core.beautiful_cli import print_sunset_banner
    print_sunset_banner()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load and display configuration
    from core.config_manager import get_config, display_config_banner
    config = get_config()
    if config.debug:
        display_config_banner()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Project Sunset Phase 7 - Complete Pipeline")
    
    # Pipeline operations
    parser.add_argument("--health-check", action="store_true", help="Run health check only")
    parser.add_argument("--fetch-jobs", action="store_true", help="Fetch jobs")
    parser.add_argument("--process-jobs", action="store_true", help="Process jobs with specialists") 
    parser.add_argument("--export-excel", action="store_true", help="Export jobs to Excel (JMFS format)")
    parser.add_argument("--generate-cover-letters", action="store_true", help="Generate cover letters for good matches")
    parser.add_argument("--send-email", action="store_true", help="Send Excel and cover letters via email")
    parser.add_argument("--run-all", action="store_true", help="Run complete pipeline (all steps)")
    
    # Recovery options
    parser.add_argument("--no-recovery", action="store_true", help="Disable automatic missing job recovery")
    parser.add_argument("--max-recovery", type=int, default=25, help="Maximum jobs to recover per run (default: 25)")
    parser.add_argument("--recovery-only", action="store_true", help="Run recovery only (no other pipeline steps)")
    
    # Job options
    parser.add_argument("--max-jobs", type=int, default=60, help="Maximum jobs to fetch (default: 60 for Frankfurt)")
    parser.add_argument("--quick", action="store_true", help="Quick mode (5 jobs)")
    parser.add_argument("--job-ids", nargs="*", type=str, help="Specific job IDs to process")
    parser.add_argument("--profile", type=str, default="xai_frankfurt_focus", help="Search criteria profile to use")
    parser.add_argument("--force-reprocess", action="store_true", help="Force reprocessing of existing jobs (overwrite AI analysis)")
    
    args = parser.parse_args()
    
    # Default behavior
    if not any([args.health_check, args.fetch_jobs, args.process_jobs, args.export_excel, 
                args.generate_cover_letters, args.send_email, args.run_all, args.recovery_only]):
        args.health_check = True
    
    # Run recovery only
    if args.recovery_only:
        logger.info("🔧 Running recovery-only mode...")
        
        from scripts.pipeline.modules.health_check import health_check
        if not health_check():
            logger.error("❌ Health check failed")
            return 1
        
        from scripts.pipeline.modules.job_recovery import detect_and_recover_missing_jobs
        recovered = detect_and_recover_missing_jobs(
            max_recovery=args.max_recovery, 
            enable_recovery=True
        )
        
        if recovered > 0:
            logger.info(f"✅ Recovery complete: {recovered} jobs recovered")
            return 0
        else:
            logger.info("✅ No missing jobs found")
            return 0
    
    # Run health check only
    if args.health_check and not any([args.fetch_jobs, args.process_jobs, args.export_excel, 
                                      args.generate_cover_letters, args.send_email, args.run_all]):
        from scripts.pipeline.modules.health_check import health_check
        return 0 if health_check() else 1
    
    # Run pipeline
    return run_pipeline(args)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
