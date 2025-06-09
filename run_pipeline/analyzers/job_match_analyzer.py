#!/usr/bin/env python3
"""
[DEPRECATED] - DO NOT USE - Job Match Analyzer Module

THIS FILE IS DEPRECATED AND SHOULD NOT BE USED.
A new implementation has replaced this module.
This file is kept only for historical reference.

This module aggregates and analyzes the results from all enhancement modules to create
a comprehensive job match assessment. It evaluates:

1. Overall match score with weighted contributions from specialized modules
2. Job fit across multiple dimensions (skills, impact, regulatory, management, synergy)
3. Key strengths and improvement areas for the specific role
4. Custom match insights based on correlations between different modules

This is distinct from the pipeline runner in that it provides deeper analytical insights
rather than just orchestrating the execution of other modules.

Function:
    analyze_job_match(job_id, results=None, force_reprocess=False) -> Dict[str, Any]
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple, Optional

# Configure logging
logger = logging.getLogger("job_match_analyzer")

# File paths
DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / "cache" / "job_match"
OUTPUT_DIR = DATA_DIR / "output" / "job_match"
JOB_DATA_DIR = DATA_DIR / "jobs"
PROFILE_DATA_PATH = DATA_DIR / "profile" / "profile.json"

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Default module weights for overall scoring
DEFAULT_WEIGHTS = {
    "terminology": 0.15,
    "impact": 0.20,
    "regulatory": 0.15,
    "management": 0.20,
    "synergy": 0.30
}

# Job title classifications for custom weighting
JOB_CLASSIFICATIONS = {
    "technical": [
        "engineer", "developer", "architect", "programmer", "analyst", 
        "administrator", "technician", "specialist"
    ],
    "management": [
        "manager", "director", "lead", "head", "chief", "officer", 
        "supervisor", "coordinator"
    ],
    "creative": [
        "designer", "writer", "editor", "creator", "artist", "producer", 
        "author", "consultant"
    ],
    "analytical": [
        "analyst", "scientist", "researcher", "strategist", "planner", 
        "advisor", "consultant"
    ],
    "regulatory": [
        "compliance", "legal", "auditor", "regulator", "governance", 
        "inspector", "examiner", "officer"
    ]
}

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

def _load_module_results(job_id: str, module_name: str) -> Optional[Dict[str, Any]]:
    """
    Load results from a specific module
    
    Args:
        job_id: Job ID
        module_name: Name of the module
        
    Returns:
        Module results or None if not found
    """
    cache_file = DATA_DIR / "cache" / module_name / f"{job_id}_{module_name}.json"
    if not cache_file.exists():
        logger.warning(f"Module results not found: {cache_file}")
        return None
        
    try:
        with open(cache_file, 'r') as f:
            return json.load(f)  # type: ignore
    except Exception as e:
        logger.error(f"Error loading module results: {e}")
        return None

def _classify_job(job_data: Dict[str, Any]) -> List[str]:
    """
    Classify the job into different categories based on title and description
    
    Args:
        job_data: Job data dictionary
        
    Returns:
        List of job classifications
    """
    job_title = job_data.get("title", "").lower()
    job_desc = job_data.get("description", "").lower()
    
    classifications = []
    
    for classification, keywords in JOB_CLASSIFICATIONS.items():
        if any(keyword in job_title for keyword in keywords):
            classifications.append(classification)
        elif any(keyword in job_desc for keyword in keywords):
            # Lower confidence if only in description, not title
            if classification not in classifications:
                classifications.append(classification)
    
    return classifications

def _calculate_custom_weights(job_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate custom module weights based on job classification
    
    Args:
        job_data: Job data dictionary
        
    Returns:
        Dictionary of module weights
    """
    classifications = _classify_job(job_data)
    weights = DEFAULT_WEIGHTS.copy()
    
    if "technical" in classifications:
        weights["terminology"] = 0.20
        weights["impact"] = 0.15
        weights["regulatory"] = 0.10
        weights["management"] = 0.15
        weights["synergy"] = 0.40
    
    elif "management" in classifications:
        weights["terminology"] = 0.10
        weights["impact"] = 0.25
        weights["regulatory"] = 0.10
        weights["management"] = 0.35
        weights["synergy"] = 0.20
    
    elif "regulatory" in classifications:
        weights["terminology"] = 0.15
        weights["impact"] = 0.15
        weights["regulatory"] = 0.40
        weights["management"] = 0.15
        weights["synergy"] = 0.15
    
    elif "creative" in classifications:
        weights["terminology"] = 0.15
        weights["impact"] = 0.25
        weights["regulatory"] = 0.05
        weights["management"] = 0.15
        weights["synergy"] = 0.40
    
    elif "analytical" in classifications:
        weights["terminology"] = 0.20
        weights["impact"] = 0.30
        weights["regulatory"] = 0.10
        weights["management"] = 0.10
        weights["synergy"] = 0.30
    
    # Normalize weights to ensure they sum to 1.0
    total_weight = sum(weights.values())
    if total_weight != 1.0:
        weights = {k: v / total_weight for k, v in weights.items()}
    
    return weights

