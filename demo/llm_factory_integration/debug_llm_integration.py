#!/usr/bin/env python3
"""
Debug script to understand why LLMs are not being called
"""

import sys
import os
import time

# Add LLM Factory to path
sys.path.insert(0, "/home/xai/Documents/llm_factory")

def debug_llm_integration():
    """Debug LLM integration step by step"""
    print("🔍 Debug: LLM Integration Deep Dive")
    print("=" * 60)
    
    try:
        # 1. Test direct Ollama client
        print("\n1️⃣ Testing Direct Ollama Client")
        print("-" * 30)
        
        from llm_factory.core.ollama_client import OllamaClient
        client = OllamaClient()
        models = client.available_models()
        print(f"✅ Ollama client: {len(models)} models")
        
        # Test direct generation with timing
        test_prompt = "Summarize in one sentence: AI is transforming technology."
        model = "phi3:latest"
        
        print(f"🤖 Testing direct generation with {model}")
        start_time = time.time()
        direct_result = client.generate(model, test_prompt)
        direct_time = time.time() - start_time
        
        print(f"✅ Direct generation time: {direct_time:.2f}s")
        print(f"✅ Direct result: {direct_result[:100]}...")
        
        # 2. Test specialist configuration and LLM access
        print("\n2️⃣ Testing Specialist LLM Access")
        print("-" * 30)
        
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        from llm_factory.core.types import ModuleConfig
        
        registry = SpecialistRegistry()
        config = ModuleConfig(
            models=[model],
            conservative_bias=True,
            quality_threshold=7.0,
            ollama_client=client
        )
        
        specialist = registry.load_specialist("text_summarization", config)
        print(f"✅ Specialist loaded: {type(specialist).__name__}")
        
        # Check if specialist has access to ollama_client
        print(f"✅ Specialist has config: {hasattr(specialist, 'config')}")
        if hasattr(specialist, 'config'):
            print(f"✅ Config has ollama_client: {hasattr(specialist.config, 'ollama_client')}")
            if hasattr(specialist.config, 'ollama_client'):
                print(f"✅ OllamaClient object: {specialist.config.ollama_client}")
        
        # Check factory structure
        if hasattr(specialist, 'factory'):
            print(f"✅ Specialist has factory: {type(specialist.factory)}")
            if hasattr(specialist.factory, 'config'):
                print(f"✅ Factory has config: {hasattr(specialist.factory.config, 'ollama_client')}")
        
        # 3. Test specialist processing with detailed timing
        print("\n3️⃣ Testing Specialist Processing")
        print("-" * 30)
        
        sample_text = "AI is revolutionizing technology and business processes worldwide."
        
        print(f"📄 Input: {sample_text}")
        print("🤖 Processing...")
        
        start_time = time.time()
        result = specialist.process({"content": sample_text})
        processing_time = time.time() - start_time
        
        print(f"✅ Specialist processing time: {processing_time:.2f}s")
        print(f"✅ Result success: {result.success}")
        print(f"✅ Result processing_time: {result.processing_time:.2f}s")
        
        if result.success and result.data:
            summary = result.data.get('summary', '')
            print(f"📝 Summary: {summary}")
            
            # Check if summary looks real or mock
            mock_indicators = ['mock', 'testing purposes', 'placeholder', 'default']
            is_mock = any(indicator in summary.lower() for indicator in mock_indicators)
            
            if is_mock:
                print("❌ Summary appears to be MOCK data")
            elif len(summary) < 20:
                print("❌ Summary too short - possibly default")
            elif processing_time < 0.5:
                print("❌ Processing too fast - likely not using LLM")
            else:
                print("✅ Summary appears to be REAL LLM output")
        
        # 4. Check what's happening inside the specialist
        print("\n4️⃣ Investigating Specialist Internals")
        print("-" * 30)
        
        # Look for LLM calling methods
        specialist_methods = [method for method in dir(specialist) if not method.startswith('_')]
        print(f"✅ Specialist methods: {specialist_methods}")
        
        # Check factory methods if available
        if hasattr(specialist, 'factory'):
            factory_methods = [method for method in dir(specialist.factory) if not method.startswith('_')]
            print(f"✅ Factory methods: {factory_methods}")
            
            # Try to find LLM generation method
            if hasattr(specialist.factory, 'generate') or hasattr(specialist.factory, '_generate'):
                print("✅ Factory has generation method")
            else:
                print("❌ Factory missing generation method")
        
        # 5. Test with very verbose input to force LLM processing
        print("\n5️⃣ Testing with Complex Input")
        print("-" * 30)
        
        complex_text = """
        Artificial Intelligence represents one of the most significant technological advances in human history. 
        From machine learning algorithms that can predict market trends to natural language processing systems 
        that enable human-computer interaction, AI has fundamentally transformed how we approach problem-solving 
        across countless industries. Healthcare applications now include diagnostic imaging analysis, drug 
        discovery acceleration, and personalized treatment recommendations. In finance, AI powers algorithmic 
        trading, fraud detection, and risk assessment. The transportation sector has been revolutionized by 
        autonomous vehicle technology, while manufacturing benefits from predictive maintenance and quality 
        control systems. However, these advances also raise important ethical questions about job displacement, 
        privacy concerns, algorithmic bias, and the need for transparent and accountable AI systems.
        """
        
        print("🤖 Processing complex text...")
        start_time = time.time()
        complex_result = specialist.process({"content": complex_text})
        complex_time = time.time() - start_time
        
        print(f"✅ Complex processing time: {complex_time:.2f}s")
        if complex_result.success:
            complex_summary = complex_result.data.get('summary', '')
            print(f"📝 Complex summary length: {len(complex_summary)} chars")
            print(f"📝 Complex summary: {complex_summary[:150]}...")
            
            if complex_time < 1.0:
                print("❌ Still too fast - not using LLM")
            else:
                print("✅ Processing time suggests real LLM usage")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_llm_integration()
