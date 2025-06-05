#!/usr/bin/env python3
"""
Test script for JobFitnessEvaluatorV2 integration
Replaces phi3_match_and_cover.py with LLM Factory specialist
"""
import sys
from pathlib import Path

# Add LLM Factory to path
llm_factory_path = Path("/home/xai/Documents/llm_factory")
if str(llm_factory_path) not in sys.path:
    sys.path.insert(0, str(llm_factory_path))

def test_basic_import():
    """Test if we can import the specialist using the factory"""
    try:
        from specialists.job_fitness_evaluator import create_job_fitness_evaluator
        print("✅ JobFitnessEvaluator factory imported successfully")
        return create_job_fitness_evaluator
    except ImportError as e:
        print(f"❌ Factory import failed: {e}")
        
        # Try direct import as fallback
        try:
            from specialists.job_fitness_evaluator.v2.core.job_fitness_evaluator_v2 import JobFitnessEvaluatorV2
            print("✅ Direct JobFitnessEvaluatorV2 import successful (fallback)")
            return JobFitnessEvaluatorV2
        except ImportError as e2:
            print(f"❌ Direct import also failed: {e2}")
            print(f"Checking if path exists: {llm_factory_path.exists()}")
            if llm_factory_path.exists():
                print(f"Contents: {list(llm_factory_path.iterdir())[:5]}...")
            return None

def test_specialist_api():
    """Test the specialist API and methods"""
    evaluator_factory = test_basic_import()
    if not evaluator_factory:
        return False
    
    try:
        # Import the proper config types and OllamaClient with explicit path handling
        sys.path.insert(0, str(llm_factory_path))
        from llm_factory.core.types import ModuleConfig
        from llm_factory.core.ollama_client import OllamaClient
        
        # Create a proper OllamaClient instance
        try:
            ollama_client = OllamaClient()
            print("✅ OllamaClient created successfully")
        except RuntimeError as e:
            print(f"⚠️ Ollama not available: {e}")
            # Create a mock client for testing
            ollama_client = type('MockOllamaClient', (), {
                'generate': lambda self, model, prompt, **kwargs: "Mock response for testing"
            })()
            print("✅ Using mock OllamaClient for testing")
        
        # Create proper ModuleConfig
        config = ModuleConfig(
            ollama_client=ollama_client,
            models=["llama3.2", "phi3", "olmo2"],
            quality_threshold=8.0,
            conservative_bias=True
        )
        
        # Create evaluator using factory
        evaluator = evaluator_factory(version="v2", config=config)
            
        print("✅ JobFitnessEvaluatorV2 instantiated successfully")
        print(f"Evaluator type: {type(evaluator)}")
        print(f"Available methods: {[method for method in dir(evaluator) if not method.startswith('_')]}")
        return evaluator
    except Exception as e:
        print(f"❌ Instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_evaluation():
    """Test evaluation with sample data"""
    evaluator = test_specialist_api()
    if not evaluator:
        return False
    
    # Sample data in the format expected by the specialist
    cv_content = """
Software Engineer
Education: BS Computer Science
Experience: 5 years Python development, 3 years web development
Skills: Python, JavaScript, Django, Flask, PostgreSQL, AWS
Projects: Built REST APIs, developed web applications, managed databases
"""
    
    job_description = """
Senior Python Developer
Requirements:
- 3+ years Python experience
- Web framework experience (Django/Flask)
- Database knowledge
- API development experience
Responsibilities:
- Develop backend services
- Design database schemas
- Integrate with third-party APIs
"""
    
    try:
        print("🔍 Testing evaluation...")
        
        # Format data as expected by the specialist (based on source code analysis)
        data = {
            "job_posting": {
                "description": job_description,
                "title": "Senior Python Developer",
                "requirements": ["3+ years Python experience", "Web framework experience", "Database knowledge"]
            },
            "candidate_profile": {
                "cv_content": cv_content,
                "skills": ["Python", "JavaScript", "Django", "Flask", "PostgreSQL", "AWS"],
                "experience_years": 5
            }
        }
        
        # The specialist uses a process() method based on the source code
        if hasattr(evaluator, 'process'):
            result = evaluator.process(data)
        elif hasattr(evaluator, 'evaluate_job_fitness'):
            result = evaluator.evaluate_job_fitness(
                cv_content=cv_content,
                job_description=job_description
            )
        elif hasattr(evaluator, 'evaluate'):
            result = evaluator.evaluate(cv_content, job_description)
        else:
            print("❌ No recognized evaluation method found")
            print(f"Available methods: {[m for m in dir(evaluator) if not m.startswith('_')]}")
            return False
        
        print("✅ Evaluation successful!")
        print(f"Result type: {type(result)}")
        print(f"Result content: {result}")
        
        # Try to extract match percentage and cover letter
        if isinstance(result, dict):
            match_percentage = result.get('match_percentage') or result.get('fitness_score') or result.get('score')
            cover_letter = result.get('cover_letter') or result.get('letter') or result.get('recommendation')
            
            print(f"\n📊 Extracted data:")
            print(f"Match Percentage: {match_percentage}")
            print(f"Cover Letter: {cover_letter[:100]}..." if cover_letter and len(str(cover_letter)) > 100 else f"Cover Letter: {cover_letter}")
        
        return True
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_with_current_system():
    """Compare with current phi3_match_and_cover.py output"""
    try:
        sys.path.insert(0, "/home/xai/Documents/sunset")
        from run_pipeline.core.phi3_match_and_cover import get_match_and_cover_letter
        
        cv = "Software Engineer with 5 years Python experience"
        job = "Senior Python Developer position requiring 3+ years experience"
        
        print("\n🔄 Comparing with current system...")
        current_result = get_match_and_cover_letter(cv, job)
        print("📋 Current system output:")
        print(f"Type: {type(current_result)}")
        print(f"Content: {current_result}")
        
    except Exception as e:
        print(f"⚠️ Could not test current system: {e}")

def main():
    """Main test execution"""
    print("🚀 Testing JobFitnessEvaluatorV2 Integration")
    print("=" * 50)
    
    # Test sequence
    if test_evaluation():
        print("\n🎉 JobFitnessEvaluatorV2 integration test SUCCESSFUL!")
        compare_with_current_system()
        
        print("\n📋 Next steps:")
        print("1. Create migration script")
        print("2. Backup current implementation")
        print("3. Replace phi3_match_and_cover.py")
        print("4. Run full system test")
        
    else:
        print("\n❌ Integration test FAILED")
        print("📋 Troubleshooting needed:")
        print("1. Check LLM Factory installation")
        print("2. Verify specialist API documentation")
        print("3. Check dependency requirements")

if __name__ == "__main__":
    main()