def _identify_key_strengths(module_results: Dict[str, Dict[str, Any]], 
                          threshold: float = 0.75) -> List[Dict[str, Any]]:
    """
    Identify key strengths from module results
    
    Args:
        module_results: Dictionary of module results
        threshold: Score threshold for strengths
        
    Returns:
        List of key strengths
    """
    strengths = []
    
    for module, results in module_results.items():
        score = results.get("score", 0.0)
        
        if score >= threshold:
            if module == "terminology":
                matching_terms = results.get("match_analysis", {}).get("matching_terminology", [])
                if matching_terms:
                    strengths.append({
                        "module": "terminology",
                        "type": "terminology_match",
                        "score": score,
                        "description": f"Strong industry terminology alignment ({len(matching_terms)} matches)",
                        "details": matching_terms[:5]  # Top 5
                    })
            
            elif module == "impact":
                if score >= 0.8:  # Extra high score
                    strengths.append({
                        "module": "impact",
                        "type": "high_impact",
                        "score": score,
                        "description": "Exceptional project impact track record",
                        "details": results.get("match_analysis", {}).get("impact_alignment", 0.0)
                    })
            
            elif module == "regulatory":
                reg_domains = results.get("match_analysis", {}).get("domain_match_score", 0.0)
                if reg_domains >= 0.7:
                    strengths.append({
                        "module": "regulatory",
                        "type": "regulatory_expertise",
                        "score": score,
                        "description": "Strong regulatory domain knowledge",
                        "details": results.get("candidate_analysis", {}).get("regulatory_domains", {})
                    })
            
            elif module == "management":
                leadership = results.get("candidate_analysis", {}).get("leadership_level", {})
                if leadership:
                    strengths.append({
                        "module": "management",
                        "type": "leadership_level",
                        "score": score,
                        "description": f"Strong {leadership.get('level', 'management')} experience",
                        "details": leadership
                    })
            
            elif module == "synergy":
                synergies = results.get("match_analysis", {}).get("synergy_matches", [])
                if synergies:
                    strengths.append({
                        "module": "synergy",
                        "type": "skill_synergies",
                        "score": score,
                        "description": f"Valuable skill combinations: {', '.join([s['name'] for s in synergies[:2]])}",
                        "details": synergies[:3]  # Top 3
                    })
    
    # Sort by score in descending order
    strengths.sort(key=lambda x: x["score"], reverse=True)
    return strengths

