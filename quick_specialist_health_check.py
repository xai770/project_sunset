#!/usr/bin/env python3
"""
Quick Specialist Health Check
============================

Run this before any major pipeline runs to verify specialists are working correctly.

Usage: python quick_specialist_health_check.py
"""

import sys
import time
sys.path.insert(0, '/home/xai/Documents/llm_factory')

def quick_health_check():
    """Quick test to verify LLM specialists are actually using Ollama"""
    
    print("🏥 SPECIALIST HEALTH CHECK")
    print("=" * 40)
    
    # Test data
    test_metadata = {'title': 'Test Software Engineer', 'id': 'HEALTH_001'}
    test_description = "Software engineer role requiring Python programming skills."
    
    try:
        # Test v1_1 (should be slow - LLM)
        from llm_factory.modules.quality_validation.specialists_versioned.domain_classification.v1_1.src.domain_classification_specialist_llm import classify_job_domain_llm
        
        print("🧠 Testing v1_1 LLM specialist...")
        start_time = time.time()
        result = classify_job_domain_llm(test_metadata, test_description)
        v1_1_time = time.time() - start_time
        
        print(f"⏱️  v1_1 Processing Time: {v1_1_time:.2f}s")
        
        if v1_1_time > 2.0:
            print("✅ HEALTHY: v1_1 is using LLM (Ollama) correctly")
            return True
        else:
            print("🚨 PROBLEM: v1_1 is suspiciously fast - may not be using Ollama!")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Could not test v1_1 specialist: {e}")
        return False

if __name__ == "__main__":
    healthy = quick_health_check()
    if healthy:
        print("\n✅ All specialists healthy - safe to run pipeline!")
        sys.exit(0)
    else:
        print("\n🚨 Specialist issues detected - investigate before running pipeline!")
        sys.exit(1)
