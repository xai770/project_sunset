#!/usr/bin/env python3
"""
Domain-Enhanced Skill Matcher Runner

This script provides a command-line interface to the enhanced domain skill matcher,
which analyzes job requirements and candidate skills with domain-aware matching.

The domain-enhanced matcher combines semantic similarity with domain relationship
analysis to produce more accurate skill matches with reduced false positives.

Usage:
    python run_domain_enhanced_matcher.py 12345    # Process a single job
    python run_domain_enhanced_matcher.py --all    # Process all jobs
    python run_domain_enhanced_matcher.py --jobs 12345,12346,12347
"""

import os
import sys
import json
import time
import logging
import argparse
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set

# Add the parent directory to the path to allow imports
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Set up basic logging
log_dir = Path(parent_dir) / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "domain_enhanced_matcher.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("enhanced_domain_skill_matcher")

# Import the enhanced domain skill matcher
try:
    from run_pipeline.skill_matching.enhanced_domain_skill_matcher import process_job_match
    HAS_MATCHER = True
except ImportError as e:
    logger.error(f"Error importing enhanced domain skill matcher: {e}")
    HAS_MATCHER = False

# Domain match cache
domain_match_cache: Dict[str, Dict[str, Any]] = {}
DOMAIN_CACHE_PATH = Path(parent_dir) / "data" / "skill_match_cache" / "domain_match_cache.json"

def load_domain_match_cache() -> Dict[str, Dict[str, Any]]:
    """
    Load the domain match cache from disk

    Returns:
        Domain match cache dictionary
    """
    global domain_match_cache
    
    if domain_match_cache:
        return domain_match_cache
    
    try:
        if DOMAIN_CACHE_PATH.exists():
            with open(DOMAIN_CACHE_PATH, 'r') as f:
                domain_match_cache = json.load(f)
                logger.info(f"Loaded {len(domain_match_cache)} domain match entries from cache")
                return domain_match_cache
        else:
            logger.info("No domain match cache found - starting fresh")
            domain_match_cache = {}
            return domain_match_cache
    except Exception as e:
        logger.error(f"Error loading domain match cache: {e}")
        domain_match_cache = {}
        return domain_match_cache

def save_domain_match_cache() -> None:
    """
    Save the domain match cache to disk
    """
    try:
        DOMAIN_CACHE_PATH.parent.mkdir(exist_ok=True, parents=True)
        with open(DOMAIN_CACHE_PATH, 'w') as f:
            json.dump(domain_match_cache, f)
            logger.info(f"Saved {len(domain_match_cache)} domain match entries to cache")
    except Exception as e:
        logger.error(f"Error saving domain match cache: {e}")

def get_all_job_ids() -> List[int]:
    """
    Get all available job IDs in the data directory

    Returns:
        List of job IDs
    """
    try:
        job_data_dir = Path(parent_dir) / "data" / "postings"
        if not job_data_dir.exists():
            logger.error(f"Job data directory not found: {job_data_dir}")
            return []
        job_files = list(job_data_dir.glob("*.json"))
        job_ids = []
        for job_file in job_files:
            stem = job_file.stem
            # Accept both job<ID>.json and <ID>.json
            if stem.startswith("job") and stem[3:].isdigit():
                job_ids.append(int(stem[3:]))
            elif stem.isdigit():
                job_ids.append(int(stem))
            # else skip non-numeric or non-matching files
        logger.info(f"Found {len(job_ids)} total job files.")
        return job_ids
    except Exception as e:
        logger.error(f"Error getting job IDs: {e}")
        return []

def get_job_file_path(job_id: int) -> Optional[Path]:
    """
    Return the Path to the job file, supporting both job<ID>.json and <ID>.json naming.
    """
    job_data_dir = Path(parent_dir) / "data" / "postings"
    job_file_job = job_data_dir / f"job{job_id}.json"
    job_file_plain = job_data_dir / f"{job_id}.json"
    if job_file_job.exists():
        return job_file_job
    elif job_file_plain.exists():
        return job_file_plain
    else:
        return None

def filter_jobs_needing_processing(job_ids: List[int], force_reprocess: bool = False) -> List[int]:
    """
    Filter jobs that need domain-enhanced processing

    Args:
        job_ids: List of job IDs to check
        force_reprocess: Force reprocessing even if results exist

    Returns:
        Filtered list of job IDs
    """
    if force_reprocess:
        return job_ids

    filtered_ids = []
    for job_id in job_ids:
        job_file_path = get_job_file_path(job_id)
        if not job_file_path:
            continue  # skip missing job files
        try:
            with open(job_file_path, 'r') as f:
                job_data = json.load(f)
            # Only include jobs that do NOT have 'domain_enhanced_match' key
            if "domain_enhanced_match" not in job_data:
                filtered_ids.append(job_id)
        except Exception as e:
            logger.error(f"Error reading job file {job_id}: {e}")
            continue
    logger.info(f"Filtered to {len(filtered_ids)} job files that need processing.")
    return filtered_ids

