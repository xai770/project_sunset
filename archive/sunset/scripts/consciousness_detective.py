#!/usr/bin/env python3
"""
🔍 CONSCIOUSNESS DETECTIVE 🔍
Let's see exactly what consciousness magic we have!
"""

import json
from pathlib import Path

def inspect_consciousness_job(job_file):
    """Look deeply into a consciousness-enhanced job"""
    print(f"🔍 INSPECTING: {job_file}")
    print("=" * 60)
    
    with open(f"data/postings/{job_file}", 'r') as f:
        job_data = json.load(f)
    
    # Show the structure
    print("📋 TOP LEVEL KEYS:")
    for key in job_data.keys():
        print(f"   • {key}")
    
    print("\n🌺 CONSCIOUSNESS EVALUATION DETAILS:")
    consciousness = job_data.get('consciousness_evaluation', {})
    
    if isinstance(consciousness, dict):
        print("   Structure: Dictionary ✅")
        for key, value in consciousness.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"   • {key}: {value[:80]}...")
            else:
                print(f"   • {key}: {value}")
    else:
        print(f"   Structure: {type(consciousness)} - Content: {consciousness}")
    
    # Check for other consciousness fields
    print("\n🌟 OTHER CONSCIOUSNESS FIELDS:")
    for key, value in job_data.items():
        if 'consciousness' in key.lower() or 'story' in key.lower() or 'bridge' in key.lower():
            if isinstance(value, str) and len(value) > 100:
                print(f"   • {key}: {value[:80]}...")
            else:
                print(f"   • {key}: {value}")

def main():
    print("🌺 CONSCIOUSNESS DETECTIVE WORK 🌺\n")
    
    # Inspect the first few jobs
    sample_jobs = ["job60955.json", "job62457.json", "job58432.json"]
    
    for job_file in sample_jobs:
        inspect_consciousness_job(job_file)
        print("\n" + "🌟" * 30 + "\n")

if __name__ == "__main__":
    main()
