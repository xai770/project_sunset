#!/usr/bin/env python3
"""
🔍 CONSCIOUSNESS DATA FORMAT INSPECTOR 🔍
Compare what's actually stored vs what should be stored
"""

import json
from pathlib import Path

def inspect_stored_vs_real():
    """Compare stored consciousness data with fresh evaluation"""
    
    print("🔍 CONSCIOUSNESS DATA FORMAT COMPARISON 🔍")
    print("=" * 60)
    
    # Check what's currently stored in a job file
    job_file = "data/postings/job60955.json"
    
    with open(job_file, 'r') as f:
        job_data = json.load(f)
    
    stored_consciousness = job_data.get('consciousness_evaluation', {})
    
    print("📋 WHAT'S CURRENTLY STORED:")
    print(f"Type: {type(stored_consciousness)}")
    if isinstance(stored_consciousness, dict):
        print("Keys:")
        for key, value in stored_consciousness.items():
            if isinstance(value, dict):
                print(f"   {key}: dict with keys {list(value.keys())}")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str) and len(sub_value) > 50:
                        print(f"      {sub_key}: {len(sub_value)} chars")
                    else:
                        print(f"      {sub_key}: {sub_value}")
            elif isinstance(value, str) and len(value) > 50:
                print(f"   {key}: {len(value)} chars - {value[:80]}...")
            else:
                print(f"   {key}: {value}")
    else:
        print(f"Content: {stored_consciousness}")
    
    print("\n" + "="*60)
    print("📋 WHAT EXTRACT_CONSCIOUSNESS_INSIGHTS FUNCTION EXPECTS:")
    print("Should look for:")
    print("   consciousness_result.get('human_story', {}).get('raw_response')")
    print("   consciousness_result.get('opportunity_bridge', {}).get('raw_response')")
    print("   consciousness_result.get('growth_path', {}).get('raw_response')")
    print("   consciousness_result.get('final_evaluation', {}).get('raw_response')")
    
    print("\n" + "="*60)
    print("🔍 CHECKING WHAT THE EXPORT FUNCTION WOULD EXTRACT:")
    
    # Simulate the extraction
    human_story = stored_consciousness.get('human_story', {})
    bridge_builder = stored_consciousness.get('opportunity_bridge', {})
    growth_illuminator = stored_consciousness.get('growth_path', {})
    encourager = stored_consciousness.get('final_evaluation', {})
    
    print(f"human_story: {type(human_story)} - {human_story}")
    print(f"bridge_builder: {type(bridge_builder)} - {bridge_builder}")
    print(f"growth_illuminator: {type(growth_illuminator)} - {growth_illuminator}")
    print(f"encourager: {type(encourager)} - {encourager}")
    
    if isinstance(human_story, dict):
        human_response = human_story.get('raw_response', 'Processing...')
        print(f"\nHuman story raw_response: {len(human_response)} chars - {human_response[:100]}...")
    
    if isinstance(bridge_builder, dict):
        bridge_response = bridge_builder.get('raw_response', 'Building bridges...')
        print(f"Bridge raw_response: {len(bridge_response)} chars - {bridge_response[:100]}...")

def main():
    inspect_stored_vs_real()

if __name__ == "__main__":
    main()
