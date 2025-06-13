#!/usr/bin/env python3
"""
Enhanced Domain Skill Matcher Module

This module provides advanced skill matching with domain-aware analysis.
It extends traditional semantic similarity matching by incorporating domain
context to reduce false positives and improve match quality.

Key features:
1. Domain-aware skill similarity calculation
2. Domain relationship analysis for complementary skills
3. Enhanced scoring with domain context weights
4. Support for sub-domain expertise recognition
5. Skill synergy detection within and across domains

The algorithm leverages both the domain matcher integration module
and specialized skill matching techniques to provide more accurate results.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Set, Union, DefaultDict
from collections import defaultdict
from datetime import datetime

# Configure logging
logger = logging.getLogger("enhanced_domain_skill_matcher")

# Add the parent directory to the path to allow imports
parent_dir = str(Path(__file__).resolve().parents[2])
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import domain matcher integration
from run_pipeline.skill_matching.domain_matcher_integration import (
    get_skill_domain,
    get_domain_aware_similarity,
    analyze_matches,
    get_skill_relationship,
    is_domain_match,
    analyze_job_domains
)

# Configuration paths
CONFIG_DIR = Path(parent_dir) / "config"
ENHANCED_MATCHER_CONFIG_PATH = CONFIG_DIR / "enhanced_matcher_config.json"
SKILL_DATA_DIR = Path(parent_dir) / "data" / "skill_enrichment_feedback"
SKILL_DATA_DIR.mkdir(exist_ok=True, parents=True)

# Cache file paths
SIMILARITY_CACHE_PATH = Path(parent_dir) / "data" / "semantic_similarity_cache.json"
DOMAIN_SKILL_CACHE_PATH = Path(parent_dir) / "data" / "skill_match_cache" / "domain_skill_matches.json"

# Cache dictionaries
similarity_cache: Dict[str, Dict[str, float]] = {}
domain_skill_matches_cache: Dict[str, Dict[str, Any]] = {}

# Default configuration
DEFAULT_CONFIG = {
    "domain_weight": 0.35,
    "semantic_weight": 0.65,
    "minimum_match_threshold": 0.6,
    "exact_match_bonus": 0.15,
    "same_domain_bonus": 0.1,
    "cross_domain_penalty": 0.1,
    "synergy_bonus": 0.05,
    "use_cached_similarity": True,
    "cache_match_results": True
}

def load_config() -> Dict[str, Any]:
    """
    Load the enhanced matcher configuration
    
    Returns:
        Configuration dictionary with matching parameters
    """
    try:
        if ENHANCED_MATCHER_CONFIG_PATH.exists():
            with open(ENHANCED_MATCHER_CONFIG_PATH, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {ENHANCED_MATCHER_CONFIG_PATH}")
                return config
        else:
            logger.warning(f"Configuration file not found: {ENHANCED_MATCHER_CONFIG_PATH}, using defaults")
            return DEFAULT_CONFIG
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return DEFAULT_CONFIG

def _load_similarity_cache() -> Dict[str, Dict[str, float]]:
    """
    Load the semantic similarity cache
    
    Returns:
        Similarity cache dictionary
    """
    global similarity_cache
    
    if similarity_cache:
        return similarity_cache
    
    try:
        if SIMILARITY_CACHE_PATH.exists():
            with open(SIMILARITY_CACHE_PATH, 'r') as f:
                similarity_cache = json.load(f)
                logger.info(f"Loaded similarity cache with {len(similarity_cache)} entries")
                return similarity_cache
        else:
            logger.info(f"Similarity cache not found: {SIMILARITY_CACHE_PATH}, starting empty")
            similarity_cache = {}
            return similarity_cache
    except Exception as e:
        logger.error(f"Error loading similarity cache: {e}")
        similarity_cache = {}
        return similarity_cache

def _save_similarity_cache() -> None:
    """
    Save the semantic similarity cache to disk
    """
    try:
        SIMILARITY_CACHE_PATH.parent.mkdir(exist_ok=True, parents=True)
        with open(SIMILARITY_CACHE_PATH, 'w') as f:
            json.dump(similarity_cache, f, indent=2)
            logger.info(f"Saved similarity cache with {len(similarity_cache)} entries")
    except Exception as e:
        logger.error(f"Error saving similarity cache: {e}")

def _load_domain_skill_matches_cache() -> Dict[str, Dict[str, Any]]:
    """
    Load the domain skill matches cache
    
    Returns:
        Domain skill matches cache dictionary
    """
    global domain_skill_matches_cache
    
    if domain_skill_matches_cache:
        return domain_skill_matches_cache
    
    try:
        if DOMAIN_SKILL_CACHE_PATH.exists():
            with open(DOMAIN_SKILL_CACHE_PATH, 'r') as f:
                domain_skill_matches_cache = json.load(f)
                logger.info(f"Loaded domain skill matches cache with {len(domain_skill_matches_cache)} entries")
                return domain_skill_matches_cache
        else:
            logger.info(f"Domain skill matches cache not found: {DOMAIN_SKILL_CACHE_PATH}, starting empty")
            domain_skill_matches_cache = {}
            return domain_skill_matches_cache
    except Exception as e:
        logger.error(f"Error loading domain skill matches cache: {e}")
        domain_skill_matches_cache = {}
        return domain_skill_matches_cache

def _save_domain_skill_matches_cache() -> None:
    """
    Save the domain skill matches cache to disk
    """
    try:
        DOMAIN_SKILL_CACHE_PATH.parent.mkdir(exist_ok=True, parents=True)
        with open(DOMAIN_SKILL_CACHE_PATH, 'w') as f:
            json.dump(domain_skill_matches_cache, f, indent=2)
            logger.info(f"Saved domain skill matches cache with {len(domain_skill_matches_cache)} entries")
    except Exception as e:
        logger.error(f"Error saving domain skill matches cache: {e}")

def get_semantic_similarity(skill1: str, skill2: str) -> float:
    """
    Calculate semantic similarity between skills with caching
    
    Args:
        skill1: First skill
        skill2: Second skill
        
    Returns:
        Similarity score (0-1)
    """
    config = load_config()
    
    # Create cache key (order-independent)
    cache_key = tuple(sorted([skill1.lower(), skill2.lower()]))
    skill1_lower, skill2_lower = cache_key
    
    # Check if using cached similarity is enabled
    if config["use_cached_similarity"]:
        # Load cache if not loaded
        similarity_cache = _load_similarity_cache()
        
        # Check cache (both directions)
        if skill1_lower in similarity_cache and skill2_lower in similarity_cache[skill1_lower]:
            return similarity_cache[skill1_lower][skill2_lower]
        
        if skill2_lower in similarity_cache and skill1_lower in similarity_cache[skill2_lower]:
            return similarity_cache[skill2_lower][skill1_lower]
    
    # If the skills are identical, return perfect similarity
    if skill1_lower == skill2_lower:
        return 1.0
        
    # Calculate similarity using domain-aware similarity
    similarity, _ = get_domain_aware_similarity(skill1, skill2)
    
    # Cache the result if caching is enabled
    if config["use_cached_similarity"]:
        if skill1_lower not in similarity_cache:
            similarity_cache[skill1_lower] = {}
        
        similarity_cache[skill1_lower][skill2_lower] = similarity
        
        # Save cache periodically (based on size changes)
        if len(similarity_cache) % 50 == 0:
            _save_similarity_cache()
    
    return similarity

def get_enhanced_domain_match(
    job_skill: str, 
    candidate_skill: str,
    job_domain_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get enhanced domain match information between a job skill and candidate skill
    
    Args:
        job_skill: Skill required by the job
        candidate_skill: Skill possessed by the candidate
        job_domain_context: Optional job domain analysis for context
        
    Returns:
        Dictionary with match information and scores
    """
    config = load_config()
    
    # Check cache if enabled
    if config["cache_match_results"]:
        cache = _load_domain_skill_matches_cache()
        cache_key = f"{job_skill.lower()}:{candidate_skill.lower()}"
        
        if cache_key in cache:
            return cache[cache_key]
    
    # Get semantic similarity
    semantic_similarity = get_semantic_similarity(job_skill, candidate_skill)
    
    # Get domain information
    job_skill_domain = get_skill_domain(job_skill)
    candidate_skill_domain = get_skill_domain(candidate_skill)
    
    # Get relationship information
    relationship_data = get_skill_relationship(job_skill, candidate_skill)
    
    # Check domain match
    is_valid, domain_match_data = is_domain_match(
        job_skill, 
        candidate_skill, 
        threshold=config["minimum_match_threshold"]
    )
    
    # Calculate match score with domain weights
    semantic_weight = config["semantic_weight"]
    domain_weight = config["domain_weight"]
    
    # Base score from semantic similarity
    base_score = semantic_similarity * semantic_weight
    
    # Domain component
    domain_score = 0.0
    
    # Exact match bonus
    if job_skill.lower() == candidate_skill.lower():
        domain_score += config["exact_match_bonus"]
    
    # Domain similarity factors
    if job_skill_domain and candidate_skill_domain:
        if job_skill_domain == candidate_skill_domain:
            domain_score += config["same_domain_bonus"]
        else:
            domain_score -= config["cross_domain_penalty"]
    
    # Synergy bonus from relationship data
    if relationship_data.get("primary_relationship") in ["Complementary", "Foundational", "Advanced"]:
        domain_score += config["synergy_bonus"]
    
    # Weight the domain score
    domain_score = max(0, min(1, domain_score)) * domain_weight
    
    # Final score
    final_score = base_score + domain_score
    
    # Cap score between 0 and 1
    final_score = max(0, min(1, final_score))
    
    # Prepare result
    result = {
        "job_skill": job_skill,
        "candidate_skill": candidate_skill,
        "match_score": final_score,
        "semantic_similarity": semantic_similarity,
        "domain_match": is_valid,
        "relationship": relationship_data.get("primary_relationship"),
        "domains": {
            "job_skill_domain": job_skill_domain,
            "candidate_skill_domain": candidate_skill_domain,
            "same_domain": job_skill_domain == candidate_skill_domain if job_skill_domain and candidate_skill_domain else False
        },
        "match_quality": "High" if final_score >= 0.8 else "Medium" if final_score >= 0.6 else "Low"
    }
    
    # Cache result if enabled
    if config["cache_match_results"]:
        cache_key = f"{job_skill.lower()}:{candidate_skill.lower()}"
        domain_skill_matches_cache[cache_key] = result
        
        # Save cache periodically (based on size changes)
        if len(domain_skill_matches_cache) % 50 == 0:
            _save_domain_skill_matches_cache()
    
    return result

