#!/usr/bin/env python3
"""
Management Skills Differentiator Module

This module analyzes management and leadership requirements in job descriptions
and evaluates how well a candidate's profile demonstrates these skills. It focuses on:

1. Leadership competencies (team leading, decision making, strategic thinking)
2. People management skills (mentoring, performance management, team building)
3. Process management (workflow optimization, resource allocation)
4. Management style and approach

The module helps identify leadership gaps and provides targeted recommendations
for better positioning in management-focused roles.

Function:
    differentiate_management_skills(job_id, force_reprocess=False) -> Dict[str, Any]
"""

import os
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple, Optional

# Configure logging
logger = logging.getLogger("management_skills_differentiator")

# File paths
DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / "cache" / "management"
OUTPUT_DIR = DATA_DIR / "output" / "management"
JOB_DATA_DIR = DATA_DIR / "jobs"
PROFILE_DATA_PATH = DATA_DIR / "profile" / "profile.json"
LEADERSHIP_FRAMEWORK_PATH = DATA_DIR / "reference" / "leadership_framework.json"

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Management competency categories
MANAGEMENT_COMPETENCIES = {
    "team_leadership": [
        "lead team", "team lead", "supervised", "managed team", "directed team",
        "leadership", "team leader", "guided team", "headed", "oversaw team"
    ],
    "strategic_planning": [
        "strategy", "strategic", "long-term", "vision", "roadmap", 
        "business planning", "strategic direction", "strategic initiative"
    ],
    "decision_making": [
        "decision", "judgment", "prioritize", "evaluated options", "authorized",
        "approved", "determined", "resolved", "problem-solving"
    ],
    "people_development": [
        "mentor", "coach", "train", "develop staff", "career development", 
        "performance review", "feedback", "growth", "talent development"
    ],
    "resource_management": [
        "budget", "resource allocation", "cost control", "financial management",
        "forecasting", "resource planning", "funding", "financial oversight"
    ],
    "communication": [
        "communicate", "presentation", "public speaking", "facilitation", 
        "stakeholder", "executive", "board", "persuasion", "influence"
    ],
    "change_management": [
        "change", "transformation", "transition", "restructuring", "realignment",
        "organizational change", "change initiative", "implementation"
    ],
    "conflict_resolution": [
        "conflict", "mediation", "dispute", "resolution", "negotiation",
        "consensus", "agreement", "compromise", "problem resolution"
    ]
}

# Phrases that indicate team size
TEAM_SIZE_PATTERNS = [
    r"team of (\d+)",
    r"(\d+)[- ]person team",
    r"managing (\d+)",
    r"supervising (\d+)",
    r"leading (\d+)",
    r"team with (\d+)",
    r"(\d+) direct reports",
    r"(\d+) employees"
]

