#!/usr/bin/env python3
"""
Clear Job Processing Cache
==========================

Remove cached results so the main pipeline will reprocess jobs with specialists.

Usage:
python clear_job_cache.py 57488 60955    # Clear specific jobs
python clear_job_cache.py --all          # Clear all job caches
"""

import argparse
from pathlib import Path

def clear_job_cache(job_id):
    """Clear all cached results for a job"""
    postings_dir = Path("/home/xai/Documents/sunset/data/postings")
    
    # Files that indicate job has been processed
    cache_patterns = [
        f"job{job_id}_llm_output.txt",
        f"job{job_id}_all_llm_responses.txt",
        f"job{job_id}_evaluation_*.json"
    ]
    
    removed_files = []
    
    for pattern in cache_patterns:
        cache_files = list(postings_dir.glob(pattern))
        for cache_file in cache_files:
            if cache_file.exists():
                cache_file.unlink()
                removed_files.append(cache_file.name)
    
    return removed_files

def main():
    parser = argparse.ArgumentParser(description='Clear job processing cache')
    parser.add_argument('job_ids', nargs='*', help='Specific job IDs to clear')
    parser.add_argument('--all', action='store_true', help='Clear all job caches')
    
    args = parser.parse_args()
    
    if args.all:
        postings_dir = Path("/home/xai/Documents/sunset/data/postings")
        cache_files = list(postings_dir.glob("job*_llm_output.txt")) + \
                     list(postings_dir.glob("job*_all_llm_responses.txt"))
        
        for cache_file in cache_files:
            cache_file.unlink()
        
        print(f"🗑️  Cleared {len(cache_files)} cache files")
        print("✅ All jobs will be reprocessed on next pipeline run")
        
    elif args.job_ids:
        total_removed = 0
        
        for job_id in args.job_ids:
            removed_files = clear_job_cache(job_id)
            total_removed += len(removed_files)
            
            if removed_files:
                print(f"🗑️  Job {job_id}: Removed {len(removed_files)} cache files")
                for file in removed_files:
                    print(f"    - {file}")
            else:
                print(f"✅ Job {job_id}: No cache files found (already clear)")
        
        print(f"\n🎯 Total cache files removed: {total_removed}")
        print("✅ Selected jobs will be reprocessed on next pipeline run")
        
    else:
        print("Usage:")
        print("python clear_job_cache.py 57488 60955    # Clear specific jobs")
        print("python clear_job_cache.py --all          # Clear all job caches")

if __name__ == "__main__":
    main()
