#!/usr/bin/env python3
"""
Job Recovery Module

Handles detection and recovery of missing jobs in the pipeline.
This module provides functionality to identify jobs that are referenced in Excel
but missing from the data directory, and attempts to recover them.
"""

import logging
import sys
import json
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

def detect_and_recover_missing_jobs(max_recovery: int = 25, enable_recovery: bool = True) -> int:
    """
    Detect missing jobs and attempt to recover them
    
    Args:
        max_recovery: Maximum number of jobs to recover in one run
        enable_recovery: Whether to actually attempt recovery or just detect
        
    Returns:
        Number of jobs successfully recovered
    """
    logger.info("🔧 Starting missing job detection and recovery...")
    
    try:
        # Find all Excel files to check for job references
        excel_files = find_excel_files()
        
        # Extract job IDs referenced in Excel files
        referenced_jobs = extract_job_ids_from_excel(excel_files)
        
        # Find existing job files
        existing_jobs = find_existing_job_files()
        
        # Identify missing jobs
        missing_jobs = find_missing_jobs(referenced_jobs, existing_jobs)
        
        if not missing_jobs:
            logger.info("✅ No missing jobs detected")
            return 0
        
        logger.info(f"🔍 Found {len(missing_jobs)} missing jobs")
        
        if not enable_recovery:
            logger.info("🔧 Recovery disabled - only detecting missing jobs")
            return 0
        
        # Limit recovery to max_recovery
        jobs_to_recover = missing_jobs[:max_recovery]
        
        if len(missing_jobs) > max_recovery:
            logger.info(f"🔧 Limiting recovery to {max_recovery} jobs (out of {len(missing_jobs)} missing)")
        
        # Attempt to recover missing jobs
        recovered_count = recover_missing_jobs(jobs_to_recover)
        
        logger.info(f"🎉 Recovery complete: {recovered_count}/{len(jobs_to_recover)} jobs recovered")
        
        return recovered_count
        
    except Exception as e:
        logger.error(f"❌ Error during missing job recovery: {e}")
        return 0

def find_excel_files() -> List[Path]:
    """Find all Excel files that might reference jobs"""
    excel_files = []
    
    # Check common Excel output locations
    excel_dirs = [
        project_root / "output" / "excel",
        project_root / "data" / "output",
        project_root / "output",
        project_root / "data" / "reports"
    ]
    
    for excel_dir in excel_dirs:
        if excel_dir.exists():
            excel_files.extend(list(excel_dir.glob("job_matches_*.xlsx")))
            excel_files.extend(list(excel_dir.glob("*.xlsx")))
    
    logger.info(f"📊 Found {len(excel_files)} Excel files to check")
    return excel_files

def extract_job_ids_from_excel(excel_files: List[Path]) -> List[str]:
    """Extract job IDs referenced in Excel files"""
    job_ids = set()
    
    try:
        import pandas as pd
        
        for excel_file in excel_files:
            try:
                # Read Excel file
                df = pd.read_excel(excel_file)
                
                # Look for job ID columns
                job_id_columns = ['job_id', 'Job ID', 'JobID', 'ID']
                
                for col in job_id_columns:
                    if col in df.columns:
                        # Extract non-null job IDs
                        file_job_ids = df[col].dropna().astype(str).tolist()
                        job_ids.update(file_job_ids)
                        logger.debug(f"📊 Found {len(file_job_ids)} job IDs in {excel_file.name}")
                        break
                        
            except Exception as e:
                logger.warning(f"⚠️ Could not read Excel file {excel_file}: {e}")
                
    except ImportError:
        logger.warning("⚠️ pandas not available - cannot extract job IDs from Excel")
    
    job_ids_list = list(job_ids)
    logger.info(f"📊 Extracted {len(job_ids_list)} unique job IDs from Excel files")
    return job_ids_list

def find_existing_job_files() -> List[str]:
    """Find existing job files in the data directory"""
    data_dir = project_root / "data" / "postings"
    
    if not data_dir.exists():
        logger.warning(f"⚠️ Data directory not found: {data_dir}")
        return []
    
    # Find all job files
    job_files = list(data_dir.glob("job*.json"))
    
    # Extract job IDs from filenames
    job_ids = []
    for job_file in job_files:
        # Extract ID from filename like "job12345.json"
        filename = job_file.stem
        if filename.startswith("job"):
            job_id = filename[3:]  # Remove "job" prefix
            job_ids.append(job_id)
    
    logger.info(f"📁 Found {len(job_ids)} existing job files")
    return job_ids

def find_missing_jobs(referenced_jobs: List[str], existing_jobs: List[str]) -> List[str]:
    """Find jobs that are referenced but missing from data directory"""
    referenced_set = set(referenced_jobs)
    existing_set = set(existing_jobs)
    
    missing_jobs = list(referenced_set - existing_set)
    
    # Filter out obviously invalid job IDs
    valid_missing_jobs = []
    for job_id in missing_jobs:
        if job_id and len(job_id) > 2 and job_id.isdigit():
            valid_missing_jobs.append(job_id)
    
    logger.info(f"🔍 Identified {len(valid_missing_jobs)} missing jobs")
    return valid_missing_jobs

