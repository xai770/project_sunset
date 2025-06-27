#!/usr/bin/env python3
"""
Ada ValidationCoordinator + LLM Factory Integration Module

This module integrates Ada's ValidationCoordinator with the LLM Factory specialists
for high-quality cover letter generation without AI artifacts.

Key Features:
- Professional cover letters with zero AI artifacts
- Multi-model consensus for reliability
- Conservative bias enforcement with 2/3 threshold
- <15 second processing time with comprehensive fallbacks
"""

import sys
import os
import logging
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='run_pipeline/ada_integration.log'
)
logger = logging.getLogger("ada_llm_factory_integration")

# Add LLM Factory to path
LLM_FACTORY_PATH = '/home/xai/Documents/llm_factory'
if LLM_FACTORY_PATH not in sys.path:
    sys.path.insert(0, LLM_FACTORY_PATH)
    logger.info(f"Added LLM Factory to path: {LLM_FACTORY_PATH}")

# Import LLM Factory components
# Tell mypy and Pylance to ignore missing imports for the llm_factory module
# mypy: ignore-missing-imports
# type: ignore[import]
# pyright: reportMissingImports=false
try:
    # These imports don't have type stubs
    from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry  # type: ignore
    from llm_factory.core.types import ModuleConfig  # type: ignore
    from llm_factory.core.ollama_client import OllamaClient  # type: ignore
    
    # Import successful
    LLM_FACTORY_AVAILABLE = True
    logger.info("✅ Successfully imported LLM Factory components")
except ImportError as e:
    logger.error(f"❌ Failed to import LLM Factory: {e}")
    LLM_FACTORY_AVAILABLE = False

# Ada's ValidationCoordinator configuration
class AdaValidationConfig:
    """Configuration for Ada's ValidationCoordinator with conservative bias"""
    
    def __init__(self):
        self.conservative_bias = True
        self.consensus_threshold = 2/3  # 2 out of 3 specialists must agree
        self.processing_time_limit = 15  # seconds
        self.detail_level = "high"
        self.safety_checks = True
        self.artifact_detection = True
        self.quality_threshold = 0.85
        self.reliability_target = 0.99