def _load_leadership_framework() -> Dict[str, Any]:
    """
    Load leadership framework reference data
    
    Returns:
        Dictionary with leadership framework
    """
    try:
        if LEADERSHIP_FRAMEWORK_PATH.exists():
            with open(LEADERSHIP_FRAMEWORK_PATH, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Leadership framework file not found: {LEADERSHIP_FRAMEWORK_PATH}")
            # Return a default framework
            return {
                "levels": [
                    {
                        "name": "Individual Contributor",
                        "description": "No formal management responsibilities",
                        "team_size": 0,
                        "key_competencies": ["technical expertise", "self-management"]
                    },
                    {
                        "name": "Team Lead",
                        "description": "Guides small teams without formal authority",
                        "team_size": [1, 5],
                        "key_competencies": ["team_leadership", "communication"]
                    },
                    {
                        "name": "Manager",
                        "description": "Directly manages team members",
                        "team_size": [3, 15],
                        "key_competencies": ["team_leadership", "people_development", "resource_management"]
                    },
                    {
                        "name": "Senior Manager",
                        "description": "Manages other managers and larger departments",
                        "team_size": [10, 50],
                        "key_competencies": ["strategic_planning", "decision_making", "change_management"]
                    },
                    {
                        "name": "Director",
                        "description": "Oversees multiple teams or departments",
                        "team_size": [25, 100],
                        "key_competencies": ["strategic_planning", "communication", "resource_management"]
                    },
                    {
                        "name": "Executive",
                        "description": "C-suite or equivalent leadership position",
                        "team_size": [50, 1000],
                        "key_competencies": ["strategic_planning", "change_management", "communication"]
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error loading leadership framework: {e}")
        return {"levels": []}

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

def _extract_management_competencies(text: str) -> Dict[str, List[str]]:
    """
    Extract management competencies from text
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary mapping competency categories to found keywords
    """
    text = text.lower()
    competencies = {}
    
    for category, keywords in MANAGEMENT_COMPETENCIES.items():
        found = []
        for keyword in keywords:
            if keyword.lower() in text:
                found.append(keyword)
                
        if found:
            competencies[category] = found
    
    return competencies

def _extract_team_size(text: str) -> Optional[int]:
    """
    Extract team size mentioned in text
    
    Args:
        text: Text to analyze
        
    Returns:
        Team size as integer, or None if not found
    """
    largest_team = None
    
    for pattern in TEAM_SIZE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                team_size = int(match)
                if largest_team is None or team_size > largest_team:
                    largest_team = team_size
            except ValueError:
                pass
    
    return largest_team

def _determine_leadership_level(competencies: Dict[str, List[str]], team_size: Optional[int]) -> Dict[str, Any]:
    """
    Determine leadership level based on competencies and team size
    
    Args:
        competencies: Dictionary of competency categories
        team_size: Team size or None
        
    Returns:
        Dictionary with leadership level assessment
    """
    framework = _load_leadership_framework()
    competency_keys = set(competencies.keys())
    
    best_match = None
    best_match_score = -1
    
    for level in framework["levels"]:
        # Match on team size
        size_match = 0
        if team_size is not None and level.get("team_size", 0):
            if isinstance(level["team_size"], list):
                min_size, max_size = level["team_size"]
                if min_size <= team_size <= max_size:
                    size_match = 1
            elif team_size >= level["team_size"]:
                size_match = 1
        
        # Match on competencies
        competency_match = 0
        level_competencies = set(level.get("key_competencies", []))
        if level_competencies:
            competency_match = len(competency_keys.intersection(level_competencies)) / len(level_competencies)
        
        # Calculate overall match
        match_score = (size_match * 0.6) + (competency_match * 0.4)
        
        if match_score > best_match_score:
            best_match_score = match_score
            best_match = level
    
    if best_match:
        return {
            "level": best_match["name"],
            "description": best_match["description"],
            "confidence": best_match_score,
            "key_competencies": best_match.get("key_competencies", [])
        }
    else:
        return {
            "level": "Individual Contributor",
            "description": "No formal management responsibilities detected",
            "confidence": 1.0,
            "key_competencies": ["technical expertise", "self-management"]
        }

def differentiate_management_skills(job_id: str, force_reprocess: bool = False) -> Dict[str, Any]:
    """
    Analyze management skills alignment between job and candidate profile
    
    Args:
        job_id: Job ID to process
        force_reprocess: Force reprocessing even if cached results exist
        
    Returns:
        Dictionary with management skills analysis results
    """
    logger.info(f"Starting management skills analysis for job {job_id}")
    
    # Check for cached results
    cache_file = CACHE_DIR / f"{job_id}_management.json"
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
    
    # Extract text for analysis
    job_text = ' '.join([
        job_data.get('title', ''),
        job_data.get('description', ''),
        ' '.join(job_data.get('requirements', [])),
        ' '.join(job_data.get('responsibilities', []))
    ])
    
    # Extract management requirements from job
    job_competencies = _extract_management_competencies(job_text)
    job_team_size = _extract_team_size(job_text)
    
    # Determine job's leadership level
    job_leadership = _determine_leadership_level(job_competencies, job_team_size)
    
    # Calculate management intensity of the job (how management-focused it is)
    competency_count = sum(len(mentions) for mentions in job_competencies.values())
    management_intensity = min(1.0, competency_count / 20)  # Normalize, cap at 1.0
    
    # Process candidate profile
    profile_text = f"{profile_data.get('summary', '')} {' '.join(profile_data.get('skills', []))}"
    profile_experience = profile_data.get('experience', [])
    for exp in profile_experience:
        profile_text += f" {exp.get('title', '')} {exp.get('description', '')}"
    
    # Extract candidate's management experience
    candidate_competencies = _extract_management_competencies(profile_text)
    candidate_team_size = _extract_team_size(profile_text)
    
    # Determine candidate's leadership level
    candidate_leadership = _determine_leadership_level(candidate_competencies, candidate_team_size)
    
    # Calculate competency matches
    competency_matches = 0
    total_job_competencies = len(job_competencies)
    
    for category in job_competencies:
        if category in candidate_competencies:
            competency_matches += 1
    
    competency_match_score = competency_matches / max(1, total_job_competencies) if total_job_competencies > 0 else 0.0
    
    # Calculate team size match
    if job_team_size and candidate_team_size:
        if candidate_team_size >= job_team_size:
            team_size_match = 1.0
        else:
            team_size_match = candidate_team_size / job_team_size
    elif job_team_size:
        team_size_match = 0.0
    else:
        team_size_match = 1.0  # No team size requirement specified
    
    # Calculate leadership level match
    framework = _load_leadership_framework()
    level_names = [level["name"] for level in framework["levels"]]
    
    if job_leadership["level"] in level_names and candidate_leadership["level"] in level_names:
        job_level_index = level_names.index(job_leadership["level"])
        candidate_level_index = level_names.index(candidate_leadership["level"])
        
        if candidate_level_index >= job_level_index:
            leadership_match = 1.0  # Candidate meets or exceeds required level
        else:
            # Partial credit for being close
            level_gap = job_level_index - candidate_level_index
            leadership_match = max(0.0, 1.0 - (level_gap * 0.25))
    else:
        leadership_match = 0.5  # Default if levels can't be compared
    
    # Calculate overall management skills score
    if management_intensity > 0.7:  # Highly management-focused role
        management_score = (
            competency_match_score * 0.4 +
            team_size_match * 0.3 +
            leadership_match * 0.3
        )
    else:  # Less management-focused role
        management_score = (
            competency_match_score * 0.5 +
            team_size_match * 0.2 +
            leadership_match * 0.3
        )
    
    # Prepare results
    results = {
        "success": True,
        "job_id": job_id,
        "score": management_score,
        "job_analysis": {
            "management_competencies": job_competencies,
            "team_size": job_team_size,
            "leadership_level": job_leadership,
            "management_intensity": management_intensity
        },
        "candidate_analysis": {
            "management_competencies": candidate_competencies,
            "team_size": candidate_team_size,
            "leadership_level": candidate_leadership
        },
        "match_analysis": {
            "competency_match_score": competency_match_score,
            "team_size_match": team_size_match,
            "leadership_match": leadership_match
        },
        "recommendations": []
    }
    
    # Generate recommendations
    if management_intensity > 0.5 and management_score < 0.7:
        missing_competencies = [comp for comp in job_competencies if comp not in candidate_competencies]
        
        if missing_competencies:
            results["recommendations"].append({
                "type": "competency_gap",
                "message": f"Highlight experience with these management competencies: {', '.join(missing_competencies)}"
            })
            
        if job_team_size and (not candidate_team_size or candidate_team_size < job_team_size):
            results["recommendations"].append({
                "type": "team_size_gap",
                "message": f"Emphasize experience managing larger teams (target: {job_team_size}+ team members)"
            })
            
        if job_leadership["level"] in level_names and candidate_leadership["level"] in level_names:
            job_level_index = level_names.index(job_leadership["level"])
            candidate_level_index = level_names.index(candidate_leadership["level"])
            
            if job_level_index > candidate_level_index:
                results["recommendations"].append({
                    "type": "leadership_level_gap",
                    "message": f"Position yourself at the {job_leadership['level']} level by highlighting strategic initiatives and higher-level responsibilities"
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
    output_file = OUTPUT_DIR / f"{job_id}_management_analysis.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save detailed output: {e}")
    
    logger.info(f"Completed management skills analysis for job {job_id} with score {results['score']:.2f}")
    return results

if __name__ == "__main__":
    import argparse
    
    # Set up logging for standalone usage
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"logs/management_skills_differentiator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        ]
    )
    
    parser = argparse.ArgumentParser(description="Analyze management skills alignment between job and candidate profile")
    parser.add_argument("job_id", help="Job ID to process")
    parser.add_argument("--force", action="store_true", help="Force reprocessing even if cached results exist")
    args = parser.parse_args()
    
    results = differentiate_management_skills(args.job_id, args.force)
    print(json.dumps(results, indent=2))