def process_job_batch(
    job_ids: List[int],
    force_reprocess: bool = False,
    batch_num: int = 1,
    total_batches: int = 1
) -> Tuple[int, float]:
    """
    Process a batch of jobs with the domain-enhanced matcher

    Args:
        job_ids: List of job IDs to process
        force_reprocess: Force reprocessing
        batch_num: Current batch number
        total_batches: Total number of batches

    Returns:
        Tuple of (number of jobs processed, total time in seconds)
    """
    if not job_ids:
        return 0, 0.0
        
    logger.info(f"Processing batch {batch_num}/{total_batches} ({len(job_ids)} jobs)")
    
    start_time = time.time()
    updated_count = 0
    cache = load_domain_match_cache()
    
    # Process each job in the batch
    for idx, job_id in enumerate(job_ids):
        try:
            str_job_id = str(job_id)
            
            # Process the job
            result = process_job_match(str_job_id, force_reprocess=force_reprocess)
            
            # Update the cache
            if result.get("success", False):
                cache[str_job_id] = {
                    "job_id": str_job_id,
                    "timestamp": datetime.now().isoformat(),
                    "match_coverage": result.get("match_results", {}).get("match_coverage_percent", 0),
                    "avg_score": result.get("match_results", {}).get("average_match_score", 0)
                }
                updated_count += 1
            
            # Log progress
            elapsed = time.time() - start_time
            avg_time = elapsed / (idx + 1)
            remaining_jobs = len(job_ids) - (idx + 1)
            est_remaining = avg_time * remaining_jobs
            
            if (idx + 1) % 5 == 0 or (idx + 1) == len(job_ids):
                logger.info(
                    f"Processed {idx + 1}/{len(job_ids)} job files ({updated_count} updated) in {elapsed:.1f}s "
                    f"(avg: {avg_time:.1f}s/job, est. remaining: {est_remaining:.1f}s)"
                )
        
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {e}")
    
    # Save the cache after the batch
    save_domain_match_cache()
    
    elapsed = time.time() - start_time
    logger.info(f"Batch complete in {elapsed:.1f}s. Updated {updated_count} jobs.")
    
    return updated_count, elapsed

def run_domain_enhanced_matcher(
    job_ids: Optional[List[int]] = None,
    force_reprocess: bool = False,
    max_workers: int = 2,
    batch_size: int = 2,
    export_csv: bool = True
) -> bool:
    """
    Run the domain-enhanced matcher on job files

    Args:
        job_ids: List of job IDs to process
        force_reprocess: Force reprocessing
        max_workers: Maximum number of parallel workers
        batch_size: Number of jobs to process in each batch
        export_csv: Whether to export results to CSV after processing

    Returns:
        Success flag
    """
    if not HAS_MATCHER:
        logger.error("Enhanced domain skill matcher is not available. Cannot proceed.")
        return False
    
    # Load all job IDs if not specified
    if job_ids is None:
        job_ids = get_all_job_ids()
    
    if not job_ids:
        logger.warning("No job IDs found to process.")
        return False
    
    logger.info(f"Found {len(job_ids)} job files matching the specified IDs.")
    
    if not force_reprocess:
        # Filter to jobs that need processing
        job_ids = filter_jobs_needing_processing(job_ids, force_reprocess)
    
    if not job_ids:
        logger.info("No jobs need processing. All done!")
        return True
    
    # Prepare batches
    batches = []
    for i in range(0, len(job_ids), batch_size):
        batches.append(job_ids[i:i+batch_size])
    
    total_jobs = len(job_ids)
    total_batches = len(batches)
    
    logger.info(f"Using {batch_size} parallel jobs with {max_workers} workers each")
    
    # Process batches with parallel workers
    start_time = time.time()
    total_updated = 0
    
    # If max_workers > 1, use parallel processing
    if max_workers > 1 and total_batches > 1:
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_batch = {
                executor.submit(
                    process_job_batch, 
                    batch, 
                    force_reprocess,
                    batch_idx + 1,
                    total_batches
                ): batch_idx 
                for batch_idx, batch in enumerate(batches)
            }
            
            for future in concurrent.futures.as_completed(future_to_batch):
                batch_idx = future_to_batch[future]
                try:
                    updated_count, _ = future.result()
                    total_updated += updated_count
                except Exception as e:
                    logger.error(f"Error processing batch {batch_idx + 1}: {e}")
    else:
        # Process sequentially
        for batch_idx, batch in enumerate(batches):
            updated_count, _ = process_job_batch(
                batch,
                force_reprocess,
                batch_idx + 1,
                total_batches
            )
            total_updated += updated_count
    
    # Save the final cache
    save_domain_match_cache()
    
    # Log completion summary
    elapsed = time.time() - start_time
    avg_time = elapsed / total_jobs if total_jobs > 0 else 0
    
    logger.info(
        f"Domain-enhanced skill matching complete. Updated {total_updated}/{total_jobs} "
        f"job files in {elapsed:.1f}s (avg: {avg_time:.1f}s/job)"
    )
    
    # Export results to CSV if requested
    if export_csv and job_ids:
        csv_path = Path(parent_dir) / "data" / "reports" / f"domain_enhanced_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        export_success = export_results_to_csv(job_ids, csv_path)
        if export_success:
            logger.info(f"Results exported to CSV: {csv_path}")
        else:
            logger.warning("Failed to export results to CSV")
    
    return True

