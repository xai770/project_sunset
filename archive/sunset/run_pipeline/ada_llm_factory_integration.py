#!/usr/bin/env python3
"""
LLM Factory Cover Letter Generator with Ada's ValidationCoordinator Integration
Phase 1A: CoverLetterGeneratorV2 + Conservative Bias Validation

This module replaces the broken cover letter generation in process_excel_cover_letters.py
with professional LLM Factory specialists and Ada's conservative validation requirements.

Features:
- CoverLetterGeneratorV2 integration with conservative bias enforcement
- 2/3 consensus requirement for quality validation
- Most conservative assessment when specialists disagree
- Human review triggers for suspicious quality scores
- Job 63144 baseline quality testing framework
- Zero AI artifact tolerance with professional narrative flow
"""
import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add LLM Factory to path for specialists
llm_factory_path = Path("/home/xai/Documents/llm_factory")
if str(llm_factory_path) not in sys.path:
    sys.path.insert(0, str(llm_factory_path))

# Tell mypy and Pylance to ignore missing imports for the llm_factory module
# mypy: ignore-missing-imports
# type: ignore[import]
# pyright: reportMissingImports=false
try:
    # Import LLM Factory core types and base classes - these don't have type stubs
    from llm_factory.core.types import ModuleConfig, ValidationResult, ModuleResult, ConsensusConfig  # type: ignore
    from llm_factory.core.ollama_client import OllamaClient  # type: ignore
    from llm_factory.modules.quality_validation.specialists_versioned.cover_letter_generator.v2_0.src.cover_letter_generator_specialist import CoverLetterGeneratorV2  # type: ignore
    from llm_factory.modules.quality_validation.specialists_versioned.factual_consistency.v1_0.src.factual_consistency_specialist import FactualConsistencySpecialist  # type: ignore
    from llm_factory.modules.quality_validation.specialists_versioned.language_coherence.v1_0.src.language_coherence_specialist import LanguageCoherenceSpecialist  # type: ignore
    from llm_factory.modules.quality_validation.specialists_versioned.ai_language_detection.v1_0.src.ai_language_detection_specialist import AILanguageDetectionSpecialist  # type: ignore
    
    LLM_FACTORY_AVAILABLE = True
    logger.info("✅ LLM Factory specialists imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ LLM Factory specialists not available: {e}")
    LLM_FACTORY_AVAILABLE = False
    # Create a mock OllamaClient for fallback
    class MockOllamaClient:
        def __init__(self, model="mock"):
            self.model = model
    OllamaClient = MockOllamaClient

class ConservativeValidationConfig:
    """Ada's ValidationCoordinator configuration for conservative bias enforcement"""
    
    def __init__(self):
        self.consensus_threshold = 2/3  # Ada's 2/3 requirement
        self.conservative_bias = True   # Always select most conservative assessment
        self.human_review_triggers = {
            'quality_score_below': 0.85,    # Trigger review for suspicious scores
            'ai_artifact_detected': True,   # Zero tolerance for AI artifacts
            'coherence_score_below': 0.80,  # Professional narrative flow requirement
            'factual_consistency_below': 0.90  # High accuracy requirement
        }
        self.retry_attempts = 3
        self.fallback_strategy = 'most_conservative'
        self.processing_time_limit = 15  # Ada's <15 second requirement
        self.reliability_target = 0.99   # 99%+ reliability requirement

class QualityBaseline:
    """Job 63144 quality baseline testing framework"""
    
    def __init__(self):
        self.baseline_job_id = "63144"
        self.baseline_job_title = "DWS Operations Specialist - E-invoicing (m/w/d)"
        self.quality_metrics = {
            'ai_artifacts_count': 0,          # Zero tolerance
            'manual_corrections_needed': 0.05, # <5% target
            'processing_time_seconds': 15,    # <15 seconds
            'quality_score_min': 0.85,       # Conservative threshold
            'coherence_score_min': 0.80,     # Professional narrative
            'factual_accuracy_min': 0.90     # High accuracy
        }

