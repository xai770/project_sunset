#!/usr/bin/env python3
"""
Quick test script to verify specialist functionality
"""

import sys
import os

# Add LLM Factory to path
sys.path.insert(0, "/home/xai/Documents/llm_factory")

def test_specialist():
    try:
        print("🧪 Testing Specialist Functionality")
        print("=" * 40)
        
        # Test Ollama connection
        from llm_factory.core.ollama_client import OllamaClient
        client = OllamaClient()
        models = client.available_models()
        print(f"✅ Ollama connected: {len(models)} models")
        
        # Test specialist registry
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        registry = SpecialistRegistry()
        specialists = registry.list_specialists()
        print(f"✅ Registry loaded: {len(specialists)} specialists")
        
        # Test loading a specialist
        from llm_factory.core.types import ModuleConfig
        config = ModuleConfig(
            models=["phi3:latest"],
            conservative_bias=True,
            quality_threshold=8.0
        )
        
        specialist = registry.load_specialist("text_summarization", config)
        print(f"✅ Specialist loaded: {type(specialist).__name__}")
        
        print("\n🎯 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specialist()
