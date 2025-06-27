#!/usr/bin/env python3
"""
Individual Specialist Evaluators
===============================
Handlers for specific specialist types with LLM Factory integration.
"""

from typing import Dict, Any, List
import logging
import time

from core.specialist_types import SpecialistResult
from core.specialist_config import LLM_FACTORY_AVAILABLE, logger

class SpecialistEvaluator:
    """Handler for individual specialist evaluations"""
    
    def __init__(self, model: str = "llama3.2:latest"):
        self.model = model
    
    def evaluate_job_fitness(self, input_data: Dict[str, Any]) -> SpecialistResult:
        """Evaluate job fitness using specialist"""
        start_time = time.time()
        if not LLM_FACTORY_AVAILABLE:
            return SpecialistResult(
                success=False,
                result="Specialist access unavailable",
                specialist_used="job_fitness_evaluator",
                execution_time=time.time() - start_time,
                error="LLM Factory not available"
            )
        
        try:
            from core.job_matching_specialists import DirectJobMatchingSpecialists
            specialist = DirectJobMatchingSpecialists(self.model)
            cv_data = {"text": input_data.get("candidate_profile", "")}
            job_data = {"description": input_data.get("job_requirements", "")}
            result = specialist.evaluate_job_fitness(cv_data, job_data)
            return SpecialistResult(
                success=result.success if hasattr(result, 'success') else True,
                result=result,
                specialist_used="job_fitness_evaluator",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return SpecialistResult(
                success=False,
                result=f"Evaluation failed: {str(e)}",
                specialist_used="job_fitness_evaluator",
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    def evaluate_domain_classification(self, input_data: Dict[str, Any]) -> SpecialistResult:
        """Evaluate domain classification using specialist"""
        start_time = time.time()
        if not LLM_FACTORY_AVAILABLE:
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="domain_classification",
                execution_time=time.time() - start_time,
                error="LLM Factory not available"
            )
        
        try:
            from llm_factory.modules.quality_validation.specialists_versioned.domain_classification.v1_1.src.domain_classification_specialist_llm import classify_job_domain_llm
            
            job_metadata = input_data.get("job_metadata", {})
            job_description = input_data.get("job_description", "")
            
            result = classify_job_domain_llm(job_metadata, job_description)
            
            return SpecialistResult(
                success=True,
                result=result,
                specialist_used="domain_classification",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"❌ Domain classification failed: {e}")
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="domain_classification",
                execution_time=time.time() - start_time,
                error=f"Domain classification error: {str(e)}"
            )
    
    def evaluate_location_validation(self, input_data: Dict[str, Any]) -> SpecialistResult:
        """Evaluate location validation using specialist"""
        start_time = time.time()
        if not LLM_FACTORY_AVAILABLE:
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="location_validation",
                execution_time=time.time() - start_time,
                error="LLM Factory not available"
            )
        
        try:
            from llm_factory.modules.quality_validation.specialists_versioned.location_validation.v1_0.src.location_validation_specialist import validate_locations
            
            job_metadata = input_data.get("job_metadata", {})
            job_description = input_data.get("job_description", "")
            
            # Fix location format - specialist expects string, job data has dict
            if "location" in job_metadata and isinstance(job_metadata["location"], dict):
                location_dict = job_metadata["location"]
                # Convert dict to string format: "City, Country" or just "City"
                location_parts = []
                if location_dict.get("city"):
                    location_parts.append(location_dict["city"])
                if location_dict.get("country"):
                    location_parts.append(location_dict["country"])
                location_string = ", ".join(location_parts) if location_parts else "Unknown"
                
                # Create a copy with fixed location format
                job_metadata_fixed = job_metadata.copy()
                job_metadata_fixed["location"] = location_string
            else:
                job_metadata_fixed = job_metadata
            
            result = validate_locations(job_metadata_fixed, job_description)
            
            return SpecialistResult(
                success=True,
                result=result,
                specialist_used="location_validation",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"❌ Location validation failed: {e}")
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="location_validation",
                execution_time=time.time() - start_time,
                error=f"Location validation error: {str(e)}"
            )
    
    def evaluate_mock_specialist(self, specialist_name: str, input_data: Dict[str, Any]) -> SpecialistResult:
        """Mock evaluation for testing purposes"""
        start_time = time.time()
        return SpecialistResult(
            success=True,
            result=f"Mock evaluation result for {specialist_name}",
            specialist_used=specialist_name,
            execution_time=time.time() - start_time
        )
    
    def get_available_specialists(self) -> List[str]:
        """List all available specialists"""
        if not LLM_FACTORY_AVAILABLE:
            return []
        try:
            return [
                "job_fitness_evaluator",
                "domain_classification",
                "location_validation",
                "text_summarization",
                "adversarial_prompt_generator",
                "consensus_engine",
                "document_analysis",
                "feedback_processor"
            ]
        except Exception as e:
            logger.error(f"❌ Failed to list specialists: {e}")
            return []
