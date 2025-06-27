#!/usr/bin/env python3
"""
[DEPRECATED] - DO NOT USE - Validate and Improve Job Descriptions

THIS FILE IS DEPRECATED AND SHOULD NOT BE USED.
A new implementation has replaced this module.
This file is kept only for historical reference.

This script validates existing job descriptions and improves them by:
1. Detecting and translating non-English descriptions to English
2. Enforcing proper structural format (Job Title, Responsibilities, Requirements)
3. Removing introductory remarks or unrelated content
4. Optionally providing JSON-structured output

Usage:
  python validate_and_improve_job_descriptions.py [--batch-size BATCH_SIZE] [--model MODEL] [--json-output]

Options:
  --batch-size BATCH_SIZE   Number of jobs to process in each batch (default: 10)
  --model MODEL             Model to use for cleaning (default: llama3.2:latest)
  --json-output             Output job descriptions in structured JSON format
  --dry-run                 Identify and report issues without making changes
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any
import concurrent.futures
import re

try:
    from langdetect import detect  # type: ignore
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False
    print("Warning: langdetect not installed. Language detection will be limited.")
    print("Install with: pip install langdetect")

# Add the project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from run_pipeline.config.paths import (
    PROJECT_ROOT,
    JOB_DATA_DIR
)

from run_pipeline.core.cleaner_module import (
    extract_concise_description,
    clean_llm_artifacts,
    get_cleaner_instance
)

# Set up logging
log_dir = PROJECT_ROOT / "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = log_dir / f"job_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)

logger = logging.getLogger('job_validation')

# Constants for validation
JOB_TITLE_PATTERNS = [
    r'^Job Title:',
    r'^Position:',
    r'^Title:'
]

INTRO_REMARKS_PATTERNS = [
    r'^Das war eine',
    r'^Here is the',
    r'^I have extracted',
    r'^Based on the',
    r'^The following is',
    r'^Following is',
    r'^Below is',
    r'^Here are',
    r'^Here is',
    r'^I\'ve extracted',
    r'^I\'ve formatted',
    r'^I\'ve provided',
    r'^Here is the extracted job information',
    r'^The job information extracted',
    r'^According to the',
    r'^Here\'s the',
    r'^I\'m providing',
    r'^I will provide',
    r'^As requested',
    r'^As per your request',
    r'^After reviewing',
    r'^From the provided',
    r'^Based on my analysis',
    r'^Based on your request',
    r'^Based on the provided text',
    r'^After analyzing'
]

GERMAN_MARKERS = [
    'Wir suchen', 'Ihre Aufgaben', 'Rollenbeschreibung', 'Verantwortlichkeiten',
    'Anforderungen', 'Kenntnisse', 'Abschluss', 'Berufserfahrung', 'Beherrschung'
]

class ValidationResult:
    """Class to store validation results and issues"""
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.issues: List[str] = []
        self.is_valid = True
        self.needs_translation = False
        self.detected_language: Optional[str] = None
        self.has_intro_remarks = False
        self.has_proper_structure = True
        
    def add_issue(self, issue: str):
        self.issues.append(issue)
        self.is_valid = False
    
    def summary(self) -> str:
        """Return a summary of validation results"""
        if self.is_valid:
            return f"Job {self.job_id}: Valid"
        
        return f"Job {self.job_id}: Invalid - {len(self.issues)} issues: {', '.join(self.issues)}"


def detect_language(text: str) -> Optional[str]:
    """
    Detect the language of a text
    
    Args:
        text (str): Text to analyze
        
    Returns:
        Optional[str]: ISO language code (en, de, etc.) or None if detection failed
    """
    if not text:
        return None
    
    # Check for German markers first (more reliable for short job descriptions)
    for marker in GERMAN_MARKERS:
        if marker in text:
            return 'de'
    
    # Use langdetect if available
    if HAS_LANGDETECT:
        try:
            return detect(text)
        except:
            pass
    
    # Fallback: use heuristics
    # Count German-specific characters
    german_chars = 'äöüßÄÖÜ'
    german_char_count = sum(text.count(c) for c in german_chars)
    
    if german_char_count > 5:
        return 'de'
    
    # Default to English if unsure
    return 'en'


def translate_job_description(job_desc: str, source_lang: str, model: str) -> Optional[str]:
    """
    Translate job description to English
    
    Args:
        job_desc (str): Job description text
        source_lang (str): Source language code
        model (str): LLM model to use
        
    Returns:
        Optional[str]: Translated job description or None if translation failed
    """
    cleaner = get_cleaner_instance(model)
    
    # Create a specialized prompt for translation
    translation_prompt = f"""Translate the following job description from {source_lang} to English. 
