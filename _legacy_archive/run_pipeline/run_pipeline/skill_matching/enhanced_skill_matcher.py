#!/usr/bin/env python3
"""
Enhanced Skill Matching Orchestration

This module orchestrates the enhanced skill matching process, utilizing optimized approaches for matching job skills to CV skills.
It coordinates the workflow, leveraging externalized modules for caching, category mapping, embedding generation, and LLM processing.
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced_skill_matcher")

# Get paths from the main config
try:
    from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR
except ImportError:
    # Fallback if imported outside the pipeline
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    JOB_DATA_DIR = PROJECT_ROOT / "data" / "postings"

# Define paths
YOUR_SKILLS_FILE = PROJECT_ROOT / "profile" / "skills" / "skill_decompositions.json"
CACHE_DIR = PROJECT_ROOT / "data" / "skill_match_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / "skill_match_cache.json"

# Ensure cache directory exists
if not CACHE_DIR.exists():
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created skill match cache directory: {CACHE_DIR}")
    except Exception as e:
        logger.warning(f"Failed to create cache directory {CACHE_DIR}: {e}")

# Ollama settings
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")

# Importing externalized modules for caching, category mapping, embedding generation, and LLM processing
from run_pipeline.skill_matching.cache import SkillMatchCache
from run_pipeline.skill_matching.category_utils import get_skill_category, should_compare_skills, SKILL_CATEGORIES, COMPATIBLE_CATEGORIES
from run_pipeline.skill_matching.embedding_matching import generate_skill_embeddings, find_embedding_matches, EMBEDDINGS_AVAILABLE
from run_pipeline.skill_matching.llm_matching import batch_llm_domain_overlap


def domain_overlap(job_skill: dict, your_skill: dict) -> float:
    job_domains = set(job_skill.get("domains", []))
    your_domains = set(your_skill.get("domains", []))
    if not job_domains or not your_domains:
        return 0.0
    intersection = job_domains & your_domains
    union = job_domains | your_domains
    return len(intersection) / len(union) if union else 0.0


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
    """Load your skills from the skills file"""
    if not YOUR_SKILLS_FILE.exists():
        logger.error(f"Your skills file not found: {YOUR_SKILLS_FILE}")
        return None
    try:
        with open(YOUR_SKILLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load your skills: {e}")
        return None


def process_job_skills_enhanced(
    job_data: Dict[str, Any], 
    your_skills: Dict[str, Any], 
    use_llm: bool = True, 
    batch_size: int = 10, 
    domain_threshold: float = 0.3,
    embedding_threshold: float = 0.6,
    use_embeddings: bool = True
) -> List[Dict[str, Any]]:
    """
    Process job skills against CV skills using enhanced multi-strategy matching approach
    
    Args:
        job_data: Job data including SDR skills
        your_skills: Your CV skills
        use_llm: Whether to use LLM for matching (more accurate but slower)
        batch_size: Number of skill pairs to process in a single LLM call
        domain_threshold: Minimum threshold for considering a match
        embedding_threshold: Minimum threshold for embedding similarity
        use_embeddings: Whether to use embedding-based matching
        
    Returns:
        List of matched skills with scores
    """
    # Initialize cache
    cache = SkillMatchCache(CACHE_FILE)
    
    # Extract job SDR skills
    job_sdr_skills = job_data.get("sdr_skills", {}).get("enriched", {})
    if not job_sdr_skills:
        logger.warning(f"No SDR skills found in job {job_data.get('job_id', 'unknown')}")
        return []
    
    # Generate embeddings if requested and available
    job_skill_embeddings = {}
    your_skill_embeddings = {}
    
    if use_embeddings and EMBEDDINGS_AVAILABLE:
        logger.info("Generating embeddings for skills matching")
        job_skill_embeddings = generate_skill_embeddings(job_sdr_skills)
        your_skill_embeddings = generate_skill_embeddings(your_skills)
    
    # Categorize job skills
    job_skills_by_category: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
    for job_skill_name, job_skill in job_sdr_skills.items():
        category = get_skill_category(job_skill)
        if category not in job_skills_by_category:
            job_skills_by_category[category] = []
        job_skills_by_category[category].append((job_skill_name, job_skill))
    
    # Categorize your skills
    your_skills_by_category: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
    for your_skill_name, your_skill in your_skills.items():
        if isinstance(your_skill, dict):
            category = get_skill_category(your_skill)
            if category not in your_skills_by_category:
                your_skills_by_category[category] = []
            your_skills_by_category[category].append((your_skill_name, your_skill))
    
    # Process each category with compatible categories
    matches = []
    llm_pairs_to_process = []
    
    # Track which skills have already been matched to avoid duplicates
    matched_job_skills = set()
    
    # First pass: Use embeddings for quick approximate matching if available
    if use_embeddings and job_skill_embeddings and your_skill_embeddings:
        logger.info("Using embedding-based matching for initial filtering")
        
        for job_skill_name, embedding in job_skill_embeddings.items():
            # Find potential matches via embeddings
            embedding_matches = find_embedding_matches(
                job_skill_name, 
                embedding, 
                your_skill_embeddings,
                threshold=embedding_threshold
            )
            
            # If we found embedding matches, use the best one
            if embedding_matches:
                best_match_name, best_score = embedding_matches[0]
                
                # Check if we already have this in cache
                cached_score = cache.get(job_skill_name, best_match_name)
                if cached_score is not None and cached_score >= domain_threshold:
                    matches.append({
                        "job_skill": job_skill_name,
                        "your_skill": best_match_name,
                        "cached_score": cached_score,
                        "embedding_score": best_score
                    })
                    matched_job_skills.add(job_skill_name)
                elif use_llm:
                    # Add top embedding matches to LLM verification queue
                    for match_name, _ in embedding_matches[:3]:  # Use top 3 matches for LLM verification
                        llm_pairs_to_process.append((job_skill_name, match_name))
    
    # Second pass: Use cached results and quick domain overlap for eligible pairs
    for job_category, job_skill_list in job_skills_by_category.items():
        for job_skill_name, job_skill in job_skill_list:
            # Skip already matched skills
            if job_skill_name in matched_job_skills:
                continue
                
            best_match = None
            best_score = 0.0
            
            # Check compatible categories
            for cv_category in COMPATIBLE_CATEGORIES.get(job_category, [job_category]):
                if cv_category not in your_skills_by_category:
                    continue
                    
                for your_skill_name, your_skill in your_skills_by_category.get(cv_category, []):
                    # Check cache first
                    cached_score = cache.get(job_skill_name, your_skill_name)
                    if cached_score is not None:
                        score = cached_score
                    else:
                        # If using LLM, queue for batch processing
                        if use_llm:
                            llm_pairs_to_process.append((job_skill_name, your_skill_name))
                            continue
                        else:
                            # Use domain overlap as fallback
                            score = domain_overlap(job_skill, your_skill)
                            cache.set(job_skill_name, your_skill_name, score)
                    
                    # Update best match
                    if score > best_score:
                        best_score = score
                        best_match = your_skill_name
            
            # If we found a good enough match without LLM, add it
            if best_match and best_score >= domain_threshold:
                matched_job_skills.add(job_skill_name)
                matches.append({
                    "job_skill": job_skill_name,
                    "your_skill": best_match,
                    "domain_overlap": best_score
                })
    
    # Third pass: Process queued LLM requests in batches using parallel execution
    if use_llm and llm_pairs_to_process:
        logger.info(f"Processing {len(llm_pairs_to_process)} skill pairs with LLM in batches of {batch_size}")
        
        # Deduplicate skill pairs to avoid processing the same pair twice
        unique_pairs = list(set(llm_pairs_to_process))
        logger.info(f"Removed {len(llm_pairs_to_process) - len(unique_pairs)} duplicate pairs")
        
        results = {}
        
        # Function to process a batch with LLM
        def process_batch(batch_pairs):
            return batch_llm_domain_overlap(batch_pairs)
        
        # Process in batches using ThreadPoolExecutor for parallelism
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit batches for processing
            future_to_batch = {}
            for i in range(0, len(unique_pairs), batch_size):
                batch = unique_pairs[i:i+batch_size]
                future = executor.submit(process_batch, batch)
                future_to_batch[future] = batch
            
            # Process results as they complete
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    batch_results = future.result()
                    results.update(batch_results)
                    
                    # Update cache with results
                    for job_skill_name, your_skill_name in batch:
                        key = f"{job_skill_name}::{your_skill_name}"
                        score = batch_results.get(key, 0.0)
                        cache.set(job_skill_name, your_skill_name, score)
                        
                except Exception as e:
                    logger.error(f"Error processing batch: {e}")
        
        # Final pass to find best matches using LLM results
        for job_category, job_skill_list in job_skills_by_category.items():
            for job_skill_name, job_skill in job_skill_list:
                # Skip already matched skills
                if job_skill_name in matched_job_skills:
                    continue
                    
                best_match = None
                best_score = 0.0
                
                # Check compatible categories
                for cv_category in COMPATIBLE_CATEGORIES.get(job_category, [job_category]):
                    if cv_category not in your_skills_by_category:
                        continue
                        
                    for your_skill_name, your_skill in your_skills_by_category.get(cv_category, []):
                        # Get score from cache (should be there now after batch processing)
                        score = cache.get(job_skill_name, your_skill_name) or 0.0
                        
                        # Update best match
                        if score > best_score:
                            best_score = score
                            best_match = your_skill_name
                
                # Add match if it meets threshold
                if best_match and best_score >= domain_threshold:
                    matches.append({
                        "job_skill": job_skill_name,
                        "your_skill": best_match,
                        "llm_domain_overlap": best_score
                    })
    
    # Save cache for future use
    cache.save_cache()
    
    # Log cache stats
    stats = cache.get_stats()
    logger.info(f"Cache stats: {stats['hits']} hits, {stats['misses']} misses, " +
               f"{stats['hit_rate']:.2%} hit rate, {stats['total_entries']} total entries")
    
    return matches


def process_job_in_thread(
    job_path: Path, 
    your_skills: Dict[str, Any],
    domain_threshold: float = 0.3,
    use_llm: bool = True,
    batch_size: int = 10,
    embedding_threshold: float = 0.6,
    use_embeddings: bool = True
) -> Tuple[bool, str]:
    """Process a single job file in a separate thread"""
    try:
        job_data = load_job_data(job_path)
        if not job_data:
            return False, f"Failed to load job data from {job_path}"
            
        # Process job skills with optimized matching
        matches = process_job_skills_enhanced(
            job_data, your_skills,
            use_llm=use_llm,
            batch_size=batch_size,
            domain_threshold=domain_threshold,
            embedding_threshold=embedding_threshold,
            use_embeddings=use_embeddings
        )
        
        # Calculate match percentage
        job_sdr_skills = job_data.get("sdr_skills", {}).get("enriched", {})
        total_skills = len(job_sdr_skills)
        match_percentage = (len(matches) / total_skills) if total_skills > 0 else 0.0
        
        # Update job data with matches
        job_data["skill_matches"] = {
            "matches": matches,
            "domain_threshold": domain_threshold,
            "llm": use_llm,
            "match_percentage": match_percentage,
            "timestamp": datetime.now().isoformat(),
            "used_embeddings": use_embeddings
        }
        
        # Save updated job data
        save_job_data(job_path, job_data)
        return True, f"Successfully processed job file {job_path.name}"
    except Exception as e:
        return False, f"Error processing {job_path.name}: {str(e)}"


def enhanced_batch_match_all_jobs(
    domain_threshold: float = 0.3, 
    use_llm: bool = True, 
    job_ids: Optional[List[int]] = None, 
    batch_size: int = 10,
    max_workers: int = 4,
    embedding_threshold: float = 0.6,
    use_embeddings: bool = True
) -> None:
    """
    Efficiently match all jobs to your skills with optimized processing and multi-threading
    
    Args:
        domain_threshold: Minimum threshold for considering a match
        use_llm: Whether to use LLM for matching
        job_ids: Optional list of specific job IDs to match
        batch_size: Number of skill pairs to process in a single LLM call
        max_workers: Maximum number of parallel workers for job processing
        embedding_threshold: Minimum threshold for embedding similarity
        use_embeddings: Whether to use embedding-based matching
    """
    your_skills = load_your_skills()
    if not your_skills:
        logger.error("No user skills loaded. Aborting batch match.")
        return
    
    # Filter by job IDs if specified
    if job_ids:
        job_files = []
        for job_id in job_ids:
            job_path = JOB_DATA_DIR / f"job{job_id}.json"
            if job_path.exists():
                job_files.append(job_path)
        logger.info(f"Found {len(job_files)} job files matching the specified IDs.")
    else:
        job_files = sorted(JOB_DATA_DIR.glob("job*.json"))
        logger.info(f"Found {len(job_files)} job files to process for matching.")
    
    start_time = time.time()
    
    # Use ThreadPoolExecutor to parallelize job processing
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for job_path in job_files:
            future = executor.submit(
                process_job_in_thread,
                job_path,
                your_skills,
                domain_threshold,
                use_llm,
                batch_size,
                embedding_threshold,
                use_embeddings
            )
            futures.append((future, job_path))
        
        # Track progress
        success_count = 0
        failure_count = 0
        
        for i, (future, job_path) in enumerate(futures):
            success, message = future.result()
            if success:
                success_count += 1
            else:
                failure_count += 1
                logger.error(message)
            
            # Log progress periodically
            if (i+1) % 10 == 0 or i+1 == len(futures):
                elapsed = time.time() - start_time
                avg_time = elapsed / (i+1)
                remaining = avg_time * (len(futures) - (i+1))
                logger.info(f"Processed {i+1}/{len(futures)} job files " +
                           f"({success_count} succeeded, {failure_count} failed) " +
                           f"in {elapsed:.1f}s " +
                           f"(avg: {avg_time:.1f}s/job, " +
                           f"est. remaining: {remaining:.1f}s)")
    
    # Final stats
    elapsed = time.time() - start_time
    logger.info(f"Enhanced batch skill matching complete. " +
               f"Processed {len(job_files)} job files " +
               f"({success_count} succeeded, {failure_count} failed) " +
               f"in {elapsed:.1f}s " +
               f"(avg: {elapsed/len(job_files) if job_files else 0:.1f}s/job)")


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description="Enhanced skill matching between CV skills and job SDR skills.")
    parser.add_argument('--domain-threshold', type=float, default=0.3, 
                       help='Domain overlap threshold (default: 0.3)')
    parser.add_argument('--no-llm', action='store_true', 
                       help='Disable LLM-based matching (use basic domain overlap)')
    parser.add_argument('--job-ids', type=int, nargs='*', 
                       help='Specific job IDs to match (e.g., --job-ids 1 2 3)')
    parser.add_argument('--batch-size', type=int, default=10, 
                       help='Number of skill pairs to process in a single LLM call (default: 10)')
    parser.add_argument('--max-workers', type=int, default=4, 
                       help='Maximum number of parallel workers (default: 4)')
    parser.add_argument('--embedding-threshold', type=float, default=0.6,
                       help='Minimum threshold for embedding similarity (default: 0.6)')
    parser.add_argument('--no-embeddings', action='store_true',
                       help='Disable embedding-based matching')
    
    args = parser.parse_args()
    
    enhanced_batch_match_all_jobs(
        domain_threshold=args.domain_threshold,
        use_llm=not args.no_llm,
        job_ids=args.job_ids,
        batch_size=args.batch_size,
        max_workers=args.max_workers,
        embedding_threshold=args.embedding_threshold,
        use_embeddings=not args.no_embeddings
    )
