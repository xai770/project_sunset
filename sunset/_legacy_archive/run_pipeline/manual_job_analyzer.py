#!/usr/bin/env python3
"""
Manual Job Skill Analyzer

This script analyzes specific job positions against your skill profile
without relying on existing SDR skills.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("job_skill_analyzer")

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
postings_DIR = PROJECT_ROOT / "data" / "postings"
YOUR_SKILLS_FILE = PROJECT_ROOT / "docs" / "skill_matching" / "gershon-skills-categorized.json"

def load_job_data(job_id: str) -> Dict[str, Any]:
    """Load job data from file"""
    job_path = postings_DIR / f"job{job_id}.json"
    try:
        with open(job_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load job file {job_path}: {e}")
        return {}

def load_your_skills() -> Dict[str, Any]:
    """Load your skills profile"""
    try:
        with open(YOUR_SKILLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load skills file {YOUR_SKILLS_FILE}: {e}")
        return {}

def extract_key_job_skills(job_data: Dict[str, Any]) -> List[str]:
    """Extract key skills from job description"""
    description = job_data.get("web_details", {}).get("concise_description", "")
    responsibilities = job_data.get("web_details", {}).get("structured_description", {}).get("responsibilities", [])
    requirements = job_data.get("web_details", {}).get("structured_description", {}).get("requirements", [])
    
    # Sample key terms for IT Application Owner
    key_terms = [
        "application management",
        "governance",
        "risk management",
        "compliance",
        "IT operations",
        "system stability",
        "stakeholder management",
        "single point of contact",
        "subject matter expert",
        "cloud platform",
        "application architecture",
        "security",
        "access management",
        "documentation",
        "audits"
    ]
    
    return key_terms

def evaluate_job_match(job_id: str) -> None:
    """Evaluate match between job and your skills"""
    # Load data
    job_data = load_job_data(job_id)
    your_skills = load_your_skills()
    
    if not job_data or not your_skills:
        return
    
    # Get job details
    job_title = job_data.get("web_details", {}).get("position_title", "Unknown Title")
    
    # Extract job skills
    job_skills = extract_key_job_skills(job_data)
    
    # Get your skill categories
    skill_categories = your_skills.get("skill_categories", {})
    
    # Analyze match with your skills
    matching_skills = []
    
    print(f"\nAnalyzing match for job {job_id}: {job_title}\n")
    print("Key job requirements:")
    for skill in job_skills:
        print(f"- {skill}")
    
    print("\nYour matching skills by category:")
    for category, skills in skill_categories.items():
        category_matches = []
        
        for skill_data in skills:
            skill_name = skill_data.get("name")
            skill_level = skill_data.get("level", 0)
            
            # Check if this skill is relevant for the job
            for job_skill in job_skills:
                if skill_name.lower() in job_skill.lower() or job_skill.lower() in skill_name.lower():
                    category_matches.append({
                        "skill": skill_name,
                        "level": skill_level,
                        "job_requirement": job_skill
                    })
                    matching_skills.append(skill_name)
                    break
        
        if category_matches:
            print(f"\n{category}:")
            for match in category_matches:
                print(f"- {match['skill']} (Level: {match['level']}/5) -> matches job requirement: {match['job_requirement']}")
    
    # Find additional relevant skills that might not directly match keywords
    print("\nAdditional relevant skills:")
    relevant_skills = [
        ("IT_Management", ["Enterprise IT Governance", "Software License Management", "IT Project Management"]),
        ("Leadership_and_Management", ["Team Leadership", "Stakeholder Management", "Risk Management", "Process Design and Implementation"]),
        ("Sourcing_and_Procurement", ["Contract Negotiation", "Vendor Relationship Management"]),
        ("Domain_Knowledge", ["Enterprise IT", "Financial Services Industry", "Regulatory Compliance"])
    ]
    
    for category, skills in relevant_skills:
        category_skills = skill_categories.get(category, [])
        for skill_name in skills:
            # Check if we already counted this skill
            if skill_name in matching_skills:
                continue
                
            # Find the skill in your profile
            for skill_data in category_skills:
                if skill_data.get("name") == skill_name:
                    print(f"- {skill_name} (Level: {skill_data.get('level', 0)}/5) - Relevant for this position")
                    matching_skills.append(skill_name)
                    break
    
    # Calculate match percentage (simplified)
    essential_skills_count = 8  # Number of "must-have" skills for this position
    match_percentage = min(100, len(matching_skills) / essential_skills_count * 100)
    
    print(f"\nEstimated match percentage: {match_percentage:.1f}%")
    print("(Based on overlap between your skills and key job requirements)")
    
    print("\nConclusion:")
    if match_percentage >= 70:
        print("Your profile is a STRONG MATCH for this position.")
    elif match_percentage >= 50:
        print("Your profile is a GOOD MATCH for this position.")
    else:
        print("Your profile shows SOME RELEVANT SKILLS for this position.")

def main():
    """Main function"""
    # Analyze IT Application Owner position
    evaluate_job_match("53554")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
