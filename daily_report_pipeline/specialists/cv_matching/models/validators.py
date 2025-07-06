"""
Validators for CV Matching Models
"""

from dataclasses import dataclass
from typing import Any, List, Optional
import re
from datetime import datetime

def validate_confidence_score(score: float) -> bool:
    """Validate that a confidence score is between 0.0 and 1.0"""
    return isinstance(score, (int, float)) and 0.0 <= float(score) <= 1.0

def validate_date_string(date_str: str) -> bool:
    """Validate date string format (YYYY-MM-DD or YYYY-MM)"""
    if date_str.lower() == 'present':
        return True
        
    patterns = [
        r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        r'^\d{4}-\d{2}$',        # YYYY-MM
        r'^\d{4}$'               # YYYY
    ]
    
    return any(re.match(pattern, date_str) for pattern in patterns)

def validate_experience_entry(experience: dict) -> List[str]:
    """Validate an experience entry"""
    errors = []
    
    required_fields = ['title', 'start_date']
    for field in required_fields:
        if field not in experience:
            errors.append(f"Missing required field: {field}")
            
    # Validate dates
    if 'start_date' in experience and not validate_date_string(experience['start_date']):
        errors.append("Invalid start_date format")
    
    if 'end_date' in experience and not validate_date_string(experience['end_date']):
        errors.append("Invalid end_date format")
        
    return errors

def validate_skill_entry(skill: dict) -> List[str]:
    """Validate a skill entry"""
    errors = []
    
    if 'years_experience' in skill:
        try:
            years = float(skill['years_experience'])
            if years < 0:
                errors.append("years_experience cannot be negative")
        except (ValueError, TypeError):
            errors.append("Invalid years_experience value")
            
    if 'proficiency' in skill:
        valid_levels = {'beginner', 'intermediate', 'advanced', 'expert'}
        if skill['proficiency'].lower() not in valid_levels:
            errors.append("Invalid proficiency level")
            
    return errors
