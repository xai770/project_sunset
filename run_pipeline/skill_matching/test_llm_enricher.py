#!/usr/bin/env python3
"""
Test script for the Enhanced SDR Skill Analysis

This script tests the enhanced SDR skill analysis module with a set of sample skills
across different domains to validate its effectiveness.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from run_pipeline.skill_matching.skill_analyzer import SkillAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_sdr_enricher")

# Output directory
OUTPUT_DIR = os.path.join(project_root, 'docs', 'skill_matching')

def main():
    """Main function to test the Enhanced SDR Skill Analysis"""
    # Create the analyzer
    analyzer = SkillAnalyzer()
    
    # Sample skills across domains
    test_skills = [
        {"name": "Python Programming", "category": "IT_Technical"},
        {"name": "Project Management", "category": "IT_Management"},
        {"name": "Contract Negotiation", "category": "Sourcing_and_Procurement"},
        {"name": "Team Leadership", "category": "Leadership_and_Management"},
        {"name": "Data Analysis", "category": "Analysis_and_Reporting"},
        {"name": "Banking Regulations", "category": "Domain_Knowledge"}
    ]
    
    # Process each skill and collect results
    enriched_skills = []
    for skill in test_skills:
        logger.info(f"Testing enrichment for: {skill['name']}")
        try:
            # Use the enhanced SDR pipeline approach instead of deprecated LLM enricher
            enriched = analyzer.create_enriched_skill_definition(skill["name"], use_llm=False)
            enriched_skills.append(enriched)
            
            # Print a summary of the enrichment
            logger.info(f"Enrichment successful for {skill['name']}:")
            logger.info(f"- Knowledge components: {len(enriched.get('knowledge_components', []))} items")
            logger.info(f"- Contexts: {len(enriched.get('contexts', []))} items")
            logger.info(f"- Related skills: {len(enriched.get('related_skills', []))} items")
        except Exception as e:
            logger.error(f"Error processing {skill['name']}: {e}")
    
    # Save the results
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, 'sdr_enriched_skills_test.json')
    
    with open(output_file, 'w') as f:
        json.dump(enriched_skills, f, indent=2)
    
    logger.info(f"Test results saved to {output_file}")
    
    # Print statistics
    logger.info(f"Test completed. Successfully enriched {len(enriched_skills)} out of {len(test_skills)} skills.")

if __name__ == "__main__":
    main()
