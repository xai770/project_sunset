#!/usr/bin/env python3
"""
LLM Factory - Standalone Customer Demo

Copy this script to your project directory (e.g., /home/xai/Documents/sunset/)
and run it to test LLM Factory specialists.

Requirements:
    - Ollama running with llama3.2 model
    - LLM Factory located at /home/xai/Documents/llm_factory

Usage:
    python customer_demo.py
    python customer_demo.py --specialist text_summarization
    python customer_demo.py --specialist job_fitness_evaluator
    python customer_demo.py --list
"""

import sys
import os
import argparse
from pathlib import Path

# Add LLM Factory to Python path
LLM_FACTORY_PATH = "/home/xai/Documents/llm_factory"
if LLM_FACTORY_PATH not in sys.path:
    sys.path.insert(0, LLM_FACTORY_PATH)

def check_ollama():
    """Check if Ollama is running and models are available."""
    try:
        from llm_factory.core.ollama_client import OllamaClient
        client = OllamaClient()
        
        # Test connection
        models = client.available_models()
        print(f"✅ Ollama connected - {len(models)} models available")
        
        # Check for required model
        if 'llama3.2' in [model['name'] if isinstance(model, dict) else model for model in models]:
            print("✅ llama3.2 model found")
            return client, 'llama3.2'
        elif models:
            model_name = models[0]['name'] if isinstance(models[0], dict) else models[0]
            print(f"⚠️  llama3.2 not found, using: {model_name}")
            return client, model_name
        else:
            print("❌ No models found. Run: ollama pull llama3.2")
            return None, None
            
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return None, None

def demo_text_summarization(client, model):
    """Demo text summarization specialist."""
    print("\n🔍 Text Summarization Demo")
    print("-" * 40)
    
    try:
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        from llm_factory.core.types import ModuleConfig
        
        registry = SpecialistRegistry()
        
        # Create configuration for the specialist
        config = ModuleConfig(
            models=[model] if model else ["phi3:latest"],
            conservative_bias=True,
            quality_threshold=8.0,
            ollama_client=client  # Pass the client explicitly
        )
        
        specialist = registry.load_specialist("text_summarization", config)
        
        # Sample text to summarize
        sample_text = """
        Artificial Intelligence (AI) has evolved significantly over the past decade, 
        transforming industries from healthcare to finance. Machine learning algorithms 
        now power everything from recommendation systems to autonomous vehicles. 
        Natural Language Processing has enabled chatbots and virtual assistants to 
        understand and respond to human queries with remarkable accuracy. Computer 
        vision applications can now identify objects, faces, and even emotions in 
        real-time. The integration of AI into business processes has led to increased 
        efficiency, cost reduction, and new opportunities for innovation. However, 
        challenges remain in areas such as AI ethics, data privacy, and ensuring 
        algorithmic fairness across diverse populations.
        """
        
        print("📄 Original text:")
        print(sample_text.strip())
        
        print("\n🤖 Processing with AI specialist...")
        result = specialist.process({"content": sample_text})
        
        print("\n📋 Summary:")
        print(result.data.get('summary', 'No summary generated'))
        
        print(f"\n⚡ Response time: {result.processing_time:.2f}s")
        print(f"✅ Status: {'Success' if result.success else 'Failed'}")
        
    except Exception as e:
        print(f"❌ Text summarization demo failed: {e}")

