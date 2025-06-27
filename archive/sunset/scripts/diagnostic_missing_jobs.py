#!/usr/bin/env python3
"""
Emergency Diagnostic: Missing Jobs Analysis
==========================================

Analyzes what went wrong with the pipeline and identifies missing jobs.
"""

import json
import os
from pathlib import Path
from typing import Set, List, Dict, Tuple
from datetime import datetime

def load_progress_tracker() -> Set[str]:
    """Load job IDs from progress tracker"""
    progress_file = Path("data/job_scans/search_api_scan_progress.json")
    
    try:
        with open(progress_file, 'r') as f:
            data = json.load(f)
        return set(data.get("jobs_processed", []))
    except Exception as e:
        print(f"❌ Error loading progress tracker: {e}")
        return set()

def scan_existing_files() -> Tuple[Set[str], Dict[str, List[str]]]:
    """Scan existing job files and categorize them"""
    postings_dir = Path("data/postings")
    
    job_files = set()
    file_types = {
        'json': [],
        'llm_output': [],
        'llm_responses': [],
        'other': []
    }
    
    if not postings_dir.exists():
        print(f"❌ Postings directory doesn't exist: {postings_dir}")
        return set(), file_types
    
    for file_path in postings_dir.glob("job*"):
        filename = file_path.name
        
        if filename.endswith('.json'):
            # Extract job ID from filename
            job_id = filename.replace('job', '').replace('.json', '')
            job_files.add(job_id)
            file_types['json'].append(filename)
        elif 'llm_output' in filename:
            file_types['llm_output'].append(filename)
        elif 'llm_responses' in filename:
            file_types['llm_responses'].append(filename)
        else:
            file_types['other'].append(filename)
    
    return job_files, file_types

def analyze_job_content(job_id: str) -> Dict[str, any]:
    """Analyze a specific job file's content and processing state"""
    job_file = Path(f"data/postings/job{job_id}.json")
    
    if not job_file.exists():
        return {"exists": False}
    
    try:
        with open(job_file, 'r') as f:
            data = json.load(f)
        
        # Check what analysis exists
        analysis = {
            "exists": True,
            "has_evaluation_results": "evaluation_results" in data,
            "has_llama32_evaluation": "llama32_evaluation" in data,
            "has_cv_match": False,
            "status": data.get("job_metadata", {}).get("status", "unknown"),
            "created_at": data.get("job_metadata", {}).get("created_at", "unknown"),
            "processor": data.get("job_metadata", {}).get("processor", "unknown")
        }
        
        # Check if CV matching was done
        if "evaluation_results" in data:
            cv_match = data["evaluation_results"].get("cv_to_role_match")
            analysis["has_cv_match"] = cv_match is not None
            
        if "llama32_evaluation" in data:
            cv_match = data["llama32_evaluation"].get("cv_to_role_match")
            analysis["has_cv_match"] = analysis["has_cv_match"] or cv_match is not None
            
        return analysis
        
    except Exception as e:
        return {"exists": True, "error": str(e)}

def main():
    print("🔍 EMERGENCY DIAGNOSTIC: Missing Jobs Analysis")
    print("=" * 60)
    
    # Load expected jobs from progress tracker
    expected_jobs = load_progress_tracker()
    print(f"📊 Progress tracker says we should have: {len(expected_jobs)} jobs")
    
    # Scan existing files
    existing_jobs, file_types = scan_existing_files()
    print(f"📂 Actually found job files: {len(existing_jobs)} jobs")
    
    # Analysis
    missing_jobs = expected_jobs - existing_jobs
    unexpected_jobs = existing_jobs - expected_jobs
    
    print(f"\n📋 FILE TYPE BREAKDOWN:")
    for file_type, files in file_types.items():
        print(f"  {file_type}: {len(files)} files")
    
    print(f"\n❌ MISSING JOBS: {len(missing_jobs)}")
    if missing_jobs:
        missing_list = sorted(list(missing_jobs), key=int)
        print("Missing job IDs:")
        for i in range(0, len(missing_list), 10):
            batch = missing_list[i:i+10]
            print("  " + ", ".join(batch))
    
    print(f"\n➕ UNEXPECTED JOBS: {len(unexpected_jobs)}")
    if unexpected_jobs:
        unexpected_list = sorted(list(unexpected_jobs), key=int)
        print("Unexpected job IDs:")
        for i in range(0, len(unexpected_list), 10):
            batch = unexpected_list[i:i+10]
            print("  " + ", ".join(batch))
    
    # Analyze processing state of existing jobs
    print(f"\n🧠 PROCESSING STATE ANALYSIS:")
    processed_count = 0
    needs_processing = []
    
    for job_id in sorted(list(existing_jobs), key=int)[:10]:  # Sample first 10
        analysis = analyze_job_content(job_id)
        if analysis.get("has_cv_match"):
            processed_count += 1
        else:
            needs_processing.append(job_id)
    
    print(f"  Sample analysis (first 10 jobs):")
    print(f"  - Jobs with CV analysis: {processed_count}/10")
    print(f"  - Jobs needing processing: {len(needs_processing)}")
    
    if needs_processing:
        print(f"  Jobs needing AI processing: {', '.join(needs_processing[:5])}...")
    
    # Recovery recommendations
    print(f"\n💡 RECOVERY RECOMMENDATIONS:")
    if missing_jobs:
        print(f"  1. Run recovery for {len(missing_jobs)} missing jobs")
        print(f"  2. Re-run AI analysis for recovered jobs")
    
    if needs_processing:
        print(f"  3. Run AI processing for jobs without analysis")
    
    print(f"\n📝 SUMMARY:")
    print(f"  Expected: {len(expected_jobs)} jobs")
    print(f"  Found: {len(existing_jobs)} jobs") 
    print(f"  Missing: {len(missing_jobs)} jobs")
    print(f"  Data loss impact: {len(missing_jobs)/len(expected_jobs)*100:.1f}%")

if __name__ == "__main__":
    # Change to project root
    os.chdir("/home/xai/Documents/sunset")
    main()
