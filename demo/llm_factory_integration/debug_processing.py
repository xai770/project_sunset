#!/usr/bin/env python3
"""
Quick test of specialist processing to understand why result.data is empty
"""

import sys
sys.path.insert(0, "/home/xai/Documents/llm_factory")

def test_specialist_processing():
    """Test specialist processing in detail."""
    print("🔍 Debugging Specialist Processing")
    print("=" * 50)
    
    try:
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        from llm_factory.core.types import ModuleConfig
        
        # Initialize
        registry = SpecialistRegistry()
        config = ModuleConfig(
            models=["phi3:latest"],  # Use available model
            conservative_bias=True,
            quality_threshold=8.0
        )
        
        # Load specialist
        specialist = registry.load_specialist("text_summarization", config)
        print(f"✅ Specialist loaded: {type(specialist).__name__}")
        
        # Test input with different formats
        test_inputs = [
            {"text": "This is a simple test. Machine learning is great."},
            "This is a simple test. Machine learning is great.",  # String format
        ]
        
        for i, test_input in enumerate(test_inputs, 1):
            print(f"\n🧪 Test {i}: Input format = {type(test_input).__name__}")
            print(f"📤 Input: {test_input}")
            
            try:
                result = specialist.process(test_input)
                print(f"📥 Result type: {type(result)}")
                
                # Analyze result
                if hasattr(result, 'data'):
                    print(f"📊 Data keys: {list(result.data.keys()) if result.data else 'No data'}")
                    print(f"📊 Data content: {result.data}")
                else:
                    print("❌ Result has no 'data' attribute")
                
                # Check other attributes
                if hasattr(result, '__dict__'):
                    print(f"🔍 All result attributes: {list(result.__dict__.keys())}")
                    
                print(f"✅ Processing successful for test {i}")
                
            except Exception as e:
                print(f"❌ Processing failed for test {i}: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specialist_processing()
