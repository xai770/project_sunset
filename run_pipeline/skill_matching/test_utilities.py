#!/usr/bin/env python3
"""
Test Utilities for SDR Framework

This module contains utility functions for testing the SDR framework components,
including domain-aware matching tests and evaluation metrics.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Tuple, Optional, Collection, Sequence, MutableSequence

# Make functions accessible from module import
__all__ = ['check_domain_aware_match', 'test_domain_aware_matching', 'calculate_match_metrics']

# Add the project root to the path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import components
from run_pipeline.skill_matching.domain_aware_matcher import DomainAwareMatchingAlgorithm

# Configure logging
logger = logging.getLogger("sdr_test_utilities")

# Constants
OUTPUT_DIR = os.path.join(project_root, 'docs', 'skill_matching')

def check_domain_aware_match(
    matcher: DomainAwareMatchingAlgorithm, 
    job_skill: str, 
    candidate_skill: str
) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if a job skill matches a candidate skill using domain awareness
    
    Args:
        matcher: The DomainAwareMatchingAlgorithm instance
        job_skill: The job skill to check
        candidate_skill: The candidate skill to check
        
    Returns:
        Tuple of (is_match, match_details)
    """
    # Default return for skills we don't have data for
    if job_skill not in matcher.skill_map or candidate_skill not in matcher.skill_map:
        return False, {"reason": "Skill not in enriched skills database"}
    
    # Get the domains for both skills
    job_domain = matcher.skill_map[job_skill]["category"]
    candidate_domain = matcher.skill_map[candidate_skill]["category"]
    
    # Exact match
    if job_skill == candidate_skill:
        return True, {"reason": "Exact skill match"}
    
    # Domain match
    if job_domain == candidate_domain:
        # Check for relationship in the relationship matrix
        if job_skill in matcher.relationships and candidate_skill in matcher.relationships[job_skill]:
            relationship = matcher.relationships[job_skill][candidate_skill]["relationship"]
            return True, {
                "reason": f"Related skill in same domain with relationship: {relationship}",
                "relationship": relationship,
                "domain": job_domain
            }
    
    # Check for knowledge component overlap
    job_components = set(matcher.skill_map[job_skill].get("knowledge_components", []))
    candidate_components = set(matcher.skill_map[candidate_skill].get("knowledge_components", []))
    
    component_overlap = job_components.intersection(candidate_components)
    
    if len(component_overlap) > 0:
        return True, {
            "reason": "Knowledge component overlap",
            "overlapping_components": list(component_overlap)
        }
    
    # No match found
    return False, {"reason": "No matching criteria found"}