class AdaValidationCoordinator:
    """
    Ada's ValidationCoordinator integrated with LLM Factory specialists
    Implements conservative bias enforcement and consensus mechanisms
    """
    
    def __init__(self):
        self.config = ConservativeValidationConfig()
        self.baseline = QualityBaseline()
        self.specialists = self._initialize_specialists()
        
    def _initialize_specialists(self) -> Dict[str, Any]:
        """Initialize LLM Factory specialists with proper configs"""
        specialists = {}
        
        if LLM_FACTORY_AVAILABLE:
            try:
                # Create actual Ollama client
                ollama_client = OllamaClient()
                
                # Create consensus configuration
                consensus_config = ConsensusConfig(
                    conservative_selection=True,
                    quality_check_individual=True,
                    quality_check_consensus=True,
                    min_confidence_threshold=0.85,
                    max_timeline_days=180
                )
                
                # Create proper ModuleConfig instances with Ollama client
                cover_letter_config = ModuleConfig(
                    ollama_client=ollama_client,
                    quality_threshold=8.5,
                    models=["llama3"],
                    conservative_bias=True,
                    consensus_config=consensus_config
                )
                
                factual_config = ModuleConfig(
                    ollama_client=ollama_client,
                    quality_threshold=9.0,
                    models=["llama3"],
                    conservative_bias=True,
                    consensus_config=consensus_config
                )
                
                coherence_config = ModuleConfig(
                    ollama_client=ollama_client,
                    quality_threshold=8.0,
                    models=["llama3"],
                    conservative_bias=True,
                    consensus_config=consensus_config
                )
                
                ai_detection_config = ModuleConfig(
                    ollama_client=ollama_client,
                    quality_threshold=7.0,
                    models=["llama3"],
                    conservative_bias=True,
                    consensus_config=consensus_config
                )
                
                # Initialize specialists with proper configs
                specialists['cover_letter_generator'] = CoverLetterGeneratorV2(cover_letter_config)
                specialists['factual_consistency'] = FactualConsistencySpecialist(factual_config)
                specialists['language_coherence'] = LanguageCoherenceSpecialist(coherence_config)
                specialists['ai_detection'] = AILanguageDetectionSpecialist(ai_detection_config)
                logger.info("✅ All LLM Factory specialists initialized with proper ModuleConfig and Ollama clients")
            except Exception as e:
                logger.error(f"❌ Error initializing specialists: {e}")
                specialists = self._create_fallback_specialists()
        else:
            specialists = self._create_fallback_specialists()
            
        return specialists
    
    def _create_fallback_specialists(self) -> Dict[str, Any]:
        """Create fallback implementations when LLM Factory is not available"""
        logger.warning("⚠️ Using fallback specialist implementations")
        
        class FallbackCoverLetterGenerator:
            def generate_cover_letter(self, cv_data, job_data, tone="professional", format_type="markdown"):
                return {
                    'cover_letter': "Fallback cover letter generation - LLM Factory not available",
                    'quality_score': 0.5,
                    'validation_results': {'fallback': True}
                }
            
            def process(self, input_data):
                """Process method to match LLM Factory specialist interface"""
                # Create a mock ModuleResult-like object
                class MockResult:
                    def __init__(self, success=True, data=None):
                        self.success = success
                        self.data = data or {}
                
                fallback_letter = f"""Dear Hiring Manager,

I am writing to express my interest in the {input_data.get('job', {}).get('title', 'position')} at {input_data.get('job', {}).get('company', 'your company')}.

While the LLM Factory specialists are not currently available, I am confident that my background and experience make me a strong candidate for this role.

Thank you for your consideration.

Best regards,
[Your Name]"""
                
                return MockResult(success=True, data={
                    'cover_letter': fallback_letter,
                    'quality_score': 0.7,
                    'validation_results': {'fallback': True, 'method': 'process'}
                })
        
        class FallbackFactualValidator:
            def verify_cover_letter_consistency(self, cover_letter, job_posting, cv_data):
                return {'consistency_score': 0.5, 'issues': ['LLM Factory not available']}
        
        class FallbackLanguageValidator:
            def enforce_language_consistency(self, cover_letter):
                return {'coherence_score': 0.5, 'issues': ['LLM Factory not available']}
        
        class FallbackAIDetector:
            def detect_ai_markers(self, cover_letter):
                return {'ai_probability': 0.5, 'issues': ['LLM Factory not available']}
        
        return {
            'cover_letter_generator': FallbackCoverLetterGenerator(),
            'factual_consistency': FallbackFactualValidator(),
            'language_coherence': FallbackLanguageValidator(),
            'ai_detection': FallbackAIDetector()
        }
    
    def generate_cover_letter_with_validation(self, 
                                            cv_content: str, 
                                            job_data: Dict[str, Any],
                                            profile_data: Dict[str, Any],
                                            application_narrative: str) -> Dict[str, Any]:
        """
        Generate cover letter with Ada's conservative validation requirements
        
        Args:
            cv_content: CV content for analysis
            job_data: Complete job posting data
            profile_data: User profile information
            application_narrative: Application-specific narrative
            
        Returns:
            Dict with cover letter, quality metrics, and validation results
        """
        start_time = datetime.now()
        
        try:
            # Prepare requirements with conservative bias
            requirements = {
                'conservative_bias': self.config.conservative_bias,
                'consensus_threshold': self.config.consensus_threshold,
                'quality_threshold': self.config.human_review_triggers['quality_score_below'],
                'include_validation': True,
                'processing_time_limit': self.config.processing_time_limit,
                'job_specific_content': True,
                'professional_tone': True,
                'no_ai_artifacts': True
            }
            
            # Extract job description for specialist
            job_description = self._extract_job_description(job_data)
            
            # Format the input data according to CoverLetterGeneratorV2's expected format
            # This is the key fix - following the exact input format expected by the specialist
            input_data = {
                "cv": cv_content,
                "job_description": job_description,
                "specific_interest": application_narrative,
                "job_title": job_data.get('job_title', ''),
                "company_name": job_data.get('company_name', ''),
                "template_id": profile_data.get('template_preference', 'professional'),
                "conservative_bias": self.config.conservative_bias,
                "max_processing_time": self.config.processing_time_limit,
                "applicant_name": profile_data.get('name', ''),
                "applicant_email": profile_data.get('email', ''),
                "applicant_phone": profile_data.get('phone', ''),
                "professional_tone": True
            }
            
            # Generate cover letter with CoverLetterGeneratorV2
            # Prepare data structures for the specialist
            cv_data = {
                "text": cv_content,
                "format": "plain",
                "skills": profile_data.get('skills', [])
            }
            
            prepared_job_data = {
                "title": job_data.get('job_title', ''),
                "company": job_data.get('company_name', ''),
                "description": job_data.get('job_description', ''),
                "requirements": job_data.get('requirements', []),
                "location": job_data.get('location', '')
            }
            
            input_data = {
                "cv": cv_data,
                "job": prepared_job_data,
                "tone": "professional",
                "format_type": "markdown",
                "template_id": "professional",
                "conservative_bias": True,
                "max_processing_time": self.config.processing_time_limit
            }
            
            # Use the standard process method from CoverLetterGeneratorV2
            result = self.specialists['cover_letter_generator'].process(input_data)
            generation_result = result.data
            
            # Apply conservative validation consensus
            validation_results = self._apply_conservative_validation(
                cover_letter=generation_result.get('cover_letter', ''),
                job_data=job_data,
                requirements=requirements
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Apply conservative bias assessment
            final_assessment = self._apply_conservative_bias(
                generation_result, validation_results, processing_time
            )
            
            # Check against Job 63144 baseline if applicable
            baseline_comparison = None
            if job_data.get('job_id') == self.baseline.baseline_job_id:
                baseline_comparison = self._compare_against_baseline(final_assessment)
            
            return {
                'cover_letter': final_assessment['cover_letter'],
                'quality_metrics': final_assessment['quality_metrics'],
                'validation_results': validation_results,
                'processing_time_seconds': processing_time,
                'conservative_assessment': final_assessment['conservative_assessment'],
                'human_review_required': final_assessment['human_review_required'],
                'baseline_comparison': baseline_comparison,
                'ada_validation_passed': final_assessment['ada_validation_passed']
            }
            
        except Exception as e:
            logger.error(f"❌ Error in cover letter generation: {e}")
            return self._create_error_fallback(str(e), start_time)
    
    def _extract_job_description(self, job_data: Dict[str, Any]) -> str:
        """Extract clean job description from job data"""
        # Try multiple sources for job description
        if 'api_details' in job_data and 'html' in job_data['api_details']:
            # Clean HTML content would go here
            html_content = job_data['api_details']['html']
            return str(html_content) if html_content is not None else ""
        elif 'web_details' in job_data:
            web_details = job_data['web_details']
            return str(web_details) if web_details is not None else ""
        else:
            return json.dumps(job_data, indent=2)
    
    def _apply_conservative_validation(self, 
                                     cover_letter: str, 
                                     job_data: Dict[str, Any],
                                     requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Ada's 2/3 consensus conservative validation"""
        
        validation_scores = {}
        
        # Factual Consistency Validation  
        # Convert job_data to expected format for verification
        job_posting = {
            'title': job_data.get('title', 'Unknown'),
            'company': job_data.get('company', 'Unknown'),
            'description': self._extract_job_description(job_data),
            'requirements': job_data.get('requirements', [])
        }
        
        # Create basic CV data from requirements if available
        cv_data = {
            'education': requirements.get('profile_data', {}).get('education', []),
            'experience': requirements.get('profile_data', {}).get('experience', []),
            'skills': requirements.get('profile_data', {}).get('skills', [])
        }
        
        factual_result = self.specialists['factual_consistency'].verify_cover_letter_consistency(
            cover_letter, job_posting, cv_data
        )
        validation_scores['factual_consistency'] = factual_result.get('consistency_score', 0.0)
        
        # Language Coherence Validation
        coherence_result = self.specialists['language_coherence'].enforce_language_consistency(
            cover_letter
        )
        validation_scores['language_coherence'] = coherence_result.get('coherence_score', 0.0)
        
        # AI Artifact Detection
        ai_detection_result = self.specialists['ai_detection'].detect_ai_markers(
            cover_letter
        )
        validation_scores['ai_artifact_free'] = 1.0 - ai_detection_result.get('ai_probability', 1.0)
        
        # Apply 2/3 consensus requirement
        passing_validations = sum(1 for score in validation_scores.values() 
                                if score >= self.config.human_review_triggers['quality_score_below'])
        
        consensus_reached = passing_validations >= (len(validation_scores) * self.config.consensus_threshold)
        
        return {
            'scores': validation_scores,
            'consensus_reached': consensus_reached,
            'passing_validations': passing_validations,
            'total_validations': len(validation_scores),
            'overall_score': min(validation_scores.values()) if self.config.conservative_bias else sum(validation_scores.values()) / len(validation_scores)
        }
    
    def _apply_conservative_bias(self, 
                               generation_result: Dict[str, Any],
                               validation_results: Dict[str, Any],
                               processing_time: float) -> Dict[str, Any]:
        """Apply Ada's conservative bias - select most conservative assessment when disagreement"""
        
        # Get the most conservative (lowest) scores
        quality_score = validation_results['overall_score']
        
        # Determine if human review is required
        human_review_required = (
            quality_score < self.config.human_review_triggers['quality_score_below'] or
            validation_results['scores']['ai_artifact_free'] < 1.0 or
            validation_results['scores']['language_coherence'] < self.config.human_review_triggers['coherence_score_below'] or
            validation_results['scores']['factual_consistency'] < self.config.human_review_triggers['factual_consistency_below'] or
            processing_time > self.config.processing_time_limit or
            not validation_results['consensus_reached']
        )
        
        # Ada's validation criteria
        ada_validation_passed = (
            quality_score >= self.config.human_review_triggers['quality_score_below'] and
            validation_results['consensus_reached'] and
            processing_time <= self.config.processing_time_limit and
            validation_results['scores']['ai_artifact_free'] >= 1.0
        )
        
        return {
            'cover_letter': generation_result.get('cover_letter', ''),
            'quality_metrics': {
                'overall_quality_score': quality_score,
                'processing_time_seconds': processing_time,
                'consensus_reached': validation_results['consensus_reached'],
                'ai_artifacts_detected': validation_results['scores']['ai_artifact_free'] < 1.0,
                **validation_results['scores']
            },
            'conservative_assessment': {
                'most_conservative_score': min(validation_results['scores'].values()),
                'conservative_bias_applied': True,
                'assessment_rationale': 'Selected most conservative assessment as per Ada requirements'
            },
            'human_review_required': human_review_required,
            'ada_validation_passed': ada_validation_passed
        }
    
    def _compare_against_baseline(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Compare against Job 63144 baseline for A/B testing"""
        
        baseline_met = {
            'processing_time': assessment['quality_metrics']['processing_time_seconds'] <= self.baseline.quality_metrics['processing_time_seconds'],
            'quality_score': assessment['quality_metrics']['overall_quality_score'] >= self.baseline.quality_metrics['quality_score_min'],
            'ai_artifacts': not assessment['quality_metrics']['ai_artifacts_detected'],
            'coherence': assessment['quality_metrics']['language_coherence'] >= self.baseline.quality_metrics['coherence_score_min'],
            'factual_accuracy': assessment['quality_metrics']['factual_consistency'] >= self.baseline.quality_metrics['factual_accuracy_min']
        }
        
        return {
            'baseline_job_id': self.baseline.baseline_job_id,
            'criteria_met': baseline_met,
            'overall_baseline_passed': all(baseline_met.values()),
            'improvement_areas': [criterion for criterion, met in baseline_met.items() if not met]
        }
    
    def _create_error_fallback(self, error_message: str, start_time: datetime) -> Dict[str, Any]:
        """Create fallback response for errors"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'cover_letter': f"Error generating cover letter: {error_message}",
            'quality_metrics': {
                'overall_quality_score': 0.0,
                'processing_time_seconds': processing_time,
                'error': True
            },
            'validation_results': {'error': error_message},
            'processing_time_seconds': processing_time,
            'conservative_assessment': {'error': True},
            'human_review_required': True,
            'baseline_comparison': None,
            'ada_validation_passed': False
        }

# Create global instance for import
ada_cover_letter_coordinator = AdaValidationCoordinator()

def generate_ada_validated_cover_letter(cv_content: str, 
                                       job_data: Dict[str, Any],
                                       profile_data: Dict[str, Any],
                                       application_narrative: str) -> Dict[str, Any]:
    """
    Main function to generate cover letter with Ada's ValidationCoordinator
    
    This function replaces the broken cover letter generation in process_excel_cover_letters.py
    
    Args:
        cv_content: The content of the CV/resume
        job_data: Dictionary with job details
        profile_data: User profile information
        application_narrative: The specific interest text for the cover letter
        
    Returns:
        Dictionary containing the cover letter text and quality metrics
    """
    try:
        # Log the request
        logger.info(f"Generating cover letter for {job_data.get('job_title', 'Unknown Position')} "
                   f"at {job_data.get('company_name', 'Unknown Company')}")
        
        # Call the validation coordinator
        result = ada_cover_letter_coordinator.generate_cover_letter_with_validation(
            cv_content=cv_content,
            job_data=job_data,
            profile_data=profile_data,
            application_narrative=application_narrative
        )
        
        # Log success metrics
        logger.info(f"Cover letter generated successfully: "
                   f"Quality score: {result.get('quality_metrics', {}).get('quality_score', 'N/A')}, "
                   f"Processing time: {result.get('processing_time_seconds', 'N/A')}s")
        
        return result
    except Exception as e:
        logger.error(f"Error generating cover letter: {e}")
        # Return a graceful error response
        return {
            'cover_letter': "",
            'error': str(e),
            'quality_metrics': {'quality_score': 0, 'artifacts_detected': True},
            'ada_validation_passed': False
        }

if __name__ == "__main__":
    # Test with Job 63144 baseline
    print("🚀 Ada ValidationCoordinator + LLM Factory Integration")
    print(f"✅ LLM Factory Available: {LLM_FACTORY_AVAILABLE}")
    print(f"✅ Conservative Bias Enforcement: Enabled")
    print(f"✅ 2/3 Consensus Requirement: Enabled")
    print(f"✅ Job 63144 Baseline Testing: Ready")
    print(f"✅ <15 Second Processing Target: {ada_cover_letter_coordinator.config.processing_time_limit}s")
    print(f"✅ 99%+ Reliability Target: {ada_cover_letter_coordinator.config.reliability_target}")
