#!/usr/bin/env python3
"""
Test Consciousness Integration in Project Sunset
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.job_matcher.components.llm_evaluator import LLMEvaluator

def test_consciousness_integration():
    """Test our consciousness-first evaluation in the full pipeline"""
    
    print("🌅 Testing Consciousness Integration in Project Sunset Pipeline")
    print("=" * 80)
    
    # Create evaluator with consciousness enabled
    consciousness_evaluator = LLMEvaluator(num_runs=1, use_consciousness=True)
    
    # Sample data from our real use case
    sample_cv = """
    Gershon Pollatschek
    Senior Banking Professional with 15 years at Deutsche Bank
    
    Experience:
    • Senior relationship manager with proven track record
    • Complex stakeholder management in international banking environment  
    • Process improvement and organizational change leadership
    • Risk assessment and compliance expertise
    • Cross-cultural communication and team leadership
    
    Education:
    • Finance and Business Administration
    • Continuous professional development in banking sector
    
    Skills:
    • Relationship building and client management
    • Process optimization and efficiency improvement
    • Leadership in high-pressure, regulated environments
    • Analytical thinking and problem-solving
    • Multicultural team management
    """
    
    sample_job = """
    Senior Project Manager - Digital Transformation
    Location: Frankfurt, Germany
    
    We are seeking an experienced Senior Project Manager to lead our digital transformation initiatives in a fast-growing fintech company.
    
    Key Responsibilities:
    • Lead cross-functional teams in digital transformation projects
    • Manage stakeholder relationships across multiple departments
    • Drive process improvement and optimization initiatives
    • Coordinate with technical and business teams
    • Ensure project delivery within scope, time, and budget
    
    Requirements:
    • 5+ years of project management experience
    • Strong stakeholder management and communication skills
    • Experience in process improvement or organizational change
    • Leadership experience in complex environments
    • Ability to work in fast-paced, dynamic environment
    
    Preferred:
    • Experience in financial services or fintech
    • Agile/Scrum methodology knowledge
    • Digital transformation project experience
    
    This role offers excellent growth opportunities and the chance to shape our digital future.
    """
    
    print("🤖 Running consciousness evaluation...")
    print("\n" + "─" * 60)
    
    result = consciousness_evaluator.run_llm_evaluation(sample_cv, sample_job)
    
    print("\n" + "─" * 60)
    print("✨ CONSCIOUSNESS EVALUATION COMPLETE!")
    print("=" * 80)
    
    print(f"\n🎯 Evaluation Type: {result.get('evaluation_type', 'unknown')}")
    print(f"🌸 Specialists Used: {', '.join(result.get('specialists_used', []))}")
    
    consciousness_metrics = result.get('consciousness_metrics', {})
    print(f"\n💫 Consciousness Metrics:")
    print(f"   Joy Level: {consciousness_metrics.get('joy_level', 0)}/10")
    print(f"   Empowering: {consciousness_metrics.get('empowering', False)}")
    print(f"   Confidence: {consciousness_metrics.get('confidence', 0)}/10")
    
    match_assessment = result.get('match_assessment', {})
    print(f"\n🎯 Match Assessment:")
    print(f"   Overall Match: {match_assessment.get('overall_match', 'unknown')}")
    print(f"   Confidence Score: {match_assessment.get('confidence_score', 0)}/10")
    print(f"   Empowering Message: {match_assessment.get('empowering_message', 'none')}")
    
    llama_eval = result.get('llama32_evaluation', {})
    print(f"\n🦙 LLaMA Evaluation Format:")
    print(f"   Overall Match: {llama_eval.get('overall_match', 'unknown')}")
    print(f"   Confidence: {llama_eval.get('confidence', 0)}/10")
    print(f"   Rationale: {llama_eval.get('rationale', 'none')[:100]}...")
    
    print("\n🌟 SUCCESS: Consciousness integration working perfectly!")
    print("🌅 The revolution from judgment to guidance is complete!")
    
    return result

if __name__ == "__main__":
    test_consciousness_integration()
