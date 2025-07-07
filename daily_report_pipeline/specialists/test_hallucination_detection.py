#!/usr/bin/env python3
"""
Advanced test script to identify LLM hallucination patterns
Testing edge cases that might trigger the issues Sandy mentioned
"""

import sys
import os
sys.path.append('/home/xai/Documents/sandy/daily_report_pipeline/specialists')

from location_validation_specialist_llm import LocationValidationSpecialistLLM
import logging

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_edge_cases():
    """Test various edge cases that might trigger hallucinations"""
    
    print("🔍 ADVANCED LLM HALLUCINATION DETECTION TESTS")
    print("=" * 60)
    
    specialist = LocationValidationSpecialistLLM()
    
    # Test cases designed to trigger potential issues
    test_cases = [
        {
            "name": "Test 1: Frankfurt→Pune (Original)",
            "metadata": "Frankfurt", 
            "description": "Join our team at Deutsche Bank Technology Center in Pune, India. This position is based in our state-of-the-art Pune office...",
            "expected_conflict": True,
            "expected_location": "Pune, India"
        },
        {
            "name": "Test 2: Berlin→Berlin (Original)", 
            "metadata": "Berlin, Germany",
            "description": "We are looking for a software engineer to join our Berlin team. Great opportunities in our German headquarters...",
            "expected_conflict": False,
            "expected_location": "Berlin, Germany"
        },
        {
            "name": "Test 3: Multiple Mentions",
            "metadata": "London",
            "description": "This role is based in our London office. You will work closely with teams in Frankfurt, Berlin, and our main London headquarters...",
            "expected_conflict": False,  # London is primary
            "expected_location": "London"
        },
        {
            "name": "Test 4: Ambiguous References",
            "metadata": "Frankfurt",
            "description": "Work with global teams. Travel to various offices including Frankfurt, London, Pune. Home base to be determined.",
            "expected_conflict": False,  # No clear single location
            "expected_location": "Frankfurt"
        },
        {
            "name": "Test 5: Context Bleeding Test",
            "metadata": "New York", 
            "description": "Join our New York trading floor. Experience the energy of Wall Street in our Manhattan office.",
            "expected_conflict": False,
            "expected_location": "New York"
        },
        {
            "name": "Test 6: Same City Different Country",
            "metadata": "London",
            "description": "This position is located in London, Ontario, Canada. Great opportunity in our Canadian operations.",
            "expected_conflict": True,  # Different London
            "expected_location": "London, Ontario, Canada"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases):
        print(f"\n🧪 {test['name']}")
        print(f"📍 Metadata: {test['metadata']}")
        print(f"📝 Description: {test['description'][:100]}...")
        print(f"🎯 Expected: conflict={test['expected_conflict']}, location={test['expected_location']}")
        
        try:
            result = specialist.validate_location(
                test['metadata'], 
                test['description'], 
                f"edge_test_{i+1}"
            )
            
            print(f"🤖 LLM Result: conflict={result.conflict_detected}, location={result.authoritative_location}")
            print(f"📊 Confidence: {result.confidence_score}%")
            print(f"💭 Reasoning: {result.analysis_details.get('reasoning', 'N/A')}")
            
            # Check for correctness
            conflict_correct = result.conflict_detected == test['expected_conflict']
            location_reasonable = test['expected_location'].lower() in result.authoritative_location.lower()
            
            if conflict_correct and (location_reasonable or not test['expected_conflict']):
                print("✅ CORRECT")
                results.append("PASS")
            else:
                print("❌ INCORRECT - Potential hallucination detected!")
                results.append("FAIL")
                
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
            results.append("ERROR")
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"🎯 HALLUCINATION DETECTION SUMMARY")
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed: {results.count('PASS')}")
    print(f"Failed: {results.count('FAIL')}")
    print(f"Errors: {results.count('ERROR')}")
    
    if results.count('FAIL') == 0:
        print("✅ NO HALLUCINATIONS DETECTED - LLM appears to be working correctly!")
    else:
        print("⚠️ HALLUCINATIONS DETECTED - Need prompt engineering fixes")
        
    return results

if __name__ == "__main__":
    test_edge_cases()
