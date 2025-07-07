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

    def process_job_file(self, job_file_path: str) -> SpecialistResult:
        """
        Process a single job file using the appropriate specialists
        
        Args:
            job_file_path: Path to the job file (JSON format)
            
        Returns:
            SpecialistResult with the processing outcome
        """
        try:
            import json
            with open(job_file_path, 'r') as f:
                job_data = json.load(f)
            
            # Extract job ID from file name (assuming format like job_123.json)
            job_id = os.path.splitext(os.path.basename(job_file_path))[0]
            job_data['job_id'] = job_id
            
            logger.info(f"📂 Processing job file: {job_file_path}")
            
            # Step 1: Extract skills and content from job description
            extraction_result = self.extract_content_skills(job_data.get('description', ''))
            if not extraction_result.success:
                return extraction_result
            
            # Enrich job data with extracted skills
            job_data['extracted_skills'] = extraction_result.result.get('all_skills', [])
            
            # Step 2: Evaluate job fitness for a sample CV (using a dummy CV for now)
            dummy_cv = {
                "text": "Experienced professional with a strong background in risk management and compliance.",
                "skills": ["risk management", "compliance"],
                "experience": "5 years in financial services"
            }
            fitness_result = self.evaluate_job_fitness(dummy_cv, job_data)
            job_data['fitness_evaluation'] = fitness_result.result
            
            # Step 3: Generate a cover letter (using legacy generator for now)
            cover_letter_result = self.generate_cover_letter(dummy_cv, job_data)
            job_data['cover_letter'] = cover_letter_result.result
            
            return SpecialistResult(
                success=True,
                result=job_data,
                specialist_used="job_file_processor",
                execution_time=0.0,
                quality_score=None
            )
        except Exception as e:
            logger.error(f"❌ Error processing job file {job_file_path}: {e}")
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="job_file_processor",
                execution_time=0.0,
                error=str(e)
            )

    def process_job(self, job_data: Dict[str, Any]) -> SpecialistResult:
        """
        Process a single job entry (dictionary) using the appropriate specialists
        
        Args:
            job_data: Job data as a dictionary
            
        Returns:
            SpecialistResult with the processing outcome
        """
        try:
            # Step 1: Extract skills and content from job description
            extraction_result = self.extract_content_skills(job_data.get('description', ''))
            if not extraction_result.success:
                return extraction_result
            
            # Enrich job data with extracted skills
            job_data['extracted_skills'] = extraction_result.result.get('all_skills', [])
            
            # Step 2: Evaluate job fitness for a sample CV (using a dummy CV for now)
            dummy_cv = {
                "text": "Experienced professional with a strong background in risk management and compliance.",
                "skills": ["risk management", "compliance"],
                "experience": "5 years in financial services"
            }
            fitness_result = self.evaluate_job_fitness(dummy_cv, job_data)
            job_data['fitness_evaluation'] = fitness_result.result
            
            # Step 3: Generate a cover letter (using legacy generator for now)
            cover_letter_result = self.generate_cover_letter(dummy_cv, job_data)
            job_data['cover_letter'] = cover_letter_result.result
            
            return SpecialistResult(
                success=True,
                result=job_data,
                specialist_used="job_processor",
                execution_time=0.0,
                quality_score=None
            )
        except Exception as e:
            logger.error(f"❌ Error processing job data {job_data.get('job_id')}: {e}")
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="job_processor",
                execution_time=0.0,
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

def process_jobs_with_specialists(jobs=None, model="llama3.2:latest"):
    """Process jobs with LLM specialists"""
    specialist = DirectJobMatchingSpecialists(model=model)
    results = []
    
    if jobs is None:
        # Process jobs from data/postings directory
        postings_dir = os.path.join("data", "postings")
        if not os.path.exists(postings_dir):
            logger.warning("⚠️ No jobs found in data/postings")
            return results
            
        for job_file in os.listdir(postings_dir):
            if job_file.endswith(".json"):
                job_path = os.path.join(postings_dir, job_file)
                result = specialist.process_job_file(job_path)
                results.append(result)
    else:
        # Process provided jobs
        for job in jobs:
            result = specialist.process_job(job)
            results.append(result)
    
    logger.info(f"✅ Processed {len(results)} jobs with specialists")
    return results
