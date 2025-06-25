"""
Skill extraction logic for job postings.
"""
import re
from typing import Dict, Any, List

def extract_skills_from_job(job_data: Dict[str, Any]) -> List[str]:
    """
    Extract skills from a job posting
    Args:
        job_data: Job data dictionary
    Returns:
        List of extracted skills
    """
    skills = []
    # Gather all relevant text fields for extraction
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
    combined_text = "\n".join(text_blobs)
    # Define skills by category
    tech_skills = [
        "Python", "JavaScript", "Java", "C++", "C#", "SQL", "NoSQL", 
        "Machine Learning", "Data Science", "Big Data", "Project Management",
        "Agile", "Scrum", "Kanban", "DevOps", "CI/CD", "Cloud Computing", 
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "React", "Angular", "Vue",
        "Node.js", "Django", "Flask", "TensorFlow", "PyTorch", "Spark", "Hadoop",
        "R", "Excel", "Power BI", "Tableau", "ETL", "Data Warehousing",
        "Databricks", "API Development", "Microservices", "REST", "GraphQL"
    ]
    finance_skills = [
        "Accounting", "Bookkeeping", "Financial Analysis", "Financial Reporting",
        "Budgeting", "Forecasting", "Financial Modeling", "Cost Analysis",
        "Risk Management", "Investment Analysis", "Portfolio Management",
        "Tax Preparation", "Tax Planning", "Tax Compliance", "GAAP", "IFRS",
        "Audit", "Internal Controls", "Reconciliation", "AP/AR", "Payroll",
        "SAP", "Oracle", "QuickBooks", "Xero", "Sage", "ERP Systems",
        "FP&A", "Cash Flow Management", "Equity Research", "M&A", "Financial Statements"
    ]
    tax_skills = [
        "Tax Law", "Tax Preparation", "Tax Planning", "Tax Compliance", 
        "IRS Reporting", "Tax Return", "Corporate Taxation", "Individual Taxation", 
        "Estate Tax", "Gift Tax", "International Tax", "SALT", "Sales Tax", 
        "Property Tax", "VAT", "GST", "Tax Credits", "Tax Deductions", 
        "Tax Exemptions", "Tax Treaties", "Transfer Pricing", "Tax Audit", 
        "Tax Dispute", "Tax Research", "Tax Technology", "Tax Transformation",
        "IRS Circular 230", "Taxation of Financial Products", "Partnership Taxation",
        "S-Corporation", "C-Corporation", "Excise Tax", "Withholding Tax", "FIRPTA",
        "FATCA", "CRS", "BEPS", "DAC6", "IRC Regulations", "Tax Court"
    ]
    soft_skills = [
        "Communication", "Leadership", "Problem Solving", "Critical Thinking",
        "Teamwork", "Collaboration", "Time Management", "Adaptability",
        "Creativity", "Emotional Intelligence", "Conflict Resolution",
        "Decision Making", "Customer Service", "Presentation Skills",
        "Negotiation", "Relationship Building", "Work Ethic", "Attention to Detail"
    ]
    all_skills = tech_skills + finance_skills + tax_skills + soft_skills
    for skill in all_skills:
        if skill.lower() in combined_text.lower():
            skills.append(skill)
    tax_finance_indicators = [
        "CPA", "EA", "Enrolled Agent", "ITIN", "Form W-2", "Form 1040", 
        "Schedule C", "Form 1065", "Form 1120", "Form 1120S", "Form 706", 
        "Form 709", "Charitable Contribution", "Section 179", "Section 1031", 
        "Depreciation", "Amortization", "Depletion", "AMT", "Tax-Exempt", 
        "Tax Evasion", "Tax Avoidance", "Tax Liability", "Tax Basis",
        "Financial Statement Analysis", "Balance Sheet", "Income Statement",
        "Cash Flow Statement", "Financial Ratios", "ROI", "ROE", "EBITDA"
    ]
    for term in tax_finance_indicators:
        if term.lower() in combined_text.lower():
            skills.append(term)
    for field in ["requirements", "technologies", "required_skills"]:
        if field in job_data and isinstance(job_data[field], list):
            for item in job_data[field]:
                skills.append(item)
    if "concise_description" in job_data and isinstance(job_data["concise_description"], dict):
        if "skills" in job_data["concise_description"]:
            if isinstance(job_data["concise_description"]["skills"], list):
                for skill in job_data["concise_description"]["skills"]:
                    skills.append(skill)
            elif isinstance(job_data["concise_description"]["skills"], str):
                skill_list = job_data["concise_description"]["skills"].split(",")
                for skill in skill_list:
                    clean_skill = skill.strip()
                    if clean_skill:
                        skills.append(clean_skill)
    return list(set(skills))

