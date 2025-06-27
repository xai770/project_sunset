#!/usr/bin/env python3
"""
Project Impact Analyzer Module

This module evaluates project impact by analyzing:
1. Project scale and complexity mentioned in job descriptions
2. Project impact metrics in candidate experience 
3. Alignment between job projects and candidate project experience
4. Project outcome focus in both job and candidate profiles

The analysis helps determine if a candidate's project experience aligns with 
the scale and impact expected in the job position.

Function:
    analyze_project_impact(job_id, force_reprocess=False) -> Dict[str, Any]
"""

import os
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple, Optional

# Configure logging
logger = logging.getLogger("project_impact_analyzer")

# File paths
DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / "cache" / "project_impact"
OUTPUT_DIR = DATA_DIR / "output" / "project_impact"
JOB_DATA_DIR = DATA_DIR / "jobs"
PROFILE_DATA_PATH = DATA_DIR / "profile" / "profile.json"

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Project scale indicators
SCALE_INDICATORS = {
    "enterprise": 5.0,
    "large-scale": 4.5,
    "complex": 4.0,
    "multi-team": 3.5,
    "cross-functional": 3.5,
    "company-wide": 4.0,
    "global": 5.0,
    "international": 4.0,
    "national": 3.5,
    "regional": 3.0,
    "department": 2.5,
    "team": 2.0,
    "small": 1.5,
    "individual": 1.0
}

# Impact metrics
IMPACT_METRICS = [
    r"(\d+)%\s+increase",
    r"(\d+)%\s+improvement",
    r"(\d+)%\s+reduction",
    r"reduced\s+(\d+)%",
    r"improved\s+(\d+)%",
    r"saved\s+(\d+)\s+hours",
    r"(\$[\d,.]+\s+[kmb]illion)",
    r"(\$[\d,.]+\s+[kmb]?)",
    r"(increased|improved|enhanced|optimized|streamlined)",
    r"(led|managed|directed|supervised)\s+team\s+of\s+(\d+)",
    r"impacting\s+(\d+)"
]

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

def _extract_project_scale(text: str) -> Dict[str, float]:
    """
    Extract project scale indicators from text
    
    Args:
        text: Text to extract scale indicators from
        
    Returns:
        Dictionary of scale indicators and their scores
    """
    text = text.lower()
    found_scales = {}
    
    for indicator, score in SCALE_INDICATORS.items():
        if indicator.lower() in text:
            found_scales[indicator] = score
            
    return found_scales

def _extract_impact_metrics(text: str) -> List[str]:
    """
    Extract impact metrics from text
    
    Args:
        text: Text to extract impact metrics from
        
    Returns:
        List of found impact metric strings
    """
    found_metrics = []
    for pattern in IMPACT_METRICS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            for match in matches:
                if isinstance(match, tuple):
                    # Some patterns have capture groups
                    metric_text = ' '.join([m for m in match if m])
                    found_metrics.append(metric_text)
                else:
                    found_metrics.append(match)
    
    return found_metrics

