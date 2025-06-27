#!/usr/bin/env python3
"""
Example: Pipeline with Automatic Version-Aware Reprocessing
===========================================================

This shows how to integrate processing_state_manager into the main pipeline
for automatic detection and reprocessing of outdated jobs.
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append('/home/xai/Documents/sandy')

from core.processing_state_manager import ProcessingManifest
from core.direct_specialist_manager import DirectSpecialistManager

def pipeline_with_version_tracking():
    """Enhanced pipeline that automatically reprocesses outdated jobs"""
    
    # Initialize managers
    manifest = ProcessingManifest()
    specialist_mgr = DirectSpecialistManager()
    
    # Find jobs that need processing
    job_files = list(Path("/home/xai/Documents/sandy/data/postings").glob("job*.json"))
    outdated_jobs = manifest.get_outdated_jobs()
    
    print(f"Found {len(job_files)} total jobs")
    print(f"Found {len(outdated_jobs)} jobs needing reprocessing")
    
    # Check if specialist versions have changed
    current_versions = {
        "domain_classification": "v1_1",
        "location_validation": "v1_0"
    }
    
    for specialist, version in current_versions.items():
        if manifest.manifest["current_specialist_versions"].get(specialist) != version:
            print(f"Specialist {specialist} version updated to {version}")
            manifest.update_specialist_version(specialist, version)
    
    # Process jobs that need processing
    jobs_to_process = []
    for job_file in job_files:
        job_id = job_file.stem
        if job_id in outdated_jobs or job_id not in manifest.manifest["processing_records"]:
            jobs_to_process.append(job_file)
    
    if not jobs_to_process:
        print("All jobs are up to date!")
        return
    
    print(f"Processing {len(jobs_to_process)} jobs...")
    
    for job_file in jobs_to_process[:3]:  # Limit for demo
        job_id = job_file.stem
        print(f"\nProcessing {job_id}...")
        
        # Load job data
        with open(job_file, 'r') as f:
            job_data = f.read()
        
        # Process with specialists
        start_time = time.time()
        
        try:
            # Domain classification
            domain_start = time.time()
            domain_result = specialist_mgr.classify_domain(job_data)
            domain_time = time.time() - domain_start
            
            # Location validation (would need to fix the dict/string issue first)
            # location_start = time.time()
            # location_result = specialist_mgr.validate_location(job_data)
            # location_time = time.time() - location_start
            
            # Record processing
            manifest.record_processing(
                job_id=job_id,
                specialists_used={"domain_classification": "v1_1"},
                processing_times={"domain_classification": domain_time},
                results_summary={"domain_classification": domain_result}
            )
            
            print(f"  Domain: {domain_result} ({domain_time:.2f}s)")
            
        except Exception as e:
            print(f"  Error processing {job_id}: {e}")
    
    # Show final stats
    stats = manifest.get_processing_stats()
    print(f"\nProcessing complete!")
    print(f"Total jobs: {stats['total_jobs']}")
    print(f"Up to date: {stats['up_to_date']}")

if __name__ == "__main__":
    pipeline_with_version_tracking()