def export_results_to_csv(job_ids: List[int], output_path: Optional[Path] = None) -> bool:
    """
    Export domain-enhanced matching results to CSV
    
    Args:
        job_ids: List of job IDs to include in the export
        output_path: Path to save the CSV file (optional)
        
    Returns:
        Success flag
    """
    if not job_ids:
        logger.warning("No job IDs provided for CSV export")
        return False
    
    # Default output path
    if output_path is None:
        output_path = Path(parent_dir) / "data" / "reports" / f"domain_enhanced_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Create parent directory if it doesn't exist
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    try:
        # Prepare CSV rows
        rows = []
        headers = [
            "job_id", 
            "job_title", 
            "match_coverage_percent", 
            "avg_match_score",
            "high_quality_matches",
            "medium_quality_matches", 
            "low_quality_matches",
            "primary_domains",
            "matched_job_skills",
            "job_skills_count",
            "candidate_skills_count"
        ]
        
        # Process each job
        for job_id in job_ids:
            job_file_path = get_job_file_path(job_id)
            if not job_file_path:
                logger.warning(f"Job file not found for ID {job_id}, skipping")
                continue
            try:
                with open(job_file_path, 'r') as f:
                    job_data = json.load(f)
                # Check if domain enhanced match results exist
                if "domain_enhanced_match" not in job_data:
                    logger.warning(f"No domain enhanced match results for job {job_id}, skipping")
                    continue
                match_data = job_data["domain_enhanced_match"]
                
                # Extract the data for CSV
                row = {
                    "job_id": job_id,
                    "job_title": job_data.get("title", "Unknown"),
                    "match_coverage_percent": match_data.get("match_coverage_percent", 0),
                    "avg_match_score": match_data.get("average_match_score", 0),
                    "high_quality_matches": match_data.get("match_quality_summary", {}).get("high_quality_matches", 0),
                    "medium_quality_matches": match_data.get("match_quality_summary", {}).get("medium_quality_matches", 0),
                    "low_quality_matches": match_data.get("match_quality_summary", {}).get("low_quality_matches", 0),
                    "primary_domains": ", ".join(match_data.get("job_domain_analysis", {}).get("primary_domains", {}).keys()),
                    "matched_job_skills": match_data.get("matched_job_skills_count", 0),
                    "job_skills_count": match_data.get("total_job_skills_count", 0),
                    "candidate_skills_count": len(job_data.get("skills", []))
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.error(f"Error processing job {job_id} for CSV export: {e}")
        
        # Write CSV
        import csv
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        
        logger.info(f"Exported {len(rows)} domain enhanced match results to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting results to CSV: {e}")
        return False

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the domain-enhanced skill matcher")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("job_id", nargs="?", help="Single job ID to process")
    group.add_argument("--all", action="store_true", help="Process all jobs")
    group.add_argument("--jobs", help="Comma-separated list of job IDs to process")
    
    parser.add_argument("--force", action="store_true", help="Force reprocessing of already processed jobs")
    parser.add_argument("--workers", type=int, default=2, help="Number of parallel workers")
    parser.add_argument("--batch-size", type=int, default=2, help="Number of jobs to process in each batch")
    parser.add_argument("--no-csv", action="store_true", help="Don't export results to CSV")
    parser.add_argument("--csv-path", help="Custom path for CSV export")
    
    args = parser.parse_args()
    
    # Determine job IDs to process
    job_ids = None
    
    if args.job_id:
        try:
            job_ids = [int(args.job_id)]
        except ValueError:
            parser.error(f"Invalid job ID: {args.job_id}")
    elif args.all:
        job_ids = None  # Will be loaded from the data directory
    elif args.jobs:
        try:
            job_ids = [int(job_id.strip()) for job_id in args.jobs.split(",")]
        except ValueError:
            parser.error(f"Invalid job IDs: {args.jobs}")
    
    # Run the matcher
    success = run_domain_enhanced_matcher(
        job_ids=job_ids,
        force_reprocess=args.force,
        max_workers=args.workers,
        batch_size=args.batch_size,
        export_csv=not args.no_csv
    )
    
    # If CSV export requested with custom path, do it separately
    if not args.no_csv and args.csv_path and job_ids:
        csv_path = Path(args.csv_path)
        export_success = export_results_to_csv(job_ids, csv_path)
        if export_success:
            print(f"Results exported to custom CSV path: {csv_path}")
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
