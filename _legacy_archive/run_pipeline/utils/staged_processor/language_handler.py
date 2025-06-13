#!/usr/bin/env python3
"""
Language detection and handling for staged job processing
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

# Try to import langdetect
try:
    from langdetect import detect  # type: ignore
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False
    print("Warning: langdetect not installed. Language detection will be limited.")

from run_pipeline.config.paths import JOB_DATA_DIR
from run_pipeline.utils.common_tools import clean_llm_artifacts

from run_pipeline.utils.staged_processor.utils import (
    logger, GERMAN_MARKERS, ROLE_MARKERS, REQUIREMENT_MARKERS, ENGLISH_SECTION_MARKERS
)

def detect_language(text: str) -> str:
    """
    Detect language of text using multiple techniques
    
    Args:
        text: Text to analyze
        
    Returns:
        Language code ('en', 'de', etc.)
    """
    if not text:
        return "en"  # Default to English
        
    # Extract a sample of text to analyze (first 1000 chars + middle section)
    # This helps avoid false positives from small German sections in mostly English text
    sample = text[:1000]
    if len(text) > 2000:
        sample += text[len(text)//2:len(text)//2+1000]
        
    # Count German and English markers
    german_marker_count = 0
    for marker in GERMAN_MARKERS:
        if marker in text:
            german_marker_count += 1
            
    # Only consider it German if multiple markers are found
    if german_marker_count >= 3:
        return "de"
    
    # Use langdetect if available (on the sample)
    if HAS_LANGDETECT:
        try:
            return detect(sample)
        except:
            pass
    
    # Fallback to heuristics
    german_chars = 'äöüßÄÖÜ'
    german_char_count = sum(sample.count(c) for c in german_chars)
    if german_char_count > 10:  # Increased threshold
        return "de"
    
    # Default to English
    return "en"


def split_language_sections(text: str) -> Dict[str, str]:
    """
    Split text into language sections if bilingual
    
    Args:
        text: Potentially bilingual text
        
    Returns:
        Dictionary with language codes as keys and text sections as values
    """
    result = {}
    
    # Check for common English/German section markers
    for marker in ENGLISH_SECTION_MARKERS:
        if marker in text:
            parts = text.split(marker, 1)
            if len(parts) == 2:
                result["de"] = parts[0].strip()
                result["en"] = marker + parts[1].strip()
                return result
    
    # If no clear markers, return empty dict
    return result


def extract_key_job_sections(text: str) -> str:
    """
    Extract key job sections from text for more efficient translation
    
    Args:
        text: Job description text
        
    Returns:
        Text with just the key sections for translation
    """
    # Look for job description and requirements sections
    key_sections = []
    
    # Try to find and extract the job description section
    for marker in ROLE_MARKERS:
        if marker in text:
            start_idx = text.find(marker)
            # Find the next section marker after this one
            next_section = len(text)
            for next_marker in REQUIREMENT_MARKERS:
                if next_marker in text[start_idx:]:
                    next_idx = text[start_idx:].find(next_marker) + start_idx
                    if next_idx < next_section:
                        next_section = next_idx
            
            # Extract text from marker to next section or 1000 chars if too long
            section_text = text[start_idx:min(next_section, start_idx + 1000)]
            key_sections.append(section_text)
            break
    
    # Try to find and extract the requirements section
    for marker in REQUIREMENT_MARKERS:
        if marker in text:
            start_idx = text.find(marker)
            # Extract up to 1000 chars from the requirements
            section_text = text[start_idx:start_idx + 1000]
            key_sections.append(section_text)
            break
    
    # Return combined key sections or empty string if none found
    return "\n\n".join(key_sections)


def translate_text(text: str, source_lang: str, model: str, cleaner) -> Optional[str]:
    """
    Translate text to English using LLM
    
    Args:
        text: Text to translate
        source_lang: Source language code
        model: LLM model to use
        cleaner: Cleaner instance with _run_extraction_model method
        
    Returns:
        Translated text or None if failed
    """
    import re
    
    translation_prompt = f"""Translate the following job description from {source_lang} to English. 
Keep the exact same structure, only translate the text content.
IMPORTANT: Do not add any introductory remarks or explanations. 
Do not include phrases like "Here is the translation" or "I translated".
Just provide the direct translation without any commentary.

Original text:
{text}"""
    
    try:
        # Use the cleaner's extraction model to perform translation
        translated_text = cleaner._run_extraction_model(model, translation_prompt)
        
        # Clean up any artifacts and introductory phrases
        if translated_text and isinstance(translated_text, str):
            translated_text = clean_llm_artifacts(translated_text)
            
            # Remove any translation introductory phrases
            intro_patterns = [
                r'^Here is the (?:translation|translated job description)[:,]?\s*',
                r'^I[\'ve]* translated the (?:text|job description)[:,]?\s*',
                r'^Translation[:,]?\s*',
                r'^Translated (?:text|job description)[:,]?\s*'
            ]
            
            for pattern in intro_patterns:
                if isinstance(translated_text, str):
                    translated_text = re.sub(pattern, '', translated_text, flags=re.IGNORECASE)
            
        return translated_text
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return None


def handle_language(text: str, job_id: str, model: str, cleaner) -> Tuple[str, str]:
    """
    Handle language - identify if text is bilingual, extract or translate as needed
    
    Args:
        text: Text to process
        job_id: Job ID
        model: LLM model to use
        cleaner: Cleaner instance with _run_extraction_model method
        
    Returns:
        Tuple[str, str]: (english_text, original_language)
    """
    # First check if we already have a good concise description
    job_path = Path(JOB_DATA_DIR) / f"job{job_id}.json"
    try:
        with open(job_path, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
            if "web_details" in job_data:
                if "concise_description" in job_data["web_details"]:
                    desc = job_data["web_details"]["concise_description"]
                    if (desc and len(desc) > 500 and 
                        "Responsibilities:" in desc and 
                        "Requirements:" in desc):
                        logger.info(f"Job {job_id} already has a good English description. Using that.")
                        return desc, "en_existing"
    except Exception:
        pass
    
    # Detect language
        print("DEBUG: Found good description, returning it directly...")
    lang = detect_language(text)
    
    # If already English, return as is
    if lang == "en":
        logger.info(f"Job {job_id} content is in English")
        return text, "en"
    
    # Check if text contains both German and English parts
    sections = split_language_sections(text)
    
    if "en" in sections:
        logger.info(f"Job {job_id} contains both German and English text. Using English section.")
        return sections["en"], "bilingual"
    
    # If no English section found but we need just part of the content, extract key sections first
    key_sections = extract_key_job_sections(text)
    if key_sections:
        logger.info(f"Job {job_id} - extracted key sections for translation")
        text_to_translate = key_sections
    else:
        text_to_translate = text
        
    # Translate the content
    logger.info(f"Job {job_id} is in {lang}, preparing for translation")
    translated = translate_text(text_to_translate, lang, model, cleaner)
    if translated:
        return translated, lang
    
    # If translation failed, return original with warning
    logger.warning(f"Translation failed for job {job_id}, using original {lang} text")
    return text, lang
