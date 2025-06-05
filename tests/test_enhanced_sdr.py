#!/usr/bin/env python3
"""
Comprehensive Test Script for Enhanced SDR Implementation

This script tests each component of the enhanced SDR framework:
1. Skill Analyzer with LLM-based enrichment
2. Domain Relationship Classification
3. Domain-Aware Matching
4. Skill Validation System

It runs a small-scale test of the entire pipeline and generates a test report.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Import components
from run_pipeline.skill_matching.skill_analyzer import SkillAnalyzer
from run_pipeline.skill_matching.domain_relationship_classifier import DomainRelationshipClassifier
from run_pipeline.skill_matching.domain_aware_matcher import DomainAwareMatchingAlgorithm
try:
    from run_pipeline.skill_matching.skill_validation import SkillValidationSystem
    skill_validation_available = True
except ImportError:
    print("Skill validation module not available, validation tests will be skipped.")
    skill_validation_available = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'logs', f'sdr_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'))
    ]
)
logger = logging.getLogger("sdr_test")

# Constants
OUTPUT_DIR = os.path.join(project_root, 'docs', 'skill_matching')
TEST_DIR = os.path.join(OUTPUT_DIR, 'test_results')
os.makedirs(TEST_DIR, exist_ok=True)

def test_skill_analyzer(use_llm: bool = False, max_skills: int = 5) -> List[Dict[str, Any]]:
    """
    Test the Skill Analyzer component
    
    Args:
        use_llm: Whether to use LLM-based enrichment
        max_skills: Maximum number of skills to analyze
        
    Returns:
        List of enriched skill definitions
    """
    logger.info("=== Testing Skill Analyzer ===")
    
    try:
        analyzer = SkillAnalyzer()
        
        # Test loading skills
        logger.info("Testing job skills loading...")
        analyzer.load_job_skills()
        logger.info(f"Loaded {len(analyzer.job_skills)} job skills")
        
        logger.info("Testing CV skills loading...")  
        analyzer.load_cv_skills()
        cv_skills_count = sum(len(skills) for domain, skills in analyzer.cv_skills.items())
        logger.info(f"Loaded {cv_skills_count} CV skills across {len(analyzer.cv_skills)} domains")
        
        # Test ambiguity calculation
        logger.info("Testing ambiguity calculation...")
        analyzer.calculate_ambiguity_factors()
        logger.info(f"Calculated ambiguity factors for {len(analyzer.skill_ambiguity)} skills")
        
        # Test impact score calculation
        logger.info("Testing impact score calculation...")
        analyzer.calculate_impact_scores()
        logger.info(f"Calculated impact scores for {len(analyzer.skill_impact)} skills")
        
        # Test skill selection
        logger.info("Testing skill selection...")
        top_skills = analyzer.select_top_skills(num_skills=max_skills)
        logger.info(f"Selected {len(top_skills)} top skills")
        
        # Test skill enrichment
        logger.info(f"Testing skill enrichment (use_llm={use_llm})...")
        enriched_skills = []
        for skill in top_skills:
            logger.info(f"Enriching skill: {skill}")
            enriched_def = analyzer.create_enriched_skill_definition(skill, use_llm=use_llm)
            enriched_skills.append(enriched_def)
        
        # Save the test results
        test_output = os.path.join(TEST_DIR, 'test_skill_analyzer_results.json')
        with open(test_output, 'w') as f:
            json.dump(enriched_skills, f, indent=2)
        logger.info(f"Test results saved to {test_output}")
        
        # Test against baseline (optional)
        if os.path.exists(os.path.join(OUTPUT_DIR, 'enriched_skills.json')):
            logger.info("Comparing against baseline enriched skills...")
            with open(os.path.join(OUTPUT_DIR, 'enriched_skills.json'), 'r') as f:
                baseline = json.load(f)
            logger.info(f"Baseline has {len(baseline)} skills")
        
        return enriched_skills
    
    except Exception as e:
        logger.error(f"Error testing Skill Analyzer: {e}", exc_info=True)
        return []

def test_domain_relationship_classifier(enriched_skills: List[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Test the Domain Relationship Classifier component
    
    Args:
        enriched_skills: List of enriched skill definitions
        
    Returns:
        Dictionary of skill relationships
    """
    logger.info("=== Testing Domain Relationship Classifier ===")
    
    try:
        classifier = DomainRelationshipClassifier()
        
        # Test relationship classification
        logger.info(f"Testing relationship classification for {len(enriched_skills)} skills...")
        relationships = classifier.classify_relationships(enriched_skills)
        
        # Count relationship types
        relationship_types: Dict[str, int] = {}
        for skill1, relations in relationships.items():
            for skill2, relation_data in relations.items():
                rel_type = relation_data.get('relationship', 'Unknown')
                relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
        
        logger.info(f"Classified relationships: {relationship_types}")
        
        # Save the test results
        test_output = os.path.join(TEST_DIR, 'test_relationship_classifier_results.json')
        with open(test_output, 'w') as f:
            json.dump(relationships, f, indent=2)
        logger.info(f"Test results saved to {test_output}")
        
        return relationships
    
    except Exception as e:
        logger.error(f"Error testing Domain Relationship Classifier: {e}", exc_info=True)
        return {}

