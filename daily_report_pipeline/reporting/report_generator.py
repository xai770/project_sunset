"""
Report Generator - Clean Orchestrator
===================================

Orchestrates the entire report generation process using clean,
modular components.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import time

from ..data.job_repository import JobRepository
from ..processing.job_processor import JobProcessor
from .generators.excel_generator import ExcelReportGenerator
from .generators.markdown_generator import MarkdownReportGenerator

class ReportGenerator:
    """Clean orchestrator for report generation process"""
    
    def __init__(self):
        """Initialize the report generator with its components"""
        # Initialize components
        self.reports_path = Path('/home/xai/Documents/sandy/reports')
        self.job_repository = JobRepository()
        self.job_processor = JobProcessor()
        self.excel_generator = ExcelReportGenerator(self.reports_path)
        self.markdown_generator = MarkdownReportGenerator(self.reports_path)
        
        # Progress tracking
        self.total_jobs = 0
        self.processed_jobs = 0
        self.start_time = 0.0
    
    def count_available_jobs(self) -> int:
        """Get count of available jobs"""
        return self.job_repository.count_available_jobs()
    
    def generate_report(self, limit: Optional[int] = None) -> Optional[Tuple[Path, Path]]:
        """Generate reports for the specified number of jobs
        
        Args:
            limit: Maximum number of jobs to process. If None, processes all jobs.
            
        Returns:
            Tuple of (excel_path, markdown_path) if successful, None if no jobs processed
        """
        print(f"\nGENERATING DAILY REPORT (MODULAR ARCHITECTURE)")
        print(f"Processing {'all' if limit is None else limit} jobs for compliant report...")
        print("=" * 80)
        
        # Load and process jobs
        self.start_time = time.time()
        jobs = self.job_repository.load_jobs(limit)
        
        if not jobs:
            print("❌ No jobs available for processing!")
            return None
        
        # Process each job
        processed_jobs = []
        for i, job_data in enumerate(jobs, 1):
            print(f"\nDAILY REPORT JOB #{i}/{len(jobs)}: Job {job_data.get('job_id', 'unknown')}")
            print("-" * 60)
            
            try:
                result = self.job_processor.process_job(job_data)
                processed_jobs.append(result)
                print(f"  ✅ Job processed successfully!")
            except Exception as e:
                print(f"  ❌ Error processing job: {e}")
                continue
        
        if not processed_jobs:
            print("❌ No jobs were successfully processed!")
            return None
        
        # Generate reports
        try:
            excel_path = self.excel_generator.generate_report(processed_jobs)
            markdown_path = self.markdown_generator.generate_report(processed_jobs)
            
            processing_time = time.time() - self.start_time
            print(f"\n✅ Report generation complete!")
            print(f"📊 Excel Report: {excel_path}")
            print(f"📝 Markdown Report: {markdown_path}")
            print(f"⏱️ Total processing time: {processing_time:.2f}s")
            
            return excel_path, markdown_path
            
        except Exception as e:
            print(f"❌ Error generating reports: {e}")
            return None
