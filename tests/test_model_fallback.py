#!/usr/bin/env python3
"""
Test script for model fallback system and qualification narrative improvement

This script tests:
1. The model fallback mechanism for Ollama in the skill decomposer
2. The qualification narrative changes to ensure consistency with match scores
"""

import sys
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_fallback')

# Add the project root to the Python path so we can import the modules
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    # Import the required modules
    from scripts.utils.skill_decomposer.api import try_all_models, call_ollama
    from scripts.utils.self_assessment.narrative_generator import NarrativeGenerator
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error("Make sure you're running this script from the project root directory.")
    sys.exit(1)

def test_ollama_fallback():
    """Test the Ollama model fallback mechanism"""
    logger.info("=== Testing Ollama Model Fallback Mechanism ===")
    
    # Define a simple test prompt
    test_prompt = """
    Parse this job requirement into specific skills: "Experience with software development in Python"
    Return the result as a JSON list of skill names.
    """
    
    # Test the default fallback mechanism
    logger.info("Testing model fallback with default models list...")
    model, json_content = try_all_models(test_prompt)
    
    if model:
        logger.info(f"✅ Successfully used model: {model}")
        logger.info(f"Response: {json_content}")
    else:
        logger.error("❌ All models failed to produce valid JSON")
    
    # Test with a specific list of models including a non-existent one to force fallback
    logger.info("Testing model fallback with a custom models list including a non-existent model...")
    custom_models = ["non-existent-model", "llama3.2:latest", "mistral:latest"]
    model, json_content = try_all_models(test_prompt, custom_models)
    
    if model:
        logger.info(f"✅ Successfully fell back to model: {model}")
        logger.info(f"Response: {json_content}")
    else:
        logger.error("❌ All models failed to produce valid JSON")
    
    return model is not None

def test_qualification_narrative():
    """Test the qualification narrative generation with different match scores"""
    logger.info("=== Testing Qualification Narrative Generation ===")
    
    # Define test cases with different match scores
    test_cases = [
        {"score": 0.95, "expected_level": "exceptionally qualified"},
        {"score": 0.85, "expected_level": "highly qualified"},
        {"score": 0.75, "expected_level": "well qualified"},
        {"score": 0.65, "expected_level": "qualified"},
        {"score": 0.55, "expected_level": "moderately qualified"},
        {"score": 0.45, "expected_level": "somewhat qualified"},  # New level
        {"score": 0.35, "expected_level": "minimally qualified"},  # Changed from "partially qualified"
        {"score": 0.25, "expected_level": "developing qualifications"}
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        score = test_case["score"]
        expected = test_case["expected_level"]
        actual = NarrativeGenerator._get_match_level(score)
        
        if actual == expected:
            logger.info(f"✅ Score {score:.2f} -> '{actual}' (expected: '{expected}')")
        else:
            logger.error(f"❌ Score {score:.2f} -> '{actual}' (expected: '{expected}')")
            all_passed = False
    
    # Test the full narrative generation for a low match score (33%)
    job_title = "Tax Senior Specialist"
    overall_match = 0.333
    strong_matches = []
    moderate_matches = []
    weak_matches = [("Tax Compliance", {"your_skill": "contract compliance", "match_strength": 0.8})]
    missing_skills = ["Global Tax Planning", "Steuerrechtliche Rechtsentwicklungen"]
    
    narrative = NarrativeGenerator.generate_narrative(
        job_title, overall_match, strong_matches, moderate_matches, weak_matches, missing_skills
    )
    
    logger.info(f"Full narrative for 33.3% match:")
    logger.info(narrative)
    
    # Check if the narrative contains the expected match level
    if "minimally qualified" in narrative.lower():
        logger.info("✅ Narrative correctly describes candidate as 'minimally qualified'")
    else:
        logger.error("❌ Narrative does not correctly describe qualification level")
        all_passed = False
    
    return all_passed

def test_on_actual_job_file():
    """Test the changes on an actual job file"""
    job_file = project_root / "data" / "postings" / "job61951.json"
    if not job_file.exists():
        logger.warning(f"⚠️ Job file {job_file} doesn't exist. Skipping this test.")
        return True
    
    logger.info(f"=== Testing with actual job file {job_file} ===")
    try:
        with open(job_file, 'r') as f:
            job_data = json.load(f)
        
        match_score = job_data.get("matches", {}).get("overall_match", 0)
        narrative = job_data.get("self_assessment", {}).get("qualification_narrative", "")
        
        logger.info(f"Job match score: {match_score:.2%}")
        logger.info(f"Current narrative: {narrative}")
        
        # Get what the narrative should be according to our new logic
        expected_match_level = NarrativeGenerator._get_match_level(match_score)
        logger.info(f"Expected qualification level with new logic: {expected_match_level}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing with job file: {e}")
        return False

def main():
    """Main test function"""
    logger.info("Starting model fallback and qualification narrative tests")
    
    fallback_passed = test_ollama_fallback()
    narrative_passed = test_qualification_narrative()
    job_test_passed = test_on_actual_job_file()
    
    # Print summary
    logger.info("\n=== Test Summary ===")
    logger.info(f"Model Fallback Tests: {'✅ PASSED' if fallback_passed else '❌ FAILED'}")
    logger.info(f"Qualification Narrative Tests: {'✅ PASSED' if narrative_passed else '❌ FAILED'}")
    logger.info(f"Actual Job File Test: {'✅ PASSED' if job_test_passed else '❌ FAILED'}")
    
    if fallback_passed and narrative_passed and job_test_passed:
        logger.info("\n✅ All tests passed!")
        return 0
    else:
        logger.error("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())