def analyze_project_impact(job_id: str, force_reprocess: bool = False) -> Dict[str, Any]:
    """
    Analyze project impact alignment between job and candidate profile
    
    Args:
        job_id: Job ID to process
        force_reprocess: Force reprocessing even if cached results exist
        
    Returns:
        Dictionary with project impact analysis results
    """
    logger.info(f"Starting project impact analysis for job {job_id}")
    
    # Check for cached results
    cache_file = CACHE_DIR / f"{job_id}_project_impact.json"
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
    
    # Extract project scale from job
    job_scales = _extract_project_scale(job_text)
    job_scale_score = max(job_scales.values()) if job_scales else 2.5  # Default to mid-range if no scales found
    
    # Extract impact metrics from job
    job_impact_metrics = _extract_impact_metrics(job_text)
    
    # Calculate job's impact focus (how much the job description focuses on impact)
    job_impact_focus = min(1.0, len(job_impact_metrics) / 5)  # Normalize to 0-1, cap at 1.0
    
    # Analyze candidate profile for project impact
    profile_experience = profile_data.get('experience', [])
    candidate_projects = []
    
    for exp in profile_experience:
        exp_text = f"{exp.get('title', '')} {exp.get('description', '')}"
        project_scales = _extract_project_scale(exp_text)
        impact_metrics = _extract_impact_metrics(exp_text)
        
        # Calculate the scale score for this experience
        scale_score = max(project_scales.values()) if project_scales else 1.0
        
        # Calculate the impact focus for this experience
        impact_focus = min(1.0, len(impact_metrics) / 3)  # Normalize, cap at 1.0
        
        candidate_projects.append({
            "title": exp.get('title', 'Untitled Experience'),
            "scale_indicators": project_scales,
            "scale_score": scale_score,
            "impact_metrics": impact_metrics,
            "impact_focus": impact_focus
        })
    
    # Calculate overall candidate scale score (weighted toward higher scale experiences)
    candidate_scales = sorted([p["scale_score"] for p in candidate_projects], reverse=True)
    if candidate_scales:
        # Give more weight to the top 3 experiences
        top_scales = candidate_scales[:3]
        candidate_scale_score = sum(top_scales) / len(top_scales) if top_scales else 0
    else:
        candidate_scale_score = 0
    
    # Calculate overall candidate impact focus
    candidate_impact_metrics = []
    for project in candidate_projects:
        candidate_impact_metrics.extend(project["impact_metrics"])
    
    candidate_impact_focus = min(1.0, len(candidate_impact_metrics) / 10)  # Normalize, cap at 1.0
    
    # Calculate scale alignment (how well the candidate's project scale matches the job's requirements)
    # 1.0 means perfect alignment, 0.0 means completely misaligned
    if job_scale_score > 0 and candidate_scale_score > 0:
        scale_ratio = candidate_scale_score / job_scale_score
        scale_alignment = min(1.0, scale_ratio)  # Cap at 1.0
    else:
        scale_alignment = 0.0
    
    # Calculate impact alignment
    impact_alignment = min(1.0, candidate_impact_focus / max(0.1, job_impact_focus))
    
    # Calculate overall project impact score
    # Weight scale alignment higher for senior positions, impact alignment higher for junior positions
    is_senior = any(term in job_data.get('title', '').lower() for term in ['senior', 'lead', 'manager', 'director', 'head'])
    
    if is_senior:
        # Senior roles need both scale and impact
        project_impact_score = (scale_alignment * 0.7) + (impact_alignment * 0.3)
    else:
        # Junior roles focus more on impact metrics
        project_impact_score = (scale_alignment * 0.3) + (impact_alignment * 0.7)
    
    # Prepare results
    results = {
        "success": True,
        "job_id": job_id,
        "score": project_impact_score,
        "job_analysis": {
            "scale_indicators": job_scales,
            "scale_score": job_scale_score,
            "impact_metrics": job_impact_metrics,
            "impact_focus": job_impact_focus,
            "is_senior_role": is_senior
        },
        "candidate_analysis": {
            "projects": candidate_projects,
            "scale_score": candidate_scale_score,
            "impact_metrics": candidate_impact_metrics,
            "impact_focus": candidate_impact_focus
        },
        "alignment": {
            "scale_alignment": scale_alignment,
            "impact_alignment": impact_alignment
        },
        "recommendations": []
    }
    
    # Generate recommendations
    if scale_alignment < 0.7:
        results["recommendations"].append({
            "type": "scale_improvement",
            "message": "Consider highlighting larger-scale project experience",
            "context": f"Job requires {list(job_scales.keys())[:3] if job_scales else 'significant'} project scale"
        })
    
    if impact_alignment < 0.7:
        results["recommendations"].append({
            "type": "impact_improvement",
            "message": "Include more quantifiable impact metrics in your experience descriptions",
            "context": "Quantify your achievements with percentages, numbers, or other metrics"
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
    output_file = OUTPUT_DIR / f"{job_id}_project_impact_analysis.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save detailed output: {e}")
    
    logger.info(f"Completed project impact analysis for job {job_id} with score {results['score']:.2f}")
    return results

if __name__ == "__main__":
    import argparse
    
    # Set up logging for standalone usage
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"logs/project_impact_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        ]
    )
    
    parser = argparse.ArgumentParser(description="Analyze project impact alignment between job and candidate profile")
    parser.add_argument("job_id", help="Job ID to process")
    parser.add_argument("--force", action="store_true", help="Force reprocessing even if cached results exist")
    args = parser.parse_args()
    
    results = analyze_project_impact(args.job_id, args.force)
    print(json.dumps(results, indent=2))