def match_skills_with_domain_context(
    job_skills: List[str],
    candidate_skills: List[str]
) -> Dict[str, Any]:
    """
    Match job skills with candidate skills using domain-aware matching
    
    Args:
        job_skills: List of skills required by the job
        candidate_skills: List of skills possessed by the candidate
        
    Returns:
        Dictionary with match results
    """
    config = load_config()
    
    # Analyze job domains for context
    job_skill_dict = [{"text": skill} for skill in job_skills]
    job_domain_analysis = analyze_job_domains(job_skill_dict)
    
    # Track matches for each job skill
    matches: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    # For each job skill, find candidate skills that match
    for job_skill in job_skills:
        for candidate_skill in candidate_skills:
            match_result = get_enhanced_domain_match(
                job_skill,
                candidate_skill,
                job_domain_analysis
            )
            
            # Add to matches if above threshold
            if match_result["match_score"] >= config["minimum_match_threshold"]:
                matches[job_skill].append(match_result)
    
    # Sort matches by score
    for job_skill, skill_matches in matches.items():
        matches[job_skill] = sorted(
            skill_matches,
            key=lambda m: m["match_score"],
            reverse=True
        )
    
    # Calculate overall match statistics
    matched_job_skills = [job_skill for job_skill in job_skills if job_skill in matches]
    match_coverage = len(matched_job_skills) / len(job_skills) if job_skills else 0
    
    # Compute average match score
    all_matches = [match for matches_list in matches.values() for match in matches_list]
    avg_match_score = sum(match["match_score"] for match in all_matches) / len(all_matches) if all_matches else 0
    
    # Prepare result
    result = {
        "matches": dict(matches),
        "matched_job_skills_count": len(matched_job_skills),
        "total_job_skills_count": len(job_skills),
        "match_coverage_percent": match_coverage * 100,
        "average_match_score": avg_match_score,
        "job_domain_analysis": job_domain_analysis,
        "match_quality_summary": {
            "high_quality_matches": sum(1 for match in all_matches if match["match_score"] >= 0.8),
            "medium_quality_matches": sum(1 for match in all_matches if 0.6 <= match["match_score"] < 0.8),
            "low_quality_matches": sum(1 for match in all_matches if match["match_score"] < 0.6)
        }
    }
    
    return result

