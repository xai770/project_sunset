"""
Experience Analyzer Component
===========================

Analyzes professional experience matching between CV and job requirements,
considering career progression, role levels, and transferable experience.

Author: Sandy's Modular Architecture
Version: 1.0 (Development)
"""

from typing import Dict, Any, List, Set
from ..models.matching_result import ExperienceMatchResult
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ExperienceAnalyzer:
    """Intelligent experience matching analyzer"""
    
    def __init__(self):
        self.role_levels = {
            'entry': {'associate', 'junior', 'trainee', 'intern'},
            'mid': {'senior', 'lead', 'specialist', 'expert'},
            'management': {'manager', 'head', 'director', 'vp', 'chief'},
            'executive': {'cto', 'cio', 'ceo', 'executive'}
        }
        
        self.equivalent_roles = {
            'software architect': {'solution architect', 'technical architect', 'system architect'},
            'project manager': {'program manager', 'project lead', 'delivery manager'},
            'team lead': {'technical lead', 'development lead', 'team leader'},
            'developer': {'programmer', 'software engineer', 'coder'}
        }
    
    def analyze(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> ExperienceMatchResult:
        """
        Analyze experience match between CV and job requirements
        
        Args:
            cv_data: Dictionary containing CV information
            job_data: Dictionary containing job requirements
            
        Returns:
            ExperienceMatchResult with match details
        """
        try:
            # Check years of experience
            required_years = self._extract_required_years(job_data)
            actual_years = self._calculate_total_experience(cv_data)
            years_match = actual_years >= required_years
            
            # Check role level match
            required_level = self._extract_required_level(job_data)
            cv_level = self._determine_current_level(cv_data)
            role_level_match = self._check_level_match(required_level, cv_level)
            
            # Find relevant past roles
            relevant_roles = self._find_relevant_roles(cv_data, job_data)
            
            # Find transferable experience
            transferable = self._find_transferable_experience(cv_data, job_data)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(
                years_match=years_match,
                role_level_match=role_level_match,
                relevant_roles=relevant_roles,
                transferable_experience=transferable,
                required_years=required_years,
                actual_years=actual_years
            )
            
            return ExperienceMatchResult(
                years_match=years_match,
                role_level_match=role_level_match,
                relevant_roles=list(relevant_roles),
                transferable_experience=list(transferable),
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error in experience analysis: {str(e)}")
            return ExperienceMatchResult(confidence=0.0)
    
    def _extract_required_years(self, job_data: Dict[str, Any]) -> int:
        """Extract required years of experience from job data"""
        requirements = str(job_data.get('requirements', ''))
        
        # Look for patterns like "X+ years" or "X years"
        import re
        patterns = [
            r'(\d+)\+?\s*years?(?:\s+of)?\s+experience',
            r'(\d+)\s*years?(?:\s+of)?\s+minimum',
            r'minimum\s+of\s+(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, requirements.lower())
            if match:
                return int(match.group(1))
        
        return 0  # Default to 0 if not specified
    
    def _calculate_total_experience(self, cv_data: Dict[str, Any]) -> float:
        """Calculate total years of relevant experience"""
        total_years = 0.0
        current_year = datetime.now().year
        
        experience = cv_data.get('professional_experience', [])
        for role in experience:
            if isinstance(role, dict):
                start_year = self._extract_year(role.get('start_date', ''))
                end_year = self._extract_year(role.get('end_date', 'Present'))
                
                if end_year == 'Present':
                    end_year = current_year
                
                if start_year and end_year:
                    total_years += float(end_year) - float(start_year)
        
        return total_years
    
    def _extract_year(self, date_str: str) -> Any:
        """Extract year from date string"""
        if not date_str:
            return None
            
        if date_str.lower() == 'present':
            return 'Present'
            
        # Try to extract year
        import re
        match = re.search(r'(\d{4})', str(date_str))
        return int(match.group(1)) if match else None
    
    def _extract_required_level(self, job_data: Dict[str, Any]) -> str:
        """Determine required role level from job data"""
        title = str(job_data.get('title', '')).lower()
        
        for level, indicators in self.role_levels.items():
            if any(ind in title for ind in indicators):
                return level
        
        # Default to mid-level if not specified
        return 'mid'
    
    def _determine_current_level(self, cv_data: Dict[str, Any]) -> str:
        """Determine current role level from CV"""
        experience = cv_data.get('professional_experience', [])
        if not experience:
            return 'entry'
            
        # Look at most recent role
        latest_role = experience[0] if isinstance(experience, list) else {}
        title = str(latest_role.get('title', '')).lower()
        
        for level, indicators in self.role_levels.items():
            if any(ind in title for ind in indicators):
                return level
        
        # Default to mid-level
        return 'mid'
    
    def _check_level_match(self, required: str, actual: str) -> bool:
        """Check if actual level matches or exceeds required level"""
        levels = ['entry', 'mid', 'management', 'executive']
        
        try:
            required_idx = levels.index(required)
            actual_idx = levels.index(actual)
            return actual_idx >= required_idx
        except ValueError:
            return False
    
    def _find_relevant_roles(self, cv_data: Dict[str, Any], 
                           job_data: Dict[str, Any]) -> Set[str]:
        """Find directly relevant past roles"""
        relevant = set()
        
        # Extract job context
        job_context = ' '.join([
            str(job_data.get('title', '')),
            str(job_data.get('description', '')),
            str(job_data.get('department', ''))
        ]).lower()
        
        # Check each role
        experience = cv_data.get('professional_experience', [])
        for role in experience:
            if isinstance(role, dict):
                title = str(role.get('title', '')).lower()
                
                # Check for direct title match or equivalent role
                if title in job_context:
                    relevant.add(title)
                else:
                    # Check equivalent roles
                    for base_role, equivalents in self.equivalent_roles.items():
                        if title in equivalents and base_role in job_context:
                            relevant.add(title)
        
        return relevant
    
    def _find_transferable_experience(self, cv_data: Dict[str, Any],
                                    job_data: Dict[str, Any]) -> Set[str]:
        """Identify transferable experience from past roles"""
        transferable = set()
        
        # Extract key aspects of the job
        job_aspects = self._extract_job_aspects(job_data)
        
        # Look through past roles for transferable experience
        experience = cv_data.get('professional_experience', [])
        for role in experience:
            if isinstance(role, dict):
                # Check responsibilities
                for resp in role.get('responsibilities', []):
                    resp_aspects = self._extract_aspects_from_text(resp)
                    if resp_aspects & job_aspects:
                        transferable.add(str(role.get('title', '')))
                        break
        
        return transferable
    
    def _extract_job_aspects(self, job_data: Dict[str, Any]) -> Set[str]:
        """Extract key aspects from job data"""
        aspects = set()
        
        # Common aspects to look for
        aspect_indicators = {
            'team management', 'project management', 'stakeholder management',
            'technical leadership', 'strategy', 'architecture', 'development',
            'analysis', 'design', 'implementation', 'optimization',
            'vendor management', 'process improvement'
        }
        
        # Extract from various job fields
        for field in ['title', 'description', 'responsibilities', 'requirements']:
            text = str(job_data.get(field, '')).lower()
            aspects.update(aspect for aspect in aspect_indicators if aspect in text)
        
        return aspects
    
    def _extract_aspects_from_text(self, text: str) -> Set[str]:
        """Extract key aspects from text"""
        text = text.lower()
        
        aspects = {
            'team management': {'team', 'manage', 'lead', 'direct'},
            'project management': {'project', 'program', 'initiative'},
            'stakeholder management': {'stakeholder', 'client', 'partner'},
            'technical leadership': {'technical', 'architecture', 'design'},
            'strategy': {'strategy', 'strategic', 'planning'},
            'development': {'develop', 'implement', 'code', 'program'},
            'analysis': {'analyze', 'assess', 'evaluate'},
            'optimization': {'optimize', 'improve', 'enhance'},
            'vendor management': {'vendor', 'supplier', 'procurement'}
        }
        
        found = set()
        for aspect, indicators in aspects.items():
            if any(ind in text for ind in indicators):
                found.add(aspect)
        
        return found
    
    def _calculate_confidence(self, years_match: bool, role_level_match: bool,
                            relevant_roles: Set[str], transferable_experience: Set[str],
                            required_years: int, actual_years: float) -> float:
        """Calculate overall confidence score"""
        score = 0.0
        
        # Years of experience (40%)
        if years_match:
            score += 0.4
        elif required_years > 0:
            # Partial credit for close matches
            ratio = min(1.0, actual_years / required_years)
            score += 0.4 * ratio
        
        # Role level match (30%)
        if role_level_match:
            score += 0.3
        
        # Relevant roles (20%)
        if relevant_roles:
            score += 0.2
        elif transferable_experience:
            score += 0.1  # Partial credit for transferable experience
        
        return score
