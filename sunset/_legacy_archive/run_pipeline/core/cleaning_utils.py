#!/usr/bin/env python3
"""
Utilities for cleaning job description text extracted by LLM models

This module provides helper functions for processing and cleaning text from
LLM outputs, specifically for job description extraction tasks.
"""

import logging
from typing import Optional

logger = logging.getLogger('cleaner_module.utils')

def clean_llm_artifacts(text: Optional[str]) -> Optional[str]:
    """
    Clean up common LLM artifacts from extracted job descriptions
    
    Args:
        text (str): Raw text from LLM
        
    Returns:
        str: Cleaned text without artifacts
    """
    if not text:
        return text
        
    # Common artifacts to remove from the beginning
    start_artifacts = [
        "Here is the extracted job information in the requested format:",
        "Here is the job information extracted from the provided content:",
        "Here is the job posting information:",
        "Here's the extracted job information:",
        "I've extracted the job details as requested:",
        "Based on the provided HTML content, here is the extracted job information:",
        "Job Posting Content:",
        "Here is the essential information from the job description:",
        "Here is the cleaned job description:",
        "---",
    ]
    
    # Common artifacts to remove from the end
    end_artifacts = [
        "---",
        "I hope this helps!",
        "Let me know if you need anything else.",
        "Does this look good?",
        "Is there anything else you'd like me to extract?",
        "Is this format suitable for your needs?",
    ]
    
    # Clean up the text
    cleaned_text = text.strip()
    
    # Remove artifacts from start of text
    for artifact in start_artifacts:
        if cleaned_text.lower().startswith(artifact.lower()):
            cleaned_text = cleaned_text[len(artifact):].strip()
    
    # Remove artifacts from end of text
    for artifact in end_artifacts:
        if cleaned_text.lower().endswith(artifact.lower()):
            cleaned_text = cleaned_text[:-len(artifact)].strip()
    
    # Remove any question sections that might appear at the end
    question_indicators = [
        "What specific skills",
        "How does the job",
        "Can you elaborate",
        "What are the key",
        "Could you explain",
        "Would you please",
    ]
    
    for indicator in question_indicators:
        index = cleaned_text.find(indicator)
        if index > 0:
            cleaned_text = cleaned_text[:index].strip()
    
    # Remove any trailing "---" or "===" separators
    while cleaned_text.endswith("---") or cleaned_text.endswith("==="):
        cleaned_text = cleaned_text[:-3].strip()
        
    return cleaned_text
