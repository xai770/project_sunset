#!/usr/bin/env python3
"""
[DEPRECATED] - DO NOT USE - Efficient Skill Matching Module

THIS FILE IS DEPRECATED AND SHOULD NOT BE USED.
A new implementation has replaced this module.
This file is kept only for historical reference.

This module provides optimized approaches for matching job skills to CV skills:
1. Category-based pre-filtering to reduce the comparison space
2. Batched LLM processing to minimize API calls
3. Embedding-based initial filtering for fast approximate matching
4. Caching mechanism to avoid re-computing the same comparisons
5. Progressive matching pipeline that starts with simpler methods
6. Multi-threading for parallel batch processing

This approach is significantly more efficient than the previous implementation,
especially for large numbers of skills and jobs.
"""

import os
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import re
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

import logging
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("efficient_skill_matcher")

# Try to import embedding utilities
try:
    from run_pipeline.skill_matching.embedding_utils import (
        EmbeddingGenerator,
        find_top_matches,
        cosine_similarity
    )
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("Embedding utilities not available. Embedding-based matching will be disabled.")

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

# Skill category mapping
# This helps pre-filter skills before expensive matching operations
SKILL_CATEGORIES = {
    "Technical": [
        "IT_Technical", "Software_Development", "Data_Science", "Engineering", 
        "Programming_Languages", "Cloud_Services", "Databases", "DevOps"
    ],
    "Management": [
        "Leadership_and_Management", "Project_Management", "Team_Leadership", 
        "Business_Management", "Strategic_Planning"
    ],
    "Domain_Knowledge": [
        "Finance", "Banking", "Insurance", "Healthcare", "Manufacturing", 
        "Retail", "Telecom", "Energy", "Legal"
    ],
    "Procurement": [
        "Sourcing_and_Procurement", "Vendor_Management", "Contract_Management", 
        "Supply_Chain", "Purchasing"
    ],
    "Soft_Skills": [
        "Communication", "Teamwork", "Problem_Solving", "Critical_Thinking", 
        "Adaptability", "Time_Management"
    ]
}

# Define compatible categories that should be compared
# This reduces unnecessary comparisons between unrelated categories
COMPATIBLE_CATEGORIES = {
    "Technical": ["Technical", "Management"],
    "Management": ["Management", "Technical", "Domain_Knowledge", "Soft_Skills"],
    "Domain_Knowledge": ["Domain_Knowledge", "Management"],
    "Procurement": ["Procurement", "Management", "Domain_Knowledge"],
    "Soft_Skills": ["Soft_Skills", "Management"]
}

class SkillMatchCache:
    """Cache for skill matching results to avoid redundant computations"""
    
    def __init__(self, cache_file: Path = CACHE_FILE):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.hits = 0
        self.misses = 0
    
    def _load_cache(self) -> Dict[str, float]:
        """Load the cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                logger.info(f"Loaded {len(cache)} skill match entries from cache")
                return cache
        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
        
        return {}
    
    def save_cache(self):
        """Save the cache to disk"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
            logger.info(f"Saved {len(self.cache)} skill match entries to cache")
        except Exception as e:
            logger.warning(f"Error saving cache: {e}")
    
    def get_key(self, skill1: str, skill2: str) -> str:
        """Generate a cache key for two skills"""
        # Sort skills alphabetically to ensure consistent keys regardless of order
        sorted_skills = sorted([skill1, skill2])
        return hashlib.md5(f"{sorted_skills[0]}::{sorted_skills[1]}".encode()).hexdigest()
    
    def get(self, skill1: str, skill2: str) -> Optional[float]:
        """Get a cached match score"""
        key = self.get_key(skill1, skill2)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, skill1: str, skill2: str, score: float):
        """Set a match score in the cache"""
        key = self.get_key(skill1, skill2)
        self.cache[key] = score
        
        # Periodically save the cache to avoid loss
        if len(self.cache) % 100 == 0:
            self.save_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        }


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


def get_skill_category(skill_data: Dict[str, Any]) -> str:
    """Determine the high-level category for a skill"""
    category = skill_data.get("category", "")
    
    # Map the specific category to a high-level category
    for high_level, specific_categories in SKILL_CATEGORIES.items():
        if any(specific in category for specific in specific_categories):
            return high_level
    
    # Default to a catch-all category if no match
    return "General"


def should_compare_skills(job_skill_category: str, cv_skill_category: str) -> bool:
    """Determine if two skills from different categories should be compared"""
    if job_skill_category == cv_skill_category:
        return True
    
    compatible_categories = COMPATIBLE_CATEGORIES.get(job_skill_category, [])
    return cv_skill_category in compatible_categories


def domain_overlap(job_skill: Dict[str, Any], your_skill: Dict[str, Any]) -> float:
    """Calculate domain overlap between two skills using set operations"""
    # Simple domain overlap: intersection over union of domains
    job_domains = set(job_skill.get("domains", []))
    your_domains = set(your_skill.get("domains", []))
    if not job_domains or not your_domains:
        return 0.0
    intersection = job_domains & your_domains
    union = job_domains | your_domains
    return len(intersection) / len(union) if union else 0.0


