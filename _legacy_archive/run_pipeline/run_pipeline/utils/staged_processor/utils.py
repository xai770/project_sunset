#!/usr/bin/env python3
"""
Common utilities and helper functions for staged job processing
"""

import os
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any

# Set up logging
log_dir = Path("/home/xai/Documents/sunset/logs")
os.makedirs(log_dir, exist_ok=True)
log_file = log_dir / f"staged_job_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)

logger = logging.getLogger('staged_job_processor')

# Language detection patterns
GERMAN_MARKERS = [
    'Wir suchen', 'Ihre Aufgaben', 'Rollenbeschreibung', 'Verantwortlichkeiten',
    'Anforderungen', 'Kenntnisse', 'Abschluss', 'Berufserfahrung', 'Beherrschung'
]

# Job sections markers
ROLE_MARKERS = [
    "Rollenbeschreibung", "Als Senior", "Job Description", "About the Role", 
    "gehört zu Ihren Aufgaben", "Responsibilities", "Verantwortlichkeiten"
]

REQUIREMENT_MARKERS = [
    "Wir suchen", "Requirements", "Anforderungen", "Qualifikationen", 
    "Qualifications", "Skills", "Kenntnisse"
]

# Bilingual content markers
ENGLISH_SECTION_MARKERS = [
    "English version below", 
    "---", 
    "About DWS:", 
    "About Deutsche Bank:",
    "Team / division overview"
]

def clean_llm_artifacts(text: str) -> str:
    """
    Clean common artifacts from LLM-generated text
    
    Args:
        text: Raw LLM output
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Implement directly to avoid circular imports
    # This is a local version of run_pipeline.core.cleaning_utils.clean_llm_artifacts
    # Remove common artifacts in LLM outputs
    cleaned = text
    
    # Remove any markdown code block markers
    cleaned = re.sub(r'```(?:json|python|markdown|md|)?\n?', '', cleaned)
    
    # Remove JSON formatting artifacts
    cleaned = re.sub(r'^(\s*["{}\[\],])+\s*$', '', cleaned, flags=re.MULTILINE)
    
    # Remove any extra newlines at beginning or end
    cleaned = cleaned.strip()
    
    return cleaned
