#!/usr/bin/env python3
"""
Test script for LLM domain extraction for automation skills using the 
Skill Domain Relationship framework.

This tests how the LLM extracts domain-specific information from different
types of automation skills, demonstrating how this approach addresses the
false positive matching problem.
"""

import sys
import os
import json
import logging
from typing import Dict, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.skill_decomposer.skill_domain_relationship import enrich_skill, classify_relationship, is_valid_match
from scripts.utils.llm_client import call_ollama_api, get_available_models

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_automation_domain')

def extract_domain_with_llm(skill_name: str, model: str = "llama3.2") -> Dict[str, Any]:
    """Use LLM to extract domain information for a skill
    
    Args:
        skill_name: The name of the skill
        model: The model to use
        
    Returns:
        Dictionary with domain information
    """
    logger.info(f"Extracting domain for '{skill_name}' using {model}")
    
    prompt = f"""You are a professional skill domain analyzer. Your task is to extract the key components of the following skill:

SKILL: {skill_name}

Please analyze this skill and provide the following information in JSON format:
{{
  "name": "{skill_name}",
  "domain": "The professional domain this skill belongs to",
  "knowledge_components": [
    "List 5-8 specific knowledge areas required for this skill"
  ],
  "contexts": [
    "List 3-5 environments where this skill is typically applied"
  ],
  "functions": [
    "List 3-5 primary purposes or functions of this skill"
  ],
  "proficiency_level": "A number from 1-10 representing typical expertise level required"
}}

Focus on being precise and domain-specific in your analysis. Avoid generic descriptions.
Provide only the JSON output without additional commentary."""
    
    try:
        response = call_ollama_api(prompt, model=model, temperature=0.2)
        
        if not response:
            logger.warning(f"Empty response for {skill_name}")
            return None
            
        # Parse JSON response
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response
                
        domain_info = json.loads(json_str)
        
        # Convert proficiency level to int
        if "proficiency_level" in domain_info:
            try:
                domain_info["proficiency_level"] = int(domain_info["proficiency_level"])
            except (ValueError, TypeError):
                # Default to 5 if not a valid integer
                domain_info["proficiency_level"] = 5
                
        logger.info(f"Successfully extracted domain for '{skill_name}'")
        return domain_info
        
    except Exception as e:
        logger.error(f"Error extracting domain for '{skill_name}': {e}")
        return None

def compare_automation_skills(model: str = "llama3.2"):
    """Compare different automation skills using LLM domain extraction
    
    Args:
        model: The model to use
    """
    # Test skills
    automation_skills = [
        "automation",  # General automation
        "Business Process Automation",  # Office/business automation
        "CI/CD Deployment Automation",  # Technical automation
        "Test Automation Framework Development",  # QA automation
        "Industrial Automation",  # Factory automation
        "Marketing Automation"  # Marketing automation
    ]
    
    # Extract domains for each skill
    domains = {}
    for skill in automation_skills:
        domain_info = extract_domain_with_llm(skill, model)
        if domain_info:
            # Enrich skill with domain information
            enriched_skill = enrich_skill(
                skill_name=domain_info["name"],
                domain=domain_info["domain"],
                knowledge_components=domain_info["knowledge_components"],
                contexts=domain_info["contexts"],
                functions=domain_info["functions"],
                proficiency_level=domain_info["proficiency_level"]
            )
            domains[skill] = domain_info
            
    print("\n===== DOMAIN EXTRACTION RESULTS =====\n")
    
    # Print domain information for each skill
    for skill, info in domains.items():
        print(f"SKILL: {skill}")
        print(f"Domain: {info['domain']}")
        print(f"Knowledge Components: {', '.join(info['knowledge_components'][:3])}...")
        print(f"Contexts: {', '.join(info['contexts'][:2])}...")
        print(f"Functions: {', '.join(info['functions'][:2])}...")
        print(f"Proficiency Level: {info['proficiency_level']}")
        print()
        
    print("===== RELATIONSHIP ANALYSIS =====\n")
    
    # Compare general automation with specialized automation fields
    general = "automation"
    for skill in automation_skills[1:]:  # Skip the general automation
        if skill in domains and general in domains:
            relationship = classify_relationship(general, skill)
            print(f"{general} vs {skill}:")
            print(f"  Relationship: {relationship['primary_relationship']}")
            print(f"  Compatibility: {relationship['compatibility_percentage']}%")
            print(f"  Knowledge Overlap: {relationship['metrics']['knowledge_overlap'] * 100:.1f}%")
            print(f"  Context Overlap: {relationship['metrics']['context_overlap'] * 100:.1f}%")
            print(f"  Function Overlap: {relationship['metrics']['function_overlap'] * 100:.1f}%")
            print()
            
    print("===== MATCH VALIDATION =====\n")
    
    # Test if generic automation matches specialized requirements
    requirements = [
        "Deployment Automation (CI/CD)",
        "Test Automation Framework Development",
        "RPA (Robotic Process Automation)",
        "Marketing Campaign Automation"
    ]
    
    for req in requirements:
        is_valid, rel_data = is_valid_match(req, "automation", min_compatibility=0.3)
        print(f"'{req}' matches with 'automation'? {'Yes' if is_valid else 'No'}")
        print(f"  Compatibility: {rel_data['compatibility_percentage']}%")
        print(f"  Relationship: {rel_data['primary_relationship']}")
        print()
        
    # Save detailed results to file
    results = {
        "domains": domains,
        "timestamp": datetime.now().isoformat(),
        "model": model
    }
    
    reports_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "reports"
    )
    os.makedirs(reports_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(reports_dir, f"automation_domain_analysis_{timestamp}.json")
    
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Detailed results saved to: {filepath}")

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description="Test LLM domain extraction for automation skills")
    parser.add_argument(
        "--model",
        default="llama3.2",
        help="Model to use for domain extraction (default: llama3.2)"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models and exit"
    )
    
    args = parser.parse_args()
    
    if args.list_models:
        models = get_available_models()
        if models:
            print("Available models:")
            for model in models:
                print(f"  - {model}")
        else:
            print("No models available or could not connect to Ollama")
        return
    
    print(f"Testing domain extraction with model: {args.model}")
    compare_automation_skills(args.model)
    
if __name__ == "__main__":
    main()