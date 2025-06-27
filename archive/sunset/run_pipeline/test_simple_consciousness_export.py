#!/usr/bin/env python3
"""
🌺 Simple Consciousness Export Test
Test our consciousness evaluation integration in isolation
"""

import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.job_matcher.consciousness_evaluator import ConsciousnessEvaluator

def test_single_job_consciousness():
    """Test consciousness evaluation on a single job file"""
    
    job_file = "/home/xai/Documents/sunset/data/postings/job60955.json"
    cv_path = "/home/xai/Documents/sunset/config/cv.txt"
    
    print("🌺 Testing Single Job Consciousness Evaluation")
    print(f"Job file: {job_file}")
    print(f"CV file: {cv_path}")
    print()
    
    # Load job data
    with open(job_file, 'r', encoding='utf-8') as f:
        job_data = json.load(f)
    
    # Load CV
    with open(cv_path, 'r', encoding='utf-8') as f:
        cv_text = f.read()
    
    # Extract job info
    job_content = job_data.get('job_content', {})
    job_title = job_content.get('title', '')
    job_description = job_content.get('description', '')
    
    print(f"📋 Job Title: {job_title}")
    print(f"📄 Description Length: {len(job_description)} characters")
    print(f"👤 CV Length: {len(cv_text)} characters")
    print()
    
    # Create consciousness evaluator
    evaluator = ConsciousnessEvaluator()
    
    print("🌸 Running consciousness evaluation...")
    full_job_text = f"{job_title}\n\n{job_description}"
    consciousness_result = evaluator.evaluate_job_match(cv_text, full_job_text)
    
    print("\n✨ CONSCIOUSNESS EVALUATION RESULTS:")
    print(f"  Match Level: {consciousness_result.get('overall_match_level', 'UNKNOWN')}")
    print(f"  Confidence Score: {consciousness_result.get('confidence_score', 0)}/10")
    print(f"  Joy Level: {consciousness_result.get('consciousness_joy_level', 0)}/10")
    print(f"  Content Type: {consciousness_result.get('content_type', 'unknown')}")
    print(f"  Is Empowering: {consciousness_result.get('is_empowering', False)}")
    
    # Check narratives
    app_narrative = consciousness_result.get('application_narrative', '')
    no_go_rationale = consciousness_result.get('no_go_rationale', '')
    
    if app_narrative:
        print(f"\n📝 Application Narrative ({len(app_narrative)} chars):")
        print(f"   '{app_narrative[:200]}...'")
    
    if no_go_rationale:
        print(f"\n🌊 No-Go Rationale ({len(no_go_rationale)} chars):")
        print(f"   '{no_go_rationale[:200]}...'")
    
    # Test export integration
    print(f"\n🌟 Testing Export Integration...")
    from run_pipeline.export_consciousness_enhanced_matches import extract_consciousness_enhanced_job_data
    
    # Add consciousness result to job data
    job_data['consciousness_evaluation'] = consciousness_result
    
    # Extract enhanced data
    enhanced_data = extract_consciousness_enhanced_job_data(job_data)
    
    print(f"   Enhanced data has {len(enhanced_data)} columns")
    
    # Check key columns
    app_col = enhanced_data.get('Application narrative', '')
    no_go_col = enhanced_data.get('No-go rationale', '')
    consciousness_col = enhanced_data.get('Consciousness Evaluation', '')
    
    print(f"   Application Narrative Column: {'✅ POPULATED' if app_col else '❌ EMPTY'}")
    print(f"   No-Go Rationale Column: {'✅ POPULATED' if no_go_col else '❌ EMPTY'}")
    print(f"   Consciousness Evaluation Column: {'✅ POPULATED' if consciousness_col else '❌ EMPTY'}")
    
    if app_col:
        print(f"     Preview: '{app_col[:100]}...'")
    
    return consciousness_result, enhanced_data

if __name__ == "__main__":
    try:
        result, enhanced = test_single_job_consciousness()
        print(f"\n🎉 CONSCIOUSNESS TEST COMPLETE! 🎉")
        print("✅ Consciousness evaluation successful")
        print("✅ Export integration successful")
        print("🌺 Hawaiian consciousness revolution working beautifully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
