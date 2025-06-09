"""
Skill category and compatibility logic (extracted from enhanced_skill_matcher.py)
"""
from typing import Dict, Any, List

# Skill category mapping with enhanced categorization
SKILL_CATEGORIES = {
    "Technical": [
        "IT_Technical", "Software_Development", "Data_Science", "Engineering", 
        "Programming_Languages", "Cloud_Services", "Databases", "DevOps",
        "Software_Engineering", "Machine_Learning", "AI", "Artificial_Intelligence",
        "Backend", "Frontend", "Web_Development", "Mobile_Development", "DevOps",
        "System_Administration", "Network", "Security", "Cybersecurity", "Infrastructure"
    ],
    "Management": [
        "Leadership_and_Management", "Project_Management", "Team_Leadership", 
        "Business_Management", "Strategic_Planning", "Program_Management",
        "Portfolio_Management", "People_Management", "Executive_Leadership",
        "Change_Management", "Organizational_Development", "Resource_Management"
    ],
    "Domain_Knowledge": [
        "Finance", "Banking", "Insurance", "Healthcare", "Manufacturing", 
        "Retail", "Telecom", "Energy", "Legal", "Education", "Government",
        "Pharmaceuticals", "Biotechnology", "Real_Estate", "Hospitality",
        "Transportation", "Logistics", "Agriculture", "Media", "Entertainment"
    ],
    "Procurement": [
        "Sourcing_and_Procurement", "Vendor_Management", "Contract_Management", 
        "Supply_Chain", "Purchasing", "Supplier_Relationship_Management",
        "Strategic_Sourcing", "Inventory_Management", "Logistics", "Distribution"
    ],
    "Soft_Skills": [
        "Communication", "Teamwork", "Problem_Solving", "Critical_Thinking", 
        "Adaptability", "Time_Management", "Collaboration", "Interpersonal_Skills",
        "Negotiation", "Conflict_Resolution", "Emotional_Intelligence", 
        "Leadership", "Decision_Making", "Creativity", "Innovation"
    ],
    "Analytics": [
        "Data_Analysis", "Business_Intelligence", "Reporting", "Statistics",
        "Forecasting", "Predictive_Analytics", "Data_Visualization", "SQL",
        "Quantitative_Analysis", "Market_Research", "Competitive_Analysis"
    ]
}

COMPATIBLE_CATEGORIES = {
    "Technical": ["Technical", "Management", "Analytics"],
    "Management": ["Management", "Technical", "Domain_Knowledge", "Soft_Skills", "Procurement"],
    "Domain_Knowledge": ["Domain_Knowledge", "Management", "Analytics"],
    "Procurement": ["Procurement", "Management", "Domain_Knowledge"],
    "Soft_Skills": ["Soft_Skills", "Management"],
    "Analytics": ["Analytics", "Technical", "Domain_Knowledge"]
}

def get_skill_category(skill_data: Dict[str, Any]) -> str:
    category = skill_data.get("category", "")
    skill_name = skill_data.get("name", "").lower()
    description = skill_data.get("description", "").lower()
    domains = skill_data.get("domains", [])
    for high_level, specific_categories in SKILL_CATEGORIES.items():
        if any(specific in category for specific in specific_categories):
            return high_level
    keywords_by_category = {
        "Technical": ["programming", "software", "development", "coding", "engineer", 
                     "technical", "IT", "database", "frontend", "backend", "fullstack",
                     "algorithm", "API", "architecture"],
        "Management": ["management", "leadership", "strategy", "executive", "direct",
                      "oversee", "organize", "coordinate", "supervise", "administrate"],
        "Analytics": ["analytics", "analysis", "data", "statistics", "reporting", 
                     "metrics", "measure", "research", "evaluation", "assessment"],
        "Soft_Skills": ["communication", "interpersonal", "teamwork", "collaboration",
                       "attitude", "adaptability", "flexibility", "creativity"],
        "Domain_Knowledge": ["industry", "sector", "field", "expertise", "specialist",
                           "professional", "domain", "knowledge"]
    }
    text_to_search = f"{skill_name} {description} {' '.join(domains)}".lower()
    matches = {}
    for category, keywords in keywords_by_category.items():
        count = sum(1 for keyword in keywords if keyword.lower() in text_to_search)
        if count > 0:
            matches[category] = count
    if matches:
        return max(matches.items(), key=lambda x: x[1])[0]  # type: ignore
    return "General"

def should_compare_skills(job_skill_category: str, cv_skill_category: str) -> bool:
    if job_skill_category == cv_skill_category:
        return True
    compatible_categories = COMPATIBLE_CATEGORIES.get(job_skill_category, [])
    return cv_skill_category in compatible_categories
