#!/usr/bin/env python3
"""
Test Script for SDR Continuous Learning Integration

This script tests the continuous learning integration component of the enhanced SDR framework,
including feedback processing, quality assessment, and visualization generation.
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
try:
    from run_pipeline.skill_matching.continuous_learning import ContinuousLearningSystem
    from run_pipeline.skill_matching.sdr_continuous_learning import SDRContinuousLearningIntegration
    continuous_learning_available = True
except ImportError:
    print("Continuous learning module not available. Tests cannot run.")
    continuous_learning_available = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("continuous_learning_test")

# Constants
TEST_DIR = os.path.join(project_root, 'tests', 'output')
os.makedirs(TEST_DIR, exist_ok=True)
SKILLS_DIR = os.path.join(project_root, 'docs', 'skill_matching')
SAMPLE_FEEDBACK_DIR = os.path.join(TEST_DIR, 'sample_feedback')
os.makedirs(SAMPLE_FEEDBACK_DIR, exist_ok=True)

def create_sample_feedback() -> str:
    """
    Create sample feedback data for testing
    
    Returns:
        Path to the sample feedback file
    """
    logger.info("Creating sample feedback data for testing")
    
    # Create a sample feedback file
    sample_feedback = {
        "Python Programming": {
            "timestamp": datetime.now().isoformat(),
            "source": "expert_review",
            "rating": 4,
            "corrections": {
                "knowledge_components": "Should include data structures, algorithms, and OOP principles",
                "tools": "Should list common libraries like pandas, numpy, and frameworks like Django/Flask"
            },
            "comments": "Good definition but needs more emphasis on practical applications"
        },
        "Project Management": {
            "timestamp": datetime.now().isoformat(),
            "source": "expert_review",
            "rating": 3,
            "corrections": {
                "proficiency_levels": "Advanced level should mention portfolio management skills",
                "related_skills": "Should include risk management as a related skill"
            },
            "comments": "Mostly accurate but lacks some depth in advanced applications"
        }
    }
    
    # Save to file
    feedback_path = os.path.join(SAMPLE_FEEDBACK_DIR, 'test_feedback.json')
    with open(feedback_path, 'w') as f:
        json.dump(sample_feedback, f, indent=2)
    
    logger.info(f"Sample feedback saved to {feedback_path}")
    return feedback_path

def test_continuous_learning_system():
    """Test the continuous learning system component"""
    logger.info("=== Testing Continuous Learning System ===")
    
    if not continuous_learning_available:
        logger.error("Continuous learning modules not available. Test skipped.")
        return {}
    
    try:
        # Initialize the continuous learning system
        cl_system = ContinuousLearningSystem()
        
        # Create sample feedback
        create_sample_feedback()
        
        # Load a sample enriched skills file or create a minimal one for testing
        skills_path = os.path.join(SKILLS_DIR, 'enriched_skills.json')
        if not os.path.exists(skills_path):
            logger.info("Creating a minimal skills file for testing")
            minimal_skills = [
                {
                    "name": "Python Programming",
                    "category": "IT_Technical",
                    "knowledge_components": ["Python syntax", "functional programming"],
                    "contexts": ["software development", "data analysis"],
                    "functions": ["automation", "data processing"],
                    "proficiency_levels": {
                        "beginner": {"description": "Basic syntax", "estimated_acquisition_time": "1 month"},
                        "intermediate": {"description": "Building applications", "estimated_acquisition_time": "6 months"},
                        "advanced": {"description": "Complex systems", "estimated_acquisition_time": "1 year"}
                    },
                    "tools": ["IDLE", "PyCharm"]
                },
                {
                    "name": "Project Management",
                    "category": "Leadership_and_Management",
                    "knowledge_components": ["planning", "resource allocation"],
                    "contexts": ["business", "development teams"],
                    "functions": ["coordination", "delivery"],
                    "proficiency_levels": {
                        "beginner": {"description": "Basic concepts", "estimated_acquisition_time": "3 months"},
                        "intermediate": {"description": "Managing small projects", "estimated_acquisition_time": "1 year"},
                        "advanced": {"description": "Complex projects", "estimated_acquisition_time": "3 years"}
                    },
                    "tools": ["MS Project", "Jira"]
                }
            ]
            with open(os.path.join(TEST_DIR, 'test_skills.json'), 'w') as f:
                json.dump(minimal_skills, f, indent=2)
            skills_path = os.path.join(TEST_DIR, 'test_skills.json')
        
        # Load the skills data
        if not cl_system.load_data(skills_path):
            logger.error("Failed to load skills data")
            return {}
        
        # Configure feedback directory
        cl_system.feedback_dir = SAMPLE_FEEDBACK_DIR
        
        # Test loading expert feedback
        feedback = cl_system.load_expert_feedback(SAMPLE_FEEDBACK_DIR)
        logger.info(f"Loaded feedback for {len(feedback)} skills")
        
        # Test calculating quality scores
        quality_scores = cl_system.calculate_quality_scores()
        logger.info(f"Calculated quality scores for {len(quality_scores)} skills")
        
        # Test checking consistency
        consistency_issues = cl_system.check_consistency()
        logger.info(f"Found {len(consistency_issues)} consistency issues")
        
        # Test applying expert feedback
        updated_skills = cl_system.apply_expert_feedback()
        logger.info(f"Applied expert feedback to {sum(1 for skill in updated_skills if 'feedback_applied' in skill)} skills")
        
        # Test generating quality report
        report_path = os.path.join(TEST_DIR, 'test_quality_report.json')
        cl_system.generate_quality_report(report_path)
        logger.info(f"Generated quality report at {report_path}")
        
        # Prepare test results
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "feedback_loaded": len(feedback),
            "quality_scores": quality_scores,
            "consistency_issues": len(consistency_issues),
            "feedback_applied": sum(1 for skill in updated_skills if 'feedback_applied' in skill),
            "quality_report": report_path
        }
        
        # Save test results
        results_path = os.path.join(TEST_DIR, 'test_continuous_learning_results.json')
        with open(results_path, 'w') as f:
            json.dump(test_results, f, indent=2)
        logger.info(f"Test results saved to {results_path}")
        
        return test_results
        
    except Exception as e:
        logger.error(f"Error testing Continuous Learning System: {e}", exc_info=True)
        return {}

def test_sdr_continuous_learning_integration():
    """Test the SDR continuous learning integration"""
    logger.info("=== Testing SDR Continuous Learning Integration ===")
    
    if not continuous_learning_available:
        logger.error("Continuous learning modules not available. Test skipped.")
        return {}
    
    try:
        # Initialize the integration
        integration = SDRContinuousLearningIntegration()
        
        # Create sample feedback and skills if needed
        create_sample_feedback()
        
        # Test data loading
        skills_path = os.path.join(TEST_DIR, 'test_skills.json')
        if not os.path.exists(skills_path):
            test_continuous_learning_system()  # This will create the test skills file
        
        relationships_path = os.path.join(TEST_DIR, 'test_relationships.json')
        if not os.path.exists(relationships_path):
            # Create a minimal relationships file for testing
            minimal_relationships = {
                "Python Programming": {
                    "Project Management": {
                        "relationship": "Neighboring",
                        "similarity": 0.3
                    }
                },
                "Project Management": {
                    "Python Programming": {
                        "relationship": "Neighboring",
                        "similarity": 0.3
                    }
                }
            }
            with open(relationships_path, 'w') as f:
                json.dump(minimal_relationships, f, indent=2)
        
        # Test loading data
        if not integration.load_skill_data(skills_path, relationships_path):
            logger.error("Failed to load skill data")
            return {}
        
        # Set feedback directory
        integration.cl_system.feedback_dir = SAMPLE_FEEDBACK_DIR
        
        # Test processing feedback
        feedback_results = integration.process_feedback(generate_report=True)
        logger.info(f"Processed feedback for {feedback_results.get('feedback_processed', 0)} skills")
        
        # Test quality and consistency check
        quality_results = integration.check_quality_and_consistency()
        logger.info(f"Checked quality with average score: {quality_results.get('average_quality_score', 0):.2f}")
        
        # Test saving updated skills
        saved_path = integration.save_updated_skills(os.path.join(TEST_DIR, 'test_updated_skills.json'))
        logger.info(f"Saved updated skills to {saved_path}")
        
        # Try to generate visualizations
        try:
            visualizations = integration.generate_visualizations()
            logger.info(f"Generated {len(visualizations)} visualizations")
        except Exception as e:
            logger.warning(f"Failed to generate visualizations: {e}")
            visualizations = {}
        
        # Prepare test results
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "feedback_results": feedback_results,
            "quality_results": quality_results,
            "saved_path": saved_path,
            "visualizations_count": len(visualizations)
        }
        
        # Save test results
        results_path = os.path.join(TEST_DIR, 'test_sdr_continuous_learning_integration_results.json')
        with open(results_path, 'w') as f:
            json.dump(test_results, f, indent=2)
        logger.info(f"Test results saved to {results_path}")
        
        return test_results
        
    except Exception as e:
        logger.error(f"Error testing SDR Continuous Learning Integration: {e}", exc_info=True)
        return {}

def main():
    """Main entry point for running tests"""
    parser = argparse.ArgumentParser(description='Test the SDR Continuous Learning Integration')
    
    parser.add_argument('--component', choices=['all', 'cl_system', 'integration'],
                       default='all', help='Component to test')
    
    args = parser.parse_args()
    
    # Create test output directory
    os.makedirs(TEST_DIR, exist_ok=True)
    
    if args.component == 'all' or args.component == 'cl_system':
        # Test the continuous learning system
        cl_results = test_continuous_learning_system()
        if cl_results:
            print("\n=== Continuous Learning System Test Results ===")
            print(f"Feedback loaded: {cl_results.get('feedback_loaded', 0)}")
            print(f"Feedback applied: {cl_results.get('feedback_applied', 0)}")
            print(f"Consistency issues: {cl_results.get('consistency_issues', 0)}")
            print("===============================================\n")
    
    if args.component == 'all' or args.component == 'integration':
        # Test the SDR continuous learning integration
        integration_results = test_sdr_continuous_learning_integration()
        if integration_results:
            print("\n=== SDR Continuous Learning Integration Test Results ===")
            
            feedback_results = integration_results.get('feedback_results', {})
            print(f"Feedback processed: {feedback_results.get('feedback_processed', 0)}")
            print(f"Skills updated: {feedback_results.get('skills_updated', 0)}")
            
            quality_results = integration_results.get('quality_results', {})
            print(f"Average quality score: {quality_results.get('average_quality_score', 0):.2f}")
            
            print(f"Visualizations generated: {integration_results.get('visualizations_count', 0)}")
            print("====================================================\n")
    
if __name__ == "__main__":
    main()
