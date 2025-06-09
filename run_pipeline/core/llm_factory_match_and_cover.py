"""
LLM Factory-based replacement for phi3_match_and_cover.py

This module replaces the basic phi3 implementation with professional LLM Factory specialists
that provide quality-controlled job matching and cover letter generation.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add LLM Factory to Python path
LLM_FACTORY_PATH = "/home/xai/Documents/llm_factory"
if LLM_FACTORY_PATH not in sys.path:
    sys.path.insert(0, LLM_FACTORY_PATH)

from llm_factory.core.ollama_client import OllamaClient  # type: ignore
from llm_factory.core.types import ModuleConfig  # type: ignore
from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry  # type: ignore

logger = logging.getLogger("llm_factory_match_and_cover")

class LLMFactoryJobMatcher:
    """
    Professional job matching and cover letter generation using LLM Factory specialists.
    
    Provides quality-controlled alternatives to the basic phi3 implementation with:
    - Adversarial verification for reliability
    - Consensus-based assessments
    - Structured output with confidence scores
    - Professional cover letter generation
    """
    
    def __init__(self, model="llama3.2:latest"):
        """Initialize the LLM Factory job matcher."""
        self.client = None
        self.model = model
        self.registry = None
        self._setup_client()
        
    def _setup_client(self):
        """Set up the Ollama client and specialist registry."""
        try:
            self.client = OllamaClient()
            # Test connection
            models = self.client.available_models()
            logger.info(f"✅ LLM Factory connected - {len(models)} models available")
            
            # Verify model availability
            available_model_names = []
            for model in models:
                if isinstance(model, dict) and 'name' in model:
                    available_model_names.append(model['name'])  # type: ignore
                else:
                    available_model_names.append(str(model))
            
            if self.model not in available_model_names:
                if models:
                    fallback_model = available_model_names[0]
                    logger.warning(f"⚠️ {self.model} not found, using: {fallback_model}")
                    self.model = fallback_model
                else:
                    raise Exception("No models available in Ollama")
            
            self.registry = SpecialistRegistry()
            logger.info("✅ LLM Factory specialists ready")
            
        except Exception as e:
            logger.error(f"❌ LLM Factory setup failed: {e}")
            self.client = None
            self.registry = None
    
    def _get_base_config(self):
        """Get base configuration for specialists."""
        return ModuleConfig(
            models=[self.model],
            conservative_bias=True,
            quality_threshold=8.0,
            ollama_client=self.client
        )
    
    def get_job_fitness_assessment(self, cv: str, job_description: str) -> dict:
        """
        Get comprehensive job fitness assessment using LLM Factory specialist.
        
        Returns detailed assessment with match percentage, confidence, and analysis.
        """
        if not self.client or not self.registry:
            logger.error("LLM Factory not properly initialized, falling back to basic method")
            return self._fallback_assessment(cv, job_description)
        
        try:
            # Prepare input data for job fitness evaluator
            input_data = {
                "job_posting": {
                    "description": job_description,
                    "title": "Job Position",  # Could be extracted from job_description
                    "requirements": []  # Could be parsed from job_description
                },
                "candidate_profile": {
                    "cv_content": cv,
                    "name": "Candidate",  # Generic for privacy
                    "skills": [],  # Could be extracted from CV
                    "experience": ""  # Could be extracted from CV
                }
            }
            
            # Load and run job fitness evaluator specialist
            config = self._get_base_config()
            specialist = self.registry.load_specialist("job_fitness_evaluator", config)
            
            logger.info("🤖 Processing job fitness with LLM Factory specialist...")
            result = specialist.process(input_data)
            
            if result.success:
                # Extract match percentage from overall score (convert 0-10 scale to 0-100)
                overall_score = result.data.get('overall_score', 5.0)
                match_percentage = int(overall_score * 10)  # Convert to percentage
                
                # Extract additional insights
                fitness_data = {
                    'match_percentage': match_percentage,
                    'confidence': result.data.get('confidence', 'Medium'),
                    'fitness_rating': result.data.get('fitness_rating', 'Unknown'),
                    'recommendation': result.data.get('recommendation', 'Review Required'),
                    'success_probability': result.data.get('success_probability', 0.5),
                    'strengths': result.data.get('strengths', []),
                    'weaknesses': result.data.get('weaknesses', []),
                    'risk_factors': result.data.get('risk_factors', []),
                    'key_insights': result.data.get('key_insights', []),
                    'processing_time': result.processing_time,
                    'assessment_method': result.data.get('assessment_method', 'llm_factory')
                }
                
                logger.info(f"✅ Job fitness assessment complete: {match_percentage}% match")
                return fitness_data
            else:
                logger.error("❌ Job fitness specialist failed")
                return self._fallback_assessment(cv, job_description)
                
        except Exception as e:
            logger.error(f"❌ Job fitness assessment error: {e}")
            return self._fallback_assessment(cv, job_description)
    
    def generate_cover_letter(self, cv: str, job_description: str, job_fitness_data: Optional[dict] = None) -> dict:
        """
        Generate professional cover letter using LLM Factory specialist.
        
        Returns cover letter with quality metrics and validation.
        """
        if not self.client or not self.registry:
            logger.error("LLM Factory not properly initialized")
            return {"cover_letter": "Error: Unable to generate cover letter.", "quality": "Failed"}
        
        try:
            # Extract job title and company from job description (basic extraction)
            job_title = "Position"
            company_name = "Company"
            
            # Simple extraction attempts
            lines = job_description.split('\n')
            for line in lines[:3]:  # Check first 3 lines for title
                if any(word in line.lower() for word in ['developer', 'engineer', 'manager', 'analyst', 'specialist']):
                    job_title = line.strip()
                    break
            
            # Extract candidate name from CV if possible
            candidate_name = "Applicant"
            cv_lines = cv.split('\n')
            if cv_lines and len(cv_lines[0].strip()) < 50:  # First line might be name
                candidate_name = cv_lines[0].strip()
            
            # Prepare input data for cover letter generator (matching demo format)
            input_data = {
                "job_data": {
                    "title": job_title,
                    "company": company_name,
                    "description": job_description,
                    "requirements": []  # Could extract requirements from job description
                },
                "cv_data": {
                    "name": candidate_name,
                    "experience": cv,  # Full CV as experience
                    "skills": job_fitness_data.get("strengths", []) if job_fitness_data else [],
                    "achievements": []  # Could extract from CV
                }
            }
            
            # Load and run cover letter generator specialist
            config = self._get_base_config()
            specialist = self.registry.load_specialist("cover_letter_generator", config)
            
            logger.info("📝 Generating cover letter with LLM Factory specialist...")
            result = specialist.process(input_data)
            
            if result.success:
                cover_letter_data = {
                    'cover_letter': result.data.get('cover_letter', ''),
                    'format': result.data.get('format', 'text'),
                    'tone': result.data.get('tone', 'professional'),
                    'quality_validation': result.data.get('quality_validation', {}),
                    'processing_time': result.processing_time,
                    'generation_method': 'llm_factory'
                }
                
                logger.info("✅ Cover letter generation complete")
                return cover_letter_data
            else:
                logger.error("❌ Cover letter specialist failed")
                return {"cover_letter": "Error: Unable to generate professional cover letter.", "quality": "Failed"}
                
        except Exception as e:
            logger.error(f"❌ Cover letter generation error: {e}")
            return {"cover_letter": "Error: Cover letter generation failed.", "quality": "Failed"}
    
    def _fallback_assessment(self, cv: str, job_description: str) -> dict:
        """Fallback assessment when LLM Factory is not available."""
        logger.warning("Using fallback assessment method")
        return {
            'match_percentage': 50,
            'confidence': 'Low',
            'fitness_rating': 'Unknown',
            'recommendation': 'Manual Review Required',
            'success_probability': 0.5,
            'strengths': [],
            'weaknesses': ['Unable to perform detailed analysis'],
            'risk_factors': ['LLM Factory unavailable'],
            'key_insights': ['Fallback assessment - limited analysis available'],
            'processing_time': 0.0,
            'assessment_method': 'fallback'
        }


def get_match_and_cover_letter(cv: str, job_description: str) -> dict:
    """
    LLM Factory-based replacement for the original phi3 implementation.
    
    Provides professional job matching and cover letter generation with quality control.
    
    Returns:
        dict: {
            'match_percentage': int (0-100),
            'cover_letter': str,
            'fitness_assessment': dict (detailed assessment data),
            'quality_metrics': dict (quality validation data)
        }
    """
    logger.info("🏭 Starting LLM Factory job matching and cover letter generation")
    
    # Initialize the matcher
    matcher = LLMFactoryJobMatcher()
    
    # Get comprehensive job fitness assessment
    fitness_assessment = matcher.get_job_fitness_assessment(cv, job_description)
    match_percentage = fitness_assessment.get('match_percentage', 50)
    
    # Generate professional cover letter
    cover_letter_data = matcher.generate_cover_letter(cv, job_description, fitness_assessment)
    cover_letter = cover_letter_data.get('cover_letter', '')
    
    # Compile results in the expected format
    result = {
        'match_percentage': match_percentage,
        'cover_letter': cover_letter,
        'fitness_assessment': fitness_assessment,
        'quality_metrics': {
            'cover_letter_quality': cover_letter_data.get('quality_validation', {}),
            'assessment_confidence': fitness_assessment.get('confidence', 'Unknown'),
            'processing_time': {
                'fitness_assessment': fitness_assessment.get('processing_time', 0.0),
                'cover_letter': cover_letter_data.get('processing_time', 0.0)
            }
        }
    }
    
    logger.info(f"✅ LLM Factory processing complete: {match_percentage}% match, cover letter generated")
    return result


# Backwards compatibility: maintain the original function name and signature
def phi3_match_and_cover(cv: str, job_description: str) -> dict:
    """Backwards compatible wrapper for the original function name."""
    return get_match_and_cover_letter(cv, job_description)
