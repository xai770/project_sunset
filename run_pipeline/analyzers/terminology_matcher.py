#!/usr/bin/env python3
"""
Terminology Matcher Module

This module analyzes job descriptions and candidate profiles to identify and match
industry-specific terminology and jargon. It helps identify domain-specific language
alignment between job requirements and candidate skills.

The module uses NLP techniques to:
1. Extract domain-specific terms from job descriptions
2. Match these terms against candidate profiles and skill descriptions
3. Calculate a terminology alignment score
4. Provide insights into terminology gaps

Function:
    match_terminology(job_id, force_reprocess=False) -> Dict[str, Any]
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple, Optional

# Configure logging
logger = logging.getLogger("terminology_matcher")

# File paths
DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / "cache" / "terminology"
OUTPUT_DIR = DATA_DIR / "output" / "terminology"
JOB_DATA_DIR = DATA_DIR / "jobs"
PROFILE_DATA_PATH = DATA_DIR / "profile" / "profile.json"
DOMAIN_TERMS_PATH = DATA_DIR / "reference" / "domain_terminology.json"

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _load_domain_terminology() -> Dict[str, List[str]]:
    """
    Load domain-specific terminology from reference file
    
    Returns:
        Dictionary mapping domain names to lists of domain-specific terms
    """
    try:
        if DOMAIN_TERMS_PATH.exists():
            with open(DOMAIN_TERMS_PATH, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Domain terminology file not found: {DOMAIN_TERMS_PATH}")
            # Return a minimal set of domains with basic terms
            return {
                "software_development": ["algorithm", "API", "framework", "repository", "backend", "frontend"],
                "finance": ["accounting", "audit", "compliance", "risk assessment", "financial analysis"],
                "healthcare": ["clinical", "patient care", "medical records", "HIPAA", "diagnosis"],
                "marketing": ["campaign", "analytics", "SEO", "content strategy", "conversion"],
                "project_management": ["agile", "scrum", "sprint", "milestone", "deliverable", "roadmap"]
            }
    except Exception as e:
        logger.error(f"Error loading domain terminology: {e}")
        return {}

def _extract_terms_from_text(text: str, term_list: List[str]) -> Set[str]:
    """
    Extract domain-specific terms from text
    
    Args:
        text: Text to extract terms from
        term_list: List of terms to search for
        
    Returns:
        Set of found terms
    """
    text = text.lower()
    found_terms = set()
    
    for term in term_list:
        if term.lower() in text:
            found_terms.add(term)
            
    return found_terms

def _detect_domain(job_data: Dict[str, Any]) -> List[Tuple[str, float]]:
    """
    Detect the likely domains for a job description
    
    Args:
        job_data: Job data dictionary
        
    Returns:
        List of (domain, confidence) tuples, ordered by confidence
    """
    domain_terminology = _load_domain_terminology()
    job_text = ' '.join([
        job_data.get('title', ''),
        job_data.get('description', ''),
        ' '.join(job_data.get('requirements', [])),
        ' '.join(job_data.get('responsibilities', []))
    ]).lower()
    
    domain_matches = []
    
    for domain, terms in domain_terminology.items():
        matched_terms = _extract_terms_from_text(job_text, terms)
        if terms:
            confidence = len(matched_terms) / len(terms)
            domain_matches.append((domain, confidence, matched_terms))
    
    # Sort by confidence score in descending order
    domain_matches.sort(key=lambda x: x[1], reverse=True)
    
    return [(domain, confidence) for domain, confidence, _ in domain_matches if confidence > 0.1]

def _load_job_data(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Load job data from file
    
    Args:
        job_id: Job ID to load
        
    Returns:
        Job data dictionary or None if not found
    """
    job_file = JOB_DATA_DIR / f"{job_id}.json"
    if not job_file.exists():
        logger.error(f"Job file not found: {job_file}")
        return None
        
    try:
        with open(job_file, 'r') as f:
            return json.load(f)  # type: ignore
    except Exception as e:
        logger.error(f"Error loading job data: {e}")
        return None