Keep the exact same structure and format, only translate the text content.
Do NOT add any introductory remarks or explanations. 
Start directly with the job title line.

Original text:
{job_desc}"""
    
    try:
        # Use the cleaner's extraction model to perform translation
        translated_text = cleaner._run_extraction_model(model, translation_prompt)
        
        # Clean up any artifacts
        if translated_text:
            translated_text = clean_llm_artifacts(translated_text)
        
        return translated_text
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return None


def validate_job_description(job_id: str, job_desc: str) -> ValidationResult:
    """
    Validate job description format and content
    
    Args:
        job_id (str): Job ID
        job_desc (str): Job description text
        
    Returns:
        ValidationResult: Validation result with issues
    """
    result = ValidationResult(job_id)
    
    if not job_desc:
        result.add_issue("Empty job description")
        return result
    
    # Check language
    lang = detect_language(job_desc)
    result.detected_language = lang
    
    if lang and lang != 'en':
        result.needs_translation = True
        result.add_issue(f"Non-English content detected (language: {lang})")
    
    # Check for introductory remarks
    first_line = job_desc.strip().split('\n')[0]
    has_intro = any(re.search(pattern, first_line) for pattern in INTRO_REMARKS_PATTERNS)
    
    if has_intro:
        result.has_intro_remarks = True
        result.add_issue("Contains introductory remarks")
    
    # Check for proper job title at start
    has_job_title = any(re.search(pattern, first_line) for pattern in JOB_TITLE_PATTERNS)
    
    if not has_job_title and not has_intro:
        result.has_proper_structure = False
        result.add_issue("Missing proper job title format")
    
    # Check for Responsibilities and Requirements sections
    if "Responsibilities:" not in job_desc and "Duties:" not in job_desc:
        result.has_proper_structure = False
        result.add_issue("Missing Responsibilities section")
    
    if "Requirements:" not in job_desc and "Qualifications:" not in job_desc:
        result.has_proper_structure = False
        result.add_issue("Missing Requirements section")
    
    # Check for unrelated content
    if "Deutsche Bank AG ist eine deutsche Universalbank" in job_desc:
        result.add_issue("Contains unrelated company description instead of job details")
    
    # Check for placeholder content
    if "placeholder for a concise description" in job_desc.lower():
        result.add_issue("Contains placeholder text")
    
    return result


def improve_job_description(job_desc: str, validation: ValidationResult, model: str) -> str:
    """
    Improve job description based on validation results
    
    Args:
        job_desc (str): Original job description
        validation (ValidationResult): Validation results
        model (str): LLM model to use
        
    Returns:
        str: Improved job description
    """
    improved_desc = job_desc
    
    # If needs translation, translate first
    if validation.needs_translation and validation.detected_language:
        logger.info(f"Translating job {validation.job_id} from {validation.detected_language} to English")
        translated = translate_job_description(job_desc, validation.detected_language, model)
        if translated:
            improved_desc = translated
            # Revalidate after translation
            new_validation = validate_job_description(validation.job_id, translated)
            validation = new_validation
        else:
            logger.warning(f"Translation failed for job {validation.job_id}")
    
    # Remove introductory remarks manually if detected
    if validation.has_intro_remarks:
        logger.info(f"Removing introductory remarks from job {validation.job_id}")
        lines = improved_desc.strip().split('\n')
        # Skip any lines until we find one that starts with "Job Title:" or similar patterns
        start_idx = 0
        for i, line in enumerate(lines):
            if any(re.search(pattern, line) for pattern in JOB_TITLE_PATTERNS):
                start_idx = i
                break
        
        # Keep only from the job title onwards
        if start_idx > 0:
            improved_desc = '\n'.join(lines[start_idx:])
            logger.info(f"Removed {start_idx} introductory lines from job description")
        
        # Check for remaining intro remarks even after initial cleaning
        first_line = improved_desc.strip().split('\n')[0]
        intro_prefixes = ["Here is", "Based on", "Below is", "Following", "As requested"]
        if any(first_line.startswith(prefix) for prefix in intro_prefixes):
            # Just use restructuring directly to clean it up
            logger.info("Detected remaining introductory remarks, using restructuring to clean")
            validation.is_valid = False  # Force restructuring below
    
    # If still has issues, use restructuring prompt
    if not validation.is_valid:
        cleaner = get_cleaner_instance(model)
        
        # Create specialized prompt for restructuring
        improvement_prompt = f"""Extract and properly format the job information from the text below.
        
