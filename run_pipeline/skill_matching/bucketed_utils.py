#!/usr/bin/env python3
"""
Skill extraction, categorization, and utility functions for bucketed matcher (extracted from bucketed_skill_matcher.py)
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucketed_utils")

# Get paths from the main config
try:
    from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR
except ImportError:
    # Fallback if imported outside the pipeline
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    JOB_DATA_DIR = PROJECT_ROOT / "data" / "postings"

# Define paths
YOUR_SKILLS_FILE = PROJECT_ROOT / "profile" / "skills" / "skill_decompositions.json"

# Define skill buckets - simplified from the enhanced_skill_matcher categories
SKILL_BUCKETS = {
    "Technical": [
        "programming", "software", "development", "engineering", "code", "coding", 
        "database", "cloud", "devops", "system", "infrastructure", "technology",
        "technical", "it", "computer", "machine learning", "ai", "algorithm",
        "architecture", "backend", "frontend", "web", "mobile", "network",
        "security", "cybersecurity", "hardware", "automation", "qa", "testing"
    ],
    "Management": [
        "leadership", "management", "project", "team", "strategic", "planning", 
        "program", "portfolio", "executive", "change", "organizational", "resource",
        "supervisor", "director", "manager", "lead", "coordinator", "administration"
    ],
    "Domain_Knowledge": [
        "finance", "banking", "insurance", "healthcare", "manufacturing", "retail", 
        "telecom", "energy", "legal", "education", "government", "pharmaceutical",
        "biotech", "real estate", "hospitality", "transportation", "logistics",
        "agriculture", "media", "entertainment", "industry", "domain", "sector",
        "field", "specialization", "expertise", "knowledge"
    ],
    "Soft_Skills": [
        "communication", "teamwork", "problem solving", "critical thinking", 
        "adaptability", "time management", "collaboration", "interpersonal",
        "negotiation", "conflict resolution", "emotional intelligence", "leadership",
        "decision making", "creativity", "innovation", "motivation", "flexibility",
        "presentation", "persuasion", "empathy", "ethic", "social", "personal"
    ],
    "Analytics": [
        "data analysis", "business intelligence", "reporting", "statistics",
        "forecasting", "analytics", "visualization", "sql", "quantitative",
        "market research", "competitive analysis", "metrics", "kpi", "insight",
        "trend", "pattern", "predictive", "descriptive", "diagnostic", "dashboard"
    ]
}

def categorize_skill(skill_name: str, skill_description: str = "") -> str:
    """
    Categorize a skill into one of the predefined buckets
    
    Args:
        skill_name: The name of the skill
        skill_description: Optional description of the skill
    
    Returns:
        str: The bucket name (or 'Other' if no match)
    """
    # Combine name and description for better categorization
    text = f"{skill_name} {skill_description}".lower()
    
    # Check each bucket's keywords
    for bucket, keywords in SKILL_BUCKETS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return bucket
    
    # Default bucket for uncategorized skills
    return "Other"

def extract_cv_skills(cv_skills_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Extract skills from CV data and organize them into buckets
    
    Args:
        cv_skills_data: The CV skills data structure
    
    Returns:
        Dict[str, List[str]]: Skills organized by bucket
    """
    bucketed_skills: Dict[str, List[str]] = {bucket: [] for bucket in SKILL_BUCKETS.keys()}
    bucketed_skills["Other"] = []  # For skills that don't match any bucket
    
    # Process complex skills
    complex_skills = cv_skills_data.get("complex_skills", [])
    for skill in complex_skills:
        name = skill.get("name", "")
        description = skill.get("description", "")
        
        if name:
            bucket = categorize_skill(name, description)
            bucketed_skills[bucket].append(name)
    
    # Process elementary skills if they exist separately
    elementary_skills = cv_skills_data.get("elementary_skills", [])
    for skill in elementary_skills:
        if isinstance(skill, dict):
            name = skill.get("name", "")
            description = skill.get("description", "")
        else:
            name = skill
            description = ""
        
        if name and name not in [s for skills in bucketed_skills.values() for s in skills]:
            bucket = categorize_skill(name, description)
            bucketed_skills[bucket].append(name)
    
    return bucketed_skills

