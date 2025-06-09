#!/usr/bin/env python3
"""
LLM Factory - Comprehensive Customer Demo

Copy this script to your project directory (e.g., /home/xai/Documents/sunset/)
and run it to test ALL LLM Factory specialists.

Requirements:
    - Ollama running with llama3.2:latest model
    - LLM Factory located at /home/xai/Documents/llm_factory

Usage:
    python customer_demo.py                          # Run all specialists
    python customer_demo.py --specialist <name>      # Run specific specialist
    python customer_demo.py --list                   # List all specialists
    python customer_demo.py --quick                  # Run quick subset of specialists
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
        if 'llama3.2:latest' in [model['name'] if isinstance(model, dict) else model for model in models]: # type: ignore
            print("✅ llama3.2:latest model found")
            return client, 'llama3.2:latest'
        elif models:
            model_name = models[0]['name'] if isinstance(models[0], dict) else models[0] # type: ignore
            print(f"⚠️  llama3.2 not found, using: {model_name}")
            return client, model_name
        else:
            print("❌ No models found. Run: ollama pull llama3.2:latest")
            return None, None
            
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return None, None

def get_base_config(client, model):
    """Get base configuration for all specialists."""
    from llm_factory.core.types import ModuleConfig
    return ModuleConfig(
        models=[model] if model else ["phi3:latest"],
        conservative_bias=True,
        quality_threshold=8.0,
        ollama_client=client
    )

def run_specialist_demo(specialist_name, input_data, client, model, description=""):
    """Generic function to run any specialist demo."""
    print(f"\n{description}")
    print("-" * 50)
    
    try:
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        
        registry = SpecialistRegistry()
        config = get_base_config(client, model)
        specialist = registry.load_specialist(specialist_name, config)
        
        print(f"🤖 Processing with {specialist_name} specialist...")
        result = specialist.process(input_data)
        
        print("\n📊 Results:")
        for key, value in result.data.items():
            if key not in ['response_time', 'status']:
                if isinstance(value, list) and len(value) > 3:
                    print(f"   {key}: {value[:3]}... (+{len(value)-3} more)")
                elif isinstance(value, str) and len(value) > 200:
                    print(f"   {key}: {value[:200]}...")
                else:
                    print(f"   {key}: {value}")
        
        print(f"\n⚡ Response time: {result.processing_time:.2f}s")
        print(f"✅ Status: {'Success' if result.success else 'Failed'}")
        
    except Exception as e:
        print(f"❌ {specialist_name} demo failed: {e}")

def demo_text_summarization(client, model):
    """Demo text summarization specialist."""
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
    
    input_data = {"content": sample_text.strip()}
    run_specialist_demo("text_summarization", input_data, client, model, 
                       "🔍 Text Summarization Demo")

def demo_job_fitness_evaluator(client, model):
    """Demo job fitness evaluator specialist."""
    job_posting = {
        "title": "Software Developer - Python/AI",
        "description": """We are seeking a skilled Software Developer with experience in Python, 
        machine learning, and AI technologies. The ideal candidate will have:
        - 3+ years Python development experience
        - Experience with ML frameworks (TensorFlow, PyTorch)
        - Knowledge of REST APIs and web development
        - Strong problem-solving skills
        - Bachelor's degree in Computer Science or related field""",
        "requirements": ["Python", "Machine Learning", "TensorFlow", "REST APIs", "Computer Science degree"],
        "company": "TechCorp"
    }
    
    candidate_profile = {
        "name": "John Smith",
        "experience": "4 years Python development",
        "skills": ["Python", "Machine Learning", "TensorFlow", "Flask", "Docker", "Git"],
        "education": "BS Computer Science, State University",
        "previous_roles": ["Software Engineer at Tech Corp"],
        "achievements": ["Led team of 3 developers on AI chatbot project", "Built ML models using TensorFlow"]
    }
    
    input_data = {
        "job_posting": job_posting,
        "candidate_profile": candidate_profile
    }
    
    run_specialist_demo("job_fitness_evaluator", input_data, client, model,
                       "💼 Job Fitness Evaluator Demo")

def demo_cover_letter_generator(client, model):
    """Demo cover letter generator specialist."""
    input_data = {
        "job_data": {
            "title": "Marketing Manager",
            "company": "TechCorp",
            "description": "We are seeking a dynamic Marketing Manager to lead our digital marketing initiatives.",
            "requirements": ["5+ years marketing experience", "Digital marketing expertise", "Team leadership"]
        },
        "cv_data": {
            "name": "Sarah Johnson",
            "experience": "5 years digital marketing experience",
            "skills": ["Digital Marketing", "SEO", "Content Strategy", "Team Leadership"],
            "achievements": ["Increased web traffic by 150%", "Led team of 8 marketers"]
        }
    }
    
    run_specialist_demo("cover_letter_generator", input_data, client, model,
                       "📝 Cover Letter Generator Demo")

