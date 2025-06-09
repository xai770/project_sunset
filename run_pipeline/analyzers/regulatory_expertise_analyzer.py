#!/usr/bin/env python3
"""
Regulatory Expertise Analyzer Module

This module analyzes regulatory and compliance expertise requirements in job descriptions
and matches them against candidate experience. It specializes in:

1. Identifying industry-specific regulations and compliance frameworks
2. Assessing depth of compliance experience in candidate profiles
3. Matching regulatory domains between jobs and candidates
4. Evaluating certification and formal regulatory training

The module is especially relevant for positions in highly regulated industries like
finance, healthcare, pharmaceuticals, aviation, and government contracting.

Function:
    analyze_regulatory_expertise(job_id, force_reprocess=False) -> Dict[str, Any]
"""

import os
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple, Optional

# Configure logging
logger = logging.getLogger("regulatory_expertise_analyzer")

# File paths
DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / "cache" / "regulatory"
OUTPUT_DIR = DATA_DIR / "output" / "regulatory"
JOB_DATA_DIR = DATA_DIR / "jobs"
PROFILE_DATA_PATH = DATA_DIR / "profile" / "profile.json"
REGULATIONS_PATH = DATA_DIR / "reference" / "regulations.json"

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Common regulatory domains
REGULATORY_DOMAINS = {
    "finance": ["banking", "securities", "investment", "trading", "financial", "fiscal", "tax"],
    "healthcare": ["medical", "health", "hospital", "patient", "clinical", "pharma"],
    "data_privacy": ["privacy", "data protection", "personal data", "gdpr", "ccpa", "cpra", "hipaa"],
    "environment": ["environmental", "emissions", "sustainability", "pollution", "waste"],
    "labor": ["employment", "workplace", "worker", "labor", "compensation", "discrimination"],
    "safety": ["safety", "occupational", "hazard", "protective", "prevention"],
    "telecom": ["telecommunications", "spectrum", "radio", "broadcast", "fcc"],
    "food": ["food", "agricultural", "fda", "usda", "nutrition"],
    "transportation": ["transportation", "automotive", "aviation", "railway", "shipping"],
    "energy": ["energy", "utilities", "electric", "nuclear", "petroleum"]
}

# Certification patterns
CERTIFICATION_PATTERNS = [
    r"certified\s+([a-z\s]+)",
    r"([a-z]{2,5})\s+certification",
    r"certified\s+([a-z]{2,5})",
    r"licensed\s+([a-z\s]+)"
]

