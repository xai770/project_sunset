"""
Skills Analyzer Component
========================

Analyzes and matches skills between CV and job requirements with
intelligent recognition of equivalent and transferable skills.

Author: Sandy's Modular Architecture
Version: 1.0 (Development)
"""

from typing import Dict, Any, List, Set
from ..models.matching_result import SkillsMatchResult
import logging

logger = logging.getLogger(__name__)

class SkillsAnalyzer:
    """Intelligent skills matching analyzer"""
    
    def __init__(self):
        self.technical_skill_indicators = {
            'programming', 'software', 'development', 'database',
            'architecture', 'infrastructure', 'cloud', 'security',
            'implementation', 'design', 'analysis', 'deployment'
        }
        
        self.management_skill_indicators = {
            'leadership', 'management', 'governance', 'strategy',
            'planning', 'coordination', 'supervision', 'direction',
            'optimization', 'transformation', 'stakeholder'
        }
        
        self.equivalent_skills = {
            'vendor management': {'supplier management', 'procurement', 'sourcing'},
            'project management': {'program management', 'project leadership'},
            'software development': {'programming', 'coding', 'development'},
            'contract management': {'agreement management', 'legal management'},
            'it governance': {'technology governance', 'tech governance'},
        }
    
    def analyze(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> SkillsMatchResult:
        """
        Analyze skills match between CV and job requirements
        
        Args:
            cv_data: Dictionary containing CV information
            job_data: Dictionary containing job requirements
            
        Returns:
            SkillsMatchResult with match details
        """
        try:
            # Extract required skills from job
            required_skills = self._extract_required_skills(job_data)
            
            # Extract skills from CV
            cv_skills = self._extract_cv_skills(cv_data)
            
            # Find direct matches
            direct_matches = required_skills & cv_skills
            
            # Find equivalent skill matches
            equivalent_matches = self._find_equivalent_skills(
                required_skills - direct_matches,
                cv_skills - direct_matches
            )
            
            # Combine direct and equivalent matches
            matched_skills = list(direct_matches | equivalent_matches)
            
            # Find relevant additional skills
            additional_skills = self._find_relevant_additional_skills(
                cv_skills - direct_matches - equivalent_matches,
                job_data
            )
            
            # Calculate missing skills
            missing = list(required_skills - direct_matches - equivalent_matches)
            
            # Calculate confidence score
            if not required_skills:
                confidence = 1.0  # No required skills specified
            else:
                matches = len(matched_skills)
                required = len(required_skills)
                confidence = matches / required
                
                # Boost confidence if we have relevant additional skills
                if additional_skills:
                    confidence = min(1.0, confidence + 0.1)
            
            return SkillsMatchResult(
                required_skills_matched=matched_skills,
                additional_relevant_skills=list(additional_skills),
                missing_skills=missing,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error in skills analysis: {str(e)}")
            return SkillsMatchResult(confidence=0.0)
    
    def _extract_required_skills(self, job_data: Dict[str, Any]) -> Set[str]:
        """Extract and normalize required skills from job data"""
        skills = set()
        
        # Extract from requirements section
        requirements = job_data.get('requirements', [])
        if isinstance(requirements, list):
            for req in requirements:
                skills.update(self._normalize_skill_text(req))
        elif isinstance(requirements, str):
            skills.update(self._normalize_skill_text(requirements))
            
        # Extract from responsibilities section
        responsibilities = job_data.get('responsibilities', [])
        if isinstance(responsibilities, list):
            for resp in responsibilities:
                skills.update(self._extract_skills_from_text(resp))
        elif isinstance(responsibilities, str):
            skills.update(self._extract_skills_from_text(responsibilities))
            
        return skills
    
    def _extract_cv_skills(self, cv_data: Dict[str, Any]) -> Set[str]:
        """Extract and normalize skills from CV data"""
        skills = set()
        
        # Extract from core competencies
        competencies = cv_data.get('core_competencies', {})
        for category, items in competencies.items():
            if isinstance(items, list):
                for item in items:
                    skills.update(self._normalize_skill_text(item))
            elif isinstance(items, str):
                skills.update(self._normalize_skill_text(items))
        
        # Extract from experience
        experience = cv_data.get('professional_experience', [])
        for role in experience:
            if isinstance(role, dict):
                # Extract from responsibilities/achievements
                for item in role.get('responsibilities', []):
                    skills.update(self._extract_skills_from_text(item))
                    
                # Extract from role title
                skills.update(self._extract_skills_from_text(role.get('title', '')))
        
        return skills
    
    def _normalize_skill_text(self, text: str) -> Set[str]:
        """Normalize skill text and split into individual skills"""
        if not text:
            return set()
            
        # Convert to lowercase
        text = text.lower()
        
        # Split on common delimiters
        parts = text.replace(',', ' ').replace(';', ' ').replace('•', ' ').split()
        
        # Remove common filler words
        skills = {
            word for word in parts 
            if len(word) > 2 and word not in {'and', 'the', 'for', 'with'}
        }
        
        return skills
    
    def _extract_skills_from_text(self, text: str) -> Set[str]:
        """Extract likely skills from text"""
        words = self._normalize_skill_text(text)
        
        # Keep words that look like skills
        return {
            word for word in words
            if any(indicator in word for indicator in 
                  self.technical_skill_indicators | self.management_skill_indicators)
        }
    
    def _find_equivalent_skills(self, required: Set[str], available: Set[str]) -> Set[str]:
        """Find equivalent skills between required and available skills"""
        equivalent_matches = set()
        
        for req in required:
            # Check each equivalent set
            for base_skill, equivalents in self.equivalent_skills.items():
                if req in equivalents:
                    # Check if we have any equivalent skills
                    matches = available & equivalents
                    if matches:
                        equivalent_matches.update(matches)
        
        return equivalent_matches
    
    def _find_relevant_additional_skills(self, 
                                       remaining_skills: Set[str],
                                       job_data: Dict[str, Any]) -> Set[str]:
        """Find additional skills that might be relevant to the role"""
        relevant = set()
        
        # Extract context from job data
        context = ' '.join([
            str(job_data.get('title', '')),
            str(job_data.get('description', '')),
            str(job_data.get('department', ''))
        ]).lower()
        
        # Keep skills that appear in the job context
        for skill in remaining_skills:
            if skill in context:
                relevant.add(skill)
        
        return relevant
