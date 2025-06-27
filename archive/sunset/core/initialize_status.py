#!/usr/bin/env python3
"""
Initialize pipeline status for jobs using the Beautiful JSON Architecture status system
"""
import json
import sys
from pathlib import Path
from datetime import datetime

def initialize_pipeline_status(job_data, status_code=1, status_state="fetched"):
    """Initialize pipeline status for a job"""
    
    # Ensure job_metadata exists
    if "job_metadata" not in job_data:
        job_data["job_metadata"] = {}
    
    # Add pipeline status
    job_data["job_metadata"]["pipeline_status"] = {
        "code": status_code,
        "state": status_state,
        "updated_at": datetime.now().isoformat(),
        "progress_percentage": (status_code / 9) * 100,
        "next_action": determine_next_action(status_code),
        "can_auto_proceed": status_code < 9,
        "requires_attention": False,
        "error_count": 0
    }
    
    # Ensure processing_log exists
    if "processing_log" not in job_data:
        job_data["processing_log"] = []
    
    # Add status initialization to log
    job_data["processing_log"].append({
        "timestamp": datetime.now().isoformat(),
        "action": "status_initialized",
        "processor": "status_initializer",
        "status": "success",
        "pipeline_status": {
            "from": 0,
            "to": status_code,
            "state": status_state
        },
        "details": f"Pipeline status initialized to {status_state} (code {status_code})"
    })
    
    return job_data

def determine_next_action(status_code):
    """Determine next action based on status code"""
    next_actions = {
        0: "manual_intervention",
        1: "enhance_description",
        2: "process_with_llm", 
        3: "export_to_excel",
        4: "generate_cover_letter",
        5: "email_to_reviewer",
        6: "await_feedback",
        7: "process_feedback",
        8: "track_response",
        9: "archive"
    }
    return next_actions.get(status_code, "unknown")

def main():
    """Initialize status for Frankfurt jobs"""
    job_files = list(Path("data/postings").glob("job64*.json"))
    
    # Filter out backup files
    job_files = [f for f in job_files if "backup" not in f.name.lower()]
    
    print(f"🚀 Initializing pipeline status for {len(job_files)} Frankfurt jobs...")
    
    for job_file in job_files:
        try:
            print(f"📝 Processing {job_file.name}...")
            
            with open(job_file, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Check if already has status
            existing_status = job_data.get("job_metadata", {}).get("pipeline_status")
            if existing_status:
                print(f"   ✅ Already has status: {existing_status.get('state', 'unknown')}")
                continue
            
            # Initialize status
            job_data = initialize_pipeline_status(job_data)
            
            # Save back to file
            with open(job_file, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            
            job_id = job_data.get("job_metadata", {}).get("job_id", job_file.stem)
            print(f"   ✅ Initialized status for job {job_id}: fetched (code 1)")
            
        except Exception as e:
            print(f"   ❌ Error processing {job_file.name}: {e}")
    
    print("\n🎯 Status initialization complete!")

if __name__ == "__main__":
    main()
