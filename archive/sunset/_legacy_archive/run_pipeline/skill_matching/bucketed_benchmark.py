#!/usr/bin/env python3
"""
[DEPRECATED] - DO NOT USE - Benchmark Script for Bucketed Skill Matching

THIS FILE IS DEPRECATED AND SHOULD NOT BE USED.
A new implementation has replaced this module.
This file is kept only for historical reference.

This script compares the performance of all implemented skill matching approaches:
1. Original implementation (job_skill_matcher.py)
2. Efficient implementation (efficient_skill_matcher.py)
3. Enhanced implementation (enhanced_skill_matcher.py)
4. Bucketed implementation (bucketed_skill_matcher.py)

It provides both single-job and batch processing benchmarks.
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
import resource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucketed_benchmark")

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
    try:
        from run_pipeline.skill_matching.enhanced_skill_matcher import enhanced_batch_match_all_jobs as enhanced_batch_match
        from run_pipeline.skill_matching.enhanced_skill_matcher import process_job_skills_enhanced as enhanced_match
        ENHANCED_AVAILABLE = True
    except ImportError:
        logger.warning("Enhanced implementation not available")
        ENHANCED_AVAILABLE = False
    
    # Bucketed implementation
    from run_pipeline.skill_matching.bucketed_skill_matcher import batch_match_all_jobs as bucketed_batch_match
    from run_pipeline.skill_matching.bucket_matcher import match_job_to_your_skills as bucketed_match
    
except ImportError as e:
    logger.warning(f"Error importing skill matchers: {e}")
    sys.exit(1)

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
        batch_size: Batch size for batch operations
        use_llm: Whether to use LLM for matching
        use_embeddings: Whether to use embeddings for enhanced matching
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
    your_skill_count = len(your_skills.get("complex_skills", [])) + len(your_skills.get("elementary_skills", []))
    
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
        "efficient": {},
        "bucketed": {}
    }
    
    if ENHANCED_AVAILABLE:
        results["enhanced"] = {}
    
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
        "matches": len(matches) if matches else 0,
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
        "matches": len(matches) if matches else 0,
        "speedup": original_time / efficient_time if efficient_time > 0 else float('inf')
    }
    
    # Benchmark enhanced implementation if available
    if ENHANCED_AVAILABLE:
        logger.info(f"Benchmarking enhanced implementation for job {job_id} (LLM: {use_llm}, Embeddings: {use_embeddings})")
        start_time = time.time()
        matches = enhanced_match(
            job_data,
            your_skills,
            use_llm=use_llm,
            use_embeddings=use_embeddings,
            batch_size=batch_size
        )
        enhanced_time = time.time() - start_time
        
        results["enhanced"] = {
            "time": enhanced_time,
            "matches": len(matches) if matches else 0,
            "speedup": original_time / enhanced_time if enhanced_time > 0 else float('inf')
        }
    
    # Benchmark bucketed implementation
    logger.info(f"Benchmarking bucketed implementation for job {job_id}")
    start_time = time.time()
    match_result = bucketed_match(job_data, your_skills)
    bucketed_time = time.time() - start_time
    
    # Extract bucket information
    bucket_stats = {}
    if match_result and "bucket_results" in match_result:
        for bucket, data in match_result.get("bucket_results", {}).items():
            bucket_stats[bucket] = {
                "job_skills": len(data.get("job_skills", [])),
                "cv_skills": len(data.get("cv_skills", [])),
                "match_percentage": data.get("match_percentage", 0.0),
                "weight": data.get("weight", 0.0)
            }
    
    results["bucketed"] = {
        "time": bucketed_time,
        "overall_match": match_result.get("overall_match", 0.0) if match_result else 0.0,
        "bucket_stats": bucket_stats,
        "speedup": original_time / bucketed_time if bucketed_time > 0 else float('inf')
    }
    
    # Clean up temp file
    try:
        os.unlink(tmp_path)
    except:
        pass
    
    return results

def benchmark_batch_all_implementations(
    job_ids: List[int],
    batch_size: int = 10,
    max_workers: int = 4,
    use_llm: bool = True,
    use_embeddings: bool = True
):
    """
    Benchmark all batch implementations
    
    Args:
        job_ids: List of job IDs to process
        batch_size: Batch size for LLM calls
        max_workers: Max worker threads for parallel processing
        use_llm: Whether to use LLM for matching
        use_embeddings: Whether to use embeddings for enhanced matching
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
        your_skill_count = len(your_skills.get("complex_skills", [])) + len(your_skills.get("elementary_skills", [])) #type: ignore
        
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
            "bucketed": {}
        }
        
        if ENHANCED_AVAILABLE:
            results["enhanced"] = {}
        
        # Monkey patch the paths to use our temp directory
        import run_pipeline.skill_matching.job_skill_matcher as job_skill_matcher
        original_job_dir = job_skill_matcher.postings_DIR
        job_skill_matcher.postings_DIR = temp_dir
        
        import run_pipeline.skill_matching.efficient_skill_matcher as efficient_skill_matcher
        efficient_original_job_dir = efficient_skill_matcher.JOB_DATA_DIR
        efficient_skill_matcher.JOB_DATA_DIR = temp_dir
        
        # For bucketed matcher
        import run_pipeline.skill_matching.bucket_utils as bucket_utils
        bucket_original_job_dir = bucket_utils.JOB_DATA_DIR
        bucket_utils.JOB_DATA_DIR = temp_dir
        
        if ENHANCED_AVAILABLE:
            import run_pipeline.skill_matching.enhanced_skill_matcher as enhanced_skill_matcher
            enhanced_original_job_dir = enhanced_skill_matcher.JOB_DATA_DIR
            enhanced_skill_matcher.JOB_DATA_DIR = temp_dir
        
        try:
            # Start with memory stats
            start_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            
            # Benchmark original implementation
            logger.info(f"Benchmarking original batch implementation for {len(job_ids)} jobs (LLM: {use_llm})")
            start_time = time.time()
            original_batch_match(use_llm=use_llm, job_ids=job_ids)
            original_time = time.time() - start_time
            
            original_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - start_mem
            
            results["original"] = {
                "time": original_time,
                "time_per_job": original_time / len(job_ids) if job_ids else 0,
                "memory_kb": original_mem
            }
            
            # Benchmark efficient implementation
            logger.info(f"Benchmarking efficient batch implementation for {len(job_ids)} jobs (LLM: {use_llm})")
            start_time = time.time()
            start_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            
            efficient_batch_match(
                use_llm=use_llm, 
                job_ids=job_ids, 
                batch_size=batch_size
            )
            efficient_time = time.time() - start_time
            efficient_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - start_mem
            
            results["efficient"] = {
                "time": efficient_time,
                "time_per_job": efficient_time / len(job_ids) if job_ids else 0,
                "speedup": original_time / efficient_time if efficient_time > 0 else float('inf'),
                "memory_kb": efficient_mem
            }
            
            # Benchmark enhanced implementation if available
            if ENHANCED_AVAILABLE:
                logger.info(f"Benchmarking enhanced batch implementation for {len(job_ids)} jobs (LLM: {use_llm}, Workers: {max_workers}, Embeddings: {use_embeddings})")
                start_time = time.time()
                start_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                
                enhanced_batch_match(
                    job_ids=job_ids,
                    batch_size=batch_size,
                    max_workers=max_workers,
                    use_llm=use_llm,
                    use_embeddings=use_embeddings
                )
                enhanced_time = time.time() - start_time
                enhanced_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - start_mem
                
                results["enhanced"] = {
                    "time": enhanced_time,
                    "time_per_job": enhanced_time / len(job_ids) if job_ids else 0,
                    "speedup": original_time / enhanced_time if enhanced_time > 0 else float('inf'),
                    "memory_kb": enhanced_mem
                }
            
            # Benchmark bucketed implementation
            logger.info(f"Benchmarking bucketed batch implementation for {len(job_ids)} jobs")
            start_time = time.time()
            start_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            
            bucketed_batch_match(
                job_ids=job_ids,
                batch_size=batch_size,
                max_workers=max_workers
            )
            bucketed_time = time.time() - start_time
            bucketed_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - start_mem
            
            results["bucketed"] = {
                "time": bucketed_time,
                "time_per_job": bucketed_time / len(job_ids) if job_ids else 0,
                "speedup": original_time / bucketed_time if bucketed_time > 0 else float('inf'),
                "memory_kb": bucketed_mem
            }
            
        finally:
            # Restore original paths
            job_skill_matcher.postings_DIR = original_job_dir
            efficient_skill_matcher.JOB_DATA_DIR = efficient_original_job_dir
            bucket_utils.JOB_DATA_DIR = bucket_original_job_dir
            
            if ENHANCED_AVAILABLE:
                enhanced_skill_matcher.JOB_DATA_DIR = enhanced_original_job_dir
        
        return results

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
        print(f"{'Implementation':<15} {'Time (s)':<12} {'Matches':<10} {'Speedup':<12}")
        print("-" * 58)
        
        implementations = []
        implementations.append(("Original", results["original"]))
        implementations.append(("Efficient", results["efficient"]))
        
        if "enhanced" in results:
            implementations.append(("Enhanced", results["enhanced"]))
        
        implementations.append(("Bucketed", results["bucketed"]))
        
        for name, data in implementations:
            time_val = data.get("time", 0)
            matches = data.get("matches", 0)
            speedup = data.get("speedup", "1.00x")
            if isinstance(speedup, float):
                speedup = f"{speedup:.2f}x"
            print(f"{name:<15} {time_val:<12.3f} {matches:<10} {speedup:<12}")
            
        # Print bucket details for the bucketed approach
        if "bucketed" in results and "bucket_stats" in results["bucketed"]:
            print("\nBucket Details (Bucketed Approach):")
            print(f"{'Bucket':<15} {'Job Skills':<12} {'CV Skills':<12} {'Match %':<10} {'Weight':<10}")
            print("-" * 65)
            
            for bucket, stats in results["bucketed"]["bucket_stats"].items():
                job_skills = stats.get("job_skills", 0)
                cv_skills = stats.get("cv_skills", 0)
                match_pct = stats.get("match_percentage", 0) * 100
                weight = stats.get("weight", 0)
                
                print(f"{bucket:<15} {job_skills:<12} {cv_skills:<12} {match_pct:<10.1f}% {weight:<10.2f}")
            
            print(f"\nOverall match: {results['bucketed'].get('overall_match', 0) * 100:.1f}%")
    
    else:
        # Batch benchmark
        print(f"Jobs processed: {results['job_count']}")
        print(f"Total job skills: {results['total_job_skills']}")
        print(f"Your skills: {results['your_skill_count']}")
        print(f"Total potential comparisons: {results['total_comparisons']}")
        print(f"LLM used: {results['use_llm']}")
        print(f"Batch size: {results['batch_size']}")
        print(f"Max workers: {results['max_workers']}")
        
        print("\nExecution times:")
        print(f"{'Implementation':<15} {'Time (s)':<12} {'Time/Job':<12} {'Memory (KB)':<12} {'Speedup':<12}")
        print("-" * 70)
        
        implementations = []
        implementations.append(("Original", results["original"]))
        implementations.append(("Efficient", results["efficient"]))
        
        if "enhanced" in results:
            implementations.append(("Enhanced", results["enhanced"]))
        
        implementations.append(("Bucketed", results["bucketed"]))
        
        for name, data in implementations:
            time_val = data.get("time", 0)
            time_per_job = data.get("time_per_job", 0)
            memory = data.get("memory_kb", 0)
            speedup = data.get("speedup", "1.00x")
            
            if isinstance(speedup, float):
                speedup = f"{speedup:.2f}x"
            
            print(f"{name:<15} {time_val:<12.3f} {time_per_job:<12.3f} {memory:<12} {speedup:<12}")

def save_benchmark_results(results: Dict[str, Any], prefix: str = ""):
    """Save benchmark results to a file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = PROJECT_ROOT / "data" / "benchmarks"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    if prefix:
        filename = f"skill_matcher_benchmark_{timestamp}_{prefix}.json"
    else:
        filename = f"skill_matcher_benchmark_{timestamp}.json"
    
    output_file = output_dir / filename
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Benchmark results saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save benchmark results: {e}")

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