def extract_job_skills(job_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Extract skills from job data and organize them into buckets
    
    Args:
        job_data: The job data structure
    
    Returns:
        Dict[str, List[str]]: Skills organized by bucket
    """
    bucketed_skills: Dict[str, List[str]] = {bucket: [] for bucket in SKILL_BUCKETS.keys()}
    bucketed_skills["Other"] = []  # For skills that don't match any bucket
    
    # Process SDR skills if available
    sdr_skills = job_data.get("sdr_skills", {}).get("enriched", {})
    
    if sdr_skills:
        for skill_name, skill_info in sdr_skills.items():
            if isinstance(skill_info, dict):
                description = skill_info.get("description", "")
            else:
                description = ""
            
            bucket = categorize_skill(skill_name, description)
            bucketed_skills[bucket].append(skill_name)
    
    # If no SDR skills found, try to extract from job description
    if not any(skills for skills in bucketed_skills.values()):
        job_description = job_data.get("job_description", "")
        if job_description:
            # Extract potential skills from job description
            extracted_skills = extract_skills_from_text(job_description)
            for skill in extracted_skills:
                bucket = categorize_skill(skill)
                bucketed_skills[bucket].append(skill)
    
    return bucketed_skills

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract potential skills from text using simple heuristics
    This is a basic implementation that could be enhanced
    
    Args:
        text: Text to extract skills from
    
    Returns:
        List[str]: List of potential skills
    """
    # Basic skill extraction using common patterns
    skills = []
    
    # Look for "skills" sections
    skill_section_pattern = r"(?:skills|requirements|qualifications)(?:[^\n]*)\n((?:.*\n)+?)(?:\n\n|\Z)"
    skill_sections = re.findall(skill_section_pattern, text.lower(), re.IGNORECASE)
    
    for section in skill_sections:
        # Extract bullet points
        bullet_pattern = r"(?:^|\n)(?:\s*[-•*]\s*|\d+\.\s*)([^\n]+)"
        bullets = re.findall(bullet_pattern, section)
        skills.extend([b.strip() for b in bullets if len(b.strip()) > 3])
    
    # If no skills found, try to extract potential skill phrases
    if not skills:
        # Look for common skill phrase patterns
        skill_phrases = re.findall(r"(?:proficient in|experience with|knowledge of|expertise in|skilled in|familiar with)\s+([^,.;]+)", text.lower())
        skills.extend([s.strip() for s in skill_phrases if len(s.strip()) > 3])
    
    # Remove duplicates
    return list(set(skills))

def extract_percentage(text: str) -> float:
    """
    Extract percentage value from LLM response
    
    Args:
        text: Text containing a percentage value
        
    Returns:
        float: Extracted percentage as a value between 0.0 and 1.0
    """
    # Look for percentage patterns
    percentage_patterns = [
        r"(\d{1,3})%",  # 85%
        r"(\d{1,3})\s*percent",  # 85 percent
        r"(\d{1,3}(?:\.\d+)?)%"  # 85.5%
        r"(\d{1,3}(?:\.\d+)?)\s*percent"  # 85.5 percent
    ]
    
    for pattern in percentage_patterns:
        matches = re.findall(pattern, text)
        if matches:
            try:
                return float(matches[0]) / 100  # Convert to 0-1 scale
            except (ValueError, TypeError):
                continue
    
    # If no percentage found, look for decimal format
    decimal_patterns = [
        r"(\d\.\d+)\s*(?:out of 1)?",  # 0.85 or 0.85 out of 1
        r"(\d+)/100"  # 85/100
    ]
    
    for pattern in decimal_patterns:
        matches = re.findall(pattern, text)
        if matches:
            try:
                value = float(matches[0])
                if "100" in pattern:  # If pattern is x/100
                    value = value / 100
                return value
            except (ValueError, TypeError):
                continue
    
    # Default if no match found
    logger.warning(f"Could not extract percentage from LLM response: {text}")
    return 0.5  # Default to 50%

def load_your_skills() -> Optional[Dict[str, Any]]:
    """
    Load your skills from the standard location
    
    Returns:
        Optional[Dict[str, Any]]: Your skills data or None if loading fails
    """
    if not YOUR_SKILLS_FILE.exists():
        logger.error(f"Your skills file not found: {YOUR_SKILLS_FILE}")
        return None
    try:
        with open(YOUR_SKILLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load your skills: {e}")
        return None

def load_job_data(job_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load job data from a file
    
    Args:
        job_path: Path to job file
        
    Returns:
        Optional[Dict[str, Any]]: Job data or None if loading fails
    """
    try:
        with open(job_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load job file {job_path}: {e}")
        return None

def save_job_data(job_path: Path, job_data: Dict[str, Any]) -> None:
    """
    Save job data to a file
    
    Args:
        job_path: Path to job file
        job_data: Job data to save
    """
    try:
        with open(job_path, "w", encoding="utf-8") as f:
            json.dump(job_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save job file {job_path}: {e}")
