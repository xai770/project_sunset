#!/usr/bin/env python3
"""
Continuous Learning System for SDR Framework

This module implements the continuous learning system recommended by OLMo2
for the Skill Domain Relationship (SDR) framework. It enhances the framework
with expert feedback incorporation, quality scoring, and consistency checking.
"""

import os
import sys
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import numpy as np
from collections import defaultdict

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("continuous_learning")

# Define paths
FEEDBACK_DIR = os.path.join(project_root, 'data', 'skill_enrichment_feedback')
SKILL_DIR = os.path.join(project_root, 'docs', 'skill_matching')
os.makedirs(FEEDBACK_DIR, exist_ok=True)


class ContinuousLearningSystem:
    """
    Implements continuous learning for the SDR framework through expert feedback,
    quality scoring, and consistency checking.
    """
    
    def __init__(self):
        """Initialize the continuous learning system"""
        self.enriched_skills = []
        self.expert_feedback = {}
        self.quality_scores = {}
        self.consistency_issues = []
        
    def load_data(self, skills_path: str) -> bool:
        """
        Load enriched skills data
        
        Args:
            skills_path: Path to the enriched skills JSON file
            
        Returns:
            True if data loaded successfully, False otherwise
        """
        try:
            with open(skills_path, 'r') as f:
                self.enriched_skills = json.load(f)
                
            logger.info(f"Loaded {len(self.enriched_skills)} enriched skills")
            return True
        except Exception as e:
            logger.error(f"Error loading enriched skills: {e}")
            return False
    
    def load_expert_feedback(self, feedback_dir: str = FEEDBACK_DIR) -> Dict[str, Any]:
        """
        Load expert feedback from the feedback directory
        
        Args:
            feedback_dir: Directory containing expert feedback files
            
        Returns:
            Dictionary containing expert feedback
        """
        feedback = {}
        
        try:
            # Find all feedback files in the directory
            feedback_files = [f for f in os.listdir(feedback_dir) if f.endswith('.json')]
            
            for file in feedback_files:
                file_path = os.path.join(feedback_dir, file)
                with open(file_path, 'r') as f:
                    file_feedback = json.load(f)
                    
                # Merge feedback
                for skill_name, skill_feedback in file_feedback.items():
                    if skill_name not in feedback:
                        feedback[skill_name] = skill_feedback
                    else:
                        # If we have multiple feedback instances for the same skill,
                        # prioritize the most recent one (assuming higher quality)
                        if 'timestamp' in skill_feedback and 'timestamp' in feedback[skill_name]:
                            if skill_feedback['timestamp'] > feedback[skill_name]['timestamp']:
                                feedback[skill_name] = skill_feedback
                        else:
                            # If no timestamp, just overwrite
                            feedback[skill_name] = skill_feedback
            
            logger.info(f"Loaded expert feedback for {len(feedback)} skills")
            self.expert_feedback = feedback
            return feedback
            
        except Exception as e:
            logger.error(f"Error loading expert feedback: {e}")
            return {}
    
    def calculate_quality_scores(self) -> Dict[str, float]:
        """
        Calculate quality scores for each enriched skill definition
        
        Returns:
            Dictionary mapping skill names to quality scores (0-100)
        """
        logger.info("Calculating quality scores for skill definitions")
        quality_scores = {}
        
        for skill in self.enriched_skills:
            name = skill.get('name')
            if not name:
                continue
                
            # Initialize score
            score = 60.0  # Start with a base score
            
            # Check for completeness (all required fields)
            if all(k in skill for k in ['name', 'category', 'knowledge_components', 'contexts', 'functions']):
                score += 10.0
            
            # Check for depth of enrichment
            components_count = (
                len(skill.get('knowledge_components', [])) + 
                len(skill.get('contexts', [])) + 
                len(skill.get('functions', []))
            )
            
            # More components indicate better enrichment, up to a reasonable limit
            if components_count >= 15:
                score += 15.0
            elif components_count >= 10:
                score += 10.0
            elif components_count >= 5:
                score += 5.0
            
            # Check for expert feedback
            if name in self.expert_feedback:
                feedback = self.expert_feedback[name]
                
                # Adjust score based on expert rating if available
                if 'rating' in feedback:
                    # Expert ratings are on a 1-5 scale, normalize to -10 to +10 adjustment
                    rating_adjustment = (feedback['rating'] - 3) * 5
                    score += rating_adjustment
                
                # Apply corrections if available
                if 'corrections' in feedback and feedback['corrections']:
                    # Corrections exist, which means the original wasn't perfect
                    score -= 5.0
            
            # Ensure score is within bounds
            score = max(0.0, min(100.0, score))
            quality_scores[name] = score
        
        self.quality_scores = quality_scores
        logger.info(f"Calculated quality scores for {len(quality_scores)} skills")
        return quality_scores
    
    def check_consistency(self) -> List[Dict[str, Any]]:
        """
        Check for consistency issues across skill definitions
        
        Returns:
            List of consistency issues found
        """
        logger.info("Checking consistency across skill definitions")
        issues = []
        
        # Group skills by domain
        domain_skills = defaultdict(list)
        for skill in self.enriched_skills:
            domain = skill.get('category', 'Unknown')
            domain_skills[domain].append(skill)
        
        # Check for consistency within domains
        for domain, skills in domain_skills.items():
            # Collect all components used in this domain
            all_knowledge = set()
            all_contexts = set()
            all_functions = set()
            
            for skill in skills:
                all_knowledge.update(skill.get('knowledge_components', []))
                all_contexts.update(skill.get('contexts', []))
                all_functions.update(skill.get('functions', []))
            
            # Check each skill for inconsistent usage or outliers
            for skill in skills:
                name = skill.get('name', '')
                
                # Check for unique components (potential inconsistencies)
                unique_knowledge = set(skill.get('knowledge_components', [])) - all_knowledge
                unique_contexts = set(skill.get('contexts', [])) - all_contexts
                unique_functions = set(skill.get('functions', [])) - all_functions
                
                if unique_knowledge or unique_contexts or unique_functions:
                    issues.append({
                        'skill_name': name,
                        'domain': domain,
                        'issue_type': 'unique_components',
                        'description': 'Skill uses components not found in other skills in the same domain',
                        'unique_knowledge': list(unique_knowledge),
                        'unique_contexts': list(unique_contexts),
                        'unique_functions': list(unique_functions)
                    })
                
                # Check for extremely sparse definitions
                components_count = (
                    len(skill.get('knowledge_components', [])) + 
                    len(skill.get('contexts', [])) + 
                    len(skill.get('functions', []))
                )
                
                domain_avg = np.mean([
                    len(s.get('knowledge_components', [])) + 
                    len(s.get('contexts', [])) + 
                    len(s.get('functions', []))
                    for s in skills
                ])
                
                if components_count < domain_avg * 0.5:
                    issues.append({
                        'skill_name': name,
                        'domain': domain,
                        'issue_type': 'sparse_definition',
                        'description': 'Skill definition is significantly sparser than others in the same domain',
                        'components_count': components_count,
                        'domain_average': domain_avg
                    })
        
        self.consistency_issues = issues
        logger.info(f"Found {len(issues)} consistency issues")
        return issues
    
    def apply_expert_feedback(self) -> List[Dict[str, Any]]:
        """
        Apply expert feedback to improve skill definitions
        
        Returns:
            List of updated skill definitions
        """
        if not self.expert_feedback:
            logger.warning("No expert feedback available to apply")
            return self.enriched_skills
            
        logger.info(f"Applying expert feedback to {len(self.expert_feedback)} skills")
        updated_skills = []
        
        for skill in self.enriched_skills:
            name = skill.get('name')
            if not name or name not in self.expert_feedback:
                # No feedback for this skill, keep it unchanged
                updated_skills.append(skill)
                continue
                
            feedback = self.expert_feedback[name]
            updated_skill = skill.copy()
            
            # Apply corrections if available
            if 'corrections' in feedback:
                corrections = feedback['corrections']
                
                # Update category if provided
                if 'category' in corrections:
                    updated_skill['category'] = corrections['category']
                
                # Update components if provided
                for component_type in ['knowledge_components', 'contexts', 'functions']:
                    if component_type in corrections:
                        # Replace or merge components
                        if corrections.get('replace_' + component_type, False):
                            updated_skill[component_type] = corrections[component_type]
                        else:
                            # Merge while removing duplicates
                            current = set(updated_skill.get(component_type, []))
                            current.update(corrections[component_type])
                            updated_skill[component_type] = sorted(list(current))
            
            # Add expert notes if available
            if 'notes' in feedback:
                updated_skill['expert_notes'] = feedback['notes']
                
            # Add feedback metadata
            updated_skill['feedback_applied'] = {
                'timestamp': datetime.datetime.now().isoformat(),
                'source': feedback.get('source', 'unknown')
            }
            
            updated_skills.append(updated_skill)
        
        logger.info(f"Applied expert feedback to {len(self.expert_feedback)} skills")
        self.enriched_skills = updated_skills
        return updated_skills
    
    def generate_quality_report(self, output_path: str) -> str:
        """
        Generate a quality report for the skill definitions
        
        Args:
            output_path: Path to save the quality report
            
        Returns:
            Path to the saved report
        """
        if not self.quality_scores:
            self.calculate_quality_scores()
            
        if not self.consistency_issues:
            self.check_consistency()
        
        # Create the report
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'total_skills': len(self.enriched_skills),
            'quality_scores': self.quality_scores,
            'average_quality_score': sum(self.quality_scores.values()) / len(self.quality_scores) if self.quality_scores else 0,
            'consistency_issues': self.consistency_issues,
            'issue_count': len(self.consistency_issues),
            'feedback_applied_count': sum(1 for skill in self.enriched_skills if 'feedback_applied' in skill)
        }
        
        # Add quality distribution
        score_ranges = {
            '0-25': 0,
            '26-50': 0,
            '51-75': 0,
            '76-100': 0
        }
        
        for score in self.quality_scores.values():
            if score <= 25:
                score_ranges['0-25'] += 1
            elif score <= 50:
                score_ranges['26-50'] += 1
            elif score <= 75:
                score_ranges['51-75'] += 1
            else:
                score_ranges['76-100'] += 1
                
        report['quality_distribution'] = score_ranges
        
        # Save the report
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Quality report saved to {output_path}")
        return output_path
    
    def save_updated_skills(self, output_path: str) -> str:
        """
        Save the updated skill definitions
        
        Args:
            output_path: Path to save the updated skill definitions
            
        Returns:
            Path to the saved file
        """
        with open(output_path, 'w') as f:
            json.dump(self.enriched_skills, f, indent=2)
            
        logger.info(f"Updated {len(self.enriched_skills)} skill definitions saved to {output_path}")
        return output_path
        

