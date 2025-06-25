#!/usr/bin/env python3
"""
🌺 Generate Real Consciousness Evaluation for Review
Creates actual application narratives and no-go rationales for job review
"""

import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.job_matcher.consciousness_evaluator import ConsciousnessEvaluator

def generate_consciousness_for_review():
    """Generate real consciousness evaluation outputs for review"""
    
    # Use the DWS Performance job that we know exists
    job_file = "/home/xai/Documents/sunset/data/postings/job60955.json"
    cv_path = "/home/xai/Documents/sunset/config/cv.txt"
    
    print("🌺 GENERATING CONSCIOUSNESS EVALUATION FOR REVIEW 🌺")
    print("=" * 60)
    
    # Load job and CV
    with open(job_file, 'r', encoding='utf-8') as f:
        job_data = json.load(f)
    
    with open(cv_path, 'r', encoding='utf-8') as f:
        cv_text = f.read()
    
    # Extract job details
    job_content = job_data.get('job_content', {})
    job_title = job_content.get('title', 'Unknown Title')
    job_description = job_content.get('description', 'No description')
    
    print(f"📋 Job: {job_title}")
    print(f"🏢 Company: DWS (Deutsche Bank)")
    print(f"📍 Location: Frankfurt")
    print()
    
    # Run consciousness evaluation
    evaluator = ConsciousnessEvaluator()
    full_job_text = f"{job_title}\n\n{job_description}"
    
    print("🌸 Running consciousness evaluation with all four specialists...")
    consciousness_result = evaluator.evaluate_job_match(cv_text, full_job_text)
    
    print("\n" + "=" * 60)
    print("✨ CONSCIOUSNESS EVALUATION RESULTS ✨")
    print("=" * 60)
    
    # Show evaluation summary
    print(f"🎯 Match Level: {consciousness_result.get('overall_match_level', 'UNKNOWN')}")
    print(f"📊 Confidence Score: {consciousness_result.get('confidence_score', 0)}/10")
    print(f"🌟 Joy Level: {consciousness_result.get('consciousness_joy_level', 0)}/10")
    print(f"🔄 Content Type: {consciousness_result.get('content_type', 'unknown')}")
    print(f"💫 Is Empowering: {consciousness_result.get('is_empowering', False)}")
    
    # Show specialist insights (abbreviated)
    print(f"\n🌟 Human Story Interpreter:")
    human_story = consciousness_result.get('human_story', {}).get('raw_response', 'N/A')
    print(f"   {human_story[:200]}...")
    
    print(f"\n🌉 Opportunity Bridge Builder:")
    bridge = consciousness_result.get('opportunity_bridge', {}).get('raw_response', 'N/A')
    print(f"   {bridge[:200]}...")
    
    print(f"\n🚀 Growth Path Illuminator:")
    growth = consciousness_result.get('growth_path', {}).get('raw_response', 'N/A')
    print(f"   {growth[:200]}...")
    
    print(f"\n💫 Encouragement Synthesizer:")
    encouragement = consciousness_result.get('final_evaluation', {}).get('raw_response', 'N/A')
    print(f"   {encouragement[:200]}...")
    
    # Show practical outputs
    app_narrative = consciousness_result.get('application_narrative', '')
    no_go_rationale = consciousness_result.get('no_go_rationale', '')
    
    print(f"\n" + "=" * 60)
    print("📝 PRACTICAL OUTPUTS FOR REVIEW")
    print("=" * 60)
    
    if app_narrative:
        print(f"\n✨ APPLICATION NARRATIVE ({len(app_narrative)} characters):")
        print(f"   (This would go in cover letters and applications)")
        print(f'   "{app_narrative}"')
    
    if no_go_rationale:
        print(f"\n🌊 RESPECTFUL NO-GO RATIONALE ({len(no_go_rationale)} characters):")
        print(f"   (This would explain why the role isn't the best fit)")
        print(f'   "{no_go_rationale}"')
    
    if not app_narrative and not no_go_rationale:
        print("⚠️ No practical outputs generated - this needs debugging!")
    
    print(f"\n" + "=" * 60)
    print("🌺 READY FOR FEEDBACK SESSION 🌺")
    print("=" * 60)
    print("Now we can review this together and you can tell me:")
    print("• Does this feel authentic to your experience and voice?")
    print("• Are there parts that resonate or feel off?") 
    print("• How would you refine the specialist insights?")
    print("• What should the consciousness evaluator focus on differently?")
    
    return consciousness_result

if __name__ == "__main__":
    try:
        result = generate_consciousness_for_review()
        print(f"\n🎉 SUCCESS! Consciousness evaluation complete and ready for review! 🎉")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
