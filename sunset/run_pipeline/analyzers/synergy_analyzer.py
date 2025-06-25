#!/usr/bin/env python3
"""
Synergy Analyzer Module

This module evaluates the synergistic potential of skills and experiences,
identifying complementary skill sets that may create higher value together
than they would individually. It analyzes:

1. Skill combinations that create unique value propositions
2. Cross-functional experience that bridges multiple domains
3. Balanced technical and soft skill portfolios
4. Innovative combinations of disparate skills and experiences

The analysis helps identify "skill synergies" that may not be apparent
from standard skill matching approaches.

Function:
    analyze_synergies(job_id, force_reprocess=False) -> Dict[str, Any]
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple, Optional

# Configure logging
logger = logging.getLogger("synergy_analyzer")

# File paths
DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / "cache" / "synergy"
OUTPUT_DIR = DATA_DIR / "output" / "synergy"
JOB_DATA_DIR = DATA_DIR / "jobs"
PROFILE_DATA_PATH = DATA_DIR / "profile" / "profile.json"
SYNERGY_PATTERNS_PATH = DATA_DIR / "reference" / "skill_synergies.json"

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Skill category mappings
SKILL_CATEGORIES = {
    "technical": [
        "programming", "development", "coding", "software", "engineering", 
        "algorithm", "database", "network", "architecture", "system"
    ],
    "design": [
        "design", "ux", "ui", "user interface", "user experience", "creative",
        "graphic", "visual", "layout", "wireframe"
    ],
    "data": [
        "data", "analytics", "analysis", "visualization", "statistics", 
        "machine learning", "ai", "artificial intelligence", "big data", "mining"
    ],
    "project_management": [
        "project management", "agile", "scrum", "kanban", "sprint", 
        "waterfall", "delivery", "timeline", "milestone", "coordination"
    ],
    "communication": [
        "communication", "writing", "speaking", "presentation", "documentation", 
        "reporting", "collaboration", "teamwork", "interpersonal", "messaging"
    ],
    "business": [
        "business", "strategy", "marketing", "sales", "finance", 
        "operations", "growth", "scaling", "monetization", "revenue"
    ],
    "leadership": [
        "leadership", "management", "executive", "direction", "vision", 
        "strategy", "coaching", "mentoring", "guidance", "decision-making"
    ]
}

def _load_synergy_patterns() -> Dict[str, Any]:
    """
    Load skill synergy patterns from reference file
    
    Returns:
        Dictionary of synergy patterns
    """
    try:
        if SYNERGY_PATTERNS_PATH.exists():
            with open(SYNERGY_PATTERNS_PATH, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Synergy patterns file not found: {SYNERGY_PATTERNS_PATH}")
            # Return a default set of synergy patterns
            return {
                "synergy_combinations": [
                    {
                        "name": "Full-Stack Development",
                        "skills": ["frontend", "backend", "database"],
                        "value_proposition": "End-to-end development capabilities",
                        "synergy_score": 0.9
                    },
                    {
                        "name": "Data Science",
                        "skills": ["statistics", "programming", "domain knowledge"],
                        "value_proposition": "Converting data into actionable insights",
                        "synergy_score": 0.85
                    },
                    {
                        "name": "UX Engineering",
                        "skills": ["ux design", "frontend development", "user research"],
                        "value_proposition": "Seamless design-to-implementation workflow",
                        "synergy_score": 0.8
                    },
                    {
                        "name": "DevOps",
                        "skills": ["development", "operations", "automation"],
                        "value_proposition": "Streamlined software delivery pipeline",
                        "synergy_score": 0.85
                    },
                    {
                        "name": "Product Management",
                        "skills": ["business strategy", "technical knowledge", "project management"],
                        "value_proposition": "Technical product leadership",
                        "synergy_score": 0.8
                    },
                    {
                        "name": "Technical Leadership",
                        "skills": ["technical expertise", "leadership", "communication"],
                        "value_proposition": "Effective technical team leadership",
                        "synergy_score": 0.85
                    },
                    {
                        "name": "Growth Engineering",
                        "skills": ["development", "analytics", "marketing"],
                        "value_proposition": "Technical implementation of growth strategies",
                        "synergy_score": 0.75
                    },
                    {
                        "name": "AI/ML Engineering",
                        "skills": ["machine learning", "software engineering", "data pipeline"],
                        "value_proposition": "End-to-end AI solution development",
                        "synergy_score": 0.9
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error loading synergy patterns: {e}")
        return {"synergy_combinations": []}

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
            return json.load(f)
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
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading profile data: {e}")
        return None

def _categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """
    Categorize skills into different domains
    
    Args:
        skills: List of skills to categorize
        
    Returns:
        Dictionary mapping categories to lists of skills
    """
    categorized = {}
    uncategorized = []
    
    for skill in skills:
        skill_lower = skill.lower()
        categorized_flag = False
        
        for category, keywords in SKILL_CATEGORIES.items():
            for keyword in keywords:
                if keyword in skill_lower:
                    if category not in categorized:
                        categorized[category] = []
                    categorized[category].append(skill)
                    categorized_flag = True
                    break
            if categorized_flag:
                break
                
        if not categorized_flag:
            uncategorized.append(skill)
    
    if uncategorized:
        categorized["other"] = uncategorized
        
    return categorized

def _extract_skills_from_job(job_data: Dict[str, Any]) -> List[str]:
    """
    Extract skills from job data
    
    Args:
        job_data: Job data dictionary
        
    Returns:
        List of skills
    """
    skills = []
    
    # Extract from requirements
    for req in job_data.get("requirements", []):
        # Simple extraction - in a real system this would be more sophisticated
        if len(req.split()) <= 4:  # Simple skills are usually short phrases
            skills.append(req)
    
    # Extract from explicit skills list if available
    if "skills" in job_data:
        skills.extend(job_data["skills"])
    
    return list(set(skills))  # Remove duplicates

def _identify_synergies(skills: List[str], synergy_patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Identify potential synergies among skills
    
    Args:
        skills: List of skills to analyze
        synergy_patterns: Dictionary of synergy patterns
        
    Returns:
        List of identified synergies
    """
    skills_lower = [s.lower() for s in skills]
    identified_synergies = []
    
    for pattern in synergy_patterns.get("synergy_combinations", []):
        pattern_skills = pattern.get("skills", [])
        pattern_skills_lower = [s.lower() for s in pattern_skills]
        
        # Count how many of the pattern skills are present
        matches = 0
        matching_skills = []
        
        for pattern_skill in pattern_skills_lower:
            for skill in skills_lower:
                if pattern_skill in skill or skill in pattern_skill:
                    matches += 1
                    matching_skills.append(skill)
                    break
        
        # Calculate match percentage
        if pattern_skills:
            match_percentage = matches / len(pattern_skills)
            
            # If more than half the skills in the pattern are present, consider it a synergy
            if match_percentage >= 0.5:
                synergy = pattern.copy()
                synergy["match_percentage"] = match_percentage
                synergy["matching_skills"] = matching_skills
                synergy["missing_skills"] = [
                    s for s in pattern_skills 
                    if not any(s.lower() in skill or skill in s.lower() for skill in skills_lower)
                ]
                identified_synergies.append(synergy)
    
    # Sort by match percentage in descending order
    identified_synergies.sort(key=lambda x: x["match_percentage"], reverse=True)
    return identified_synergies