def main():
    """Main function for the continuous learning system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run the continuous learning system for the SDR framework')
    
    parser.add_argument('--skills', type=str, default=os.path.join(SKILL_DIR, 'enriched_skills.json'),
                       help='Path to the enriched skills JSON file')
    
    parser.add_argument('--feedback-dir', type=str, default=FEEDBACK_DIR,
                       help='Directory containing expert feedback files')
    
    parser.add_argument('--output-dir', type=str, default=SKILL_DIR,
                       help='Directory to save output files')
    
    parser.add_argument('--apply-feedback', action='store_true',
                       help='Apply expert feedback to improve skill definitions')
    
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate a quality report for skill definitions')
    
    args = parser.parse_args()
    
    # Create the continuous learning system
    cl_system = ContinuousLearningSystem()
    
    # Load data
    if not cl_system.load_data(args.skills):
        logger.error("Failed to load enriched skills data. Exiting.")
        sys.exit(1)
    
    # Load expert feedback
    cl_system.load_expert_feedback(args.feedback_dir)
    
    # Apply expert feedback if requested
    if args.apply_feedback:
        updated_skills = cl_system.apply_expert_feedback()
        output_path = os.path.join(args.output_dir, 'enriched_skills_updated.json')
        cl_system.save_updated_skills(output_path)
        
    # Calculate quality scores
    quality_scores = cl_system.calculate_quality_scores()
    
    # Check consistency
    consistency_issues = cl_system.check_consistency()
    
    # Generate quality report if requested
    if args.generate_report:
        report_path = os.path.join(args.output_dir, f'quality_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        cl_system.generate_quality_report(report_path)
    
    # Print summary
    print("\n===== SDR Continuous Learning System Summary =====")
    print(f"Analyzed {len(cl_system.enriched_skills)} skill definitions")
    print(f"Applied expert feedback to {sum(1 for skill in cl_system.enriched_skills if 'feedback_applied' in skill)} skills")
    print(f"Found {len(consistency_issues)} consistency issues")
    print(f"Average quality score: {sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0:.2f}")
    print("================================================\n")
    

if __name__ == "__main__":
    main()
