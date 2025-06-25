#!/usr/bin/env python3
"""
Domain Matcher Integration Module

This module provides a unified interface to the domain matching functionality,
integrating both basic and advanced domain matchers. It serves as a bridge between
the older domain matching system and the newer Skill Domain Relationship (SDR) framework.

The module supports:
1. Basic domain lookups for simple skill categorization
2. Advanced domain relationship analysis for sophisticated matching
3. Compatibility layer for different domain matching implementations
4. Configuration options for preferred domain matching approach

This integration simplifies using domain matching throughout the system by providing
a consistent API regardless of which implementation is used underneath.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Set, Union

# Configure logging
logger = logging.getLogger("domain_matcher_integration")

# Add the parent directory to the path to allow imports
parent_dir = str(Path(__file__).resolve().parents[2])
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Try importing the different domain matcher implementations
try:
    # Import basic domain matcher
    from scripts.utils.domain_matcher import (
        get_skill_domain as basic_get_skill_domain,
        get_domain_aware_similarity as basic_get_domain_aware_similarity,
        domain_analyze_matches as basic_domain_analyze_matches,
        rerank_by_domain_relevance as basic_rerank_by_domain_relevance
    )
    
    BASIC_MATCHER_AVAILABLE = True
    logger.info("Basic domain matcher imported successfully")
except ImportError as e:
    BASIC_MATCHER_AVAILABLE = False
    logger.warning(f"Basic domain matcher import failed: {e}")

try:
    # Import advanced domain matcher (SDR framework)
    from scripts.utils.skill_decomposer.domain_overlap_rater import (
        calculate_domain_overlap,
        get_skill_domain_info,
        analyze_job_domain_focus,
        enhance_matches_with_domain_info
    )
    
    from scripts.utils.skill_decomposer.skill_domain_relationship import (
        classify_relationship,
        is_valid_match,
        get_enriched_skill
    )
    
    SDR_AVAILABLE = True
    logger.info("Advanced domain matcher (SDR) imported successfully")
except ImportError as e:
    SDR_AVAILABLE = False
    logger.warning(f"Advanced domain matcher import failed: {e}")

# Configuration
CONFIG_PATH = Path(parent_dir) / "config" / "domain_matcher_config.json"
DEFAULT_CONFIG = {
    "preferred_implementation": "advanced" if SDR_AVAILABLE else "basic",
    "fallback_enabled": True,
    "domain_boost_factor": 0.15,
    "minimum_domain_overlap": 0.3,
    "cache_domains": True
}

# Domain cache for quick lookups
_domain_cache: Dict[str, str] = {}

def _load_config() -> Dict[str, Any]:
    """
    Load domain matcher configuration
    
    Returns:
        Configuration dictionary
    """
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                return config
        else:
            logger.warning(f"Configuration file not found: {CONFIG_PATH}, using defaults")
            return DEFAULT_CONFIG
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return DEFAULT_CONFIG

def _get_implementation_preference() -> str:
    """
    Get the preferred domain matcher implementation based on config and availability
    
    Returns:
        Implementation choice: "advanced", "basic", or "none"
    """
    config = _load_config()
    preferred = config.get("preferred_implementation", "advanced").lower()
    fallback_enabled = config.get("fallback_enabled", True)
    
    if preferred == "advanced" and SDR_AVAILABLE:
        return "advanced"
    elif preferred == "basic" and BASIC_MATCHER_AVAILABLE:
        return "basic"
    elif fallback_enabled:
        if SDR_AVAILABLE:
            return "advanced"
        elif BASIC_MATCHER_AVAILABLE:
            return "basic"
    
    return "none"

def get_skill_domain(skill: str) -> Optional[str]:
    """
    Get the domain for a specific skill using the preferred implementation
    
    Args:
        skill: The skill to find the domain for
        
    Returns:
        Domain name or None if not found
    """
    # Check cache first
    if skill.lower() in _domain_cache:
        return _domain_cache[skill.lower()]
    
    implementation = _get_implementation_preference()
    domain = None
    
    if implementation == "advanced" and SDR_AVAILABLE:
        # Use SDR framework for domain lookup
        domain_info = get_skill_domain_info(skill)
        if domain_info:
            domain = domain_info.get("domain", None)
    
    if (domain is None or implementation == "basic") and BASIC_MATCHER_AVAILABLE:
        # Fall back to basic domain matcher
        domain = basic_get_skill_domain(skill)
    
    # Cache the result
    config = _load_config()
    if config.get("cache_domains", True) and domain:
        _domain_cache[skill.lower()] = domain
    
    return domain

def get_domain_aware_similarity(skill1: str, skill2: str, base_threshold: float = 0.5) -> Tuple[float, bool]:
    """
    Get domain-aware similarity between two skills using the preferred implementation
    
    Args:
        skill1: First skill
        skill2: Second skill
        base_threshold: Base similarity threshold (for basic implementation)
        
    Returns:
        Tuple of (similarity_score, same_domain_flag)
    """
    implementation = _get_implementation_preference()
    
    if implementation == "advanced" and SDR_AVAILABLE:
        # Use SDR framework for domain-aware similarity
        domain_overlap = calculate_domain_overlap(skill1, skill2)
        
        # Get domain info for same-domain check
        domain1 = get_skill_domain(skill1)
        domain2 = get_skill_domain(skill2)
        same_domain = domain1 == domain2 if domain1 and domain2 else False
        
        # Scale domain overlap to similarity score (0-1)
        similarity = domain_overlap
        
        return similarity, same_domain
    
    elif implementation == "basic" and BASIC_MATCHER_AVAILABLE:
        # Use basic domain matcher
        return basic_get_domain_aware_similarity(skill1, skill2, base_threshold)
    
    # Default fallback if no implementation available
    return 0.5, False

def analyze_matches(matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze and enhance match results with domain information
    
    Args:
        matches: List of match dictionaries
        
    Returns:
        Enhanced matches with domain information
    """
    implementation = _get_implementation_preference()
    config = _load_config()
    
    if implementation == "advanced" and SDR_AVAILABLE:
        # Use SDR framework for enhanced matching
        min_overlap = config.get("minimum_domain_overlap", 0.3)
        return enhance_matches_with_domain_info(matches, min_domain_overlap=min_overlap)
    
    elif implementation == "basic" and BASIC_MATCHER_AVAILABLE:
        # Use basic domain matcher
        return basic_domain_analyze_matches(matches)
    
    # No enhancement if no implementation available
    return matches

