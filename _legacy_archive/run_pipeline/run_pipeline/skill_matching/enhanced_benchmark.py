#!/usr/bin/env python3
"""
[DEPRECATED] - DO NOT USE - Enhanced Benchmark Script for Comparing Skill Matching Implementations

THIS FILE IS DEPRECATED AND SHOULD NOT BE USED.
A new implementation has replaced this module.
This file is kept only for historical reference.

This script compares the performance of three skill matching approaches:
1. Original implementation (job_skill_matcher.py)
2. Efficient implementation (efficient_skill_matcher.py) 
3. Enhanced implementation (enhanced_skill_matcher.py)

It measures execution time, match quality, and resource usage across implementations.
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tempfile
import shutil
import traceback
import resource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced_benchmark")

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Import implementations
try:
    # Original implementation
    from run_pipeline.skill_matching.job_skill_matcher import batch_match_all_jobs as original_batch_match
    from run_pipeline.skill_matching.job_skill_matcher import match_job_to_your_skills_llm as original_match_llm
    
    # Efficient implementation
    from run_pipeline.skill_matching.efficient_skill_matcher import batch_match_all_jobs as efficient_batch_match
    from run_pipeline.skill_matching.efficient_skill_matcher import process_job_skills as efficient_match
    
    # Enhanced implementation
    from run_pipeline.skill_matching.enhanced_skill_matcher import enhanced_batch_match_all_jobs as enhanced_batch_match
    from run_pipeline.skill_matching.enhanced_skill_matcher import process_job_skills_enhanced as enhanced_match
    
    ENHANCED_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Enhanced implementation not available: {e}")
    ENHANCED_AVAILABLE = False

# Import common utilities
from run_pipeline.config.paths import JOB_DATA_DIR, PROJECT_ROOT

def load_job_data(job_path: Path) -> Optional[Dict[str, Any]]:
    """Load job data from a file"""
    try:
        with open(job_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load job file {job_path}: {e}")
        return None

def save_job_data(job_path: Path, job_data: Dict[str, Any]) -> None:
    """Save job data to a file"""
    try:
        with open(job_path, "w", encoding="utf-8") as f:
            json.dump(job_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save job file {job_path}: {e}")

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

def benchmark_single_job_all_implementations(
    job_id: int, 
    batch_size: int = 10, 
    use_llm: bool = True,
    use_embeddings: bool = True
):
    """
    Benchmark all implementations for a single job file
    
    Args:
        job_id: The job ID to benchmark
        batch_size: Batch size for the batched implementations
        use_llm: Whether to use LLM for matching
        use_embeddings: Whether to use embeddings in enhanced implementation
        
    Returns:
        Dictionary with benchmark results
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
    
    results = {
        "job_id": job_id,
        "job_skill_count": job_skill_count,
        "your_skill_count": your_skill_count,
        "total_comparisons": job_skill_count * your_skill_count,
        "use_llm": use_llm,
        "batch_size": batch_size,
        "original": {},
        "efficient": {},
        "enhanced": {} if ENHANCED_AVAILABLE else None
    }
    
    # Create a temp copy of the job data to avoid modifying the original
    temp_job_data = json.loads(json.dumps(job_data))
    
    # Function to measure resource usage
    def get_resource_usage():
        usage = resource.getrusage(resource.RUSAGE_SELF)
        return {
            "memory_mb": usage.ru_maxrss / 1024,  # Convert KB to MB
            "user_cpu_time": usage.ru_utime,
            "system_cpu_time": usage.ru_stime,
            "total_cpu_time": usage.ru_utime + usage.ru_stime
        }
    
    # Benchmark original implementation
    logger.info(f"Benchmarking original implementation for job {job_id} (LLM: {use_llm})")
    start_time = time.time()
    start_resources = get_resource_usage()
    
    try:
        if use_llm:
            matches = original_match_llm(temp_job_data, your_skills)
        else:
            # Use the non-LLM version
            from run_pipeline.skill_matching.job_skill_matcher import match_job_to_your_skills
            matches = match_job_to_your_skills(temp_job_data, your_skills)
        
        original_time = time.time() - start_time
        end_resources = get_resource_usage()
        
        results["original"] = {
            "time": original_time,
            "matches": len(matches) if matches else 0,
            "time_per_comparison": original_time / (job_skill_count * your_skill_count) if job_skill_count * your_skill_count > 0 else 0,
            "resources": {
                "memory_usage_mb": end_resources["memory_mb"] - start_resources["memory_mb"],
                "cpu_time": end_resources["total_cpu_time"] - start_resources["total_cpu_time"]
            }
        }
    except Exception as e:
        results["original"] = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    
    # Benchmark efficient implementation
    logger.info(f"Benchmarking efficient implementation for job {job_id} (LLM: {use_llm})")
    temp_job_data = json.loads(json.dumps(job_data))  # Reset job data
    start_time = time.time()
    start_resources = get_resource_usage()
    
    try:
        matches = efficient_match(
            temp_job_data, 
            your_skills, 
            use_llm=use_llm,
            batch_size=batch_size
        )
        
        efficient_time = time.time() - start_time
        end_resources = get_resource_usage()
        
        results["efficient"] = {
            "time": efficient_time,
            "matches": len(matches) if matches else 0,
            "time_per_comparison": efficient_time / (job_skill_count * your_skill_count) if job_skill_count * your_skill_count > 0 else 0,
            "speedup_factor": results["original"].get("time", 0) / efficient_time if efficient_time > 0 else float('inf'),#type: ignore
            "resources": {
                "memory_usage_mb": end_resources["memory_mb"] - start_resources["memory_mb"],
                "cpu_time": end_resources["total_cpu_time"] - start_resources["total_cpu_time"]
            }
        }
    except Exception as e:
        results["efficient"] = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    
    # Benchmark enhanced implementation if available
    if ENHANCED_AVAILABLE:
        logger.info(f"Benchmarking enhanced implementation for job {job_id} (LLM: {use_llm}, Embeddings: {use_embeddings})")
        temp_job_data = json.loads(json.dumps(job_data))  # Reset job data
        start_time = time.time()
        start_resources = get_resource_usage()
        
        try:
            matches = enhanced_match(
                temp_job_data, 
                your_skills, 
                use_llm=use_llm,
                batch_size=batch_size,
                use_embeddings=use_embeddings
            )
            
            enhanced_time = time.time() - start_time
            end_resources = get_resource_usage()
            
            results["enhanced"] = {
                "time": enhanced_time,
                "matches": len(matches) if matches else 0,
                "time_per_comparison": enhanced_time / (job_skill_count * your_skill_count) if job_skill_count * your_skill_count > 0 else 0,
                "speedup_vs_original": results["original"].get("time", 0) / enhanced_time if enhanced_time > 0 else float('inf'),#type: ignore
                "speedup_vs_efficient": results["efficient"].get("time", 0) / enhanced_time if enhanced_time > 0 else float('inf'),#type: ignore
                "use_embeddings": use_embeddings,
                "resources": {
                    "memory_usage_mb": end_resources["memory_mb"] - start_resources["memory_mb"],
                    "cpu_time": end_resources["total_cpu_time"] - start_resources["total_cpu_time"]
                }
            }
        except Exception as e:
            results["enhanced"] = {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "use_embeddings": use_embeddings
            }
    
    return results

