"""
Domain Classification Specialist LLM v1.1
=======================================

LLM-powered specialist for classifying job domains and assessing domain match.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def classify_job_domain_llm(job_description: str, job_id: str = "unknown") -> Dict[str, Any]:
    """
    LLM-powered domain classification specialist
    
    Returns structured domain classification with analysis details
    """
    logger.info(f"🤖 Running LLM domain classification for job {job_id}")
    
    # Mock LLM analysis based on job description keywords
    description_lower = job_description.lower()
    
    # Simple keyword-based classification for testing
    if any(keyword in description_lower for keyword in ['software', 'python', 'java', 'react', 'developer', 'engineer', 'coding', 'programming']):
        domain = 'technology'
        confidence = 92.0  # Already as percentage
    elif any(keyword in description_lower for keyword in ['finance', 'banking', 'accounting', 'financial', 'investment']):
        domain = 'finance'
        confidence = 88.0
    elif any(keyword in description_lower for keyword in ['marketing', 'sales', 'advertising', 'brand', 'campaign']):
        domain = 'marketing'
        confidence = 85.0
    elif any(keyword in description_lower for keyword in ['legal', 'lawyer', 'attorney', 'compliance', 'law']):
        domain = 'legal'
        confidence = 90.0
    elif any(keyword in description_lower for keyword in ['healthcare', 'medical', 'nurse', 'doctor', 'clinical']):
        domain = 'healthcare'
        confidence = 89.0
    else:
        domain = 'general'
        confidence = 75.0
    
    return {
        'primary_domain_classification': domain,
        'confidence': confidence,
        'should_proceed_with_evaluation': True,
        'analysis_details': {
            'domain_reasoning': f"Classified as {domain} based on job description keywords",
            'domain_requirements': [f"{domain} expertise", "relevant experience"],
            'domain_gaps': []
        }
    }
