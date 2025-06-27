#!/usr/bin/env python3
"""
Text extraction and JSON conversion for staged job processing
"""

import re
import json
import logging
from typing import Dict, Optional, Any

# Use local utility functions to avoid circular imports
from run_pipeline.utils.staged_processor.utils import (
    logger, ROLE_MARKERS, REQUIREMENT_MARKERS, clean_llm_artifacts
)

def extract_job_details(text: str, job_id: str, output_format: str, model: str, cleaner) -> Optional[str]:
    """
    Extract structured job details using LLM
    
    Args:
        text: Text to extract from
        job_id: Job ID
        output_format: Output format ('text' or 'json')
        model: LLM model to use
        cleaner: Cleaner instance with _run_extraction_model method
        
    Returns:
        Structured job details or None if failed
    """
    # Look for existing job details sections
    role_desc_markers = ROLE_MARKERS
    req_markers = REQUIREMENT_MARKERS
    
    # Try to first locate the sections with actual job details
    text_to_use = text
    for marker in role_desc_markers:
        if marker in text:
            # Get text from this point onwards, which likely contains the actual job details
            text_to_use = text[text.find(marker):]
            logger.info(f"Found job details marker: '{marker}', focusing on this section")
            break
    
    # Extract position title from the beginning of the text
    position_title = ""
    title_match = re.search(r'<h1>\s*([^<]+)\s*</h1>', text)
    if title_match:
        position_title = title_match.group(1).strip()
    
    # Create a specialized prompt for extraction
    extraction_prompt = f"""Extract the job title, responsibilities and requirements from the job description text below.
If the text is in German, translate it to English first.

!!! CRITICAL FORMATTING INSTRUCTIONS - FOLLOW EXACTLY !!!

OUTPUT FORMAT:
Job Title: [Title]

Responsibilities:
- [Responsibility 1]
- [Responsibility 2]
...

Requirements:
- [Requirement 1]
- [Requirement 2]
...

RULES:
- START DIRECTLY with the job title - no preamble whatsoever
- Include ONLY responsibilities and requirements sections
- Make sure to extract ALL responsibilities and requirements 
- DO NOT include statements on benefits, company culture, etc.
- DO NOT add ANY opening remarks or introductions
- NO "Here is the extracted job information" or similar phrases
- NO "I have identified the following" or similar phrases
- ABSOLUTELY NO phrases like "Here is", "I've extracted", "Here are" at the beginning

Job description text:
{text_to_use}"""

    try:
        # Use extraction model
        extracted_text = cleaner._run_extraction_model(model, extraction_prompt)
        
        if not extracted_text:
            logger.warning(f"Failed to extract job details from text")
            return None
            
        # Clean up any artifacts
        cleaned = clean_llm_artifacts(extracted_text)
        
        # Check if we got actual content with responsibilities and requirements
        if cleaned and ("Responsibilities:" not in cleaned or "Requirements:" not in cleaned):
            logger.warning(f"Extraction missing key sections. Retrying with full text...")
            
            # Retry with the full text as a fallback
            fallback_prompt = f"""Extract the responsibilities and requirements from the job description below.
The text may be in German, translate to English if needed.

OUTPUT FORMAT:
Job Title: [Title]

Responsibilities:
- [Responsibility 1]
- [Responsibility 2]
...

Requirements:
- [Requirement 1]
- [Requirement 2]
...

Job description:
{text}"""
            
            retry_text = cleaner._run_extraction_model(model, fallback_prompt)
            if retry_text and isinstance(retry_text, str) and "Responsibilities:" in retry_text and "Requirements:" in retry_text:
                cleaned = clean_llm_artifacts(retry_text)
        
        # Convert to JSON if requested
        if cleaned is not None:
            if output_format == "json":
                return convert_to_json(cleaned)
            return cleaned
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting job details: {str(e)}")
        return None


def convert_to_json(text: str) -> str:
    """
    Convert formatted job description to JSON string
    
    Args:
        text: Formatted job description text
        
    Returns:
        JSON string representation
    """
    result = {
        "title": "",
        "responsibilities": [],
        "requirements": []
    }
    
    # Extract title - enhanced with better handling when title might be missing
    title_match = re.search(r'(?:Job Title|Title|Position):\s*(.+?)(?:\n|$)', text)
    if title_match:
        result["title"] = title_match.group(1).strip()
    else:
        # If no title found in the format, try to extract from the first line
        first_line = text.split("\n")[0].strip()
        if first_line and "Responsibilities:" not in first_line and "Requirements:" not in first_line:
            result["title"] = first_line
    
    # Ensure we have a title - use fallback if none found
    if not result["title"]:
        result["title"] = "Professional Specialist"  # Generic fallback title
    
    # Extract responsibilities
    resp_section = re.search(r'(?:Responsibilities|Duties):(.*?)(?:Requirements|Qualifications|$)', text, re.DOTALL)
    if resp_section:
        items = re.findall(r'-\s*(.+?)(?:\n|$)', resp_section.group(1))
        result["responsibilities"] = [item.strip() for item in items if item.strip()]
    
    # Extract requirements
    req_section = re.search(r'(?:Requirements|Qualifications):(.*?)$', text, re.DOTALL)
    if req_section:
        items = re.findall(r'-\s*(.+?)(?:\n|$)', req_section.group(1))
        result["requirements"] = [item.strip() for item in items if item.strip()]
    
    return json.dumps(result, indent=2)
