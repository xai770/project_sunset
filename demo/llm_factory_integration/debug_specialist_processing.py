#!/usr/bin/env python3
"""
Debug script to understand why specialists return mock data instead of real LLM processing
"""

import sys
import os

# Add LLM Factory to path
llm_factory_path = "/home/xai/Documents/llm_factory"
if llm_factory_path not in sys.path:
    sys.path.insert(0, llm_factory_path)

def debug_specialist_processing():
    """Debug specialist processing step by step"""
    print("🔍 Debug: Specialist Processing Deep Dive")
    print("=" * 60)
    
    try:
        # Import required modules
        from llm_factory.core.ollama_client import OllamaClient
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        from llm_factory.core.types import ModuleConfig
        
        # 1. Test Ollama client first
        print("\n1️⃣ Testing Ollama Client")
        print("-" * 30)
        client = OllamaClient()
        models = client.available_models()
        print(f"✅ Ollama client working: {len(models)} models")
        
        # Test generation directly
        test_prompt = "Summarize this in one sentence: Artificial intelligence is transforming the world."
        selected_model = "phi3:latest" if "phi3:latest" in models else models[0] if models else "phi3"
        print(f"🤖 Testing direct generation with {selected_model}")
        
        direct_result = client.generate(selected_model, test_prompt)
        print(f"✅ Direct generation result: {direct_result[:100]}...")
        
        # 2. Test specialist configuration
        print("\n2️⃣ Testing Specialist Configuration")
        print("-" * 30)
        
        registry = SpecialistRegistry()
        
        # Create config with Ollama client
        config = ModuleConfig(
            models=[selected_model],
            conservative_bias=True,
            quality_threshold=7.0,
            ollama_client=client  # Make sure client is passed
        )
        
        print(f"✅ Config created with model: {config.models}")
        print(f"✅ Config has ollama_client: {hasattr(config, 'ollama_client')}")
        
        # 3. Load specialist
        print("\n3️⃣ Loading Text Summarization Specialist")
        print("-" * 30)
        
        specialist = registry.load_specialist("text_summarization", config)
        print(f"✅ Specialist loaded: {type(specialist)}")
        print(f"✅ Specialist name: {getattr(specialist, 'name', 'Unknown')}")
        
        # Check if specialist has ollama_client
        if hasattr(specialist, 'ollama_client'):
            print(f"✅ Specialist has ollama_client: {specialist.ollama_client}")
        elif hasattr(specialist, 'config') and hasattr(specialist.config, 'ollama_client'):
            print(f"✅ Specialist config has ollama_client: {specialist.config.ollama_client}")
        else:
            print("❌ Specialist missing ollama_client")
        
        # 4. Test specialist processing with verbose output
        print("\n4️⃣ Testing Specialist Processing")
        print("-" * 30)
        
        sample_text = """
        Artificial Intelligence has revolutionized many industries. Machine learning algorithms 
        now power recommendation systems, autonomous vehicles, and virtual assistants. However, 
        challenges remain in AI ethics and data privacy.
        """
        
        print("📄 Input text prepared")
        print(f"📏 Text length: {len(sample_text)} characters")
        
        # Process with detailed error handling
        try:
            print("🤖 Calling specialist.process()...")
            result = specialist.process({"content": sample_text})
            
            print(f"✅ Processing complete. Success: {result.success}")
            print(f"✅ Processing time: {result.processing_time:.2f}s")
            
            if result.success:
                print(f"✅ Data keys: {list(result.data.keys())}")
                
                summary = result.data.get('summary', '')
                print(f"📝 Summary length: {len(summary)} characters")
                print(f"📝 Summary preview: {summary[:200]}...")
                
                # Check if summary looks like mock data
                if "mock" in summary.lower() or "testing purposes" in summary.lower():
                    print("⚠️  Summary appears to be mock data")
                else:
                    print("✅ Summary appears to be real AI-generated content")
                    
            else:
                print("❌ Processing failed")
                if result.data and 'error' in result.data:
                    print(f"❌ Error: {result.data['error']}")
                    
            # Check validation
            if result.validation:
                print(f"✅ Validation score: {result.validation.quality_score}")
                if result.validation.issues:
                    print(f"⚠️  Validation issues: {result.validation.issues}")
                    
        except Exception as e:
            print(f"❌ Exception during processing: {e}")
            import traceback
            traceback.print_exc()
            
        # 5. Check specialist internals
        print("\n5️⃣ Checking Specialist Internals")
        print("-" * 30)
        
        # Check if it's a factory-based specialist
        if hasattr(specialist, 'factory'):
            print(f"✅ Specialist has factory: {type(specialist.factory)}")
            if hasattr(specialist.factory, 'config'):
                print(f"✅ Factory has config: {specialist.factory.config}")
        
        # Check available methods
        specialist_methods = [method for method in dir(specialist) if not method.startswith('_')]
        print(f"✅ Specialist methods: {specialist_methods}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_specialist_processing()