def rerank_by_domain_relevance(matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rerank matches by domain relevance using the preferred implementation
    
    Args:
        matches: List of match dictionaries
        
    Returns:
        Reranked matches
    """
    implementation = _get_implementation_preference()
    
    if implementation == "advanced" and SDR_AVAILABLE:
        # Analyze with SDR framework first to add domain data
        enhanced_matches = enhance_matches_with_domain_info(matches)
        
        # Sort by domain relevance and match strength
        return sorted(
            enhanced_matches,
            key=lambda m: (
                m.get("domain_data", {}).get("overlap_score", 0),
                m.get("match_strength", 0)
            ),
            reverse=True
        )
    
    elif implementation == "basic" and BASIC_MATCHER_AVAILABLE:
        # Use basic domain matcher
        return basic_rerank_by_domain_relevance(matches)
    
    # No reranking if no implementation available
    return matches

def get_skill_relationship(skill1: str, skill2: str) -> Dict[str, Any]:
    """
    Get the relationship classification between two skills
    
    Args:
        skill1: First skill
        skill2: Second skill
        
    Returns:
        Dictionary with relationship classification information
    """
    if SDR_AVAILABLE:
        # Use SDR framework for relationship classification
        return classify_relationship(skill1, skill2)
    
    # Simplified relationship if SDR not available
    domain1 = get_skill_domain(skill1)
    domain2 = get_skill_domain(skill2)
    
    if domain1 == domain2 and domain1 is not None:
        relationship = "Same_Domain"
    else:
        relationship = "Different_Domain"
    
    return {
        "primary_relationship": relationship,
        "confidence": 0.7,
        "compatibility_percentage": 70 if relationship == "Same_Domain" else 30
    }

def is_domain_match(requirement: str, skill: str, threshold: float = 0.3) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if a skill and requirement are domain-compatible
    
    Args:
        requirement: Job requirement
        skill: Candidate skill
        threshold: Minimum compatibility threshold
        
    Returns:
        Tuple of (is_valid, relationship_data)
    """
    if SDR_AVAILABLE:
        # Use SDR framework for domain matching
        return is_valid_match(requirement, skill, min_compatibility=threshold)
    
    # Simplified check if SDR not available
    domain1 = get_skill_domain(requirement)
    domain2 = get_skill_domain(skill)
    
    # Basic compatibility check
    if domain1 == domain2 and domain1 is not None:
        is_valid = True
        compatibility = 0.8
    else:
        is_valid = False
        compatibility = 0.2
    
    return is_valid, {
        "primary_relationship": "Same_Domain" if is_valid else "Different_Domain",
        "compatibility_percentage": compatibility * 100,
        "confidence": 0.7
    }

def get_available_implementations() -> Dict[str, Union[bool, str]]:
    """
    Get information about available domain matcher implementations
    
    Returns:
        Dictionary with implementation availability
    """
    return {
        "basic": BASIC_MATCHER_AVAILABLE,
        "advanced": SDR_AVAILABLE,
        "preferred": _get_implementation_preference()
    }

def analyze_job_domains(job_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze the domain focus of a job based on its requirements
    
    Args:
        job_requirements: List of job requirement dictionaries
        
    Returns:
        Dictionary with domain analysis results
    """
    if SDR_AVAILABLE:
        # Use SDR framework for job domain analysis
        return analyze_job_domain_focus(job_requirements)
    
    # Simplified domain analysis if SDR not available
    domains = {}
    
    for req in job_requirements:
        req_text = req.get("text", "")
        domain = get_skill_domain(req_text)
        
        if domain:
            if domain not in domains:
                domains[domain] = 0
            domains[domain] += 1
    
    # Calculate domain percentages
    total = sum(domains.values())
    domain_percentages = {d: (count / total) for d, count in domains.items()} if total > 0 else {}
    
    # Identify primary domains (>10%)
    primary_domains = {d: pct for d, pct in domain_percentages.items() if pct >= 0.1}
    
    return {
        "domain_counts": domains,
        "domain_percentages": domain_percentages,
        "primary_domains": primary_domains,
        "domain_diversity": len(domains) / max(1, len(job_requirements))
    }

if __name__ == "__main__":
    # Set up logging for standalone usage
    logging.basicConfig(level=logging.INFO)
    
    # Print implementation availability
    implementations = get_available_implementations()
    print(f"Domain Matcher Implementations:")
    print(f"  Basic: {'Available' if implementations['basic'] else 'Not Available'}")
    print(f"  Advanced (SDR): {'Available' if implementations['advanced'] else 'Not Available'}")
    print(f"  Preferred: {implementations['preferred']}")
    
    # Test domain lookups
    test_skills = [
        "Python Programming",
        "Project Management",
        "Financial Analysis",
        "UX Design",
        "Machine Learning"
    ]
    
    print("\nDomain Lookups:")
    for skill in test_skills:
        domain = get_skill_domain(skill)
        print(f"  {skill}: {domain or 'Unknown'}")
    
    # Test relationship classification
    if SDR_AVAILABLE:
        print("\nRelationship Classifications:")
        test_pairs = [
            ("Python Programming", "JavaScript Development"),
            ("Financial Analysis", "Accounting"),
            ("UX Design", "Frontend Development")
        ]
        
        for skill1, skill2 in test_pairs:
            relationship = get_skill_relationship(skill1, skill2)
            print(f"  {skill1} - {skill2}: {relationship['primary_relationship']} " +
                 f"({relationship['compatibility_percentage']}% compatible)")
            
    print("\nDomain Matcher Integration test completed.")