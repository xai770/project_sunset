#!/usr/bin/env python3
"""
Create a test job with Frankfurt→India conflict to verify the fix is working
"""

import json
import tempfile
import os
from daily_report_pipeline.specialists.location_validation_enhanced import LocationValidationEnhanced

def test_pipeline_with_conflict():
    """Test the enhanced pipeline with a Frankfurt→India conflict"""
    
    # Create a test job with Frankfurt metadata but India description
    test_job_data = {
        'location': 'Frankfurt, Germany',
        'description': '''
        Senior Software Engineer - Deutsche Bank Technology Center
        Location: Frankfurt, Germany

        We are looking for a Senior Software Engineer to join our development team 
        at Deutsche Bank Technology Center in Pune, India.

        Key Responsibilities:
        - Develop software solutions for our Indian operations
        - Work closely with our Pune-based development team
        - Collaborate with stakeholders across our India offices in Mumbai and Bangalore
        - Support our growing operations in Pune

        Requirements:
        - 5+ years of software development experience
        - Strong background in Java and Python
        - Experience with banking or financial systems
        - Willingness to work in our Pune facility

        About the Role:
        This position is based in our state-of-the-art Pune office and offers excellent 
        growth opportunities within Deutsche Bank's India operations. You'll be working 
        with cutting-edge technology in our modern Pune facility.

        The role requires on-site presence at our Pune location and involves close 
        collaboration with teams across our Indian offices.
        '''
    }

    print("🧪 TESTING PIPELINE WITH FRANKFURT→INDIA CONFLICT")
    print("=" * 60)
    print(f"Metadata Location: {test_job_data['location']}")
    print(f"Description mentions: Pune, India extensively")
    print()

    # Test the enhanced location validation specialist
    specialist = LocationValidationEnhanced()
    
    result = specialist.validate_job_location(test_job_data, "conflict_test")
    
    print("📊 PIPELINE RESULTS:")
    print(f"   Conflict Detected: {result['conflict_detected']}")
    print(f"   Metadata Location: {test_job_data['location']}")
    print(f"   Authoritative Location: {result['authoritative_location']}")
    print(f"   Confidence Score: {result['confidence_score']}")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Processing Time: {result['processing_time']:.3f}s")
    print()
    print(f"📋 Location Validation Details Format:")
    print(f"   {result['summary']}")
    print()
    print("🎯 SUCCESS CRITERIA:")
    print(f"   ✅ Conflict Detection: {'PASS' if result['conflict_detected'] else 'FAIL'}")
    print(f"   ✅ Authoritative Location: {'PASS' if 'Pune' in result['authoritative_location'] else 'FAIL'}")
    print(f"   ✅ Processing Time: {'PASS' if result['processing_time'] > 1.0 else 'FAIL'} (LLM processing)")
    
    # Demonstrate the formatted output that would appear in reports
    location_validation_details = f"Conflict: {'DETECTED' if result['conflict_detected'] else 'NONE'} | Confidence: {result['confidence_score']:.2f} | Authoritative: {result['authoritative_location']} | Processing: {result['processing_time']:.2f}s | Risk: {result['risk_level'].upper()}"
    
    print(f"\n📄 REPORT FORMAT:")
    print(f"   Location Validation Details: {location_validation_details}")

if __name__ == "__main__":
    test_pipeline_with_conflict()
