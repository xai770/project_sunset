#!/usr/bin/env python3
"""
Processing State Manager - Track specialist versions without polluting job data
==============================================================================

This system tracks which jobs have been processed with which specialist versions,
enabling smart reprocessing without coupling job data to processing infrastructure.
"""

import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging
from datetime import datetime
from pathlib import Path

@dataclass
class ProcessingRecord:
    """Record of a job being processed by specialists"""
    job_id: str
    timestamp: str
    specialists_used: Dict[str, str]  # specialist_name -> version
    processing_times: Dict[str, float]  # specialist_name -> seconds
    results_summary: Dict[str, str]  # specialist_name -> decision/result
    pipeline_version: str = "v7.0"

class ProcessingManifest:
    """Manages processing state separate from job data"""
    
    def __init__(self, manifest_path: str = "/home/xai/Documents/sandy/data/processing_manifest.json"):
        self.manifest_path = Path(manifest_path)
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict:
        """Load existing manifest or create new one"""
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        return {
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "current_specialist_versions": {
                "domain_classification": "v1_1",
                "location_validation": "v1_0", 
                "job_fitness_evaluator": "v2_0"
            },
            "processing_records": {},
            "reprocessing_history": []
        }
    
    def save_manifest(self):
        """Save manifest to disk"""
        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def record_processing(self, record: ProcessingRecord):
        """Record that a job has been processed"""
        self.manifest["processing_records"][record.job_id] = asdict(record)
        self.save_manifest()
    
    def needs_reprocessing(self, job_id: str) -> Dict[str, bool]:
        """Check if job needs reprocessing for any specialists"""
        if job_id not in self.manifest["processing_records"]:
            return {"all": True}
        
        record = self.manifest["processing_records"][job_id]
        current_versions = self.manifest["current_specialist_versions"]
        used_versions = record["specialists_used"]
        
        needs_reprocessing = {}
        for specialist, current_version in current_versions.items():
            used_version = used_versions.get(specialist, "none")
            needs_reprocessing[specialist] = (used_version != current_version)
        
        return needs_reprocessing
    
    def get_outdated_jobs(self) -> List[str]:
        """Get list of jobs that need reprocessing"""
        outdated = []
        for job_id in self.manifest["processing_records"]:
            if any(self.needs_reprocessing(job_id).values()):
                outdated.append(job_id)
        return outdated
    
    def update_specialist_version(self, specialist_name: str, new_version: str):
        """Update current version of a specialist"""
        old_version = self.manifest["current_specialist_versions"].get(specialist_name, "unknown")
        self.manifest["current_specialist_versions"][specialist_name] = new_version
        
        # Log the version update
        self.manifest["reprocessing_history"].append({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "action": "version_update",
            "specialist": specialist_name,
            "old_version": old_version,
            "new_version": new_version,
            "jobs_affected": len(self.get_outdated_jobs())
        })
        
        self.save_manifest()
    
    def get_processing_stats(self) -> Dict:
        """Get processing statistics"""
        records = self.manifest["processing_records"]
        if not records:
            return {"total_jobs": 0}
        
        total_jobs = len(records)
        outdated_jobs = len(self.get_outdated_jobs())
        
        # Calculate average processing times
        avg_times = {}
        for specialist in self.manifest["current_specialist_versions"]:
            times = []
            for record in records.values():
                if specialist in record.get("processing_times", {}):
                    times.append(record["processing_times"][specialist])
            avg_times[specialist] = sum(times) / len(times) if times else 0
        
        return {
            "total_jobs": total_jobs,
            "up_to_date": total_jobs - outdated_jobs,
            "need_reprocessing": outdated_jobs,
            "average_processing_times": avg_times,
            "current_versions": self.manifest["current_specialist_versions"]
        }
    
    def detect_and_recover_missing_jobs(self, max_recovery: int = 10, enable_recovery: bool = True) -> int:
        """
        Detect and recover missing jobs from the processing manifest
        
        Args:
            max_recovery: Maximum number of jobs to recover
            enable_recovery: Whether to actually perform recovery
            
        Returns:
            int: Number of jobs recovered
        """
        logger = logging.getLogger(__name__)
        
        job_dir = Path("/home/xai/Documents/sandy/data/postings")
        
        # Find missing jobs
        missing_jobs = []
        for job_file in job_dir.glob("*.json"):
            job_id = job_file.stem.replace("job", "")
            if job_id not in self.manifest["processing_records"]:
                missing_jobs.append(job_id)
        
        if not missing_jobs:
            return 0
            
        if not enable_recovery:
            return len(missing_jobs)
            
        # Limit recovery
        missing_jobs = missing_jobs[:max_recovery]
        
        # Recover jobs
        recovered = 0
        for job_id in missing_jobs:
            try:
                job_file = job_dir / f"job{job_id}.json"
                if job_file.exists():
                    # Add job to manifest
                    record = ProcessingRecord(
                        job_id=job_id,
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        specialists_used={},
                        processing_times={},
                        results_summary={}
                    )
                    self.manifest["processing_records"][job_id] = asdict(record)
                    recovered += 1
            except Exception as e:
                logger.error(f"Error recovering job {job_id}: {e}")
                
        self.save_manifest()
        return recovered

