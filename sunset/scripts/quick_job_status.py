#!/usr/bin/env python3
"""
Quick Job Status Check - Fixed Version
"""

import json
import os
import glob
from pathlib import Path
from datetime import datetime

def main():
    base_path = Path("/home/xai/Documents/sunset")
    jobs_dir = base_path / "data" / "postings"
    progress_file = base_path / "data" / "job_scans" / "search_api_scan_progress.json"
    
    print("🔍 QUICK JOB STATUS CHECK")
    print("=" * 50)
    
    # Load progress tracker
    with open(progress_file, 'r') as f:
        progress_data = json.load(f)
    tracked_jobs = set(progress_data.get("jobs_processed", []))
    
    # Get local files (handle job prefix)
    job_files = glob.glob(str(jobs_dir / "job*.json"))
    local_jobs = set()
    for file_path in job_files:
        filename = os.path.basename(file_path)
        job_id = filename.replace('job', '').replace('.json', '')
        local_jobs.add(job_id)
    
    print(f"📊 Tracked jobs: {len(tracked_jobs)}")
    print(f"📂 Local files: {len(local_jobs)}")
    
    # Check for discrepancies
    missing_files = tracked_jobs - local_jobs
    unexpected_files = local_jobs - tracked_jobs
    common_jobs = tracked_jobs & local_jobs
    
    print(f"❌ Missing files: {len(missing_files)}")
    print(f"➕ Unexpected files: {len(unexpected_files)}")
    print(f"✅ Matching jobs: {len(common_jobs)}")
    
    if missing_files:
        print(f"   Missing: {sorted(list(missing_files))[:5]}...")
    if unexpected_files:
        print(f"   Unexpected: {sorted(list(unexpected_files))[:5]}...")
    
    # Check AI analysis for existing jobs
    ai_analysis_count = 0
    sample_jobs = sorted(list(local_jobs), key=int)[:20]  # Sample 20 jobs
    
    for job_id in sample_jobs:
        file_path = jobs_dir / f"job{job_id}.json"
        try:
            with open(file_path, 'r') as f:
                job_data = json.load(f)
            
            has_ai = any([
                'llama32_evaluation' in job_data,
                'cv_analysis' in job_data,
                'evaluation_results' in job_data
            ])
            
            if has_ai:
                ai_analysis_count += 1
        except Exception:
            pass
    
    print(f"\n🧠 AI ANALYSIS STATUS (sample of {len(sample_jobs)} jobs):")
    print(f"   With AI analysis: {ai_analysis_count}")
    print(f"   Without AI analysis: {len(sample_jobs) - ai_analysis_count}")
    print(f"   Estimated data loss: {(len(sample_jobs) - ai_analysis_count) / len(sample_jobs) * 100:.1f}%")

if __name__ == "__main__":
    main()
