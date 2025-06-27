#!/usr/bin/env python3
"""
Job description cleaning module for the job expansion pipeline

This module extracts concise job descriptions from HTML content in job posting JSONs
and updates the original JSONs with the concise descriptions using the StagedJobProcessor.
It provides a more robust approach with language detection, HTML cleaning, and structured extraction.
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

# Import utility modules
from run_pipeline.utils.process_utils import run_process
from run_pipeline.config.paths import (
    PROJECT_ROOT,
    JOB_DATA_DIR,
    DEFAULT_MODEL
)

# Import internal modules
from run_pipeline.core.cleaning_utils import clean_llm_artifacts
from run_pipeline.core.job_analysis import (
    count_placeholder_jobs,
    get_jobs_without_concise_description
)

# Set up logger
logger = logging.getLogger('cleaner_module')

class JobCleaner:
    """
    A class for cleaning and processing job descriptions by extracting concise versions
    from HTML content using LLM models via Ollama.
    """
    
    # Constants for log formatting
    LOG_SEPARATOR = "=" * 80
    
    # Testing mode reference description
    TEST_REFERENCE_DESC = """Associate Engineer (f/m/x) at Deutsche Bank
Location: Frankfurt
Job ID: R0376511
Posted: 2025-04-24

Core Responsibilities:
- Design/build/improve software components (old and new design)
- Build testing (Junit or automation testing)
- Deployment of applications in all environments to production
- Provide on-demand production support
- Bug fixing

Requirements:
- Experience with Java
- Ability to design, build and test components
- Knowledge of technologies like: Apache Camel, SpringBoot, Docker, Git/GitHub/Bitbucket, Eclipse/IntelliJ, Google Cloud, JSE/JMS/MQ, XML/JSON/YAML, DevOps, Kafka, REST, OpenAPI, Jenkins
- DevOps/SRE approach to designing/building applications
- Ability to share information and impart expertise

Contact: Amela Mumanovic: +49 (69) 910 42985"""

    # Prompt template for extraction
    EXTRACTION_PROMPT = """Extract the responsibilities and requirements in English from the given text.     

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

Your response MUST begin with the job title. Any introduction text will be considered an error.

