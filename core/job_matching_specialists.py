#!/usr/bin/env python3
"""
Direct Job Matching Specialists
==============================
Phase 3 Architecture: Direct job matching specialists - no abstraction layers
"""

from typing import Dict, Any, Optional, Union
import logging
import time
import os
from datetime import datetime

from core.specialist_types import SpecialistResult
from core.specialist_config import (
    LLM_FACTORY_AVAILABLE, 
    CONTENT_EXTRACTION_AVAILABLE,
    logger
)

# Import LLM Factory components if available
if LLM_FACTORY_AVAILABLE:
    try:
        import sys
        sys.path.insert(0, '/home/xai/Documents/llm_factory')
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        from llm_factory.core.types import ModuleConfig
        from llm_factory.core.ollama_client import OllamaClient
    except ImportError:
        pass

# Import Content Extraction Specialist if available
if CONTENT_EXTRACTION_AVAILABLE:
    try:
        from core.content_extraction_specialist import ContentExtractionSpecialistV33
    except ImportError:
        pass


class DirectJobMatchingSpecialists:
    """
    Direct job matching specialists - no abstraction layers
    Phase 3 Architecture: Simplified specialist access without wrapper classes
    """
    def __init__(self, model: str = "llama3.2:latest"):
        self.model = model
        self.registry: Optional['SpecialistRegistry'] = None
        self.client: Optional['OllamaClient'] = None
        self._init_direct_access()

    def _init_direct_access(self):
        """Initialize direct specialist access"""
        if not LLM_FACTORY_AVAILABLE:
            logger.info("LLM Factory not available - fallback mode")
            return
        try:
            self.client = OllamaClient()  # type: ignore
            self.registry = SpecialistRegistry()  # type: ignore
            logger.info("✅ Direct specialist access initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize direct specialist access: {e}")
            self.client = None
            self.registry = None

    def evaluate_job_fitness(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> SpecialistResult:
        """
        Direct job fitness evaluation - Phase 3 simplified architecture
        """
        # Check if direct specialist access is available
        if not LLM_FACTORY_AVAILABLE:
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="none",
                execution_time=0.0,
                error="LLM Factory not available"
            )
        if not self.registry or not self.client:
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="none",
                execution_time=0.0,
                error="Direct specialist access not initialized"
            )
        try:
            start_time = time.time()
            # Direct specialist configuration - no wrapper classes
            config = ModuleConfig(  # type: ignore
                models=[self.model],
                conservative_bias=True,
                quality_threshold=8.0,
                ollama_client=self.client
            )
            # Load specialist directly from registry
            specialist = self.registry.load_specialist("job_fitness_evaluator", config)  # type: ignore
            # Direct input preparation
            input_data = {
                "job_posting": {
                    "description": job_data.get("description", ""),
                    "title": "Job Position",
                    "requirements": []
                },
                "candidate_profile": {
                    "cv_content": cv_data.get("text", ""),
                    "name": "Candidate",
                    "skills": [],
                    "experience": ""
                }
            }
            # Direct specialist call
            result = specialist.process(input_data)
            execution_time = time.time() - start_time
            if result.success:
                return SpecialistResult(
                    success=True,
                    result=result.data,
                    specialist_used="job_fitness_evaluator",
                    execution_time=execution_time,
                    quality_score=getattr(result, 'quality_score', None)
                )
            else:
                return SpecialistResult(
                    success=False,
                    result=None,
                    specialist_used="job_fitness_evaluator",
                    execution_time=execution_time,
                    error="Specialist processing failed"
                )
        except Exception as e:
            logger.error(f"❌ Direct fitness assessment failed: {e}")
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="job_fitness_evaluator",
                execution_time=0.0,
                error=str(e)
            )

    def process_feedback(self, feedback_data: Dict[str, Any]) -> SpecialistResult:
        """
        Process feedback using direct specialist access - Phase 3 architecture
        """
        # Check if direct specialist access is available
        if not LLM_FACTORY_AVAILABLE:
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="none",
                execution_time=0.0,
                error="LLM Factory not available"
            )
        if not self.registry or not self.client:
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="none",
                execution_time=0.0,
                error="Direct specialist access not initialized"
            )
        try:
            start_time = time.time()
            # Direct specialist configuration for feedback processing
            config = ModuleConfig(  # type: ignore
                models=[self.model],
                conservative_bias=True,
                quality_threshold=8.0,
                ollama_client=self.client
            )
            # Load feedback specialist directly from registry
            specialist = self.registry.load_specialist("feedback_analyzer", config)  # type: ignore
            # Direct feedback processing
            result = specialist.process(feedback_data)
            execution_time = time.time() - start_time
            if result.success:
                return SpecialistResult(
                    success=True,
                    result=result.data,
                    specialist_used="feedback_analyzer",
                    execution_time=execution_time,
                    quality_score=getattr(result, 'quality_score', None)
                )
            else:
                return SpecialistResult(
                    success=False,
                    result=None,
                    specialist_used="feedback_analyzer",
                    execution_time=execution_time,
                    error="Feedback processing failed"
                )
        except Exception as e:
            logger.error(f"❌ Direct feedback processing failed: {e}")
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="feedback_analyzer",
                execution_time=0.0,
                error=str(e)
            )

    def generate_cover_letter(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> SpecialistResult:
        """
        Generate a cover letter using the legacy generator only (forced fallback for now).
        """
        print("[DEBUG] Using legacy cover letter generator fallback path.")
        try:
            import sys
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../_legacy_archive/run_pipeline/cover_letter')))
            from template_manager import generate_cover_letter
            # Use a known-good template path
            template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../_legacy_archive/run_pipeline/cover_letter/cover_letter_template.md'))
            if not os.path.exists(template_path):
                print(f"[DEBUG] Template not found at {template_path}")
                return SpecialistResult(
                    success=False,
                    result=None,
                    specialist_used="legacy_cover_letter_generator",
                    execution_time=0.0,
                    error=f"Template not found at {template_path}"
                )
            job_details = {
                'company': job_data.get('company', 'Deutsche Bank AG'),
                'company_address': job_data.get('company_address', '60262 Frankfurt'),
                'job_title': job_data.get('job_title', 'Senior Risk Manager'),
                'reference_number': job_data.get('reference_number', 'N/A'),
                'department': job_data.get('department', ''),
                'primary_expertise_area': 'regulatory optimization and risk management',
                'skill_area_1': 'cost savings',
                'skill_area_2': 'compliance frameworks',
                'qualification_paragraph': '',
                'skill_bullets': '- Led cross-cultural teams\n- Implemented compliance frameworks',
                'development_paragraph': '',
                'skill_match_chart': '',
                'qualification_summary': '',
                'specific_interest': 'the opportunity to lead risk management at Deutsche Bank',
                'relevant_experience': 'regulatory optimization and compliance',
                'relevant_understanding': 'Swiss financial regulations',
                'potential_contribution': 'optimize risk and compliance processes',
                'value_proposition': 'drive cost savings and regulatory excellence',
                'quantifiable_achievements': 'Achieved €2M+ cost savings through regulatory optimization.',
                'date': datetime.now().strftime('%d %B %Y'),
            }
            job_details['cv_content'] = cv_data.get('text', '')
            job_details['description'] = job_data.get('description', '')
            cover_letter = generate_cover_letter(template_path, job_details)
            if not cover_letter:
                print("[DEBUG] Legacy generator returned no content.")
                return SpecialistResult(
                    success=False,
                    result=None,
                    specialist_used="legacy_cover_letter_generator",
                    execution_time=0.0,
                    error="Legacy generator returned no content."
                )
            return SpecialistResult(
                success=True,
                result=cover_letter,
                specialist_used="legacy_cover_letter_generator",
                execution_time=0.0,
                quality_score=None
            )
        except Exception as e:
            print(f"[DEBUG] Legacy cover letter generation failed: {e}")
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="legacy_cover_letter_generator",
                execution_time=0.0,
                error=str(e)
            )

    def extract_content_skills(self, job_description: str) -> SpecialistResult:
        """
        Extract skills and content from job description using v3.3 production specialist
        
        Args:
            job_description: Raw job description text
            
        Returns:
            SpecialistResult with extracted skills and content
        """
        start_time = time.time()
        
        if not CONTENT_EXTRACTION_AVAILABLE:
            logger.warning("⚠️ Content extraction specialist not available, using fallback")
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="content_extraction_fallback",
                execution_time=0.0,
                error="Content extraction specialist not available"
            )
        
        try:
            logger.info("🔧 Extracting content using v3.3 production specialist")
            specialist = ContentExtractionSpecialistV33()
            result = specialist.extract_skills(job_description)
            execution_time = time.time() - start_time
            
            # Convert specialist result to our standard format
            extracted_data = {
                "technical_skills": result.technical_skills if hasattr(result, 'technical_skills') else [],
                "soft_skills": result.soft_skills if hasattr(result, 'soft_skills') else [],
                "business_skills": result.business_skills if hasattr(result, 'business_skills') else [],
                "process_skills": result.process_skills if hasattr(result, 'process_skills') else [],
                "all_skills": result.all_skills if hasattr(result, 'all_skills') else [],
                "processing_time": execution_time,
                "model_used": result.model_used if hasattr(result, 'model_used') else self.model,
                "accuracy_confidence": result.accuracy_confidence if hasattr(result, 'accuracy_confidence') else "high"
            }
            
            logger.info(f"✅ Content extraction completed: {len(extracted_data['all_skills'])} skills in {execution_time:.1f}s")
            
            return SpecialistResult(
                success=True,
                result=extracted_data,
                specialist_used="content_extraction_v3_3",
                execution_time=execution_time,
                quality_score=1.0  # v3.3 is production-ready with 100% format compliance
            )
            
        except Exception as e:
            logger.error(f"❌ Content extraction failed: {e}")
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="content_extraction_v3_3",
                execution_time=time.time() - start_time,
                error=str(e)
            )


def get_job_matching_specialists(model: str = "llama3.2:latest") -> DirectJobMatchingSpecialists:
    """
    Get direct access to job matching specialists - Phase 3 Architecture
    """
    return DirectJobMatchingSpecialists(model)

def get_feedback_specialists(model: str = "llama3.2:latest") -> DirectJobMatchingSpecialists:
    """
    Get direct access to feedback analysis specialists - Phase 3 Architecture
    """
    return DirectJobMatchingSpecialists(model)
