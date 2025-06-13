#!/usr/bin/env python3
"""
Beautiful JSON Status Manager
Manages pipeline status for Project Sunset jobs with the numbered status system.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Pipeline status definitions
PIPELINE_STATES = {
    0: {"state": "error", "description": "Processing failed", "next_action": "manual_intervention"},
    1: {"state": "fetched", "description": "Basic job data retrieved", "next_action": "enhance_description"},
    2: {"state": "enhanced", "description": "Rich job description added", "next_action": "process_with_llm"},
    3: {"state": "processed", "description": "LLM evaluation completed", "next_action": "export_to_excel"},
    4: {"state": "exported", "description": "Included in Excel feedback", "next_action": "generate_cover_letter"},
    5: {"state": "cover_generated", "description": "Cover letter created", "next_action": "email_to_reviewer"},
    6: {"state": "under_review", "description": "Sent to human reviewer", "next_action": "await_feedback"},
    7: {"state": "feedback_received", "description": "Human feedback processed", "next_action": "take_action"},
    8: {"state": "applied", "description": "Application submitted", "next_action": "track_response"},
    9: {"state": "archived", "description": "Final state", "next_action": "none"}
}

class StatusManager:
    """Manages beautiful JSON status tracking for jobs"""
    
    def __init__(self, job_data_dir: str = "/home/xai/Documents/sunset/data/postings"):
        self.job_data_dir = Path(job_data_dir)
    
    def get_job_status(self, job_data: Dict[str, Any]) -> Tuple[int, str]:
        """Get current pipeline status of a job"""
        
        # Check for beautiful JSON structure first
        if "job_metadata" in job_data:
            pipeline_status = job_data["job_metadata"].get("pipeline_status", {})
            code = pipeline_status.get("code", 0)
            state = pipeline_status.get("state", "unknown")
            return code, state
        
        # Legacy format - infer status from data presence
        return self._infer_legacy_status(job_data)
    
    def _infer_legacy_status(self, job_data: Dict[str, Any]) -> Tuple[int, str]:
        """Infer status from legacy job format"""
        
        # Check if has LLM evaluation (status 3+)
        if job_data.get("evaluation_results", {}).get("cv_to_role_match"):
            return 3, "processed"
        
        # Check if has enhanced description (status 2+)
        web_details = job_data.get("web_details", {})
        if (web_details.get("concise_description") or 
            web_details.get("clean_description") or
            len(web_details.get("full_description", "")) > 1000):
            return 2, "enhanced"
        
        # Check if has basic job data (status 1+)
        if job_data.get("job_id") and job_data.get("web_details", {}).get("position_title"):
            return 1, "fetched"
        
        # Default to error state
        return 0, "error"
    
    def update_status(self, job_data: Dict[str, Any], new_code: int, 
                     processor: str = "status_manager", details: str = "") -> Dict[str, Any]:
        """Update job status to new code"""
        
        if new_code not in PIPELINE_STATES:
            raise ValueError(f"Invalid status code: {new_code}")
        
        state_info = PIPELINE_STATES[new_code]
        old_code, old_state = self.get_job_status(job_data)
        
        # Ensure beautiful JSON structure exists
        if "job_metadata" not in job_data:
            job_data["job_metadata"] = {}
        
        # Update pipeline status
        job_data["job_metadata"]["pipeline_status"] = {
            "code": new_code,
            "state": state_info["state"],
            "updated_at": datetime.now().isoformat(),
            "progress_percentage": round((new_code / 9) * 100, 1),
            "next_action": state_info["next_action"],
            "can_auto_proceed": new_code < 9,
            "requires_attention": new_code == 0
        }
        
        # Add to processing log
        if "processing_log" not in job_data:
            job_data["processing_log"] = []
        
        job_data["processing_log"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "status_update",
            "processor": processor,
            "status": "success",
            "pipeline_status": {
                "from": old_code,
                "to": new_code,
                "state": state_info["state"]
            },
            "details": details or f"Status updated from {old_state} to {state_info['state']}"
        })
        
        return job_data
    
    def get_jobs_by_status(self, status_code: int) -> List[Dict[str, Any]]:
        """Get all jobs at a specific status"""
        jobs = []
        
        for job_file in self.job_data_dir.glob("job*.json"):
            try:
                with open(job_file, 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                
                current_code, _ = self.get_job_status(job_data)
                if current_code == status_code:
                    jobs.append(job_data)
                    
            except Exception as e:
                print(f"Error reading {job_file}: {e}")
        
        return jobs
    
    def get_status_overview(self) -> Dict[str, int]:
        """Get overview of all job statuses"""
        status_counts = {state["state"]: 0 for state in PIPELINE_STATES.values()}
        
        for job_file in self.job_data_dir.glob("job*.json"):
            try:
                with open(job_file, 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                
                code, state = self.get_job_status(job_data)
                if state in status_counts:
                    status_counts[state] += 1
                else:
                    status_counts["unknown"] = status_counts.get("unknown", 0) + 1
                    
            except Exception as e:
                print(f"Error reading {job_file}: {e}")
        
        return status_counts
    
    def print_status_dashboard(self):
        """Print beautiful status dashboard"""
        print("\n🎨 ═══════════════════════════════════════════════════")
        print("     BEAUTIFUL JSON PIPELINE STATUS DASHBOARD")
        print("═══════════════════════════════════════════════════")
        
        overview = self.get_status_overview()
        total_jobs = sum(overview.values())
        
        print(f"📊 Total Jobs: {total_jobs}")
        print("\n🏗️  Pipeline Status:")
        
        for code, state_info in PIPELINE_STATES.items():
            state = state_info["state"]
            count = overview.get(state, 0)
            percentage = (count / total_jobs * 100) if total_jobs > 0 else 0
            
            # Status icons
            icons = {
                "error": "❌", "fetched": "📥", "enhanced": "✨", "processed": "🧠",
                "exported": "📊", "cover_generated": "📝", "under_review": "👀",
                "feedback_received": "💬", "applied": "🚀", "archived": "📦"
            }
            
            icon = icons.get(state, "❓")
            progress_bar = "█" * (count // 2) if count > 0 else ""
            
            print(f"  {code}. {icon} {state:<15} │ {count:3d} jobs ({percentage:5.1f}%) │{progress_bar}")
        
        # Next actions summary
        print("\n🎯 Next Actions Needed:")
        needs_enhancement = overview.get("fetched", 0)
        needs_processing = overview.get("enhanced", 0) 
        needs_export = overview.get("processed", 0)
        
        if needs_enhancement > 0:
            print(f"   📝 {needs_enhancement} jobs need description enhancement")
        if needs_processing > 0:
            print(f"   🧠 {needs_processing} jobs need LLM processing")
        if needs_export > 0:
            print(f"   📊 {needs_export} jobs ready for Excel export")
        
        print("═══════════════════════════════════════════════════\n")
    
    def migrate_legacy_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate legacy job format to beautiful JSON with status"""
        
        # Infer current status
        current_code, current_state = self._infer_legacy_status(job_data)
        
        # Add job_metadata if missing
        if "job_metadata" not in job_data:
            job_id = job_data.get("job_id", "unknown")
            job_data["job_metadata"] = {
                "job_id": job_id,
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "source": "legacy_migration",
                "processor": "status_manager"
            }
        
        # Add status tracking
        job_data = self.update_status(job_data, current_code, "legacy_migration", 
                                    f"Migrated from legacy format, detected status: {current_state}")
        
        return job_data

