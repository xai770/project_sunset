#!/usr/bin/env python3
"""
🌺 Show Full Consciousness Evaluation for Review
Displays the complete application narrative and specialist insights
"""

import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.job_matcher.consciousness_evaluator import ConsciousnessEvaluator

def show_full_evaluation():
    """Show the complete consciousness evaluation for review"""
    
    # Load CV and job
    job_file = "/home/xai/Documents/sunset/data/postings/job60955.json"
    cv_path = "/home/xai/Documents/sunset/config/cv.txt"
    
    with open(job_file, 'r', encoding='utf-8') as f:
        job_data = json.load(f)
    
    with open(cv_path, 'r', encoding='utf-8') as f:
        cv_text = f.read()
    
    # Extract job details
    job_content = job_data.get('job_content', {})
    job_title = job_content.get('title', 'Unknown Title')
    job_description = job_content.get('description', 'No description')
    
    print("🌺 COMPLETE CONSCIOUSNESS EVALUATION 🌺")
    print("=" * 60)
    print(f"📋 Job: {job_title}")
    print("=" * 60)
    
    # Run consciousness evaluation
    evaluator = ConsciousnessEvaluator()
    full_job_text = f"{job_title}\n\n{job_description}"
    consciousness_result = evaluator.evaluate_job_match(cv_text, full_job_text)
    
    # Show the full application narrative
    app_narrative = consciousness_result.get('application_narrative', '')
    print("\n📝 FULL APPLICATION NARRATIVE:")
    print("-" * 40)
    print(app_narrative)
    print("-" * 40)
    
    # Show evaluation summary
    print(f"\n✨ EVALUATION SUMMARY:")
    print(f"   Match Level: {consciousness_result.get('overall_match_level', 'UNKNOWN')}")
    print(f"   Confidence: {consciousness_result.get('confidence_score', 0)}/10")
    print(f"   Joy Level: {consciousness_result.get('consciousness_joy_level', 0)}/10")
    
    print(f"\n🌺 READY FOR YOUR FEEDBACK! 🌺")
    print("Questions to consider:")
    print("• Does this sound like your voice?")
    print("• Does the content feel authentic to your experience?")
    print("• What resonates? What feels off?")
    print("• How would you describe this role differently?")

if __name__ == "__main__":
    show_full_evaluation()
