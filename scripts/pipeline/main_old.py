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

Enhanced with beautiful CLI interface and centralized configuration.
Using specialists for ALL LLM interactions.

This file now uses a modular architecture with organized components.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.config_manager import get_config, display_config_banner
from core.beautiful_cli import print_sunset_banner

# Import the modular pipeline components
from .modules.pipeline_orchestrator import main as orchestrator_main

def load_search_criteria(profile_name: str = "xai_frankfurt_focus") -> dict:
    """Load search criteria from config file"""
    config_path = project_root / "config" / "search_criteria.json"
    
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        profiles = config_data.get("search_profiles", {})
        if profile_name not in profiles:
            print_warning(f"Profile '{profile_name}' not found, using default")
            profile_name = config_data.get("global_settings", {}).get("default_profile", "xai_frankfurt_focus")
        
        profile = profiles.get(profile_name, {})
        if not profile.get("active", False):
            print_warning(f"Profile '{profile_name}' is not active")
        
        print_info(f"Loaded search criteria profile: {profile_name}")
        print_info(f"Description: {profile.get('description', 'No description')}")
        
        return profile
        
    except Exception as e:
        print_error(f"Failed to load search criteria: {e}")
        return {}

def health_check():
    """Perform system health check with beautiful output"""
    config = get_config()
    
    print_info("Starting Project Sunset Phase 7 health check...")
    show_progress_spinner("Checking system health", 1.5)
    
    try:
        # Initialize modern API
        api = JobMatchingAPI()
        
        # Health check
        health = api.health_check()
        print_info(f"API Health: {health['status']}")
        print_info(f"Available Specialists: {health.get('available_specialists', 0)}")
        
        if health['status'] == 'healthy':
            print_success("Project Sunset Phase 7 - Complete Pipeline Ready!")
            return True
        else:
            print_error(f"Health check failed: {health.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print_error(f"Health check failed with exception: {e}")
        return False
        logger.error(f"❌ Startup failed: {e}")
        return False

def fetch_jobs(max_jobs=60, quick=False, profile_name="xai_frankfurt_focus"):
    """Fetch jobs using the beautiful enhanced fetcher with search criteria"""
    logger = logging.getLogger(__name__)
    logger.info("=== FETCHING JOBS (Phase 7) ===")
    
    print_info("Starting beautiful job fetching with integrated search criteria...")
    
    # Load search criteria
    search_criteria = load_search_criteria(profile_name)
    
    # Extract max jobs from search criteria if available
    criteria_max_jobs = search_criteria.get("fetching", {}).get("max_jobs_per_run", max_jobs)
    final_max_jobs = max_jobs if max_jobs > criteria_max_jobs else criteria_max_jobs
    
    # For Frankfurt focus, we want to get ALL Frankfurt jobs (~60)
    if "frankfurt" in profile_name.lower():
        final_max_jobs = max(final_max_jobs, 60)  # Ensure we get at least 60 jobs for Frankfurt
    
    show_progress_spinner("Initializing enhanced job fetcher...", 1.0)
    
    try:
        # Use the enhanced fetcher with beautiful JSON structure
        fetcher = EnhancedJobFetcher()
        job_count = 5 if quick else final_max_jobs
        
        print_info(f"Fetching up to {job_count} jobs using profile '{profile_name}' (quick_mode: {quick})")
        print_info(f"Search criteria: {search_criteria.get('description', 'No description')}")
        
        jobs = fetcher.fetch_jobs(max_jobs=job_count, quick_mode=quick, search_criteria=search_criteria)
        
        if jobs:
            print_success(f"Successfully fetched {len(jobs)} jobs with beautiful structure!")
            
            # Display summary using our beautiful CLI
            job_summary_data = []
            for job in jobs:
                job_summary_data.append({
                    'job_id': job['job_metadata']['job_id'],
                    'web_details': {'position_title': job['job_content']['title']},
                    'llama32_evaluation': {},  # Not evaluated yet
                    'search_details': {
                        'PositionLocation': [{
                            'CityName': job['job_content']['location']['city'],
                            'CountryName': job['job_content']['location']['country']
                        }]
                    }
                })
            
            display_job_summary(job_summary_data)
            logger.info(f"✅ Successfully fetched {len(jobs)} jobs using profile '{profile_name}'")
            return len(jobs)
        else:
            print_warning("No jobs were fetched")
            logger.warning("⚠️ No jobs were fetched") 
            return 0
            
    except Exception as e:
        logger.error(f"❌ Error during job fetching: {e}")
        print_error(f"Job fetching failed: {e}")
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
            job_id_col='Job ID',  # Fixed: Use correct column name from Excel
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

def detect_and_recover_missing_jobs(max_recovery=25, enable_recovery=True):
    """
    Detect missing job files and recover them automatically
    This makes the pipeline self-healing and robust
    """
    logger = logging.getLogger(__name__)
    logger.info("=== MISSING JOB DETECTION & RECOVERY ===")
    
    if not enable_recovery:
        logger.info("🔧 Job recovery is disabled, skipping...")
        return 0
    
    try:
        # Load progress data to see what jobs should exist
        progress_file = project_root / "data" / "job_scans" / "search_api_scan_progress.json"
        if not progress_file.exists():
            logger.info("📁 No scan progress file found, skipping recovery")
            return 0
            
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        
        # Get list of jobs that should exist
        progress_ids = set(str(job_id) for job_id in progress.get('jobs_processed', []))
        
        # Get list of jobs that actually exist
        data_dir = project_root / "data" / "postings"
        job_files = list(data_dir.glob('job*.json'))
        file_ids = set()
        for f in job_files:
            job_id = f.stem.replace('job', '')
            file_ids.add(job_id)
        
        # Find missing jobs
        missing_files = progress_ids - file_ids
        missing_count = len(missing_files)
        
        if missing_count == 0:
            logger.info("✅ No missing job files detected - all good!")
            return 0
        
        logger.info(f"🔍 Detected {missing_count} missing job files")
        
        # Limit recovery to avoid performance issues
        recovery_limit = min(missing_count, max_recovery)
        if missing_count > max_recovery:
            logger.info(f"⚡ Limiting recovery to {max_recovery} jobs for performance")
        
        # Sort missing IDs and take the most recent ones first
        missing_sorted = sorted([int(x) for x in missing_files], reverse=True)
        jobs_to_recover = missing_sorted[:recovery_limit]
        
        logger.info(f"🔄 Attempting to recover {len(jobs_to_recover)} missing jobs...")
        
        # Initialize the enhanced job fetcher for recovery
        fetcher = EnhancedJobFetcher()
        
        recovered_count = 0
        failed_count = 0
        
        for i, job_id in enumerate(jobs_to_recover, 1):
            try:
                logger.info(f"🔄 Recovering job {i}/{len(jobs_to_recover)}: {job_id}")
                
                # Try to fetch the job description
                job_description = fetcher.fetch_job_description(str(job_id))
                
                if job_description:
                    # Create a simple job structure for recovery
                    recovered_job = {
                        "job_metadata": {
                            "job_id": str(job_id),
                            "version": "1.0",
                            "created_at": datetime.now().isoformat(),
                            "last_modified": datetime.now().isoformat(),
                            "source": "recovery_system",
                            "processor": "pipeline_auto_recovery",
                            "status": "recovered"
                        },
                        "job_content": {
                            "title": f"Recovered Job {job_id}",
                            "description": job_description,
                            "requirements": [],
                            "location": {
                                "city": "Frankfurt am Main",
                                "country": "Germany",
                                "remote_options": False
                            },
                            "employment_details": {
                                "type": "Full-time",
                                "schedule": "Regular",
                                "career_level": "Professional"
                            },
                            "organization": {
                                "name": "Deutsche Bank",
                                "division": "Unknown"
                            }
                        },
                        "evaluation_results": {
                            "cv_to_role_match": None,
                            "match_confidence": None
                        },
                        "processing_log": [
                            {
                                "timestamp": datetime.now().isoformat(),
                                "action": "auto_recovery",
                                "processor": "pipeline_recovery_system",
                                "status": "success",
                                "details": f"Automatically recovered missing job {job_id}"
                            }
                        ],
                        "raw_source_data": {
                            "description_source": "recovery_fetch"
                        }
                    }
                    
                    # Save the recovered job
                    job_file = data_dir / f"job{job_id}.json"
                    with open(job_file, 'w', encoding='utf-8') as f:
                        json.dump(recovered_job, f, indent=2, ensure_ascii=False)
                    
                    recovered_count += 1
                    logger.info(f"✅ Successfully recovered job {job_id}")
                    
                else:
                    failed_count += 1
                    logger.warning(f"⚠️ Could not recover job {job_id} - may no longer exist")
                
                # Add a small delay to be nice to the API
                import time
                time.sleep(0.5)
                
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Error recovering job {job_id}: {e}")
        
        # Summary
        logger.info(f"🎉 Recovery complete: {recovered_count} recovered, {failed_count} failed")
        
        if recovered_count > 0:
            logger.info(f"✅ Successfully recovered {recovered_count} missing jobs!")
            logger.info(f"📊 Recovery rate: {recovered_count}/{len(jobs_to_recover)} ({recovered_count/len(jobs_to_recover)*100:.1f}%)")
        
        return recovered_count
        
    except Exception as e:
        logger.error(f"❌ Error during missing job recovery: {e}")
        return 0

def run_complete_pipeline(args):
    """Run the complete Phase 7 pipeline"""
    start_time = datetime.now()
    logger = logging.getLogger(__name__)
    
    logger.info(f"=== STARTING PROJECT SUNSET PHASE 7 COMPLETE PIPELINE ===")
    logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = True
    excel_path = None
    cover_letters = []
    email_success = False
    recovered_jobs = 0
    
    # Health check first
    if not health_check():
        logger.error("❌ Health check failed, aborting pipeline")
        return 1
    
    # Step 0: Auto-recovery of missing jobs (always enabled unless disabled)
    if not getattr(args, 'no_recovery', False):
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
        jobs_fetched = fetch_jobs(max_jobs=args.max_jobs, quick=args.quick, profile_name=args.profile)
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
        # Bridge job data structure for compatibility
        bridge_job_data_structure()
        
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
            # Handle both integer count and list of cover letters
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
    """Main entry point for Project Sunset Phase 7 with beautiful CLI"""
    
    # Display beautiful banner
    print_sunset_banner()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load and display configuration
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
    
    args = parser.parse_args()
    
    # Default behavior
    if not any([args.health_check, args.fetch_jobs, args.process_jobs, args.export_excel, 
                args.generate_cover_letters, args.send_email, args.run_all, args.recovery_only]):
        args.health_check = True
    
    # Run recovery only
    if args.recovery_only:
        logger = logging.getLogger(__name__)
        logger.info("🔧 Running recovery-only mode...")
        
        if not health_check():
            logger.error("❌ Health check failed")
            return 1
        
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
        return 0 if health_check() else 1
    
    # Run pipeline
    return run_pipeline(args)

def bridge_job_data_structure():
    """Bridge function to ensure compatibility between JobFetcherP5 and legacy Excel export"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Bridging job data structure for Excel export compatibility...")
    
    import json
    import glob
    
    # Find all job files in data/postings
    job_files = glob.glob(str(project_root / "data" / "postings" / "job*.json"))
    updated_count = 0
    
    for job_file in job_files:
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            # Check if this job needs structure bridging
            needs_update = False
            
            # If job has 'title' but no 'web_details.position_title', create the bridge
            if 'title' in job_data and ('web_details' not in job_data or 
                                       'position_title' not in job_data.get('web_details', {})):
                
                # Ensure web_details exists
                if 'web_details' not in job_data:
                    job_data['web_details'] = {}
                
                # Bridge the title
                job_data['web_details']['position_title'] = job_data['title']
                needs_update = True
            
            # Bridge other common fields for Excel export compatibility
            if 'raw_data' in job_data and isinstance(job_data['raw_data'], dict):
                raw_data = job_data['raw_data']
                
                # Extract from MatchedObjectDescriptor if available
                if 'MatchedObjectDescriptor' in raw_data:
                    descriptor = raw_data['MatchedObjectDescriptor']
                    
                    # Bridge location
                    if 'LocationName' in descriptor and 'location' not in job_data.get('web_details', {}):
                        if 'web_details' not in job_data:
                            job_data['web_details'] = {}
                        job_data['web_details']['location'] = descriptor['LocationName']
                        needs_update = True
                    
                    # Bridge department/organizational unit
                    if 'OrganizationalUnit' in descriptor and 'department' not in job_data.get('web_details', {}):
                        if 'web_details' not in job_data:
                            job_data['web_details'] = {}
                        job_data['web_details']['department'] = descriptor['OrganizationalUnit']
                        needs_update = True
            
            # Save updated job data if changes were made
            if needs_update:
                with open(job_file, 'w') as f:
                    json.dump(job_data, f, indent=2)
                updated_count += 1
                
        except Exception as e:
            logger.warning(f"⚠️ Could not bridge job file {job_file}: {e}")
    
    logger.info(f"✅ Bridged data structure for {updated_count} job files")
    return updated_count

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