def demo_consensus_engine(client, model):
    """Demo consensus engine specialist."""
    input_data = {
        "job_posting": {
            "title": "Senior Software Engineer",
            "description": "We're looking for an experienced software engineer to join our team.",
            "requirements": [
                "5+ years of software development experience",
                "Proficiency in Python and JavaScript",
                "Experience with cloud platforms (AWS/Azure)",
                "Strong problem-solving skills"
            ],
            "company": "TechCorp Inc."
        },
        "candidate_profile": {
            "name": "Jane Doe",
            "skills": ["Python", "JavaScript", "AWS", "Docker", "React"],
            "experience": "6 years of full-stack development",
            "education": "BS Computer Science",
            "achievements": [
                "Led team of 4 developers",
                "Reduced deployment time by 40%",
                "Built scalable microservices architecture"
            ]
        }
    }
    
    run_specialist_demo("consensus_engine", input_data, client, model,
                       "🤝 Consensus Engine Demo")

def demo_document_analysis(client, model):
    """Demo document analysis specialist."""
    input_data = {
        "document_text": "This document contains technical specifications for our new AI system. It includes performance metrics, architecture details, and implementation guidelines. The system shows 95% accuracy in natural language processing tasks and can handle 1000 concurrent requests. Implementation requires Python 3.8+, Docker, and Redis for caching."
    }
    
    run_specialist_demo("document_analysis", input_data, client, model,
                       "📄 Document Analysis Demo")

