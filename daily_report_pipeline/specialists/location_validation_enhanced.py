"""
Location Validation Specialist - Enhanced LLM Integration
=========================================================

Integrates Termie's LLM-powered Location Validation Specialist v2.0 into our modular pipeline.
This specialist successfully catches critical Frankfurt→India conflicts that our previous 
specialist missed.

Key Improvements:
- Genuine LLM processing (>2s average processing time)
- Correctly detects Frankfurt→India conflicts (critical golden test cases)
- High confidence scores and detailed analysis
- Template-based parsing for reliability

Usage in Pipeline:
from daily_report_pipeline.specialists.location_validation_enhanced import LocationValidationEnhanced
"""

import logging
import time
import sys
import os
from typing import Dict, Any, Optional

# Import the LLM specialist - handle both direct execution and module import
try:
    from .location_validation_specialist_llm import LocationValidationSpecialistLLM, LocationValidationResult
except ImportError:
    # Direct execution - add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from location_validation_specialist_llm import LocationValidationSpecialistLLM, LocationValidationResult

logger = logging.getLogger(__name__)

class LocationValidationEnhanced:
    """
    Enhanced Location Validation Specialist using Termie's LLM-powered v2.0
    
    Integrates seamlessly with our modular pipeline while providing:
    - Critical conflict detection (Frankfurt→India cases)
    - Genuine LLM processing 
    - High confidence analysis
    - Detailed reasoning and risk assessment
    """
    
    def __init__(self):
        """Initialize the enhanced location validation specialist"""
        self.specialist = LocationValidationSpecialistLLM()
        self.stats = {
            'jobs_processed': 0,
            'conflicts_detected': 0,
            'high_risk_conflicts': 0,
            'total_processing_time': 0
        }
        logger.info("✅ Enhanced Location Validation Specialist initialized (LLM-powered v2.0)")
    
    def validate_job_location(self, job_data: Dict[str, Any], job_id: str = "unknown") -> Dict[str, Any]:
        """
        Main validation method for pipeline integration
        
        Args:
            job_data: Job data dictionary with 'location' and 'description' keys
            job_id: Job identifier for tracking
            
        Returns:
            Dictionary with validation results formatted for pipeline
        """
        start_time = time.time()
        
        # Extract required fields
        metadata_location = job_data.get('location', 'Unknown')
        job_description = job_data.get('description', '')
        
        logger.info(f"🌍 Processing location validation for job {job_id} - Metadata: {metadata_location}")
        
        try:
            # Use Termie's LLM specialist
            result = self.specialist.validate_location(
                metadata_location=metadata_location,
                job_description=job_description,
                job_id=job_id
            )
            
            # DEBUG: Log the raw LLM specialist result
            logger.info(f"🔍 DEBUG - Raw LLM Result for {job_id}:")
            logger.info(f"    metadata_location_accurate: {result.metadata_location_accurate}")
            logger.info(f"    authoritative_location: '{result.authoritative_location}'")
            logger.info(f"    conflict_detected: {result.conflict_detected}")
            logger.info(f"    confidence_score: {result.confidence_score}")
            logger.info(f"    analysis_details: {result.analysis_details}")
            
            # Update our statistics
            self.stats['jobs_processed'] += 1
            self.stats['total_processing_time'] += result.processing_time
            
            if result.conflict_detected:
                self.stats['conflicts_detected'] += 1
                
                # Track high-risk conflicts (different countries/continents)
                risk_level = result.analysis_details.get('risk_level', 'low')
                if risk_level in ['critical', 'high']:
                    self.stats['high_risk_conflicts'] += 1
            
            # Format for pipeline compatibility
            validation_result = {
                'metadata_location_accurate': result.metadata_location_accurate,
                'authoritative_location': result.authoritative_location,
                'conflict_detected': result.conflict_detected,
                'confidence_score': result.confidence_score,
                'risk_level': result.analysis_details.get('risk_level', 'low'),
                'reasoning': result.analysis_details.get('reasoning', ''),
                'extracted_locations': result.analysis_details.get('extracted_locations', []),
                'processing_time': result.processing_time,
                'llm_model': result.analysis_details.get('llm_model', 'llama3.2:latest'),
                'specialist_version': 'Enhanced LLM v2.0'
            }
            
            # Generate summary for report
            if result.conflict_detected:
                summary = f"⚠️ CONFLICT: {metadata_location} → {result.authoritative_location} "
                summary += f"(Risk: {risk_level.upper()}, Confidence: {result.confidence_score:.0f}%)"
            else:
                summary = f"✅ VALIDATED: {metadata_location} "
                summary += f"(Confidence: {result.confidence_score:.0f}%)"
            
            validation_result['summary'] = summary
            
            logger.info(f"✅ Location validation completed for job {job_id} - {summary}")
            
            return validation_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Location validation failed for job {job_id}: {str(e)}")
            
            # Return safe fallback result
            return {
                'metadata_location_accurate': True,  # Conservative default
                'authoritative_location': metadata_location,
                'conflict_detected': False,
                'confidence_score': 0.0,
                'risk_level': 'unknown',
                'reasoning': f"Processing error: {str(e)}",
                'extracted_locations': [],
                'processing_time': processing_time,
                'llm_model': 'error',
                'specialist_version': 'Enhanced LLM v2.0',
                'summary': f"❌ ERROR: {metadata_location} (Processing failed)",
                'error': str(e)
            }
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get processing statistics for monitoring"""
        if self.stats['jobs_processed'] == 0:
            return {
                'jobs_processed': 0,
                'conflict_rate': 0.0,
                'high_risk_rate': 0.0,
                'avg_processing_time': 0.0
            }
        
        return {
            'jobs_processed': self.stats['jobs_processed'],
            'conflicts_detected': self.stats['conflicts_detected'],
            'high_risk_conflicts': self.stats['high_risk_conflicts'],
            'conflict_rate': (self.stats['conflicts_detected'] / self.stats['jobs_processed']) * 100,
            'high_risk_rate': (self.stats['high_risk_conflicts'] / self.stats['jobs_processed']) * 100,
            'avg_processing_time': self.stats['total_processing_time'] / self.stats['jobs_processed']
        }


def main():
    """Demo the enhanced location validation for pipeline testing"""
    print("🌍 Enhanced Location Validation Specialist - Pipeline Integration Demo")
    print("=" * 70)
    
    specialist = LocationValidationEnhanced()
    
    # Test cases
    test_cases = [
        {
            'name': 'Frankfurt→Pune conflict',
            'job': {
                'location': 'Frankfurt',
                'description': '''
                Senior Software Engineer - Deutsche Bank Technology Center
                
                Join our development team at Deutsche Bank Technology Center in Pune, India.
                This position is based in our state-of-the-art Pune office and requires
                on-site collaboration with our growing India operations team.
                '''
            }
        },
        {
            'name': 'Berlin no conflict',
            'job': {
                'location': 'Berlin, Germany',
                'description': '''
                Senior Software Engineer - Tech Company
                
                We are looking for a passionate software engineer to join our Berlin team.
                This role offers great opportunities for growth in our German headquarters.
                Modern office environment with excellent benefits.
                '''
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🧪 Test {i+1}: {test_case['name']}...")
        result = specialist.validate_job_location(test_case['job'], f"demo_test_{i+1}")
        
        print(f"   Summary: {result['summary']}")
        print(f"   Conflict: {result['conflict_detected']}")
        print(f"   Authoritative: {result['authoritative_location']}")
        print(f"   Risk: {result['risk_level']}")
    
    # Show final stats
    stats = specialist.get_validation_statistics()
    print(f"\n📈 Final Statistics: {stats}")



if __name__ == "__main__":
    main()
