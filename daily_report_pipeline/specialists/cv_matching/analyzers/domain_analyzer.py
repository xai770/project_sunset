from typing import List, Dict, Set
from ..models.matching_result import DomainMatch

class DomainAnalyzer:
    def __init__(self):
        self.industry_weight = 0.4
        self.domain_skills_weight = 0.3
        self.experience_weight = 0.3
        
    def analyze_domain(
        self,
        cv_data: Dict,
        job_data: Dict
    ) -> DomainMatch:
        """
        Analyze domain expertise matching between CV and job requirements.
        
        Args:
            cv_data: Dictionary containing CV information including experience and skills
            job_data: Dictionary containing job requirements and domain information
            
        Returns:
            DomainMatch object with detailed domain matching information
        """
        # Extract domain information
        job_industry = job_data.get('industry', '')
        job_domain_skills = set(job_data.get('domain_specific_skills', []))
        
        # Get CV domain information
        cv_industries = self._extract_cv_industries(cv_data)
        cv_domain_skills = self._extract_domain_skills(cv_data)
        
        # Calculate industry match
        industry_match = self._calculate_industry_match(
            cv_industries,
            job_industry
        )
        
        # Calculate domain skills match
        domain_skills_match = self._calculate_domain_skills_match(
            cv_domain_skills,
            job_domain_skills
        )
        
        # Find relevant experience
        relevant_experience = self._find_relevant_experience(
            cv_data.get('experience', []),
            job_industry
        )
        
        # Calculate overall match level
        match_level = (
            self.industry_weight * industry_match +
            self.domain_skills_weight * domain_skills_match +
            self.experience_weight * (min(1.0, len(relevant_experience) / 2))
        )
        
        # Get domain-specific skills that were matched
        matched_domain_skills = list(job_domain_skills.intersection(cv_domain_skills))
        
        return DomainMatch(
            industry=job_industry,
            match_level=match_level,
            relevant_experience=relevant_experience,
            domain_specific_skills=matched_domain_skills
        )
    
    def _extract_cv_industries(self, cv_data: Dict) -> Set[str]:
        """Extract all industries from CV experience."""
        industries = set()
        
        # Add industries from experience
        for exp in cv_data.get('experience', []):
            if 'industry' in exp:
                industries.add(exp['industry'].lower())
                
        # Add industries from profile section if available
        if 'profile' in cv_data and 'industries' in cv_data['profile']:
            industries.update(ind.lower() for ind in cv_data['profile']['industries'])
            
        return industries
    
    def _extract_domain_skills(self, cv_data: Dict) -> Set[str]:
        """Extract domain-specific skills from CV."""
        domain_skills = set()
        
        # Add skills from experience
        for exp in cv_data.get('experience', []):
            domain_skills.update(exp.get('domain_skills', []))
            
        # Add skills from dedicated skills section
        if 'skills' in cv_data:
            domain_skills.update(cv_data['skills'].get('domain_specific', []))
            
        return domain_skills
    
    def _calculate_industry_match(self, cv_industries: Set[str], job_industry: str) -> float:
        """Calculate how well the CV industries match the job industry."""
        if not job_industry:
            return 0.5  # Default match if job industry is not specified
            
        job_industry = job_industry.lower()
        
        # Direct match
        if job_industry in cv_industries:
            return 1.0
            
        # Industry relationships (simplified)
        related_industries = self._get_related_industries(job_industry)
        
        # Check for related industry matches
        overlap = cv_industries.intersection(related_industries)
        if overlap:
            return 0.7  # Good but not perfect match
            
        return 0.3  # Some relevant experience but not directly related
    
    def _get_related_industries(self, industry: str) -> Set[str]:
        """Get a set of related industries for a given industry."""
        # This is a simplified version - in practice, you'd want a more
        # comprehensive industry relationship mapping
        industry_relations = {
            'software': {'technology', 'it', 'consulting', 'finance'},
            'technology': {'software', 'it', 'telecommunications', 'consulting'},
            'finance': {'banking', 'insurance', 'technology', 'consulting'},
            'healthcare': {'biotech', 'medical', 'pharmaceutical', 'technology'},
            'consulting': {'technology', 'finance', 'strategy', 'management'},
        }
        
        return industry_relations.get(industry, set())
    
    def _calculate_domain_skills_match(
        self,
        cv_skills: Set[str],
        required_skills: Set[str]
    ) -> float:
        """Calculate the match level for domain-specific skills."""
        if not required_skills:
            return 0.5  # Default match if no specific skills required
            
        # Calculate overlap
        matching_skills = cv_skills.intersection(required_skills)
        
        # Calculate match ratio
        return len(matching_skills) / len(required_skills)
    
    def _find_relevant_experience(
        self,
        experience: List[Dict],
        target_industry: str
    ) -> List[str]:
        """Find experience entries relevant to the target industry."""
        relevant_exp = []
        target_industry = target_industry.lower()
        related_industries = self._get_related_industries(target_industry)
        
        for exp in experience:
            exp_industry = exp.get('industry', '').lower()
            if exp_industry == target_industry or exp_industry in related_industries:
                relevant_exp.append(
                    f"{exp.get('title', 'Role')} at {exp.get('company', 'Company')}"
                )
                
        return relevant_exp[:3]  # Return top 3 most relevant experiences
