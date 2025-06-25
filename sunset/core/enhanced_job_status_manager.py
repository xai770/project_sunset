#!/usr/bin/env python3
"""
Enhanced Job Status Manager
==========================

Comprehensive solution for tracking job statuses and detecting data inconsistencies.
Addresses the three key questions:
1. Can we use progress tracker to detect missing vs existing files?
2. How to handle jobs removed from site?
3. What other failure modes exist?

This module provides:
- Real-time progress tracker validation
- Job status tracking (active, removed_from_site, archived, expired)
- Data integrity checks
- Failure mode detection and prevention
"""

import json
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    ACTIVE = "active"
    REMOVED_FROM_SITE = "removed_from_site"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    FILLED = "filled"
    PROCESSING_ERROR = "processing_error"
    UNKNOWN = "unknown"

@dataclass
class JobRecord:
    """Enhanced job record with status tracking"""
    job_id: str
    status: JobStatus
    last_seen: datetime
    last_checked: datetime
    has_ai_analysis: bool
    file_exists: bool
    file_size: int
    checksum: Optional[str] = None
    error_count: int = 0
    notes: str = ""

class EnhancedJobStatusManager:
    """Enhanced job status manager with comprehensive tracking"""
    
    def __init__(self, base_path: str = "/home/xai/Documents/sunset"):
        self.base_path = Path(base_path)
        self.jobs_dir = self.base_path / "data" / "postings"
        self.progress_file = self.base_path / "data" / "job_scans" / "search_api_scan_progress.json"
        self.status_file = self.base_path / "data" / "job_scans" / "enhanced_job_status.json"
        self.integrity_log = self.base_path / "data" / "job_scans" / "integrity_log.json"
        
        # Ensure directories exist
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_progress_tracker(self) -> Dict:
        """Load the original progress tracker"""
        if not self.progress_file.exists():
            return {"jobs_processed": [], "stats": {}}
        
        with open(self.progress_file, 'r') as f:
            return json.load(f)
    
    def load_status_tracker(self) -> Dict[str, JobRecord]:
        """Load enhanced status tracker"""
        if not self.status_file.exists():
            return {}
        
        try:
            with open(self.status_file, 'r') as f:
                data = json.load(f)
            
            # Convert to JobRecord objects
            records = {}
            for job_id, record_data in data.items():
                records[job_id] = JobRecord(
                    job_id=record_data['job_id'],
                    status=JobStatus(record_data['status']),
                    last_seen=datetime.fromisoformat(record_data['last_seen']),
                    last_checked=datetime.fromisoformat(record_data['last_checked']),
                    has_ai_analysis=record_data['has_ai_analysis'],
                    file_exists=record_data['file_exists'],
                    file_size=record_data['file_size'],
                    checksum=record_data.get('checksum'),
                    error_count=record_data.get('error_count', 0),
                    notes=record_data.get('notes', '')
                )
            return records
        except Exception as e:
            logger.error(f"Error loading status tracker: {e}")
            return {}
    
    def save_status_tracker(self, records: Dict[str, JobRecord]):
        """Save enhanced status tracker"""
        try:
            # Convert JobRecord objects to serializable format
            data = {}
            for job_id, record in records.items():
                record_dict = asdict(record)
                record_dict['status'] = record.status.value
                record_dict['last_seen'] = record.last_seen.isoformat()
                record_dict['last_checked'] = record.last_checked.isoformat()
                data[job_id] = record_dict
            
            with open(self.status_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving status tracker: {e}")
    
    def get_local_job_files(self) -> Dict[str, Path]:
        """Get all job files with their paths"""
        job_files = {}
        for file_path in self.jobs_dir.glob("job*.json"):
            filename = file_path.name
            if filename.endswith('.json'):
                job_id = filename.replace('.json', '')
                if job_id.startswith('job'):
                    job_id = job_id[3:]  # Remove 'job' prefix
                job_files[job_id] = file_path
        return job_files
    
    def analyze_job_file(self, job_id: str, file_path: Path) -> Dict:
        """Analyze a job file for completeness and integrity"""
        if not file_path.exists():
            return {
                "has_file": False,
                "has_ai_analysis": False,
                "file_size": 0,
                "checksum": None,
                "error": "File not found"
            }
        
        try:
            with open(file_path, 'r') as f:
                job_data = json.load(f)
            
            stat = file_path.stat()
            
            # Check for AI analysis indicators
            has_ai_analysis = any([
                'llama32_evaluation' in job_data,
                'cv_analysis' in job_data,
                'ai_processed' in job_data,
                'skill_match' in job_data and job_data['skill_match'].get('overall_match', 0) > 0,
                'domain_enhanced_match' in job_data,
                job_data.get('web_details', {}).get('concise_description', '').strip() and 
                'placeholder for a concise description' not in job_data.get('web_details', {}).get('concise_description', '').lower()
            ])
            
            # Simple checksum for integrity checking
            import hashlib
            content = json.dumps(job_data, sort_keys=True)
            checksum = hashlib.md5(content.encode()).hexdigest()
            
            return {
                "has_file": True,
                "has_ai_analysis": has_ai_analysis,
                "file_size": stat.st_size,
                "checksum": checksum,
                "job_data": job_data,
                "last_modified": datetime.fromtimestamp(stat.st_mtime)
            }
        except Exception as e:
            return {
                "has_file": True,
                "has_ai_analysis": False,
                "file_size": 0,
                "checksum": None,
                "error": str(e)
            }
    
    def detect_discrepancies(self) -> Dict:
        """Answer Question 1: Detect missing vs existing files using progress tracker"""
        progress_data = self.load_progress_tracker()
        tracked_jobs = set(progress_data.get("jobs_processed", []))
        local_files = self.get_local_job_files()
        local_job_ids = set(local_files.keys())
        
        missing_files = tracked_jobs - local_job_ids  # In tracker but no file
        unexpected_files = local_job_ids - tracked_jobs  # Have file but not in tracker
        
        return {
            "tracked_jobs": len(tracked_jobs),
            "local_jobs": len(local_job_ids),
            "missing_files": list(missing_files),
            "unexpected_files": list(unexpected_files),
            "can_detect_missing": len(missing_files) > 0 or len(unexpected_files) > 0,
            "integrity_score": len(local_job_ids & tracked_jobs) / max(len(tracked_jobs), 1) * 100,
            "all_jobs": tracked_jobs | local_job_ids
        }
    
    def update_job_status(self, job_id: str, new_status: JobStatus, notes: str = ""):
        """Update job status and save to enhanced tracker"""
        records = self.load_status_tracker()
        
        now = datetime.now()
        
        if job_id in records:
            record = records[job_id]
            record.status = new_status
            record.last_checked = now
            record.notes = notes
            if new_status in [JobStatus.ACTIVE]:
                record.last_seen = now
        else:
            # Create new record
            local_files = self.get_local_job_files()
            file_path = local_files.get(job_id)
            
            if file_path:
                analysis = self.analyze_job_file(job_id, file_path)
                record = JobRecord(
                    job_id=job_id,
                    status=new_status,
                    last_seen=now if new_status == JobStatus.ACTIVE else now,
                    last_checked=now,
                    has_ai_analysis=analysis.get('has_ai_analysis', False),
                    file_exists=True,
                    file_size=analysis.get('file_size', 0),
                    checksum=analysis.get('checksum'),
                    notes=notes
                )
            else:
                record = JobRecord(
                    job_id=job_id,
                    status=new_status,
                    last_seen=now if new_status == JobStatus.ACTIVE else now,
                    last_checked=now,
                    has_ai_analysis=False,
                    file_exists=False,
                    file_size=0,
                    notes=notes
                )
            
            records[job_id] = record
        
        self.save_status_tracker(records)
        logger.info(f"Updated job {job_id} status to {new_status.value}: {notes}")
    
    def mark_job_removed_from_site(self, job_id: str, reason: str = "Job no longer available on website"):
        """Answer Question 2: Handle jobs removed from site"""
        self.update_job_status(job_id, JobStatus.REMOVED_FROM_SITE, reason)
        
        # Optionally rename the file to indicate removal
        local_files = self.get_local_job_files()
        if job_id in local_files:
            old_path = local_files[job_id]
            new_path = old_path.parent / f"{old_path.stem}_removed.json"
            
            try:
                old_path.rename(new_path)
                logger.info(f"Renamed job file {old_path} to {new_path}")
            except Exception as e:
                logger.error(f"Failed to rename job file {old_path}: {e}")
    
    def comprehensive_integrity_check(self) -> Dict:
        """Comprehensive integrity check addressing all failure modes"""
        logger.info("🔍 Starting comprehensive integrity check...")
        
        # Get all data sources
        discrepancies = self.detect_discrepancies()
        local_files = self.get_local_job_files()
        status_records = self.load_status_tracker()
        
        # Analysis results
        results = {
            "timestamp": datetime.now().isoformat(),
            "discrepancies": discrepancies,
            "data_integrity": {
                "files_analyzed": 0,
                "files_with_ai_analysis": 0,
                "files_corrupted": 0,
                "files_suspicious": 0
            },
            "failure_modes_detected": [],
            "recommendations": []
        }
        
        # Analyze each file
        corrupted_files = []
        suspicious_files = []
        ai_analysis_count = 0
        
        for job_id, file_path in local_files.items():
            analysis = self.analyze_job_file(job_id, file_path)
            results["data_integrity"]["files_analyzed"] += 1
            
            if analysis.get("error"):
                corrupted_files.append({
                    "job_id": job_id,
                    "error": analysis["error"],
                    "file_path": str(file_path)
                })
                results["data_integrity"]["files_corrupted"] += 1
            
            if analysis.get("has_ai_analysis"):
                ai_analysis_count += 1
                results["data_integrity"]["files_with_ai_analysis"] += 1
            
            # Check for suspicious patterns
            if analysis.get("file_size", 0) < 1000:  # Very small files
                suspicious_files.append({
                    "job_id": job_id,
                    "reason": "File too small",
                    "file_size": analysis.get("file_size", 0)
                })
                results["data_integrity"]["files_suspicious"] += 1
        
        # Detect failure modes
        if len(discrepancies["missing_files"]) > 0:
            results["failure_modes_detected"].append({
                "mode": "Missing Files",
                "severity": "HIGH",
                "count": len(discrepancies["missing_files"]),
                "description": "Jobs tracked in progress tracker but files missing"
            })
        
        if len(discrepancies["unexpected_files"]) > 0:
            results["failure_modes_detected"].append({
                "mode": "Unexpected Files",
                "severity": "MEDIUM",
                "count": len(discrepancies["unexpected_files"]),
                "description": "Job files exist but not tracked in progress tracker"
            })
        
        if len(corrupted_files) > 0:
            results["failure_modes_detected"].append({
                "mode": "Corrupted Files",
                "severity": "HIGH",
                "count": len(corrupted_files),
                "description": "Files cannot be read or parsed"
            })
        
        # Calculate data loss percentage
        total_files = results["data_integrity"]["files_analyzed"]
        data_loss_percentage = (total_files - ai_analysis_count) / max(total_files, 1) * 100
        
        if data_loss_percentage > 50:
            results["failure_modes_detected"].append({
                "mode": "Major Data Loss",
                "severity": "CRITICAL",
                "percentage": data_loss_percentage,
                "description": f"{data_loss_percentage:.1f}% of jobs missing AI analysis"
            })
        
        # Generate recommendations
        if len(discrepancies["missing_files"]) > 0:
            results["recommendations"].append("Investigate missing job files and restore from backup if available")
        
        if data_loss_percentage > 0:
            results["recommendations"].append("Run AI processing pipeline on jobs missing analysis")
        
        if len(corrupted_files) > 0:
            results["recommendations"].append("Fix or restore corrupted job files")
        
        results["recommendations"].append("Implement regular automated integrity checks")
        results["recommendations"].append("Create backup mechanism for critical job data")
        
        # Save integrity log
        try:
            with open(self.integrity_log, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save integrity log: {e}")
        
        return results
    
    def get_jobs_by_status(self, status: JobStatus) -> List[str]:
        """Get all jobs with a specific status"""
        records = self.load_status_tracker()
        return [job_id for job_id, record in records.items() if record.status == status]
    
    def sync_with_progress_tracker(self):
        """Synchronize enhanced status tracker with original progress tracker"""
        logger.info("🔄 Synchronizing with progress tracker...")
        
        progress_data = self.load_progress_tracker()
        tracked_jobs = set(progress_data.get("jobs_processed", []))
        local_files = self.get_local_job_files()
        status_records = self.load_status_tracker()
        
        updated_count = 0
        
        # Update status for all tracked jobs
        for job_id in tracked_jobs:
            if job_id not in status_records:
                if job_id in local_files:
                    analysis = self.analyze_job_file(job_id, local_files[job_id])
                    status_records[job_id] = JobRecord(
                        job_id=job_id,
                        status=JobStatus.ACTIVE,
                        last_seen=datetime.now(),
                        last_checked=datetime.now(),
                        has_ai_analysis=analysis.get('has_ai_analysis', False),
                        file_exists=True,
                        file_size=analysis.get('file_size', 0),
                        checksum=analysis.get('checksum'),
                        notes="Synced from progress tracker"
                    )
                    updated_count += 1
                else:
                    # Job tracked but file missing
                    status_records[job_id] = JobRecord(
                        job_id=job_id,
                        status=JobStatus.UNKNOWN,
                        last_seen=datetime.now(),
                        last_checked=datetime.now(),
                        has_ai_analysis=False,
                        file_exists=False,
                        file_size=0,
                        notes="Missing file - tracked but not found"
                    )
                    updated_count += 1
        
        # Handle unexpected files
        for job_id, file_path in local_files.items():
            if job_id not in tracked_jobs and job_id not in status_records:
                analysis = self.analyze_job_file(job_id, file_path)
                status_records[job_id] = JobRecord(
                    job_id=job_id,
                    status=JobStatus.UNKNOWN,
                    last_seen=datetime.now(),
                    last_checked=datetime.now(),
                    has_ai_analysis=analysis.get('has_ai_analysis', False),
                    file_exists=True,
                    file_size=analysis.get('file_size', 0),
                    checksum=analysis.get('checksum'),
                    notes="Unexpected file - exists but not tracked"
                )
                updated_count += 1
        
        self.save_status_tracker(status_records)
        logger.info(f"✅ Sync complete. Updated {updated_count} job records.")

def main():
    """CLI interface for enhanced job status management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Job Status Manager")
    parser.add_argument("--check", action="store_true", help="Run comprehensive integrity check")
    parser.add_argument("--sync", action="store_true", help="Sync with progress tracker")
    parser.add_argument("--status", help="Get jobs by status")
    parser.add_argument("--mark-removed", help="Mark job as removed from site")
    
    args = parser.parse_args()
    
    manager = EnhancedJobStatusManager()
    
    if args.check:
        results = manager.comprehensive_integrity_check()
        print("\n🔍 COMPREHENSIVE INTEGRITY CHECK RESULTS")
        print("=" * 60)
        print(f"Files analyzed: {results['data_integrity']['files_analyzed']}")
        print(f"Files with AI analysis: {results['data_integrity']['files_with_ai_analysis']}")
        print(f"Files corrupted: {results['data_integrity']['files_corrupted']}")
        print(f"Failure modes detected: {len(results['failure_modes_detected'])}")
        
        for mode in results["failure_modes_detected"]:
            print(f"  🚨 {mode['mode']} ({mode['severity']}): {mode['description']}")
        
        print(f"\n📋 Recommendations:")
        for rec in results["recommendations"]:
            print(f"  • {rec}")
    
    elif args.sync:
        manager.sync_with_progress_tracker()
    
    elif args.status:
        try:
            status = JobStatus(args.status)
            jobs = manager.get_jobs_by_status(status)
            print(f"Jobs with status '{status.value}': {len(jobs)}")
            for job_id in jobs[:10]:  # Show first 10
                print(f"  {job_id}")
            if len(jobs) > 10:
                print(f"  ... and {len(jobs) - 10} more")
        except ValueError:
            print(f"Invalid status. Valid options: {[s.value for s in JobStatus]}")
    
    elif args.mark_removed:
        manager.mark_job_removed_from_site(args.mark_removed)
        print(f"Marked job {args.mark_removed} as removed from site")

if __name__ == "__main__":
    main()
