"""
CV Matching Specialist
=====================

Matches CV against job descriptions using intelligent analysis.
"""

import time
from typing import List, Dict, Set, Tuple
from datetime import date
from difflib import SequenceMatcher
import spacy
from pathlib import Path

from .data_models import (
    CV, JobPosting, MatchResult, SkillMatch,
    Language, LanguageProficiency, JobRequirement
)
from .cv_parser import CVParser

class CVMatchingSpecialist:
    """Specialist for matching CVs against job postings"""
    
    def __init__(self) -> None:
        """Initialize the CV matching specialist with NLP models and configurations"""
        # Load spaCy model for text similarity
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            # If model not found, download it
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_lg"])
            self.nlp = spacy.load("en_core_web_lg")

        # Skill similarity threshold for fuzzy matching
        self.SKILL_SIMILARITY_THRESHOLD = 0.85
        
        # Weights for different matching aspects
        self.weights = {
            "skills": 0.35,
            "experience": 0.25,
            "education": 0.15,
            "industry": 0.15,
            "language": 0.10
        }

    def match_cv_to_job(self, cv: CV, job: JobPosting) -> MatchResult:
        """Match a CV against a job posting and return detailed match results."""
        # Calculate individual match scores
        skill_matches = self._match_skills(cv, job.requirements)
        language_score = self._match_languages(cv.languages, job.requirements.languages)
        experience_score = self._match_experience(cv, job.requirements)
        education_score = self._match_education(cv, job.requirements)
        industry_score = self._match_industry(cv, job.requirements)
        location_score = self._match_location(cv, job)

        # Calculate weighted overall score
        overall_score = (
            self.weights["skills"] * self._calculate_skill_score(skill_matches) +
            self.weights["experience"] * experience_score +
            self.weights["education"] * education_score +
            self.weights["industry"] * industry_score +
            self.weights["language"] * language_score
        )

        # Generate reasons and recommendations
        reasons = self._generate_match_reasons(
            cv, job, skill_matches, language_score,
            experience_score, education_score, industry_score
        )
        recommendations = self._generate_recommendations(
            cv, job, skill_matches, language_score,
            experience_score, education_score, industry_score
        )

        return MatchResult(
            cv=cv,
            job=job,
            overall_score=overall_score,
            skill_matches=skill_matches,
            language_match_score=language_score,
            experience_match_score=experience_score,
            education_match_score=education_score,
            industry_match_score=industry_score,
            location_match_score=location_score,
            reasons=reasons,
            recommendations=recommendations
        )

    def _match_skills(self, cv: CV, requirements: JobRequirement) -> List[SkillMatch]:
        """Match CV skills against job requirements"""
        skill_matches: List[SkillMatch] = []
        
        # Combine all skills from CV
        cv_skills: Set[str] = set()
        cv_skills.update(cv.skills)
        for exp in cv.experience:
            cv_skills.update(exp.skills)
        for category in cv.core_competencies.values():
            cv_skills.update(category)

        # Process required skills
        for req_skill in requirements.required_skills:
            best_match = self._find_best_skill_match(req_skill, cv_skills)
            if best_match:
                skill, confidence = best_match
                years = self._calculate_skill_years(cv, skill)
                skill_matches.append(SkillMatch(
                    skill=req_skill,
                    confidence=confidence,
                    source="direct_match" if confidence > 0.95 else "similar_skill",
                    years=years
                ))

        # Process preferred skills
        for pref_skill in requirements.preferred_skills:
            if pref_skill not in {sm.skill for sm in skill_matches}:
                best_match = self._find_best_skill_match(pref_skill, cv_skills)
                if best_match:
                    skill, confidence = best_match
                    years = self._calculate_skill_years(cv, skill)
                    skill_matches.append(SkillMatch(
                        skill=pref_skill,
                        confidence=confidence * 0.8,  # Lower confidence for preferred skills
                        source="preferred_skill",
                        years=years
                    ))

        return skill_matches

    def _find_best_skill_match(self, target_skill: str, cv_skills: Set[str]) -> Tuple[str, float] | None:
        """Find the best matching skill from CV skills for a target skill"""
        best_match = None
        best_score = 0.0
        
        # Normalize skills for comparison
        target_doc = self.nlp(target_skill.lower())
        
        for cv_skill in cv_skills:
            cv_doc = self.nlp(cv_skill.lower())
            
            # Calculate similarity scores
            exact_match_score = 1.0 if target_skill.lower() == cv_skill.lower() else 0.0
            fuzzy_score = SequenceMatcher(None, target_skill.lower(), cv_skill.lower()).ratio()
            semantic_score = target_doc.similarity(cv_doc)
            
            # Combine scores with weights
            combined_score = max(
                exact_match_score,
                0.7 * fuzzy_score + 0.3 * semantic_score
            )
            
            if combined_score > best_score and combined_score >= self.SKILL_SIMILARITY_THRESHOLD:
                best_score = combined_score
                best_match = (cv_skill, combined_score)
        
        return best_match

    def _calculate_skill_years(self, cv: CV, skill: str) -> float:
        """Calculate years of experience for a specific skill"""
        total_years = 0.0
        skill_doc = self.nlp(skill.lower())
        
        for exp in cv.experience:
            # Check if skill is mentioned in description or skills
            is_skill_present = False
            for desc in exp.description:
                desc_doc = self.nlp(desc.lower())
                if desc_doc.similarity(skill_doc) > self.SKILL_SIMILARITY_THRESHOLD:
                    is_skill_present = True
                    break
            
            if not is_skill_present:
                for exp_skill in exp.skills:
                    exp_skill_doc = self.nlp(exp_skill.lower())
                    if exp_skill_doc.similarity(skill_doc) > self.SKILL_SIMILARITY_THRESHOLD:
                        is_skill_present = True
                        break
            
            if is_skill_present:
                end = exp.end_date if exp.end_date else date.today()
                years = (end - exp.start_date).days / 365.25
                total_years += years
        
        return round(total_years, 1)

    def _match_languages(self, cv_languages: List[Language], required_languages: List[Language]) -> float:
        """Calculate language match score"""
        if not required_languages:
            return 1.0  # Perfect match if no language requirements
            
        total_score = 0.0
        for req_lang in required_languages:
            best_match_score = 0.0
            for cv_lang in cv_languages:
                if cv_lang.name.lower() == req_lang.name.lower():
                    # Convert proficiency to numeric score
                    req_score = self._proficiency_to_score(req_lang.proficiency)
                    cv_score = self._proficiency_to_score(cv_lang.proficiency)
                    
                    if cv_score >= req_score:
                        best_match_score = 1.0
                    else:
                        best_match_score = cv_score / req_score
                    break
            total_score += best_match_score
        
        return total_score / len(required_languages)

    def _proficiency_to_score(self, proficiency: LanguageProficiency) -> float:
        """Convert language proficiency to numeric score"""
        scores = {
            LanguageProficiency.NATIVE: 1.0,
            LanguageProficiency.FLUENT: 0.9,
            LanguageProficiency.ADVANCED: 0.7,
            LanguageProficiency.INTERMEDIATE: 0.5,
            LanguageProficiency.BASIC: 0.3
        }
        return scores[proficiency]

    def _match_experience(self, cv: CV, requirements: JobRequirement) -> float:
        """Calculate experience match score"""
        if not requirements.years_experience:
            return 1.0  # Perfect match if no experience requirement
            
        # Calculate total relevant experience
        total_relevant_years = 0.0
        for exp in cv.experience:
            # Check if experience is in relevant industry
            industry_relevance = any(
                self._calculate_text_similarity(exp.industry, req_ind) > 0.7
                for req_ind in requirements.industry_experience
            )
            
            # Calculate years for this position
            end = exp.end_date if exp.end_date else date.today()
            years = (end - exp.start_date).days / 365.25
            
            # Apply relevance factor
            if industry_relevance:
                total_relevant_years += years
            else:
                total_relevant_years += years * 0.5  # Count non-industry experience at half weight
        
        # Calculate score based on required years
        if total_relevant_years >= requirements.years_experience:
            return 1.0
        else:
            return total_relevant_years / requirements.years_experience

    def _match_education(self, cv: CV, requirements: JobRequirement) -> float:
        """Calculate education match score"""
        if not requirements.education_level:
            return 1.0  # Perfect match if no education requirement
            
        education_levels = {
            "high school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "phd": 5
        }
        
        required_level = 0
        for level, score in education_levels.items():
            if level in requirements.education_level.lower():
                required_level = score
                break
        
        if required_level == 0:
            return 1.0  # Cannot determine required level
            
        # Find highest education level in CV
        cv_level = 0
        for edu in cv.education:
            for level, score in education_levels.items():
                if level in edu.degree.lower():
                    cv_level = max(cv_level, score)
        
        if cv_level >= required_level:
            return 1.0
        else:
            return cv_level / required_level

    def _match_industry(self, cv: CV, requirements: JobRequirement) -> float:
        """Calculate industry match score"""
        if not requirements.industry_experience:
            return 1.0  # Perfect match if no industry requirement
            
        # Get unique industries from CV
        cv_industries = {exp.industry for exp in cv.experience if exp.industry}
        
        # Calculate best match score for each required industry
        total_score = 0.0
        for req_industry in requirements.industry_experience:
            best_score = max(
                (self._calculate_text_similarity(req_industry, cv_ind)
                 for cv_ind in cv_industries),
                default=0.0
            )
            total_score += best_score
        
        return total_score / len(requirements.industry_experience)

    def _match_location(self, cv: CV, job: JobPosting) -> float:
        """Calculate location match score"""
        if not cv.contact.get('address') or not job.location:
            return 0.5  # Neutral score if location information is missing
            
        return self._calculate_text_similarity(
            cv.contact['address'],
            job.location
        )

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        doc1 = self.nlp(text1.lower())
        doc2 = self.nlp(text2.lower())
        return doc1.similarity(doc2)

    def _calculate_skill_score(self, skill_matches: List[SkillMatch]) -> float:
        """Calculate overall skill match score from individual skill matches"""
        if not skill_matches:
            return 0.0
        return sum(match.confidence for match in skill_matches) / len(skill_matches)

    def _generate_match_reasons(
        self, cv: CV, job: JobPosting,
        skill_matches: List[SkillMatch],
        language_score: float,
        experience_score: float,
        education_score: float,
        industry_score: float
    ) -> List[str]:
        """Generate human-readable reasons for the match score"""
        reasons = []
        
        # Skills analysis
        strong_matches = [m for m in skill_matches if m.confidence > 0.9]
        if strong_matches:
            reasons.append(f"Strong match on {len(strong_matches)} key skills: " +
                         ", ".join(m.skill for m in strong_matches[:3]))
        
        # Experience analysis
        if experience_score > 0.8:
            reasons.append("Has sufficient relevant work experience")
        elif experience_score > 0.5:
            reasons.append("Has some relevant work experience, but may need more")
        
        # Education analysis
        if education_score > 0.8:
            reasons.append("Meets or exceeds education requirements")
        
        # Language analysis
        if language_score > 0.8:
            reasons.append("Meets language requirements")
        
        # Industry analysis
        if industry_score > 0.8:
            reasons.append("Has relevant industry experience")
        
        return reasons

    def _generate_recommendations(
        self, cv: CV, job: JobPosting,
        skill_matches: List[SkillMatch],
        language_score: float,
        experience_score: float,
        education_score: float,
        industry_score: float
    ) -> List[str]:
        """Generate recommendations for improving the match"""
        recommendations = []
        
        # Missing skills
        missing_required = set(job.requirements.required_skills) - {m.skill for m in skill_matches}
        if missing_required:
            recommendations.append(f"Develop skills in: {', '.join(missing_required)}")
        
        # Experience gaps
        if experience_score < 0.7:
            recommendations.append(
                "Gain more experience in " +
                ", ".join(job.requirements.industry_experience[:2])
            )
        
        # Language improvements
        if language_score < 0.7:
            missing_languages = [
                lang.name for lang in job.requirements.languages
                if not any(cv_lang.name == lang.name for cv_lang in cv.languages)
            ]
            if missing_languages:
                recommendations.append(f"Consider improving proficiency in: {', '.join(missing_languages)}")
        
        # Education suggestions
        if education_score < 0.7 and job.requirements.education_level:
            recommendations.append(f"Consider pursuing {job.requirements.education_level} degree")
        
        return recommendations

    def parse_cv_from_file(self, cv_path: str | Path) -> CV:
        """Parse a CV from a markdown file"""
        parser = CVParser()
        return parser.parse_markdown_cv(cv_path)
