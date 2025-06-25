"""
Skill importance analysis logic for the job expansion pipeline
"""
from typing import Dict, Any, List

def analyze_skill_importance(job_data: Dict[str, Any], skills: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Analyze the importance of skills in a job posting
    Args:
        job_data: Job data dictionary
        skills: List of extracted skills
    Returns:
        Dictionary with skill importance analysis
    """
    result: Dict[str, Dict[str, Any]] = {}
    if not skills:
        return result
    text_blobs = []
    if "job_description" in job_data:
        text_blobs.append(job_data["job_description"])
    if "web_details" in job_data:
        wd = job_data["web_details"]
        if "structured_description" in wd:
            sd = wd["structured_description"]
            if isinstance(sd, dict):
                if "title" in sd:
                    text_blobs.append(str(sd["title"]))
                if "responsibilities" in sd and isinstance(sd["responsibilities"], list):
                    text_blobs.extend([str(r) for r in sd["responsibilities"]])
                if "requirements" in sd and isinstance(sd["requirements"], list):
                    text_blobs.extend([str(r) for r in sd["requirements"]])
    if "web_details" in job_data and "concise_description" in job_data["web_details"]:
        text_blobs.append(str(job_data["web_details"]["concise_description"]))
    if "concise_description" in job_data and isinstance(job_data["concise_description"], str):
        text_blobs.append(job_data["concise_description"])
    job_text = "\n".join(text_blobs).lower()
    job_title = job_data.get("job_title", "").lower()
    for skill in skills:
        skill_lower = skill.lower()
        occurrences = job_text.count(skill_lower)
        in_title = skill_lower in job_title
        in_requirements = False
        importance = 1
        if "web_details" in job_data:
            wd = job_data["web_details"]
            if "structured_description" in wd:
                sd = wd["structured_description"]
                if isinstance(sd, dict) and "requirements" in sd and isinstance(sd["requirements"], list):
                    in_requirements = any(skill_lower in str(req).lower() for req in sd["requirements"])
        elif occurrences > 1:
            importance += 1
        if in_title:
            importance += 1
        if in_requirements:
            importance += 1
        importance = min(5, importance)
        result[skill] = {
            "occurrences": occurrences,
            "in_title": in_title,
            "in_requirements": in_requirements,
            "importance_score": importance,
            "importance_level": ["Very Low", "Low", "Medium", "High", "Very High"][importance - 1]
        }
    return result
