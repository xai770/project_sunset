#!/usr/bin/env python3
"""
Data Models for Daily Report Pipeline
Professional dataclasses for specialist results
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

# Import enhanced requirements types
try:
    from ..specialists.enhanced_requirements_extraction import FiveDimensionalRequirements
except ImportError:
    FiveDimensionalRequirements = None

@dataclass
class ContentExtractionResult:
    """Result from content extraction specialist"""
    specialist_id: str = "content_extraction_v3_4"
    technical_skills: List[str] = None  #type: ignore  
    soft_skills: List[str] = None  #type: ignore
    business_skills: List[str] = None  #type: ignore
    all_skills: List[str] = None  #type: ignore
    processing_time: float = 0.0
    accuracy_confidence: str = "production_validated"
    format_compliance: bool = True
    
    # NEW: Enhanced 5D requirements data
    enhanced_requirements: Optional[Any] = None

@dataclass
class LocationValidationResult:
    """Result from location validation specialist"""
    specialist_id: str = "location_validation"
    metadata_location_accurate: bool = False
    authoritative_location: str = ""
    conflict_detected: bool = False
    confidence_score: float = 0.0
    analysis_details: Dict[str, Any] = None  #type: ignore
    processing_time: float = 0.0

@dataclass
class SummarizationResult:
    """Result from text summarization specialist"""
    specialist_id: str = "text_summarization"
    original_text: str = ""
    summary: str = ""
    original_length: int = 0
    summary_length: int = 0
    compression_ratio: float = 0.0
    processing_time: float = 0.0
