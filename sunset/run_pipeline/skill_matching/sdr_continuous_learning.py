#!/usr/bin/env python3
"""
SDR Continuous Learning Integration Script

This script integrates the continuous learning system with the SDR framework,
allowing for iterative improvement of skill definitions based on expert feedback.
It serves as a bridge between the SDR implementation and the continuous learning system.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Collection, Sequence, MutableSequence

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Import components
from run_pipeline.skill_matching.continuous_learning import ContinuousLearningSystem
from run_pipeline.skill_matching.skill_validation import SkillValidationSystem
from run_pipeline.skill_matching.visualize_relationships import SkillRelationshipVisualizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sdr_continuous_learning")

# Constants
OUTPUT_DIR = os.path.join(project_root, 'docs', 'skill_matching')
FEEDBACK_DIR = os.path.join(project_root, 'data', 'skill_enrichment_feedback')


class SDRContinuousLearningIntegration:
    """
    Integrates the continuous learning system with the SDR framework,
    facilitating the iterative improvement of skill definitions.
    """
    
    def __init__(self):
        """Initialize the integration class"""
        self.cl_system = ContinuousLearningSystem()
        self.validator = SkillValidationSystem()
        self.visualizer = SkillRelationshipVisualizer()
        
    def load_skill_data(self, skills_path: str, relationships_path: str) -> bool:
        """
        Load skill definitions and relationships
        
        Args:
            skills_path: Path to the enriched skills JSON file
            relationships_path: Path to the skill relationships JSON file
            
        Returns:
            True if data loaded successfully, False otherwise
        """
        try:
            # Load skills using continuous learning system
            if not self.cl_system.load_data(skills_path):
                return False
                
            # Load relationships for visualization
            self.visualizer.load_data(skills_path, relationships_path)
            
            logger.info(f"Loaded {len(self.cl_system.enriched_skills)} skills and their relationships")
            return True
            
        except Exception as e:
            logger.error(f"Error loading skill data: {e}")
            return False
    
    def process_feedback(self, generate_report: bool = True) -> Dict[str, Any]:
        """
        Process expert feedback and update skill definitions
        
        Args:
            generate_report: Whether to generate a quality report
            
        Returns:
            Dictionary with processing results
        """
        results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "feedback_processed": 0,
            "skills_updated": 0,
            "quality_changes": {}
        }
        
        # Load expert feedback
        feedback = self.cl_system.load_expert_feedback()
        results["feedback_processed"] = len(feedback)
        
        if not feedback:
            logger.info("No expert feedback found to process")
            return results
        
        # Calculate initial quality scores
        initial_scores = self.cl_system.calculate_quality_scores()
        
        # Apply expert feedback
        updated_skills = self.cl_system.apply_expert_feedback()
        results["skills_updated"] = sum(1 for skill in updated_skills if "feedback_applied" in skill)
        
        # Calculate updated quality scores
        updated_scores = self.cl_system.calculate_quality_scores()
        
        # Record quality changes
        for skill_name in updated_scores:
            if skill_name in initial_scores:
                initial = initial_scores[skill_name]
                current = updated_scores[skill_name]
                change = current - initial
                # Ensure results["quality_changes"] is a Dict[str, Dict[str, Any]]
                results["quality_changes"][skill_name] = { # This line is fine if results["quality_changes"] is properly typed
                    "initial": initial,
                    "current": current,
                    "change": change
                }
        
        # Generate quality report if requested
        if generate_report:
            report_path = os.path.join(OUTPUT_DIR, f'quality_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            self.cl_system.generate_quality_report(report_path)
            results["quality_report"] = report_path
        
        return results
    
    def generate_visualizations(self) -> Dict[str, str]:
        """
        Generate visualizations for skill relationships
        
        Returns:
            Dictionary mapping visualization types to output paths
        """
        # Ensure the visualization directory exists
        visualization_dir = os.path.join(OUTPUT_DIR, 'visualizations')
        os.makedirs(visualization_dir, exist_ok=True)
        
        # Generate timestamp for file names
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        visualizations = {}
        
        # Generate network graph
        try:
            network_path = os.path.join(visualization_dir, f'skill_network_{timestamp}.png')
            self.visualizer.visualize_network_graph(network_path)
            visualizations['network'] = network_path
        except Exception as e:
            logger.error(f"Error generating network graph: {e}")
        
        # Generate domain heatmap
        try:
            heatmap_path = os.path.join(visualization_dir, f'domain_heatmap_{timestamp}.png')
            self.visualizer.visualize_domain_heatmap(heatmap_path)
            visualizations['heatmap'] = heatmap_path
        except Exception as e:
            logger.error(f"Error generating domain heatmap: {e}")
        
        # Try to generate chord diagram
        try:
            chord_path = os.path.join(visualization_dir, f'relationship_chord_{timestamp}.png')
            self.visualizer.visualize_relationship_chord_diagram(chord_path)
            visualizations['chord'] = chord_path
        except Exception as e:
            logger.warning(f"Could not generate chord diagram: {e}")
        
        logger.info(f"Generated {len(visualizations)} visualizations in {visualization_dir}")
        return visualizations
    
    def check_quality_and_consistency(self) -> Dict[str, Any]:
        """
        Check the quality and consistency of skill definitions
        
        Returns:
            Dictionary with quality and consistency check results
        """
        results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "quality_scores": {},
            "consistency_issues": [], # Type: List[Any] or more specific if known
            "recommendations": [] # Type: List[str]
        }
        
        # Calculate quality scores
        quality_scores = self.cl_system.calculate_quality_scores()
        results["quality_scores"] = quality_scores
        
        # Calculate average quality score
        if quality_scores:
            avg_quality = sum(quality_scores.values()) / len(quality_scores)
            results["average_quality_score"] = avg_quality
            
            # Add recommendations based on quality score
            if avg_quality < 70:
                results["recommendations"].append(
                    "Quality scores are below target threshold (70). Consider running the enrichment process again with improved prompts."
                )
        
        # Check for consistency issues
        consistency_issues: List[Dict[str, Any]] = self.cl_system.check_consistency() # Assuming check_consistency returns List[Dict[str,Any]]
        results["consistency_issues"] = consistency_issues
        results["issue_count"] = len(consistency_issues)
        
        # Add recommendations based on consistency issues
        if len(consistency_issues) > 10:
            results["recommendations"].append(
                "High number of consistency issues detected. Consider reviewing the skill definitions for standardization."
            )
        
        # Find low-quality skills
        low_quality_skills = [
            skill_name for skill_name, score in quality_scores.items() if score < 60
        ]
        
        if low_quality_skills:
            results["low_quality_skills"] = low_quality_skills
            results["recommendations"].append(
                f"Found {len(low_quality_skills)} low-quality skill definitions (score < 60). Consider prioritizing these for improvement."
            )
        
        return results
    
    def save_updated_skills(self, output_path: Optional[str] = None) -> str:
        """
        Save the updated skill definitions
        
        Args:
            output_path: Path to save the updated definitions (optional)
            
        Returns:
            Path where the skills were saved
        """
        if not output_path:
            # Generate a new path with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(OUTPUT_DIR, f'enriched_skills_updated_{timestamp}.json')
        
        return self.cl_system.save_updated_skills(output_path)
    
    def run_full_integration(self, skills_path: str, relationships_path: str, 
                           save_updated: bool = True, generate_report: bool = True,
                           create_visualizations: bool = True) -> Dict[str, Any]:
        """
        Run the full continuous learning integration process
        
        Args:
            skills_path: Path to the enriched skills JSON file
            relationships_path: Path to the skill relationships JSON file
            save_updated: Whether to save updated skill definitions
            generate_report: Whether to generate a quality report
            create_visualizations: Whether to create visualizations
            
        Returns:
            Dictionary with integration results
        """
        results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "steps_completed": [] # Type: List[str]
        }
        
        # Step 1: Load data
        logger.info("Step 1: Loading skill data")
        if not self.load_skill_data(skills_path, relationships_path):
            results["status"] = "error"
            results["error"] = "Failed to load skill data"
            return results
        
        results["steps_completed"].append("data_loading")
        
        # Step 2: Process feedback
        logger.info("Step 2: Processing expert feedback")
        feedback_results = self.process_feedback(generate_report=generate_report)
        results["feedback_results"] = feedback_results
        results["steps_completed"].append("feedback_processing")
        
        # Step 3: Quality and consistency check
        logger.info("Step 3: Checking quality and consistency")
        quality_results = self.check_quality_and_consistency()
        results["quality_results"] = quality_results
        results["steps_completed"].append("quality_check")
        
        # Step 4: Save updated definitions if requested
        if save_updated:
            logger.info("Step 4: Saving updated skill definitions")
            saved_path = self.save_updated_skills()
            results["updated_skills_path"] = saved_path
            results["steps_completed"].append("save_updated")
        
        # Step 5: Generate visualizations if requested
        if create_visualizations:
            logger.info("Step 5: Generating visualizations")
            visualizations = self.generate_visualizations()
            results["visualizations"] = visualizations
            results["steps_completed"].append("create_visualizations")
        
        logger.info("Continuous learning integration completed successfully")
        return results


def main():
    """Main function for the integration script"""
    parser = argparse.ArgumentParser(description='Integrate continuous learning with the SDR framework')
    
    parser.add_argument('--skills', type=str, default=os.path.join(OUTPUT_DIR, 'enriched_skills.json'),
                       help='Path to the enriched skills JSON file')
    
    parser.add_argument('--relationships', type=str, default=os.path.join(OUTPUT_DIR, 'skill_relationships.json'),
                       help='Path to the skill relationships JSON file')
    
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save updated skill definitions')
    
    parser.add_argument('--no-report', action='store_true',
                       help='Do not generate quality report')
    
    parser.add_argument('--no-visualizations', action='store_true',
                       help='Do not create visualizations')
    
    args = parser.parse_args()
    
    # Create the integration object
    integration = SDRContinuousLearningIntegration()
    
    # Run the full integration process
    results = integration.run_full_integration(
        skills_path=args.skills,
        relationships_path=args.relationships,
        save_updated=not args.no_save,
        generate_report=not args.no_report,
        create_visualizations=not args.no_visualizations
    )
    
    # Print summary
    print("\n===== SDR Continuous Learning Integration Summary =====")
    print(f"Status: {results['status']}")
    
    if 'feedback_results' in results:
        fb_results = results['feedback_results']
        print(f"Feedback processed: {fb_results.get('feedback_processed', 0)}")
        print(f"Skills updated: {fb_results.get('skills_updated', 0)}")
    
    if 'quality_results' in results:
        q_results = results['quality_results']
        print(f"Average quality score: {q_results.get('average_quality_score', 0):.2f}")
        print(f"Consistency issues found: {q_results.get('issue_count', 0)}")
    
    if 'updated_skills_path' in results:
        print(f"Updated skills saved to: {results['updated_skills_path']}")
    
    if 'visualizations' in results:
        viz = results['visualizations']
        print(f"Visualizations generated: {len(viz)}")
        for viz_type, path in viz.items():
            print(f"  - {viz_type}: {os.path.basename(path)}")
    
    print("==========================================\n")

if __name__ == "__main__":
    main()
