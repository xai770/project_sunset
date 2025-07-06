#!/usr/bin/env python3
"""
🌍 LOCATION VALIDATION SPECIALIST TEST - Phase 1 Discovery & Analysis
====================================================================

Testing the LLM Factory Location Validation Specialist to verify:
1. Genuine LLM processing (>1 second execution time)
2. Proper conflict detection capabilities  
3. Accurate location analysis
4. Integration readiness for our pipeline

Part of Sandy's Golden Rules Phase 1: Discovery & Analysis cycle
"""

import json
import time
import logging
import requests
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the LLM Factory classes
import sys
import os
sys.path.append('/home/xai/Documents/sandy/0_mailboxes/sandy@consciousness/favorites')

# Copy the exact classes from LLM Factory demo
class LLMProcessingError(Exception):
    """Raised when LLM processing encounters errors"""
    pass

class ProfessionalLLMCore:
    """Core LLM interface for specialist processing"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3.2:latest"):
        self.ollama_url = ollama_url
        self.model = model
        self.stats = {
            'specialists_executed': 0,
            'total_processing_time': 0,
            'success_rate': 0.0
        }
    
    def process_with_llm(self, prompt: str, operation: str = "LLM processing") -> str:
        """Core LLM processing function"""
        start_time = time.time()
        
        try:
            logger.info(f"Processing: {operation}")
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "top_p": 0.9}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '').strip()
                processing_time = time.time() - start_time
                
                # Update stats
                self.stats['total_processing_time'] += processing_time
                
                logger.info(f"Completed {operation} in {processing_time:.2f}s")
                return result
            else:
                raise LLMProcessingError(f"LLM processing failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"LLM processing error: {e}")
            return ""

@dataclass
class LocationValidationResult:
    specialist_id: str = "location_validation"
    metadata_location_accurate: bool = False
    authoritative_location: str = ""
    conflict_detected: bool = False
    confidence_score: float = 0.0
    analysis_details: Dict[str, Any] = None  #type: ignore
    processing_time: float = 0.0

class LocationValidationSpecialist(ProfessionalLLMCore):
    """Professional location validation specialist using LLM analysis"""
    
    def __init__(self):
        super().__init__()
        self.specialist_name = "Location Validation Specialist"
    
    def validate_location(self, metadata_location: str, job_description: str) -> LocationValidationResult:
        """Validate job location using LLM analysis"""
        start_time = time.time()
        
        logger.info(f"Processing location validation - Metadata: {metadata_location}")
        
        validation_prompt = f"""
You are a location validation specialist. Analyze if there's a conflict between the metadata location and the actual job location mentioned in the description.

METADATA LOCATION: {metadata_location}

JOB DESCRIPTION:
{job_description}

Analyze the job description for any mentions of work locations, office locations, or where the job will be based.

ANALYSIS FORMAT:
CONFLICT_DETECTED: [YES/NO]
AUTHORITATIVE_LOCATION: [The actual location where work will be performed]
CONFIDENCE: [0.0-1.0]
REASONING: [Brief explanation of your analysis]

