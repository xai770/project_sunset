#!/usr/bin/env python3
"""
Debug Phase 2 Integration Issues
"""

import sys
import os

# Add paths
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, '/home/xai/Documents/llm_factory')

def debug_imports():
    """Debug import issues step by step"""
    print("🔍 Debugging Phase 2 Import Issues")
    print("=" * 60)
    
    # Test 1: Basic LLM Factory imports
    print("\n1️⃣ Testing Basic LLM Factory Imports")
    try:
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        from llm_factory.core.types import ModuleConfig
        from llm_factory.core.ollama_client import OllamaClient
        print("✅ Basic LLM Factory imports successful")
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False
    
    # Test 2: Our wrapper import
    print("\n2️⃣ Testing LLM Factory Wrapper Import")
    try:
        from run_pipeline.core.llm_factory_match_and_cover import LLMFactoryJobMatcher
        print("✅ LLM Factory wrapper import successful")
    except Exception as e:
        print(f"❌ Wrapper import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Wrapper instantiation
    print("\n3️⃣ Testing Wrapper Instantiation") 
    try:
        matcher = LLMFactoryJobMatcher()
        print("✅ LLM Factory wrapper instantiation successful")
    except Exception as e:
        print(f"❌ Wrapper instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Enhanced job processor import
    print("\n4️⃣ Testing Enhanced Job Processor Import")
    try:
        from run_pipeline.job_matcher.job_processor import run_enhanced_llm_evaluation
        print("✅ Enhanced job processor import successful")
    except Exception as e:
        print(f"❌ Enhanced job processor import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Check LLM_FACTORY_AVAILABLE flag
    print("\n5️⃣ Testing LLM_FACTORY_AVAILABLE Flag")
    try:
        from run_pipeline.job_matcher.job_processor import LLM_FACTORY_AVAILABLE
        print(f"LLM_FACTORY_AVAILABLE: {LLM_FACTORY_AVAILABLE}")
        if not LLM_FACTORY_AVAILABLE:
            print("⚠️ LLM Factory marked as unavailable in job_processor")
        else:
            print("✅ LLM Factory marked as available")
    except Exception as e:
        print(f"❌ Could not check flag: {e}")
    
    # Test 6: Try enhanced evaluation 
    print("\n6️⃣ Testing Enhanced Evaluation")
    try:
        cv_text = "Test CV with Python experience"
        job_description = "Python developer position"
        result = run_enhanced_llm_evaluation(cv_text, job_description, 1)
        
        method = result.get('assessment_method', 'unknown')
        print(f"Assessment method used: {method}")
        
        if 'llm_factory' in method:
            print("✅ LLM Factory was used successfully!")
            return True
        else:
            print("⚠️ Fallback method was used")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_imports()
    print("\n" + "=" * 60)
    if success:
        print("🎯 DEBUG RESULT: LLM Factory integration working!")
    else:
        print("❌ DEBUG RESULT: Issues found that need fixing")
