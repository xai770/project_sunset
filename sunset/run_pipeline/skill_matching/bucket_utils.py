#!/usr/bin/env python3
"""
Utility functions for bucketed skill matching
"""

import re
import logging
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucket_utils")

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract potential skills from text using improved heuristics
    
    Args:
        text: Text to extract skills from
    
    Returns:
        List[str]: List of potential skills
    """
    if not text:
        return []
        
    # Normalize text for better extraction
    normalized_text = text.replace('\r', '\n')
    skills = []
    
    # Common technical skills to look for directly
    common_technical_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "Go", "PHP",
        "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "Spring",
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Git", "SQL", "NoSQL",
        "MongoDB", "PostgreSQL", "MySQL", "Redis", "Elasticsearch", "GraphQL", "REST API",
        "CI/CD", "Jenkins", "GitHub Actions", "Terraform", "Ansible", "DevOps", "Agile", "Scrum"
    ]
    
    # Add common technical skills if they appear in the text
    for skill in common_technical_skills:
        if skill.lower() in normalized_text.lower():
            if skill not in skills:
                skills.append(skill)
    
    # Extract skills from bullet points and lists
    bullet_pattern = r'(?:^|\n)(?:[\s]*[-•*>+]|\d+\.)[\s]+([^:\n]+)'
    bullet_matches = re.findall(bullet_pattern, normalized_text)
    
    for match in bullet_matches:
        # Clean up the match and check if it looks like a skill
        cleaned = match.strip()
        if 3 <= len(cleaned) <= 50 and not cleaned.endswith(('.', ':', ';')):
            if cleaned not in skills:
                skills.append(cleaned)
    
    # Extract skills from longer text
    words = normalized_text.split()
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        if (words[i][0].isupper() or words[i+1][0].isupper()) and 3 <= len(bigram) <= 30:
            if bigram not in skills:
                skills.append(bigram)
    
    return skills

# Get paths from the main config
try:
    from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR
except ImportError:
    # Fallback if imported outside the pipeline
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    JOB_DATA_DIR = PROJECT_ROOT / "data" / "postings"

# Define paths
YOUR_SKILLS_FILE = PROJECT_ROOT / "profile" / "skills" / "skill_decompositions.json"

# Define skill buckets - simplified categories
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
    all_skills: Set[str] = set()  # Track all skills to avoid duplicates
    skills_found = False
    
    # Process SDR skills if available (highest priority source)
    sdr_skills = job_data.get("sdr_skills", {}).get("enriched", {})
    
    if sdr_skills:
        for skill_name, skill_info in sdr_skills.items():
            if isinstance(skill_info, dict):
                description = skill_info.get("description", "")
            else:
                description = ""
            
            if skill_name.lower() not in all_skills:
                bucket = categorize_skill(skill_name, description)
                bucketed_skills[bucket].append(skill_name)
                all_skills.add(skill_name.lower())
                skills_found = True
    
    # Check for standard skills as a simple list
    standard_skills = job_data.get("skills", [])
    if standard_skills and isinstance(standard_skills, list):
        for skill in standard_skills:
            if isinstance(skill, str) and skill.lower() not in all_skills:
                bucket = categorize_skill(skill)
                bucketed_skills[bucket].append(skill)
                all_skills.add(skill.lower())
                skills_found = True
    
    # Check for skill matches that might contain skill information
    skill_matches = job_data.get("skill_matches", {}).get("matches", [])
    if skill_matches:
        for match_entry in skill_matches:
            if isinstance(match_entry, dict):
                skill = match_entry.get("job_skill", "")
                if skill and skill.lower() not in all_skills:
                    bucket = categorize_skill(skill)
                    bucketed_skills[bucket].append(skill)
                    all_skills.add(skill.lower())
                    skills_found = True
    
    # Check for structured description requirements
    structured_requirements = job_data.get("web_details", {}).get("structured_description", {}).get("requirements", [])
    if structured_requirements and isinstance(structured_requirements, list):
        for requirement in structured_requirements:
            if isinstance(requirement, str):
                # Extract potential skills from each requirement
                skill_parts = re.split(r',|;|and', requirement)
                for part in skill_parts:
                    skill = part.strip()
                    if len(skill) > 3 and skill.lower() not in all_skills:
                        bucket = categorize_skill(skill)
                        bucketed_skills[bucket].append(skill)
                        all_skills.add(skill.lower())
                        skills_found = True
    
    # Also check responsibilities for skillset requirements
    structured_responsibilities = job_data.get("web_details", {}).get("structured_description", {}).get("responsibilities", [])
    if structured_responsibilities and isinstance(structured_responsibilities, list):
        for responsibility in structured_responsibilities:
            if isinstance(responsibility, str):
                # Look for phrases indicating skills in responsibilities
                if any(keyword in responsibility.lower() for keyword in [
                    "using", "with", "skills", "ability", "knowledge", "experience", "proficient"
                ]):
                    skill_parts = re.split(r',|;|and', responsibility)
                    for part in skill_parts:
                        skill = part.strip()
                        if len(skill) > 3 and skill.lower() not in all_skills:
                            bucket = categorize_skill(skill)
                            bucketed_skills[bucket].append(skill)
                            all_skills.add(skill.lower())
                            skills_found = True
    
    # Check for concise description - often contains key skills
    concise_description = job_data.get("web_details", {}).get("concise_description", "")
    if isinstance(concise_description, str) and concise_description:
        # Extract requirements section from concise description
        requirements_match = re.search(r'Requirements:(.*?)(?:\n\n|\Z)', concise_description, re.DOTALL)
        if requirements_match:
            requirements_text = requirements_match.group(1)
            requirements_items = re.findall(r'-\s*(.*?)(?:\n|$)', requirements_text)
            for item in requirements_items:
                skill = item.strip()
                if len(skill) > 3 and skill.lower() not in all_skills:
                    bucket = categorize_skill(skill)
                    bucketed_skills[bucket].append(skill)
                    all_skills.add(skill.lower())
                    skills_found = True
    
    # If still no skills found, try to extract from job description
    if not skills_found or sum(len(skills) for skills in bucketed_skills.values()) < 3:
        job_description = job_data.get("job_description", "")
        if job_description:
            # Extract potential skills from job description
            extracted_skills = extract_skills_from_text(job_description)
            for skill in extracted_skills:
                if skill.lower() not in all_skills:
                    bucket = categorize_skill(skill)
                    bucketed_skills[bucket].append(skill)
                    all_skills.add(skill.lower())
    
    return bucketed_skills

def calculate_bucket_weights(job_skills_buckets: Dict[str, List[str]]) -> Dict[str, float]:
    """
    Calculate weights for each skill bucket based on job requirements
    
    Args:
        job_skills_buckets: Job skills organized by bucket
    
    Returns:
        Dict[str, float]: Weight for each bucket (0.0-1.0)
    """
    # Count skills in each bucket
    bucket_counts = {bucket: len(skills) for bucket, skills in job_skills_buckets.items()}
    total_skills = sum(bucket_counts.values())
    
    if total_skills == 0:
        # Equal weight if no skills
        return {bucket: 1.0 / len(job_skills_buckets) for bucket in job_skills_buckets}
    
    # Calculate weights based on proportion of skills
    weights = {bucket: count / total_skills for bucket, count in bucket_counts.items()}
    
    # Ensure minimum weight for each bucket with at least one skill
    min_weight = 0.1
    for bucket, count in bucket_counts.items():
        if count > 0 and weights[bucket] < min_weight:
            weights[bucket] = min_weight
    
    # Normalize weights to sum to 1.0
    weight_sum = sum(weights.values())
    return {bucket: weight / weight_sum for bucket, weight in weights.items()}

def extract_percentage(text: str) -> float:
    """
    Extract percentage value from LLM response
    
    Args:
        text: Text that may contain percentage information
    
    Returns:
        float: Extracted percentage as a value between 0.0 and 1.0
    """
    # Look for percentage patterns
    percentage_patterns = [
        r"(\d{1,3})%",  # 85%
        r"(\d{1,3})\s*percent",  # 85 percent
        r"(\d{1,3}(?:\.\d+)?)%",  # 85.5%
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

# Commenting out the duplicate/incomplete function definition
# def extract_skills_from_text(text: str) -> List[str]:
#     """
#     Extract potential skills from text using improved heuristics and NLP techniques
    
#     Args:
#         text: Text to extract skills from
    
#     Returns:
#         List[str]: List of potential skills
#     """
#     if not text:
#         return []
        
#     # Normalize text for better extraction
#     normalized_text = text.replace('\\r', '\\n').replace('\\t', ' ')
#     skills = []
    
#     # Common technical skills to look for directly
#     common_technical_skills = [
#         # Programming languages
#         "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "Go", "PHP",
#         "Swift", "Kotlin", "Rust", "Scala", "R", "MATLAB", "Perl", "Shell", "PowerShell",
#         "Bash", "Objective-C", "SQL", "PL/SQL", "T-SQL", "Dart", "Groovy", "F#"
#     ]
#     # You may want to continue the function logic here, or remove this duplicate function if not needed.
