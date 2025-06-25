#!/usr/bin/env python3
"""
Test Location Validation Fix - Quick Validation
==============================================

Test that the location validation specialist now works with our job data format.
"""

import sys
import json
from pathlib import Path

# Add project paths
sys.path.append('/home/xai/Documents/sunset')
sys.path.append('/home/xai/Documents/llm_factory')

from core.direct_specialist_manager import DirectSpecialistManager

def test_location_validation_fix():
    """Test the location validation fix with real job data"""
    
    print("🧪 Testing Location Validation Fix")
    print("=" * 40)
    
    # Load a real job to test with
    job_file = Path("/home/xai/Documents/sunset/data/postings/job62999.json")
    
    if not job_file.exists():
        print("❌ Test job file not found")
        return
    
    with open(job_file, 'r') as f:
        job_data = json.load(f)
    
    # Extract the data format our specialist manager expects
    job_content = job_data.get("job_content", {})
    
    input_data = {
        "job_metadata": {
            "location": job_content.get("location", {}),  # This is the dict format
            "title": job_content.get("title", ""),
            "id": job_data.get("job_metadata", {}).get("job_id", "test")
        },
        "job_description": job_content.get("description", "")
    }
    
    print(f"📋 Testing with job: {input_data['job_metadata']['title']}")
    print(f"📍 Original location format: {input_data['job_metadata']['location']}")
    
    # Test with the specialist manager
    specialist_mgr = DirectSpecialistManager()
    
    try:
        result = specialist_mgr.evaluate_with_specialist("location_validation", input_data)
        
        if result.success:
            print("✅ Location validation succeeded!")
            print(f"📊 Result: {result.result}")
            print(f"⏱️  Execution time: {result.execution_time:.4f}s")
        else:
            print("❌ Location validation failed:")
            print(f"Error: {result.error}")
            
    except Exception as e:
        print(f"❌ Exception during test: {e}")

if __name__ == "__main__":
    test_location_validation_fix()
