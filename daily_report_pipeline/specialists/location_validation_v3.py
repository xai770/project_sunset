#!/usr/bin/env python3
"""
Enhanced Location Validation Specialist v3.0 - Hybrid Regex + LLM Approach
Fixes the 20% false positive hallucination issue identified by Arden
"""

import re
import time
import logging
from typing import Dict, Any, List, Optional

from ..core.llm_base import ProfessionalLLMCore
from ..core.data_models import LocationValidationResult

class LocationValidationSpecialistV3(ProfessionalLLMCore):
    """Enhanced location validation using hybrid regex + LLM approach to eliminate hallucinations"""
    
    def __init__(self):
        super().__init__()
        self.specialist_name = "Enhanced Location Validation Specialist v3.0"
        self._init_location_patterns()
    
    def _init_location_patterns(self):
        """Initialize comprehensive German and international location patterns"""
        
        # German cities with common variations
        self.german_cities = {
            'frankfurt': ['frankfurt', 'frankfurt am main', 'frankfurt/main', 'ffm'],
            'berlin': ['berlin'],
            'münchen': ['münchen', 'munich'],
            'hamburg': ['hamburg'],
            'köln': ['köln', 'cologne'],
            'düsseldorf': ['düsseldorf', 'duesseldorf'],
            'stuttgart': ['stuttgart'],
            'dortmund': ['dortmund'],
            'essen': ['essen'],
            'bremen': ['bremen'],
            'dresden': ['dresden'],
            'leipzig': ['leipzig'],
            'hannover': ['hannover', 'hanover'],
            'nürnberg': ['nürnberg', 'nuremberg'],
            'duisburg': ['duisburg']
        }
        
        # German states
        self.german_states = {
            'hessen': ['hessen', 'hesse'],
            'bayern': ['bayern', 'bavaria'],
            'baden-württemberg': ['baden-württemberg', 'baden-wuerttemberg'],
            'nordrhein-westfalen': ['nordrhein-westfalen', 'nrw', 'north rhine-westphalia'],
            'niedersachsen': ['niedersachsen', 'lower saxony'],
            'berlin': ['berlin'],
            'hamburg': ['hamburg'],
            'bremen': ['bremen'],
            'sachsen': ['sachsen', 'saxony'],
            'thüringen': ['thüringen', 'thuringia'],
            'sachsen-anhalt': ['sachsen-anhalt', 'saxony-anhalt'],
            'brandenburg': ['brandenburg'],
            'mecklenburg-vorpommern': ['mecklenburg-vorpommern'],
            'schleswig-holstein': ['schleswig-holstein'],
            'saarland': ['saarland'],
            'rheinland-pfalz': ['rheinland-pfalz', 'rhineland-palatinate']
        }
        
        # Country variations
        self.country_variants = {
            'deutschland': ['deutschland', 'germany', 'de', 'german', 'deutsche'],
            'österreich': ['österreich', 'austria', 'at', 'austrian'],
            'schweiz': ['schweiz', 'switzerland', 'ch', 'swiss'],
            'united kingdom': ['uk', 'united kingdom', 'great britain', 'britain', 'gb'],
            'united states': ['usa', 'united states', 'america', 'us'],
            'france': ['france', 'fr', 'french'],
            'netherlands': ['netherlands', 'holland', 'nl', 'dutch'],
            'belgium': ['belgium', 'be', 'belgian']
        }
        
        # Create reverse lookup dictionaries
        self._create_lookup_maps()
    
    def _create_lookup_maps(self):
        """Create reverse lookup maps for efficient pattern matching"""
        self.city_lookup = {}
        self.state_lookup = {}
        self.country_lookup = {}
        
        # Cities
        for canonical_city, variants in self.german_cities.items():
            for variant in variants:
                self.city_lookup[variant.lower()] = canonical_city
        
        # States
        for canonical_state, variants in self.german_states.items():
            for variant in variants:
                self.state_lookup[variant.lower()] = canonical_state
        
        # Countries
        for canonical_country, variants in self.country_variants.items():
            for variant in variants:
                self.country_lookup[variant.lower()] = canonical_country
    
    def validate_location(self, metadata_location: str, job_description: str) -> LocationValidationResult:
        """Enhanced location validation with regex-first approach"""
        start_time = time.time()
        
        # Phase 1: Regex-based validation (handles 95% of cases)
        regex_result = self._regex_location_validation(metadata_location, job_description)
        
        if regex_result['confidence'] >= 0.8:
            # High confidence from regex - use this result
            processing_time = time.time() - start_time
            return self._create_result(regex_result, processing_time)
        
        # Phase 2: LLM validation only for ambiguous cases
        if regex_result['confidence'] < 0.8:
            llm_result = self._llm_location_validation(metadata_location, job_description, regex_result)
            processing_time = time.time() - start_time
            return self._create_result(llm_result, processing_time)
        
        # Fallback
        processing_time = time.time() - start_time
        return self._create_result(regex_result, processing_time)
    
    def _regex_location_validation(self, metadata_location: str, job_description: str) -> Dict[str, Any]:
        """Primary regex-based location validation"""
        
        # Parse metadata location
        metadata_parsed = self._parse_location_string(metadata_location)
        
        # Extract locations from job description
        job_locations = self._extract_locations_from_text(job_description)
        
        # Analyze for conflicts
        conflict_detected = False
        authoritative_location = metadata_location
        confidence = 0.9  # High confidence by default
        reasoning = "Regex-based validation"
        
        if not job_locations['cities']:
            # No cities mentioned in job description - no conflict possible
            confidence = 0.95
            reasoning = "No specific cities mentioned in job description - using metadata location"
        else:
            # Check for city conflicts
            metadata_city = metadata_parsed.get('city', '').lower()
            job_cities = [city.lower() for city in job_locations['cities']]
            
            # Normalize cities for comparison
            metadata_city_normalized = self._normalize_city_name(metadata_city)
            job_cities_normalized = [self._normalize_city_name(city) for city in job_cities]
            
            if metadata_city_normalized:
                if metadata_city_normalized in job_cities_normalized:
                    # Same city mentioned - no conflict
                    confidence = 0.95
                    reasoning = f"Same city '{metadata_city}' found in job description"
                else:
                    # Different city mentioned - potential conflict
                    conflicting_cities = [city for city in job_cities_normalized if city != metadata_city_normalized and city in self.city_lookup]
                    
                    if conflicting_cities:
                        conflict_detected = True
                        authoritative_location = f"{conflicting_cities[0].title()}, Deutschland"
                        confidence = 0.85
                        reasoning = f"Different city mentioned in job description: {conflicting_cities[0]}"
                    else:
                        # Cities mentioned but not in our German cities list - might be international
                        confidence = 0.6  # Lower confidence - needs LLM review
                        reasoning = f"Non-German cities mentioned: {', '.join(job_cities)} - needs LLM review"
            else:
                # Can't parse metadata city - needs LLM review
                confidence = 0.5
                reasoning = "Cannot parse metadata city - needs LLM review"
        
        return {
            'conflict_detected': conflict_detected,
            'authoritative_location': authoritative_location,
            'confidence': confidence,
            'reasoning': reasoning,
            'method': 'regex',
            'metadata_parsed': metadata_parsed,
            'job_locations': job_locations
        }
    
    def _llm_location_validation(self, metadata_location: str, job_description: str, regex_result: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback LLM validation for ambiguous cases only"""
        
        # Simplified LLM prompt with context from regex analysis
        validation_prompt = f"""
You are a location validation specialist. A regex analysis has found an ambiguous case that needs expert review.

METADATA LOCATION: {metadata_location}
REGEX ANALYSIS: {regex_result['reasoning']}

JOB DESCRIPTION (first 1000 chars):
{job_description[:1000]}

INSTRUCTIONS:
1. Only report CONFLICT if there's a CLEAR, REAL conflict between different cities/countries
2. Frankfurt vs Frankfurt am Main = NO CONFLICT (same city)
3. Frankfurt, Germany vs Berlin, Germany = CONFLICT (different cities)
4. If unsure, report NO CONFLICT

FORMAT:
CONFLICT: [YES/NO]
LOCATION: [Authoritative work location]
REASONING: [Brief explanation]
"""
        
        try:
            llm_response = self.process_with_llm(validation_prompt, "location validation fallback")
            
            # Parse LLM response with strict validation
            conflict_match = re.search(r'CONFLICT[:\s]+(YES|NO)', llm_response, re.IGNORECASE)
            location_match = re.search(r'LOCATION[:\s]+([^\n]+)', llm_response, re.IGNORECASE)
            reasoning_match = re.search(r'REASONING[:\s]+([^\n]+)', llm_response, re.IGNORECASE)
            
            conflict_detected = False
            if conflict_match and conflict_match.group(1).upper() == 'YES':
                conflict_detected = True
            
            authoritative_location = metadata_location
            if location_match:
                authoritative_location = location_match.group(1).strip()
            
            reasoning = f"LLM analysis: {reasoning_match.group(1) if reasoning_match else 'LLM validation completed'}"
            
            # Safety check: If LLM claims conflict but locations are similar, override
            if conflict_detected and self._locations_are_similar(metadata_location, authoritative_location):
                conflict_detected = False
                reasoning += " (Override: locations are similar)"
            
            return {
                'conflict_detected': conflict_detected,
                'authoritative_location': authoritative_location,
                'confidence': 0.75,  # Lower confidence for LLM results
                'reasoning': reasoning,
                'method': 'llm',
                'llm_response': llm_response
            }
            
        except Exception as e:
            # LLM failed - use regex result as fallback
            return {
                'conflict_detected': False,
                'authoritative_location': metadata_location,
                'confidence': 0.6,
                'reasoning': f"LLM validation failed ({str(e)}) - using metadata location",
                'method': 'fallback'
            }
    
    def _parse_location_string(self, location: str) -> Dict[str, str]:
        """Parse location string into components"""
        if not location:
            return {}
        
        parts = [part.strip() for part in location.split(',')]
        
        parsed = {}
        
        for part in parts:
            part_lower = part.lower()
            
            # Check if it's a city
            normalized_city = self._normalize_city_name(part_lower)
            if normalized_city in self.city_lookup:
                parsed['city'] = self.city_lookup[normalized_city]
            
            # Check if it's a state
            if part_lower in self.state_lookup:
                parsed['state'] = self.state_lookup[part_lower]
            
            # Check if it's a country
            if part_lower in self.country_lookup:
                parsed['country'] = self.country_lookup[part_lower]
        
        return parsed
    
    def _extract_locations_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract locations from job description text"""
        if not text:
            return {'cities': [], 'states': [], 'countries': []}
        
        text_lower = text.lower()
        
        found_cities = []
        found_states = []
        found_countries = []
        
        # Find cities
        for canonical_city, variants in self.german_cities.items():
            for variant in variants:
                if variant in text_lower:
                    found_cities.append(canonical_city)
                    break
        
        # Find states
        for canonical_state, variants in self.german_states.items():
            for variant in variants:
                if variant in text_lower:
                    found_states.append(canonical_state)
                    break
        
        # Find countries
        for canonical_country, variants in self.country_variants.items():
            for variant in variants:
                if variant in text_lower:
                    found_countries.append(canonical_country)
                    break
        
        return {
            'cities': list(set(found_cities)),
            'states': list(set(found_states)),
            'countries': list(set(found_countries))
        }
    
    def _normalize_city_name(self, city: str) -> str:
        """Normalize city name for comparison"""
        if not city:
            return ""
        
        city_lower = city.lower().strip()
        
        # Handle Frankfurt variations
        if any(variant in city_lower for variant in ['frankfurt am main', 'frankfurt/main', 'ffm']):
            return 'frankfurt'
        
        # Remove common suffixes
        city_lower = re.sub(r'\s+(am\s+main|upon.*|city)$', '', city_lower)
        
        return city_lower
    
    def _locations_are_similar(self, loc1: str, loc2: str) -> bool:
        """Check if two locations refer to the same place"""
        if not loc1 or not loc2:
            return False
        
        parsed1 = self._parse_location_string(loc1)
        parsed2 = self._parse_location_string(loc2)
        
        # If both have cities, compare cities
        if 'city' in parsed1 and 'city' in parsed2:
            return parsed1['city'] == parsed2['city']
        
        # If one has city and other doesn't, check if city name appears in the other
        city1 = parsed1.get('city', '').lower()
        city2 = parsed2.get('city', '').lower()
        
        if city1 and city1 in loc2.lower():
            return True
        if city2 and city2 in loc1.lower():
            return True
        
        return False
    
    def _create_result(self, analysis: Dict[str, Any], processing_time: float) -> LocationValidationResult:
        """Create LocationValidationResult from analysis"""
        
        return LocationValidationResult(
            metadata_location_accurate=not analysis['conflict_detected'],
            authoritative_location=analysis['authoritative_location'],
            conflict_detected=analysis['conflict_detected'],
            confidence_score=analysis['confidence'],
            analysis_details={
                'method': analysis.get('method', 'hybrid'),
                'reasoning': analysis['reasoning'],
                'confidence': analysis['confidence'],
                'extracted_locations': analysis.get('job_locations', {}).get('cities', []) if analysis.get('job_locations') else [],
                'llm_model': self.model_name if analysis.get('method') == 'llm' else None
            },
            processing_time=processing_time
        )
    
    def validate_job_location(self, job_data: Dict[str, Any], job_id: str = "unknown") -> Dict[str, Any]:
        """
        Pipeline-compatible method for location validation
        
        Args:
            job_data: Job data containing metadata and description
            job_id: Job identifier for logging
            
        Returns:
            Dictionary with validation results compatible with pipeline
        """
        start_time = time.time()
        
        try:
            # Extract required data
            metadata_location = job_data.get('metadata', {}).get('location', 'Unknown')
            job_description = job_data.get('job_description', '')
            
            # Run validation
            result = self.validate_location(metadata_location, job_description)
            
            processing_time = time.time() - start_time
            
            # Return pipeline-compatible format
            return {
                'metadata_location_accurate': not result.conflict_detected,
                'authoritative_location': result.authoritative_location,
                'conflict_detected': result.conflict_detected,
                'confidence_score': result.confidence_score,
                'extracted_locations': result.analysis_details.get('extracted_locations', []),
                'reasoning': result.analysis_details.get('reasoning', 'Location validation completed'),
                'risk_level': 'low' if not result.conflict_detected else 'medium',
                'processing_time': processing_time,
                'specialist_version': 'v3.0',
                'analysis_details': {
                    'metadata_location': metadata_location,
                    'extracted_locations': result.analysis_details.get('extracted_locations', []),
                    'conflict_type': 'none' if not result.conflict_detected else 'location_mismatch',
                    'reasoning': result.analysis_details.get('reasoning', 'Location validation completed'),
                    'risk_level': 'low' if not result.conflict_detected else 'medium',
                    'validation_method': result.analysis_details.get('method', 'hybrid'),
                    'processing_time': processing_time
                }
            }
            
        except Exception as e:
            logging.error(f"Location validation error for job {job_id}: {e}")
            return {
                'metadata_location_accurate': True,  # Safe fallback
                'authoritative_location': job_data.get('metadata', {}).get('location', 'Unknown'),
                'conflict_detected': False,
                'confidence_score': 0.5,
                'analysis_details': {
                    'error': str(e),
                    'validation_method': 'error_fallback'
                }
            }