def benchmark_batch_all_implementations(
    job_ids: List[int], 
    batch_size: int = 10, 
    use_llm: bool = True,
    max_workers: int = 4,
    use_embeddings: bool = True
):
    """
    Benchmark batch processing of all implementations across multiple jobs
    
    Args:
        job_ids: List of job IDs to benchmark
        batch_size: Batch size for batched processing
        use_llm: Whether to use LLM for matching
        max_workers: Max workers for parallel processing
        use_embeddings: Whether to use embeddings in the enhanced implementation
        
    Returns:
        Dictionary with benchmark results
    """
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
            "batch_size": batch_size,
            "max_workers": max_workers,
            "original": {},
            "efficient": {},
            "enhanced": {} if ENHANCED_AVAILABLE else None
        }
        
        # Function to measure resource usage
        def get_resource_usage():
            usage = resource.getrusage(resource.RUSAGE_SELF)
            return {
                "memory_mb": usage.ru_maxrss / 1024,  # Convert KB to MB
                "user_cpu_time": usage.ru_utime,
                "system_cpu_time": usage.ru_stime,
                "total_cpu_time": usage.ru_utime + usage.ru_stime
            }
        
        # Monkey patch the paths to use our temp directory
        import run_pipeline.skill_matching.job_skill_matcher as job_skill_matcher
        original_job_dir = job_skill_matcher.postings_DIR
        job_skill_matcher.postings_DIR = temp_dir
        
        import run_pipeline.skill_matching.efficient_skill_matcher as efficient_skill_matcher
        efficient_original_job_dir = efficient_skill_matcher.JOB_DATA_DIR
        efficient_skill_matcher.JOB_DATA_DIR = temp_dir
        
        if ENHANCED_AVAILABLE:
            import run_pipeline.skill_matching.enhanced_skill_matcher as enhanced_skill_matcher
            enhanced_original_job_dir = enhanced_skill_matcher.JOB_DATA_DIR
            enhanced_skill_matcher.JOB_DATA_DIR = temp_dir
        
        try:
            # Benchmark original implementation
            logger.info(f"Benchmarking original batch implementation for {len(job_ids)} jobs (LLM: {use_llm})")
            start_time = time.time()
            start_resources = get_resource_usage()
            
            try:
                original_batch_match(use_llm=use_llm, job_ids=job_ids)
                original_time = time.time() - start_time
                end_resources = get_resource_usage()
                
                # Collect metrics from job files
                matches_count = 0
                match_percentages = []
                
                for job_id in job_ids:
                    job_path = temp_dir / f"job{job_id}.json"
                    if job_path.exists():
                        job_data = load_job_data(job_path)
                        if job_data and "skill_matches" in job_data:
                            matches = job_data["skill_matches"].get("matches", [])
                            match_percentage = job_data["skill_matches"].get("match_percentage", 0)
                            
                            matches_count += len(matches)
                            match_percentages.append(match_percentage)
                
                avg_match_percentage = sum(match_percentages) / len(match_percentages) if match_percentages else 0
                
                results["original"] = {
                    "time": original_time,
                    "total_matches": matches_count,
                    "avg_matches_per_job": matches_count / len(job_ids) if job_ids else 0,
                    "avg_match_percentage": avg_match_percentage,
                    "time_per_job": original_time / len(job_ids) if job_ids else 0,
                    "resources": {
                        "memory_usage_mb": end_resources["memory_mb"] - start_resources["memory_mb"],
                        "cpu_time": end_resources["total_cpu_time"] - start_resources["total_cpu_time"]
                    }
                }
            except Exception as e:
                results["original"] = {
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            
            # Reset job files
            for job_id in job_ids:
                source = JOB_DATA_DIR / f"job{job_id}.json"
                if source.exists():
                    target = temp_dir / f"job{job_id}.json"
                    shutil.copy(source, target)
            
            # Benchmark efficient implementation
            logger.info(f"Benchmarking efficient batch implementation for {len(job_ids)} jobs (LLM: {use_llm})")
            start_time = time.time()
            start_resources = get_resource_usage()
            
            try:
                efficient_batch_match(
                    use_llm=use_llm, 
                    job_ids=job_ids,
                    batch_size=batch_size,
                    max_workers=1  # Original implementation doesn't use max_workers effectively
                )
                efficient_time = time.time() - start_time
                end_resources = get_resource_usage()
                
                # Collect metrics from job files
                matches_count = 0
                match_percentages = []
                
                for job_id in job_ids:
                    job_path = temp_dir / f"job{job_id}.json"
                    if job_path.exists():
                        job_data = load_job_data(job_path)
                        if job_data and "skill_matches" in job_data:
                            matches = job_data["skill_matches"].get("matches", [])
                            match_percentage = job_data["skill_matches"].get("match_percentage", 0)
                            
                            matches_count += len(matches)
                            match_percentages.append(match_percentage)
                
                avg_match_percentage = sum(match_percentages) / len(match_percentages) if match_percentages else 0
                
                results["efficient"] = {
                    "time": efficient_time,
                    "total_matches": matches_count,
                    "avg_matches_per_job": matches_count / len(job_ids) if job_ids else 0,
                    "avg_match_percentage": avg_match_percentage,
                    "time_per_job": efficient_time / len(job_ids) if job_ids else 0,
                    "speedup_factor": results["original"].get("time", 0) / efficient_time if efficient_time > 0 else float('inf'),#type: ignore
                    "resources": {
                        "memory_usage_mb": end_resources["memory_mb"] - start_resources["memory_mb"],
                        "cpu_time": end_resources["total_cpu_time"] - start_resources["total_cpu_time"]
                    }
                }
            except Exception as e:
                results["efficient"] = {
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            
            # Benchmark enhanced implementation if available
            if ENHANCED_AVAILABLE:
                # Reset job files
                for job_id in job_ids:
                    source = JOB_DATA_DIR / f"job{job_id}.json"
                    if source.exists():
                        target = temp_dir / f"job{job_id}.json"
                        shutil.copy(source, target)
                
                logger.info(f"Benchmarking enhanced batch implementation for {len(job_ids)} jobs " +
                          f"(LLM: {use_llm}, Workers: {max_workers}, Embeddings: {use_embeddings})")
                start_time = time.time()
                start_resources = get_resource_usage()
                
                try:
                    enhanced_batch_match(
                        use_llm=use_llm, 
                        job_ids=job_ids,
                        batch_size=batch_size,
                        max_workers=max_workers,
                        use_embeddings=use_embeddings
                    )
                    enhanced_time = time.time() - start_time
                    end_resources = get_resource_usage()
                    
                    # Collect metrics from job files
                    matches_count = 0
                    match_percentages = []
                    
                    for job_id in job_ids:
                        job_path = temp_dir / f"job{job_id}.json"
                        if job_path.exists():
                            job_data = load_job_data(job_path)
                            if job_data and "skill_matches" in job_data:
                                matches = job_data["skill_matches"].get("matches", [])
                                match_percentage = job_data["skill_matches"].get("match_percentage", 0)
                                
                                matches_count += len(matches)
                                match_percentages.append(match_percentage)
                    
                    avg_match_percentage = sum(match_percentages) / len(match_percentages) if match_percentages else 0
                    
                    results["enhanced"] = {
                        "time": enhanced_time,
                        "total_matches": matches_count,
                        "avg_matches_per_job": matches_count / len(job_ids) if job_ids else 0,
                        "avg_match_percentage": avg_match_percentage,
                        "time_per_job": enhanced_time / len(job_ids) if job_ids else 0,
                        "speedup_vs_original": results["original"].get("time", 0) / enhanced_time if enhanced_time > 0 else float('inf'),#type: ignore
                        "speedup_vs_efficient": results["efficient"].get("time", 0) / enhanced_time if enhanced_time > 0 else float('inf'),#type: ignore
                        "use_embeddings": use_embeddings,
                        "max_workers": max_workers,
                        "resources": {
                            "memory_usage_mb": end_resources["memory_mb"] - start_resources["memory_mb"],
                            "cpu_time": end_resources["total_cpu_time"] - start_resources["total_cpu_time"]
                        }
                    }
                except Exception as e:
                    results["enhanced"] = {
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                        "use_embeddings": use_embeddings,
                        "max_workers": max_workers
                    }
        
        finally:
            # Restore original paths
            job_skill_matcher.postings_DIR = original_job_dir
            efficient_skill_matcher.JOB_DATA_DIR = efficient_original_job_dir
            
            if ENHANCED_AVAILABLE:
                enhanced_skill_matcher.JOB_DATA_DIR = enhanced_original_job_dir
        
        return results

def save_benchmark_results(results: Dict[str, Any], name: str = None):#type: ignore
    """Save benchmark results to file"""
    benchmark_dir = PROJECT_ROOT / "data" / "benchmarks"
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"skill_matcher_benchmark_{timestamp}"
    if name:
        file_name += f"_{name}"
    file_name += ".json"
    
    result_path = benchmark_dir / file_name
    
    try:
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Benchmark results saved to {result_path}")
        
        # Also save to a consistent location for easy access
        with open(benchmark_dir / "latest_benchmark.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving benchmark results: {e}")

def print_benchmark_summary(results: Dict[str, Any]):
    """Print a summary of benchmark results"""
    print("\n=== BENCHMARK SUMMARY ===\n")
    
    if "job_id" in results:
        # Single job benchmark
        print(f"Job ID: {results['job_id']}")
        print(f"Job skills: {results['job_skill_count']}")
        print(f"Your skills: {results['your_skill_count']}")
        print(f"Total potential comparisons: {results['total_comparisons']}")
        print(f"LLM used: {results['use_llm']}")
        print("\nExecution times:")
        
        implementations = []
        
        if "original" in results and isinstance(results["original"], dict) and "time" in results["original"]:
            implementations.append(("Original", results["original"]))
        
        if "efficient" in results and isinstance(results["efficient"], dict) and "time" in results["efficient"]:
            implementations.append(("Efficient", results["efficient"]))
        
        if ENHANCED_AVAILABLE and "enhanced" in results and isinstance(results["enhanced"], dict) and "time" in results["enhanced"]:
            implementations.append(("Enhanced", results["enhanced"]))
        
        # Print table header
        print(f"{'Implementation':<15} {'Time (s)':<12} {'Matches':<10} {'Speedup':<12}")
        print("-" * 50)
        
        # Print implementation data
        original_time = None
        for name, data in implementations:
            time_val = data.get("time", 0)
            matches = data.get("matches", 0)
            
            if name == "Original":
                original_time = time_val
                speedup = "1.00x"
            else:
                speedup = f"{original_time / time_val:.2f}x" if time_val > 0 and original_time else "N/A"
            
            print(f"{name:<15} {time_val:<12.3f} {matches:<10} {speedup:<12}")
    
    else:
        # Batch benchmark
        print(f"Jobs processed: {results['job_count']}")
        print(f"Total job skills: {results['total_job_skills']}")
        print(f"Your skills: {results['your_skill_count']}")
        print(f"Total potential comparisons: {results['total_comparisons']}")
        print(f"LLM used: {results['use_llm']}")
        print(f"Batch size: {results['batch_size']}")
        
        if "max_workers" in results:
            print(f"Max workers: {results['max_workers']}")
        
        print("\nExecution times:")
        
        implementations = []
        
        if "original" in results and isinstance(results["original"], dict) and "time" in results["original"]:
            implementations.append(("Original", results["original"]))
        
        if "efficient" in results and isinstance(results["efficient"], dict) and "time" in results["efficient"]:
            implementations.append(("Efficient", results["efficient"]))
        
        if ENHANCED_AVAILABLE and "enhanced" in results and isinstance(results["enhanced"], dict) and "time" in results["enhanced"]:
            implementations.append(("Enhanced", results["enhanced"]))
        
        # Print table header
        print(f"{'Implementation':<15} {'Time (s)':<12} {'Time/Job':<12} {'Matches':<10} {'Match %':<12} {'Speedup':<12}")
        print("-" * 80)
        
        # Print implementation data
        original_time = None
        for name, data in implementations:
            time_val = data.get("time", 0)
            matches = data.get("total_matches", 0)
            time_per_job = data.get("time_per_job", 0)
            match_pct = data.get("avg_match_percentage", 0) * 100
            
            if name == "Original":
                original_time = time_val
                speedup = "1.00x"
            else:
                speedup = f"{original_time / time_val:.2f}x" if time_val > 0 and original_time else "N/A"
            
            print(f"{name:<15} {time_val:<12.3f} {time_per_job:<12.3f} {matches:<10} {match_pct:<12.2f}% {speedup:<12}")
    
    print("\n")

def main():
    """Main function for running benchmarks"""
    parser = argparse.ArgumentParser(description="Benchmark skill matcher implementations.")
    
    # Common arguments
    parser.add_argument("--job-ids", type=int, required=True, nargs="+",
                        help="Job IDs to benchmark (e.g., --job-ids 1 2 3)")
    parser.add_argument("--single", action="store_true", 
                        help="Benchmark each job individually")
    parser.add_argument("--batch", action="store_true", 
                        help="Benchmark batch processing")
    parser.add_argument("--batch-size", type=int, default=10,
                        help="Batch size for LLM calls (default: 10)")
    parser.add_argument("--max-workers", type=int, default=4,
                        help="Maximum worker threads for parallel processing (default: 4)")
    parser.add_argument("--no-llm", action="store_true",
                        help="Skip LLM-based matching")
    parser.add_argument("--no-embeddings", action="store_true",
                        help="Skip embedding-based matching")
    parser.add_argument("--output", type=str,
                        help="Name prefix for the output file")
    
    args = parser.parse_args()
    
    # Set defaults if neither single nor batch specified
    if not args.single and not args.batch:
        args.batch = True
    
    use_llm = not args.no_llm
    use_embeddings = not args.no_embeddings
    
    if args.single:
        # Benchmark each job individually
        all_results = {
            "timestamp": datetime.now().isoformat(),
            "batch_size": args.batch_size,
            "max_workers": args.max_workers,
            "use_llm": use_llm,
            "use_embeddings": use_embeddings,
            "results": {}
        }
        
        for job_id in args.job_ids:
            logger.info(f"Benchmarking job {job_id}")
            result = benchmark_single_job_all_implementations(
                job_id=job_id,
                batch_size=args.batch_size,
                use_llm=use_llm,
                use_embeddings=use_embeddings
            )
            
            if result:
                all_results["results"][str(job_id)] = result
                print_benchmark_summary(result)
        
        # Save combined results
        save_benchmark_results(all_results, f"single_{args.output}" if args.output else "single")
    
    if args.batch:
        # Benchmark batch processing
        logger.info(f"Benchmarking batch processing for {len(args.job_ids)} jobs")
        batch_result = benchmark_batch_all_implementations(
            job_ids=args.job_ids,
            batch_size=args.batch_size,
            use_llm=use_llm,
            max_workers=args.max_workers,
            use_embeddings=use_embeddings
        )
        
        if batch_result:
            save_benchmark_results(batch_result, f"batch_{args.output}" if args.output else "batch")
            print_benchmark_summary(batch_result)

if __name__ == "__main__":
    main()