ANALYSIS:
"""
        
        llm_response = self.process_with_llm(validation_prompt, "location validation")
        analysis_results = self._parse_location_response(llm_response, metadata_location)
        
        processing_time = time.time() - start_time
        self.stats['specialists_executed'] += 1
        
        return LocationValidationResult(
            metadata_location_accurate=not analysis_results['conflict_detected'],
            authoritative_location=analysis_results['authoritative_location'],
            conflict_detected=analysis_results['conflict_detected'],
            confidence_score=analysis_results['confidence'],
            analysis_details=analysis_results,
            processing_time=processing_time
        )
    
    def _parse_location_response(self, response: str, metadata_location: str) -> Dict[str, Any]:
        """Parse LLM response for location analysis"""
        if not response:
            return {
                'conflict_detected': False,
                'authoritative_location': metadata_location,
                'confidence': 0.5,
                'reasoning': 'LLM analysis failed - using metadata location'
            }
        
        conflict_detected = 'YES' in response.upper() or 'CONFLICT' in response.upper()
        
        # Extract confidence score
        confidence = 0.7
        conf_match = re.search(r'CONFIDENCE[:\s]+([\d.]+)', response, re.IGNORECASE)
        if conf_match:
            try:
                confidence = float(conf_match.group(1))
            except ValueError:
                pass
        
        # Extract authoritative location
        auth_match = re.search(r'AUTHORITATIVE_LOCATION[:\s]+([^\n]+)', response, re.IGNORECASE)
        authoritative_location = auth_match.group(1).strip() if auth_match else metadata_location
        
        return {
            'conflict_detected': conflict_detected,
            'authoritative_location': authoritative_location,
            'confidence': confidence,
            'reasoning': response
        }

# Test cases for location validation
TEST_CASES = [
    {
        "name": "Perfect Match - Frankfurt",
        "metadata_location": "Frankfurt, Germany",
        "job_description": """
Senior Software Engineer - Python/Machine Learning
Location: Frankfurt, Germany

We are seeking a talented Senior Software Engineer to join our dynamic team in Frankfurt. 
The role involves developing cutting-edge machine learning applications.
Modern office space in the heart of Frankfurt.
        """,
        "expected_conflict": False
    },
    {
        "name": "Clear Conflict - Remote vs Office",
        "metadata_location": "Frankfurt, Germany", 
        "job_description": """
Remote Software Developer
Location: Fully Remote (Germany)

This is a 100% remote position. You can work from anywhere in Germany.
No office visits required. All meetings conducted via video conference.
        """,
        "expected_conflict": True
    },
    {
        "name": "Hybrid Model - Should Detect Nuance",
        "metadata_location": "Munich, Germany",
        "job_description": """
Technical Lead Position
Location: Munich, Germany (Hybrid)

Based in our Munich office with flexible remote work options.
2-3 days per week in the Munich office required.
Remaining days can be worked from home.
        """,
        "expected_conflict": False
    },
    {
        "name": "Location Conflict - Different Cities",
        "metadata_location": "Berlin, Germany",
        "job_description": """
DevOps Engineer
Location: Hamburg, Germany

Join our Hamburg-based team for this exciting DevOps role.
Daily collaboration with our Hamburg development team.
Position requires presence in our Hamburg headquarters.
        """,
        "expected_conflict": True
    },
    {
        "name": "Ambiguous Case - Multiple Locations",
        "metadata_location": "Cologne, Germany",
        "job_description": """
Regional Sales Manager
Territory: Germany, Austria, Switzerland

