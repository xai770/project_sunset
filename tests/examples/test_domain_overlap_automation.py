#!/usr/bin/env python3
"""
Test script for domain overlap rater with focus on automation skills

This script tests how the domain overlap rater handles different types of automation skills,
which was the primary motivation for redesigning the domain overlap rater.
"""

import sys
import os
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
import pandas as pd

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scripts.utils.skill_decomposer.domain_overlap_rater import (
    calculate_domain_overlap,
    get_skill_domain_info,
    enhance_matches_with_domain_info
)

def print_header(text: str) -> None:
    """Print a section header for better readability"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def test_automation_domains() -> None:
    """Test domain info extraction for different automation skills"""
    print_header("Testing domain info extraction for automation skills")
    
    automation_skills = [
        "Business Process Automation",
        "CI/CD Deployment Automation", 
        "Test Automation Framework Development",
        "Industrial Automation",
        "Marketing Automation",
        "Automation" # Generic skill
    ]
    
    for skill in automation_skills:
        print(f"\nSkill: {skill}")
        info = get_skill_domain_info(skill)
        print(f"  Domain: {info.get('domain', 'N/A')}")
        print(f"  Category: {info.get('category', 'N/A')}")
        print(f"  Knowledge Components: {', '.join(info.get('subcategories', ['N/A']))[:80]}")
        print(f"  Related Domains: {', '.join(info.get('related_domains', ['N/A']))}")
        print(f"  Source: {info.get('source', 'N/A')}")

def test_automation_overlaps() -> None:
    """Test domain overlap calculation between automation skills"""
    print_header("Testing domain overlap between automation skills")
    
    # Define skill pairs to test
    skill_pairs = [
        ("Business Process Automation", "CI/CD Deployment Automation"),
        ("Test Automation Framework Development", "CI/CD Deployment Automation"),
        ("Industrial Automation", "Marketing Automation"),
        ("Business Process Automation", "Industrial Automation"),
        ("Test Automation Framework Development", "Marketing Automation"),
        ("Automation", "CI/CD Deployment Automation"),
        ("Automation", "Business Process Automation"),
        ("Automation", "Test Automation Framework Development"),
        ("Automation", "Industrial Automation"),
        ("Automation", "Marketing Automation")
    ]
    
    results = []
    
    for skill1, skill2 in skill_pairs:
        overlap = calculate_domain_overlap(skill1, skill2)
        results.append({
            "Skill 1": skill1,
            "Skill 2": skill2,
            "Domain Overlap": overlap,
            "Is Compatible": "Yes" if overlap >= 0.3 else "No"
        })
        print(f"{skill1} + {skill2}: {overlap:.2f} (Compatible: {'Yes' if overlap >= 0.3 else 'No'})")
    
    # Convert to DataFrame for better visualization
    df = pd.DataFrame(results)
    print("\nOverlap Results Summary:")
    print(df)
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "reports", f"automation_domain_analysis_{timestamp}.json"
    )
    
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_path}")

def test_match_enhancement() -> None:
    """Test how domain analysis enhances match scores"""
    print_header("Testing match enhancement with domain analysis")
    
    # Create some sample matches
    sample_matches = [
        {
            "skill": "Automation",
            "requirement": "CI/CD Deployment Automation",
            "match_strength": 0.9  # High semantic similarity but different domains
        },
        {
            "skill": "CI/CD Deployment Automation",
            "requirement": "CI/CD Deployment Automation",
            "match_strength": 0.9  # Same domain
        },
        {
            "skill": "Business Process Automation",
            "requirement": "Process Automation",
            "match_strength": 0.8  # Similar domains
        },
        {
            "skill": "Test Automation Framework Development",
            "requirement": "Automation Testing",
            "match_strength": 0.85  # Similar domains
        },
        {
            "skill": "Industrial Automation",
            "requirement": "Marketing Automation",
            "match_strength": 0.6  # Different domains but both automation
        }
    ]
    
    # Enhance matches with domain analysis
    enhanced_matches = enhance_matches_with_domain_info(sample_matches)
    
    # Print results
    for i, match in enumerate(enhanced_matches):
        original = sample_matches[i]["match_strength"]
        new = match["match_strength"]
        domain_data = match.get("domain_data", {})
        domain_overlap = domain_data.get("domain_overlap", 0)
        
        print(f"\nMatch {i+1}: {match['skill']} + {match['requirement']}")
        print(f"  Original Score: {original:.2f}")
        print(f"  Final Score: {new:.2f}")
        print(f"  Domain Overlap: {domain_overlap:.2f}")
        
        if domain_data.get("penalty_applied", False):
            print(f"  Penalty Applied: {domain_data.get('penalty_factor', 0):.2f}")
        if domain_data.get("boost_applied", False):
            print(f"  Boost Applied: {domain_data.get('boost_factor', 0):.2f}")
            
        print(f"  Match Type: {match.get('match_type', 'N/A')}")

if __name__ == "__main__":
    test_automation_domains()
    test_automation_overlaps()
    test_match_enhancement()