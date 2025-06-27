#!/usr/bin/env python3
"""
SDR Pipeline Core Implementation

This module contains the core implementation of the Skill Domain Relationship (SDR) 
framework pipeline, responsible for skill enrichment, relationship classification,
quality assessment, visualization generation, and job file updates.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Set
from pathlib import Path

# Add the project root to the path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import components
from run_pipeline.skill_matching.skill_analyzer import SkillAnalyzer
from run_pipeline.skill_matching.domain_relationship_classifier import DomainRelationshipClassifier
from run_pipeline.skill_matching.continuous_learning import ContinuousLearningSystem
from run_pipeline.skill_matching.visualize_relationships import SkillRelationshipVisualizer
from run_pipeline.config.paths import JOB_DATA_DIR
from run_pipeline.skill_matching.sdr_job_update import update_job_files_with_enriched_skills

# Configure logging
logger = logging.getLogger("sdr_pipeline")

# Constants
OUTPUT_DIR = os.path.join(project_root, 'docs', 'skill_matching')

def run_skill_analysis(use_llm: bool = False, max_skills: int = 50) -> List[Dict[str, Any]]:
    """
    Run the skill analysis and enrichment step
    
    Args:
        use_llm: Whether to use LLM for skill enrichment
        max_skills: Maximum number of skills to analyze
        
    Returns:
        List of enriched skill definitions
    """
    logger.info(f"Starting skill analysis with {max_skills} skills")
    
    # Initialize the skill analyzer
    analyzer = SkillAnalyzer()
    
    # Run the full analysis
    enriched_skills = analyzer.run_analysis(use_llm=use_llm, max_skills=max_skills)
    
    # Save enriched skills to a file
    enriched_skills_file = os.path.join(OUTPUT_DIR, 'enriched_skills.json')
    os.makedirs(os.path.dirname(enriched_skills_file), exist_ok=True)
    
    with open(enriched_skills_file, 'w') as f:
        json.dump(enriched_skills, f, indent=2)
    
    logger.info(f"Completed skill analysis with {len(enriched_skills)} enriched skills")
    return enriched_skills

def run_relationship_classification(
    enriched_skills: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Run the domain relationship classification step
    
    Args:
        enriched_skills: List of enriched skill definitions
        
    Returns:
        Dictionary of skill relationships
    """
    logger.info("Starting domain relationship classification")
    
    # Initialize the classifier
    classifier = DomainRelationshipClassifier()
    
    # Classify relationships
    skill_relationships = classifier.classify_relationships(enriched_skills)
    
    # Save relationships to a file
    relationships_file = os.path.join(OUTPUT_DIR, 'skill_relationships.json')
    os.makedirs(os.path.dirname(relationships_file), exist_ok=True)
    
    with open(relationships_file, 'w') as f:
        json.dump(skill_relationships, f, indent=2)
    
    logger.info(f"Completed relationship classification with {len(skill_relationships)} skills")
    return skill_relationships