def _load_regulations_reference() -> Dict[str, Any]:
    """
    Load regulations reference data
    
    Returns:
        Dictionary of regulations by domain
    """
    try:
        if REGULATIONS_PATH.exists():
            with open(REGULATIONS_PATH, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Regulations reference file not found: {REGULATIONS_PATH}")
            # Return a minimal set of regulations
            return {
                "finance": [
                    {"name": "Sarbanes-Oxley (SOX)", "keywords": ["sox", "sarbanes", "internal controls"]},
                    {"name": "Basel III", "keywords": ["basel", "capital requirements"]},
                    {"name": "Dodd-Frank", "keywords": ["dodd", "frank", "financial regulation"]}
                ],
                "healthcare": [
                    {"name": "HIPAA", "keywords": ["hipaa", "health insurance", "phi", "protected health"]},
                    {"name": "FDA Regulations", "keywords": ["fda", "food and drug", "medical device"]},
                    {"name": "Medicare/Medicaid", "keywords": ["medicare", "medicaid", "cms"]}
                ],
                "data_privacy": [
                    {"name": "GDPR", "keywords": ["gdpr", "general data protection", "eu privacy"]},
                    {"name": "CCPA/CPRA", "keywords": ["ccpa", "cpra", "california privacy"]},
                    {"name": "PIPEDA", "keywords": ["pipeda", "canadian privacy"]}
                ],
                "general": [
                    {"name": "ISO Standards", "keywords": ["iso", "international standards"]},
                    {"name": "Corporate Compliance", "keywords": ["compliance", "corporate governance"]},
                    {"name": "Risk Management", "keywords": ["risk", "compliance risk"]}
                ]
            }
    except Exception as e:
        logger.error(f"Error loading regulations reference: {e}")
        return {}

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

def _detect_regulatory_domains(text: str) -> Dict[str, float]:
    """
    Detect regulatory domains in text
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary of domain names to confidence scores
    """
    text = text.lower()
    domain_scores = {}
    
    for domain, keywords in REGULATORY_DOMAINS.items():
        matches = 0
        for keyword in keywords:
            if keyword.lower() in text:
                matches += 1
                
        if matches > 0:
            confidence = min(1.0, matches / max(1, len(keywords) / 2))
            domain_scores[domain] = confidence
    
    return domain_scores

def _detect_regulations(text: str, regulations: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Detect specific regulations in text
    
    Args:
        text: Text to analyze
        regulations: Regulations reference dictionary
        
    Returns:
        List of detected regulations with confidence scores
    """
    text = text.lower()
    detected = []
    
    for domain, regs in regulations.items():
        for reg in regs:
            name = reg["name"]
            keywords = reg["keywords"]
            
            matches = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    matches += 1
                    
            if matches > 0:
                confidence = min(1.0, matches / len(keywords))
                detected.append({
                    "name": name,
                    "domain": domain,
                    "confidence": confidence
                })
    
    # Sort by confidence score
    detected.sort(key=lambda x: x["confidence"], reverse=True)
    return detected

def _extract_certifications(text: str) -> List[str]:
    """
    Extract certification mentions from text
    
    Args:
        text: Text to analyze
        
    Returns:
        List of detected certifications
    """
    text = text.lower()
    certifications = set()
    
    for pattern in CERTIFICATION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        certifications.update(matches)
    
    return list(certifications)

def analyze_regulatory_expertise(job_id: str, force_reprocess: bool = False) -> Dict[str, Any]:
    """
    Analyze regulatory expertise alignment between job and candidate profile
    
    Args:
        job_id: Job ID to process
        force_reprocess: Force reprocessing even if cached results exist
        
    Returns:
        Dictionary with regulatory expertise analysis results
    """
    logger.info(f"Starting regulatory expertise analysis for job {job_id}")
    
    # Check for cached results
    cache_file = CACHE_DIR / f"{job_id}_regulatory.json"
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
    regulations_ref = _load_regulations_reference()
    
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
    
    # Analyze job regulatory requirements
    job_domains = _detect_regulatory_domains(job_text)
    job_regulations = _detect_regulations(job_text, regulations_ref)
    job_certifications = _extract_certifications(job_text)
    
    # Calculate regulatory intensity of the job
    regulatory_intensity = min(1.0, (
        len(job_domains) * 0.3 + 
        len(job_regulations) * 0.5 + 
        len(job_certifications) * 0.2
    ) / 3)
    
    # Process candidate profile
    profile_text = f"{profile_data.get('summary', '')} {' '.join(profile_data.get('skills', []))}"
    profile_experience = profile_data.get('experience', [])
    for exp in profile_experience:
        profile_text += f" {exp.get('title', '')} {exp.get('description', '')}"
    
    # Analyze candidate regulatory expertise
    candidate_domains = _detect_regulatory_domains(profile_text)
    candidate_regulations = _detect_regulations(profile_text, regulations_ref)
    candidate_certifications = _extract_certifications(profile_text)
    
    # Calculate domain match score
    domain_matches = 0.0
    total_job_domains = len(job_domains)
    
    for domain, job_score in job_domains.items():
        if domain in candidate_domains:
            candidate_score = candidate_domains[domain]
            domain_matches += min(job_score, candidate_score)
    
    domain_match_score = domain_matches / max(1, total_job_domains) if total_job_domains > 0 else 0.0
    
    # Calculate regulation match score
    regulation_matches = 0
    total_job_regulations = len(job_regulations)
    
    for job_reg in job_regulations:
        for cand_reg in candidate_regulations:
            if job_reg["name"] == cand_reg["name"]:
                regulation_matches += min(job_reg["confidence"], cand_reg["confidence"])
                break
    
    regulation_match_score = regulation_matches / max(1, total_job_regulations) if total_job_regulations > 0 else 0.0
    
    # Calculate certification match
    cert_match_count = 0
    for job_cert in job_certifications:
        for cand_cert in candidate_certifications:
            if job_cert.lower() in cand_cert.lower() or cand_cert.lower() in job_cert.lower():
                cert_match_count += 1
                break
                
    cert_match_score = cert_match_count / max(1, len(job_certifications)) if job_certifications else 1.0
    
    # Calculate overall regulatory match score
    if regulatory_intensity > 0.6:  # Highly regulated role
        regulatory_score = (
            domain_match_score * 0.3 +
            regulation_match_score * 0.4 +
            cert_match_score * 0.3
        )
    else:  # Less regulated role
        regulatory_score = (
            domain_match_score * 0.4 +
            regulation_match_score * 0.4 +
            cert_match_score * 0.2
        )
    
    # Prepare results
    results: Dict[str, Any] = {
        "success": True,
        "job_id": job_id,
        "score": regulatory_score,
        "job_analysis": {
            "regulatory_domains": job_domains,
            "regulations": job_regulations,
            "certifications": job_certifications,
            "regulatory_intensity": regulatory_intensity
        },
        "candidate_analysis": {
            "regulatory_domains": candidate_domains,
            "regulations": candidate_regulations,
            "certifications": candidate_certifications
        },
        "match_analysis": {
            "domain_match_score": domain_match_score,
            "regulation_match_score": regulation_match_score,
            "certification_match_score": cert_match_score
        },
        "recommendations": []
    }
    
    # Generate recommendations
    if regulatory_intensity > 0.5 and regulatory_score < 0.7:
        missing_domains = [domain for domain in job_domains if domain not in candidate_domains]
        missing_regulations = [reg["name"] for reg in job_regulations if not any(
            cand_reg["name"] == reg["name"] for cand_reg in candidate_regulations
        )]
        missing_certifications = [cert for cert in job_certifications if not any(
            cert.lower() in cand_cert.lower() or cand_cert.lower() in cert.lower() 
            for cand_cert in candidate_certifications
        )]
        
        if missing_domains:
            results["recommendations"].append({
                "type": "domain_gap",
                "message": f"Highlight experience in these regulatory domains: {', '.join(missing_domains[:3])}"
            })
            
        if missing_regulations:
            results["recommendations"].append({
                "type": "regulation_gap",
                "message": f"Emphasize experience with these regulations: {', '.join(missing_regulations[:3])}"
            })
            
        if missing_certifications:
            results["recommendations"].append({
                "type": "certification_gap",
                "message": f"Consider obtaining these certifications: {', '.join(missing_certifications[:3])}"
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
    output_file = OUTPUT_DIR / f"{job_id}_regulatory_analysis.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save detailed output: {e}")
    
    logger.info(f"Completed regulatory expertise analysis for job {job_id} with score {results['score']:.2f}")
    return results

if __name__ == "__main__":
    import argparse
    
    # Set up logging for standalone usage
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"logs/regulatory_expertise_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        ]
    )
    
    parser = argparse.ArgumentParser(description="Analyze regulatory expertise alignment between job and candidate profile")
    parser.add_argument("job_id", help="Job ID to process")
    parser.add_argument("--force", action="store_true", help="Force reprocessing even if cached results exist")
    args = parser.parse_args()
    
    results = analyze_regulatory_expertise(args.job_id, args.force)
    print(json.dumps(results, indent=2))