def process_job_match(
    job_id: str,
    job_skills: Optional[List[str]] = None,
    candidate_skills: Optional[List[str]] = None,
    force_reprocess: bool = False
) -> Dict[str, Any]:
    """
    Process a job match with domain-enhanced matching
    
    Args:
        job_id: Job identifier
        job_skills: List of job skills (optional, will load if not provided)
        candidate_skills: List of candidate skills (optional, will load if not provided)
        force_reprocess: Force reprocessing even if cached results exist
        
    Returns:
        Dictionary with match results
    """
    logger.info(f"Processing job match with domain enhancement for job {job_id}")
    
    # Define output file paths
    # Support both job<ID>.json and <ID>.json naming
    job_file_path = None
    postings_dir = Path(parent_dir) / "data" / "postings"
    job_file_candidates = [postings_dir / f"{job_id}.json", postings_dir / f"job{job_id}.json"]
    for candidate in job_file_candidates:
        if candidate.exists():
            job_file_path = candidate
            break
    if job_file_path is None:
        logger.error(f"Job file not found for job_id {job_id} (tried: {[str(c) for c in job_file_candidates]})")
        return {"success": False, "error": "Job file not found"}
    
    # Check if already processed in job file and reprocessing not forced
    if not force_reprocess:
        try:
            with open(job_file_path, 'r') as f:
                job_data = json.load(f)
                if job_data.get("domain_enhanced_match"):
                    logger.info(f"Job {job_id} already has domain-enhanced match results")
                    return {
                        "success": True, 
                        "job_id": job_id,
                        "match_results": job_data.get("domain_enhanced_match"),
                        "from_cache": True
                    }
        except Exception as e:
            logger.warning(f"Error checking job file for existing results: {e}")
    
    # Load job skills if not provided
    if job_skills is None:
        try:
            with open(job_file_path, 'r') as f:
                job_data = json.load(f)
                job_skills = [skill["text"] for skill in job_data.get("skills", [])]
                logger.info(f"Loaded {len(job_skills)} job skills for job {job_id}")
                
                if not job_skills:
                    logger.error(f"No skills found in job {job_id}")
                    return {"success": False, "error": "No skills found in job"}
        except Exception as e:
            logger.error(f"Error loading job skills: {e}")
            return {"success": False, "error": f"Error loading job skills: {e}"}
    
    # Load candidate skills if not provided
    if candidate_skills is None:
        candidate_skills_path = Path(parent_dir) / "data" / "cv_skills.json"
        try:
            if candidate_skills_path.exists():
                with open(candidate_skills_path, 'r') as f:
                    candidate_data = json.load(f)
                    # Support both old and new formats
                    candidate_skills = []
                    if "skills" in candidate_data:
                        candidate_skills = [skill["text"] if isinstance(skill, dict) and "text" in skill else skill for skill in candidate_data["skills"]]
                    elif "cv_skills" in candidate_data:
                        # Flatten experience_skills and core_competencies
                        exp = candidate_data["cv_skills"].get("experience_skills", [])
                        comp = candidate_data["cv_skills"].get("core_competencies", {})
                        candidate_skills = list(exp)
                        for v in comp.values():
                            candidate_skills.extend(v)
                    logger.info(f"Loaded {len(candidate_skills)} candidate skills")
            else:
                logger.error(f"Candidate skills file not found: {candidate_skills_path}")
                return {"success": False, "error": "Candidate skills not found"}
        except Exception as e:
            logger.error(f"Error loading candidate skills: {e}")
            return {"success": False, "error": f"Error loading candidate skills: {e}"}
    
    # Perform domain-enhanced matching
    try:
        match_results = match_skills_with_domain_context(job_skills, candidate_skills)
        
        # Add metadata
        results = {
            "success": True,
            "job_id": job_id,
            "job_skills_count": len(job_skills),
            "candidate_skills_count": len(candidate_skills),
            "timestamp": datetime.now().isoformat(),
            "match_results": match_results
        }
        
        # Update the job file with the results
        try:
            with open(job_file_path, 'r') as f:
                job_data = json.load(f)
            
            # Add domain enhanced match results
            job_data["domain_enhanced_match"] = match_results
            
            # Write updated job data
            with open(job_file_path, 'w') as f:
                json.dump(job_data, f, indent=2)
                logger.info(f"Updated job file with domain-enhanced match results: {job_file_path}")
        
        except Exception as e:
            logger.error(f"Error updating job file with results: {e}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error in domain-enhanced matching: {e}")
        return {
            "success": False,
            "job_id": job_id,
            "error": f"Error in domain-enhanced matching: {e}"
        }

