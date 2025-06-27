#!/usr/bin/env python3
"""
Enhanced Progress Tracker with Job Status Management
===================================================

Answers your key questions:
1. ✅ Can we use progress tracker to detect missing vs existing files?
2. ✅ How to handle jobs removed from site? 
3. ✅ What other failure modes exist?

This module provides comprehensive job status tracking and management.
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Job status enumeration"""
    ACTIVE = "active"                    # Job is live on site
    REMOVED_FROM_SITE = "removed_from_site"  # Job no longer on site
    ARCHIVED = "archived"                # Job archived but preserved
    EXPIRED = "expired"                  # Job posting expired
    FILLED = "filled"                    # Position was filled
    PROCESSING = "processing"            # Currently being processed
    ERROR = "error"                      # Error state
    UNKNOWN = "unknown"                  # Status unknown

@dataclass
class JobTrackingRecord:
    """Individual job tracking record"""
    job_id: str
    status: JobStatus
    title: str = ""
    url: str = ""
    last_seen_on_site: Optional[str] = None
    last_updated: Optional[str] = None
    has_ai_analysis: bool = False
    has_file: bool = False
    file_size: int = 0
    processing_history: List[Dict] = None
    
    def __post_init__(self):
        if self.processing_history is None:
            self.processing_history = []
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()

