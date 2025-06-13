#!/usr/bin/env python3
"""
Job Data Recovery and Monitoring System
======================================

Provides comprehensive recovery procedures and continuous monitoring
to prevent and recover from data loss incidents.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
import subprocess
import logging

logger = logging.getLogger(__name__)

class JobDataRecoverySystem:
    """Comprehensive recovery system for job data loss incidents"""
    
    def __init__(self, base_path: str = "/home/xai/Documents/sunset"):
        self.base_path = Path(base_path)
        self.jobs_dir = self.base_path / "data" / "postings"
        self.backup_dirs = [
            self.base_path / "data" / "postings_BACKUP_20250612_124835",
            self.base_path / "data" / "postings_BACKUP_20250612_125111", 
            self.base_path / "data" / "postings_BACKUP_20250612_131915",
            self.base_path / "data" / "postings_BAK",
            self.base_path / "data" / "postings_BAK_20250527_202556",
            self.base_path / "data" / "postings_BAK_20250527_202749",
            self.base_path / "data" / "postings_BAK_20250610_201631",
            self.base_path / "data" / "postings_PHASE7_BACKUP_20250611_055426",
            self.base_path / "data" / "postings_BACKUPS"
        ]
        self.logs_dir = self.base_path / "logs"
        
        # Create logs directory
        self.logs_dir.mkdir(exist_ok=True)
    
    def scan_available_backups(self) -> List[Dict]:
        """Scan all backup directories for available recovery data"""
        backups = []
        
        for backup_dir in self.backup_dirs:
            if backup_dir.exists():
                job_files = list(backup_dir.glob("job*.json"))
                
                if job_files:
                    # Analyze backup quality
                    ai_analysis_count = 0
                    total_files = len(job_files)
                    
                    # Sample first 10 files to check for AI analysis
                    for job_file in job_files[:10]:
                        try:
                            with open(job_file, 'r') as f:
                                job_data = json.load(f)
                            
                            if any(field in job_data for field in ['llama32_evaluation', 'cv_analysis', 'skill_match']):
                                ai_analysis_count += 1
                        except:
                            pass
                    
                    # Estimate AI analysis percentage
                    ai_percentage = (ai_analysis_count / min(10, total_files)) * 100 if total_files > 0 else 0
                    
                    backups.append({
                        "path": str(backup_dir),
                        "name": backup_dir.name,
                        "job_count": total_files,
                        "ai_analysis_percentage": ai_percentage,
                        "quality_score": ai_percentage,
                        "last_modified": datetime.fromtimestamp(backup_dir.stat().st_mtime).isoformat()
                    })
        
        # Sort by quality score (AI analysis percentage) descending
        backups.sort(key=lambda x: x["quality_score"], reverse=True)
        return backups
    
    def find_best_backup_for_job(self, job_id: str) -> Optional[Dict]:
        """Find the best backup containing AI analysis for a specific job"""
        backups = self.scan_available_backups()
        
        for backup in backups:
            backup_path = Path(backup["path"])
            job_file = backup_path / f"job{job_id}.json"
            
            if job_file.exists():
                try:
                    with open(job_file, 'r') as f:
                        job_data = json.load(f)
                    
                    # Check for AI analysis
                    has_ai = any(field in job_data for field in ['llama32_evaluation', 'cv_analysis', 'skill_match', 'domain_enhanced_match'])
                    
                    if has_ai:
                        return {
                            "backup_info": backup,
                            "job_file_path": str(job_file),
                            "has_ai_analysis": True,
                            "ai_fields": [field for field in ['llama32_evaluation', 'cv_analysis', 'skill_match', 'domain_enhanced_match'] if field in job_data]
                        }
                        
                except Exception as e:
                    logger.error(f"Error reading job {job_id} from backup {backup['name']}: {e}")
                    continue
        
        return None
    
    def recover_single_job(self, job_id: str, restore_to_current: bool = False) -> Dict:
        """Recover a single job from the best available backup"""
        
        best_backup = self.find_best_backup_for_job(job_id)
        
        if not best_backup:
            return {
                "success": False,
                "error": f"No backup found for job {job_id} with AI analysis"
            }
        
        try:
            source_file = Path(best_backup["job_file_path"])
            
            if restore_to_current:
                # Restore to current jobs directory
                target_file = self.jobs_dir / f"job{job_id}.json"
                
                # Create backup of current file if it exists
                if target_file.exists():
                    backup_file = target_file.with_suffix(f'.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                    shutil.copy2(target_file, backup_file)
                
                shutil.copy2(source_file, target_file)
                logger.info(f"✅ Recovered job {job_id} to {target_file}")
            
            return {
                "success": True,
                "job_id": job_id,
                "source_backup": best_backup["backup_info"]["name"],
                "ai_fields_recovered": best_backup["ai_fields"],
                "target_file": str(target_file) if restore_to_current else "preview_only"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to recover job {job_id}: {e}"
            }
    
    def batch_recovery_analysis(self, job_ids: List[str] = None) -> Dict:
        """Analyze recovery potential for multiple jobs"""
        
        if job_ids is None:
            # Get all jobs from current directory that might need recovery
            current_jobs = list(self.jobs_dir.glob("job*.json"))
            job_ids = []
            
            for job_file in current_jobs:
                job_id = job_file.stem.replace('job', '')
                try:
                    with open(job_file, 'r') as f:
                        job_data = json.load(f)
                    
                    # Check if job lacks AI analysis
                    has_ai = any(field in job_data for field in ['llama32_evaluation', 'cv_analysis', 'skill_match'])
                    if not has_ai:
                        job_ids.append(job_id)
                except:
                    job_ids.append(job_id)  # Add jobs that can't be read
        
        recovery_analysis = {
            "total_jobs_analyzed": len(job_ids),
            "recoverable_jobs": [],
            "unrecoverable_jobs": [],
            "recovery_summary": {
                "can_recover": 0,
                "cannot_recover": 0,
                "total_ai_fields_recoverable": 0
            }
        }
        
        for job_id in job_ids:
            recovery_info = self.find_best_backup_for_job(job_id)
            
            if recovery_info:
                recovery_analysis["recoverable_jobs"].append({
                    "job_id": job_id,
                    "backup_source": recovery_info["backup_info"]["name"],
                    "ai_fields": recovery_info["ai_fields"]
                })
                recovery_analysis["recovery_summary"]["can_recover"] += 1
                recovery_analysis["recovery_summary"]["total_ai_fields_recoverable"] += len(recovery_info["ai_fields"])
            else:
                recovery_analysis["unrecoverable_jobs"].append(job_id)
                recovery_analysis["recovery_summary"]["cannot_recover"] += 1
        
        return recovery_analysis
    
    def execute_batch_recovery(self, job_ids: List[str], confirm: bool = False) -> Dict:
        """Execute batch recovery for multiple jobs"""
        
        if not confirm:
            return {
                "success": False,
                "error": "Batch recovery requires explicit confirmation (confirm=True)"
            }
        
        logger.info(f"🔄 Starting batch recovery for {len(job_ids)} jobs")
        
        # Create pre-recovery backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_recovery_backup = self.jobs_dir.parent / f"postings_PRE_RECOVERY_{timestamp}"
        shutil.copytree(self.jobs_dir, pre_recovery_backup)
        logger.info(f"📁 Created pre-recovery backup: {pre_recovery_backup}")
        
        results = {
            "pre_recovery_backup": str(pre_recovery_backup),
            "total_jobs": len(job_ids),
            "successful_recoveries": [],
            "failed_recoveries": [],
            "summary": {
                "success_count": 0,
                "failure_count": 0,
                "total_ai_fields_recovered": 0
            }
        }
        
        for job_id in job_ids:
            recovery_result = self.recover_single_job(job_id, restore_to_current=True)
            
            if recovery_result["success"]:
                results["successful_recoveries"].append(recovery_result)
                results["summary"]["success_count"] += 1
                results["summary"]["total_ai_fields_recovered"] += len(recovery_result.get("ai_fields_recovered", []))
                logger.info(f"✅ Recovered job {job_id}")
            else:
                results["failed_recoveries"].append(recovery_result)
                results["summary"]["failure_count"] += 1
                logger.error(f"❌ Failed to recover job {job_id}: {recovery_result['error']}")
        
        logger.info(f"🎯 Batch recovery complete: {results['summary']['success_count']}/{len(job_ids)} successful")
        return results
    
    def create_monitoring_dashboard(self) -> str:
        """Create a monitoring dashboard for job data health"""
        
        # Get current job analysis
        current_jobs = list(self.jobs_dir.glob("job*.json"))
        
        stats = {
            "total_jobs": len(current_jobs),
            "jobs_with_ai": 0,
            "jobs_without_ai": 0,
            "corrupted_jobs": 0,
            "recoverable_jobs": 0
        }
        
        jobs_needing_recovery = []
        
        for job_file in current_jobs:
            job_id = job_file.stem.replace('job', '')
            
            try:
                with open(job_file, 'r') as f:
                    job_data = json.load(f)
                
                # Check for AI analysis
                has_ai = any(field in job_data for field in ['llama32_evaluation', 'cv_analysis', 'skill_match'])
                
                if has_ai:
                    stats["jobs_with_ai"] += 1
                else:
                    stats["jobs_without_ai"] += 1
                    
                    # Check if recoverable
                    if self.find_best_backup_for_job(job_id):
                        stats["recoverable_jobs"] += 1
                        jobs_needing_recovery.append(job_id)
                        
            except Exception:
                stats["corrupted_jobs"] += 1
        
        # Calculate health metrics
        health_score = (stats["jobs_with_ai"] / max(stats["total_jobs"], 1)) * 100
        recovery_potential = (stats["recoverable_jobs"] / max(stats["jobs_without_ai"], 1)) * 100
        
        dashboard = [
            "🔍 JOB DATA HEALTH MONITORING DASHBOARD",
            "=" * 60,
            f"📊 Total jobs: {stats['total_jobs']}",
            f"✅ Jobs with AI analysis: {stats['jobs_with_ai']}",
            f"❌ Jobs without AI analysis: {stats['jobs_without_ai']}",
            f"💾 Recoverable from backups: {stats['recoverable_jobs']}",
            f"🔴 Corrupted/unreadable: {stats['corrupted_jobs']}",
            "",
            f"📈 Health Score: {health_score:.1f}%",
            f"🔄 Recovery Potential: {recovery_potential:.1f}%",
            "",
            "🎯 RECOMMENDATIONS:"
        ]
        
        if health_score < 50:
            dashboard.append("   🚨 CRITICAL: Health score below 50% - immediate recovery needed")
        elif health_score < 80:
            dashboard.append("   ⚠️  WARNING: Health score below 80% - recovery recommended")
        else:
            dashboard.append("   ✅ GOOD: Health score above 80%")
        
        if stats["recoverable_jobs"] > 0:
            dashboard.extend([
                "",
                f"💡 RECOVERY OPPORTUNITY: {stats['recoverable_jobs']} jobs can be recovered",
                "   To recover all jobs with available backups:",
                f"   python scripts/job_recovery.py --batch-recover {' '.join(jobs_needing_recovery[:10])}..."
            ])
        
        return "\n".join(dashboard)
    
    def generate_recovery_report(self) -> str:
        """Generate comprehensive recovery report"""
        
        # Scan backups
        backups = self.scan_available_backups()
        
        # Analyze recovery potential
        recovery_analysis = self.batch_recovery_analysis()
        
        # Create dashboard
        dashboard = self.create_monitoring_dashboard()
        
        report = [
            "🛠️  COMPREHENSIVE RECOVERY REPORT",
            "=" * 60,
            "",
            "📁 AVAILABLE BACKUPS:",
        ]
        
        for backup in backups[:5]:  # Show top 5 backups
            report.append(f"   {backup['name']}:")
            report.append(f"      Jobs: {backup['job_count']}, AI: {backup['ai_analysis_percentage']:.1f}%")
        
        report.extend([
            "",
            "🔄 RECOVERY ANALYSIS:",
            f"   Can recover: {recovery_analysis['recovery_summary']['can_recover']} jobs",
            f"   Cannot recover: {recovery_analysis['recovery_summary']['cannot_recover']} jobs",
            f"   Total AI fields recoverable: {recovery_analysis['recovery_summary']['total_ai_fields_recoverable']}",
            "",
            dashboard,
            "",
            "⚡ QUICK RECOVERY COMMANDS:",
            "   # Analyze recovery potential:",
            "   python scripts/job_recovery.py --analyze",
            "",
            "   # Recover specific job:",
            "   python scripts/job_recovery.py --recover-job 12345",
            "",
            "   # Batch recovery (use with caution):",
            "   python scripts/job_recovery.py --batch-recover --confirm"
        ])
        
        return "\n".join(report)

if __name__ == "__main__":
    # Example usage
    recovery = JobDataRecoverySystem()
    report = recovery.generate_recovery_report()
    print(report)
