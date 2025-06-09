#!/usr/bin/env python3
"""
Response Parser module for job matching.

This module handles the extraction and parsing of different elements
from the LLM response, such as match level, domain knowledge assessment,
and application narratives or no-go rationales.
"""
import re
from typing import Tuple, Optional

def extract_match_level(response: str) -> Optional[str]:
    """
    Extract the match level from the LLM response.
    
    Args:
        response: The LLM response text
        
    Returns:
        The extracted match level ("Low", "Moderate", "Good") or None if not found
    """
    # Try standard format first
    match = re.search(r"\*\*CV-to-role match:\*\* (Low|Moderate|Good) match", response)
    if match:
        return match.group(1)
    
    # Try alternative formats
    match = re.search(r"\*\*CV-to-role match:\*\*\s*(Low|Moderate|Good)", response)
    if match:
        return match.group(1)
        
    match = re.search(r"CV-to-role match:\s*(Low|Moderate|Good)", response)
    if match:
        return match.group(1)
    
    match = re.search(r"The CV-to-role match level is \*\*(Low|Moderate|Good) match\*\*", response)
    if match:
        return match.group(1)
    
    match = re.search(r"match level is \*\*(Low|Moderate|Good)\*\*", response)
    if match:
        return match.group(1)
        
    # Look for any mention of the match level
    if "Low match" in response:
        return "Low"
    elif "Moderate match" in response:
        return "Moderate"
    elif "Good match" in response:
        return "Good"
        
    return None

def get_lowest_match(match_levels: list[str]) -> Optional[str]:
    """
    Get the lowest match level from a list of match levels.
    
    Args:
        match_levels: List of match levels
        
    Returns:
        The lowest match level or None if the list is empty
    """
    if "Low" in match_levels:
        return "Low"
    elif "Moderate" in match_levels:
        return "Moderate"
    elif "Good" in match_levels:
        return "Good"
    return None

def extract_domain_knowledge_assessment(response: str) -> Optional[str]:
    """
    Extract the domain knowledge assessment from the response.
    
    Args:
        response: The LLM response text
        
    Returns:
        The extracted domain knowledge assessment or None if not found
    """
    patterns = [
        r"\*\*Domain knowledge assessment:\*\*\s*(.*?)(?:\n\n|\Z|\*\*Application|\*\*No-go|\*\*CV-to-role)",
        r"\*\*Domain knowledge assessment:\*\*(.+?)(?=\n\n|\Z|\*\*Application|\*\*No-go|\*\*CV-to-role)",
        r"Domain knowledge assessment:\s*(.*?)(?:\n\n|\Z|Application|No-go|CV-to-role)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    return None

def extract_narrative_or_rationale(response: str, match_level: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract the application narrative or no-go rationale from the response.
    
    Args:
        response: The LLM response text
        match_level: The match level ("Low", "Moderate", "Good")
        
    Returns:
        A tuple of (field_type, content) where field_type is either "Application narrative"
        or "No-go rationale", and content is the extracted text
    """
    if match_level == "Good":
        match = re.search(r"\*\*Application narrative:\*\*\s*(.*?)(?:\n\n|\Z|\*\*No-go|\*\*CV-to-role|\*\*Domain)", response, re.DOTALL)
        if match:
            return "Application narrative", match.group(1).strip()
        # Fallback for different formatting
        match = re.search(r"\*\*Application narrative:\*\*(.+?)(?=\n\n|\Z|\*\*No-go|\*\*CV-to-role|\*\*Domain)", response, re.DOTALL)
        if match:
            return "Application narrative", match.group(1).strip()
        
        # Try additional formats
        match = re.search(r"Application narrative:\s*(.*?)(?:\n\n|\Z|No-go|CV-to-role|Domain)", response, re.DOTALL)
        if match:
            return "Application narrative", match.group(1).strip()
    else:
        match = re.search(r"\*\*No-go rationale:\*\*\s*(.*?)(?:\n\n|\Z|\*\*Application|\*\*CV-to-role|\*\*Domain)", response, re.DOTALL)
        if match:
            return "No-go rationale", match.group(1).strip()
        # Fallback for different formatting
        match = re.search(r"\*\*No-go rationale:\*\*(.+?)(?=\n\n|\Z|\*\*Application|\*\*CV-to-role|\*\*Domain)", response, re.DOTALL)
        if match:
            return "No-go rationale", match.group(1).strip()
        
        # Try additional formats
        match = re.search(r"No-go rationale:\s*(.*?)(?:\n\n|\Z|Application|CV-to-role|Domain)", response, re.DOTALL)
        if match:
            return "No-go rationale", match.group(1).strip()
        
        match = re.search(r"No go rationale:\s*(.*?)(?:\n\n|\Z|Application|CV-to-role|Domain)", response, re.DOTALL)  
        if match:
            return "No-go rationale", match.group(1).strip()
        
        # Special case: If we can't find a No-go rationale but there is an Application narrative
        # (this shouldn't happen according to the prompt, but LLMs sometimes make mistakes)
        if match_level in ["Low", "Moderate"]:
            match = re.search(r"\*\*Application narrative:\*\*\s*(.*?)(?:\n\n|\Z|\*\*No-go|\*\*CV-to-role|\*\*Domain)", response, re.DOTALL)
            if match:
                narrative = match.group(1).strip()
                return "No-go rationale", f"I have compared my CV and the role description and decided not to apply due to the following reasons: [Extracted from incorrectly formatted narrative: {narrative}]"
            
            match = re.search(r"Application narrative:\s*(.*?)(?:\n\n|\Z|No-go|CV-to-role|Domain)", response, re.DOTALL)
            if match:
                narrative = match.group(1).strip()
                return "No-go rationale", f"I have compared my CV and the role description and decided not to apply due to the following reasons: [Extracted from incorrectly formatted narrative: {narrative}]"
    
    # If no content found, try to extract reasons from analysis text
    if match_level in ["Low", "Moderate"]:
        # Look for explanation text in the analysis section
        patterns = [
            r"decided not to apply due to\s*(.+?)(?=\n\n|\Z)",
            r"due to the lack of\s*(.+?)(?=\n\n|\Z)",
            r"due to\s*(.+?)(?=\n\n|\Z)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                return "No-go rationale", f"I have compared my CV and the role description and decided not to apply due to the following reasons: {match.group(1).strip()}"
    
    # If no content found, provide a default explanation
    if match_level == "Good":
        return "Application narrative", "No specific narrative was provided by the LLM, but the match was rated as Good."
    else:
        return "No-go rationale", "I have compared my CV and the role description and decided not to apply, but no specific reasons were provided by the LLM."
