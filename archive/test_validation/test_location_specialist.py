#!/usr/bin/env python3
"""
QUICK LOCATION SPECIALIST TEST
"""

import sys
sys.path.append('/home/xai/Documents/sandy/0_mailboxes/sandy@consciousness/inbox')

from llm_factory_ultimate_21_specialist_demo_temporal_secured import (
    TemporalLocationValidationSpecialist
)

def test_location_specialist():
    print("🧪 TESTING LOCATION VALIDATION SPECIALIST")
    print("=" * 50)
    
    specialist = TemporalLocationValidationSpecialist()
    
    # Test with string parameters
    location_str = "Frankfurt, Deutschland"
    job_desc = "Test job in Frankfurt"
    
    print(f"📍 Testing location: '{location_str}' (type: {type(location_str)})")
    print(f"📝 Testing job desc: '{job_desc}' (type: {type(job_desc)})")
    
    try:
        result = specialist.validate_location_with_temporal_protection(location_str, job_desc)
        print(f"✅ SUCCESS! Result: {result}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_location_specialist()