class AdaValidationCoordinator:
    """
    Ada's ValidationCoordinator integrated with LLM Factory specialists.
    
    Orchestrates quality validation with multiple specialists and applies
    Ada's conservative bias requirements.
    """
    
    def __init__(self):
        self.config = AdaValidationConfig()
        self.registry = None
        self.specialists = {}
        self.ollama_client = None
        self.initialize_specialists()
    
    def initialize_specialists(self):
        """Initialize the LLM Factory specialists"""
        global LLM_FACTORY_AVAILABLE
        if not LLM_FACTORY_AVAILABLE:
            logger.warning("⚠️ LLM Factory not available - using fallbacks")
            return
        
        try:
            # Create the registry
            self.registry = SpecialistRegistry()
            
            # Create the Ollama client
            self.ollama_client = OllamaClient()
            
            # Create base config with correct parameters
            base_config = ModuleConfig(
                ollama_client=self.ollama_client,
                quality_threshold=8.0,
                models=["llama3", "phi3", "olmo2"],
                conservative_bias=True
            )
            
            # Load specialists
            self.specialists["cover_letter_generator"] = self.registry.load_specialist(
                "cover_letter_generator", base_config, "v2_0"
            )
            
            self.specialists["ai_language_detection"] = self.registry.load_specialist(
                "ai_language_detection", base_config
            )
            
            self.specialists["language_coherence"] = self.registry.load_specialist(
                "language_coherence", base_config
            )
            
            self.specialists["factual_consistency"] = self.registry.load_specialist(
                "factual_consistency", base_config
            )
            
            logger.info("✅ Successfully loaded all specialists")
            
        except Exception as e:
            logger.error(f"❌ Error initializing specialists: {e}")
            LLM_FACTORY_AVAILABLE = False
    
    def generate_cover_letter_with_validation(self,
                                            cv_content: str,
                                            job_data: Dict[str, Any],
                                            profile_data: Dict[str, Any],
                                            application_narrative: str) -> Dict[str, Any]:
        """
        Generate a cover letter with validation using LLM Factory specialists
        
        Args:
            cv_content: The content of the CV
            job_data: Job details dictionary
            profile_data: User profile information
            application_narrative: The specific interest text
            
        Returns:
            Dictionary with cover letter and validation results
        """
        start_time = datetime.now()
        
        if not LLM_FACTORY_AVAILABLE or not self.specialists:
            return self._create_fallback_response("LLM Factory specialists not available", start_time)
        
        try:
            # Extract job description
            job_description = job_data.get("job_description", "")
            if not job_description:
                job_description = job_data.get("description", "")
            if not job_description and "api_details" in job_data:
                job_description = job_data["api_details"].get("description", "")
            
            # Prepare input data for the cover letter generator
            input_data = {
                "cv": cv_content,
                "job_description": job_description,
                "specific_interest": application_narrative,
                "template_id": profile_data.get("template_preference", "professional"),
                "job_title": job_data.get("job_title", ""),
                "company_name": job_data.get("company_name", ""),
                "skills_match": {},  # Optional skills matching data
                "conservative_bias": self.config.conservative_bias,
                "max_processing_time": self.config.processing_time_limit,
            }
            
            # Generate the cover letter
            cover_letter_result = self.specialists["cover_letter_generator"].process(input_data)
            
            if not cover_letter_result.success:
                return self._create_fallback_response(
                    f"Cover letter generation failed: {cover_letter_result.validation}", 
                    start_time
                )
            
            cover_letter_text = cover_letter_result.data.get("cover_letter", "")
            
            # Perform validation with specialists
            validation_results = self._validate_cover_letter(
                cover_letter_text, job_description, cv_content, input_data
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Apply Ada's conservative bias assessment
            assessment = self._apply_conservative_assessment(
                validation_results, cover_letter_text, processing_time
            )
            
            return {
                'cover_letter': cover_letter_text,
                'quality_metrics': assessment['quality_metrics'],
                'validation_results': validation_results,
                'processing_time_seconds': processing_time,
                'conservative_assessment': assessment['conservative_assessment'],
                'human_review_required': assessment['human_review_required'],
                'ada_validation_passed': assessment['ada_validation_passed']
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating cover letter: {e}")
            return self._create_fallback_response(str(e), start_time)
    
    def _validate_cover_letter(self, 
                             cover_letter: str, 
                             job_description: str, 
                             cv_content: str,
                             original_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the cover letter with multiple specialists
        
        Args:
            cover_letter: The generated cover letter text
            job_description: The job description
            cv_content: The CV content
            original_input: The original input data used for generation
            
        Returns:
            Dictionary with validation results from each specialist
        """
        validation_results = {}
        
        # Skip validation if specialists aren't available
        if not self.specialists:
            return {"validation_skipped": True}
        
        # AI Language Detection validation
        try:
            ai_detection_input = {"text": cover_letter}
            ai_detection_result = self.specialists["ai_language_detection"].process(ai_detection_input)
            validation_results["ai_detection"] = {
                "ai_probability": ai_detection_result.data.get("ai_probability", 1.0),
                "human_probability": ai_detection_result.data.get("human_probability", 0.0),
                "artifacts_detected": ai_detection_result.data.get("artifacts_detected", [])
            }
        except Exception as e:
            logger.error(f"AI detection validation failed: {e}")
            validation_results["ai_detection"] = {"error": str(e)}
        
        # Language Coherence validation
        try:
            coherence_input = {"text": cover_letter, "check_professional_tone": True}
            coherence_result = self.specialists["language_coherence"].process(coherence_input)
            validation_results["language_coherence"] = {
                "coherence_score": coherence_result.data.get("coherence_score", 0.0),
                "professional_tone_score": coherence_result.data.get("professional_tone_score", 0.0),
                "issues": coherence_result.data.get("issues", [])
            }
        except Exception as e:
            logger.error(f"Language coherence validation failed: {e}")
            validation_results["language_coherence"] = {"error": str(e)}
        
        # Factual Consistency validation
        try:
            factual_input = {
                "text": cover_letter,
                "reference1": job_description,
                "reference2": cv_content,
                "check_type": "cover_letter"
            }
            factual_result = self.specialists["factual_consistency"].process(factual_input)
            validation_results["factual_consistency"] = {
                "consistency_score": factual_result.data.get("consistency_score", 0.0),
                "accuracy_score": factual_result.data.get("accuracy_score", 0.0),
                "issues": factual_result.data.get("issues", [])
            }
        except Exception as e:
            logger.error(f"Factual consistency validation failed: {e}")
            validation_results["factual_consistency"] = {"error": str(e)}
        
        return validation_results
    
    def _apply_conservative_assessment(self,
                                     validation_results: Dict[str, Any],
                                     cover_letter: str,
                                     processing_time: float) -> Dict[str, Any]:
        """
        Apply Ada's conservative bias to validation results
        
        Args:
            validation_results: Results from specialist validations
            cover_letter: The generated cover letter text
            processing_time: Time taken to generate the cover letter
            
        Returns:
            Dictionary with conservative assessment and quality metrics
        """
        # Extract scores (using conservative defaults for errors)
        ai_prob = validation_results.get("ai_detection", {}).get("ai_probability", 1.0)
        coherence_score = validation_results.get("language_coherence", {}).get("coherence_score", 0.0)
        professional_score = validation_results.get("language_coherence", {}).get("professional_tone_score", 0.0)
        consistency_score = validation_results.get("factual_consistency", {}).get("consistency_score", 0.0)
        accuracy_score = validation_results.get("factual_consistency", {}).get("accuracy_score", 0.0)
        
        # Human content probability (inverse of AI probability)
        human_prob = 1.0 - ai_prob
        
        # Get all scores for conservative assessment
        scores = [
            human_prob,
            coherence_score,
            professional_score,
            consistency_score,
            accuracy_score
        ]
        
        # Filter out any None or negative values
        valid_scores = [s for s in scores if s is not None and s >= 0]
        
        # Apply conservative bias (take the minimum score)
        conservative_score = min(valid_scores) if valid_scores else 0.0
        
        # Calculate overall quality with weighted average
        weights = {
            "human_probability": 0.3,
            "coherence": 0.2,
            "professional_tone": 0.15,
            "consistency": 0.2,
            "accuracy": 0.15
        }
        
        quality_components = {
            "human_probability": human_prob,
            "coherence": coherence_score,
            "professional_tone": professional_score,
            "consistency": consistency_score,
            "accuracy": accuracy_score
        }
        
        # Calculate weighted quality score
        weighted_sum = sum(score * weights[name] for name, score in quality_components.items())
        
        # Calculate passing specialists (using Ada's threshold)
        threshold = self.config.quality_threshold
        passing_specialists = sum(1 for score in valid_scores if score >= threshold)
        
        # Apply 2/3 consensus requirement
        consensus_reached = passing_specialists >= len(valid_scores) * self.config.consensus_threshold
        
        # Determine if human review is required
        human_review_required = (
            conservative_score < threshold or
            not consensus_reached or
            processing_time > self.config.processing_time_limit or
            ai_prob > 0.1  # Conservative bias: Any AI probability > 10% triggers review
        )
        
        # Determine if Ada validation passed
        ada_validation_passed = (
            conservative_score >= threshold and
            consensus_reached and
            processing_time <= self.config.processing_time_limit and
            ai_prob <= 0.1
        )
        
        # Compile quality metrics
        quality_metrics = {
            "conservative_score": conservative_score,
            "weighted_quality_score": weighted_sum,
            "human_probability": human_prob,
            "ai_probability": ai_prob,
            "coherence_score": coherence_score,
            "professional_tone_score": professional_score,
            "factual_consistency_score": consistency_score,
            "factual_accuracy_score": accuracy_score,
            "processing_time_seconds": processing_time,
            "consensus_reached": consensus_reached,
            "passing_specialists": passing_specialists,
            "total_specialists": len(valid_scores)
        }
        
        # Compile conservative assessment
        conservative_assessment = {
            "most_conservative_score": conservative_score,
            "conservative_bias_applied": True,
            "assessment_rationale": "Selected most conservative assessment as per Ada requirements",
            "review_triggers": {
                "low_quality_score": conservative_score < threshold,
                "consensus_not_reached": not consensus_reached,
                "processing_time_exceeded": processing_time > self.config.processing_time_limit,
                "ai_artifacts_detected": ai_prob > 0.1,
            }
        }
        
        return {
            "quality_metrics": quality_metrics,
            "conservative_assessment": conservative_assessment,
            "human_review_required": human_review_required,
            "ada_validation_passed": ada_validation_passed
        }
    
    def _create_fallback_response(self, error_message: str, start_time: datetime) -> Dict[str, Any]:
        """Create a fallback response when errors occur"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "cover_letter": f"[ERROR: {error_message}]",
            "quality_metrics": {
                "error": error_message,
                "processing_time_seconds": processing_time
            },
            "validation_results": {
                "error": error_message
            },
            "processing_time_seconds": processing_time,
            "conservative_assessment": {
                "error": error_message
            },
            "human_review_required": True,
            "ada_validation_passed": False
        }

# Create global instance for importing
ada_cover_letter_coordinator = AdaValidationCoordinator()

def generate_ada_validated_cover_letter(cv_content: str, 
                                      job_data: Dict[str, Any],
                                      profile_data: Dict[str, Any],
                                      application_narrative: str) -> Dict[str, Any]:
    """
    Generate a cover letter with Ada's validation
    
    Args:
        cv_content: The content of the CV
        job_data: Job details dictionary
        profile_data: User profile information
        application_narrative: The specific interest text
        
    Returns:
        Dictionary with cover letter and validation results
    """
    try:
        # Log the request
        logger.info(f"Generating cover letter for {job_data.get('job_title', 'Unknown Position')} "
                  f"at {job_data.get('company_name', 'Unknown Company')}")
        
        # Generate with validation
        result = ada_cover_letter_coordinator.generate_cover_letter_with_validation(
            cv_content=cv_content,
            job_data=job_data,
            profile_data=profile_data,
            application_narrative=application_narrative
        )
        
        # Log results
        quality_score = result.get("quality_metrics", {}).get("conservative_score", 0.0)
        processing_time = result.get("processing_time_seconds", 0.0)
        passed = result.get("ada_validation_passed", False)
        
        logger.info(f"Cover letter generation {'passed' if passed else 'failed'} Ada validation. "
                  f"Quality score: {quality_score:.2f}, Processing time: {processing_time:.2f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_ada_validated_cover_letter: {e}")
        return {
            "cover_letter": "",
            "error": str(e),
            "quality_metrics": {"error": str(e)},
            "ada_validation_passed": False
        }

# Test the module when run directly
if __name__ == "__main__":
    print("🚀 Ada ValidationCoordinator + LLM Factory Integration")
    print(f"✅ LLM Factory Available: {LLM_FACTORY_AVAILABLE}")
    print(f"✅ Conservative Bias: {ada_cover_letter_coordinator.config.conservative_bias}")
    print(f"✅ Consensus Threshold: {ada_cover_letter_coordinator.config.consensus_threshold}")
    print(f"✅ Processing Time Limit: {ada_cover_letter_coordinator.config.processing_time_limit}s")
    print(f"✅ Quality Threshold: {ada_cover_letter_coordinator.config.quality_threshold}")
    print(f"✅ Reliability Target: {ada_cover_letter_coordinator.config.reliability_target}")
