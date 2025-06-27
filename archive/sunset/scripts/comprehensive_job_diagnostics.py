#!/usr/bin/env python3
"""
Comprehensive Job Diagnostics Tool
Answers three critical questions:
1. Can we use progress tracker to detect missing vs existing files?
2. How to handle jobs removed from site?
3. What other failure modes exist?
"""

import json
import os
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, List, Tuple, Optional
import requests
from dataclasses import dataclass

@dataclass
class JobStatus:
    id: str
    has_file: bool
    has_ai_analysis: bool
    file_size: int
    last_modified: Optional[datetime]
    in_progress_tracker: bool
    on_remote_site: Optional[bool] = None
    status: str = "unknown"

class ComprehensiveJobDiagnostics:
    def __init__(self, base_path: str = "/home/xai/Documents/sunset"):
        self.base_path = Path(base_path)
        self.jobs_dir = self.base_path / "data" / "postings"
        self.progress_file = self.base_path / "data" / "job_scans" / "search_api_scan_progress.json"
        
    def load_progress_tracker(self) -> Dict:
        """Load the progress tracker data"""
        if not self.progress_file.exists():
            return {"jobs_processed": [], "stats": {}}
        
        with open(self.progress_file, 'r') as f:
            return json.load(f)
    
    def get_local_job_files(self) -> Set[str]:
        """Get all job IDs that have local files"""
        job_files = glob.glob(str(self.jobs_dir / "*.json"))
        job_ids = set()
        for file_path in job_files:
            filename = os.path.basename(file_path)
            if filename.endswith('.json'):
                job_id = filename.replace('.json', '')
                # Handle both formats: job63819.json -> 63819 and 63819.json -> 63819
                if job_id.startswith('job'):
                    job_id = job_id[3:]  # Remove 'job' prefix
                job_ids.add(job_id)
        return job_ids
    
    def analyze_job_file(self, job_id: str) -> Dict:
        """Analyze a single job file for completeness"""
        # Handle both filename formats
        file_path = self.jobs_dir / f"job{job_id}.json"
        if not file_path.exists():
            file_path = self.jobs_dir / f"{job_id}.json"
        
        if not file_path.exists():
            return {
                "has_file": False,
                "has_ai_analysis": False,
                "file_size": 0,
                "last_modified": None
            }
        
        try:
            with open(file_path, 'r') as f:
                job_data = json.load(f)
            
            stat = file_path.stat()
            
            # Check for AI analysis indicators
            has_ai_analysis = any([
                'llama32_evaluation' in job_data,
                'cv_analysis' in job_data,
                'ai_processed' in job_data
            ])
            
            return {
                "has_file": True,
                "has_ai_analysis": has_ai_analysis,
                "file_size": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime),
                "job_data": job_data
            }
        except Exception as e:
            return {
                "has_file": True,
                "has_ai_analysis": False,
                "file_size": 0,
                "last_modified": None,
                "error": str(e)
            }
    
    def check_job_on_remote(self, job_id: str) -> Optional[bool]:
        """Check if job still exists on remote site (mock implementation)"""
        # TODO: Implement actual API check to remote site
        # For now, return None to indicate we haven't checked
        return None
    
    def detect_discrepancies(self) -> Dict:
        """Answer Question 1: Can we use progress tracker to detect missing vs existing files?"""
        progress_data = self.load_progress_tracker()
        tracked_jobs = set(progress_data.get("jobs_processed", []))
        local_jobs = self.get_local_job_files()
        
        missing_files = tracked_jobs - local_jobs  # In tracker but no file
        unexpected_files = local_jobs - tracked_jobs  # Have file but not in tracker
        
        return {
            "tracked_jobs": len(tracked_jobs),
            "local_jobs": len(local_jobs),
            "missing_files": list(missing_files),
            "unexpected_files": list(unexpected_files),
            "can_detect_missing": len(missing_files) > 0 or len(unexpected_files) > 0,
            "integrity_score": len(local_jobs & tracked_jobs) / max(len(tracked_jobs), 1) * 100
        }
    
    def analyze_all_jobs(self) -> Dict[str, JobStatus]:
        """Comprehensive analysis of all jobs"""
        progress_data = self.load_progress_tracker()
        tracked_jobs = set(progress_data.get("jobs_processed", []))
        local_jobs = self.get_local_job_files()
        all_jobs = tracked_jobs | local_jobs
        
        job_statuses = {}
        
        for job_id in all_jobs:
            file_analysis = self.analyze_job_file(job_id)
            
            status = JobStatus(
                id=job_id,
                has_file=file_analysis["has_file"],
                has_ai_analysis=file_analysis["has_ai_analysis"],
                file_size=file_analysis["file_size"],
                last_modified=file_analysis.get("last_modified"),
                in_progress_tracker=job_id in tracked_jobs,
                on_remote_site=self.check_job_on_remote(job_id)
            )
            
            # Determine status
            if not status.has_file and status.in_progress_tracker:
                status.status = "missing_file"
            elif status.has_file and not status.in_progress_tracker:
                status.status = "unexpected_file"
            elif status.has_file and not status.has_ai_analysis:
                status.status = "needs_ai_processing"
            elif status.has_file and status.has_ai_analysis:
                status.status = "complete"
            else:
                status.status = "unknown"
            
            job_statuses[job_id] = status
        
        return job_statuses
    
    def suggest_removed_job_handling(self) -> Dict:
        """Answer Question 2: How to handle jobs removed from site?"""
        return {
            "strategy": "status_update",
            "recommended_statuses": [
                "removed_from_site",
                "archived",
                "expired",
                "filled"
            ],
            "implementation": {
                "add_status_field": "Add 'job_status' field to job data",
                "periodic_check": "Implement periodic remote availability check",
                "graceful_handling": "Don't delete files, just mark as unavailable",
                "reporting": "Track removed jobs in separate report"
            }
        }
    
    def identify_failure_modes(self) -> Dict:
        """Answer Question 3: What other failure modes exist?"""
        return {
            "data_loss_modes": [
                {
                    "name": "Overwrite Without Backup",
                    "risk": "HIGH",
                    "description": "Enhanced Job Fetcher overwrites existing files with fresh data",
                    "prevention": "Check for existing AI analysis before overwriting"
                },
                {
                    "name": "Partial Processing Failure",
                    "risk": "MEDIUM", 
                    "description": "Job file created but AI processing fails",
                    "prevention": "Atomic operations, rollback on failure"
                },
                {
                    "name": "Progress Tracker Corruption",
                    "risk": "MEDIUM",
                    "description": "Progress tracker becomes inconsistent with reality",
                    "prevention": "Regular validation and backup of progress tracker"
                },
                {
                    "name": "Concurrent Access Issues",
                    "risk": "LOW",
                    "description": "Multiple processes modifying same files",
                    "prevention": "File locking mechanism"
                },
                {
                    "name": "API Rate Limiting",
                    "risk": "LOW",
                    "description": "Remote API becomes unavailable during processing",
                    "prevention": "Retry logic with exponential backoff"
                }
            ],
            "validation_checks": [
                "File existence before overwrite",
                "AI analysis preservation",
                "Progress tracker consistency",
                "File size sanity checks",
                "JSON validity checks"
            ]
        }
    
    def generate_report(self) -> Dict:
        """Generate comprehensive diagnostic report"""
        print("🔍 COMPREHENSIVE JOB DIAGNOSTICS")
        print("=" * 80)
        
        # Question 1: Discrepancy Detection
        print("\n📊 QUESTION 1: Can we use progress tracker to detect discrepancies?")
        discrepancies = self.detect_discrepancies()
        print(f"   Tracked jobs: {discrepancies['tracked_jobs']}")
        print(f"   Local files: {discrepancies['local_jobs']}")
        print(f"   Missing files: {len(discrepancies['missing_files'])}")
        print(f"   Unexpected files: {len(discrepancies['unexpected_files'])}")
        print(f"   Can detect issues: {'YES' if discrepancies['can_detect_missing'] else 'NO'}")
        print(f"   Data integrity: {discrepancies['integrity_score']:.1f}%")
        
        if discrepancies['missing_files']:
            print(f"   🚨 Missing files: {discrepancies['missing_files'][:5]}{'...' if len(discrepancies['missing_files']) > 5 else ''}")
        if discrepancies['unexpected_files']:
            print(f"   ⚠️  Unexpected files: {discrepancies['unexpected_files'][:5]}{'...' if len(discrepancies['unexpected_files']) > 5 else ''}")
        
        # Job Status Analysis
        print("\n📋 JOB STATUS BREAKDOWN:")
        job_statuses = self.analyze_all_jobs()
        status_counts = {}
        ai_analysis_count = 0
        
        for job_id, status in job_statuses.items():
            status_counts[status.status] = status_counts.get(status.status, 0) + 1
            if status.has_ai_analysis:
                ai_analysis_count += 1
        
        for status, count in status_counts.items():
            print(f"   {status}: {count} jobs")
        
        print(f"\n🧠 AI ANALYSIS STATUS:")
        print(f"   Jobs with AI analysis: {ai_analysis_count}/{len(job_statuses)}")
        print(f"   Data loss impact: {(len(job_statuses) - ai_analysis_count) / len(job_statuses) * 100:.1f}%")
        
        # Question 2: Removed Job Handling
        print("\n📝 QUESTION 2: How to handle removed jobs?")
        removed_handling = self.suggest_removed_job_handling()
        print(f"   Strategy: {removed_handling['strategy']}")
        print(f"   Recommended statuses: {', '.join(removed_handling['recommended_statuses'])}")
        
        # Question 3: Failure Modes
        print("\n⚠️  QUESTION 3: Identified failure modes:")
        failure_modes = self.identify_failure_modes()
        for mode in failure_modes['data_loss_modes']:
            print(f"   🔴 {mode['name']} ({mode['risk']} risk)")
            print(f"      {mode['description']}")
        
        print("\n💡 IMMEDIATE RECOMMENDATIONS:")
        print("   1. Fix Enhanced Job Fetcher to preserve AI analysis")
        print("   2. Add validation checks before file operations")
        print("   3. Implement job status tracking for removed jobs")
        print("   4. Create backup mechanism for critical data")
        print("   5. Add atomic operations to prevent partial failures")
        
        return {
            "discrepancies": discrepancies,
            "job_statuses": {k: v.__dict__ for k, v in job_statuses.items()},
            "removed_job_handling": removed_handling,
            "failure_modes": failure_modes,
            "summary": {
                "total_jobs": len(job_statuses),
                "jobs_with_ai": ai_analysis_count,
                "data_loss_percentage": (len(job_statuses) - ai_analysis_count) / len(job_statuses) * 100,
                "integrity_score": discrepancies['integrity_score']
            }
        }

if __name__ == "__main__":
    diagnostics = ComprehensiveJobDiagnostics()
    report = diagnostics.generate_report()