⚠️⚠️⚠️ CRITICAL FORMATTING INSTRUCTIONS - FOLLOW EXACTLY ⚠️⚠️⚠️

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
✅ START DIRECTLY with the job title - no preamble whatsoever
✅ Include ONLY responsibilities and requirements sections
❌ DO NOT include statements on benefits, company culture, etc.
❌ DO NOT add ANY opening remarks or introductions
❌ ABSOLUTELY NO phrases like "Here is", "I've extracted", "Here are" at the beginning

Text to format properly:
{improved_desc}"""

        try:
            # Use extraction model to restructure
            restructured = cleaner._run_extraction_model(model, improvement_prompt)
            
            if restructured:
                cleaned = clean_llm_artifacts(restructured)
                if cleaned:
                    improved_desc = cleaned
        except Exception as e:
            logger.error(f"Restructuring error for job {validation.job_id}: {str(e)}")
    
    return improved_desc


def create_json_structure(job_desc: str) -> Dict[str, Any]:
    """
    Convert job description text to structured JSON
    
    Args:
        job_desc (str): Job description text
        
    Returns:
        dict: Structured job description 
    """
    result = {
        "title": "",
        "responsibilities": [],
        "requirements": []
    }
    
    # Extract title
    title_match = re.search(r'(?:Job Title|Title|Position):\s*(.+?)(?:\n|$)', job_desc)
    if title_match:
        result["title"] = title_match.group(1).strip()
    
    # Extract responsibilities
    resp_section = re.search(r'(?:Responsibilities|Duties):(.*?)(?:Requirements|Qualifications|$)', 
                            job_desc, re.DOTALL)
    if resp_section:
        items = re.findall(r'-\s*(.+?)(?:\n|$)', resp_section.group(1))
        result["responsibilities"] = [item.strip() for item in items if item.strip()]
    
    # Extract requirements
    req_section = re.search(r'(?:Requirements|Qualifications):(.*?)$', job_desc, re.DOTALL)
    if req_section:
        items = re.findall(r'-\s*(.+?)(?:\n|$)', req_section.group(1))
        result["requirements"] = [item.strip() for item in items if item.strip()]
    
    return result


def process_jobs(job_ids: Optional[List[str]] = None, batch_size: int = 10, 
                model: str = "llama3.2:latest", json_output: bool = False,
                dry_run: bool = False) -> Tuple[int, int, int]:
    """
    Process jobs to validate and improve descriptions
    
    Args:
        job_ids (list): Specific job IDs to process, or None for all
        batch_size (int): Number of jobs to process in each batch
        model (str): LLM model to use
        json_output (bool): Output in JSON format
        dry_run (bool): Only identify issues without making changes
        
    Returns:
        tuple: (processed_count, success_count, failure_count)
    """
    job_dir = Path(JOB_DATA_DIR)
    
    # Get job files
    if job_ids:
        job_files = []
        for job_id in job_ids:
            job_file = f"job{job_id}.json"
            if (job_dir / job_file).exists():
                job_files.append(job_file)
            else:
                logger.warning(f"Job file not found: {job_file}")
    else:
        job_files = sorted([f for f in os.listdir(job_dir) 
                   if f.startswith('job') and f.endswith('.json')])
    
    logger.info(f"Validating {len(job_files)} job files")
    
    # Process counters
    processed = 0
    success = 0
    failure = 0
    
    # Process in batches
    for i in range(0, len(job_files), batch_size):
        batch = job_files[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} jobs")
        
        for job_file in batch:
            job_id = job_file.replace('job', '').replace('.json', '')
            job_path = job_dir / job_file
            
            logger.info(f"Validating job ID {job_id} ({processed+1} of {len(job_files)})")
            
            try:
                # Read job data
                with open(job_path, 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                
                # Skip if no web_details
                if 'web_details' not in job_data:
                    logger.warning(f"Job {job_id} has no web_details, skipping")
                    processed += 1
                    failure += 1
                    continue
                
                # Get concise description
                concise_desc = job_data['web_details'].get('concise_description')
                if not concise_desc:
                    logger.warning(f"Job {job_id} has no concise description, skipping")
                    processed += 1
                    failure += 1
                    continue
                
                # Validate job description
                validation = validate_job_description(job_id, concise_desc)
                
                if validation.is_valid:
                    logger.info(f"Job {job_id} passed validation")
                    
                    # Convert to JSON if requested
                    if json_output and not dry_run:
                        json_structure = create_json_structure(concise_desc)
                        job_data['web_details']['structured_description'] = json_structure
                        logger.info(f"Added structured description to job {job_id}")
                        
                        # Save changes
                        with open(job_path, 'w', encoding='utf-8') as f:
                            json.dump(job_data, f, indent=2, ensure_ascii=False)
                    
                    success += 1
                else:
                    # Log validation issues
                    logger.warning(validation.summary())
                    
                    if not dry_run:
                        # Improve job description
                        logger.info(f"Improving job description for job {job_id}")
                        improved_desc = improve_job_description(concise_desc, validation, model)
                        
                        if improved_desc and improved_desc != concise_desc:
                            # Add improved description
                            job_data['web_details']['concise_description'] = improved_desc
                            
                            # Update metadata
                            if 'description_metadata' in job_data['web_details']:
                                job_data['web_details']['description_metadata'].update({
                                    "timestamp": datetime.now().isoformat(),
                                    "model_used": model,
                                    "is_placeholder": False,
                                    "extraction_status": "improved",
                                    "prompt_version": "1.2-improved"  # Mark as improved version
                                })
                            
                            # Add to log
                            if 'log' not in job_data:
                                job_data['log'] = []
                            
                            job_data['log'].append({
                                "timestamp": datetime.now().isoformat(),
                                "script": "run_pipeline.utils.validate_and_improve_job_descriptions",
                                "action": "improve_job_description",
                                "message": f"Improved job description for job ID {job_id}"
                            })
                            
                            # Add JSON structure if requested
                            if json_output:
                                json_structure = create_json_structure(improved_desc)
                                job_data['web_details']['structured_description'] = json_structure
                                logger.info(f"Added structured description to job {job_id}")
                            
                            # Save changes
                            with open(job_path, 'w', encoding='utf-8') as f:
                                json.dump(job_data, f, indent=2, ensure_ascii=False)
                            
                            logger.info(f"Updated job {job_id} with improved description")
                            success += 1
                        else:
                            logger.warning(f"Failed to improve job description for job {job_id}")
                            failure += 1
                    else:
                        # Count as success in dry run if we identified issues
                        success += 1
            
            except Exception as e:
                logger.error(f"Error processing job {job_id}: {str(e)}")
                failure += 1
            
            processed += 1
            
        # Small delay between batches
        if i + batch_size < len(job_files):
            time.sleep(1)
    
    logger.info(f"Processing complete. Total: {processed}, Success: {success}, Failure: {failure}")
    return (processed, success, failure)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Validate and improve job descriptions"
    )
    parser.add_argument(
        "--batch-size", 
        type=int, 
        default=10, 
        help="Number of jobs to process in each batch"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        default="llama3.2:latest", 
        help="Model to use for cleaning"
    )
    parser.add_argument(
        "--job-ids", 
        type=str,
        help="Comma-separated list of job IDs to process"
    )
    parser.add_argument(
        "--json-output", 
        action="store_true", 
        help="Output job descriptions in structured JSON format"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Identify and report issues without making changes"
    )
    
    args = parser.parse_args()
    
    # Convert job IDs string to list if provided
    job_ids = None
    if args.job_ids:
        job_ids = args.job_ids.split(',')
    
    logger.info(f"Starting job description validation with model {args.model}")
    if args.dry_run:
        logger.info("Dry run mode: No changes will be made")
    
    processed, success, failure = process_jobs(
        job_ids=job_ids,
        batch_size=args.batch_size,
        model=args.model,
        json_output=args.json_output,
        dry_run=args.dry_run
    )
    
    logger.info(f"Job validation summary:")
    logger.info(f"- Total jobs processed: {processed}")
    logger.info(f"- Successfully validated/improved: {success}")
    logger.info(f"- Failed to process: {failure}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
