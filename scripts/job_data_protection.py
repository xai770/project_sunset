#!/usr/bin/env python3
"""
Enhanced Job Data Protection System
==================================

Provides comprehensive protection against data loss during job processing operations.
Includes backup mechanisms, validation checks, and recovery procedures.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class JobDataProtectionSystem:
    """Comprehensive system to protect against job data loss"""
    
    def __init__(self, base_path: str = "/home/xai/Documents/sunset"):
        self.base_path = Path(base_path)
        self.jobs_dir = self.base_path / "data" / "postings"
        self.backup_dir = self.base_path / "data" / "postings_BACKUPS"
        self.progress_file = self.base_path / "data" / "job_scans" / "search_api_scan_progress.json"
        
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_pre_operation_backup(self, operation_name: str) -> str:
        """Create backup before destructive operations"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"BEFORE_{operation_name}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        logger.info(f"🔒 Creating backup: {backup_name}")
        
        try:
            # Copy entire postings directory
            shutil.copytree(self.jobs_dir, backup_path, dirs_exist_ok=True)
            
            # Also backup progress tracker
            if self.progress_file.exists():
                shutil.copy2(self.progress_file, backup_path / "search_api_scan_progress.json")
            
            logger.info(f"✅ Backup created: {backup_path}")
            return str(backup_path)
        
        except Exception as e:
            logger.error(f"❌ Failed to create backup: {e}")
            raise
    
    def validate_job_file_integrity(self, job_file: Path) -> Dict:
        """Validate a job file for data integrity"""
        if not job_file.exists():
            return {"valid": False, "error": "File does not exist"}
        
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            # Check for critical AI analysis fields
            ai_analysis_fields = [
                'llama32_evaluation',
                'cv_analysis', 
                'skill_match',
                'domain_enhanced_match',
                'ai_processed'
            ]
            
            has_ai_analysis = any(field in job_data for field in ai_analysis_fields)
            
            # Check for non-placeholder descriptions
            description = job_data.get('web_details', {}).get('concise_description', '')
            has_real_description = (
                description.strip() and 
                'placeholder for a concise description' not in description.lower()
            )
            
            validation = {
                "valid": True,
                "has_ai_analysis": has_ai_analysis,
                "has_real_description": has_real_description,
                "file_size": job_file.stat().st_size,
                "ai_fields_present": [field for field in ai_analysis_fields if field in job_data],
                "risk_level": "low" if has_ai_analysis else "high"
            }
            
            return validation
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def safe_job_update(self, job_id: str, new_data: Dict, preserve_ai: bool = True) -> bool:
        """Safely update a job file with AI analysis preservation"""
        job_file = self.jobs_dir / f"job{job_id}.json"
        
        if not job_file.exists():
            # New file, safe to create
            with open(job_file, 'w') as f:
                json.dump(new_data, f, indent=2)
            logger.info(f"✅ Created new job file: {job_id}")
            return True
        
        # File exists, check if we need to preserve AI analysis
        if preserve_ai:
            validation = self.validate_job_file_integrity(job_file)
            
            if validation.get("has_ai_analysis"):
                # Load existing data and merge with new data
                with open(job_file, 'r') as f:
                    existing_data = json.load(f)
                
                # Preserve AI analysis fields
                ai_fields_to_preserve = [
                    'llama32_evaluation', 'cv_analysis', 'skill_match', 
                    'domain_enhanced_match', 'ai_processed'
                ]
                
                for field in ai_fields_to_preserve:
                    if field in existing_data:
                        new_data[field] = existing_data[field]
                
                # Preserve concise descriptions that aren't placeholders
                existing_desc = existing_data.get('web_details', {}).get('concise_description', '')
                if (existing_desc.strip() and 
                    'placeholder for a concise description' not in existing_desc.lower()):
                    if 'web_details' not in new_data:
                        new_data['web_details'] = {}
                    new_data['web_details']['concise_description'] = existing_desc
                
                logger.info(f"🔒 Preserved AI analysis for job {job_id}")
        
        # Create backup of original file
        backup_file = job_file.with_suffix('.bak')
        shutil.copy2(job_file, backup_file)
        
        try:
            # Write new data
            with open(job_file, 'w') as f:
                json.dump(new_data, f, indent=2)
            
            # Remove backup on success
            backup_file.unlink()
            logger.info(f"✅ Safely updated job file: {job_id}")
            return True
            
        except Exception as e:
            # Restore from backup on failure
            shutil.copy2(backup_file, job_file)
            backup_file.unlink()
            logger.error(f"❌ Failed to update job {job_id}, restored from backup: {e}")
            return False
    
    def detect_data_loss_risk(self) -> Dict:
        """Analyze current job files for data loss risk"""
        job_files = list(self.jobs_dir.glob("job*.json"))
        
        risk_analysis = {
            "total_jobs": len(job_files),
            "high_risk_jobs": [],
            "jobs_with_ai": 0,
            "jobs_without_ai": 0,
            "validation_errors": []
        }
        
        for job_file in job_files:
            validation = self.validate_job_file_integrity(job_file)
            
            if not validation.get("valid"):
                risk_analysis["validation_errors"].append({
                    "job_id": job_file.stem.replace('job', ''),
                    "error": validation.get("error")
                })
                continue
            
            if validation.get("has_ai_analysis"):
                risk_analysis["jobs_with_ai"] += 1
            else:
                risk_analysis["jobs_without_ai"] += 1
                risk_analysis["high_risk_jobs"].append({
                    "job_id": job_file.stem.replace('job', ''),
                    "reason": "No AI analysis present"
                })
        
        risk_analysis["data_loss_risk"] = (
            "HIGH" if risk_analysis["jobs_without_ai"] > risk_analysis["jobs_with_ai"] * 0.5 
            else "MEDIUM" if risk_analysis["jobs_without_ai"] > 0 
            else "LOW"
        )
        
        return risk_analysis
    
    def generate_protection_report(self) -> str:
        """Generate comprehensive protection report"""
        risk_analysis = self.detect_data_loss_risk()
        
        report = [
            "🛡️  JOB DATA PROTECTION REPORT",
            "=" * 50,
            f"📊 Total jobs: {risk_analysis['total_jobs']}",
            f"✅ Jobs with AI analysis: {risk_analysis['jobs_with_ai']}",
            f"⚠️  Jobs without AI analysis: {risk_analysis['jobs_without_ai']}",
            f"🚨 Overall risk level: {risk_analysis['data_loss_risk']}",
            ""
        ]
        
        if risk_analysis["high_risk_jobs"]:
            report.append("🔴 HIGH RISK JOBS:")
            for job in risk_analysis["high_risk_jobs"][:10]:  # Show first 10
                report.append(f"   - Job {job['job_id']}: {job['reason']}")
            if len(risk_analysis["high_risk_jobs"]) > 10:
                report.append(f"   ... and {len(risk_analysis['high_risk_jobs']) - 10} more")
            report.append("")
        
        if risk_analysis["validation_errors"]:
            report.append("❌ VALIDATION ERRORS:")
            for error in risk_analysis["validation_errors"]:
                report.append(f"   - Job {error['job_id']}: {error['error']}")
            report.append("")
        
        report.extend([
            "💡 RECOMMENDATIONS:",
            "1. Create backup before any bulk operations",
            "2. Use safe_job_update() for individual file updates", 
            "3. Monitor high-risk jobs for data loss",
            "4. Validate files after bulk operations"
        ])
        
        return "\n".join(report)