def demo_feedback_processor(client, model):
    """Demo feedback processor specialist."""
    input_data = {
        "feedback_data": {
            "content": "The application process was confusing and took too long. However, the interview was well structured.",
            "source": "job_application_feedback",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    }
    
    run_specialist_demo("feedback_processor", input_data, client, model,
                       "💬 Feedback Processor Demo")

def demo_factual_consistency(client, model):
    """Demo factual consistency specialist."""
    input_data = {
        "text": "Paris is the capital of France and has a population of 12 million people.",
        "claims_to_verify": ["Paris is the capital of France", "Paris has 12 million people"]
    }
    
    run_specialist_demo("factual_consistency", input_data, client, model,
                       "✅ Factual Consistency Demo")

def demo_llm_skill_extractor(client, model):
    """Demo LLM skill extractor specialist."""
    input_data = {
        "text": """John Smith is a highly experienced senior software engineer with over 8 years of comprehensive experience in 
        full-stack development and artificial intelligence technologies. His technical expertise spans multiple programming 
        languages including Python, JavaScript, Java, and C++, with deep specialization in machine learning frameworks 
        such as TensorFlow, PyTorch, and Scikit-learn. John has extensive experience in REST API design and implementation, 
        microservices architecture, and cloud deployment strategies across AWS, Azure, and Google Cloud Platform.
        
        Throughout his career, John has demonstrated proficiency in Docker containerization, Kubernetes orchestration, 
        and CI/CD pipeline development using Jenkins and GitLab. His database expertise includes both SQL databases 
        (PostgreSQL, MySQL) and NoSQL solutions (MongoDB, Redis). John is well-versed in version control systems, 
        particularly Git, and follows agile development methodologies including Scrum and Kanban.
        
        In his recent projects, John has led teams of 5-10 developers in building scalable web applications using React, 
        Angular, and Vue.js for frontend development, while implementing robust backend solutions with Django, Flask, 
        Node.js, and Express.js. His artificial intelligence work includes developing neural networks for computer vision, 
        natural language processing models, and recommendation systems that have improved user engagement by 40%.
        
        John holds multiple industry certifications including AWS Solutions Architect Professional, Google Cloud 
        Professional Data Engineer, and Certified Kubernetes Administrator. He has experience with automated testing 
        frameworks including pytest, Jest, and Selenium, and has implemented comprehensive monitoring solutions using 
        Prometheus, Grafana, and ELK stack. His project management experience includes working with stakeholders, 
        conducting code reviews, and mentoring junior developers.""",
        "context": "detailed_resume_analysis"
    }
    
    run_specialist_demo("llm_skill_extractor", input_data, client, model,
                       "🔍 LLM Skill Extractor Demo")

def demo_language_coherence(client, model):
    """Demo language coherence specialist."""
    input_data = {
        "text": "The meeting will start at 3pm. Also we need to discuss budget. The quarterly results were good."
    }
    
    run_specialist_demo("language_coherence", input_data, client, model,
                       "📝 Language Coherence Demo")

def demo_ai_language_detection(client, model):
    """Demo AI language detection specialist."""
    input_data = {
        "text": "This text was generated by an AI system to demonstrate natural language processing capabilities."
    }
    
    run_specialist_demo("ai_language_detection", input_data, client, model,
                       "🤖 AI Language Detection Demo")

def demo_cover_letter_quality(client, model):
    """Demo cover letter quality specialist."""
    input_data = {
        "cover_letter": "Dear Hiring Manager, I am writing to express my interest in the Software Developer position. I have experience in Python and machine learning. Thank you for your consideration.",
        "job_description": "Software Developer position requiring Python, machine learning, and 3+ years experience."
    }
    
    run_specialist_demo("cover_letter_quality", input_data, client, model,
                       "📊 Cover Letter Quality Demo")

def demo_adversarial_prompt_generator(client, model):
    """Demo adversarial prompt generator specialist."""
    input_data = {
        "original_prompt": "Write a professional email to a client",
        "domain": "business_communication",
        "intensity": "moderate"
    }
    
    run_specialist_demo("adversarial_prompt_generator", input_data, client, model,
                       "⚔️ Adversarial Prompt Generator Demo")

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
    # List of all available specialists (based on actual registry)
    all_specialists = [
        'job_fitness_evaluator', 'text_summarization', 'adversarial_prompt_generator',
        'consensus_engine', 'document_analysis', 'feedback_processor',
        'factual_consistency', 'llm_skill_extractor', 'language_coherence',
        'cover_letter_generator', 'ai_language_detection', 'cover_letter_quality'
    ]
    
    # Quick subset for faster testing
    quick_specialists = [
        'text_summarization', 'job_fitness_evaluator', 'consensus_engine', 'document_analysis'
    ]
    
    parser = argparse.ArgumentParser(description='LLM Factory Customer Demo')
    parser.add_argument('--specialist', type=str, 
                       choices=all_specialists,
                       help='Run specific specialist demo')
    parser.add_argument('--list', action='store_true',
                       help='List all available specialists')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick subset of specialists')
    
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
        print("   2. Install model: ollama pull llama3.2:latest")
        return
    
    # Specialist demo functions mapping
    demo_functions = {
        'text_summarization': demo_text_summarization,
        'job_fitness_evaluator': demo_job_fitness_evaluator,
        'cover_letter_generator': demo_cover_letter_generator,
        'consensus_engine': demo_consensus_engine,
        'document_analysis': demo_document_analysis,
        'feedback_processor': demo_feedback_processor,
        'factual_consistency': demo_factual_consistency,
        'llm_skill_extractor': demo_llm_skill_extractor,
        'language_coherence': demo_language_coherence,
        'ai_language_detection': demo_ai_language_detection,
        'cover_letter_quality': demo_cover_letter_quality,
        'adversarial_prompt_generator': demo_adversarial_prompt_generator
    }
    
    # Run specific specialist
    if args.specialist:
        if args.specialist in demo_functions:
            demo_functions[args.specialist](client, model)
        else:
            print(f"❌ Unknown specialist: {args.specialist}")
        return
    
    # Choose which specialists to run
    specialists_to_run = quick_specialists if args.quick else all_specialists
    
    print(f"\n🚀 Running {'Quick' if args.quick else 'All'} Specialist Demos")
    print(f"📊 Testing {len(specialists_to_run)} specialists...")
    
    # Run all selected demos
    for i, specialist_name in enumerate(specialists_to_run, 1):
        print(f"\n{'='*60}")
        print(f"Demo {i}/{len(specialists_to_run)}: {specialist_name}")
        print(f"{'='*60}")
        
        if specialist_name in demo_functions:
            demo_functions[specialist_name](client, model)
        else:
            print(f"❌ Demo function not found for: {specialist_name}")
    
    print(f"\n🎉 {'Quick' if args.quick else 'All'} Demos Complete!")
    print(f"\n📋 Summary: Tested {len(specialists_to_run)} specialists")
    
    if args.quick:
        print("\nTo run all specialists:")
        print("   python customer_demo.py")
    
    print("\nTo run specific specialists:")
    print("   python customer_demo.py --specialist text_summarization")
    print("   python customer_demo.py --specialist job_fitness_evaluator")
    print("   python customer_demo.py --list")

if __name__ == "__main__":
    main()
