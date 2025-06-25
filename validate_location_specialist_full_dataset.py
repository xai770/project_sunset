#!/usr/bin/env python3
"""
Comprehensive Location Validation Test
=====================================

Run the Location Validation Specialist against all 9 jobs from our systematic manual review.
This will validate that the specialist catches all location conflicts and doesn't produce false positives.

Jobs to test (from session log):
1. Job 60955: DWS Operations Specialist - Performance Measurement  
2. Job 58432: DWS - Cybersecurity Vulnerability Management Lead
3. Job 63144: DWS Operations Specialist - E-invoicing
4. Job 52953: QA & Testing Engineer (SDET)
5. Job 55025: Institutional Cash and Trade Sales Specialist
6. Job 57488: Java Backend Developer (VALIDATION EXAMPLE - Golden Test) 
7. Job 58004: Lead Analytics Analyst - Data Engineer (AFC)
8. Job 58649: DWS Senior Product Specialist Private Debt (Real Estate)
9. Job 58735: Name and Transaction Screening Model Strats (VALIDATION EXAMPLE #2 - Golden Test)
"""

import json
import os
import sys
from typing import Dict, Any, List

# Import the quick location validation function
sys.path.append('/home/xai/Documents/sunset/0_mailboxes/sandy@consciousness/inbox')
from quick_start_for_sandy import quick_location_validation

