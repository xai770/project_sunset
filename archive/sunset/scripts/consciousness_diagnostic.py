#!/usr/bin/env python3
"""
🔍 CONSCIOUSNESS SPECIALIST DIAGNOSTIC TOOL 🔍
Find exactly where our specialists are failing in the export context
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from run_pipeline.job_matcher.consciousness_evaluator import ConsciousnessEvaluator
from run_pipeline.job_matcher.cv_loader import load_cv_text

def test_single_job_full_pipeline():
    """Test the exact same flow as the export script"""
    
    print("🔍 TESTING SINGLE JOB WITH EXPORT-STYLE PROCESSING 🔍")
    print("=" * 60)
    
    # Load a real job file (same as export script does)
    job_file = "data/postings/job60955.json"
    
    try:
        with open(job_file, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
        
        print(f"✅ Loaded job file: {job_file}")
        
        # Extract job info (same as export script)
        job_content = job_data.get('job_content', {})
        job_title = job_content.get('title', '')
        job_description = job_content.get('description', '')
        
        print(f"✅ Job title: {job_title[:50]}...")
        print(f"✅ Job description: {len(job_description)} characters")
        
        # Load CV (same as export script)
        cv_text = load_cv_text()
        print(f"✅ CV loaded: {len(cv_text)} characters")
        
        # Create evaluator (same as export script)
        evaluator = ConsciousnessEvaluator()
        print("✅ Consciousness evaluator created")
        
        # Test each specialist individually first
        print("\n🌺 TESTING INDIVIDUAL SPECIALISTS:")
        print("-" * 40)
        
        try:
            print("1. Testing Human Story Interpreter...")
            story_result = evaluator._interpret_human_story(cv_text)
            story_response = story_result.get('raw_response', '') if isinstance(story_result, dict) else str(story_result)
            print(f"   Result type: {type(story_result)}")
            print(f"   Response length: {len(story_response)} chars")
            print(f"   Preview: {story_response[:100]}...")
            if len(story_response) < 200:
                print(f"   ⚠️ WARNING: Response too short! Full content: {story_response}")
        except Exception as e:
            print(f"   ❌ ERROR in Human Story: {e}")
        
        try:
            print("\n2. Testing Opportunity Bridge Builder...")
            # This needs the human story result for context
            bridge_result = evaluator._build_opportunity_bridge(story_result, job_description)
            bridge_response = bridge_result.get('raw_response', '') if isinstance(bridge_result, dict) else str(bridge_result)
            print(f"   Result type: {type(bridge_result)}")
            print(f"   Response length: {len(bridge_response)} chars")
            print(f"   Preview: {bridge_response[:100]}...")
            if len(bridge_response) < 200:
                print(f"   ⚠️ WARNING: Response too short! Full content: {bridge_response}")
        except Exception as e:
            print(f"   ❌ ERROR in Opportunity Bridge: {e}")
        
        # Test the complete evaluation (same as export script calls)
        print("\n🌟 TESTING COMPLETE EVALUATION PIPELINE:")
        print("-" * 50)
        
        try:
            full_job_text = f"{job_title}\n\n{job_description}"
            print(f"Job text length: {len(full_job_text)} chars")
            
            print("Calling evaluate_job_match...")
            consciousness_result = evaluator.evaluate_job_match(cv_text, full_job_text)
            
            print(f"✅ Complete evaluation returned!")
            print(f"Result type: {type(consciousness_result)}")
            print(f"Keys: {list(consciousness_result.keys()) if isinstance(consciousness_result, dict) else 'Not a dict'}")
            
            # Check what we actually got
            if isinstance(consciousness_result, dict):
                print("\n📋 DETAILED RESULT INSPECTION:")
                for key, value in consciousness_result.items():
                    if isinstance(value, dict):
                        print(f"   {key}: {type(value)} with keys {list(value.keys())}")
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, str) and len(sub_value) > 50:
                                print(f"      {sub_key}: {len(sub_value)} chars - {sub_value[:50]}...")
                            else:
                                print(f"      {sub_key}: {sub_value}")
                    elif isinstance(value, str) and len(value) > 50:
                        print(f"   {key}: {len(value)} chars - {value[:50]}...")
                    else:
                        print(f"   {key}: {value}")
            
        except Exception as e:
            print(f"❌ ERROR in complete evaluation: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ ERROR loading job file: {e}")

def main():
    print("🌺 CONSCIOUSNESS SPECIALIST DIAGNOSTIC 🌺\n")
    test_single_job_full_pipeline()

if __name__ == "__main__":
    main()
