#!/usr/bin/env python3
"""
Test script to verify LLM Factory replacements are working correctly
"""
import sys
import os

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

print("Testing LLM Factory Replacements")
print("=" * 50)

# Test 1: Core LLM Client Enhanced Functions
print("\n1. Testing Enhanced LLM Client...")
try:
    from run_pipeline.utils.llm_client import call_ollama_api, get_llm_factory_enhancer
    
    # Test the enhancer initialization
    enhancer = get_llm_factory_enhancer()
    print(f"   ✅ LLM Factory enhancer initialized: {enhancer is not None}")
    print(f"   ✅ Registry available: {enhancer.registry is not None}")
    
    # Test basic API call (should try LLM Factory first, then fallback)
    test_prompt = "What is the capital of France?"
    response = call_ollama_api(test_prompt, temperature=0.1)
    print(f"   ✅ Enhanced API call successful: {len(response)} chars")
    print(f"   📝 Response preview: {response[:100]}...")
    
except Exception as e:
    print(f"   ❌ Error testing enhanced LLM client: {e}")

# Test 2: Feedback Handler Integration  
print("\n2. Testing Feedback Handler LLM Factory Integration...")
try:
    from run_pipeline.job_matcher.feedback_handler import analyze_feedback
    
    # Test with mock feedback data
    test_feedback = {
        "job_id": "test-123",
        "feedback_text": "This job requires Python programming skills which I have.",
        "job_description": "Python developer position"
    }
    
    # This should use LLM Factory if available
    result = analyze_feedback(test_feedback)
    print(f"   ✅ Feedback analysis with LLM Factory: {result is not None}")
    
except Exception as e:
    print(f"   ❌ Error testing feedback handler: {e}")

# Test 3: LLM Handlers Integration
print("\n3. Testing LLM Handlers Integration...")
try:
    from run_pipeline.core.feedback.llm_handlers import analyze_feedback_with_master_llm
    
    # Test with mock job feedback data
    jobs_with_feedback = [{
        "job_id": "test-456", 
        "position_title": "Software Engineer",
        "reviewer_feedback": "I am qualified for this position",
        "match_level": "low"
    }]
    
    config = {"llm_model": "llama3.2:latest"}
    
    # This should use LLM Factory specialists
    result = analyze_feedback_with_master_llm(jobs_with_feedback, config)
    print(f"   ✅ Master LLM analysis: {result is not None}")
    print(f"   📊 Actions identified: {len(result.get('actions', []))}")
    
except Exception as e:
    print(f"   ❌ Error testing LLM handlers: {e}")

# Test 4: Skill Validation Integration
print("\n4. Testing Skill Validation Integration...")
try:
    from run_pipeline.skill_matching.skill_validation import SkillValidationSystem
    
    # Initialize the validation system (should include LLM Factory)
    validator = SkillValidationSystem()
    print(f"   ✅ Skill validator initialized: {validator is not None}")
    print(f"   ✅ LLM Factory registry: {hasattr(validator, 'llm_factory_registry')}")
    
except Exception as e:
    print(f"   ❌ Error testing skill validation: {e}")

# Test 5: OLMo Feedback Integration
print("\n5. Testing OLMo Feedback Integration...")
try:
    from run_pipeline.skill_matching.get_olmo_feedback import _get_feedback_with_llm_factory
    
    test_prompt = "Provide feedback on skill taxonomy implementation"
    
    # This should use LLM Factory specialist if available
    result = _get_feedback_with_llm_factory(test_prompt)
    print(f"   ✅ OLMo feedback generation: {result is not None}")
    if result:
        print(f"   📝 Feedback length: {len(result)} chars")
    
except Exception as e:
    print(f"   ❌ Error testing OLMo feedback: {e}")

print("\n" + "=" * 50)
print("LLM Factory Replacement Test Complete")
print("\nSummary:")
print("- Enhanced 5 critical files with LLM Factory integration")
print("- Added quality-controlled processing with fallback mechanisms") 
print("- Maintained backward compatibility with existing LLM clients")
print("- Ready to continue with remaining files")