"""
Skill extraction logic for the job expansion pipeline
"""
def extract_skills_from_job_expansion(job_data: Dict[str, Any]) -> List[str]:
    """
    Extract skills from a job posting for the job expansion pipeline
    Args:
        job_data: Job data dictionary
    Returns:
        List of extracted skills
    """
    skills = []
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
    combined_text = "\n".join(text_blobs)
    tech_skills = [
        "Python", "JavaScript", "Java", "C++", "C#", "SQL", "NoSQL", 
        "Machine Learning", "Data Science", "Big Data", "Project Management",
        "Agile", "Scrum", "Kanban", "DevOps", "CI/CD", "Cloud Computing", 
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "React", "Angular", "Vue",
        "Node.js", "Django", "Flask", "TensorFlow", "PyTorch", "Spark", "Hadoop",
        "R", "Excel", "Power BI", "Tableau", "ETL", "Data Warehousing",
        "Databricks", "API Development", "Microservices", "REST", "GraphQL"
    ]
    finance_skills = [
        "Accounting", "Bookkeeping", "Financial Analysis", "Financial Reporting",
        "Budgeting", "Forecasting", "Financial Modeling", "Cost Analysis",
        "Risk Management", "Investment Analysis", "Portfolio Management",
        "Tax Preparation", "Tax Planning", "Tax Compliance", "GAAP", "IFRS",
        "Audit", "Internal Controls", "Reconciliation", "AP/AR", "Payroll",
        "SAP", "Oracle", "QuickBooks", "Xero", "Sage", "ERP Systems",
        "FP&A", "Cash Flow Management", "Equity Research", "M&A", "Financial Statements"
    ]
    tax_skills = [
        "Tax Law", "Tax Preparation", "Tax Planning", "Tax Compliance", 
        "IRS Reporting", "Tax Return", "Corporate Taxation", "Individual Taxation", 
        "Estate Tax", "Gift Tax", "International Tax", "SALT", "Sales Tax", 
        "Property Tax", "VAT", "GST", "Tax Credits", "Tax Deductions", 
        "Tax Exemptions", "Tax Treaties", "Transfer Pricing", "Tax Audit", 
        "Tax Dispute", "Tax Research", "Tax Technology", "Tax Transformation",
        "IRS Circular 230", "Taxation of Financial Products", "Partnership Taxation",
        "S-Corporation", "C-Corporation", "Excise Tax", "Withholding Tax", "FIRPTA",
        "FATCA", "CRS", "BEPS", "DAC6", "IRC Regulations", "Tax Court"
    ]
    soft_skills = [
        "Communication", "Leadership", "Problem Solving", "Critical Thinking",
        "Teamwork", "Collaboration", "Time Management", "Adaptability",
        "Creativity", "Emotional Intelligence", "Conflict Resolution",
        "Decision Making", "Customer Service", "Presentation Skills",
        "Negotiation", "Relationship Building", "Work Ethic", "Attention to Detail"
    ]
    all_skills = tech_skills + finance_skills + tax_skills + soft_skills
    for skill in all_skills:
        if skill.lower() in combined_text.lower():
            skills.append(skill)
    tax_finance_indicators = [
        "CPA", "EA", "Enrolled Agent", "ITIN", "Form W-2", "Form 1040", 
        "Schedule C", "Form 1065", "Form 1120", "Form 1120S", "Form 706", 
        "Form 709", "Charitable Contribution", "Section 179", "Section 1031", 
        "Depreciation", "Amortization", "Depletion", "AMT", "Tax-Exempt", 
        "Tax Evasion", "Tax Avoidance", "Tax Liability", "Tax Basis",
        "Financial Statement Analysis", "Balance Sheet", "Income Statement",
        "Cash Flow Statement", "Financial Ratios", "ROI", "ROE", "EBITDA"
    ]
    for term in tax_finance_indicators:
        if term.lower() in combined_text.lower():
            skills.append(term)
    for field in ["requirements", "technologies", "required_skills"]:
        if field in job_data and isinstance(job_data[field], list):
            for item in job_data[field]:
                skills.append(item)
    if "concise_description" in job_data and isinstance(job_data["concise_description"], dict):
        if "skills" in job_data["concise_description"]:
            if isinstance(job_data["concise_description"]["skills"], list):
                for skill in job_data["concise_description"]["skills"]:
                    skills.append(skill)
            elif isinstance(job_data["concise_description"]["skills"], str):
                skill_list = job_data["concise_description"]["skills"].split(",")
                for skill in skill_list:
                    clean_skill = skill.strip()
                    if clean_skill:
                        skills.append(clean_skill)
    return list(set(skills))
