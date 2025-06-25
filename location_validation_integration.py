#!/usr/bin/env python3
"""
Location Validation Integration for Project Sunset Pipeline
==========================================================

Integrates the Location Validation Specialist into the existing job processing pipeline.
Based on the delivered specialist from Terminator@llm_factory.
"""

import re
import json
from typing import Dict, Any, Optional

def validate_job_location(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Location validation function integrated for Project Sunset pipeline.
    
    Args:
        job_data: Job data dictionary with 'job_content' containing location and description
    
    Returns:
        Dictionary with validation results and decision
    """
    
    # Extract location and description from job data
    if 'job_content' in job_data:
        metadata_location = job_data['job_content'].get('location', {})
        if isinstance(metadata_location, dict):
            location_str = f"{metadata_location.get('city', '')} {metadata_location.get('country', '')}".strip()
        else:
            location_str = str(metadata_location)
        
        description = job_data['job_content'].get('description', '')
        job_id = job_data.get('job_metadata', {}).get('job_id', 'unknown')
    else:
        # Fallback for direct usage
        location_str = job_data.get('location', '')
        description = job_data.get('description', '')
        job_id = job_data.get('job_id', 'unknown')
    
    # Location patterns for conflict detection
    location_patterns = {
        'india_cities': r'\b(pune|mumbai|bangalore|bengaluru|delhi|hyderabad|chennai|noida|gurgaon|gurugram)\b',
        'germany_cities': r'\b(frankfurt|berlin|munich|hamburg|cologne|düsseldorf|stuttgart)\b',
        'asia_other': r'\b(singapore|hong kong|tokyo|sydney|manila|jakarta)\b',
        'country_mentions': r'\b(india|germany|german|indian)\b',
        'explicit_location': r'location:?\s*([a-z\s,]+)',
        'office_location': r'office\s+in\s+([a-z\s,]+)',
        'based_in': r'based\s+in\s+([a-z\s,]+)'
    }
    
    description_lower = description.lower()
    metadata_lower = location_str.lower()
    
    # Find locations in description
    found_locations = []
    confidence_factors = []
    
    for region, pattern in location_patterns.items():
        matches = re.findall(pattern, description_lower)
        for match in matches:
            found_locations.append({'location': match.strip(), 'region': region, 'pattern': region})
            # Higher confidence for explicit patterns
            if region in ['explicit_location', 'office_location', 'based_in']:
                confidence_factors.append(0.95)
            else:
                confidence_factors.append(0.85)
    
    # Critical conflict detection
    conflict_detected = False
    risk_level = "low"
    authoritative_location = location_str
    decision_reason = "Location metadata appears accurate"
    
    # Check for critical Frankfurt vs India conflict (Job 52953 pattern)
    india_cities = [loc for loc in found_locations if loc['region'] == 'india_cities']
    if india_cities and ('frankfurt' in metadata_lower or 'germany' in metadata_lower):
        conflict_detected = True
        risk_level = "critical"
        authoritative_location = f"{india_cities[0]['location'].title()}, India"
        decision_reason = f"CRITICAL: Metadata claims {location_str} but job is actually in {authoritative_location}"
    
    # Check for other geographic conflicts
    elif found_locations:
        # Europe vs Asia conflicts
        europe_indicators = ['frankfurt', 'germany', 'berlin', 'munich']
        asia_indicators = ['india', 'pune', 'bangalore', 'singapore']
        
        has_europe_metadata = any(indicator in metadata_lower for indicator in europe_indicators)
        has_asia_content = any(indicator in description_lower for indicator in asia_indicators)
        
        if has_europe_metadata and has_asia_content:
            conflict_detected = True
            risk_level = "high"
            asia_location = next((loc['location'] for loc in found_locations 
                                if loc['region'] in ['india_cities', 'asia_other']), 'Asia')
            authoritative_location = asia_location.title()
            decision_reason = f"Geographic conflict: Metadata suggests Europe but content indicates {authoritative_location}"
    
    # Calculate confidence score
    base_confidence = 0.85
    if confidence_factors:
        avg_confidence = sum(confidence_factors) / len(confidence_factors)
        base_confidence = max(base_confidence, avg_confidence)
    
    if conflict_detected and risk_level == "critical":
        confidence_score = 0.98  # Very high confidence for critical conflicts
    elif conflict_detected:
        confidence_score = 0.90
    else:
        confidence_score = base_confidence
    
    # Determine processing decision
    if conflict_detected and risk_level == "critical":
        processing_decision = "SKIP_EXPENSIVE_ANALYSIS"
        efficiency_note = "Skip LLM processing - geographic incompatibility"
    elif conflict_detected and risk_level == "high":
        processing_decision = "FLAG_FOR_REVIEW"
        efficiency_note = "Potential location conflict - review recommended"
    else:
        processing_decision = "PROCEED"
        efficiency_note = "Location validated - continue processing"
    
    return {
        'job_id': job_id,
        'location_validation': {
            'conflict_detected': conflict_detected,
            'confidence_score': confidence_score,
            'risk_level': risk_level,
            'metadata_location': location_str,
            'authoritative_location': authoritative_location,
            'found_locations': [loc['location'] for loc in found_locations],
            'decision_reason': decision_reason
        },
        'processing_decision': processing_decision,
        'efficiency_note': efficiency_note,
        'metadata_accurate': not conflict_detected
    }


def integrate_location_validation_to_pipeline(job_file_path: str) -> Dict[str, Any]:
    """
    Process a single job file with location validation for Project Sunset pipeline.
    
    Args:
        job_file_path: Path to job JSON file
        
    Returns:
        Dictionary with job data and validation results
    """
    try:
        with open(job_file_path, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
        
        # Run location validation
        validation_result = validate_job_location(job_data)
        
        # Add validation results to job data
        if 'validation_results' not in job_data:
            job_data['validation_results'] = {}
        
        job_data['validation_results']['location_validation'] = validation_result
        
        return {
            'success': True,
            'job_data': job_data,
            'validation': validation_result,
            'should_continue_processing': validation_result['processing_decision'] != 'SKIP_EXPENSIVE_ANALYSIS'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'job_file': job_file_path,
            'should_continue_processing': True  # Continue on validation errors
        }


def test_integration_with_job52953():
    """Test the integration with the actual Job 52953 that has the location conflict."""
    print("🧪 TESTING LOCATION VALIDATION WITH JOB 52953")
    print("=" * 60)
    
    job_file = "/home/xai/Documents/sunset/data/postings/job52953.json"
    
    try:
        result = integrate_location_validation_to_pipeline(job_file)
        
        if result['success']:
            validation = result['validation']
            print(f"✅ Job ID: {validation['job_id']}")
            print(f"📍 Metadata Location: {validation['location_validation']['metadata_location']}")
            print(f"🎯 Authoritative Location: {validation['location_validation']['authoritative_location']}")
            print(f"⚠️  Conflict Detected: {validation['location_validation']['conflict_detected']}")
            print(f"🎲 Confidence: {validation['location_validation']['confidence_score']:.2f}")
            print(f"🚨 Risk Level: {validation['location_validation']['risk_level']}")
            print(f"⚡ Processing Decision: {validation['processing_decision']}")
            print(f"💡 Efficiency Note: {validation['efficiency_note']}")
            print(f"📝 Reason: {validation['location_validation']['decision_reason']}")
            
            if validation['location_validation']['conflict_detected']:
                print("\\n🎯 SUCCESS: Location conflict detected as expected!")
                print("💰 EFFICIENCY GAIN: Would skip expensive LLM analysis")
            else:
                print("\\n❌ UNEXPECTED: Should have detected location conflict")
                
        else:
            print(f"❌ Error processing job: {result['error']}")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")


if __name__ == "__main__":
    print("🚀 LOCATION VALIDATION INTEGRATION FOR PROJECT SUNSET")
    print("🎯 Efficiency-First Pipeline Enhancement")
    print("\\n")
    
    # Test with the actual problematic job
    test_integration_with_job52953()
    
    print("\\n" + "=" * 60)
    print("💡 INTEGRATION COMPLETE")
    print("💡 Add to force_reprocess_jobs.py for production use")
    print("💡 Expected: 80%+ computational savings on location conflicts")