def _calculate_category_balance(categorized_skills: Dict[str, List[str]]) -> float:
    """
    Calculate the balance across skill categories
    
    Args:
        categorized_skills: Dictionary mapping categories to lists of skills
        
    Returns:
        Balance score (0-1)
    """
    if not categorized_skills:
        return 0.0
        
    # Count skills in each category
    category_counts = {category: len(skills) for category, skills in categorized_skills.items()}
    total_skills = sum(category_counts.values())
    
    if total_skills == 0:
        return 0.0
    
    # Calculate what percentage each category represents
    category_percentages = {category: count / total_skills for category, count in category_counts.items()}
    
    # Calculate imbalance factor - how far from an even distribution are we?
    ideal_percentage = 1 / len(category_counts) if category_counts else 0
    imbalance = sum(abs(pct - ideal_percentage) for pct in category_percentages.values()) / 2
    
    # Convert to balance (1 - imbalance)
    balance = 1 - imbalance
    return balance

def analyze_synergies(job_id: str, force_reprocess: bool = False) -> Dict[str, Any]:
    """
    Analyze skill synergies between job and candidate profile
    
    Args:
        job_id: Job ID to process
        force_reprocess: Force reprocessing even if cached results exist
        
    Returns:
        Dictionary with synergy analysis results
    """
    logger.info(f"Starting synergy analysis for job {job_id}")
    
    # Check for cached results
    cache_file = CACHE_DIR / f"{job_id}_synergy.json"
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
    synergy_patterns = _load_synergy_patterns()
    
    if not job_data or not profile_data:
        error_message = f"Missing data: job_data={'present' if job_data else 'missing'}, profile_data={'present' if profile_data else 'missing'}"
        logger.error(error_message)
        return {
            "success": False,
            "error": error_message,
            "score": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    # Extract skills from job
    job_skills = _extract_skills_from_job(job_data)
    
    # Extract skills from candidate profile
    candidate_skills = profile_data.get("skills", [])
    
    # Categorize skills
    job_categorized = _categorize_skills(job_skills)
    candidate_categorized = _categorize_skills(candidate_skills)
    
    # Calculate category balance
    job_balance = _calculate_category_balance(job_categorized)
    candidate_balance = _calculate_category_balance(candidate_categorized)
    
    # Identify job synergies
    job_synergies = _identify_synergies(job_skills, synergy_patterns)
    
    # Identify candidate synergies
    candidate_synergies = _identify_synergies(candidate_skills, synergy_patterns)
    
    # Match candidate synergies against job synergies
    synergy_matches = []
    
    for job_synergy in job_synergies:
        job_synergy_name = job_synergy["name"]
        
        for candidate_synergy in candidate_synergies:
            if candidate_synergy["name"] == job_synergy_name:
                # Calculate synergy alignment
                alignment = (
                    job_synergy["match_percentage"] * 
                    candidate_synergy["match_percentage"]
                )
                
                synergy_matches.append({
                    "name": job_synergy_name,
                    "value_proposition": job_synergy["value_proposition"],
                    "job_match": job_synergy["match_percentage"],
                    "candidate_match": candidate_synergy["match_percentage"],
                    "alignment": alignment,
                    "synergy_score": job_synergy.get("synergy_score", 0.5)
                })
                break
    
    # Calculate synergy alignment score
    if job_synergies:
        # Match the top job synergies with candidate synergies
        top_job_synergies = job_synergies[:3]  # Top 3
        synergy_alignment = 0.0
        
        for job_synergy in top_job_synergies:
            # Find if candidate has this synergy
            matching_candidate_synergy = next(
                (s for s in candidate_synergies if s["name"] == job_synergy["name"]), 
                None
            )
            
            if matching_candidate_synergy:
                synergy_alignment += (
                    job_synergy["match_percentage"] * 
                    matching_candidate_synergy["match_percentage"] *
                    job_synergy.get("synergy_score", 0.5)
                )
            
        # Normalize
        synergy_alignment = synergy_alignment / min(3, len(top_job_synergies)) if top_job_synergies else 0.0
    else:
        synergy_alignment = 0.0
    
    # Calculate balance alignment
    balance_alignment = 1.0 - abs(job_balance - candidate_balance)
    
    # Calculate overlap in skill categories
    job_categories = set(job_categorized.keys())
    candidate_categories = set(candidate_categorized.keys())
    
    common_categories = job_categories.intersection(candidate_categories)
    category_overlap = len(common_categories) / len(job_categories) if job_categories else 0.0
    
    # Calculate overall synergy score
    synergy_score = (
        synergy_alignment * 0.6 +
        balance_alignment * 0.2 +
        category_overlap * 0.2
    )
    
    # Prepare results
    results = {
        "success": True,
        "job_id": job_id,
        "score": synergy_score,
        "job_analysis": {
            "skills": job_skills,
            "categorized_skills": job_categorized,
            "category_balance": job_balance,
            "synergies": job_synergies
        },
        "candidate_analysis": {
            "skills": candidate_skills,
            "categorized_skills": candidate_categorized,
            "category_balance": candidate_balance,
            "synergies": candidate_synergies
        },
        "match_analysis": {
            "synergy_matches": synergy_matches,
            "synergy_alignment": synergy_alignment,
            "balance_alignment": balance_alignment,
            "category_overlap": category_overlap
        },
        "recommendations": []
    }
    
    # Generate recommendations
    if job_synergies and synergy_score < 0.7:
        # Look for the most valuable missing synergies
        missing_synergies = [
            js for js in job_synergies 
            if not any(cs["name"] == js["name"] for cs in candidate_synergies)
        ]
        
        if missing_synergies:
            top_missing = missing_synergies[0]
            results["recommendations"].append({
                "type": "missing_synergy",
                "message": f"Develop the '{top_missing['name']}' skill combination",
                "context": f"Value proposition: {top_missing['value_proposition']}",
                "missing_skills": top_missing.get("missing_skills", [])
            })
        
        # Look for synergies that could be strengthened
        partial_matches = [
            match for match in synergy_matches
            if match["candidate_match"] < 0.8 and match["job_match"] > 0.8
        ]
        
        if partial_matches:
            top_partial = partial_matches[0]
            results["recommendations"].append({
                "type": "strengthen_synergy",
                "message": f"Strengthen your '{top_partial['name']}' skill combination",
                "context": f"Value proposition: {top_partial['value_proposition']}"
            })
    
    # Add timestamp
    results["timestamp"] = datetime.now().isoformat()
    
    # Cache the results
    try:
        with open(cache_file, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to cache results: {e}")
    
    # Save detailed output
    output_file = OUTPUT_DIR / f"{job_id}_synergy_analysis.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save detailed output: {e}")
    
    logger.info(f"Completed synergy analysis for job {job_id} with score {results['score']:.2f}")
    return results

if __name__ == "__main__":
    import argparse
    
    # Set up logging for standalone usage
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"logs/synergy_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        ]
    )
    
    parser = argparse.ArgumentParser(description="Analyze skill synergies between job and candidate profile")
    parser.add_argument("job_id", help="Job ID to process")
    parser.add_argument("--force", action="store_true", help="Force reprocessing even if cached results exist")
    args = parser.parse_args()
    
    results = analyze_synergies(args.job_id, args.force)
    print(json.dumps(results, indent=2))