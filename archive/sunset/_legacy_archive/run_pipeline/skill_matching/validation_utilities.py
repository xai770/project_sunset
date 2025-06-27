#!/usr/bin/env python3
"""
Validation Utilities for SDR Framework

This module contains utility functions for validating the quality of enriched skills
and generating quality reports for the Skill Domain Relationship (SDR) framework.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Union, Optional

# Make validate_skill_enrichment accessible from module import
__all__ = ['validate_skill_enrichment']

# Add the project root to the path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import components
from run_pipeline.skill_matching.skill_validation import SkillValidationSystem

# Configure logging
logger = logging.getLogger("sdr_validation_utilities")

# Constants
OUTPUT_DIR = os.path.join(project_root, 'docs', 'skill_matching')

def validate_skill_enrichment(
    enriched_skills: Union[List[Dict[str, Any]], str], 
    save_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate the quality of enriched skills using the SkillValidationSystem
    
    Args:
        enriched_skills: List of enriched skill definitions or path to a file containing them
        save_path: Optional path to save the enriched skills before validation
        
    Returns:
        Dictionary with validation results
    """
    logger.info(f"Validating enriched skills")
    
    # If save_path is provided, save the enriched skills to that path
    if save_path and isinstance(enriched_skills, list):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(enriched_skills, f, indent=2)
        logger.info(f"Saved enriched skills to {save_path} for validation")
        validation_path = save_path
    elif isinstance(enriched_skills, str) and os.path.exists(enriched_skills):
        # If enriched_skills is already a path to a file
        validation_path = enriched_skills
    else:
        # Save to default location if a list is provided but no save_path
        if isinstance(enriched_skills, list):
            default_path = os.path.join(OUTPUT_DIR, 'enriched_skills.json')
            os.makedirs(os.path.dirname(default_path), exist_ok=True)
            with open(default_path, 'w') as f:
                json.dump(enriched_skills, f, indent=2)
            validation_path = default_path
        else:
            logger.error("Invalid input for validation: must be a list of skills or path to a file")
            return {"error": "Invalid input for validation"}
    
    # Create and use the validation system
    validation_system = SkillValidationSystem()
    validation_results = validation_system.validate_skills(validation_path)
    
    # Generate a comprehensive quality report
    report_path = validation_system.generate_quality_report(validation_path)
    logger.info(f"Generated quality report at {report_path}")
    
    # Calculate average quality score
    if "quality_scores" in validation_results and validation_results["quality_scores"]:
        avg_quality = sum(validation_results["quality_scores"].values()) / len(validation_results["quality_scores"])
        validation_results["average_quality_score"] = avg_quality
    else:
        validation_results["average_quality_score"] = 0
    
    # Add recommendations based on quality scores
    validation_results["recommendations"] = []
    
    if validation_results.get("average_quality_score", 0) < 70:
        validation_results["recommendations"].append(
            "Quality scores are below target threshold (70). Consider re-running with improved LLM prompts."
        )
    
    low_quality_skills = [
        skill_name for skill_name, score in validation_results.get("quality_scores", {}).items() 
        if score < 60
    ]
    
    if low_quality_skills:
        validation_results["recommendations"].append(
            f"The following skills have particularly low quality scores (<60) and should be reviewed: {', '.join(low_quality_skills[:5])}"
            + (f" and {len(low_quality_skills) - 5} more..." if len(low_quality_skills) > 5 else "")
        )
    
    return validation_results

# Main function for standalone validation
if __name__ == "__main__":
    import argparse
    from datetime import datetime
    
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Validate enriched skills')
    parser.add_argument('--skills', type=str, help='Path to enriched skills JSON file')
    parser.add_argument('--output', type=str, help='Path to save validation results')
    
    args = parser.parse_args()
    
    skills_file = args.skills or os.path.join(OUTPUT_DIR, 'enriched_skills.json')
    
    # Validate skills
    try:
        validation_results = validate_skill_enrichment(skills_file)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = args.output or os.path.join(OUTPUT_DIR, f'validation_results_{timestamp}.json')
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        # Print summary
        print("\n===== Skill Validation Results =====")
        print(f"Validation completed on {skills_file}")
        print(f"Average quality score: {validation_results.get('average_quality_score', 0):.2f}")
        
        if validation_results.get("recommendations"):
            print("\nRecommendations:")
            for rec in validation_results["recommendations"]:
                print(f"- {rec}")
        
        print(f"\nResults saved to: {output_file}")
        print("===================================\n")
        
    except Exception as e:
        logger.error(f"Error validating skills: {e}")
        print(f"Error: {e}")
        sys.exit(1)