Job posting content:
{job_content}"""

    def __init__(self, default_model: str = "llama3.2:latest", output_dir: Optional[Path] = None):
        """
        Initialize the JobCleaner with a default model and output directory
        
        Args:
            default_model (str): Default LLM model to use
            output_dir (Path): Directory to save extracted descriptions
        """
        self.default_model = default_model
        self.output_dir = output_dir or PROJECT_ROOT / "data" / "test_results" / "concise_extraction"
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_concise_description(self, job_content: str, job_title: str, job_id: str, 
                                   model: Optional[str] = None, save_output: bool = False) -> Optional[str]:
        """
        Extract super concise job description from HTML content using Ollama
        
        Args:
            job_content (str): HTML job content
            job_title (str): Job title
            job_id (str): Job ID
            model (str): Ollama model to use, defaults to self.default_model
            save_output (bool): Whether to save output to a separate file
            
        Returns:
            str: Concise job description or None if extraction failed
        """
        model = model or self.default_model
        logger.info(self.LOG_SEPARATOR)
        logger.info(f"Extracting super concise version for job {job_id} using {model}...")
        
        # For testing we can use a hardcoded response
        if os.environ.get("TEST_MODE") == "1":
            logger.info("Using hardcoded concise description (bypassing Ollama for testing)")
            self._log_concise_description(self.TEST_REFERENCE_DESC)
            return self.TEST_REFERENCE_DESC
        
        # No longer truncate content as per user request
        logger.info(f"Using full job content length: {len(job_content)} characters")

        # Create a specialized prompt for extraction
        prompt = self.EXTRACTION_PROMPT.format(job_content=job_content)

        try:
            # Run Ollama with the prompt for consistent results
            concise_desc = self._run_extraction_model(model, prompt)
            
            if not concise_desc:
                return None
                
            # Calculate compression metrics and log them
            self._calculate_compression_metrics(job_content, concise_desc)
            
            # Clean up any artifacts in the description
            concise_desc = clean_llm_artifacts(concise_desc)
            
            # Save the output to a file for reference only if requested
            if save_output:
                self._save_extraction_output(job_id, concise_desc)
            
            return concise_desc
            
        except Exception as e:
            logger.error(f"Error extracting concise description: {str(e)}")
            return None
    
    def _run_extraction_model(self, model: str, prompt: str) -> Optional[str]:
        """Run the extraction model and return the result"""
        try:
            # Run Ollama with the prompt
            result = subprocess.run(
                ["ollama", "run", model, prompt], 
                capture_output=True, 
                text=True, 
                timeout=120  # 2 minutes timeout
            )
            
            # Check if extraction was successful
            if result.returncode == 0 and result.stdout:
                concise_desc = result.stdout.strip()
                self._log_concise_description(concise_desc)
                return concise_desc
            else:
                logger.error(f"Ollama error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Ollama extraction timed out")
            return None
        except Exception as e:
            logger.error(f"Model execution error: {str(e)}")
            return None
    
    def _log_concise_description(self, description: str) -> None:
        """Log the concise description with formatting"""
        logger.info(self.LOG_SEPARATOR)
        logger.info("SUPER CONCISE JOB DESCRIPTION:")
        logger.info(self.LOG_SEPARATOR)
        logger.info(description)
        logger.info(self.LOG_SEPARATOR)
    
    def _calculate_compression_metrics(self, original_content: str, concise_content: str) -> Dict[str, float]:
        """Calculate and log compression metrics"""
        try:
            html_length = len(original_content)
            clean_length = len(original_content.strip())
            concise_length = len(concise_content)
            
            logger.info(f"Concise description length: {concise_length} characters")
            logger.info(f"Original HTML length: {html_length} characters")
            logger.info(f"Clean description length: {clean_length} characters")
            
            metrics = {}
            metrics["ratio_clean_original"] = round(clean_length / html_length, 2) if html_length > 0 else 0
            metrics["ratio_concise_clean"] = round(concise_length / clean_length, 2) if clean_length > 0 else 0
            metrics["ratio_concise_original"] = round(concise_length / html_length, 2) if html_length > 0 else 0
            
            logger.info(f"Compression ratio (clean/original): {metrics['ratio_clean_original']}")
            logger.info(f"Compression ratio (concise/clean): {metrics['ratio_concise_clean']}")
            logger.info(f"Overall compression ratio (concise/original): {metrics['ratio_concise_original']}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {}
    
    def _save_extraction_output(self, job_id: str, concise_description: Optional[str]) -> None:
        """Save extraction output to a file"""
        if concise_description is None:
            logger.warning(f"Not saving output for job {job_id} as description is None")
            return
            
        try:
            output_file = self.output_dir / f"job{job_id}_concise.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "job_id": job_id, 
                    "concise_description": concise_description,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Output saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving extraction output: {str(e)}")


def extract_concise_description(job_content: str, job_title: str, job_id: str, 
                               model: str = "llama3.2:latest") -> Tuple[Optional[str], str, Optional[str]]:
    """
    Extract super concise job description from HTML content using Ollama
    
    This is a wrapper function for backward compatibility that creates a JobCleaner
    instance and calls its extract_concise_description method.
    
    Args:
        job_content (str): HTML job content
        job_title (str): Job title
        job_id (str): Job ID
        model (str): Ollama model to use
    
    Returns:
        tuple: (description, status, error_message) where:
            - description: Concise job description or None if extraction failed
            - status: "success", "test_mode", or "error"
            - error_message: Error message if status is "error", None otherwise
    """
    try:
        cleaner = get_cleaner_instance(model=model)
        description = cleaner.extract_concise_description(job_content, job_title, job_id, save_output=False)
        
        # Check if we're in test mode
        if os.environ.get("TEST_MODE") == "1":
            return description, "test_mode", None
            
        return description, "success" if description else "error", None if description else "Failed to extract description"
    except Exception as e:
        logger.error(f"Error in extract_concise_description: {str(e)}")
        return None, "error", str(e)

# No need to redefine clean_llm_artifacts here since we're importing it directly

# Import the functions from staged_job_description_processor directly when needed
# job_analysis functions are already imported at the top

def clean_job_descriptions(max_jobs: Optional[int] = None, job_ids: Optional[List[str]] = None, 
                      model: str = DEFAULT_MODEL, log_dir: Optional[Path] = None, only_missing: bool = False,
                      output_format: str = "text") -> bool:
    """
    Clean job descriptions by extracting concise descriptions using the staged job processor.
    
    This function implements a three-stage approach:
    1. HTML cleaning - removes formatting and normalizes whitespace
    2. Language handling - detects language, handles bilingual content, translates if needed
    3. Structured extraction - extracts responsibilities and requirements in a consistent format
    
    Args:
        max_jobs (int): Maximum number of jobs to process
        job_ids (list): Specific job IDs to process
        model (str): Model to use for cleaning
        log_dir (Path): Directory for log files
        only_missing (bool): Only process jobs without concise descriptions
        output_format (str): Format for output ('text' or 'json')
        
    Returns:
        bool: Success status
    """
    logger.info(f"Processing job descriptions using {model} model with staged approach...")
    
    # Set up additional log handler if log_dir is provided
    if log_dir:
        cleaner_log_path = os.path.join(log_dir, "cleaner_module.log")
        cleaner_handler = logging.FileHandler(cleaner_log_path)
        cleaner_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(cleaner_handler)
        logger.info(f"Added log handler. Writing to {cleaner_log_path}")
    
    try:
        # If only_missing is True, get job IDs of jobs without concise descriptions
        if only_missing and not job_ids:
            logger.info("Finding jobs without concise descriptions...")
            # Using the imported function from job_analysis.py
            job_ids = get_jobs_without_concise_description(JOB_DATA_DIR)
            if not job_ids:
                logger.info("No jobs found without concise descriptions. Nothing to do.")
                return True
            logger.info(f"Found {len(job_ids)} jobs without concise descriptions. Job IDs: {job_ids}")
        
        # Process job files using the StagedJobProcessor
        # Use dynamic import to avoid circular dependencies
        import importlib
        staged_processor = importlib.import_module("run_pipeline.utils.staged_processor")
        process_jobs = getattr(staged_processor, "process_jobs")
        processed, success, failure = process_jobs(
            job_ids=job_ids,
            model=model,
            dry_run=False,
            output_format=output_format
        )
        
        # Generate summary report
        logger.info("=" * 50)
        logger.info("Job Description Cleaning Summary")
        logger.info("=" * 50)
        logger.info(f"Total jobs processed: {processed}")
        logger.info(f"Successfully processed: {success}")
        logger.info(f"Failed to process: {failure}")
        logger.info("=" * 50)
        
        # Check for placeholder jobs using the imported function from job_analysis.py
        placeholder_count = count_placeholder_jobs(JOB_DATA_DIR)
        logger.info(f"Jobs still needing valid concise descriptions: {placeholder_count}")
        
        # Consider the operation successful if we processed at least one job successfully
        return success > 0
        
    except Exception as e:
        logger.error(f"Critical error in job description cleaning: {str(e)}")
        return False

def get_cleaner_instance(model: str = DEFAULT_MODEL, output_dir: Optional[Path] = None) -> JobCleaner:
    """
    Get an instance of the JobCleaner class
    
    This function provides a standard way to create a JobCleaner instance,
    which helps avoid circular imports between modules.
    
    Args:
        model (str): The model to use for cleaning
        output_dir (Path): Optional output directory for extracted descriptions
        
    Returns:
        JobCleaner: An instance of the JobCleaner class
    """
    return JobCleaner(default_model=model, output_dir=output_dir)

def get_current_prompt() -> Tuple[str, str]:
    """
    Get the current extraction prompt and version
    
    This function returns the prompt template used for extraction along with its version.
    The version is updated whenever significant changes are made to the prompt.
    
    Returns:
        tuple: (prompt_template, version) where version is a semantic version string
    """
    # Get the prompt from the JobCleaner class
    prompt_template = JobCleaner.EXTRACTION_PROMPT
    
    # Current version is 1.2 for the strict format with explicit structure
    # Update this version string when making significant changes to the prompt
    prompt_version = "1.2"
    
    return prompt_template, prompt_version