def test_domain_aware_matching(
    enriched_skills: List[Dict[str, Any]],
    skill_relationships: Dict[str, Dict[str, Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    Test the domain-aware matching algorithm with sample data
    
    Args:
        enriched_skills: List of enriched skill definitions
        skill_relationships: Dictionary of skill relationships
        
    Returns:
        Dictionary with matching test results
    """
    logger.info("Initializing domain-aware matcher for testing")
    
    # Initialize the domain-aware matching algorithm
    matcher = DomainAwareMatchingAlgorithm()
    
    # We need to load the data manually since we're not using the default paths
    matcher.enriched_skills = enriched_skills
    matcher.relationships = skill_relationships
    
    # Create a skill map for easy lookup
    for skill in enriched_skills:
        matcher.skill_map[skill['name']] = skill
    
    # Generate some sample job requirements and candidate skills for testing
    sample_job_requirements = [
        "Python Programming",
        "Project Management",
        "Data Analysis",
        "Team Leadership",
        "Cloud Computing"
    ]
    
    sample_candidate_skills = [
        "Python",
        "Project Planning",
        "Statistical Analysis",
        "Team Building",
        "AWS"
    ]
    
    logger.info("Testing domain-aware matching with sample data")
    
    # Create test results container
    test_results: Dict[str, Any] = {
        "job_requirements": sample_job_requirements,
        "candidate_skills": sample_candidate_skills,
        "matches": {},
        "false_positives_avoided": [],
        "explanations": {}
    }
    
    # For each job requirement, find potential matches from the candidate skills
    for job_skill in sample_job_requirements:
        matches: List[str] = []
        explanations: Dict[str, Any] = {}
        
        # Use a fallback if the exact skill isn't in our enriched skills 
        job_skill_normalized = job_skill
        if job_skill not in matcher.skill_map:
            # Find the closest match in our skill map
            job_skill_normalized = next((s for s in matcher.skill_map if job_skill.lower() in s.lower()), job_skill)
        
        for candidate_skill in sample_candidate_skills:
            # Use a fallback if the exact skill isn't in our enriched skills
            candidate_skill_normalized = candidate_skill
            if candidate_skill not in matcher.skill_map:
                # Find the closest match
                candidate_skill_normalized = next((s for s in matcher.skill_map if candidate_skill.lower() in s.lower()), candidate_skill)
            
            # Check for a match
            is_match, match_details = check_domain_aware_match(
                matcher, job_skill_normalized, candidate_skill_normalized
            )
            
            if is_match:
                matches.append(candidate_skill)
                explanations[candidate_skill] = match_details
                
        test_results["matches"][job_skill] = matches
        test_results["explanations"][job_skill] = explanations
        
        # Check for false positives avoided (simple keyword matching would match, but domain-aware doesn't)
        for candidate_skill in sample_candidate_skills:
            # Simple keyword check - if job skill is partially in candidate skill or vice versa
            keyword_match = (
                job_skill.lower() in candidate_skill.lower() or
                candidate_skill.lower() in job_skill.lower()
            )
            
            # But domain-aware says no
            if keyword_match and candidate_skill not in matches:
                test_results["false_positives_avoided"].append({
                    "job_skill": job_skill,
                    "candidate_skill": candidate_skill,
                    "reason": "Domain context mismatch"
                })
    
    return test_results

def calculate_match_metrics(
    test_results: Dict[str, Any]
) -> Dict[str, float]:
    """
    Calculate metrics for matching test results
    
    Args:
        test_results: Dictionary with matching test results
        
    Returns:
        Dictionary with matching metrics
    """
    metrics = {}
    
    # Calculate false positive reduction percentage
    total_keyword_matches = 0
    false_positives_avoided = len(test_results.get("false_positives_avoided", []))
    
    for job_skill in test_results.get("job_requirements", []):
        for candidate_skill in test_results.get("candidate_skills", []):
            # Check if there would be a keyword match
            keyword_match = (
                job_skill.lower() in candidate_skill.lower() or
                candidate_skill.lower() in job_skill.lower()
            )
            
            if keyword_match:
                total_keyword_matches += 1
    
    if total_keyword_matches > 0:
        metrics["false_positive_reduction"] = (false_positives_avoided / total_keyword_matches) * 100
    else:
        metrics["false_positive_reduction"] = 0.0
    
    # Calculate average matches per job requirement
    total_matches = sum(len(matches) for matches in test_results.get("matches", {}).values())
    job_count = len(test_results.get("job_requirements", []))
    
    if job_count > 0:
        metrics["average_matches_per_job"] = total_matches / job_count
    else:
        metrics["average_matches_per_job"] = 0.0
    
    return metrics

# Main function for standalone testing
if __name__ == "__main__":
    import argparse
    from datetime import datetime
    
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Run domain-aware matching tests')
    parser.add_argument('--skills', type=str, help='Path to enriched skills JSON file')
    parser.add_argument('--relationships', type=str, help='Path to skill relationships JSON file')
    parser.add_argument('--output', type=str, help='Path to save test results')
    
    args = parser.parse_args()
    
    skills_file = args.skills or os.path.join(OUTPUT_DIR, 'enriched_skills.json')
    relationships_file = args.relationships or os.path.join(OUTPUT_DIR, 'skill_relationships.json')
    
    # Load data
    try:
        with open(skills_file, 'r') as f:
            enriched_skills = json.load(f)
        
        with open(relationships_file, 'r') as f:
            skill_relationships = json.load(f)
        
        # Run tests
        test_results = test_domain_aware_matching(enriched_skills, skill_relationships)
        
        # Calculate metrics
        metrics = calculate_match_metrics(test_results)
        test_results["metrics"] = metrics
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = args.output or os.path.join(OUTPUT_DIR, f'matching_test_results_{timestamp}.json')
        
        with open(output_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        # Print summary
        print("\n===== Domain-Aware Matching Test Results =====")
        print(f"Test completed with {len(test_results['matches'])} job requirements")
        print(f"False positives avoided: {len(test_results['false_positives_avoided'])}")
        print(f"False positive reduction: {metrics['false_positive_reduction']:.2f}%")
        print(f"Average matches per job: {metrics['average_matches_per_job']:.2f}")
        print(f"Results saved to: {output_file}")
        print("=============================================\n")
        
    except Exception as e:
        logger.error(f"Error running matching tests: {e}")
        print(f"Error: {e}")
        sys.exit(1)