class EnhancedProgressTracker:
    """Enhanced progress tracker with comprehensive job status management"""
    
    def __init__(self, base_path: str = "/home/xai/Documents/sunset"):
        self.base_path = Path(base_path)
        self.jobs_dir = self.base_path / "data" / "postings"
        self.progress_file = self.base_path / "data" / "job_scans" / "search_api_scan_progress.json"
        self.enhanced_tracker_file = self.base_path / "data" / "job_scans" / "enhanced_job_tracker.json"
        
        # Ensure directories exist
        self.enhanced_tracker_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_legacy_progress(self) -> Dict:
        """Load legacy progress tracker"""
        if not self.progress_file.exists():
            return {"jobs_processed": [], "stats": {}}
        
        with open(self.progress_file, 'r') as f:
            return json.load(f)
    
    def load_enhanced_tracker(self) -> Dict[str, JobTrackingRecord]:
        """Load enhanced job tracking data"""
        if not self.enhanced_tracker_file.exists():
            return {}
        
        try:
            with open(self.enhanced_tracker_file, 'r') as f:
                data = json.load(f)
            
            # Convert dict data back to JobTrackingRecord objects
            tracker = {}
            for job_id, record_data in data.items():
                # Convert status string back to enum
                record_data['status'] = JobStatus(record_data['status'])
                tracker[job_id] = JobTrackingRecord(**record_data)
            
            return tracker
        
        except Exception as e:
            logger.error(f"Error loading enhanced tracker: {e}")
            return {}
    
    def save_enhanced_tracker(self, tracker: Dict[str, JobTrackingRecord]):
        """Save enhanced tracking data"""
        try:
            # Convert JobTrackingRecord objects to dicts for JSON serialization
            serializable_data = {}
            for job_id, record in tracker.items():
                record_dict = asdict(record)
                record_dict['status'] = record.status.value  # Convert enum to string
                serializable_data[job_id] = record_dict
            
            with open(self.enhanced_tracker_file, 'w') as f:
                json.dump(serializable_data, f, indent=2)
            
            logger.debug(f"Saved enhanced tracker with {len(tracker)} jobs")
            
        except Exception as e:
            logger.error(f"Error saving enhanced tracker: {e}")
    
    def migrate_from_legacy(self) -> Dict[str, JobTrackingRecord]:
        """Migrate from legacy progress tracker to enhanced system"""
        logger.info("🔄 Migrating from legacy progress tracker...")
        
        legacy_data = self.load_legacy_progress()
        enhanced_tracker = self.load_enhanced_tracker()
        
        # Get all job IDs from legacy system
        legacy_jobs = set(legacy_data.get("jobs_processed", []))
        
        # Get all actual job files
        job_files = list(self.jobs_dir.glob("job*.json"))
        actual_jobs = set()
        
        for job_file in job_files:
            job_id = job_file.stem.replace('job', '')
            actual_jobs.add(job_id)
            
            # Create or update tracking record
            if job_id not in enhanced_tracker:
                # Analyze the job file
                file_analysis = self._analyze_job_file(job_file)
                
                enhanced_tracker[job_id] = JobTrackingRecord(
                    job_id=job_id,
                    status=JobStatus.ACTIVE if job_id in legacy_jobs else JobStatus.UNKNOWN,
                    title=file_analysis.get('title', ''),
                    has_ai_analysis=file_analysis.get('has_ai_analysis', False),
                    has_file=True,
                    file_size=file_analysis.get('file_size', 0),
                    last_seen_on_site=datetime.now().isoformat() if job_id in legacy_jobs else None
                )
        
        # Mark jobs that are in legacy tracker but have no files
        missing_jobs = legacy_jobs - actual_jobs
        for job_id in missing_jobs:
            if job_id not in enhanced_tracker:
                enhanced_tracker[job_id] = JobTrackingRecord(
                    job_id=job_id,
                    status=JobStatus.REMOVED_FROM_SITE,
                    has_file=False,
                    last_seen_on_site=legacy_data.get("stats", {}).get("last_updated")
                )
        
        self.save_enhanced_tracker(enhanced_tracker)
        logger.info(f"✅ Migration complete: {len(enhanced_tracker)} jobs tracked")
        
        return enhanced_tracker
    
    def _analyze_job_file(self, job_file: Path) -> Dict:
        """Analyze a job file for metadata"""
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            # Check for AI analysis
            ai_fields = ['llama32_evaluation', 'cv_analysis', 'skill_match', 'domain_enhanced_match']
            has_ai_analysis = any(field in job_data for field in ai_fields)
            
            # Get title
            title = (
                job_data.get('web_details', {}).get('position_title', '') or
                job_data.get('title', '') or
                'Unknown Title'
            )
            
            return {
                'has_ai_analysis': has_ai_analysis,
                'title': title,
                'file_size': job_file.stat().st_size,
                'valid': True
            }
            
        except Exception as e:
            logger.error(f"Error analyzing job file {job_file}: {e}")
            return {
                'has_ai_analysis': False,
                'title': 'Error reading file',
                'file_size': 0,
                'valid': False
            }
    
    def check_job_on_remote_site(self, job_id: str) -> bool:
        """Check if job still exists on Deutsche Bank careers site"""
        try:
            # Check via API
            api_url = f"https://api-deutschebank.beesite.de/jobhtml/{job_id}.json"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                logger.warning(f"Unexpected status {response.status_code} for job {job_id}")
                return None  # Unknown status
                
        except Exception as e:
            logger.error(f"Error checking job {job_id} on remote site: {e}")
            return None
    
    def update_job_status(self, job_id: str, new_status: JobStatus, reason: str = ""):
        """Update job status with logging"""
        enhanced_tracker = self.load_enhanced_tracker()
        
        if job_id not in enhanced_tracker:
            # Create new record
            enhanced_tracker[job_id] = JobTrackingRecord(
                job_id=job_id,
                status=new_status
            )
        else:
            # Update existing record
            old_status = enhanced_tracker[job_id].status
            enhanced_tracker[job_id].status = new_status
            enhanced_tracker[job_id].last_updated = datetime.now().isoformat()
            
            # Add to processing history
            enhanced_tracker[job_id].processing_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "status_change",
                "old_status": old_status.value,
                "new_status": new_status.value,
                "reason": reason
            })
        
        self.save_enhanced_tracker(enhanced_tracker)
        logger.info(f"Updated job {job_id} status to {new_status.value}")
    
    def detect_discrepancies(self) -> Dict:
        """ANSWER TO QUESTION 1: Detect missing vs existing files using progress tracker"""
        
        # Load both systems
        legacy_data = self.load_legacy_progress()
        enhanced_tracker = self.load_enhanced_tracker()
        
        # If enhanced tracker is empty, migrate first
        if not enhanced_tracker:
            enhanced_tracker = self.migrate_from_legacy()
        
        # Get sets for comparison
        tracked_jobs = set(legacy_data.get("jobs_processed", []))
        
        # Scan actual files
        job_files = list(self.jobs_dir.glob("job*.json"))
        actual_jobs = set()
        for job_file in job_files:
            job_id = job_file.stem.replace('job', '')
            actual_jobs.add(job_id)
        
        # Find discrepancies
        missing_files = tracked_jobs - actual_jobs     # In tracker but no file
        unexpected_files = actual_jobs - tracked_jobs  # Have file but not tracked
        matching_jobs = tracked_jobs & actual_jobs     # Both tracked and have file
        
        return {
            "can_detect_discrepancies": True,  # YES! We can detect them
            "tracked_jobs_count": len(tracked_jobs),
            "actual_files_count": len(actual_jobs),
            "missing_files": list(missing_files),
            "unexpected_files": list(unexpected_files),
            "matching_jobs": list(matching_jobs),
            "data_integrity_score": len(matching_jobs) / max(len(tracked_jobs), 1) * 100,
            "discrepancy_detected": len(missing_files) > 0 or len(unexpected_files) > 0
        }
    
    def handle_removed_jobs(self, check_remote: bool = False) -> Dict:
        """ANSWER TO QUESTION 2: Handle jobs removed from site"""
        
        enhanced_tracker = self.load_enhanced_tracker()
        if not enhanced_tracker:
            enhanced_tracker = self.migrate_from_legacy()
        
        removed_jobs = []
        checked_jobs = []
        
        for job_id, record in enhanced_tracker.items():
            # Skip if already marked as removed
            if record.status == JobStatus.REMOVED_FROM_SITE:
                continue
            
            # Check if file exists but job might be removed from site
            if not record.has_file:
                # Mark as removed since no local file
                self.update_job_status(job_id, JobStatus.REMOVED_FROM_SITE, "No local file found")
                removed_jobs.append(job_id)
                continue
            
            # Optionally check remote site
            if check_remote:
                remote_status = self.check_job_on_remote_site(job_id)
                checked_jobs.append(job_id)
                
                if remote_status is False:  # Definitively not on site
                    self.update_job_status(job_id, JobStatus.REMOVED_FROM_SITE, "Confirmed not on remote site")
                    removed_jobs.append(job_id)
                elif remote_status is True:
                    # Update last seen
                    record.last_seen_on_site = datetime.now().isoformat()
        
        return {
            "strategy": "status_update_with_preservation",
            "removed_jobs_found": len(removed_jobs),
            "removed_job_ids": removed_jobs,
            "jobs_checked_remotely": len(checked_jobs),
            "recommended_actions": [
                "Jobs marked as 'removed_from_site' but files preserved",
                "Use periodic remote checking to validate status",
                "Archive old removed jobs to separate directory",
                "Generate reports of removed vs active jobs"
            ]
        }
    
    def identify_failure_modes(self) -> Dict:
        """ANSWER TO QUESTION 3: Identify potential failure modes"""
        
        return {
            "critical_failure_modes": [
                {
                    "name": "AI Analysis Overwrite",
                    "risk_level": "CRITICAL",
                    "description": "Existing AI analysis gets overwritten during job refresh",
                    "prevention": "Check for AI fields before overwriting",
                    "detection": "Monitor jobs_with_ai_analysis count before/after operations"
                },
                {
                    "name": "Progress Tracker Corruption", 
                    "risk_level": "HIGH",
                    "description": "Progress tracker becomes inconsistent with actual files",
                    "prevention": "Regular validation and backup of progress tracker",
                    "detection": "Compare tracked vs actual job counts"
                },
                {
                    "name": "Bulk File Deletion",
                    "risk_level": "CRITICAL", 
                    "description": "Mass deletion of job files due to API or processing errors",
                    "prevention": "Pre-operation backups and atomic operations",
                    "detection": "Sudden drop in file count"
                },
                {
                    "name": "Partial Processing Failure",
                    "risk_level": "MEDIUM",
                    "description": "Job processing starts but fails midway leaving corrupted files",
                    "prevention": "Atomic file operations with rollback",
                    "detection": "Check file integrity after operations"
                },
                {
                    "name": "Status Tracking Drift",
                    "risk_level": "MEDIUM",
                    "description": "Job status becomes out of sync with reality",
                    "prevention": "Periodic remote validation",
                    "detection": "Regular discrepancy analysis"
                }
            ],
            "monitoring_recommendations": [
                "Daily job count validation",
                "Weekly AI analysis preservation check", 
                "Monthly remote site validation",
                "Automated backup before bulk operations",
                "Real-time file integrity monitoring"
            ],
            "recovery_procedures": [
                "Restore from automatic backups",
                "Re-run AI analysis for lost data",
                "Rebuild progress tracker from file analysis",
                "Manual job status verification"
            ]
        }
    
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive status report"""
        
        # Question 1: Discrepancy Detection
        discrepancies = self.detect_discrepancies()
        
        # Question 2: Removed Jobs Handling  
        removed_jobs = self.handle_removed_jobs(check_remote=False)  # Don't check remote by default
        
        # Question 3: Failure Modes
        failure_modes = self.identify_failure_modes()
        
        # Additional analysis
        enhanced_tracker = self.load_enhanced_tracker()
        status_counts = {}
        for record in enhanced_tracker.values():
            status = record.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        report = [
            "🔍 COMPREHENSIVE JOB TRACKING REPORT",
            "=" * 60,
            "",
            "📊 QUESTION 1: Can we detect missing vs existing files?",
            f"   ✅ ANSWER: YES - Detection capability is fully functional",
            f"   📈 Tracked jobs: {discrepancies['tracked_jobs_count']}",
            f"   📁 Actual files: {discrepancies['actual_files_count']}",
            f"   ❌ Missing files: {len(discrepancies['missing_files'])}",
            f"   ➕ Unexpected files: {len(discrepancies['unexpected_files'])}",
            f"   🎯 Data integrity: {discrepancies['data_integrity_score']:.1f}%",
            ""
        ]
        
        if discrepancies['missing_files']:
            report.append(f"   🚨 Missing: {discrepancies['missing_files'][:5]}...")
        if discrepancies['unexpected_files']: 
            report.append(f"   ⚠️  Unexpected: {discrepancies['unexpected_files'][:5]}...")
        
        report.extend([
            "",
            "📝 QUESTION 2: How to handle jobs removed from site?",
            f"   ✅ ANSWER: Status-based tracking with preservation",
            f"   🔄 Strategy: {removed_jobs['strategy']}",
            f"   📤 Jobs marked as removed: {removed_jobs['removed_jobs_found']}",
            "   📋 Recommended job statuses:",
            "      - removed_from_site (job no longer on site)",
            "      - archived (preserved but inactive)",
            "      - expired (posting expired naturally)",
            "      - filled (position was filled)",
            "",
            "⚠️  QUESTION 3: What failure modes exist?",
            "   🔴 CRITICAL RISKS:"
        ])
        
        for mode in failure_modes['critical_failure_modes']:
            if mode['risk_level'] in ['CRITICAL', 'HIGH']:
                report.append(f"      - {mode['name']} ({mode['risk_level']})")
                report.append(f"        {mode['description']}")
        
        report.extend([
            "",
            "📈 CURRENT JOB STATUS BREAKDOWN:"
        ])
        
        for status, count in status_counts.items():
            report.append(f"   {status}: {count} jobs")
        
        report.extend([
            "",
            "💡 IMMEDIATE ACTION ITEMS:",
            "   1. ✅ Enhanced progress tracker implemented",
            "   2. ⚠️  Fix AI analysis preservation in job fetcher",
            "   3. 🔄 Implement automated backup system",
            "   4. 📊 Set up daily monitoring dashboard", 
            "   5. 🔍 Add real-time validation checks"
        ])
        
        return "\n".join(report)

if __name__ == "__main__":
    # Example usage
    tracker = EnhancedProgressTracker()
    report = tracker.generate_comprehensive_report()
    print(report)