def apply_expert_feedback(
    enriched_skills: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Apply expert feedback to improve skill definitions
    
    Args:
        enriched_skills: List of enriched skill definitions
        
    Returns:
        Tuple of (updated_skills, quality_report)
    """
    logger.info("Starting expert feedback application")
    
    # Initialize the continuous learning system
    cl_system = ContinuousLearningSystem()
    cl_system.enriched_skills = enriched_skills
    
    # Load expert feedback
    cl_system.load_expert_feedback()
    
    # Apply feedback
    updated_skills = cl_system.apply_expert_feedback()
    
    # Calculate quality scores
    quality_scores = cl_system.calculate_quality_scores()
    
    # Check consistency
    consistency_issues = cl_system.check_consistency()
    
    # Generate quality report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    quality_report_path = os.path.join(OUTPUT_DIR, f'quality_report_{timestamp}.json')
    cl_system.generate_quality_report(quality_report_path)
    
    quality_report: Dict[str, Any] = {
        "quality_scores": quality_scores,
        "consistency_issues": consistency_issues,
        "quality_report_path": quality_report_path
    }
    
    # Save updated skills
    enriched_skills_file = os.path.join(OUTPUT_DIR, 'enriched_skills.json')
    os.makedirs(os.path.dirname(enriched_skills_file), exist_ok=True)
    
    with open(enriched_skills_file, 'w') as f:
        json.dump(updated_skills, f, indent=2)
    
    logger.info(f"Completed expert feedback application with {len(updated_skills)} updated skills")
    return updated_skills, quality_report

def generate_visualizations(
    enriched_skills: List[Dict[str, Any]], 
    skill_relationships: Dict[str, Dict[str, Dict[str, Any]]]
) -> Dict[str, str]:
    """
    Generate visualizations for skill relationships
    
    Args:
        enriched_skills: List of enriched skill definitions
        skill_relationships: Dictionary of skill relationships
        
    Returns:
        Dictionary mapping visualization types to output paths
    """
    logger.info("Starting visualization generation")
    
    # Initialize visualizer
    visualizer = SkillRelationshipVisualizer()
    visualizer.enriched_skills = enriched_skills
    visualizer.skill_relationships = skill_relationships
    
    # Create visualization directory
    visualization_dir = os.path.join(OUTPUT_DIR, 'visualizations')
    os.makedirs(visualization_dir, exist_ok=True)
    
    # Generate visualizations
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    visualizations = {}
    
    # Network graph
    try:
        network_path = os.path.join(visualization_dir, f'skill_network_{timestamp}.png')
        visualizer.visualize_network_graph(network_path)
        visualizations['network'] = network_path
        logger.info(f"Generated network graph at {network_path}")
    except Exception as e:
        logger.error(f"Failed to generate network graph: {e}")
    
    # Domain heatmap
    try:
        heatmap_path = os.path.join(visualization_dir, f'domain_heatmap_{timestamp}.png')
        visualizer.visualize_domain_heatmap(heatmap_path)
        visualizations['heatmap'] = heatmap_path
        logger.info(f"Generated domain heatmap at {heatmap_path}")
    except Exception as e:
        logger.error(f"Failed to generate domain heatmap: {e}")
    
    # Chord diagram
    try:
        chord_path = os.path.join(visualization_dir, f'relationship_chord_{timestamp}.png')
        visualizer.visualize_relationship_chord_diagram(chord_path)
        visualizations['chord'] = chord_path
        logger.info(f"Generated chord diagram at {chord_path}")
    except Exception as e:
        logger.warning(f"Could not generate chord diagram: {e}")
    
    logger.info(f"Completed visualization generation with {len(visualizations)} visualizations")
    return visualizations

def update_job_files(enriched_skills: List[Dict[str, Any]]) -> None:
    """
    Update job files with enriched skill information
    
    Args:
        enriched_skills: List of enriched skill definitions
    """
    logger.info("Starting job file update")
    
    # Job data directory
    job_data_dir = Path(JOB_DATA_DIR)
    os.makedirs(job_data_dir, exist_ok=True)
    
    # Update each job file
    for skill in enriched_skills:
        job_file_path = job_data_dir / f"{skill['id']}.json"
        
        # Prepare job data
        job_data = {
            "skill_id": skill["id"],
            "skill_name": skill["name"],
            "enrichment_data": skill.get("enrichment_data", {}),
            "relationships": skill.get("relationships", [])
        }
        
        # Write to job file
        with open(job_file_path, 'w') as job_file:
            json.dump(job_data, job_file, indent=2)
            logger.info(f"Updated job file for skill {skill['id']}")
    
    logger.info("Completed job file updates")

def run_complete_pipeline(
    use_llm: bool = False,
    max_skills: int = 50,
    apply_feedback: bool = False,
    generate_viz: bool = False
) -> Dict[str, Any]:
    """
    Run the complete SDR pipeline
    
    Args:
        use_llm: Whether to use LLM for skill enrichment
        max_skills: Maximum number of skills to analyze
        apply_feedback: Whether to apply expert feedback
        generate_viz: Whether to generate visualizations
        
    Returns:
        Dictionary with pipeline results
    """
    logger.info("Starting complete SDR pipeline")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results: Dict[str, Any] = {"timestamp": timestamp}
    
    # Step 1: Skill Analysis
    enriched_skills = run_skill_analysis(use_llm, max_skills)
    results["enriched_skills_count"] = len(enriched_skills)
    
    # Step 2: Relationship Classification
    skill_relationships = run_relationship_classification(enriched_skills)
    results["relationship_count"] = sum(len(rels) for rels in skill_relationships.values())
    
    # Step 3: Apply Expert Feedback (if requested)
    if apply_feedback:
        enriched_skills, quality_report = apply_expert_feedback(enriched_skills)
        results["quality_report"] = quality_report
    
    # Step 4: Generate Visualizations (if requested)
    if generate_viz:
        visualizations = generate_visualizations(enriched_skills, skill_relationships)
        results["visualizations"] = visualizations
    
    # Step 5: Update Job Files
    updated_files = update_job_files_with_enriched_skills(enriched_skills)
    results["updated_job_files"] = len(updated_files)
    
    # Save results summary
    summary_path = os.path.join(OUTPUT_DIR, f'pipeline_results_{timestamp}.json')
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Completed SDR pipeline with {len(enriched_skills)} enriched skills")
    return results

# Main function for standalone execution
if __name__ == "__main__":
    import argparse
    
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Run the core SDR pipeline')
    parser.add_argument('--use-llm', action='store_true', help='Use LLM for skill enrichment')
    parser.add_argument('--max-skills', type=int, default=50, help='Maximum number of skills to analyze')
    parser.add_argument('--apply-feedback', action='store_true', help='Apply expert feedback')
    parser.add_argument('--generate-visualizations', action='store_true', help='Generate visualizations')
    parser.add_argument('--update-job-files', action='store_true', help='Update job files with enriched skills')
    parser.add_argument('--max-jobs', type=int, help='Maximum number of jobs to update')
    parser.add_argument('--job-ids', type=str, help='Comma-separated list of job IDs to update')
    parser.add_argument('--force-reprocess', action='store_true', help='Force reprocessing of jobs that already have SDR skills')
    
    args = parser.parse_args()
    
    # Process job IDs if provided
    job_ids = None
    if args.job_ids:
        job_ids = [int(job_id.strip()) for job_id in args.job_ids.split(',') if job_id.strip()]
    
    # Run the pipeline
    results = run_complete_pipeline(
        use_llm=args.use_llm,
        max_skills=args.max_skills,
        apply_feedback=args.apply_feedback,
        generate_viz=args.generate_visualizations
    )
    
    # Update job files if requested
    if args.update_job_files:
        # Load enriched skills from file if needed
        enriched_skills_file = os.path.join(OUTPUT_DIR, 'enriched_skills.json')
        enriched_skills = []
        if os.path.exists(enriched_skills_file):
            try:
                with open(enriched_skills_file, 'r') as f:
                    enriched_skills = json.load(f)
                logger.info(f"Loaded {len(enriched_skills)} skills from {enriched_skills_file}")
            except Exception as e:
                logger.error(f"Error loading enriched skills: {e}")
                print(f"Error: Could not load enriched skills file: {e}")
                enriched_skills = []
                
        updated_files = update_job_files_with_enriched_skills(
            enriched_skills=enriched_skills,
            max_jobs=args.max_jobs,
            job_ids=job_ids,
            force_reprocess=args.force_reprocess
        )
        results["updated_job_files"] = len(updated_files)
    
    # Print summary
    print("\n===== SDR Pipeline Results =====")
    print(f"Enriched skills: {results['enriched_skills_count']}")
    print(f"Relationships: {results['relationship_count']}")
    
    if 'quality_report' in results:
        print(f"Average quality score: {results['quality_report'].get('average_quality_score', 0):.2f}")
    
    if 'visualizations' in results:
        print("\nVisualizations:")
        for viz_type, path in results['visualizations'].items():
            print(f"  {viz_type}: {path}")
    
    print("===============================\n")