def _load_profile_data() -> Optional[Dict[str, Any]]:
    """
    Load candidate profile data
    
    Returns:
        Profile data dictionary or None if not found
    """
    if not PROFILE_DATA_PATH.exists():
        logger.error(f"Profile data not found: {PROFILE_DATA_PATH}")
        return None
        
    try:
        with open(PROFILE_DATA_PATH, 'r') as f:
            return json.load(f)  # type: ignore
    except Exception as e:
        logger.error(f"Error loading profile data: {e}")
        return None

def match_terminology(job_id: str, force_reprocess: bool = False) -> Dict[str, Any]:
    """
    Match job terminology against candidate profile
    
    Args:
        job_id: Job ID to process
        force_reprocess: Force reprocessing even if cached results exist
        
    Returns:
        Dictionary with terminology matching results
    """
    logger.info(f"Starting terminology matching for job {job_id}")
    
    # Check for cached results
    cache_file = CACHE_DIR / f"{job_id}_terminology.json"
    if cache_file.exists() and not force_reprocess:
        try:
            with open(cache_file, 'r') as f:
                cached_results = json.load(f)
                logger.info(f"Using cached results for job {job_id}")
                return cached_results
        except Exception as e:
            logger.warning(f"Could not read cache file, reprocessing: {e}")
    
    # Load job and profile data
    job_data = _load_job_data(job_id)
    profile_data = _load_profile_data()
    
    if not job_data or not profile_data:
        error_message = f"Missing data: job_data={'present' if job_data else 'missing'}, profile_data={'present' if profile_data else 'missing'}"
        logger.error(error_message)
        return {
            "success": False,
            "error": error_message,
            "score": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    # Detect domains for the job
    job_domains = _detect_domain(job_data)
    
    # Load domain-specific terminology
    domain_terminology = _load_domain_terminology()
    
    # For each likely domain, look for domain-specific terminology
    job_terms = set()
    for domain, confidence in job_domains:
        if domain in domain_terminology:
            terms = domain_terminology[domain]
            job_description = job_data.get('description', '')
            requirements = ' '.join(job_data.get('requirements', []))
            job_text = f"{job_data.get('title', '')} {job_description} {requirements}"
            
            found_terms = _extract_terms_from_text(job_text, terms)
            job_terms.update(found_terms)
    
    # Look for the same terms in the candidate profile
    profile_text = f"{profile_data.get('summary', '')} {' '.join(profile_data.get('skills', []))}"
    profile_experience = profile_data.get('experience', [])
    for exp in profile_experience:
        profile_text += f" {exp.get('title', '')} {exp.get('description', '')}"
    
    profile_terms = _extract_terms_from_text(profile_text, list(job_terms))
    
    # Calculate terminology match score
    terminology_score = len(profile_terms) / max(len(job_terms), 1) if job_terms else 0.0
    
    # Prepare detailed results
    results: Dict[str, Any] = {
        "success": True,
        "job_id": job_id,
        "score": min(1.0, terminology_score),  # Cap at 1.0
        "domains": [{"name": domain, "confidence": confidence} for domain, confidence in job_domains],
        "job_terminology": list(job_terms),
        "matching_terminology": list(profile_terms),
        "missing_terminology": list(job_terms - profile_terms),
        "terminology_match_rate": terminology_score,
        "recommendations": []
    }
    
    # Generate recommendations for improvement
    if job_terms - profile_terms:
        results["recommendations"].append({
            "type": "terminology_gap",
            "message": "Consider incorporating these industry terms in your profile",
            "terms": list(job_terms - profile_terms)[:5]  # Show top 5 missing terms
        })
    
    # Add the timestamp
    results["timestamp"] = datetime.now().isoformat()
    
    # Cache the results
    try:
        with open(cache_file, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to cache results: {e}")
    
    # Save detailed output
    output_file = OUTPUT_DIR / f"{job_id}_terminology_analysis.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save detailed output: {e}")
    
    logger.info(f"Completed terminology matching for job {job_id} with score {results['score']:.2f}")
    return results

if __name__ == "__main__":
    import sys
    import argparse
    
    # Set up logging for standalone usage
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"logs/terminology_matcher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        ]
    )
    
    parser = argparse.ArgumentParser(description="Match job terminology against candidate profile")
    parser.add_argument("job_id", help="Job ID to process")
    parser.add_argument("--force", action="store_true", help="Force reprocessing even if cached results exist")
    args = parser.parse_args()
    
    results = match_terminology(args.job_id, args.force)
    print(json.dumps(results, indent=2))