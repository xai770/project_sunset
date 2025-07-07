#!/usr/bin/env python3
"""
Location Validation Specialist
Enhanced location validation with improved conflict detection
"""

import re
import time
from typing import Dict, Any

from ..core.llm_base import ProfessionalLLMCore
from ..core.data_models import LocationValidationResult

class LocationValidationSpecialist(ProfessionalLLMCore):
    """Professional location validation specialist using LLM analysis"""
    
    def __init__(self):
        super().__init__()
        self.specialist_name = "Location Validation Specialist Enhanced"
    
    def validate_location(self, metadata_location: str, job_description: str) -> LocationValidationResult:
        """Validate job location using LLM analysis"""
        start_time = time.time()
        
        validation_prompt = f"""
You are a location validation specialist. Analyze if there's a REAL CONFLICT between the metadata location and the actual job location mentioned in the description.

METADATA LOCATION: {metadata_location}

JOB DESCRIPTION:
{job_description}

CRITICAL INSTRUCTIONS:
1. Only report CONFLICT_DETECTED: YES if there's a CLEAR MISMATCH between metadata and job description locations
2. If the job description mentions the SAME location as metadata (even with different formatting), report CONFLICT_DETECTED: NO
3. If the job description doesn't mention any specific location, report CONFLICT_DETECTED: NO
4. Examples of NO CONFLICT: "Frankfurt, Deutschland" vs "Frankfurt, Germany" (same city, different language)
5. Examples of CONFLICT: "Frankfurt, Germany" vs "Berlin, Germany" (different cities)

ANALYSIS FORMAT:
CONFLICT_DETECTED: [YES/NO]
AUTHORITATIVE_LOCATION: [The actual location where work will be performed]
CONFIDENCE: [0.0-1.0]
REASONING: [Brief explanation of your analysis]

ANALYSIS:
"""
        
        llm_response = self.process_with_llm(validation_prompt, "location validation")
        
        # Debug: Print LLM response for troubleshooting
        print(f"🔍 LLM Response Debug for '{metadata_location}':")
        print(f"Response: {llm_response[:200]}...")
        print("-" * 40)
        
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
        """Parse LLM response for location analysis with robust conflict detection"""
        if not response:
            return {
                'conflict_detected': False,
                'authoritative_location': metadata_location,
                'confidence': 0.5,
                'reasoning': 'LLM analysis failed - using metadata location'
            }
        
        # More precise conflict detection - look for specific pattern
        conflict_detected = False
        
        # Look for "CONFLICT_DETECTED: YES" pattern specifically
        conflict_match = re.search(r'CONFLICT_DETECTED[:\s]+(YES|NO)', response, re.IGNORECASE)
        if conflict_match:
            conflict_detected = conflict_match.group(1).upper() == 'YES'
        else:
            # Fallback: look for explicit conflict indicators in structured format
            if re.search(r'CONFLICT[:\s]+YES', response, re.IGNORECASE):
                conflict_detected = True
            elif re.search(r'CONFLICT[:\s]+NO', response, re.IGNORECASE):
                conflict_detected = False
            else:
                # Final fallback: use location similarity comparison
                conflict_detected = self._detect_location_conflict_fallback(response, metadata_location)
        
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
        
        # Clean up authoritative location
        authoritative_location = self._clean_location_string(authoritative_location)
        
        # SEMANTIC SIMILARITY CHECK - Override conflict detection if locations are essentially the same
        if conflict_detected and self._locations_are_similar(metadata_location, authoritative_location):
            print(f"🔧 Location validation override: '{metadata_location}' vs '{authoritative_location}' - locations are similar, marking as NO CONFLICT")
            conflict_detected = False
        
        # SAFETY CHECK - If authoritative location is completely different from metadata and no explicit location mentioned in job description
        if conflict_detected and not self._location_mentioned_in_response(response, authoritative_location):
            print(f"🛡️  Safety override: Authoritative location '{authoritative_location}' not found in LLM reasoning, using metadata location")
            authoritative_location = metadata_location
            conflict_detected = False
        
        return {
            'conflict_detected': conflict_detected,
            'authoritative_location': authoritative_location,
            'confidence': confidence,
            'reasoning': response
        }
    
    def _detect_location_conflict_fallback(self, response: str, metadata_location: str) -> bool:
        """Fallback method to detect location conflicts using string similarity"""
        # Extract potential locations mentioned in the response
        response_lower = response.lower()
        metadata_lower = metadata_location.lower()
        
        # Simple similarity check - if metadata location components are mentioned in response
        # and no explicit conflict words, assume no conflict
        metadata_parts = [part.strip() for part in metadata_lower.split(',') if part.strip()]
        
        # Check if any metadata location parts are mentioned in response
        metadata_mentioned = any(part in response_lower for part in metadata_parts if len(part) > 2)
        
        # Look for explicit conflict indicators in reasoning
        conflict_indicators = [
            'different location', 'conflicting location', 'mismatch',
            'location differs', 'not the same location', 'incorrect location'
        ]
        
        explicit_conflict = any(indicator in response_lower for indicator in conflict_indicators)
        
        # If explicit conflict indicators found, return True
        if explicit_conflict:
            return True
            
        # If metadata location parts are mentioned without explicit conflict, assume no conflict
        if metadata_mentioned:
            return False
            
        # Default to no conflict if unclear
        return False
    
    def _clean_location_string(self, location: str) -> str:
        """Clean and normalize location string"""
        if not location:
            return location
            
        # Remove common prefixes and suffixes
        location = location.strip()
        
        # Remove brackets and extra whitespace
        location = re.sub(r'\[.*?\]', '', location)
        location = re.sub(r'\(.*?\)', '', location)
        location = re.sub(r'\s+', ' ', location)
        
        # Remove common location prefixes
        prefixes_to_remove = ['located in', 'based in', 'office in', 'work in']
        for prefix in prefixes_to_remove:
            if location.lower().startswith(prefix):
                location = location[len(prefix):].strip()
                break
        
        return location.strip()
    
    def _locations_are_similar(self, location1: str, location2: str) -> bool:
        """Check if two locations are semantically similar (same city, different formatting)"""
        if not location1 or not location2:
            return False
        
        # Normalize both locations
        loc1_normalized = self._normalize_location(location1)
        loc2_normalized = self._normalize_location(location2)
        
        # Direct match
        if loc1_normalized == loc2_normalized:
            return True
        
        # Check if they share the same city name
        loc1_parts = set(loc1_normalized.split())
        loc2_parts = set(loc2_normalized.split())
        
        # If they share significant location parts, consider them similar
        common_parts = loc1_parts.intersection(loc2_parts)
        
        # Consider similar if they share at least one significant location part
        # and no conflicting location names
        significant_parts = [part for part in common_parts if len(part) > 3]
        
        if significant_parts:
            # Check for conflicting city names
            city_keywords = ['berlin', 'munich', 'hamburg', 'cologne', 'düsseldorf', 'stuttgart', 'dortmund', 'essen', 'bremen', 'dresden', 'leipzig', 'hannover', 'nuremberg', 'duisburg', 'london', 'paris', 'new york', 'frankfurt', 'zürich', 'vienna', 'amsterdam', 'brussels']
            
            loc1_cities = [part for part in loc1_parts if part in city_keywords]
            loc2_cities = [part for part in loc2_parts if part in city_keywords]
            
            # If both have city names and they're different, it's a conflict
            if loc1_cities and loc2_cities and set(loc1_cities) != set(loc2_cities):
                return False
            
            return True
        
        return False
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location string for comparison"""
        if not location:
            return ""
        
        # Convert to lowercase
        normalized = location.lower()
        
        # Replace common variations
        replacements = {
            'deutschland': 'germany',
            'united kingdom': 'uk',
            'united states': 'usa',
            'main': '',  # Remove "am Main" from Frankfurt am Main
            'upon': '',  # Remove "upon" from city names
            'frankfurt am main': 'frankfurt',
            'frankfurt/main': 'frankfurt',
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remove extra spaces and punctuation
        normalized = re.sub(r'[,\-\(\)]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip()
    
    def _location_mentioned_in_response(self, response: str, location: str) -> bool:
        """Check if a location is actually mentioned in the LLM response reasoning"""
        if not response or not location:
            return False
        
        response_lower = response.lower()
        location_lower = location.lower()
        
        # Check if the location or its parts are mentioned in the response
        location_parts = [part.strip() for part in location_lower.split(',') if part.strip() and len(part.strip()) > 2]
        
        for part in location_parts:
            if part in response_lower:
                return True
        
        return False
