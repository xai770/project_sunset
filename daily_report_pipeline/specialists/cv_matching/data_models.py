"""
CV Matching Data Models
======================

Data models for CV matching specialist implementation.
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional

class LanguageProficiency(Enum):
    NATIVE = "native"
    FLUENT = "fluent"
    ADVANCED = "advanced"
    INTERMEDIATE = "intermediate"
    BASIC = "basic"

@dataclass
class Language:
    name: str
    proficiency: LanguageProficiency
    spoken: bool = True
    written: bool = True

@dataclass
class Experience:
    company: str
    title: str
    start_date: date
    end_date: Optional[date]
    description: List[str]
    skills: List[str]
    industry: str
    location: Optional[str] = None
    achievements: List[str] = field(default_factory=list)
    is_current: bool = False

@dataclass
class Education:
    institution: str
    degree: str
    field: str
    start_date: date
    end_date: Optional[date]
    achievements: List[str] = field(default_factory=list)
    description: Optional[str] = None

@dataclass
class CV:
    name: str
    contact: Dict[str, str]
    summary: str
    core_competencies: Dict[str, List[str]]
    experience: List[Experience]
    education: List[Education]
    languages: List[Language]
    skills: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    personal_info: Dict[str, str] = field(default_factory=dict)

@dataclass
class JobRequirement:
    required_skills: List[str]
    preferred_skills: List[str]
    years_experience: Optional[int]
    education_level: Optional[str]
    languages: List[Language]
    industry_experience: List[str]
    management_experience: bool = False

@dataclass
class JobPosting:
    title: str
    company: str
    location: str
    description: str
    requirements: JobRequirement
    salary_range: Optional[tuple[float, float]] = None
    posting_date: Optional[date] = None
    employment_type: Optional[str] = None

@dataclass
class SkillMatch:
    skill: str
    confidence: float  # 0.0 to 1.0
    source: str  # e.g., "direct_match", "similar_skill", "inferred"
    years: Optional[float] = None

@dataclass
class MatchResult:
    cv: CV
    job: JobPosting
    overall_score: float
    skill_matches: List[SkillMatch]
    language_match_score: float
    experience_match_score: float
    education_match_score: float
    industry_match_score: float
    location_match_score: float
    reasons: List[str]
    recommendations: List[str]
