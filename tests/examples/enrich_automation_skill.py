#!/usr/bin/env python3
"""
Example script to enrich the 'automation' skill with proper domain context
to fix the false positive matching with technical automation requirements

This demonstrates how the Skill Domain Relationship framework resolves the issue
of generic skills like "automation" causing false positive matches.
"""

import sys
import os
import json
import logging
from typing import Dict, Any

# Add project root to path to allow importing from scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.skill_decomposer.skill_domain_relationship import enrich_skill, classify_relationship, is_valid_match

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('enrich_automation')

def enrich_automation_skill():
    """
    Enrich the 'automation' skill with proper domain information
    to differentiate it from technical automation
    """
    # Define business process automation skill (what you likely have)
    business_automation = enrich_skill(
        skill_name="Business Process Automation",
        domain="Business Administration",
        knowledge_components=[
            "workflow analysis", 
            "process efficiency", 
            "basic scripting", 
            "Excel macros", 
            "Standard Operating Procedures (SOPs)",
            "business process mapping",
            "documentation"
        ],
        contexts=[
            "office environments", 
            "administrative tasks", 
            "business operations"
        ],
        functions=[
            "improve efficiency", 
            "reduce manual work", 
            "standardize processes",
            "error reduction"
        ],
        proficiency_level=6  # Adjust based on your actual proficiency
    )
    
    logger.info(f"Enriched business automation skill: {business_automation['name']}")
    
    # Define technical deployment automation for comparison
    technical_automation = enrich_skill(
        skill_name="CI/CD Deployment Automation",
        domain="Software Engineering",
        knowledge_components=[
            "CI/CD pipelines", 
            "Jenkins", 
            "GitHub Actions", 
            "Docker", 
            "shell scripting", 
            "version control",
            "build systems",
            "unit testing"
        ],
        contexts=[
            "software development", 
            "DevOps", 
            "cloud infrastructure",
            "application deployment"
        ],
        functions=[
            "automate builds", 
            "continuous integration", 
            "deployment orchestration",
            "test automation"
        ],
        proficiency_level=8  # This is a high level of proficiency needed for this specialized skill
    )
    
    logger.info(f"Defined technical automation skill for comparison: {technical_automation['name']}")
    
    # Test automation framework skill (another example from job requirements)
    test_automation = enrich_skill(
        skill_name="Test Automation Framework Development",
        domain="Software Quality Assurance",
        knowledge_components=[
            "test frameworks", 
            "Selenium", 
            "TestNG/JUnit", 
            "programming languages (Java, Python)", 
            "API testing",
            "behavior-driven development",
            "test case design"
        ],
        contexts=[
            "software testing", 
            "quality assurance", 
            "CI/CD pipelines"
        ],
        functions=[
            "automated testing", 
            "regression testing", 
            "test report generation",
            "test maintenance"
        ],
        proficiency_level=7
    )
    
    logger.info(f"Defined test automation skill for comparison: {test_automation['name']}")
    
    # Analyze relationships between skills
    business_vs_cicd = classify_relationship("Business Process Automation", "CI/CD Deployment Automation")
    logger.info(f"Relationship between business and CI/CD automation: {business_vs_cicd['primary_relationship']}")
    logger.info(f"Compatibility: {business_vs_cicd['compatibility_percentage']}%")
    
    business_vs_test = classify_relationship("Business Process Automation", "Test Automation Framework Development")
    logger.info(f"Relationship between business and test automation: {business_vs_test['primary_relationship']}")
    logger.info(f"Compatibility: {business_vs_test['compatibility_percentage']}%")
    
    # Test match validation for the problem cases from the job report
    cicd_req_valid, cicd_rel = is_valid_match("Deployment Automation (CI/CD)", "Business Process Automation", min_compatibility=0.3)
    logger.info(f"Is business automation a valid match for 'Deployment Automation (CI/CD)'? {cicd_req_valid}")
    logger.info(f"Compatibility: {cicd_rel['compatibility_percentage']}%")
    
    test_req_valid, test_rel = is_valid_match("Test Automation Framework Development", "Business Process Automation", min_compatibility=0.3) 
    logger.info(f"Is business automation a valid match for 'Test Automation Framework Development'? {test_req_valid}")
    logger.info(f"Compatibility: {test_rel['compatibility_percentage']}%")
    
    return {
        "business_automation": business_automation,
        "technical_automation": technical_automation,
        "test_automation": test_automation,
        "relationships": {
            "business_vs_cicd": business_vs_cicd,
            "business_vs_test": business_vs_test,
        },
        "match_validations": {
            "cicd_requirement": cicd_req_valid,
            "cicd_compatibility": cicd_rel['compatibility_percentage'],
            "test_requirement": test_req_valid,
            "test_compatibility": test_rel['compatibility_percentage'],
        }
    }

if __name__ == "__main__":
    print("Enriching 'automation' skill with domain context...")
    result = enrich_automation_skill()
    
    print("\nResults Summary:")
    print(f"- Business Process Automation defined (Proficiency: {result['business_automation']['proficiency_level']}/10)")
    print(f"- CI/CD Deployment Automation defined for comparison")
    print(f"- Test Automation Framework Development defined for comparison")
    print("\nRelationship Analysis:")
    print(f"- Business vs CI/CD: {result['relationships']['business_vs_cicd']['primary_relationship']}")
    print(f"- Compatibility: {result['relationships']['business_vs_cicd']['compatibility_percentage']}%")
    print(f"- Business vs Test Automation: {result['relationships']['business_vs_test']['primary_relationship']}")
    print(f"- Compatibility: {result['relationships']['business_vs_test']['compatibility_percentage']}%")
    print("\nMatch Validation for Job Requirements:")
    print(f"- 'Deployment Automation (CI/CD)' matches with Business Process Automation? {'Yes' if result['match_validations']['cicd_requirement'] else 'No'}")
    print(f"- Compatibility: {result['match_validations']['cicd_compatibility']}%")
    print(f"- 'Test Automation Framework Development' matches with Business Process Automation? {'Yes' if result['match_validations']['test_requirement'] else 'No'}")
    print(f"- Compatibility: {result['match_validations']['test_compatibility']}%")
    
    print("\nConclusion:")
    if not result['match_validations']['cicd_requirement'] and not result['match_validations']['test_requirement']:
        print("SUCCESS! Using domain-enriched skills prevents false matches between your business automation skills")
        print("and unrelated technical automation requirements.")
    else:
        print("Some matches still happened. We may need to adjust thresholds or enrich skills further.")