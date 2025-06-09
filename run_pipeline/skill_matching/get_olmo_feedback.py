#!/usr/bin/env python3
"""
OLMo2 Feedback on SDR Implementation

This script queries OLMo2 for feedback on the SDR implementation and skill enrichment process.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from run_pipeline.utils.llm_client import call_ollama_api, get_olmo_client

# Try to import LLM Factory for quality-controlled processing
try:
    from llm_factory.specialist_registry import SpecialistRegistry
    from llm_factory.quality_control import QualityController
    LLM_FACTORY_AVAILABLE = True
except ImportError:
    LLM_FACTORY_AVAILABLE = False

# Helper Functions
def load_json_file(filepath):
    """Load and return JSON data from a file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)  # type: ignore
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def get_sdr_summary():
    """Generate a summary of the SDR implementation for OLMo"""
    enriched_skills_path = os.path.join(project_root, 'docs', 'skill_matching', 'enriched_skills.json')
    relationships_path = os.path.join(project_root, 'docs', 'skill_matching', 'skill_relationships.json')
    
    enriched_skills = load_json_file(enriched_skills_path) or []
    relationships = load_json_file(relationships_path) or {}
    
    # Count relationship types
    relationship_counts: Dict[str, int] = {}
    for skill1, relations in relationships.items():
        for skill2, relation_data in relations.items():
            rel_type = relation_data.get('relationship', 'Unknown')
            relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1
    
    # Create a summary of the implementation
    summary: Dict[str, Any] = {
        "enriched_skills_count": len(enriched_skills),
        "domains_representation": {},
        "relationship_counts": relationship_counts,
        "sample_skills": enriched_skills[:5] if len(enriched_skills) > 5 else enriched_skills
    }
    
    # Count domain distribution
    for skill in enriched_skills:
        category = skill.get('category', 'Unknown')
        summary["domains_representation"][category] = summary["domains_representation"].get(category, 0) + 1
    
    return summary

def _get_llm_factory_specialist():
    """Initialize LLM Factory specialist for feedback processing."""
    if not LLM_FACTORY_AVAILABLE:
        return None, None
    
    try:
        # Initialize specialist registry
        registry = SpecialistRegistry()
        
        # Register feedback specialist
        registry.register_specialist(
            "feedback_specialist",
            {
                "type": "text_generation",
                "model": "olmo2:latest",
                "temperature": 0.7,
                "max_tokens": 3000,
                "system_prompt": "You are OLMo2, an advanced language model specialized in understanding skill taxonomies and domain relationships. Provide detailed, actionable feedback on skill definition frameworks."
            }
        )
        
        # Initialize quality controller
        quality_controller = QualityController()
        
        return registry, quality_controller
        
    except Exception as e:
        print(f"Failed to initialize LLM Factory specialist: {e}")
        return None, None

def _get_feedback_with_llm_factory(prompt):
    """Get feedback using LLM Factory specialist."""
    registry, quality_controller = _get_llm_factory_specialist()
    if not registry:
        return None
    
    try:
        specialist = registry.get_specialist("feedback_specialist")
        response = specialist.generate(prompt)
        
        # Apply quality control
        if quality_controller:
            quality_score = quality_controller.evaluate_response(response, prompt)
            print(f"LLM Factory feedback quality score: {quality_score}")
        
        return response
        
    except Exception as e:
        print(f"Error in LLM Factory feedback generation: {e}")
        return None

def main():
    """Main function to get OLMo2's feedback on the SDR implementation"""
    # Check if OLMo2 is available
    olmo_client = get_olmo_client()
    if isinstance(olmo_client, MockLLMClient):
        print("OLMo2 is not available. Please make sure Ollama is running with OLMo2 model.")
        return
    
    # Get SDR implementation summary
    sdr_summary = get_sdr_summary()
    
    # Prepare the prompt for OLMo2
    prompt = f"""
    You are OLMo2, an advanced language model specialized in understanding skill taxonomies and domain relationships.
    
    Our team has implemented the Skill Domain Relationship (SDR) framework based on your recommendations.
    The SDR framework aims to reduce false positives in skill matching by standardizing skill definitions and considering domain relationships.
    
    Here's a summary of our implementation:
    
    1. Skill Enrichment:
       - We've enriched {sdr_summary['enriched_skills_count']} skills with domain information
       - Domain distribution: {json.dumps(sdr_summary['domains_representation'], indent=2)}
       
    2. Domain Relationship Classification:
       - We've created a relationship matrix with these relationship counts:
       {json.dumps(sdr_summary['relationship_counts'], indent=2)}
       
    3. Sample enriched skills:
    {json.dumps(sdr_summary['sample_skills'], indent=2)}
    
    We're now planning to enhance the skill enrichment process by:
    1. Moving beyond placeholder knowledge components
    2. Using LLMs (including yourself) to generate more meaningful enrichments
    3. Adding more domain-specific terminology
    
    Questions for you:
    
    1. How can we improve the structure of our enriched skill definitions to make them more useful for domain-aware matching?
    
    2. What additional components should we consider adding to the skill definitions beyond knowledge components, contexts, and functions?
    
    3. What are the best practices for using LLMs like yourself to generate high-quality skill enrichments?
    
    4. How can we ensure consistency in the enrichment process across different domains?
    
    5. What are the most common pitfalls we should avoid when standardizing skill definitions?
    
    Please provide specific, actionable advice that we can implement in our next phase of development.
    """
    
    # Try using LLM Factory for quality-controlled feedback
    print("Consulting OLMo2 for feedback on SDR implementation...")
    response = _get_feedback_with_llm_factory(prompt)
    
    # Fallback to regular LLM client if needed
    if not response:
        olmo_client = get_olmo_client()
        if hasattr(olmo_client, 'generate'):
            response = olmo_client.generate(prompt)
        else:
            response = call_ollama_api(prompt, model="olmo2:latest")
    
    # Print OLMo2's response
    print("\n=== OLMo2's Feedback on SDR Implementation ===\n")
    print(response)
    print("\n===================================================\n")
    
    # Save OLMo2's feedback to a file
    feedback_dir = os.path.join(project_root, 'docs', 'skill_matching')
    os.makedirs(feedback_dir, exist_ok=True)
    
    feedback_file = os.path.join(feedback_dir, 'olmo2_sdr_feedback.md')
    with open(feedback_file, 'w') as f:
        f.write("# OLMo2 Feedback on SDR Implementation\n\n")
        f.write("*Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*\n\n")
        f.write(response)
    
    print(f"Feedback saved to {feedback_file}")

if __name__ == "__main__":
    from datetime import datetime
    from run_pipeline.utils.llm_client import MockLLMClient
    main()
