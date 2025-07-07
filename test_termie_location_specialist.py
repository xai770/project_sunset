#!/usr/bin/env python3
"""
Testing Termie's LLM-powered Location Validation Specialist v2.0
against our critical golden test cases to resolve the false positive issue.

This will test:
1. Job 57488 equivalent: Frankfurt metadata but job description mentions Pune, India
2. Job 58735 equivalent: Frankfurt metadata but job description mentions Bangalore, India  
3. Additional edge cases

These are the exact golden test cases where our current specialist fails.
"""

import json
import time
import sys
import os
from location_validation_specialist_llm import LocationValidationSpecialistLLM

def get_golden_test_cases():
    """Get the critical golden test cases that our current specialist fails on"""
    return [
        {
            "name": "Golden Test Case: Job 57488 - Frankfurt→Pune Critical Conflict",
            "job_id": "57488",
            "metadata_location": "Frankfurt",
            "job_description": """
Senior Software Engineer - Deutsche Bank Technology Center
Location: Frankfurt, Germany

We are looking for a Senior Software Engineer to join our development team at Deutsche Bank Technology Center in Pune, India.

Key Responsibilities:
- Develop and maintain critical banking software systems
- Work closely with our Pune-based development team
- Collaborate with stakeholders across our India offices
- Support our growing operations in Pune and Mumbai

Requirements:
- 5+ years of software development experience
- Strong background in Java and Python
- Experience with banking or financial systems
- Willingness to work in our Pune facility

About the Role:
This position is based in our state-of-the-art Pune office and offers excellent growth opportunities within Deutsche Bank's India operations. You'll be working with cutting-edge technology in our modern Pune facility.

The role requires on-site presence at our Pune location and involves close collaboration with teams across our Indian offices including Mumbai and Bangalore.
            """,
            "expected_conflict": True,
            "expected_authoritative_location": "Pune, India",
            "conflict_severity": "CRITICAL"  # Different continent
        },
        {
            "name": "Golden Test Case: Job 58735 - Frankfurt→Bangalore Critical Conflict", 
            "job_id": "58735",
            "metadata_location": "Frankfurt",
            "job_description": """
Technical Lead - Cloud Infrastructure
Frankfurt, Germany Office

Join our dynamic team as a Technical Lead for Cloud Infrastructure. This role is perfect for someone looking to advance their career in our expanding Bangalore operations.

Position Details:
- Lead cloud infrastructure projects for our Bangalore division
- Manage a team of 8 engineers in our Bangalore office
- Drive technical excellence across our Bangalore facility
- Coordinate with other tech hubs in Pune and Hyderabad

Location: Bangalore, India
Office: Deutsche Bank Technology Center, Bangalore

Key Requirements:
- 7+ years of cloud infrastructure experience
- Leadership experience managing distributed teams
- Experience working in India or similar markets
- Strong communication skills for our multi-cultural Bangalore environment

This is an exciting opportunity to join our rapidly growing Bangalore team and make a significant impact on our India operations. The role is based full-time in our modern Bangalore campus.
            """,
            "expected_conflict": True,
            "expected_authoritative_location": "Bangalore, India",
            "conflict_severity": "CRITICAL"  # Different continent
        },
        {
            "name": "Control Test: True Frankfurt Position",
            "job_id": "control_1", 
            "metadata_location": "Frankfurt",
            "job_description": """
Senior Software Engineer - Investment Banking
Frankfurt, Germany

Join our Investment Banking technology team in Frankfurt, Germany. This role is based in our Frankfurt headquarters and involves developing critical trading systems.

Key Details:
- Work location: Frankfurt, Germany
- Office: Deutsche Bank Twin Towers, Frankfurt
- Team: Frankfurt-based Investment Banking Technology
- Collaboration: Primarily with Frankfurt and London teams

Requirements:
- Strong Java and C++ development skills
- Experience with high-frequency trading systems
- Ability to work in our Frankfurt office environment
- German language skills preferred

This position offers the opportunity to work with cutting-edge financial technology in the heart of Frankfurt's financial district. You'll be working alongside some of the industry's brightest minds in our modern Frankfurt facility.
            """,
            "expected_conflict": False,
            "expected_authoritative_location": "Frankfurt, Germany",
            "conflict_severity": "NONE"
        },
        {
            "name": "Edge Case: Remote but Germany-based",
            "job_id": "edge_1",
            "metadata_location": "Frankfurt", 
            "job_description": """
Remote Software Developer
Base Location: Germany

This is a fully remote position for candidates based anywhere in Germany. While the role is remote, you must be located within Germany for legal and compliance reasons.

Work Arrangement:
- 100% remote work
- Quarterly team meetings in Frankfurt
- Flexible location within Germany
- Home office setup provided

Requirements:
- Must be based in Germany
- Valid German work authorization
- Strong internet connection
- Comfortable with remote collaboration tools

While this role offers remote flexibility, candidates must maintain their primary residence within Germany and be available for occasional Frankfurt office visits.
            """,
            "expected_conflict": False,  # Remote but still Germany-based
            "expected_authoritative_location": "Germany (Remote)",
            "conflict_severity": "NONE"
        }
    ]