def main():
    """CLI interface for status management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Beautiful JSON Status Manager")
    parser.add_argument("--dashboard", action="store_true", help="Show status dashboard")
    parser.add_argument("--status", type=int, help="Show jobs at specific status code")
    parser.add_argument("--migrate", action="store_true", help="Migrate all legacy jobs to beautiful format")
    parser.add_argument("--update", nargs=2, metavar=("JOB_ID", "STATUS"), help="Update job status")
    
    args = parser.parse_args()
    manager = StatusManager()
    
    if args.dashboard:
        manager.print_status_dashboard()
    
    elif args.status is not None:
        jobs = manager.get_jobs_by_status(args.status)
        state_info = PIPELINE_STATES.get(args.status, {"state": "unknown"})
        print(f"\n📋 Jobs at status {args.status} ({state_info['state']}):")
        
        for job in jobs:
            job_id = job.get("job_id") or job.get("job_metadata", {}).get("job_id")
            title = job.get("web_details", {}).get("position_title", "Unknown")
            print(f"  • Job {job_id}: {title}")
    
    elif args.migrate:
        print("🔄 Migrating legacy jobs to beautiful JSON format...")
        migrated = 0
        
        for job_file in Path("/home/xai/Documents/sunset/data/postings").glob("job*.json"):
            try:
                with open(job_file, 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                
                # Check if already has beautiful format
                if "job_metadata" not in job_data or "pipeline_status" not in job_data.get("job_metadata", {}):
                    job_data = manager.migrate_legacy_job(job_data)
                    
                    with open(job_file, 'w', encoding='utf-8') as f:
                        json.dump(job_data, f, indent=2, ensure_ascii=False)
                    
                    migrated += 1
                    job_id = job_data.get("job_id") or job_data.get("job_metadata", {}).get("job_id")
                    print(f"  ✅ Migrated job {job_id}")
                    
            except Exception as e:
                print(f"  ❌ Error migrating {job_file}: {e}")
        
        print(f"\n🎉 Migration complete! {migrated} jobs migrated to beautiful format.")
        manager.print_status_dashboard()
    
    elif args.update:
        job_id, new_status = args.update
        new_code = int(new_status)
        
        job_file = Path(f"/home/xai/Documents/sunset/data/postings/job{job_id}.json")
        if not job_file.exists():
            print(f"❌ Job file not found: {job_file}")
            return
        
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            old_code, old_state = manager.get_job_status(job_data)
            job_data = manager.update_status(job_data, new_code, "manual_update", 
                                           f"Manually updated via CLI")
            
            with open(job_file, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            
            new_state = PIPELINE_STATES[new_code]["state"]
            print(f"✅ Updated job {job_id}: {old_state} → {new_state}")
            
        except Exception as e:
            print(f"❌ Error updating job {job_id}: {e}")
    
    else:
        manager.print_status_dashboard()

if __name__ == "__main__":
    main()
