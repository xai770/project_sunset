#!/usr/bin/env python3
"""
Benchmark Script for Comparing Skill Matching Implementations

This script compares the performance of multiple skill matching approaches:
1. Original implementation (job_skill_matcher.py)
2. Efficient implementation (efficient_skill_matcher.py)
3. Enhanced implementation (enhanced_skill_matcher.py)

It measures performance across different job files, skill counts, and features.
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import tempfile
import shutil

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Import both implementations
from run_pipeline.skill_matching.job_skill_matcher import batch_match_all_jobs as original_batch_match
from run_pipeline.skill_matching.job_skill_matcher import match_job_to_your_skills_llm as original_match_llm
from run_pipeline.skill_matching.efficient_skill_matcher import batch_match_all_jobs as efficient_batch_match
from run_pipeline.skill_matching.efficient_skill_matcher import process_job_skills as efficient_match

# Import common utilities
from run_pipeline.config.paths import JOB_DATA_DIR, PROJECT_ROOT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("skill_matcher_benchmark")

def load_job_data(job_path: Path) -> Optional[Dict[str, Any]]:
    """Load job data from a file"""
    try:
        with open(job_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load job file {job_path}: {e}")
        return None

def load_your_skills() -> Optional[Dict[str, Any]]:
    """Load your skills from the standard location"""
    your_skills_file = PROJECT_ROOT / "profile" / "skills" / "skill_decompositions.json"
    if not your_skills_file.exists():
        logger.error(f"Your skills file not found: {your_skills_file}")
        return None
    try:
        with open(your_skills_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load your skills: {e}")
        return None

def benchmark_single_job(job_id: int, batch_size: int = 10, use_llm: bool = True):
    """
    Benchmark performance for a single job file
    
    Args:
        job_id: The job ID to benchmark
        batch_size: Batch size for the efficient implementation
        use_llm: Whether to use LLM for matching
    """
    job_path = JOB_DATA_DIR / f"job{job_id}.json"
    if not job_path.exists():
        logger.error(f"Job file not found: {job_path}")
        return None
    
    job_data = load_job_data(job_path)
    your_skills = load_your_skills()
    
    if not job_data or not your_skills:
        return None
    
    # Count the skills
    job_skills = job_data.get("sdr_skills", {}).get("enriched", {})
    job_skill_count = len(job_skills)
    your_skill_count = len(your_skills)
    
    # Create a temp copy to avoid modifying the original
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = Path(tmp.name)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(job_data, f)
    
    results = {
        "job_id": job_id,
        "job_skill_count": job_skill_count,
        "your_skill_count": your_skill_count,
        "total_comparisons": job_skill_count * your_skill_count,
        "use_llm": use_llm,
        "original": {},
        "efficient": {}
    }
    
    # Benchmark original implementation
    logger.info(f"Benchmarking original implementation for job {job_id} (LLM: {use_llm})")
    start_time = time.time()
    if use_llm:
        matches = original_match_llm(job_data, your_skills)
    else:
        # Use the non-LLM version
        from run_pipeline.skill_matching.job_skill_matcher import match_job_to_your_skills
        matches = match_job_to_your_skills(job_data, your_skills)
    original_time = time.time() - start_time
    
    results["original"] = {
        "time": original_time,
        "matches": len(matches),
        "time_per_comparison": original_time / (job_skill_count * your_skill_count) if job_skill_count * your_skill_count > 0 else 0
    }
    
    # Benchmark efficient implementation
    logger.info(f"Benchmarking efficient implementation for job {job_id} (LLM: {use_llm})")
    start_time = time.time()
    matches = efficient_match(
        job_data, 
        your_skills, 
        use_llm=use_llm,
        batch_size=batch_size
    )
    efficient_time = time.time() - start_time
    
    results["efficient"] = {
        "time": efficient_time,
        "matches": len(matches),
        "time_per_comparison": efficient_time / (job_skill_count * your_skill_count) if job_skill_count * your_skill_count > 0 else 0,
        "speedup_factor": original_time / efficient_time if efficient_time > 0 else float('inf')
    }
    
    # Clean up temp file
    try:
        os.unlink(tmp_path)
    except:
        pass
    
    return results

def benchmark_batch(job_ids: List[int], batch_size: int = 10, use_llm: bool = True):
    """Benchmark batch processing across multiple jobs"""
    # Create a temporary directory to avoid modifying real data
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = Path(tmpdirname)
        
        # Copy target jobs to temp directory
        for job_id in job_ids:
            source = JOB_DATA_DIR / f"job{job_id}.json"
            if source.exists():
                target = temp_dir / f"job{job_id}.json"
                shutil.copy(source, target)
        
        # Count total skills
        total_job_skills = 0
        your_skills = load_your_skills()
        your_skill_count = len(your_skills) if your_skills else 0
        
        for job_id in job_ids:
            job_path = temp_dir / f"job{job_id}.json"
            if job_path.exists():
                job_data = load_job_data(job_path)
                if job_data:
                    job_skills = job_data.get("sdr_skills", {}).get("enriched", {})
                    total_job_skills += len(job_skills)
        
        results = {
            "job_ids": job_ids,
            "job_count": len(job_ids),
            "total_job_skills": total_job_skills,
            "your_skill_count": your_skill_count,
            "total_comparisons": total_job_skills * your_skill_count,
            "use_llm": use_llm,
            "original": {},
            "efficient": {}
        }
        
        # Monkey patch the paths to use our temp directory
        import run_pipeline.skill_matching.job_skill_matcher as job_skill_matcher
        original_job_dir = job_skill_matcher.postings_DIR
        job_skill_matcher.postings_DIR = temp_dir
        
        import run_pipeline.skill_matching.efficient_skill_matcher as efficient_skill_matcher
        efficient_original_job_dir = efficient_skill_matcher.JOB_DATA_DIR
        efficient_skill_matcher.JOB_DATA_DIR = temp_dir
        
        try:
            # Benchmark original implementation
            logger.info(f"Benchmarking original batch implementation for {len(job_ids)} jobs (LLM: {use_llm})")
            start_time = time.time()
            original_batch_match(use_llm=use_llm, job_ids=job_ids)
            original_time = time.time() - start_time
            
            results["original"] = {
                "time": original_time,
                "time_per_job": original_time / len(job_ids) if job_ids else 0
            }
            
            # Benchmark efficient implementation
            logger.info(f"Benchmarking efficient batch implementation for {len(job_ids)} jobs (LLM: {use_llm})")
            start_time = time.time()
            efficient_batch_match(
                use_llm=use_llm, 
                job_ids=job_ids, 
                batch_size=batch_size
            )
            efficient_time = time.time() - start_time
            
            results["efficient"] = {
                "time": efficient_time,
                "time_per_job": efficient_time / len(job_ids) if job_ids else 0,
                "speedup_factor": original_time / efficient_time if efficient_time > 0 else float('inf')
            }
            
        finally:
            # Restore original paths
            job_skill_matcher.postings_DIR = original_job_dir
            efficient_skill_matcher.JOB_DATA_DIR = efficient_original_job_dir
        
        return results

def run_all_benchmarks(job_ids: List[int], batch_sizes: List[int], use_llm: bool = True):
    """Run all benchmarks and generate a report"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "single_job": {},
        "batch": {}
    }
    
    # Run individual job benchmarks
    for job_id in job_ids:
        for batch_size in batch_sizes:
            key = f"job_{job_id}_batch_{batch_size}"
            results["single_job"][key] = benchmark_single_job(
                job_id=job_id,
                batch_size=batch_size,
                use_llm=use_llm
            )
    
    # Run batch benchmarks with different batch sizes
    for batch_size in batch_sizes:
        key = f"batch_{batch_size}_jobs_{len(job_ids)}"
        results["batch"][key] = benchmark_batch(
            job_ids=job_ids,
            batch_size=batch_size,
            use_llm=use_llm
        )
    
    # Save results
    output_file = Path(f"skill_matcher_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Benchmark results saved to {output_file}")
    
    # Print summary
    print("\n==== BENCHMARK SUMMARY ====\n")
    print(f"{'Job ID':<10} {'Batch Size':<10} {'Original (s)':<15} {'Efficient (s)':<15} {'Speedup':<10}")
    print("-" * 60)
    
    for key, result in results["single_job"].items():
        if result:
            original_time = result["original"].get("time", 0)
            efficient_time = result["efficient"].get("time", 0)
            speedup = result["efficient"].get("speedup_factor", 0)
            job_id = result["job_id"]
            batch_size = key.split("_batch_")[1]
            print(f"{job_id:<10} {batch_size:<10} {original_time:<15.2f} {efficient_time:<15.2f} {speedup:<10.2f}x")
    
    print("\n==== BATCH PROCESSING ====\n")
    print(f"{'Batch Size':<10} {'Jobs':<10} {'Original (s)':<15} {'Efficient (s)':<15} {'Speedup':<10}")
    print("-" * 60)
    
    for key, result in results["batch"].items():
        if result:
            original_time = result["original"].get("time", 0)
            efficient_time = result["efficient"].get("time", 0)
            speedup = result["efficient"].get("speedup_factor", 0)
            batch_size = key.split("_jobs_")[0].split("batch_")[1]
            job_count = result["job_count"]
            print(f"{batch_size:<10} {job_count:<10} {original_time:<15.2f} {efficient_time:<15.2f} {speedup:<10.2f}x")

def main():
    parser = argparse.ArgumentParser(description="Benchmark skill matching implementations")
    parser.add_argument('--job-ids', type=int, nargs='+', required=True,
                        help='Job IDs to benchmark')
    parser.add_argument('--batch-sizes', type=int, nargs='+', default=[5, 10, 20],
                        help='Batch sizes to test (default: 5, 10, 20)')
    parser.add_argument('--no-llm', action='store_true',
                        help='Disable LLM-based matching for benchmarks')
    
    args = parser.parse_args()
    
    run_all_benchmarks(
        job_ids=args.job_ids,
        batch_sizes=args.batch_sizes,
        use_llm=not args.no_llm
    )

if __name__ == "__main__":
    main()
