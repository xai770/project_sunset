#!/usr/bin/env python3
"""
Debug the LLM responses to see why authoritative location extraction is failing
"""

import json
from location_validation_specialist_llm import LocationValidationSpecialistLLM

def debug_llm_responses():
    """Debug LLM responses to see exactly what's being returned"""
    specialist = LocationValidationSpecialistLLM()
    
    # Test case: Frankfurt metadata but Pune job
    test_case = {
        'metadata_location': 'Frankfurt',
        'job_description': '''
        Senior Software Engineer - Deutsche Bank Technology Center
        
        Join our development team at Deutsche Bank Technology Center in Pune, India.
        This position is based in our state-of-the-art Pune office and requires
        on-site collaboration with our growing India operations team.
        
        Key responsibilities:
        - Work in our Pune facility 
        - Collaborate with Pune-based teams
        - Support operations in Pune and Mumbai
        
        Location: Pune, India
        Office: Deutsche Bank Technology Center, Pune
        ''',
        'job_id': 'debug_test'
    }
    
    print("🔍 DEBUGGING LLM LOCATION VALIDATION RESPONSES")
    print("=" * 60)
    print(f"Metadata Location: {test_case['metadata_location']}")
    print(f"Job Description mentions: Pune, India multiple times")
    print()
    
    # We need to manually call the LLM to see the raw response
    llm_response = specialist._analyze_with_llm(
        test_case['metadata_location'],
        test_case['job_description'], 
        test_case['job_id']
    )
    
    print("🤖 RAW LLM RESPONSE:")
    print("-" * 40)
    print(llm_response)
    print("-" * 40)
    print()
    
    # Now parse it and see what we get
    parsed = specialist._parse_llm_response(llm_response)
    
    print("📊 PARSED RESULTS:")
    print(f"  Conflict Detected: {parsed['conflict_detected']}")
    print(f"  Authoritative Location: '{parsed['authoritative_location']}'")
    print(f"  Extracted Locations: {parsed['extracted_locations']}")
    print(f"  Confidence Score: {parsed['confidence_score']}")
    print(f"  Risk Level: {parsed['risk_level']}")
    print()
    print("🔍 REASONING:")
    print(f"  {parsed['reasoning']}")
    
    # Let's also test the full validation method
    print("\n" + "=" * 60)
    print("🧪 FULL VALIDATION METHOD TEST:")
    result = specialist.validate_location(
        test_case['metadata_location'],
        test_case['job_description'],
        test_case['job_id']
    )
    
    print(f"  Final Authoritative Location: '{result.authoritative_location}'")
    print(f"  Conflict Detected: {result.conflict_detected}")
    print(f"  Confidence: {result.confidence_score}")

if __name__ == "__main__":
    debug_llm_responses()
