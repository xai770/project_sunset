"""
Domain Classification Specialist
==============================

Integrates the v1.1 domain classification specialist from LLM Factory
into our modular pipeline architecture.

This specialist determines:
1. The primary domain of a job (e.g. finance, technology, legal)
2. The confidence in that classification
3. Whether to proceed with job evaluation based on domain match
"""

import logging
import sys
import os
from typing import Dict, Any, Optional

# Import the LLM specialist - handle both direct execution and module import
try:
    from llm_factory.modules.quality_validation.specialists_versioned.domain_classification.v1_1.src.domain_classification_specialist_llm import classify_job_domain_llm
except ImportError:
    # Direct execution - add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from domain_classification_specialist_llm import classify_job_domain_llm

logger = logging.getLogger(__name__)

class DomainClassificationSpecialist:
    """
    Enhanced Domain Classification using LLM Factory's v1.1 specialist
    
    Provides domain classification with:
    - Primary domain detection
    - Confidence scoring
    - Detailed analysis and reasoning
    - Domain gap detection
    """
    
    def __init__(self):
        """Initialize the domain classification specialist"""
        self.stats = {
            'jobs_processed': 0,
            'high_confidence_matches': 0,
            'domain_gaps_detected': 0
        }
        logger.info("✅ Domain Classification Specialist initialized (LLM-powered v1.1)")
    
    def classify_domain(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main domain classification method
        
        Args:
            job_data: Dictionary with job description and metadata
            
        Returns:
            Dictionary with classification results
        """
        # Extract job information
        job_description = job_data.get('job_description', '')
        job_title = job_data.get('job_metadata', {}).get('title', '')
        job_id = job_data.get('job_metadata', {}).get('id', 'unknown')
        
        logger.info(f"🎯 Processing domain classification for job {job_id}")
        
        try:
            # Use LLM Factory's v1.1 specialist  
            result = classify_job_domain_llm(
                job_description=job_description,
                job_id=job_id
            )
            
            # Update statistics
            self.stats['jobs_processed'] += 1
            if result.get('confidence', 0) > 0.8:
                self.stats['high_confidence_matches'] += 1
            if not result.get('should_proceed_with_evaluation', True):
                self.stats['domain_gaps_detected'] += 1
            
            # Format result for pipeline compatibility
            formatted_result = {
                'primary_domain': result.get('primary_domain_classification', 'unknown'),
                'confidence': result.get('confidence', 0.0),
                'should_proceed': result.get('should_proceed_with_evaluation', True),
                'reasoning': result.get('analysis_details', {}).get('domain_reasoning', ''),
                'specialist_version': 'v1.1',
                'domain_requirements': result.get('analysis_details', {}).get('domain_requirements', []),
                'domain_gaps': result.get('analysis_details', {}).get('domain_gaps', [])
            }
            
            # Log result
            logger.info(f"✅ Domain classification completed: {formatted_result['primary_domain']} "
                       f"(confidence: {formatted_result['confidence']:.2f})")
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"❌ Domain classification failed for job {job_id}: {str(e)}")
            
            # Return safe fallback
            return {
                'primary_domain': 'unknown',
                'confidence': 0.0,
                'should_proceed': True,  # Conservative default
                'reasoning': f"Classification error: {str(e)}",
                'specialist_version': 'v1.1',
                'domain_requirements': [],
                'domain_gaps': [],
                'error': str(e)
            }
    
    def get_classification_statistics(self) -> Dict[str, Any]:
        """Get domain classification statistics"""
        if self.stats['jobs_processed'] == 0:
            return {
                'jobs_processed': 0,
                'high_confidence_rate': 0.0,
                'domain_gap_rate': 0.0
            }
        
        return {
            'jobs_processed': self.stats['jobs_processed'],
            'high_confidence_matches': self.stats['high_confidence_matches'],
            'domain_gaps_detected': self.stats['domain_gaps_detected'],
            'high_confidence_rate': (self.stats['high_confidence_matches'] / self.stats['jobs_processed']) * 100,
            'domain_gap_rate': (self.stats['domain_gaps_detected'] / self.stats['jobs_processed']) * 100
        }