This role covers multiple locations across DACH region.
Travel required to various client sites in Germany and Austria.
Home office can be anywhere in Germany.
        """,
        "expected_conflict": False  # Flexible location
    }
]

def check_llm_connection(url: str = "http://localhost:11434") -> bool:
    """Check if LLM service is running and accessible"""
    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def run_location_validation_tests():
    """Run comprehensive location validation tests"""
    print("🌍 LOCATION VALIDATION SPECIALIST TEST SUITE")
    print("=" * 60)
    
    # Check LLM connection
    if not check_llm_connection():
        print("❌ ERROR: Ollama is not running or not accessible!")
        print("   Please ensure Ollama is running on localhost:11434")
        return
    
    print("✅ LLM service connection verified!")
    
    # Initialize specialist
    location_specialist = LocationValidationSpecialist()
    test_results = []
    
    print(f"\n🧪 RUNNING {len(TEST_CASES)} TEST CASES")
    print("-" * 60)
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n📋 TEST CASE {i}: {test_case['name']}")
        print(f"   Metadata Location: {test_case['metadata_location']}")
        print(f"   Expected Conflict: {'Yes' if test_case['expected_conflict'] else 'No'}")
        
        # Run validation
        try:
            result = location_specialist.validate_location(
                test_case['metadata_location'],
                test_case['job_description']
            )
            
            # Analyze results
            conflict_match = result.conflict_detected == test_case['expected_conflict']
            processing_time_ok = result.processing_time > 1.0  # Sandy's Golden Rule
            
            print(f"   ✅ RESULTS:")
            print(f"      Conflict Detected: {'Yes' if result.conflict_detected else 'No'}")
            print(f"      Authoritative Location: {result.authoritative_location}")
            print(f"      Confidence Score: {result.confidence_score:.2f}")
            print(f"      Processing Time: {result.processing_time:.2f}s")
            print(f"      Expected Match: {'✅ CORRECT' if conflict_match else '❌ INCORRECT'}")
            print(f"      LLM Processing: {'✅ GENUINE' if processing_time_ok else '❌ FAKE (<1s)'}")
            
            # Store results
            test_results.append({
                'test_name': test_case['name'],
                'conflict_detected': result.conflict_detected,
                'expected_conflict': test_case['expected_conflict'],
                'correct_prediction': conflict_match,
                'processing_time': result.processing_time,
                'genuine_llm': processing_time_ok,
                'confidence_score': result.confidence_score,
                'authoritative_location': result.authoritative_location,
                'analysis_details': result.analysis_details
            })
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            test_results.append({
                'test_name': test_case['name'],
                'error': str(e),
                'correct_prediction': False,
                'genuine_llm': False
            })
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY REPORT")
    print("=" * 60)
    
    total_tests = len(test_results)
    correct_predictions = sum(1 for r in test_results if r.get('correct_prediction', False))
    genuine_llm_count = sum(1 for r in test_results if r.get('genuine_llm', False))
    avg_processing_time = sum(r.get('processing_time', 0) for r in test_results) / total_tests
    avg_confidence = sum(r.get('confidence_score', 0) for r in test_results) / total_tests
    
    print(f"📈 OVERALL PERFORMANCE:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Correct Predictions: {correct_predictions}/{total_tests} ({correct_predictions/total_tests*100:.1f}%)")
    print(f"   Genuine LLM Processing: {genuine_llm_count}/{total_tests} ({genuine_llm_count/total_tests*100:.1f}%)")
    print(f"   Average Processing Time: {avg_processing_time:.2f}s")
    print(f"   Average Confidence Score: {avg_confidence:.2f}")
    
    # Sandy's Golden Rules Compliance
    print(f"\n🎯 SANDY'S GOLDEN RULES COMPLIANCE:")
    if genuine_llm_count == total_tests:
        print(f"   ✅ NO FAKE SPECIALISTS DETECTED")
        print(f"   ✅ All processing times >1 second")
        print(f"   ✅ Genuine LLM-powered processing confirmed")
    else:
        print(f"   ❌ FAKE SPECIALIST ALERT!")
        print(f"   ❌ {total_tests - genuine_llm_count} tests completed in <1 second")
        print(f"   ❌ ESCALATION TO TERMIE REQUIRED!")
    
    # Production readiness assessment
    print(f"\n🚀 PRODUCTION READINESS:")
    if correct_predictions >= total_tests * 0.8 and genuine_llm_count == total_tests:
        print(f"   ✅ PRODUCTION READY")
        print(f"   ✅ High accuracy + genuine LLM processing")
        print(f"   ✅ Safe for pipeline integration")
    else:
        print(f"   ❌ NOT PRODUCTION READY")
        print(f"   ❌ Requires improvement or replacement")
    
    return test_results

def main():
    """Main test execution function"""
    print("🎯 PHASE 1: DISCOVERY & ANALYSIS")
    print("Testing Location Validation Specialist from LLM Factory")
    print("Following Sandy's Golden Rules for specialist validation")
    print("")
    
    test_results = run_location_validation_tests()
    
    # Save detailed results
    results_file = f"location_validation_test_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    print("🎯 Phase 1 Discovery & Analysis: Location Validation Testing Complete!")

if __name__ == "__main__":
    main()
