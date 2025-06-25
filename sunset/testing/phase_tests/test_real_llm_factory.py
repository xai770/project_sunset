#!/usr/bin/env python3
"""
Phase 2 LLM Factory Integration Test - REAL LLM Factory Edition

Tests our enhanced job_processor.py with the ACTUAL working LLM Factory
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Add LLM Factory to Python path (using the working path from demo)
LLM_FACTORY_PATH = "/home/xai/Documents/llm_factory"
if LLM_FACTORY_PATH not in sys.path:
    sys.path.insert(0, LLM_FACTORY_PATH)

def test_actual_llm_factory_integration():
    """Test with the actual working LLM Factory"""
    try:
        # Test the correct import path from the working demo
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        from llm_factory.core.types import ModuleConfig
        from llm_factory.core.ollama_client import OllamaClient
        
        print("✅ LLM Factory imports successful!")
        
        # Test basic connection
        registry = SpecialistRegistry()
        client = OllamaClient()
        
        config = ModuleConfig(
            models=["llama3.2:latest"],
            conservative_bias=True,
            quality_threshold=8.0,
            ollama_client=client
        )
        
        print("✅ LLM Factory registry and client initialized!")
        
        # Test a simple specialist
        specialist = registry.load_specialist("text_summarization", config)
        print("✅ Specialist loaded successfully!")
        
        # Test processing
        test_input = {
            "content": "This is a test text for summarization. It contains multiple sentences to verify the LLM Factory integration is working properly with our Phase 2 enhancements."
        }
        
        result = specialist.process(test_input)
        
        if result.success:
            print(f"✅ LLM Factory processing successful!")
            print(f"Processing time: {result.processing_time:.2f}s")
            print(f"Summary preview: {str(result.data.get('summary', ''))[:100]}...")
            return True
        else:
            print(f"❌ LLM Factory processing failed")
            return False
            
    except Exception as e:
        print(f"❌ LLM Factory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase2_with_real_factory():
    """Test our Phase 2 enhancements with real LLM Factory"""
    print("🧪 Testing Phase 2 Enhanced Job Processor with REAL LLM Factory...")
    print("=" * 70)
    
    # First update our integration to use correct imports
    try:
        # Test the enhanced job processor with real factory
        from run_pipeline.job_matcher.job_processor import run_enhanced_llm_evaluation
        
        # Test data
        cv_text = """
        John Smith
        Senior Software Engineer with 5 years experience in Python, machine learning, 
        and cloud infrastructure. Proficient in AWS, Docker, Kubernetes, and agile development.
        Strong background in data analysis and AI model deployment.
        """
        
        job_description = """
        Senior Python Developer
        We are seeking an experienced Python developer to join our AI team.
        Requirements: 3+ years Python, machine learning experience, cloud platforms (AWS/Azure),
        containerization (Docker), and experience with AI model deployment.
        """
        
        print("🤖 Running enhanced evaluation with real LLM Factory...")
        result = run_enhanced_llm_evaluation(cv_text, job_description, num_runs=1)
        
        print("\n📊 Results:")
        print("-" * 30)
        print(f"Match Level: {result.get('cv_to_role_match', 'Unknown')}")
        print(f"Assessment Method: {result.get('assessment_method', 'Unknown')}")
        
        if 'llm_factory_data' in result:
            factory_data = result['llm_factory_data']
            print(f"🎯 Match Percentage: {factory_data.get('match_percentage', 'N/A')}%")
            print(f"🔍 Confidence: {factory_data.get('confidence', 'N/A')}")
            print(f"⚡ Processing Time: {factory_data.get('processing_time', 'N/A')}s")
            print("✅ LLM Factory integration WORKING!")
            return True
        else:
            print("📊 Used statistical method (fallback)")
            return False
        
    except Exception as e:
        print(f"❌ Phase 2 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Phase 2 LLM Factory Integration - REAL FACTORY TEST")
    print("=" * 80)
    
    # Test 1: Basic LLM Factory connection
    factory_test = test_actual_llm_factory_integration()
    
    if factory_test:
        print("\n" + "=" * 80)
        # Test 2: Phase 2 integration with real factory
        phase2_test = test_phase2_with_real_factory()
        
        print("\n" + "=" * 80)
        print("📋 REAL LLM Factory Test Summary:")
        print(f"Basic LLM Factory: {'✅ PASS' if factory_test else '❌ FAIL'}")
        print(f"Phase 2 Integration: {'✅ PASS' if phase2_test else '❌ FAIL'}")
        
        if factory_test and phase2_test:
            print("\n🎯 Phase 2 WITH REAL LLM FACTORY: SUCCESS!")
        elif factory_test:
            print("\n⚠️ LLM Factory works, but our integration needs fixing")
        else:
            print("\n❌ Basic LLM Factory test failed")
    else:
        print("\n❌ Cannot proceed - basic LLM Factory test failed")
