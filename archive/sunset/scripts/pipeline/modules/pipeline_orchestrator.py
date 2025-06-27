#!/usr/bin/env python3
"""
Pipeline Orchestrator Module

Main orchestration logic for the complete Phase 7 pipeline.
This module coordinates all pipeline steps and provides the main entry point
for running the complete pipeline workflow.
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

# Import other modules
try:
    from .health_check import health_check
    from .config_loader import load_search_criteria
    from .job_fetcher import fetch_jobs
    from .job_processor import process_jobs_with_specialists
    from .excel_exporter import export_jobs_to_excel
    from .cover_letter_generator import generate_cover_letters_for_good_matches
    from .email_sender import send_email_package
    from .job_recovery import detect_and_recover_missing_jobs
    from .data_bridge import bridge_job_data_structure
except ImportError:
    # Fallback to absolute imports for direct execution
    from scripts.pipeline.modules.health_check import health_check
    from scripts.pipeline.modules.config_loader import load_search_criteria
    from scripts.pipeline.modules.job_fetcher import fetch_jobs
    from scripts.pipeline.modules.job_processor import process_jobs_with_specialists
    from scripts.pipeline.modules.excel_exporter import export_jobs_to_excel
    from scripts.pipeline.modules.cover_letter_generator import generate_cover_letters_for_good_matches
    from scripts.pipeline.modules.email_sender import send_email_package
    from scripts.pipeline.modules.job_recovery import detect_and_recover_missing_jobs
    from scripts.pipeline.modules.data_bridge import bridge_job_data_structure

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """Main orchestrator for the Project Sunset Phase 7 pipeline"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.results = {
            'success': False,
            'excel_path': None,
            'cover_letters': [],
            'email_success': False,
            'recovered_jobs': 0,
            'errors': []
        }
    
    def run_complete_pipeline(self, args) -> int:
        """
        Run the complete Phase 7 pipeline
        
        Args:
            args: Command line arguments
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        self.start_time = datetime.now()
        logger.info(f"=== STARTING PROJECT SUNSET PHASE 7 COMPLETE PIPELINE ===")
        logger.info(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        success = True
        
        try:
            # Health check first
            if not self._run_health_check():
                logger.error("❌ Health check failed, aborting pipeline")
                return 1
            
            # Step 0: Auto-recovery of missing jobs (always enabled unless disabled)
            if not getattr(args, 'no_recovery', False):
                self.results['recovered_jobs'] = self._run_job_recovery(args)
            
            # Step 1: Fetch jobs if requested
            if args.fetch_jobs:
                success &= self._run_job_fetching(args)
            
            # Step 2: Process jobs with specialists if requested
            if args.process_jobs:
                success &= self._run_job_processing(args)
            
            # Step 3: Export to Excel if requested
            if args.export_excel:
                success &= self._run_excel_export(args)
            
            # Step 4: Generate cover letters if requested and we have Excel
            if args.generate_cover_letters and self.results['excel_path']:
                self._run_cover_letter_generation()
            
            # Step 5: Send email if requested and we have something to send
            if args.send_email and self.results['excel_path']:
                self.results['email_success'] = self._run_email_delivery()
            
            self.results['success'] = success
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed with exception: {e}")
            self.results['errors'].append(str(e))
            success = False
        
        finally:
            self._log_pipeline_summary(success)
        
        return 0 if success else 1
    
    def _run_health_check(self) -> bool:
        """Run pipeline health check"""
        logger.info("🏥 Running health check...")
        try:
            return health_check()
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    def _run_job_recovery(self, args) -> int:
        """Run job recovery step"""
        logger.info("🔧 Starting automatic missing job recovery...")
        try:
            recovery_limit = getattr(args, 'max_recovery', 25)
            recovered_jobs = detect_and_recover_missing_jobs(
                max_recovery=recovery_limit, 
                enable_recovery=True
            )
            if recovered_jobs > 0:
                logger.info(f"🎉 Auto-recovery successful: {recovered_jobs} jobs recovered")
            else:
                logger.info("✅ No missing jobs detected")
            return recovered_jobs
        except Exception as e:
            logger.error(f"❌ Job recovery failed: {e}")
            return 0
    
    def _run_job_fetching(self, args) -> bool:
        """Run job fetching step"""
        logger.info("🔍 Fetching jobs...")
        try:
            jobs_fetched = fetch_jobs(
                max_jobs=args.max_jobs, 
                quick=args.quick, 
                profile_name=args.profile
            )
            if jobs_fetched == 0:
                logger.warning("⚠️ No jobs fetched")
                return False
            logger.info(f"✅ Fetched {jobs_fetched} jobs")
            return True
        except Exception as e:
            logger.error(f"❌ Job fetching failed: {e}")
            self.results['errors'].append(f"Job fetching: {e}")
            return False
    
    def _run_job_processing(self, args) -> bool:
        """Run job processing step"""
        logger.info("🧠 Processing jobs with specialists...")
        try:
            processed_jobs = process_jobs_with_specialists(job_ids=args.job_ids)
            if not processed_jobs:
                logger.error("❌ Job processing with specialists failed")
                return False
            logger.info("✅ Job processing completed")
            return True
        except Exception as e:
            logger.error(f"❌ Job processing failed: {e}")
            self.results['errors'].append(f"Job processing: {e}")
            return False
    
    def _run_excel_export(self, args) -> bool:
        """Run Excel export step"""
        logger.info("📊 Exporting to Excel...")
        try:
            # Bridge job data structure for compatibility
            bridge_job_data_structure()
            
            excel_path = export_jobs_to_excel(feedback_system=True, reviewer_name="xai")
            if not excel_path:
                logger.error("❌ Excel export failed")
                return False
            
            self.results['excel_path'] = excel_path
            logger.info(f"✅ Excel exported to: {excel_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Excel export failed: {e}")
            self.results['errors'].append(f"Excel export: {e}")
            return False
    
    def _run_cover_letter_generation(self) -> None:
        """Run cover letter generation step"""
        logger.info("✍️ Generating cover letters...")
        try:
            cover_letters = generate_cover_letters_for_good_matches(self.results['excel_path'])
            self.results['cover_letters'] = cover_letters
            
            # Handle both integer count and list types
            if isinstance(cover_letters, int):
                count = cover_letters
            else:
                count = len(cover_letters) if cover_letters else 0
            
            if count > 0:
                logger.info(f"✅ Generated {count} cover letters")
            else:
                logger.info("ℹ️ No cover letters generated (no 'Good' matches found)")
                
        except Exception as e:
            logger.warning(f"⚠️ Cover letter generation failed: {e}")
            self.results['errors'].append(f"Cover letter generation: {e}")
            # Note: Cover letters are optional, so don't fail pipeline
    
    def _run_email_delivery(self) -> bool:
        """Run email delivery step"""
        logger.info("📧 Sending email package...")
        try:
            email_success = send_email_package(
                self.results['excel_path'], 
                self.results['cover_letters']
            )
            if email_success:
                logger.info("✅ Email delivery successful")
            else:
                logger.warning("⚠️ Email delivery failed, but pipeline continues")
            return email_success
        except Exception as e:
            logger.warning(f"⚠️ Email delivery failed: {e}")
            self.results['errors'].append(f"Email delivery: {e}")
            return False
    
    def _log_pipeline_summary(self, success: bool) -> None:
        """Log pipeline execution summary"""
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time
        
        if success:
            logger.info(f"✅ PHASE 7 COMPLETE PIPELINE FINISHED SUCCESSFULLY")
            logger.info(f"📊 Results:")
            if self.results['recovered_jobs'] > 0:
                logger.info(f"  🔧 Recovery: {self.results['recovered_jobs']} missing jobs recovered")
            if self.results['excel_path']:
                logger.info(f"  📋 Excel file: {self.results['excel_path']}")
            if self.results['cover_letters']:
                # Handle both integer count and list types
                if isinstance(self.results['cover_letters'], int):
                    count = self.results['cover_letters']
                else:
                    count = len(self.results['cover_letters'])
                logger.info(f"  ✍️ Cover letters: {count} generated")
            if self.results['email_success']:
                logger.info(f"  📧 Email delivery: ✅ Sent")
        else:
            logger.error(f"❌ PHASE 7 PIPELINE COMPLETED WITH ERRORS")
            if self.results['errors']:
                logger.error("❌ Errors encountered:")
                for error in self.results['errors']:
                    logger.error(f"  - {error}")
        
        logger.info(f"End time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Total runtime: {duration}")

def run_pipeline_compatibility_mode(args) -> int:
    """Compatibility wrapper for legacy run_pipeline function"""
    logger.info("🔄 Running pipeline in compatibility mode...")
    
    # If run-all is specified, enable all Phase 7 steps
    if args.run_all:
        args.fetch_jobs = True
        args.process_jobs = True
        args.export_excel = True
        args.generate_cover_letters = True
        args.send_email = True
    
    orchestrator = PipelineOrchestrator()
    return orchestrator.run_complete_pipeline(args)

def run_recovery_only_mode(args) -> int:
    """Run recovery-only mode"""
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

def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser"""
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
    
    return parser

def main() -> int:
    """Main entry point for the pipeline orchestrator"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse command line arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Default behavior
    if not any([args.health_check, args.fetch_jobs, args.process_jobs, args.export_excel, 
                args.generate_cover_letters, args.send_email, args.run_all, args.recovery_only]):
        args.health_check = True
    
    # Run recovery only
    if args.recovery_only:
        return run_recovery_only_mode(args)
    
    # Run health check only
    if args.health_check and not any([args.fetch_jobs, args.process_jobs, args.export_excel, 
                                      args.generate_cover_letters, args.send_email, args.run_all]):
        return 0 if health_check() else 1
    
    # Run pipeline
    return run_pipeline_compatibility_mode(args)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