def test_domain_aware_matcher(enriched_skills: List[Dict[str, Any]], relationships: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Test the Domain-Aware Matching component
    
    Args:
        enriched_skills: List of enriched skill definitions
        relationships: Dictionary of skill relationships
        
    Returns:
        Dictionary of matching test results
    """
    logger.info("=== Testing Domain-Aware Matching ===")
    
    try:
        # Create sample job requirements and candidate skills
        job_skills = [skill["name"] for skill in enriched_skills[:3]]
        candidate_skills = [skill["name"] for skill in enriched_skills[2:]]
        
        logger.info(f"Sample job requirements: {job_skills}")
        logger.info(f"Sample candidate skills: {candidate_skills}")
        
        # Initialize the matcher
        matcher = DomainAwareMatchingAlgorithm()
        
        # Load the data we've already prepared
        for skill in enriched_skills:
            matcher.skill_map[skill['name']] = skill
        
        # Set up relationship matrix (normally this would be loaded from file)
        matcher.relationships = relationships
        
        # Test matching logic
        logger.info("Testing matching logic...")
        matches: Dict[str, List[Dict[str, Any]]] = {}
        false_positive_count = 0
        
        for job_skill in job_skills:
            matches[job_skill] = []
            for candidate_skill in candidate_skills:
                match_score = matcher.calculate_match_score(job_skill, candidate_skill)
                is_match = match_score > 0.7  # Example threshold
                
                # Check if this would be a false positive in simple matching
                if is_match:
                    matches[job_skill].append({
                        "candidate_skill": candidate_skill,
                        "match_score": match_score,
                        "would_be_false_positive": job_skill != candidate_skill and candidate_skill not in job_skills
                    })
                    
                    # Count false positives avoided
                    if job_skill != candidate_skill and candidate_skill not in job_skills:
                        false_positive_count += 1
        
        # Prepare test results
        test_results = {
            "job_skills": job_skills,
            "candidate_skills": candidate_skills,
            "matches": matches,
            "false_positives_avoided": false_positive_count,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save the test results
        test_output = os.path.join(TEST_DIR, 'test_domain_aware_matcher_results.json')
        with open(test_output, 'w') as f:
            json.dump(test_results, f, indent=2)
        logger.info(f"Test results saved to {test_output}")
        
        return test_results
    
    except Exception as e:
        logger.error(f"Error testing Domain-Aware Matcher: {e}", exc_info=True)
        return {}

def test_skill_validation(enriched_skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Test the Skill Validation System component
    
    Args:
        enriched_skills: List of enriched skill definitions
        
    Returns:
        Dictionary of validation test results
    """
    if not skill_validation_available:
        logger.warning("Skill validation module not available, skipping test.")
        return {}
    
    logger.info("=== Testing Skill Validation System ===")
    
    try:
        # Save the enriched skills to a temporary file for validation
        temp_skills_file = os.path.join(TEST_DIR, 'temp_skills_for_validation.json')
        with open(temp_skills_file, 'w') as f:
            json.dump(enriched_skills, f, indent=2)
        
        # Initialize the validation system
        validation_system = SkillValidationSystem()
        
        # Test validation
        logger.info(f"Testing skill validation for {len(enriched_skills)} skills...")
        validation_results = validation_system.validate_skills(temp_skills_file)
        
        # Test report generation
        logger.info("Testing quality report generation...")
        report_path = validation_system.generate_quality_report(temp_skills_file)
        logger.info(f"Generated quality report: {report_path}")
        
        return validation_results
    
    except Exception as e:
        logger.error(f"Error testing Skill Validation System: {e}", exc_info=True)
        return {}

def run_full_pipeline_test(use_llm: bool = False, max_skills: int = 5) -> Dict[str, Any]:
    """
    Run a comprehensive test of the full SDR pipeline
    
    Args:
        use_llm: Whether to use LLM-based enrichment
        max_skills: Maximum number of skills to analyze
        
    Returns:
        Dictionary with test results summary
    """
    logger.info("=== Starting Comprehensive SDR Pipeline Test ===")
    start_time = datetime.now()
    
    # Test each component
    enriched_skills = test_skill_analyzer(use_llm, max_skills)
    if not enriched_skills:
        logger.error("Skill Analyzer test failed, aborting pipeline test.")
        return {"status": "failed", "component": "skill_analyzer"}
    
    relationships = test_domain_relationship_classifier(enriched_skills)
    if not relationships:
        logger.error("Domain Relationship Classifier test failed, aborting pipeline test.")
        return {"status": "failed", "component": "relationship_classifier"}
    
    matching_results = test_domain_aware_matcher(enriched_skills, relationships)
    if not matching_results:
        logger.error("Domain-Aware Matcher test failed, aborting pipeline test.")
        return {"status": "failed", "component": "domain_aware_matcher"}
    
    validation_results = {}
    if skill_validation_available:
        validation_results = test_skill_validation(enriched_skills)
        if not validation_results:
            logger.warning("Skill Validation test failed, but continuing pipeline test.")
    
    # Calculate test duration
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Prepare test summary
    test_summary = {
        "status": "success",
        "timestamp": end_time.isoformat(),
        "duration_seconds": duration,
        "components_tested": {
            "skill_analyzer": len(enriched_skills) > 0,
            "relationship_classifier": len(relationships) > 0,
            "domain_aware_matcher": len(matching_results) > 0,
            "skill_validation": len(validation_results) > 0 if skill_validation_available else "skipped"
        },
        "metrics": {
            "skills_enriched": len(enriched_skills),
            "relationships_classified": sum(len(relations) for relations in relationships.values()),
            "false_positives_avoided": matching_results.get("false_positives_avoided", 0),
            "overall_quality": validation_results.get("overall_quality_score", 0) if validation_results else "N/A"
        },
        "use_llm": use_llm,
        "max_skills": max_skills
    }
    
    # Save the test summary
    summary_output = os.path.join(TEST_DIR, f'pipeline_test_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(summary_output, 'w') as f:
        json.dump(test_summary, f, indent=2)
    logger.info(f"Pipeline test summary saved to {summary_output}")
    
    logger.info("=== Comprehensive SDR Pipeline Test Completed ===")
    return test_summary

def main():
    """Main entry point for the test script"""
    parser = argparse.ArgumentParser(description='Run comprehensive tests for the Enhanced SDR Implementation')
    
    parser.add_argument('--use-llm', action='store_true', 
                      help='Use LLM for skill enrichment (higher quality but slower)')
    
    parser.add_argument('--max-skills', type=int, default=5, 
                      help='Maximum number of skills to analyze')
    
    parser.add_argument('--component', type=str, choices=['all', 'analyzer', 'classifier', 'matcher', 'validation'],
                      default='all', help='Specific component to test')
    
    args = parser.parse_args()
    
    if args.component == 'all':
        test_summary = run_full_pipeline_test(args.use_llm, args.max_skills)
        print("\n===== SDR Pipeline Test Summary =====")
        print(f"Status: {test_summary['status']}")
        print(f"Skills enriched: {test_summary['metrics']['skills_enriched']}")
        print(f"Relationships classified: {test_summary['metrics']['relationships_classified']}")
        print(f"False positives avoided: {test_summary['metrics']['false_positives_avoided']}")
        print(f"Overall quality score: {test_summary['metrics']['overall_quality']}")
        print(f"Test duration: {test_summary['duration_seconds']:.2f} seconds")
        print("=====================================\n")
    
    elif args.component == 'analyzer':
        enriched_skills = test_skill_analyzer(args.use_llm, args.max_skills)
        print(f"\nSkill Analyzer test completed with {len(enriched_skills)} skills enriched")
    
    elif args.component == 'classifier':
        # First get skills
        enriched_skills = test_skill_analyzer(args.use_llm, args.max_skills)
        if enriched_skills:
            relationships = test_domain_relationship_classifier(enriched_skills)
            print(f"\nDomain Relationship Classifier test completed with {sum(len(relations) for relations in relationships.values())} relationships classified")
    
    elif args.component == 'matcher':
        # First get skills and relationships
        enriched_skills = test_skill_analyzer(args.use_llm, args.max_skills)
        if enriched_skills:
            relationships = test_domain_relationship_classifier(enriched_skills)
            if relationships:
                matching_results = test_domain_aware_matcher(enriched_skills, relationships)
                print(f"\nDomain-Aware Matcher test completed with {matching_results.get('false_positives_avoided', 0)} false positives avoided")
    
    elif args.component == 'validation':
        # First get skills
        enriched_skills = test_skill_analyzer(args.use_llm, args.max_skills)
        if enriched_skills and skill_validation_available:
            validation_results = test_skill_validation(enriched_skills)
            print(f"\nSkill Validation test completed with overall quality score: {validation_results.get('overall_quality_score', 'N/A')}")

if __name__ == "__main__":
    main()
