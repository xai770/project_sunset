#!/usr/bin/env python3
"""
Failure Tracker Component
========================

Handles tracking and managing job processing failures.
Implements retry logic with exponential backoff.
"""

import os
import json
import sys
import time
from typing import Dict, Any, Optional
from pathlib import Path

# Get paths - handle both module and direct execution
try:
    from run_pipeline.config.paths import JOB_DATA_DIR
except ImportError:
    # For direct execution, add project root to path
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from run_pipeline.config.paths import JOB_DATA_DIR


class FailureTracker:
    """Handles job failure tracking and retry logic"""
    
    MAX_ATTEMPTS = 3
    
    @staticmethod
    def check_failure_status(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if job has exceeded failure threshold.
        
        Args:
            job_data: The job data dictionary
            
        Returns:
            Dictionary with failure status information
        """
        failure_tracking = job_data.get("failure_tracking", {})
        failed_attempts = failure_tracking.get("failed_attempts", 0)
        
        return {
            "should_skip": failed_attempts >= FailureTracker.MAX_ATTEMPTS,
            "failed_attempts": failed_attempts,
            "max_attempts": FailureTracker.MAX_ATTEMPTS,
            "last_failure_date": failure_tracking.get("last_failure_date"),
            "last_error": failure_tracking.get("last_error")
        }
    
    @staticmethod
    def track_job_failure(job_id: str, error_message: str) -> None:
        """
        Track a job failure to prevent infinite retry loops.
        
        Args:
            job_id: The job ID that failed
            error_message: The error message from the failure
        """
        try:
            job_path = os.path.join(JOB_DATA_DIR, f"job{job_id}.json")
            
            # Load existing job data
            with open(job_path, "r", encoding="utf-8") as jf:
                job_data = json.load(jf)
            
            # Initialize or update failure tracking
            failure_tracking = job_data.get("failure_tracking", {})
            failed_attempts = failure_tracking.get("failed_attempts", 0) + 1
            
            # Update failure tracking
            failure_tracking.update({
                "failed_attempts": failed_attempts,
                "last_failure_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_error": error_message[:500],  # Truncate very long errors
                "failure_history": failure_tracking.get("failure_history", [])
            })
            
            # Add this failure to history (keep last 5)
            failure_history = failure_tracking.get("failure_history", [])
            failure_history.append({
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error": error_message[:200]  # Shorter for history
            })
            
            # Keep only last 5 failures in history
            if len(failure_history) > 5:
                failure_history = failure_history[-5:]
            
            failure_tracking["failure_history"] = failure_history
            job_data["failure_tracking"] = failure_tracking
            
            # Save updated job data
            with open(job_path, "w", encoding="utf-8") as jf:
                json.dump(job_data, jf, indent=2)
            
            print(f"📊 Tracked failure for job {job_id} (attempt {failed_attempts}/{FailureTracker.MAX_ATTEMPTS})")
            
            if failed_attempts >= FailureTracker.MAX_ATTEMPTS:
                print(f"💀 Job {job_id} has reached maximum failures - will be permanently skipped")
                
        except Exception as e:
            print(f"Error tracking failure for job {job_id}: {e}")
    
    @staticmethod
    def reset_job_failures(job_id: str) -> bool:
        """
        Reset failure tracking for a job (useful for debugging or manual intervention).
        
        Args:
            job_id: The job ID to reset failures for
            
        Returns:
            True if reset was successful, False otherwise
        """
        try:
            job_path = os.path.join(JOB_DATA_DIR, f"job{job_id}.json")
            
            # Load existing job data
            with open(job_path, "r", encoding="utf-8") as jf:
                job_data = json.load(jf)
            
            # Remove failure tracking
            if "failure_tracking" in job_data:
                del job_data["failure_tracking"]
                
                # Save updated job data
                with open(job_path, "w", encoding="utf-8") as jf:
                    json.dump(job_data, jf, indent=2)
                
                print(f"✅ Reset failure tracking for job {job_id}")
                return True
            else:
                print(f"ℹ️ Job {job_id} has no failure tracking to reset")
                return True
                
        except Exception as e:
            print(f"Error resetting failures for job {job_id}: {e}")
            return False
    
    @staticmethod
    def clear_failure_tracking(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clear failure tracking from job data (called on successful processing).
        
        Args:
            job_data: The job data dictionary
            
        Returns:
            Updated job data with failure tracking removed
        """
        if "failure_tracking" in job_data:
            del job_data["failure_tracking"]
        return job_data
    
    @staticmethod
    def get_failure_summary() -> Dict[str, Any]:
        """
        Get a summary of all failed jobs in the system.
        
        Returns:
            Dictionary with failure statistics
        """
        try:
            failed_jobs = []
            permanently_failed = []
            
            # Scan all job files for failure tracking
            for filename in os.listdir(JOB_DATA_DIR):
                if filename.startswith("job") and filename.endswith(".json"):
                    job_id = filename.replace("job", "").replace(".json", "")
                    try:
                        job_path = os.path.join(JOB_DATA_DIR, filename)
                        with open(job_path, "r", encoding="utf-8") as jf:
                            job_data = json.load(jf)
                        
                        failure_tracking = job_data.get("failure_tracking", {})
                        failed_attempts = failure_tracking.get("failed_attempts", 0)
                        
                        if failed_attempts > 0:
                            job_info = {
                                "job_id": job_id,
                                "failed_attempts": failed_attempts,
                                "last_failure_date": failure_tracking.get("last_failure_date"),
                                "last_error": failure_tracking.get("last_error", "Unknown")[:100]
                            }
                            
                            if failed_attempts >= FailureTracker.MAX_ATTEMPTS:
                                permanently_failed.append(job_info)
                            else:
                                failed_jobs.append(job_info)
                                
                    except Exception as e:
                        print(f"Error reading job {job_id}: {e}")
            
            return {
                "total_failed": len(failed_jobs),
                "permanently_failed": len(permanently_failed),
                "failed_jobs": failed_jobs,
                "permanently_failed_jobs": permanently_failed
            }
            
        except Exception as e:
            print(f"Error getting failure summary: {e}")
            return {"error": str(e)}