def _identify_improvement_areas(module_results: Dict[str, Dict[str, Any]], 
                              threshold: float = 0.6) -> List[Dict[str, Any]]:
    """
    Identify areas for improvement from module results
    
    Args:
        module_results: Dictionary of module results
        threshold: Score threshold for areas that need improvement
        
    Returns:
        List of improvement areas
    """
    improvements = []
    
    for module, results in module_results.items():
        score = results.get("score", 0.0)
        
        if score < threshold:
            recommendations = results.get("recommendations", [])
            
            if recommendations:
                for rec in recommendations[:2]:  # Take top 2 recommendations
                    improvements.append({
                        "module": module,
                        "type": rec.get("type", "improvement"),
                        "score": score,
                        "description": rec.get("message", f"Improve {module} alignment"),
                        "details": rec.get("context", "")
                    })
            else:
                # Generic improvement suggestion if no specific recommendations
                if module == "terminology":
                    improvements.append({
                        "module": "terminology",
                        "type": "terminology_gap",
                        "score": score,
                        "description": "Enhance industry-specific terminology in profile",
                        "details": "Research and incorporate key terms from job description"
                    })
                elif module == "impact":
                    improvements.append({
                        "module": "impact",
                        "type": "impact_gap",
                        "score": score,
                        "description": "Strengthen project impact descriptions",
                        "details": "Add more quantifiable achievements and outcomes"
                    })
                elif module == "regulatory":
                    improvements.append({
                        "module": "regulatory",
                        "type": "regulatory_gap",
                        "score": score,
                        "description": "Enhance regulatory expertise presentation",
                        "details": "Highlight compliance and regulatory experience"
                    })
                elif module == "management":
                    improvements.append({
                        "module": "management",
                        "type": "management_gap",
                        "score": score,
                        "description": "Improve leadership experience presentation",
                        "details": "Emphasize team leadership and management achievements"
                    })
                elif module == "synergy":
                    improvements.append({
                        "module": "synergy",
                        "type": "synergy_gap",
                        "score": score,
                        "description": "Develop complementary skill combinations",
                        "details": "Focus on skills that create valuable synergies"
                    })
    
    # Sort by score in ascending order (worst scores first)
    improvements.sort(key=lambda x: x["score"])
    return improvements

