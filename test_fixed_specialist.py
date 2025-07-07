#!/usr/bin/env python3
"""
Test the fixed LLM specialist with multiple golden test cases
"""

from location_validation_specialist_llm import LocationValidationSpecialistLLM

def test_fixed_specialist():
    """Test the fixed specialist with our critical cases"""
    specialist = LocationValidationSpecialistLLM()
    
    test_cases = [
        {
            'name': 'Frankfurt→Pune Critical',
            'metadata_location': 'Frankfurt',
            'job_description': 'Join our team in Pune, India. Based in our Pune facility.',
            'expected_authoritative': 'Pune, India'
        },
        {
            'name': 'Frankfurt→Bangalore Critical', 
            'metadata_location': 'Frankfurt',
            'job_description': 'Technical Lead position in Bangalore, India. Located in our Bangalore office.',
            'expected_authoritative': 'Bangalore, India'
        },
        {
            'name': 'True Frankfurt Position',
            'metadata_location': 'Frankfurt',
            'job_description': 'Software engineer position in Frankfurt, Germany. Based in our Frankfurt headquarters.',
            'expected_authoritative': 'Frankfurt, Germany'
        }
    ]
    
    print("🧪 TESTING FIXED LLM SPECIALIST")
    print("=" * 50)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📋 TEST {i}: {test['name']}")
        print(f"   Metadata: {test['metadata_location']}")
        print(f"   Expected: {test['expected_authoritative']}")
        
        result = specialist.validate_location(
            test['metadata_location'],
            test['job_description'],
            f"test_{i}"
        )
        
        print(f"   Result: {result.authoritative_location}")
        print(f"   Conflict: {result.conflict_detected}")
        print(f"   Match: {'✅' if result.authoritative_location == test['expected_authoritative'] else '❌'}")

if __name__ == "__main__":
    test_fixed_specialist()
