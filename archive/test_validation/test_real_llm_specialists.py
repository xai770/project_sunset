#!/usr/bin/env python3
"""
Test Real LLM Specialists - Direct Ollama Integration Test
=========================================================

This script directly tests the v1_1 LLM-powered specialists to confirm
that Ollama is being used instead of hardcoded logic.

Expected behavior:
- v1_0 (hardcoded): ~0.001-0.005 seconds per job
- v1_1 (LLM): ~5-10 seconds per job

Usage:
cd /home/xai/Documents/sunset
python test_real_llm_specialists.py
"""

import sys
import json
import time
from pathlib import Path

# Add LLM Factory to path
sys.path.insert(0, '/home/xai/Documents/llm_factory')

# Import both versions for comparison
try:
    from llm_factory.modules.quality_validation.specialists_versioned.domain_classification.v1_0.src.domain_classification_specialist import classify_job_domain as classify_v1_0
    print("✅ v1_0 (hardcoded) domain classification imported")
except ImportError as e:
    print(f"❌ Failed to import v1_0: {e}")
    classify_v1_0 = None

try:
    from llm_factory.modules.quality_validation.specialists_versioned.domain_classification.v1_1.src.domain_classification_specialist_llm import classify_job_domain_llm as classify_v1_1
    print("✅ v1_1 (LLM) domain classification imported")
except ImportError as e:
    print(f"❌ Failed to import v1_1: {e}")
    classify_v1_1 = None

def load_job_data(job_id):
    """Load job data from file"""
    job_file = Path(f"/home/xai/Documents/sunset/data/postings/job{job_id}.json")
    if not job_file.exists():
        return None
    
    with open(job_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_specialists():
    print("🚀 TESTING REAL LLM SPECIALISTS vs HARDCODED")
    print("=" * 55)
    
    # Test with a few jobs
    test_jobs = [
        "57488",  # Location conflict job (Frankfurt vs Pune)
        "60955",  # Investment management job
        "58432",  # Cybersecurity job
    ]
    
    for job_id in test_jobs:
        print(f"\n🔍 Testing Job {job_id}")
        print("-" * 25)
        
        # Load job data
        job_data = load_job_data(job_id)
        if not job_data:
            print(f"❌ Could not load job {job_id}")
            continue
        
        # Extract job content
        job_content = job_data.get('job_content', {})
        print(f"📋 Job: {job_content.get('title', 'Unknown')}")
        print(f"📍 Location: {job_content.get('location', 'Not specified')}")
        
        # Prepare inputs
        job_metadata = {
            'title': job_content.get('title', ''),
            'id': job_id,
            'location': job_content.get('location', '')
        }
        job_description = job_content.get('description', '')
        
        # Test v1_0 (hardcoded)
        if classify_v1_0:
            print("\n🏃‍♂️ Testing v1_0 (hardcoded)...")
            start_time = time.time()
            try:
                result_v1_0 = classify_v1_0(job_metadata, job_description)
                v1_0_time = time.time() - start_time
                print(f"⚡ v1_0 Processing Time: {v1_0_time:.4f}s")
                print(f"📊 v1_0 Decision: {'PROCEED' if result_v1_0.get('should_proceed_with_evaluation') else 'REJECT'}")
                print(f"🎯 v1_0 Domain: {result_v1_0.get('primary_domain_classification', 'Unknown')}")
            except Exception as e:
                print(f"❌ v1_0 Error: {e}")
                v1_0_time = None
        
        # Test v1_1 (LLM)
        if classify_v1_1:
            print("\n🧠 Testing v1_1 (LLM)...")
            start_time = time.time()
            try:
                print(f"🔄 Calling v1_1 with title: '{job_metadata['title'][:50]}...'")
                result_v1_1 = classify_v1_1(job_metadata, job_description)
                v1_1_time = time.time() - start_time
                print(f"🐌 v1_1 Processing Time: {v1_1_time:.4f}s")
                
                if result_v1_1:
                    print(f"📊 v1_1 Decision: {'PROCEED' if result_v1_1.get('should_proceed_with_evaluation') else 'REJECT'}")
                    print(f"🎯 v1_1 Domain: {result_v1_1.get('primary_domain_classification', 'Unknown')}")
                    if not result_v1_1.get('should_proceed_with_evaluation'):
                        reasoning = result_v1_1.get('analysis_details', {}).get('decision_reasoning', '')
                        if reasoning:
                            print(f"💭 v1_1 Reasoning: {reasoning[:100]}...")
                else:
                    print("❌ v1_1 returned None result")
            except Exception as e:
                print(f"❌ v1_1 Error: {e}")
                import traceback
                traceback.print_exc()
                v1_1_time = None
        
        # Compare performance
        if v1_0_time and v1_1_time:
            speedup = v1_1_time / v1_0_time
            print(f"\n📈 Performance Comparison:")
            print(f"   v1_0 (hardcoded): {v1_0_time:.4f}s")
            print(f"   v1_1 (LLM): {v1_1_time:.4f}s")
            print(f"   LLM is {speedup:.0f}x slower (expected for real AI)")
            
            if v1_1_time > 3.0:
                print("   ✅ CONFIRMED: v1_1 is using real LLM (Ollama)")
            else:
                print("   ⚠️  WARNING: v1_1 suspiciously fast - may not be using LLM")
        
        print("\n" + "="*50)

def main():
    print("🎬 Starting Direct LLM Specialist Test...")
    print("Testing to confirm v1_1 specialists use real Ollama LLM")
    print()
    
    test_specialists()
    
    print("\n✅ Test completed!")
    print("\nExpected results:")
    print("- v1_0: ~0.001-0.010 seconds (hardcoded logic)")
    print("- v1_1: ~5-15 seconds (real Ollama LLM)")
    print("\nIf v1_1 shows >3 seconds, Ollama integration is working! 🚀")

if __name__ == "__main__":
    main()