if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(description="Domain-Enhanced Skill Matcher")
    parser.add_argument("job_id", help="Job ID to process")
    parser.add_argument("--force", action="store_true", help="Force reprocessing even if results exist")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(Path(parent_dir) / "logs" / "domain_enhanced_matcher.log"),
            logging.StreamHandler()
        ]
    )
    
    # Process the job
    results = process_job_match(args.job_id, force_reprocess=args.force)
    
    # Print summary
    if results["success"]:
        match_results = results["match_results"]
        print(f"\nDomain-Enhanced Match Summary for job {args.job_id}:")
        print(f"  Job Skills: {results['job_skills_count']}")
        print(f"  Candidate Skills: {results['candidate_skills_count']}")
        print(f"  Matched Job Skills: {match_results['matched_job_skills_count']} " +
              f"({match_results['match_coverage_percent']:.1f}%)")
        print(f"  Average Match Score: {match_results['average_match_score']:.2f}")
        print("\nMatch Quality Summary:")
        print(f"  High Quality Matches: {match_results['match_quality_summary']['high_quality_matches']}")
        print(f"  Medium Quality Matches: {match_results['match_quality_summary']['medium_quality_matches']}")
        print(f"  Low Quality Matches: {match_results['match_quality_summary']['low_quality_matches']}")
    else:
        print(f"\nError: {results.get('error', 'Unknown error')}")