def recover_missing_jobs(jobs_to_recover: List[str]) -> int:
    """
    Attempt to recover missing jobs by fetching them
    
    Args:
        jobs_to_recover: List of job IDs to recover
        
    Returns:
        Number of jobs successfully recovered
    """
    logger.info(f"🔧 Attempting to recover {len(jobs_to_recover)} missing jobs...")
    
    recovered_count = 0
    failed_count = 0
    data_dir = project_root / "data" / "postings"
    
    # Ensure data directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    
    for job_id in jobs_to_recover:
        try:
            logger.info(f"🔧 Attempting to recover job {job_id}...")
            
            # Try to fetch job using the enhanced job fetcher
            job_data = fetch_single_job(job_id)
            
            if job_data:
                # Create recovered job structure
                recovered_job = create_recovered_job_structure(job_id, job_data)
                
                # Save the recovered job
                job_file = data_dir / f"job{job_id}.json"
                with open(job_file, 'w', encoding='utf-8') as f:
                    json.dump(recovered_job, f, indent=2, ensure_ascii=False)
                
                recovered_count += 1
                logger.info(f"✅ Successfully recovered job {job_id}")
                
            else:
                failed_count += 1
                logger.warning(f"⚠️ Could not recover job {job_id} - may no longer exist")
            
            # Add a small delay to be nice to the API
            import time
            time.sleep(0.5)
            
        except Exception as e:
            failed_count += 1
            logger.error(f"❌ Error recovering job {job_id}: {e}")
    
    logger.info(f"🎉 Recovery summary: {recovered_count} recovered, {failed_count} failed")
    
    if recovered_count > 0:
        recovery_rate = recovered_count / len(jobs_to_recover) * 100
        logger.info(f"📊 Recovery rate: {recovery_rate:.1f}%")
    
    return recovered_count

def fetch_single_job(job_id: str) -> Optional[Dict]:
    """
    Fetch a single job by ID using available fetchers
    
    Args:
        job_id: Job ID to fetch
        
    Returns:
        Job data if successful, None otherwise
    """
    try:
        # Try to use the enhanced job fetcher
        from core.enhanced_job_fetcher import EnhancedJobFetcher
        
        fetcher = EnhancedJobFetcher()
        job_data = fetcher.fetch_single_job(job_id)
        
        if job_data:
            logger.debug(f"✅ Fetched job {job_id} using enhanced fetcher")
            return job_data
        
    except Exception as e:
        logger.debug(f"⚠️ Enhanced fetcher failed for job {job_id}: {e}")
    
    # Try other methods or return None
    logger.debug(f"❌ Could not fetch job {job_id}")
    return None

def create_recovered_job_structure(job_id: str, job_data: Dict) -> Dict:
    """
    Create a standardized job structure for recovered jobs
    
    Args:
        job_id: Job ID
        job_data: Raw job data from fetcher
        
    Returns:
        Standardized job structure
    """
    return {
        "job_id": job_id,
        "title": job_data.get("title", f"Recovered Job {job_id}"),
        "web_details": {
            "position_title": job_data.get("title", f"Recovered Job {job_id}"),
            "location": job_data.get("location", "Frankfurt am Main, Germany"),
            "department": job_data.get("department", "Unknown")
        },
        "job_content": {
            "title": job_data.get("title", f"Recovered Job {job_id}"),
            "description": job_data.get("description", ""),
            "requirements": job_data.get("requirements", []),
            "location": {
                "city": "Frankfurt am Main",
                "country": "Germany",
                "remote_options": False
            },
            "employment_details": {
                "type": "Full-time",
                "schedule": "Regular",
                "career_level": "Professional"
            },
            "organization": {
                "name": "Deutsche Bank",
                "division": "Unknown"
            }
        },
        "evaluation_results": {
            "cv_to_role_match": None,
            "match_confidence": None
        },
        "processing_log": [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "auto_recovery",
                "processor": "pipeline_recovery_system",
                "status": "success",
                "details": f"Automatically recovered missing job {job_id}"
            }
        ],
        "raw_source_data": {
            "description_source": "recovery_fetch",
            "original_data": job_data
        }
    }

def validate_recovery_system() -> bool:
    """
    Validate that the recovery system is working
    
    Returns:
        True if system is working, False otherwise
    """
    try:
        # Check if data directory exists
        data_dir = project_root / "data" / "postings"
        if not data_dir.exists():
            logger.warning("⚠️ Data directory does not exist")
            return False
        
        # Check if we can import required modules
        from core.enhanced_job_fetcher import EnhancedJobFetcher
        
        logger.info("✅ Job recovery system validated")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Job recovery system validation failed: {e}")
        return False

if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    print("Testing job recovery module...")
    
    # Test validation
    is_working = validate_recovery_system()
    print(f"Recovery system working: {is_working}")
    
    # Test detection only (no recovery)
    missing_count = detect_and_recover_missing_jobs(max_recovery=0, enable_recovery=False)
    print(f"Missing jobs detected: {missing_count}")