def load_job_data(job_id: str) -> Dict[str, Any]:
    """Load job data from the postings directory"""
    job_file = f"/home/xai/Documents/sunset/data/postings/job{job_id}.json"
    
    if not os.path.exists(job_file):
        return None
        
    with open(job_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_location_from_job(job_data: Dict[str, Any]) -> str:
    """Extract location metadata from job posting"""
    # Check the specific structure used in our job files
    if 'job_content' in job_data and 'location' in job_data['job_content']:
        location_info = job_data['job_content']['location']
        if 'city' in location_info and location_info['city']:
            return location_info['city']
    
    # Fallback to other possible fields
    possible_fields = ['location', 'office', 'workLocation', 'city', 'address']
    
    for field in possible_fields:
        if field in job_data and job_data[field]:
            return str(job_data[field])
    
    # If no explicit location field, try to extract from other fields
    if 'locationDisplayName' in job_data:
        return job_data['locationDisplayName']
    
    if 'jobLocation' in job_data:
        return job_data['jobLocation']
        
    return "Unknown"

def extract_description_from_job(job_data: Dict[str, Any]) -> str:
    """Extract job description text"""
    # Check the specific structure used in our job files
    if 'job_content' in job_data and 'description' in job_data['job_content']:
        return job_data['job_content']['description']
    
    # Fallback to other possible fields  
    description_fields = ['description', 'jobDescription', 'content', 'details']
    
    for field in description_fields:
        if field in job_data and job_data[field]:
            return str(job_data[field])
    
    return ""

def run_comprehensive_validation():
    """Run Location Validation Specialist on our complete dataset"""
    
    # Jobs from our systematic review
    review_jobs = [
        {"id": "60955", "name": "DWS Operations Specialist - Performance Measurement", "expected_conflict": False},
        {"id": "58432", "name": "DWS - Cybersecurity Vulnerability Management Lead", "expected_conflict": False},
        {"id": "63144", "name": "DWS Operations Specialist - E-invoicing", "expected_conflict": False},
        {"id": "52953", "name": "QA & Testing Engineer (SDET)", "expected_conflict": True},
        {"id": "55025", "name": "Institutional Cash and Trade Sales Specialist", "expected_conflict": False},
        {"id": "57488", "name": "Java Backend Developer (GOLDEN TEST)", "expected_conflict": True},
        {"id": "58004", "name": "Lead Analytics Analyst - Data Engineer (AFC)", "expected_conflict": False},
        {"id": "58649", "name": "DWS Senior Product Specialist Private Debt (Real Estate)", "expected_conflict": False},
        {"id": "58735", "name": "Name and Transaction Screening Model Strats (GOLDEN TEST)", "expected_conflict": True},
    ]
    
    print("🎯 COMPREHENSIVE LOCATION VALIDATION TEST")
    print("🎯 Testing Location Validation Specialist on Complete Dataset")
    print("🎯 Jobs from Systematic Manual Review Session")
    print("=" * 80)
    
    results = []
    total_jobs = len(review_jobs)
    
    for i, job_info in enumerate(review_jobs, 1):
        job_id = job_info["id"]
        job_name = job_info["name"]
        expected_conflict = job_info["expected_conflict"]
        
        print(f"\n📋 [{i}/{total_jobs}] Job {job_id}: {job_name}")
        
        # Load job data
        job_data = load_job_data(job_id)
        if not job_data:
            print(f"   ❌ ERROR: Could not load job data for {job_id}")
            results.append({"job_id": job_id, "status": "ERROR", "reason": "File not found"})
            continue
        
        # Extract location and description
        metadata_location = extract_location_from_job(job_data)
        description = extract_description_from_job(job_data)
        
        print(f"   📍 Metadata Location: {metadata_location}")
        
        if not description:
            print(f"   ❌ ERROR: No description found for {job_id}")
            results.append({"job_id": job_id, "status": "ERROR", "reason": "No description"})
            continue
        
        # Run Location Validation Specialist
        validation_result = quick_location_validation(metadata_location, description)
        
        # Check if result matches expectation
        conflict_detected = validation_result['conflict_detected']
        passed = conflict_detected == expected_conflict
        
        status_icon = "✅ PASS" if passed else "❌ FAIL"
        expectation = "CONFLICT" if expected_conflict else "NO CONFLICT"
        actual = "CONFLICT" if conflict_detected else "NO CONFLICT"
        
        print(f"   {status_icon} - Expected: {expectation}, Got: {actual}")
        print(f"   🎯 Confidence: {validation_result['confidence_score']}")
        print(f"   📍 Authoritative Location: {validation_result['authoritative_location']}")
        print(f"   ⚠️  Risk Level: {validation_result['risk_level']}")
        
        if validation_result['found_locations']:
            print(f"   🔍 Found Locations: {', '.join(validation_result['found_locations'])}")
        
        # Store result
        results.append({
            "job_id": job_id,
            "job_name": job_name,
            "status": "PASS" if passed else "FAIL",
            "expected_conflict": expected_conflict,
            "detected_conflict": conflict_detected,
            "metadata_location": metadata_location,
            "authoritative_location": validation_result['authoritative_location'],
            "confidence": validation_result['confidence_score'],
            "risk_level": validation_result['risk_level'],
            "found_locations": validation_result['found_locations']
        })
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    
    passed_count = sum(1 for r in results if r["status"] == "PASS")
    failed_count = sum(1 for r in results if r["status"] == "FAIL") 
    error_count = sum(1 for r in results if r["status"] == "ERROR")
    
    print(f"✅ PASSED: {passed_count}/{total_jobs}")
    print(f"❌ FAILED: {failed_count}/{total_jobs}")
    print(f"🔥 ERRORS: {error_count}/{total_jobs}")
    
    if failed_count > 0:
        print(f"\n❌ FAILED JOBS:")
        for result in results:
            if result["status"] == "FAIL":
                print(f"   - Job {result['job_id']}: Expected {result['expected_conflict']}, got {result['detected_conflict']}")
    
    if error_count > 0:
        print(f"\n🔥 ERROR JOBS:")
        for result in results:
            if result["status"] == "ERROR":
                print(f"   - Job {result['job_id']}: {result['reason']}")
    
    # Success rate
    success_rate = (passed_count / (total_jobs - error_count)) * 100 if (total_jobs - error_count) > 0 else 0
    
    print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🚀 PERFECT SCORE! Location Validation Specialist is ready for production!")
    elif success_rate >= 90:
        print("⭐ EXCELLENT! Location Validation Specialist is highly reliable!")
    elif success_rate >= 75:
        print("✨ GOOD! Some tuning needed but mostly reliable!")
    else:
        print("⚠️  NEEDS WORK! Location Validation Specialist requires improvement!")
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_validation()
    
    print(f"\n💡 Ready for Phase 2: Domain Classification Specialist development!")
    print(f"💡 These validated results feed into our next LLM Factory collaboration!")