# Export helper functions
def detect_and_recover_missing_jobs(max_recovery: int = 10, enable_recovery: bool = True) -> int:
    """
    Module-level helper to detect and recover missing jobs
    
    Args:
        max_recovery: Maximum number of jobs to recover
        enable_recovery: Whether to actually perform recovery
        
    Returns:
        int: Number of jobs recovered
    """
    manifest = ProcessingManifest()
    return manifest.detect_and_recover_missing_jobs(
        max_recovery=max_recovery,
        enable_recovery=enable_recovery
    )

# CLI interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Processing State Manager')
    parser.add_argument('--status', action='store_true', help='Show processing status')
    parser.add_argument('--outdated', action='store_true', help='List outdated jobs')
    parser.add_argument('--update-version', nargs=2, metavar=('SPECIALIST', 'VERSION'), 
                       help='Update specialist version')
    
    args = parser.parse_args()
    
    manifest = ProcessingManifest()
    
    if args.status:
        stats = manifest.get_processing_stats()
        print("📊 PROCESSING STATUS")
        print("=" * 30)
        print(f"Total Jobs: {stats['total_jobs']}")
        print(f"Up to Date: {stats['up_to_date']}")
        print(f"Need Reprocessing: {stats['need_reprocessing']}")
        print(f"\nCurrent Specialist Versions:")
        for specialist, version in stats['current_versions'].items():
            print(f"  {specialist}: {version}")
        
        if stats['average_processing_times']:
            print(f"\nAverage Processing Times:")
            for specialist, time_sec in stats['average_processing_times'].items():
                print(f"  {specialist}: {time_sec:.2f}s")
    
    elif args.outdated:
        outdated = manifest.get_outdated_jobs()
        print(f"📋 OUTDATED JOBS ({len(outdated)})")
        print("=" * 30)
        for job_id in outdated[:10]:  # Show first 10
            needed = manifest.needs_reprocessing(job_id)
            specialists_needed = [k for k, v in needed.items() if v and k != 'all']
            print(f"Job {job_id}: {', '.join(specialists_needed)}")
        
        if len(outdated) > 10:
            print(f"... and {len(outdated) - 10} more")
    
    elif args.update_version:
        specialist, version = args.update_version
        manifest.update_specialist_version(specialist, version)
        print(f"✅ Updated {specialist} to {version}")
        
        outdated = manifest.get_outdated_jobs()
        print(f"📊 {len(outdated)} jobs now need reprocessing")

if __name__ == "__main__":
    main()

# Export names for external use
__all__ = ['ProcessingRecord', 'ProcessingManifest', 'detect_and_recover_missing_jobs']