# Enhanced process_and_save_jobs with protection
def protected_process_and_save_jobs(jobs, output_dir, generate_daily_summary=False, force_reprocess=False):
    """Enhanced version of process_and_save_jobs with data protection"""
    
    # Initialize protection system
    protection = JobDataProtectionSystem()
    
    # Create pre-operation backup
    backup_path = protection.create_pre_operation_backup("JOB_PROCESSING")
    
    try:
        # Import and call original function
        from run_pipeline.core.fetch.job_processing import process_and_save_jobs
        
        logger.info("🛡️  Using protected job processing with AI analysis preservation")
        
        # Process jobs with existing protection logic
        processed_count, skipped_count = process_and_save_jobs(
            jobs, output_dir, generate_daily_summary, force_reprocess
        )
        
        # Post-operation validation
        risk_analysis = protection.detect_data_loss_risk()
        
        if risk_analysis["data_loss_risk"] == "HIGH":
            logger.warning(f"⚠️  High data loss risk detected after processing!")
            logger.warning(f"Backup available at: {backup_path}")
        
        logger.info(f"✅ Protected processing complete: {processed_count} processed, {skipped_count} preserved")
        return processed_count, skipped_count
        
    except Exception as e:
        logger.error(f"❌ Error during protected processing: {e}")
        logger.info(f"💾 Backup available for recovery at: {backup_path}")
        raise

if __name__ == "__main__":
    # Example usage
    protection = JobDataProtectionSystem()
    report = protection.generate_protection_report()
    print(report)
