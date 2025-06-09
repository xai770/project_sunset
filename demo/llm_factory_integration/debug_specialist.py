#!/usr/bin/env python3
"""
Debug script to understand why specialists aren't generating proper output
"""

import sys
import os

# Add LLM Factory to path
llm_factory_path = "/home/xai/Documents/llm_factory"
if llm_factory_path not in sys.path:
    sys.path.insert(0, llm_factory_path)

def debug_specialist():
    """Debug specialist processing to see what's happening."""
    try:
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        from llm_factory.core.types import ModuleConfig
        from llm_factory.core.ollama_client import OllamaClient
        
        print("🔍 Debugging Specialist Processing")
        print("=" * 50)
        
        # Check Ollama connection
        client = OllamaClient()
        models = client.available_models()
        print(f"📋 Available models: {len(models)}")
        print(f"🎯 First few models: {models[:3] if models else 'None'}")
        
        # Create registry
        registry = SpecialistRegistry()
        specialists = registry.list_specialists()
        print(f"🏭 Available specialists: {len(specialists)}")
        
        # Test text summarization with debug output
        print("\n🧪 Testing Text Summarization Specialist")
        print("-" * 40)
        
        config = ModuleConfig(
            models=["phi3:latest"],  # Use available model
            conservative_bias=True,
            quality_threshold=8.0
        )
        
        specialist = registry.load_specialist("text_summarization", config)
        print(f"✅ Specialist loaded: {type(specialist)}")
        
        # Simple test input
        test_input = {"text": "This is a simple test. Machine learning is great."}
        print(f"📤 Input: {test_input}")
        
        # Process and get detailed result
        result = specialist.process(test_input)
        print(f"📥 Result type: {type(result)}")
        print(f"📊 Result data keys: {list(result.data.keys()) if hasattr(result, 'data') else 'No data attribute'}")
        print(f"🔍 Full result data: {result.data if hasattr(result, 'data') else result}")
        
        # Try to understand the result structure
        if hasattr(result, '__dict__'):
            print(f"🏗️  Result attributes: {list(result.__dict__.keys())}")
            for key, value in result.__dict__.items():
                print(f"   {key}: {type(value)} = {value}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_specialist()
