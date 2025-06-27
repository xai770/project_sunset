"""
Skill categorization logic for the job expansion pipeline
"""
from typing import List, Dict

def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """
    Categorize skills into different domains
    Args:
        skills: List of skills to categorize
    Returns:
        Dictionary mapping skill categories to lists of skills
    """
    categories = {
        "technical": [
            "python", "javascript", "java", "c++", "c#", "sql", "nosql", 
            "machine learning", "data science", "big data", 
            "aws", "azure", "gcp", "docker", "kubernetes", "react", "angular", "vue",
            "node.js", "django", "flask", "tensorflow", "pytorch", "spark", "hadoop",
            "r", "excel", "power bi", "tableau", "etl", "data warehousing",
            "databricks", "api", "microservices", "rest", "graphql", "git",
            "programming", "coding", "software development", "database"
        ],
        "project_management": [
            "project management", "agile", "scrum", "kanban", "devops", "ci/cd",
            "product management", "program management", "project planning", 
            "resource allocation", "timeline management", "risk assessment",
            "team coordination", "sprint planning", "backlog", "jira", "asana",
            "project delivery", "project execution", "project initiation"
        ],
        "finance": [
            "accounting", "bookkeeping", "financial analysis", "financial reporting",
            "budgeting", "forecasting", "financial modeling", "cost analysis",
            "risk management", "investment analysis", "portfolio management",
            "gaap", "ifrs", "audit", "internal controls", "reconciliation", "ap/ar",
            "payroll", "sap", "oracle", "quickbooks", "xero", "sage", "erp",
            "fp&a", "cash flow", "equity research", "m&a", "financial statements",
            "balance sheet", "income statement", "cash flow statement", "ratios",
            "roi", "roe", "ebitda"
        ],
        "tax": [
            "tax law", "tax preparation", "tax planning", "tax compliance", 
            "irs reporting", "tax return", "corporate taxation", "individual taxation", 
            "estate tax", "gift tax", "international tax", "salt", "sales tax", 
            "property tax", "vat", "gst", "tax credits", "tax deductions", 
            "tax exemptions", "tax treaties", "transfer pricing", "tax audit", 
            "tax dispute", "tax research", "tax technology", "tax transformation",
            "irs circular 230", "taxation of financial products", "partnership taxation",
            "s-corporation", "c-corporation", "excise tax", "withholding tax", "firpta",
            "fatca", "crs", "beps", "dac6", "irc regulations", "tax court", "cpa", 
            "ea", "enrolled agent", "itin", "w-2", "1040", "schedule c", "1065", 
            "1120", "1120s", "706", "709", "depreciation", "amortization", "depletion"
        ],
        "soft_skills": [
            "communication", "leadership", "problem solving", "critical thinking",
            "teamwork", "collaboration", "time management", "adaptability",
            "creativity", "emotional intelligence", "conflict resolution",
            "decision making", "customer service", "presentation", "negotiation", 
            "relationship building", "work ethic", "attention to detail",
            "verbal communication", "written communication", "interpersonal skills",
            "active listening", "flexibility", "organization", "multitasking"
        ]
    }
    result: Dict[str, List[str]] = {k: [] for k in categories}
    result["other"] = []
    for skill in skills:
        skill_lower = skill.lower()
        categorized = False
        for category, category_skills in categories.items():
            if any(category_keyword in skill_lower for category_keyword in category_skills):
                result[category].append(skill)
                categorized = True
                break
        if not categorized:
            result["other"].append(skill)
    return {k: v for k, v in result.items() if v}
