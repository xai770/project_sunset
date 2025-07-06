"""
CV Matching Specialist
=====================

Integrates CV profile matching into the modular pipeline architecture.
Handles matching job descriptions against CV profiles with intelligent
context awareness and career progression understanding.
"""

from typing import Dict, Any, Optional, Tuple, List
import logging
import hashlib
import json
from datetime import datetime, timedelta
from functools import lru_cache
from .models.matching_result import CVMatchResult
from .models.validators import validate_experience_entry, validate_skill_entry
from .analyzers.skills_analyzer import SkillsAnalyzer
from .analyzers.experience_analyzer import ExperienceAnalyzer
from .analyzers.domain_analyzer import DomainAnalyzer

logger = logging.getLogger(__name__)

class CVMatchingSpecialist:
    """CV matching specialist with intelligent context awareness"""
    
    def __init__(self):
        self.specialist_name = "CV Matching Specialist"
        self.skills_analyzer = SkillsAnalyzer()
        self.experience_analyzer = ExperienceAnalyzer()
        self.domain_analyzer = DomainAnalyzer()
        self.cache_timeout = timedelta(hours=24)
        self._clear_cache_after = datetime.now() + self.cache_timeout
        
    def _generate_cache_key(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Generate a cache key from CV and job data"""
        combined_data = {
            'cv': cv_data,
            'job': job_data
        }
        data_str = json.dumps(combined_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
        
    @lru_cache(maxsize=1000)
    def _cached_match(self, cache_key: str) -> Tuple[CVMatchResult, datetime]:
        """Cached version of the match calculation"""
        return None, datetime.min
        
    def match_cv_to_job(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> CVMatchResult:
        """
        Match CV against job requirements with intelligent context analysis
        
        Args:
            cv_data: Dictionary containing structured CV information
            job_data: Dictionary containing job requirements and context
            
        Returns:
            CVMatchResult with match details and confidence scores
        """
        try:
            # Validate input data
            validation_errors = self._validate_input_data(cv_data, job_data)
            if validation_errors:
                return CVMatchResult.create_error_result(
                    cv_data, job_data,
                    f"Input validation failed: {'; '.join(validation_errors)}"
                )
                
            # Check cache
            cache_key = self._generate_cache_key(cv_data, job_data)
            cached_result, cache_time = self._cached_match(cache_key)
            
            if cached_result and datetime.now() - cache_time < self.cache_timeout:
                logger.info("Returning cached match result")
                return cached_result
                
            # Clear cache if needed
            if datetime.now() > self._clear_cache_after:
                self._cached_match.cache_clear()
                self._clear_cache_after = datetime.now() + self.cache_timeout
            
            # Perform matching analysis
            skills_match = self.skills_analyzer.analyze(cv_data, job_data)
            experience_match = self.experience_analyzer.analyze(cv_data, job_data)
            domain_match = self.domain_analyzer.analyze_domain(cv_data, job_data)
            
            # Create result
            result = CVMatchResult(
                cv_data=cv_data,
                job_data=job_data,
                skills_match=skills_match,
                experience_match=experience_match,
                domain_match=domain_match
            )
            
            # Generate explanation
            result.match_explanation = result.generate_match_explanation()
            
            # Update cache
            self._cached_match(cache_key, (result, datetime.now()))
            
            logger.info(f"Match analysis completed with confidence: {result.confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in CV matching: {str(e)}")
            return CVMatchResult.create_error_result(cv_data, job_data, str(e))
    
    def _validate_input_data(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> List[str]:
        """Validate input data structures"""
        errors = []
        
        # Validate CV data
        if not isinstance(cv_data, dict):
            errors.append("CV data must be a dictionary")
            return errors
            
        # Check required CV sections
        if 'experience' not in cv_data:
            errors.append("CV missing 'experience' section")
        else:
            for exp in cv_data['experience']:
                exp_errors = validate_experience_entry(exp)
                if exp_errors:
                    errors.extend(f"Experience entry error: {e}" for e in exp_errors)
                    
        if 'skills' not in cv_data:
            errors.append("CV missing 'skills' section")
        else:
            for skill, details in cv_data['skills'].items():
                skill_errors = validate_skill_entry(details)
                if skill_errors:
                    errors.extend(f"Skill '{skill}' error: {e}" for e in skill_errors)
                    
        # Validate job data
        if not isinstance(job_data, dict):
            errors.append("Job data must be a dictionary")
            return errors
            
        # Check required job sections
        if 'requirements' not in job_data:
            errors.append("Job missing 'requirements' section")
            
        if 'title' not in job_data:
            errors.append("Job missing 'title' field")
            
        return errors
    
    def get_matching_statistics(self) -> Dict[str, Any]:
        """Get CV matching statistics"""
        return {
            'matches_processed': self.stats.get('specialists_executed', 0),
            'high_confidence_matches': self.stats.get('high_confidence_matches', 0),
            'low_confidence_matches': self.stats.get('low_confidence_matches', 0),
            'errors': self.stats.get('errors', 0),
            'cache_size': len(self._cached_match.cache_info().currsize)
        }