def batch_llm_domain_overlap(skill_pairs: List[Tuple[str, str]]) -> Dict[str, float]:
    """
    Process multiple skill pairs at once with a single LLM call
    
    Args:
        skill_pairs: List of (skill1, skill2) tuples to compare
        
    Returns:
        Dictionary mapping "skill1::skill2" -> overlap_score
    """
    if not skill_pairs:
        return {}
    
    # Build a prompt that includes all skill pairs
    comparisons = []
    for i, (skill1, skill2) in enumerate(skill_pairs):
        comparisons.append(f"COMPARISON {i+1}:\nSKILL A: {skill1}\nSKILL B: {skill2}")
    
    prompt = f"""Analyze domain overlap between the following skill pairs.
For each pair, consider: domain relatedness, knowledge overlap, context similarity, function similarity.
Respond with a JSON object where keys are the comparison numbers and values are compatibility percentages (0-100).

{chr(10).join(comparisons)}

Format your response EXACTLY as:
{{
  "1": compatibility_percentage,
  "2": compatibility_percentage,
  ...etc
}}
Do not include any other text or explanation."""

    try:
        url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 2048, "num_ctx": 4096}
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            text = data.get("response", "")
            
            # Extract JSON from response
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                try:
                    results = json.loads(json_str)
                    
                    # Convert to the output format
                    output = {}
                    for i, (skill1, skill2) in enumerate(skill_pairs):
                        key = f"{skill1}::{skill2}"
                        score_str = str(i+1)
                        if score_str in results:
                            pct = float(results[score_str])
                            output[key] = min(1.0, max(0.0, pct / 100.0))
                    return output
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON from LLM response: {json_str}")
            else:
                logger.warning("Could not find JSON in LLM response")
        else:
            logger.warning(f"LLM response error: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Batch LLM domain overlap failed: {e}")
    
    # Return empty dict on failure
    return {}


def process_job_skills(job_data: Dict[str, Any], your_skills: Dict[str, Any], 
                       use_llm: bool = True, batch_size: int = 10, 
                       domain_threshold: float = 0.3) -> List[Dict[str, Any]]:
    """
    Process job skills against CV skills using efficient matching strategies
    
    Args:
        job_data: Job data including SDR skills
        your_skills: Your CV skills
        use_llm: Whether to use LLM for matching (more accurate but slower)
        batch_size: Number of skill pairs to process in a single LLM call
        domain_threshold: Minimum threshold for considering a match
        
    Returns:
        List of matched skills with scores
    """
    # Initialize cache
    cache = SkillMatchCache()
    
    # Extract job SDR skills
    job_sdr_skills = job_data.get("sdr_skills", {}).get("enriched", {})
    if not job_sdr_skills:
        logger.warning(f"No SDR skills found in job {job_data.get('job_id', 'unknown')}")
        return []
    
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
    
    # First pass: Use cached results and quick domain overlap for eligible pairs
    for job_category, job_skill_list in job_skills_by_category.items():
        for job_skill_name, job_skill in job_skill_list:
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
    
    # Second pass: Process queued LLM requests in batches
    if use_llm and llm_pairs_to_process:
        logger.info(f"Processing {len(llm_pairs_to_process)} skill pairs with LLM in batches of {batch_size}")
        
        # Process in batches
        for i in range(0, len(llm_pairs_to_process), batch_size):
            batch = llm_pairs_to_process[i:i+batch_size]
            
            # Process batch
            batch_results = batch_llm_domain_overlap(batch)
            
            # Update cache with results
            for j, (job_skill_name, your_skill_name) in enumerate(batch):
                key = f"{job_skill_name}::{your_skill_name}"
                score = batch_results.get(key, 0.0)
                cache.set(job_skill_name, your_skill_name, score)
        
        # Now do a final pass to find best matches using LLM results
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


def batch_match_all_jobs(domain_threshold: float = 0.3, use_llm: bool = True, 
                         job_ids: Optional[List[int]] = None, batch_size: int = 10,
                         max_workers: int = 4) -> None:
    """
    Efficiently match all jobs to your skills with optimized processing
    
    Args:
        domain_threshold: Minimum threshold for considering a match
        use_llm: Whether to use LLM for matching
        job_ids: Optional list of specific job IDs to match
        batch_size: Number of skill pairs to process in a single LLM call
        max_workers: Maximum number of parallel workers for file operations
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
    processed_count = 0
    
    # Process files sequentially (could be parallelized further if needed)
    for i, job_path in enumerate(job_files):
        job_data = load_job_data(job_path)
        if not job_data:
            continue
            
        try:
            # Process job skills with optimized matching
            matches = process_job_skills(
                job_data, your_skills,
                use_llm=use_llm,
                batch_size=batch_size,
                domain_threshold=domain_threshold
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
                "timestamp": datetime.now().isoformat()
            }
            
            # Save updated job data
            save_job_data(job_path, job_data)
            processed_count += 1
            
            # Log progress
            if (i+1) % 10 == 0 or i+1 == len(job_files):
                elapsed = time.time() - start_time
                avg_time = elapsed / (i+1)
                remaining = avg_time * (len(job_files) - (i+1))
                logger.info(f"Processed {i+1}/{len(job_files)} job files " +
                           f"({processed_count} updated) " +
                           f"in {elapsed:.1f}s " +
                           f"(avg: {avg_time:.1f}s/job, " +
                           f"est. remaining: {remaining:.1f}s)")
                
        except Exception as e:
            logger.error(f"Error processing job {job_path.stem}: {e}")
    
    # Final stats
    elapsed = time.time() - start_time
    logger.info(f"Batch skill matching complete. " +
               f"Updated {processed_count}/{len(job_files)} job files " +
               f"in {elapsed:.1f}s (avg: {elapsed/len(job_files) if job_files else 0:.1f}s/job)")


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description="Efficient skill matching between CV skills and job SDR skills.")
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
    
    args = parser.parse_args()
    
    batch_match_all_jobs(
        domain_threshold=args.domain_threshold,
        use_llm=not args.no_llm,
        job_ids=args.job_ids,
        batch_size=args.batch_size,
        max_workers=args.max_workers
    )
