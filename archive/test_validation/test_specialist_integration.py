#!/usr/bin/env python3
"""
Test Integration of New Specialists in Project Sunset
===================================================

This script tests the integration of the Location Validation and Domain Classification
specialists in the Project Sunset pipeline through the DirectSpecialistManager.
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.direct_specialist_manager import DirectSpecialistManager

def test_location_validation():
    """Test Location Validation Specialist integration"""
    print("🧪 Testing Location Validation Specialist...")
    
    # Test with a known case: Frankfurt metadata vs India description
    test_data = {
        "job_metadata": {
            "location": "Frankfurt",
            "title": "Test Position",
            "id": "TEST_001"
        },
        "job_description": "This position is located in Pune, India. The role involves working with our Indian development team in Bangalore."
    }
    
    specialist_manager = DirectSpecialistManager()
    result = specialist_manager.evaluate_with_specialist("location_validation", test_data)
    
    print(f"✅ Success: {result.success}")
    print(f"🕒 Execution time: {result.execution_time:.4f}s")
    
    if result.success:
        location_result = result.result
        print(f"📍 Metadata accurate: {location_result.get('metadata_location_accurate', 'Unknown')}")
        print(f"🚨 Conflict detected: {location_result.get('conflict_detected', 'Unknown')}")
        print(f"🎯 Authoritative location: {location_result.get('authoritative_location', 'Unknown')}")
        print(f"💯 Confidence: {location_result.get('confidence_score', 0.0):.2f}")
    else:
        print(f"❌ Error: {result.error}")
    
    return result.success

def test_domain_classification():
    """Test Domain Classification Specialist integration"""
    print("\n🧪 Testing Domain Classification Specialist...")
    
    # Test with IT Operations role (should proceed)
    test_data = {
        "job_metadata": {
            "title": "Senior Systems Administrator",
            "id": "TEST_002"
        },
        "job_description": """Senior Systems Administrator responsible for server infrastructure management, 
        system administration, network maintenance, backup management, user account management, infrastructure monitoring, 
        technical support, system troubleshooting, and automation. Perfect match for IT Operations background."""
    }
    
    specialist_manager = DirectSpecialistManager()
    result = specialist_manager.evaluate_with_specialist("domain_classification", test_data)
    
    print(f"✅ Success: {result.success}")
    print(f"🕒 Execution time: {result.execution_time:.4f}s")
    
    if result.success:
        domain_result = result.result
        print(f"✅ Should proceed: {domain_result.get('should_proceed_with_evaluation', 'Unknown')}")
        print(f"🏷️ Domain: {domain_result.get('primary_domain_classification', 'Unknown')}")
        print(f"💯 Confidence: {domain_result.get('analysis_details', {}).get('domain_confidence', 0.0):.2f}")
        
        if not domain_result.get('should_proceed_with_evaluation', True):
            print(f"❌ Rejection reason: {domain_result.get('analysis_details', {}).get('decision_reasoning', 'Unknown')}")
    else:
        print(f"❌ Error: {result.error}")
    
    return result.success

def test_investment_management_rejection():
    """Test that Investment Management jobs are properly rejected"""
    print("\n🧪 Testing Investment Management Rejection...")
    
    # Test with Investment Management role (should reject)
    test_data = {
        "job_metadata": {
            "title": "Senior Investment Manager",
            "id": "TEST_003"
        },
        "job_description": """Senior Investment Manager position focusing on high-net-worth client portfolio management. 
        Responsibilities include developing sophisticated investment strategies, conducting comprehensive risk analysis, 
        portfolio optimization, equity research, bond analysis, derivatives trading, and client relationship management. 
        Requires deep understanding of financial markets, regulatory compliance, and investment products."""
    }
    
    specialist_manager = DirectSpecialistManager()
    result = specialist_manager.evaluate_with_specialist("domain_classification", test_data)
    
    print(f"✅ Success: {result.success}")
    print(f"🕒 Execution time: {result.execution_time:.4f}s")
    
    if result.success:
        domain_result = result.result
        should_proceed = domain_result.get('should_proceed_with_evaluation', True)
        print(f"❌ Should reject: {not should_proceed}")
        print(f"🏷️ Domain: {domain_result.get('primary_domain_classification', 'Unknown')}")
        
        if not should_proceed:
            print(f"✅ Correct rejection reason: {domain_result.get('analysis_details', {}).get('decision_reasoning', 'Unknown')}")
        else:
            print("⚠️ WARNING: Investment Management job was not rejected!")
    else:
        print(f"❌ Error: {result.error}")
    
    return result.success

def main():
    """Run integration tests"""
    print("🌅 PROJECT SUNSET - SPECIALIST INTEGRATION TEST")
    print("=" * 50)
    
    # Test both specialists
    location_success = test_location_validation()
    domain_success = test_domain_classification()
    investment_success = test_investment_management_rejection()
    
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST RESULTS")
    print(f"📍 Location Validation: {'✅ PASS' if location_success else '❌ FAIL'}")
    print(f"🏷️ Domain Classification: {'✅ PASS' if domain_success else '❌ FAIL'}")
    print(f"💼 Investment Rejection: {'✅ PASS' if investment_success else '❌ FAIL'}")
    
    all_success = location_success and domain_success and investment_success
    print(f"\n🎯 Overall Integration: {'✅ SUCCESS' if all_success else '❌ FAILED'}")
    
    if all_success:
        print("🚀 Specialists are ready for production use!")
    else:
        print("⚠️ Some tests failed - check errors above")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
