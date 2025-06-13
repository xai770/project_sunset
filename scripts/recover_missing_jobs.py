#!/usr/bin/env python3
"""
Recovery Script for Missing Job Files
====================================

This script recovers job files that were marked as "processed" but never saved to disk.
Uses the enhanced job fetcher to re-fetch missing jobs.
"""

import json
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.enhanced_job_fetcher import EnhancedJobFetcher

def setup_logging():
    """Setup logging for recovery process"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def get_missing_job_ids():
    """Get list of job IDs that are in progress but missing files"""
    # Load progress data
    progress_file = project_root / "data/job_scans/search_api_scan_progress.json"
    with open(progress_file, 'r') as f:
        progress = json.load(f)
    
    # Get job IDs from progress
    progress_ids = set(str(job_id) for job_id in progress['jobs_processed'])
    
    # Check actual files
    data_dir = project_root / "data/postings"
    job_files = list(data_dir.glob('job*.json'))
    file_ids = set()
    for f in job_files:
        job_id = f.stem.replace('job', '')
        file_ids.add(job_id)
    
    # Find missing files
    missing_files = progress_ids - file_ids
    missing_sorted = sorted([int(x) for x in missing_files])
    
    return missing_sorted

def test_job_availability(job_ids, sample_size=5):
    """Test if a sample of missing jobs are still available"""
    logger = logging.getLogger(__name__)
    fetcher = EnhancedJobFetcher()
    
    sample_ids = job_ids[:sample_size] if len(job_ids) > sample_size else job_ids
    available_jobs = []
    
    logger.info(f"Testing availability of {len(sample_ids)} sample jobs...")
    
    for job_id in sample_ids:
        try:
            # Try to fetch job description to test availability
            description = fetcher.fetch_job_description(str(job_id))
            if description and len(description) > 100:
                available_jobs.append(job_id)
                logger.info(f"✅ Job {job_id} is available ({len(description)} chars)")
            else:
                logger.warning(f"⚠️ Job {job_id} returned empty/short description")
        except Exception as e:
            logger.error(f"❌ Job {job_id} failed: {e}")
    
    return available_jobs

def recover_missing_jobs(job_ids, max_recovery=10):
    """Recover missing job files by re-fetching them"""
    logger = logging.getLogger(__name__)
    fetcher = EnhancedJobFetcher()
    
    recovery_count = min(len(job_ids), max_recovery)
    jobs_to_recover = job_ids[:recovery_count]
    
    logger.info(f"Attempting to recover {recovery_count} missing jobs...")
    
    recovered = []
    failed = []
    
    for i, job_id in enumerate(jobs_to_recover, 1):
        try:
            logger.info(f"🔄 Recovering job {i}/{recovery_count}: {job_id}")
            
            # Create a mock job API data structure for this job
            mock_job_data = {
                "MatchedObjectId": str(job_id),
                "MatchedObjectDescriptor": {
                    "PositionTitle": f"Recovered Job {job_id}",
                    "PositionURI": f"https://careers.db.com/job/{job_id}",
                    "PositionLocation": [{"CityName": "Frankfurt am Main", "CountryName": "Germany"}],
                    "OrganizationName": "Deutsche Bank",
                    "PublicationStartDate": "2025-06-12"
                }
            }
            
            # Fetch job description
            description = fetcher.fetch_job_description(str(job_id))
            
            if description and len(description) > 100:
                # Create beautiful job structure
                beautiful_job = fetcher.create_beautiful_job_structure(
                    job_api_data=mock_job_data,
                    job_description=description
                )
                
                # Save to file
                job_file = fetcher.data_dir / f"job{job_id}.json"
                with open(job_file, 'w', encoding='utf-8') as f:
                    json.dump(beautiful_job, f, indent=2, ensure_ascii=False)
                
                recovered.append(job_id)
                logger.info(f"✅ Recovered job {job_id}: {beautiful_job['job_content']['title']}")
            else:
                failed.append(job_id)
                logger.warning(f"⚠️ Job {job_id} could not be recovered (empty description)")
                
        except Exception as e:
            failed.append(job_id)
            logger.error(f"❌ Failed to recover job {job_id}: {e}")
    
    logger.info(f"🎉 Recovery complete: {len(recovered)} recovered, {len(failed)} failed")
    return recovered, failed

def main():
    """Main recovery process"""
    logger = setup_logging()
    
    logger.info("=== MISSING JOB RECOVERY SCRIPT ===")
    
    # Get missing job IDs
    missing_jobs = get_missing_job_ids()
    logger.info(f"Found {len(missing_jobs)} missing job files")
    
    if not missing_jobs:
        logger.info("No missing jobs found - nothing to recover")
        return 0
    
    # Test availability of sample jobs
    available_jobs = test_job_availability(missing_jobs, sample_size=5)
    
    if not available_jobs:
        logger.warning("No missing jobs appear to be available for recovery")
        return 1
    
    # Recover missing jobs
    recovered, failed = recover_missing_jobs(missing_jobs, max_recovery=20)
    
    # Report results
    logger.info(f"\n=== RECOVERY SUMMARY ===")
    logger.info(f"Total missing jobs: {len(missing_jobs)}")
    logger.info(f"Jobs recovered: {len(recovered)}")
    logger.info(f"Jobs failed: {len(failed)}")
    
    if recovered:
        logger.info(f"Recovered jobs: {recovered}")
    
    if failed and len(failed) < 10:  # Only show failed list if small
        logger.info(f"Failed jobs: {failed}")
    
    return 0 if recovered else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
