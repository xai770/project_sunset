"""
CV Matching Specialist Tests
===========================

Comprehensive test suite for the CV matching specialist and its components.
"""

import pytest
from typing import Dict, Any
from ..cv_matching_specialist import CVMatchingSpecialist
from ..models.matching_result import CVMatchResult, SkillsMatchResult
from ..analyzers.skills_analyzer import SkillsAnalyzer
from ..analyzers.experience_analyzer import ExperienceAnalyzer
from ..analyzers.domain_analyzer import DomainAnalyzer

# Test Data
@pytest.fixture
def sample_cv_data() -> Dict[str, Any]:
    return {
        "skills": {
            "python": {
                "years_experience": 5,
                "last_used": "current",
                "proficiency": "expert",
                "projects": ["ML Pipeline", "Data Analysis"]
            },
            "machine_learning": {
                "years_experience": 3,
                "last_used": "current",
                "proficiency": "advanced"
            }
        },
        "experience": [
            {
                "title": "Senior Data Scientist",
                "company": "AI Corp",
                "industry": "technology",
                "start_date": "2020-01",
                "end_date": "present",
                "skills": ["python", "machine_learning", "deep_learning"]
            }
        ],
        "profile": {
            "industries": ["technology", "research"]
        }
    }

@pytest.fixture
def sample_job_data() -> Dict[str, Any]:
    return {
        "title": "Machine Learning Engineer",
        "industry": "technology",
        "requirements": {
            "python": {
                "required": True,
                "years_experience": 3,
                "proficiency": "advanced"
            },
            "machine_learning": {
                "required": True,
                "years_experience": 2,
                "proficiency": "intermediate"
            }
        },
        "domain_specific_skills": ["deep_learning", "neural_networks"]
    }

class TestCVMatchingSpecialist:
    def test_initialization(self):
        specialist = CVMatchingSpecialist()
        assert specialist is not None
        assert specialist.specialist_name == "CV Matching Specialist"
        
    def test_successful_match(self, sample_cv_data, sample_job_data):
        specialist = CVMatchingSpecialist()
        result = specialist.match_cv_to_job(sample_cv_data, sample_job_data)
        
        assert isinstance(result, CVMatchResult)
        assert not result.has_error
        assert result.confidence > 0.7  # Should be a strong match
        
    def test_error_handling(self):
        specialist = CVMatchingSpecialist()
        result = specialist.match_cv_to_job({}, {})
        
        assert result.has_error
        assert result.confidence == 0.0

class TestSkillsAnalyzer:
    def test_direct_skill_match(self, sample_cv_data, sample_job_data):
        analyzer = SkillsAnalyzer()
        result = analyzer.analyze(sample_cv_data, sample_job_data)
        
        assert isinstance(result, SkillsMatchResult)
        assert "python" in result.required_skills_matched
        assert result.confidence > 0.8
        
    def test_equivalent_skills(self):
        analyzer = SkillsAnalyzer()
        cv_data = {
            "skills": {
                "programming": {"years_experience": 5}
            }
        }
        job_data = {
            "requirements": {
                "software development": {"required": True}
            }
        }
        
        result = analyzer.analyze(cv_data, job_data)
        assert result.confidence > 0.0  # Should recognize equivalent skill

class TestExperienceAnalyzer:
    def test_years_match(self, sample_cv_data, sample_job_data):
        analyzer = ExperienceAnalyzer()
        result = analyzer.analyze(sample_cv_data, sample_job_data)
        
        assert result.years_match
        assert result.confidence > 0.7
        
    def test_role_progression(self):
        analyzer = ExperienceAnalyzer()
        cv_data = {
            "experience": [
                {
                    "title": "Senior Developer",
                    "start_date": "2020-01",
                    "end_date": "present"
                }
            ]
        }
        job_data = {
            "title": "Lead Developer"
        }
        
        result = analyzer.analyze(cv_data, job_data)
        assert result.role_level_match  # Should recognize valid progression

class TestDomainAnalyzer:
    def test_industry_match(self, sample_cv_data, sample_job_data):
        analyzer = DomainAnalyzer()
        result = analyzer.analyze_domain(sample_cv_data, sample_job_data)
        
        assert result.industry_match
        assert "technology" in result.domain_expertise
        
    def test_transferable_domains(self):
        analyzer = DomainAnalyzer()
        cv_data = {
            "profile": {
                "industries": ["fintech"]
            }
        }
        job_data = {
            "industry": "finance"
        }
        
        result = analyzer.analyze(cv_data, job_data)
        assert result.match_level > 0.5  # Should recognize related domains
