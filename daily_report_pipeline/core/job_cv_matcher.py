"""
Job-CV Matching Engine
=====================

Compares job requirements against CV data to determine match level
and provide go/no-go decisions.
"""

import logging
import re
from typing import Dict, List, Any, Set
from .cv_data_manager import CVDataManager

logger = logging.getLogger(__name__)

class JobCVMatcher:
    """
    Matches job requirements against CV data using semantic similarity
    and domain alignment to provide match scores and go/no-go decisions.
    """
    
    def __init__(self, cv_manager: CVDataManager = None):
        """Initialize the job-CV matcher
        
        Args:
            cv_manager: CV data manager instance
        """
        self.cv_manager = cv_manager or CVDataManager()
        self.cv_data = self.cv_manager.load_cv_data()
        self.cv_skills = set(skill.lower() for skill in self.cv_data.get('skills', {}).get('all', []))
        self.cv_domains = set(domain.lower() for domain in self.cv_data.get('domains', []))
        
        logger.info(f"🎯 Job-CV Matcher initialized: {len(self.cv_skills)} CV skills, "
                   f"{len(self.cv_domains)} domains")
    
    def calculate_match_score(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive match score for a job
        
        Args:
            job_data: Job data including skills and domain information
            
        Returns:
            Comprehensive match result dictionary
        """
        try:
            # Extract job information
            job_skills = self._extract_job_skills(job_data)
            job_domain = job_data.get('domain_classification_result', {}).get('primary_domain', '').lower()
            job_description = job_data.get('full_content', '') or job_data.get('job_description', '')
            
            # Calculate different match components
            skill_match = self._calculate_skill_match(job_skills)
            domain_match = self._calculate_domain_match(job_domain)
            experience_match = self._calculate_experience_match(job_description, job_domain)
            seniority_match = self._calculate_seniority_match(job_description)
            
            # Calculate overall match score (weighted average)
            overall_score = (
                skill_match['score'] * 0.4 +      # 40% weight on skills
                domain_match['score'] * 0.3 +     # 30% weight on domain
                experience_match['score'] * 0.2 + # 20% weight on experience
                seniority_match['score'] * 0.1    # 10% weight on seniority
            )
            
            # Determine match level and go/no-go decision
            match_level, go_no_go, confidence = self._determine_match_level(overall_score, domain_match['score'])
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                skill_match, domain_match, experience_match, seniority_match, overall_score
            )
            
            return {
                'overall_score': round(overall_score, 2),
                'match_level': match_level,
                'go_no_go': go_no_go,
                'confidence': confidence,
                'reasoning': reasoning,
                'skill_match': skill_match,
                'domain_match': domain_match,
                'experience_match': experience_match,
                'seniority_match': seniority_match,
                'skills_matched': skill_match['matched_skills'],
                'skills_total': skill_match['job_skills_count'],
                'skill_gaps': skill_match['missing_skills']
            }
            
        except Exception as e:
            logger.error(f"❌ Match calculation failed: {e}")
            return self._get_fallback_match_result()
    
    def _extract_job_skills(self, job_data: Dict[str, Any]) -> Set[str]:
        """Extract skills from job data
        
        Args:
            job_data: Job data dictionary
            
        Returns:
            Set of job skills (lowercase)
        """
        job_skills = set()
        
        # Get skills from different sources
        technical_skills = job_data.get('technical_skills', []) or []
        business_skills = job_data.get('business_skills', []) or []
        all_skills = job_data.get('all_skills', []) or []
        
        # Combine all skills
        for skills_list in [technical_skills, business_skills, all_skills]:
            if isinstance(skills_list, list):
                job_skills.update(skill.lower().strip() for skill in skills_list if skill)
        
        # Also extract from job description text
        job_description = job_data.get('full_content', '') or job_data.get('job_description', '')
        extracted_skills = self._extract_skills_from_text(job_description)
        job_skills.update(extracted_skills)
        
        return job_skills
    
    def _extract_skills_from_text(self, text: str) -> Set[str]:
        """Extract skills from job description text
        
        Args:
            text: Job description text
            
        Returns:
            Set of extracted skills
        """
        if not text:
            return set()
        
        text_lower = text.lower()
        extracted_skills = set()
        
        # Common technical skills patterns
        tech_patterns = [
            'python', 'sql', 'java', 'javascript', 'react', 'node.js', 'angular', 'vue',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'database', 'postgresql', 'mysql', 'mongodb', 'redis',
            'api', 'rest', 'graphql', 'microservices', 'devops', 'ci/cd',
            'machine learning', 'ai', 'data science', 'analytics', 'tableau', 'power bi',
            'sap', 'oracle', 'microsoft', 'adobe', 'salesforce'
        ]
        
        # Business skills patterns
        business_patterns = [
            'project management', 'team leadership', 'stakeholder management',
            'vendor management', 'contract negotiation', 'compliance', 'governance',
            'risk management', 'audit', 'financial planning', 'budgeting',
            'process optimization', 'change management', 'agile', 'scrum',
            'business analysis', 'requirements gathering'
        ]
        
        # Check for skill patterns
        for skill in tech_patterns + business_patterns:
            if skill in text_lower:
                extracted_skills.add(skill)
        
        # Extract programming languages specifically mentioned
        prog_lang_match = re.findall(r'\b(python|java|javascript|c\+\+|c#|php|ruby|go|rust|scala)\b', text_lower)
        extracted_skills.update(prog_lang_match)
        
        return extracted_skills
    
    def _calculate_skill_match(self, job_skills: Set[str]) -> Dict[str, Any]:
        """Calculate skill matching score
        
        Args:
            job_skills: Set of job skills
            
        Returns:
            Skill match result dictionary
        """
        if not job_skills:
            return {
                'score': 0.0,
                'matched_skills': [],
                'missing_skills': [],
                'job_skills_count': 0,
                'match_percentage': 0.0
            }
        
        # Find exact matches
        exact_matches = job_skills.intersection(self.cv_skills)
        
        # Find semantic matches (partial string matches)
        semantic_matches = set()
        for job_skill in job_skills:
            if job_skill not in exact_matches:
                for cv_skill in self.cv_skills:
                    if (job_skill in cv_skill or cv_skill in job_skill) and len(job_skill) > 3:
                        semantic_matches.add(job_skill)
                        break
        
        total_matches = exact_matches.union(semantic_matches)
        missing_skills = job_skills - total_matches
        
        # Calculate score
        match_percentage = len(total_matches) / len(job_skills) if job_skills else 0
        
        # Apply experience bonus for senior roles
        experience_bonus = 0.1 if self.cv_data.get('total_years_experience', 0) >= 15 else 0
        score = min(1.0, match_percentage + experience_bonus)
        
        return {
            'score': score,
            'matched_skills': list(total_matches),
            'missing_skills': list(missing_skills),
            'job_skills_count': len(job_skills),
            'match_percentage': round(match_percentage * 100, 1)
        }
    
    def _calculate_domain_match(self, job_domain: str) -> Dict[str, Any]:
        """Calculate domain alignment score
        
        Args:
            job_domain: Job's primary domain
            
        Returns:
            Domain match result dictionary
        """
        if not job_domain:
            return {'score': 0.5, 'alignment': 'Unknown', 'reasoning': 'No job domain specified'}
        
        job_domain_clean = job_domain.lower().strip()
        
        # Check for direct domain matches
        if job_domain_clean in self.cv_domains:
            return {
                'score': 1.0, 
                'alignment': 'Perfect', 
                'reasoning': f'Direct experience in {job_domain} domain'
            }
        
        # Check for related domain matches
        domain_relationships = {
            'technology': ['tech', 'software', 'it', 'digital'],
            'finance': ['financial', 'banking', 'fintech'],
            'healthcare': ['pharmaceutical', 'medical', 'health'],
            'consulting': ['advisory', 'professional services']
        }
        
        for cv_domain in self.cv_domains:
            cv_domain_lower = cv_domain.lower()
            if job_domain_clean in domain_relationships.get(cv_domain_lower, []):
                return {
                    'score': 0.8, 
                    'alignment': 'Strong', 
                    'reasoning': f'Related experience in {cv_domain} (matches {job_domain})'
                }
        
        # Check for cross-functional experience (technology + finance)
        if (job_domain_clean in ['technology', 'finance'] and 
            'technology' in [d.lower() for d in self.cv_domains] and 
            'finance' in [d.lower() for d in self.cv_domains]):
            return {
                'score': 0.9, 
                'alignment': 'Excellent', 
                'reasoning': 'Cross-functional finance + technology experience'
            }
        
        return {
            'score': 0.3, 
            'alignment': 'Limited', 
            'reasoning': f'No direct experience in {job_domain} domain'
        }
    
    def _calculate_experience_match(self, job_description: str, job_domain: str) -> Dict[str, Any]:
        """Calculate experience relevance score
        
        Args:
            job_description: Job description text
            job_domain: Job's primary domain
            
        Returns:
            Experience match result dictionary
        """
        if not job_description:
            return {'score': 0.5, 'reasoning': 'No job description available'}
        
        job_desc_lower = job_description.lower()
        experience_indicators = []
        score = 0.5  # Base score
        
        # Check for specific experience matches from CV
        cv_experience_keywords = [
            'software license', 'vendor management', 'contract negotiation',
            'project management', 'team lead', 'compliance', 'governance',
            'deutsche bank', 'banking', 'financial services', 'technology'
        ]
        
        for keyword in cv_experience_keywords:
            if keyword in job_desc_lower:
                score += 0.1
                experience_indicators.append(keyword)
        
        # Seniority level matching
        senior_keywords = ['senior', 'lead', 'manager', 'director', 'head']
        if any(keyword in job_desc_lower for keyword in senior_keywords):
            if self.cv_data.get('total_years_experience', 0) >= 15:
                score += 0.2
                experience_indicators.append('senior role match')
        
        # Industry experience bonus
        if job_domain.lower() in ['finance', 'technology']:
            if (self.cv_data.get('finance_experience', False) or 
                self.cv_data.get('technology_experience', False)):
                score += 0.15
                experience_indicators.append('industry experience')
        
        score = min(1.0, score)
        
        return {
            'score': score,
            'reasoning': f"Experience match based on: {', '.join(experience_indicators) if experience_indicators else 'general background'}"
        }
    
    def _calculate_seniority_match(self, job_description: str) -> Dict[str, Any]:
        """Calculate seniority level match
        
        Args:
            job_description: Job description text
            
        Returns:
            Seniority match result dictionary
        """
        if not job_description:
            return {'score': 0.5, 'reasoning': 'No job description available'}
        
        job_desc_lower = job_description.lower()
        cv_seniority = self.cv_data.get('seniority_level', 'unknown')
        cv_years = self.cv_data.get('total_years_experience', 0)
        
        # Detect job seniority level
        if any(keyword in job_desc_lower for keyword in ['senior', 'lead', 'principal', 'architect']):
            required_seniority = 'senior'
        elif any(keyword in job_desc_lower for keyword in ['manager', 'director', 'head', 'chief']):
            required_seniority = 'executive'
        elif any(keyword in job_desc_lower for keyword in ['junior', 'associate', 'entry']):
            required_seniority = 'junior'
        else:
            required_seniority = 'mid'
        
        # Calculate match based on experience level
        if required_seniority == 'senior' and cv_years >= 10:
            return {'score': 1.0, 'reasoning': 'Strong senior-level experience match'}
        elif required_seniority == 'executive' and cv_years >= 15:
            return {'score': 1.0, 'reasoning': 'Executive-level experience match'}
        elif required_seniority == 'mid' and cv_years >= 5:
            return {'score': 0.9, 'reasoning': 'Mid-level experience match'}
        elif required_seniority == 'junior':
            return {'score': 0.7, 'reasoning': 'Overqualified for junior role'}
        else:
            return {'score': 0.6, 'reasoning': 'Partial seniority match'}
    
    def _determine_match_level(self, overall_score: float, domain_score: float) -> tuple:
        """Determine match level and go/no-go decision
        
        Args:
            overall_score: Overall match score (0-1)
            domain_score: Domain alignment score (0-1)
            
        Returns:
            Tuple of (match_level, go_no_go, confidence)
        """
        # Calculate confidence based on domain alignment
        confidence = int((overall_score * 0.7 + domain_score * 0.3) * 100)
        
        # Determine match level with conservative thresholds
        if overall_score >= 0.8 and domain_score >= 0.7:
            return "Excellent Match", "GO", confidence
        elif overall_score >= 0.65 and domain_score >= 0.5:
            return "Good Match", "GO", confidence
        elif overall_score >= 0.45 and domain_score >= 0.3:
            return "Moderate Match", "CONSIDER", confidence
        else:
            return "Poor Match", "NO GO", confidence
    
    def _generate_reasoning(self, skill_match: Dict, domain_match: Dict, 
                          experience_match: Dict, seniority_match: Dict, 
                          overall_score: float) -> str:
        """Generate human-readable reasoning for the match
        
        Args:
            skill_match: Skill match results
            domain_match: Domain match results
            experience_match: Experience match results
            seniority_match: Seniority match results
            overall_score: Overall match score
            
        Returns:
            Formatted reasoning string
        """
        reasoning_parts = []
        
        # Skill assessment
        skill_pct = skill_match.get('match_percentage', 0)
        reasoning_parts.append(f"Skills: {skill_pct}% match ({len(skill_match.get('matched_skills', []))} of {skill_match.get('job_skills_count', 0)} required)")
        
        # Domain assessment
        domain_alignment = domain_match.get('alignment', 'Unknown')
        reasoning_parts.append(f"Domain: {domain_alignment} alignment - {domain_match.get('reasoning', 'N/A')}")
        
        # Experience summary
        reasoning_parts.append(f"Experience: {experience_match.get('reasoning', 'N/A')}")
        
        # Overall assessment
        score_pct = int(overall_score * 100)
        reasoning_parts.append(f"Overall confidence: {score_pct}%")
        
        return " | ".join(reasoning_parts)
    
    def _get_fallback_match_result(self) -> Dict[str, Any]:
        """Return fallback match result if calculation fails
        
        Returns:
            Basic match result dictionary
        """
        return {
            'overall_score': 0.5,
            'match_level': 'Unknown',
            'go_no_go': 'MANUAL REVIEW',
            'confidence': 50,
            'reasoning': 'Match calculation failed - manual review required',
            'skill_match': {'score': 0.5, 'matched_skills': [], 'missing_skills': [], 'job_skills_count': 0},
            'domain_match': {'score': 0.5, 'alignment': 'Unknown'},
            'experience_match': {'score': 0.5},
            'seniority_match': {'score': 0.5},
            'skills_matched': [],
            'skills_total': 0,
            'skill_gaps': []
        }
