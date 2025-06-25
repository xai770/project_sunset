#!/usr/bin/env python3
"""
Domain Analyzer module for job matching.

This module is responsible for extracting domain-specific requirements
and determining the job domain from job descriptions.
"""
import re
from typing import List

def get_domain_specific_requirements(job_description: str) -> List[str]:
    """
    Extract domain-specific requirements from a job description.
    
    Args:
        job_description: The job description text
        
    Returns:
        A list of domain-specific requirements found in the job description
    """
    # Define common domain-specific requirement indicators
    domain_requirement_indicators = [
        r"(\d+)[-\s](\d+) years? (?:of )?experience (?:in|with) ([^,.]+)",  # e.g., "5-7 years experience in finance"
        r"knowledge of ([^,.]+)",  # e.g., "knowledge of IFRS standards"
        r"expertise (?:in|with) ([^,.]+)",  # e.g., "expertise in risk management"
        r"background (?:in|with) ([^,.]+)",  # e.g., "background in banking"
        r"specialist (?:in|with) ([^,.]+)",  # e.g., "specialist in cyber security"
        r"proficiency (?:in|with) ([^,.]+)",  # e.g., "proficiency in financial modeling"
        r"understanding of ([^,.]+)",  # e.g., "understanding of regulatory frameworks"
        r"familiarity with ([^,.]+)",  # e.g., "familiarity with German banking regulations"
        r"experience (?:in|with) ([^,.]+)",  # e.g., "experience in project management"
        r"skills (?:in|with) ([^,.]+)",  # e.g., "skills in data analysis"
        r"certification in ([^,.]+)",  # e.g., "certification in project management"
        r"degree in ([^,.]+)",  # e.g., "degree in computer science"
    ]
    
    domain_specific_requirements = []
    
    # Check each pattern for domain-specific requirements
    for pattern in domain_requirement_indicators:
        matches = re.finditer(pattern, job_description, re.IGNORECASE)
        for match in matches:
            # If the pattern has experience years group, extract it with the requirement
            if len(match.groups()) > 2 and match.group(1) and match.group(2):
                years_min = match.group(1)
                years_max = match.group(2)
                requirement = match.group(3).strip().lower()
                if int(years_min) >= 3:  # Consider as domain-specific if 3+ years required
                    domain_specific_requirements.append(f"{requirement} ({years_min}-{years_max} years)")
            elif len(match.groups()) >= 1:
                requirement = match.group(1).strip().lower()
                domain_specific_requirements.append(requirement)
    
    # Add industry-specific keywords if they appear in the job description
    industry_keywords = [
        "financial services", "banking", "investment", "insurance", "healthcare", 
        "pharmaceuticals", "manufacturing", "automotive", "aerospace", "defense",
        "energy", "oil and gas", "utilities", "telecommunications", "technology",
        "retail", "consumer goods", "media", "entertainment", "hospitality",
        "real estate", "construction", "legal", "consulting", "education",
        "government", "nonprofit", "transportation", "logistics"
    ]
    
    for keyword in industry_keywords:
        if keyword.lower() in job_description.lower():
            domain_specific_requirements.append(f"{keyword} industry knowledge")
    
    return list(set(domain_specific_requirements))  # Remove duplicates

def extract_job_domain(job_description: str) -> str:
    """
    Extract the primary domain/industry from a job description.
    
    Args:
        job_description: The job description text
        
    Returns:
        The primary domain/industry found in the job description
    """
    # Define common industry domains
    domains = {
        "finance": ["banking", "investment", "financial", "asset management", "wealth management", "trader", "trading"],
        "technology": ["software", "IT", "programming", "developer", "coder", "engineering", "tech ", "technology"],
        "healthcare": ["health", "medical", "clinical", "hospital", "patient", "doctor", "nurse", "pharma"],
        "manufacturing": ["manufacturing", "production", "factory", "assembly", "industrial", "fabrication"],
        "consulting": ["consulting", "consultant", "advisory", "strategy consultant", "management consult"],
        "legal": ["legal", "law", "attorney", "lawyer", "counsel", "compliance", "regulatory"],
        "marketing": ["marketing", "advertising", "brand", "market research", "digital marketing"],
        "retail": ["retail", "shop", "store", "merchandising", "e-commerce", "customer service"],
        "education": ["education", "teaching", "academic", "school", "university", "training", "instructor"],
        "human resources": ["HR", "human resources", "recruitment", "talent", "people management"]
    }
    
    # Count occurrences of domain keywords
    domain_counts = {domain: 0 for domain in domains}
    
    for domain, keywords in domains.items():
        for keyword in keywords:
            domain_counts[domain] += len(re.findall(r'\b' + re.escape(keyword) + r'\b', job_description, re.IGNORECASE))
    
    # Find the domain with the most keyword matches
    primary_domain = max(domain_counts.items(), key=lambda x: x[1])
    
    # If there are no clear matches, return "unclassified"
    if primary_domain[1] == 0:
        return "unclassified"
    
    return primary_domain[0]

def analyze_domain_knowledge_gaps(domain_assessment: str) -> tuple:
    """
    Analyze domain knowledge gaps in the assessment text.
    
    Args:
        domain_assessment: The domain knowledge assessment text from LLM response
        
    Returns:
        A tuple of (has_critical_domain_gap, has_domain_requirements, domain_gap_severity, domain_req_percentage)
    """
    if not domain_assessment:
        return False, False, 0, 0
        
    # Critical keywords indicating domain knowledge gaps
    critical_gap_indicators = [
        "lacks domain-specific knowledge", 
        "missing industry experience",
        "no direct experience in",
        "lacks experience in the",
        "does not demonstrate",
        "significant gap in",
        "would take 3+ years",
        "does not show experience",
        "missing domain knowledge",
        "lack of sector-specific experience",
        "industry knowledge is absent",
        "does not have specific experience",
        "specialized knowledge that the CV doesn't show",
        "required expertise is missing",
        "limited exposure to"
    ]
    
    # Domain requirement keywords
    domain_requirements = [
        "alternative products",
        "asset classes",
        "investment products",
        "asset management",
        "financial products",
        "regulatory framework",
        "market trends",
        "industry-specific",
        "sector-specific",
        "specialized technical skills",
        "requires extensive experience",
        "domain-specific knowledge",
        "specific regulatory framework",
        "industry standards",
        "market-specific"
    ]
    
    # Check if any indicator suggests a critical domain knowledge gap
    has_critical_domain_gap = any(indicator.lower() in domain_assessment.lower() for indicator in critical_gap_indicators)
    
    # Check if assessment mentions critical domain requirements
    has_domain_requirements = any(req.lower() in domain_assessment.lower() for req in domain_requirements)
    
    # Calculate severity of domain knowledge gap
    domain_gap_severity = 0
    if has_critical_domain_gap:
        domain_gap_severity += 2
    if has_domain_requirements:
        domain_gap_severity += 1
    
    # Check percentage of domain requirements mentioned in assessment
    domain_req_count = sum(1 for req in domain_requirements if req.lower() in domain_assessment.lower())
    domain_req_percentage = domain_req_count / len(domain_requirements) * 100
    
    return has_critical_domain_gap, has_domain_requirements, domain_gap_severity, domain_req_percentage