def run_golden_test_suite():
    """Run the golden test cases against Termie's LLM specialist"""
    print("🌍 TESTING TERMIE'S LLM-POWERED LOCATION VALIDATION SPECIALIST v2.0")
    print("=" * 80)
    print("🎯 OBJECTIVE: Resolve false positive issue with critical golden test cases")
    print("📋 GOLDEN TEST CASES: Frankfurt jobs incorrectly validated as Frankfurt when they're in India")
    print("")
    
    # Initialize Termie's specialist
    specialist = LocationValidationSpecialistLLM()
    
    test_cases = get_golden_test_cases()
    results = []
    
    print(f"🧪 RUNNING {len(test_cases)} GOLDEN TEST CASES")
    print("-" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 TEST CASE {i}: {test_case['name']}")
        print(f"   Job ID: {test_case['job_id']}")
        print(f"   Metadata Location: {test_case['metadata_location']}")
        print(f"   Expected Conflict: {'YES' if test_case['expected_conflict'] else 'NO'}")
        print(f"   Expected Authoritative: {test_case['expected_authoritative_location']}")
        print(f"   Conflict Severity: {test_case['conflict_severity']}")
        print()
        
        try:
            # Run Termie's LLM specialist
            start_time = time.time()
            result = specialist.validate_location(
                test_case['metadata_location'],
                test_case['job_description'],
                test_case['job_id']
            )
            
            # Analyze results
            conflict_prediction_correct = result.conflict_detected == test_case['expected_conflict']
            processing_time_valid = result.processing_time > 1.0  # Genuine LLM processing
            
            print(f"   🤖 LLM ANALYSIS RESULTS:")
            print(f"      Conflict Detected: {'YES' if result.conflict_detected else 'NO'}")
            print(f"      Authoritative Location: {result.authoritative_location}")
            print(f"      Confidence Score: {result.confidence_score:.1f}%")
            print(f"      Processing Time: {result.processing_time:.3f}s")
            print(f"      Risk Level: {result.analysis_details.get('risk_level', 'unknown')}")
            print()
            print(f"   📊 VALIDATION:")
            print(f"      Conflict Prediction: {'✅ CORRECT' if conflict_prediction_correct else '❌ INCORRECT'}")
            print(f"      LLM Processing: {'✅ GENUINE' if processing_time_valid else '❌ SUSPICIOUS (<1s)'}")
            
            # For failed cases, show LLM reasoning
            if not conflict_prediction_correct:
                print(f"      🔍 LLM Reasoning: {result.analysis_details.get('reasoning', 'N/A')}")
                print(f"      🔍 Extracted Locations: {result.analysis_details.get('extracted_locations', [])}")
            
            # Store results
            results.append({
                'test_name': test_case['name'],
                'job_id': test_case['job_id'],
                'metadata_location': test_case['metadata_location'],
                'expected_conflict': test_case['expected_conflict'],
                'detected_conflict': result.conflict_detected,
                'prediction_correct': conflict_prediction_correct,
                'expected_authoritative': test_case['expected_authoritative_location'],
                'detected_authoritative': result.authoritative_location,
                'confidence_score': result.confidence_score,
                'processing_time': result.processing_time,
                'genuine_llm': processing_time_valid,
                'risk_level': result.analysis_details.get('risk_level', 'unknown'),
                'reasoning': result.analysis_details.get('reasoning', ''),
                'extracted_locations': result.analysis_details.get('extracted_locations', []),
                'conflict_severity': test_case['conflict_severity']
            })
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append({
                'test_name': test_case['name'],
                'job_id': test_case['job_id'],
                'error': str(e),
                'prediction_correct': False,
                'genuine_llm': False
            })
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("📊 GOLDEN TEST SUITE RESULTS")
    print("=" * 80)
    
    total_tests = len(results)
    correct_predictions = sum(1 for r in results if r.get('prediction_correct', False))
    genuine_llm_count = sum(1 for r in results if r.get('genuine_llm', False))
    critical_conflicts_detected = sum(1 for r in results if r.get('conflict_severity') == 'CRITICAL' and r.get('detected_conflict', False))
    critical_conflicts_total = sum(1 for r in results if r.get('conflict_severity') == 'CRITICAL')
    
    avg_processing_time = sum(r.get('processing_time', 0) for r in results) / total_tests if total_tests > 0 else 0
    avg_confidence = sum(r.get('confidence_score', 0) for r in results) / total_tests if total_tests > 0 else 0
    
    print(f"📈 OVERALL PERFORMANCE:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Correct Predictions: {correct_predictions}/{total_tests} ({correct_predictions/total_tests*100:.1f}%)")
    print(f"   Critical Conflicts Detected: {critical_conflicts_detected}/{critical_conflicts_total} ({critical_conflicts_detected/critical_conflicts_total*100:.1f}% if critical_conflicts_total > 0 else 0)")
    print(f"   Genuine LLM Processing: {genuine_llm_count}/{total_tests} ({genuine_llm_count/total_tests*100:.1f}%)")
    print(f"   Average Processing Time: {avg_processing_time:.3f}s")
    print(f"   Average Confidence Score: {avg_confidence:.1f}%")
    
    # Critical analysis for pipeline integration
    print(f"\n🎯 CRITICAL ANALYSIS:")
    
    # Check if golden test cases pass
    golden_cases_pass = True
    for result in results:
        if result.get('conflict_severity') == 'CRITICAL' and not result.get('prediction_correct', False):
            golden_cases_pass = False
            print(f"   ❌ FAILED: {result['test_name']}")
            print(f"      Expected: {'Conflict' if result['expected_conflict'] else 'No Conflict'}")
            print(f"      Detected: {'Conflict' if result['detected_conflict'] else 'No Conflict'}")
            print(f"      LLM Reasoning: {result.get('reasoning', 'N/A')[:100]}...")
    
    if golden_cases_pass:
        print(f"   ✅ ALL GOLDEN TEST CASES PASS!")
        print(f"   ✅ Critical Frankfurt→India conflicts detected correctly")
        print(f"   ✅ Ready for pipeline integration")
    
    # Production readiness assessment
    print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
    if correct_predictions >= total_tests * 0.9 and genuine_llm_count == total_tests and golden_cases_pass:
        print(f"   ✅ PRODUCTION READY")
        print(f"   ✅ High accuracy: {correct_predictions/total_tests*100:.1f}%")
        print(f"   ✅ Genuine LLM processing confirmed")
        print(f"   ✅ Golden test cases pass")
        print(f"   ✅ RECOMMENDATION: Replace current specialist with Termie's LLM version")
    else:
        print(f"   ❌ NOT PRODUCTION READY")
        accuracy_ok = correct_predictions >= total_tests * 0.9
        llm_ok = genuine_llm_count == total_tests
        print(f"   Accuracy: {'✅' if accuracy_ok else '❌'} {correct_predictions/total_tests*100:.1f}% (need >90%)")
        print(f"   LLM Processing: {'✅' if llm_ok else '❌'} {genuine_llm_count}/{total_tests} genuine")
        print(f"   Golden Cases: {'✅' if golden_cases_pass else '❌'} Critical test cases")
        if not golden_cases_pass:
            print(f"   ❌ RECOMMENDATION: Escalate to Termie - Golden test cases still failing")
    
    # Specialist statistics
    stats = specialist.get_processing_statistics()
    print(f"\n📊 SPECIALIST STATISTICS:")
    print(f"   Jobs Processed: {stats['jobs_processed']}")
    print(f"   Conflicts Detected: {stats['conflicts_detected']}")
    print(f"   Conflict Rate: {stats['conflict_rate']:.1f}%")
    print(f"   Average Processing Time: {stats['avg_processing_time']:.3f}s")
    
    return results

def main():
    """Main execution function"""
    print("🎯 TERMIE'S LLM LOCATION VALIDATION SPECIALIST v2.0 - GOLDEN TEST SUITE")
    print("Following Sandy's Golden Rules Phase 1: Discovery & Analysis")
    print("Testing against critical failing cases from our current pipeline")
    print("")
    
    results = run_golden_test_suite()
    
    # Save detailed results
    results_file = f"termie_location_validation_test_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    print("🎯 Golden Test Suite Complete!")
    
    return results

if __name__ == "__main__":
    main()
