#!/usr/bin/env python3
"""
Project Sunset Phase 7 - Complete Pipeline Entry Point
====================================================

Complete, streamlined entry point for the full modernized pipeline including:
- Job fetching (JobFetcherP5)
- Job processing with specialists (JobMatchingAPI)
- Excel export (JMFS format)
- Cover letter generation
- Email delivery

Using specialists for ALL LLM interactions.
"""

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import DirectSpecialistManager, JobMatchingAPI
from core.job_fetcher_p5 import JobFetcherP5

def health_check():
    """Perform system health check"""
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Project Sunset Phase 7 - Starting Complete Pipeline")
    
    try:
        # Initialize modern API
        api = JobMatchingAPI()
        
        # Health check
        health = api.health_check()
        logger.info(f"✅ API Health: {health['status']}")
        logger.info(f"📊 Available Specialists: {health.get('available_specialists', 0)}")
        
        if health['status'] == 'healthy':
            logger.info("🎉 Project Sunset Phase 7 - Complete Pipeline Ready!")
            return True
        else:
            logger.error(f"❌ Health check failed: {health.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        return False

def fetch_jobs(max_jobs=20, quick=False):
    """Fetch jobs using Phase 5 job fetcher"""
    logger = logging.getLogger(__name__)
    logger.info("=== FETCHING JOBS (Phase 7) ===")
    
    try:
        fetcher = JobFetcherP5()
        job_count = 5 if quick else max_jobs
        result = fetcher.run_full_fetch_and_process(max_jobs=job_count)
        
        if result['success']:
            logger.info(f"✅ Successfully fetched {result['jobs_saved']} jobs")
            return result['jobs_saved']
        else:
            logger.error(f"❌ Job fetching failed: {result.get('error', 'Unknown error')}")
            return 0
            
    except Exception as e:
        logger.error(f"❌ Error during job fetching: {e}")
        return 0

def process_jobs_with_specialists(job_ids=None):
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
            import json
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
        for job_id in jobs_to_process:
            logger.info(f"🔄 Processing job {job_id} with specialists...")
            try:
                job_result = process_job(str(job_id), cv_text, num_runs=3, dump_input=False)
                if "error" not in job_result:
                    update_job_json(str(job_id), job_result)
                    processed_jobs.append(job_id)
                    logger.info(f"✅ Job {job_id} processed successfully")
                else:
                    logger.warning(f"⚠️ Job {job_id} processing had issues: {job_result.get('error', 'Unknown')}")
            except Exception as e:
                logger.error(f"❌ Error processing job {job_id}: {e}")
        
        logger.info(f"🎉 Successfully processed {len(processed_jobs)} jobs with specialists")
        return processed_jobs
        
    except Exception as e:
        logger.error(f"❌ Error during job processing with specialists: {e}")
        return []

def export_jobs_to_excel(feedback_system=True, reviewer_name="xai"):
    """Export jobs to Excel using the JMFS feedback system format"""
    logger = logging.getLogger(__name__)
    logger.info("=== EXPORTING JOBS TO EXCEL (Phase 7) ===")
    
    try:
        from run_pipeline.export_job_matches import export_job_matches
        
        # Export with feedback system enabled
        excel_path = export_job_matches(
            output_format='excel',
            output_file=None,  # Auto-generate filename
            job_ids=None,  # Export all processed jobs
            feedback_system=feedback_system,
            reviewer_name=reviewer_name
        )
        
        if excel_path:
            logger.info(f"✅ Excel export successful: {excel_path}")
            return excel_path
        else:
            logger.error("❌ Excel export failed - no data to export")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error during Excel export: {e}")
        return None

def generate_cover_letters_for_good_matches(excel_path):
    """Generate cover letters for jobs marked as 'Good' matches"""
    logger = logging.getLogger(__name__)
    logger.info("=== GENERATING COVER LETTERS (Phase 7) ===")
    
    try:
        # Use the existing cover letter generation system
        from run_pipeline.process_excel_cover_letters import main as process_cover_letters
        
        # Call the cover letter processor with the Excel file
        # This system uses specialists internally for LLM work
        cover_letter_results = process_cover_letters(
            excel_path=excel_path,
            update_excel_log=True
        )
        
        if cover_letter_results:
            logger.info(f"✅ Generated cover letters for good matches")
            return cover_letter_results
        else:
            logger.warning("⚠️ No cover letters generated (no 'Good' matches found)")
            return []
            
    except Exception as e:
        logger.error(f"❌ Error during cover letter generation: {e}")
        return []

def send_email_package(excel_path, cover_letters, reviewer_email=None):
    """Send Excel file and cover letters via email"""
    logger = logging.getLogger(__name__)
    logger.info("=== SENDING EMAIL PACKAGE (Phase 7) ===")
    
    try:
        # Try to import email sender
        try:
            from run_pipeline.email_sender import EmailSender, CONFIG
        except ImportError:
            logger.warning("📧 Email sender module not found - email delivery skipped")
            return True  # Non-critical failure
        
        # Prepare email
        reviewer_email = reviewer_email or CONFIG.get('work_email')
        if not reviewer_email:
            logger.warning("📧 No reviewer email configured - email delivery skipped")
            return True
        
        # Prepare attachments
        attachments = [excel_path]
        if cover_letters:
            # Add cover letter files to attachments
            import glob
            cover_letter_dir = project_root / "docs" / "cover_letters"
            if cover_letter_dir.exists():
                cover_letter_files = list(cover_letter_dir.glob("cover_letter_*.md"))
                attachments.extend([str(f) for f in cover_letter_files])
        
        # Send email
        sender = EmailSender(CONFIG)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        subject = f"xai job_matches_{timestamp}.xlsx"
        body = f"""Hi!

Attached are your job matches for review:

- Excel file: {Path(excel_path).name}
- {len(cover_letters)} cover letters generated for 'Good' matches

Please review the matches and add any feedback in the 'reviewer_feedback' column if needed.

Best regards,
Project Sunset Phase 7 Pipeline
"""
        
        success = sender.send_email(reviewer_email, subject, body, attachments)
        
        if success:
            logger.info(f"✅ Successfully emailed {len(attachments)} files to {reviewer_email}")
            return True
        else:
            logger.warning("⚠️ Email delivery failed - continuing pipeline")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during email delivery: {e}")
        return False

def run_complete_pipeline(args):
    """Run the complete Phase 7 pipeline"""
    start_time = datetime.now()
    logger = logging.getLogger(__name__)
    
    logger.info(f"=== STARTING PROJECT SUNSET PHASE 7 COMPLETE PIPELINE ===")
    logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = True
    excel_path = None
    cover_letters = []
    
    # Health check first
    if not health_check():
        logger.error("❌ Health check failed, aborting pipeline")
        return 1
    
    # Step 1: Fetch jobs if requested
    if args.fetch_jobs:
        jobs_fetched = fetch_jobs(max_jobs=args.max_jobs, quick=args.quick)
        if jobs_fetched == 0:
            logger.warning("⚠️ No jobs fetched")
            success = False
    
    # Step 2: Process jobs with specialists if requested
    if args.process_jobs:
        processed_jobs = process_jobs_with_specialists(job_ids=args.job_ids)
        if not processed_jobs:
            logger.error("❌ Job processing with specialists failed")
            success = False
    
    # Step 3: Export to Excel if requested
    if args.export_excel:
        excel_path = export_jobs_to_excel(feedback_system=True, reviewer_name="xai")
        if not excel_path:
            logger.error("❌ Excel export failed")
            success = False
    
    # Step 4: Generate cover letters if requested and we have Excel
    if args.generate_cover_letters and excel_path:
        cover_letters = generate_cover_letters_for_good_matches(excel_path)
        # Note: Cover letters are optional, so don't fail pipeline if none generated
    
    # Step 5: Send email if requested and we have something to send
    if args.send_email and excel_path:
        email_success = send_email_package(excel_path, cover_letters)
        if not email_success:
            logger.warning("⚠️ Email delivery failed, but pipeline continues")
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    if success:
        logger.info(f"✅ PHASE 7 COMPLETE PIPELINE FINISHED SUCCESSFULLY")
        logger.info(f"📊 Results:")
        if excel_path:
            logger.info(f"  📋 Excel file: {excel_path}")
        if cover_letters:
            logger.info(f"  ✍️ Cover letters: {len(cover_letters)} generated")
        if args.send_email:
            logger.info(f"  📧 Email delivery: {'✅ Sent' if email_success else '⚠️ Failed'}")
    else:
        logger.error(f"❌ PHASE 7 PIPELINE COMPLETED WITH ERRORS")
    
    logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Total runtime: {duration}")
    
    return 0 if success else 1

def run_pipeline(args):
    """Compatibility wrapper for legacy run_pipeline function"""
    logger = logging.getLogger(__name__)
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
    """Main entry point for Project Sunset Phase 7"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
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
    
    # Job options
    parser.add_argument("--max-jobs", type=int, default=20, help="Maximum jobs to fetch")
    parser.add_argument("--quick", action="store_true", help="Quick mode (5 jobs)")
    parser.add_argument("--job-ids", nargs="*", type=str, help="Specific job IDs to process")
    
    args = parser.parse_args()
    
    # Default behavior
    if not any([args.health_check, args.fetch_jobs, args.process_jobs, args.export_excel, 
                args.generate_cover_letters, args.send_email, args.run_all]):
        args.health_check = True
    
    # Run health check only
    if args.health_check and not any([args.fetch_jobs, args.process_jobs, args.export_excel, 
                                      args.generate_cover_letters, args.send_email, args.run_all]):
        return 0 if health_check() else 1
    
    # Run pipeline
    return run_pipeline(args)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
