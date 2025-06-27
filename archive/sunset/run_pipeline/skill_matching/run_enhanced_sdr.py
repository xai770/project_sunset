#!/usr/bin/env python3
"""
Enhanced SDR Integration Script

This script provides the full enhanced implementation of the SDR (Skill Domain Relationship)
framework with improved skill enrichment using LLMs based on OLMo2's recommendations.

It orchestrates:
1. Skill analysis and selection
2. LLM-based skill enrichment
3. Domain relationship classification
4. Domain-aware matching
5. Continuous learning and quality assessment
6. Visualization generation
7. Job file updates with enriched skills

The implementation follows OLMo2's multi-stage pipeline approach for generating
high-quality skill definitions and includes advanced visualization and continuous
learning capabilities.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Import components - use direct imports
import run_pipeline.skill_matching.sdr_pipeline as sdr_pipeline
import run_pipeline.skill_matching.validation_utilities as validation_utils
import run_pipeline.skill_matching.test_utilities as test_utils
from run_pipeline.config.paths import JOB_DATA_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'logs', f'sdr_implementation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'))
    ]
)
logger = logging.getLogger("sdr_implementation")

# Constants
OUTPUT_DIR = os.path.join(project_root, 'docs', 'skill_matching')

def run_sdr_implementation(use_llm=False, max_skills=50, validate_enrichment=True, 
                     test_matching=False, apply_feedback=False, generate_visualizations=False,
                     update_job_files=True, max_jobs=None, job_ids=None, force_reprocess=False):
    """
    Run the complete SDR implementation pipeline with LLM enhancement
    
    Args:
        use_llm: Whether to use LLM for skill enrichment
        max_skills: Maximum number of skills to analyze
        validate_enrichment: Whether to validate the enriched skills
        test_matching: Whether to test domain-aware matching with sample data
        apply_feedback: Whether to apply expert feedback to improve skill definitions
        generate_visualizations: Whether to generate visualizations for skill relationships
        update_job_files: Whether to update job files with enriched skills
        max_jobs: Maximum number of jobs to update
        job_ids: Specific job IDs to update
        force_reprocess: Whether to reprocess jobs that already have SDR skills
        
    Returns:
        A tuple of (enriched_skills, skill_relationships, visualizations)
    """
    logger.info("Starting SDR implementation with enhanced skill enrichment")
    
    # Step 1: Skill Analysis
    logger.info("Step 1: Running skill analysis and selection")
    enriched_skills = sdr_pipeline.run_skill_analysis(use_llm=use_llm, max_skills=max_skills)
    enriched_skills_file = os.path.join(OUTPUT_DIR, 'enriched_skills.json')
    
    # Step 2: Domain Relationship Classification
    logger.info("Step 2: Classifying domain relationships")
    skill_relationships = sdr_pipeline.run_relationship_classification(enriched_skills)
    
    # Step 3: Continuous learning and quality assessment (if requested)
    if apply_feedback:
        logger.info("Step 3: Applying expert feedback and quality assessment")
        enriched_skills, quality_report = sdr_pipeline.apply_expert_feedback(enriched_skills)
        logger.info(f"Updated skills with expert feedback and generated quality report")
    
    # Step 4: Quality validation (if requested)
    if validate_enrichment:
        logger.info("Step 4: Validating skill enrichment quality")
        validation_results = validation_utils.validate_skill_enrichment(enriched_skills, save_path=enriched_skills_file)
        
        # Save validation results
        validation_file = os.path.join(OUTPUT_DIR, 'enrichment_validation.json')
        with open(validation_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        logger.info(f"Validation results saved to {validation_file}")
    
    # Step 5: Domain-aware matching (if requested for testing)
    if test_matching:
        logger.info("Step 5: Testing domain-aware matching")
        matching_results = test_utils.test_domain_aware_matching(enriched_skills, skill_relationships)
        
        # Calculate metrics
        matching_results["metrics"] = test_utils.calculate_match_metrics(matching_results)
        
        # Save matching results
        matching_file = os.path.join(OUTPUT_DIR, 'matching_results.json')
        with open(matching_file, 'w') as f:
            json.dump(matching_results, f, indent=2)
        logger.info(f"Matching test results saved to {matching_file}")
    
    # Step 6: Generate visualizations (if requested)
    visualizations = {}
    if generate_visualizations:
        logger.info("Step 6: Generating visualizations")
        visualizations = sdr_pipeline.generate_visualizations(enriched_skills, skill_relationships)
        logger.info(f"Generated {len(visualizations)} visualizations")
    
    # Step 7: Update job files with enriched skills (if requested)
    if update_job_files:
        logger.info("Step 7: Updating job files with enriched skills")
        job_file_updates = sdr_pipeline.update_job_files_with_enriched_skills(
            enriched_skills,
            max_jobs=max_jobs,
            job_ids=job_ids,
            force_reprocess=force_reprocess
        )
        logger.info(f"Updated {len(job_file_updates)} job files with enriched skills")
    
    logger.info("SDR implementation completed successfully")
    return enriched_skills, skill_relationships, visualizations

def main():
    """Entry point function"""
    parser = argparse.ArgumentParser(description='Run the enhanced SDR implementation with LLM-based skill enrichment')
    
    parser.add_argument('--use-llm', action='store_true', 
                        help='Use LLM for skill enrichment (higher quality but slower)')
    
    parser.add_argument('--max-skills', type=int, default=50, 
                        help='Maximum number of skills to analyze')
    
    parser.add_argument('--skip-validation', action='store_true',
                        help='Skip validation of enriched skills')
                        
    parser.add_argument('--test-matching', action='store_true',
                        help='Test domain-aware matching with sample data')
    
    parser.add_argument('--load-existing', action='store_true',
                        help='Load existing enriched skills instead of generating new ones')
                        
    parser.add_argument('--apply-feedback', action='store_true',
                        help='Apply expert feedback to improve skill definitions')
                        
    parser.add_argument('--generate-visualizations', action='store_true',
                        help='Generate visualizations for skill relationships')
    
    parser.add_argument('--update-job-files', action='store_true',
                        help='Update job files with enriched skills')
    
    parser.add_argument('--max-jobs', type=int, 
                        help='Maximum number of jobs to update with enriched skills')
    
    parser.add_argument('--job-ids', type=str, nargs='+', 
                        help='Specific job IDs to update (overrides max-jobs)')
    
    args = parser.parse_args()
    
    enriched_skills = None
    relationships = None
    visualizations = {}
    
    if args.load_existing:
        # Load existing enriched skills and relationships
        enriched_skills_file = os.path.join(OUTPUT_DIR, 'enriched_skills.json')
        relationships_file = os.path.join(OUTPUT_DIR, 'skill_relationships.json')
        
        try:
            with open(enriched_skills_file, 'r') as f:
                enriched_skills = json.load(f)
            
            with open(relationships_file, 'r') as f:
                relationships = json.load(f)
                
            logger.info(f"Loaded {len(enriched_skills)} existing enriched skills")
            logger.info(f"Loaded relationships for {len(relationships)} skills")
            
            # Run just the validation and/or matching steps if requested
            if not args.skip_validation:
                validation_utils.validate_skill_enrichment(enriched_skills_file)
            
            if args.test_matching:
                matching_results = test_utils.test_domain_aware_matching(enriched_skills, relationships)
                matching_results["metrics"] = test_utils.calculate_match_metrics(matching_results)
                
                matching_file = os.path.join(OUTPUT_DIR, 'matching_results.json')
                with open(matching_file, 'w') as f:
                    json.dump(matching_results, f, indent=2)
                logger.info(f"Matching test results saved to {matching_file}")
            
            if args.generate_visualizations:
                visualizations = sdr_pipeline.generate_visualizations(enriched_skills, relationships)
                logger.info(f"Generated {len(visualizations)} visualizations")
                
            if args.apply_feedback:
                enriched_skills, quality_report = sdr_pipeline.apply_expert_feedback(enriched_skills)
                logger.info("Applied expert feedback and generated quality report")
            
        except Exception as e:
            logger.error(f"Error loading existing files: {e}")
            logger.info("Falling back to generating new enriched skills")
            args.load_existing = False
    
    if not args.load_existing:
        # Run the full implementation
        enriched_skills, relationships, visualizations = run_sdr_implementation(
            use_llm=args.use_llm,
            max_skills=args.max_skills,
            validate_enrichment=not args.skip_validation,
            test_matching=args.test_matching,
            apply_feedback=args.apply_feedback,
            update_job_files=args.update_job_files,
            max_jobs=args.max_jobs,
            job_ids=args.job_ids,
            generate_visualizations=args.generate_visualizations,
            force_reprocess=getattr(args, 'force_reprocess', False)
        )
    
    # Print summary
    print("\n===== Enhanced SDR Implementation Summary =====")
    print(f"Enriched skills: {len(enriched_skills) if enriched_skills else 0}")
    print(f"Domain relationships: {sum(len(relations) for relations in relationships.values()) if relationships else 0}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Print samples
    if enriched_skills:
        print("\nSample skill enrichment for:", enriched_skills[0]["name"])
        print(f"- Category: {enriched_skills[0]['category']}")
        print(f"- Knowledge components: {enriched_skills[0]['knowledge_components']}")
        print(f"- Proficiency levels: {len(enriched_skills[0]['proficiency_levels'])} defined")
        
        if args.test_matching:
            print("\nDomain-aware matching test results:")
            matching_file = os.path.join(OUTPUT_DIR, 'matching_results.json')
            try:
                with open(matching_file, 'r') as f:
                    matching_results = json.load(f)
                
                false_positives_avoided = len(matching_results.get("false_positives_avoided", []))
                metrics = matching_results.get("metrics", {})
                print(f"- False positives avoided: {false_positives_avoided}")
                print(f"- False positive reduction: {metrics.get('false_positive_reduction', 0):.2f}%")
                print(f"- Average matches per job: {metrics.get('average_matches_per_job', 0):.2f}")
                print(f"- Full results available in {matching_file}")
            except Exception as e:
                print(f"- Error reading matching results: {e}")
        
        if args.apply_feedback:
            print("\nContinuous learning results:")
            quality_reports = [f for f in os.listdir(OUTPUT_DIR) if f.startswith('quality_report_')]
            if quality_reports:
                latest_report = sorted(quality_reports)[-1]
                report_path = os.path.join(OUTPUT_DIR, latest_report)
                try:
                    with open(report_path, 'r') as f:
                        report = json.load(f)
                    
                    print(f"- Average quality score: {report.get('average_quality_score', 0):.2f}")
                    print(f"- Consistency issues found: {report.get('issue_count', 0)}")
                    print(f"- Feedback applied to {report.get('feedback_applied_count', 0)} skills")
                except Exception as e:
                    print(f"- Error reading quality report: {e}")
        
        if args.generate_visualizations and visualizations:
            print("\nVisualizations generated:")
            for viz_type, path in visualizations.items():
                print(f"- {viz_type}: {path}")
        
        print("===========================================\n")

if __name__ == "__main__":
    main()