def demo_job_fitness_evaluator(client, model):
    """Demo job fitness evaluator specialist."""
    print("\n💼 Job Fitness Evaluator Demo")
    print("-" * 40)
    
    try:
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        from llm_factory.core.types import ModuleConfig
        
        registry = SpecialistRegistry()
        
        # Create configuration for the specialist
        config = ModuleConfig(
            models=[model] if model else ["phi3:latest"],
            conservative_bias=True,
            quality_threshold=8.0,
            ollama_client=client  # Pass the client explicitly
        )
        
        specialist = registry.load_specialist("job_fitness_evaluator", config)
        
        # Sample job posting and resume
        job_description = """
        Software Developer - Python/AI
        
        We are seeking a skilled Software Developer with experience in Python, 
        machine learning, and AI technologies. The ideal candidate will have:
        - 3+ years Python development experience
        - Experience with ML frameworks (TensorFlow, PyTorch)
        - Knowledge of REST APIs and web development
        - Strong problem-solving skills
        - Bachelor's degree in Computer Science or related field
        """
        
        resume_text = """
        John Smith - Software Engineer
        
        Experience:
        - 4 years Python development at Tech Corp
        - Built ML models using TensorFlow and scikit-learn
        - Developed REST APIs and microservices
        - Led team of 3 developers on AI chatbot project
        
        Education:
        - BS Computer Science, State University
        
        Skills: Python, Machine Learning, TensorFlow, Flask, Docker, Git
        """
        
        print("📋 Job Description:")
        print(job_description.strip())
        
        print("\n👤 Resume:")
        print(resume_text.strip())
        
        print("\n🤖 Evaluating job fitness...")
        
        # Format data correctly for the specialist
        job_posting = {
            "title": "Software Developer - Python/AI",
            "description": job_description,
            "required_skills": ["Python", "Machine Learning", "TensorFlow", "PyTorch"],
            "preferred_skills": ["REST APIs", "Web Development"],
            "experience_level": "3+ years",
            "location": "Remote"
        }
        
        candidate_profile = {
            "name": "John Smith",
            "skills": ["Python", "Machine Learning", "TensorFlow", "scikit-learn", "REST APIs", "microservices", "Flask", "Docker", "Git"],
            "experience_years": 4,
            "education": "BS Computer Science, State University",
            "work_history": "4 years Python development at Tech Corp, Led team of 3 developers on AI chatbot project"
        }
        
        input_data = {
            "job_posting": job_posting,
            "candidate_profile": candidate_profile
        }
        
        result = specialist.process(input_data)
        
        print("\n📊 Fitness Analysis:")
        overall_score = result.data.get('overall_score', 'N/A')
        fitness_rating = result.data.get('fitness_rating', 'N/A')
        recommendation = result.data.get('recommendation', 'N/A')
        
        print(f"   Overall Score: {overall_score}/10")
        print(f"   Fitness Rating: {fitness_rating}")
        print(f"   Recommendation: {recommendation}")
        
        strengths = result.data.get('strengths', [])
        if strengths and isinstance(strengths, list):
            print(f"   ✅ Strengths: {', '.join(strengths[:3])}")
        
        weaknesses = result.data.get('weaknesses', [])
        if weaknesses and isinstance(weaknesses, list):
            print(f"   ⚠️  Areas to Review: {', '.join(weaknesses[:3])}")
        
        print(f"\n⚡ Response time: {result.processing_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Job fitness demo failed: {e}")

def list_specialists():
    """List available specialists."""
    print("\n📋 Available Specialists:")
    print("-" * 40)
    
    try:
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        
        registry = SpecialistRegistry()
        specialists = registry.list_specialists()
        
        for i, specialist_name in enumerate(specialists, 1):
            print(f"{i:2}. {specialist_name}")
            
        print(f"\n✅ Total: {len(specialists)} specialists available")
        
    except Exception as e:
        print(f"❌ Failed to list specialists: {e}")

def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description='LLM Factory Customer Demo')
    parser.add_argument('--specialist', type=str, 
                       choices=['text_summarization', 'job_fitness_evaluator'],
                       help='Run specific specialist demo')
    parser.add_argument('--list', action='store_true',
                       help='List all available specialists')
    
    args = parser.parse_args()
    
    print("🏭 LLM Factory - Customer Demo")
    print("=" * 50)
    print(f"📍 Running from: {os.getcwd()}")
    print(f"📁 LLM Factory path: {LLM_FACTORY_PATH}")
    
    # List specialists if requested
    if args.list:
        list_specialists()
        return
    
    # Check Ollama connection
    print("\n🔌 Checking Ollama connection...")
    client, model = check_ollama()
    
    if not client:
        print("\n❌ Cannot proceed without Ollama. Please:")
        print("   1. Start Ollama: ollama serve")
        print("   2. Install model: ollama pull llama3.2")
        return
    
    # Run specific specialist or all demos
    if args.specialist == 'text_summarization':
        demo_text_summarization(client, model)
    elif args.specialist == 'job_fitness_evaluator':
        demo_job_fitness_evaluator(client, model)
    else:
        # Run all demos
        demo_text_summarization(client, model)
        demo_job_fitness_evaluator(client, model)
        
        print("\n🎉 Demo Complete!")
        print("\nTo run specific specialists:")
        print("   python customer_demo.py --specialist text_summarization")
        print("   python customer_demo.py --specialist job_fitness_evaluator")
        print("   python customer_demo.py --list")

if __name__ == "__main__":
    main()