def _analyze_module_correlations(module_results: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze correlations between different module scores
    
    Args:
        module_results: Dictionary of module results
        
    Returns:
        List of correlation insights
    """
    insights = []
    
    # Check management-impact correlation
    if "management" in module_results and "impact" in module_results:
        mgmt_score = module_results["management"].get("score", 0.0)
        impact_score = module_results["impact"].get("score", 0.0)
        
        mgmt_impact_gap = abs(mgmt_score - impact_score)
        if mgmt_score > 0.7 and impact_score < 0.5:
            insights.append({
                "type": "management_impact_gap",
                "description": "Strong management experience lacks corresponding impact metrics",
                "recommendation": "Quantify the impact of your management contributions with specific metrics",
                "correlation": -mgmt_impact_gap
            })
    
    # Check terminology-regulatory correlation
    if "terminology" in module_results and "regulatory" in module_results:
        term_score = module_results["terminology"].get("score", 0.0)
        reg_score = module_results["regulatory"].get("score", 0.0)
        
        if term_score > 0.7 and reg_score < 0.5:
            insights.append({
                "type": "terminology_regulatory_gap",
                "description": "Strong industry terminology without regulatory depth",
                "recommendation": "Develop deeper understanding of regulatory aspects related to your terminology knowledge",
                "correlation": term_score - reg_score
            })
    
    # Check synergy-management correlation
    if "synergy" in module_results and "management" in module_results:
        synergy_score = module_results["synergy"].get("score", 0.0)
        mgmt_score = module_results["management"].get("score", 0.0)
        
        if synergy_score > 0.8 and mgmt_score < 0.6:
            insights.append({
                "type": "synergy_leadership_opportunity",
                "description": "Strong skill synergies could translate to leadership potential",
                "recommendation": "Leverage your unique skill combinations to move into leadership roles",
                "correlation": synergy_score - mgmt_score
            })
    
    return insights

def analyze_job_match(job_id: str, results: Optional[Dict[str, Any]] = None, 
                   force_reprocess: bool = False) -> Dict[str, Any]:
    """
    Analyze comprehensive job match results
    
    Args:
        job_id: Job ID to process
        results: Optional pre-loaded results from other modules
        force_reprocess: Force reprocessing even if cached results exist
        
    Returns:
        Dictionary with comprehensive match analysis
    """
    logger.info(f"Starting job match analysis for job {job_id}")
    
    # Check for cached results
    cache_file = CACHE_DIR / f"{job_id}_job_match.json"
    if cache_file.exists() and not force_reprocess:
        try:
            with open(cache_file, 'r') as f:
                cached_results = json.load(f)
                logger.info(f"Using cached results for job {job_id}")
                return cached_results
        except Exception as e:
            logger.warning(f"Could not read cache file, reprocessing: {e}")
    
    # Load job data
    job_data = _load_job_data(job_id)
    
    if not job_data:
        error_message = "Job data not found"
        logger.error(error_message)
        return {
            "success": False,
            "error": error_message,
            "score": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    # Load module results if not provided
    if not results:
        module_results = {}
        modules = ["terminology", "impact", "regulatory", "management", "synergy"]
        
        for module in modules:
            module_result = _load_module_results(job_id, module)
            if module_result and module_result.get("success", False):
                module_results[module] = module_result
    else:
        module_results = results.get("module_results", {})
    
    if not module_results:
        error_message = "No module results found"
        logger.error(error_message)
        return {
            "success": False,
            "error": error_message,
            "score": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    # Calculate custom weights based on job classification
    weights = _calculate_custom_weights(job_data)
    
    # Calculate overall weighted score
    weighted_scores = {}
    total_weight_applied = 0.0
    
    for module, weight in weights.items():
        if module in module_results:
            module_score = module_results[module].get("score", 0.0)
            weighted_scores[module] = module_score * weight
            total_weight_applied += weight
    
    # If some modules are missing, normalize by the total weight applied
    if total_weight_applied > 0 and total_weight_applied < 1.0:
        overall_score = sum(weighted_scores.values()) / total_weight_applied
    else:
        overall_score = sum(weighted_scores.values())
    
    # Identify key strengths
    strengths = _identify_key_strengths(module_results)
    
    # Identify areas for improvement
    improvements = _identify_improvement_areas(module_results)
    
    # Analyze correlations between modules
    correlation_insights = _analyze_module_correlations(module_results)
    
    # Prepare results
    results = {
        "success": True,
        "job_id": job_id,
        "job_title": job_data.get("title", "Untitled Job"),
        "job_classifications": _classify_job(job_data),
        "score": overall_score,
        "module_weights": weights,
        "module_scores": {m: r.get("score", 0.0) for m, r in module_results.items()},
        "weighted_scores": weighted_scores,
        "strengths": strengths,
        "improvement_areas": improvements,
        "correlation_insights": correlation_insights,
        "recommendations": []
    }
    
    # Generate overall recommendations
    if overall_score < 0.6:
        results["recommendations"].append({
            "type": "overall_match",
            "message": "This job appears to be a modest match for your profile",
            "action": "Focus on the improvement areas before applying"
        })
    elif overall_score < 0.75:
        results["recommendations"].append({
            "type": "overall_match",
            "message": "This job aligns well with your profile with some gaps",
            "action": "Emphasize your strengths while addressing the top improvement areas"
        })
    else:
        results["recommendations"].append({
            "type": "overall_match",
            "message": "This job is an excellent match for your profile",
            "action": "Highlight your key strengths in your application materials"
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
    output_file = OUTPUT_DIR / f"{job_id}_match_analysis.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save detailed output: {e}")
    
    logger.info(f"Completed job match analysis for job {job_id} with score {results['score']:.2f}")
    return results

if __name__ == "__main__":
    import argparse
    
    # Set up logging for standalone usage
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"logs/job_match_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        ]
    )
    
    parser = argparse.ArgumentParser(description="Analyze comprehensive job match results")
    parser.add_argument("job_id", help="Job ID to process")
    parser.add_argument("--force", action="store_true", help="Force reprocessing even if cached results exist")
    args = parser.parse_args()
    
    results = analyze_job_match(args.job_id, force_reprocess=args.force)
    print(json.dumps(results, indent=2))