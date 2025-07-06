"""
CV Match Result Data Model
=========================

Structured data model for CV matching results with confidence scoring
and detailed match analysis.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from .json_serialization import JSONSerializationMixin
from .validators import validate_confidence_score

@dataclass
class SkillsMatchResult(JSONSerializationMixin):
    """Results of skills matching analysis"""
    required_skills_matched: List[str] = field(default_factory=list)
    additional_relevant_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def __post_init__(self):
        """Validate the confidence score"""
        if not validate_confidence_score(self.confidence):
            raise ValueError("Confidence score must be between 0.0 and 1.0")
    
@dataclass
class ExperienceMatchResult(JSONSerializationMixin):
    """Results of experience matching analysis"""
    years_match: bool = False
    role_level_match: bool = False
    relevant_roles: List[str] = field(default_factory=list)
    transferable_experience: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def __post_init__(self):
        """Validate the confidence score"""
        if not validate_confidence_score(self.confidence):
            raise ValueError("Confidence score must be between 0.0 and 1.0")
    
@dataclass
class DomainMatchResult(JSONSerializationMixin):
    """Results of domain/industry matching analysis"""
    industry_match: bool = False
    domain_expertise: List[str] = field(default_factory=list)
    relevant_context: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def __post_init__(self):
        """Validate the confidence score"""
        if not validate_confidence_score(self.confidence):
            raise ValueError("Confidence score must be between 0.0 and 1.0")

@dataclass
class CVMatchResult(JSONSerializationMixin):
    """Complete results of CV to job matching analysis"""
    cv_data: Dict[str, Any]
    job_data: Dict[str, Any]
    skills_match: SkillsMatchResult = field(default_factory=SkillsMatchResult)
    experience_match: ExperienceMatchResult = field(default_factory=ExperienceMatchResult)
    domain_match: DomainMatchResult = field(default_factory=DomainMatchResult)
    error_message: Optional[str] = None
    match_explanation: Optional[str] = None
    
    @property
    def confidence(self) -> float:
        """Calculate overall match confidence"""
        if self.error_message:
            return 0.0
            
        # Weight the different aspects
        weights = {
            'skills': 0.4,
            'experience': 0.4,
            'domain': 0.2
        }
        
        confidence = (
            self.skills_match.confidence * weights['skills'] +
            self.experience_match.confidence * weights['experience'] +
            self.domain_match.confidence * weights['domain']
        )
        
        if not validate_confidence_score(confidence):
            raise ValueError("Invalid confidence score calculated")
            
        return confidence
    
    @property
    def is_strong_match(self) -> bool:
        """Determine if this is a strong match (>= 0.8 confidence)"""
        return self.confidence >= 0.8 and not self.error_message
    
    @property
    def has_error(self) -> bool:
        """Check if there was an error in match analysis"""
        return bool(self.error_message)
    
    def generate_match_explanation(self) -> str:
        """Generate a human-readable explanation of the match result"""
        if self.error_message:
            return f"Error in match analysis: {self.error_message}"
            
        explanation = []
        
        # Add skills analysis
        if self.skills_match.required_skills_matched:
            explanation.append("Required skills matched: " + 
                            ", ".join(self.skills_match.required_skills_matched))
        if self.skills_match.missing_skills:
            explanation.append("Missing required skills: " + 
                            ", ".join(self.skills_match.missing_skills))
            
        # Add experience analysis
        if self.experience_match.years_match:
            explanation.append("Years of experience requirement met")
        if self.experience_match.relevant_roles:
            explanation.append("Relevant previous roles: " + 
                            ", ".join(self.experience_match.relevant_roles[:3]))
            
        # Add domain analysis
        if self.domain_match.industry_match:
            explanation.append("Industry experience matches")
        if self.domain_match.domain_expertise:
            explanation.append("Relevant domain expertise: " + 
                            ", ".join(self.domain_match.domain_expertise))
            
        # Add overall assessment
        if self.is_strong_match:
            explanation.append("Overall: Strong match")
        elif self.confidence > 0.6:
            explanation.append("Overall: Good match with some gaps")
        else:
            explanation.append("Overall: Significant gaps exist")
            
        return "\n".join(explanation)
    
    @classmethod
    def create_error_result(cls, cv_data: Dict[str, Any], job_data: Dict[str, Any], 
                          error_message: str) -> 'CVMatchResult':
        """Create a CVMatchResult indicating an error"""
        return cls(
            cv_data=cv_data,
            job_data=job_data,
            error_message=error_message,
            match_explanation=f"Error in match analysis: {error_message}"
        )
