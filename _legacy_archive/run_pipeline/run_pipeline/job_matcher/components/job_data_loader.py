#!/usr/bin/env python3
"""
Job Data Loader Component
========================

Handles loading and preparing job data from JSON files.
Supports both modern and legacy job data formats.
"""

import os
import json
import sys
from typing import Dict, Any
from pathlib import Path

# Get paths - handle both module and direct execution
try:
    from run_pipeline.config.paths import JOB_DATA_DIR
except ImportError:
    # For direct execution, add project root to path
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from run_pipeline.config.paths import JOB_DATA_DIR


class JobDataLoader:
    """Handles loading and preparing job data"""
    
    @staticmethod
    def load_job_data(job_id: str) -> Dict[str, Any]:
        """
        Load job data from a JSON file.
        
        Args:
            job_id: The job ID to load
            
        Returns:
            A dictionary with the job data
            
        Raises:
            FileNotFoundError: If the job file does not exist
            json.JSONDecodeError: If the job file cannot be parsed as JSON
        """
        job_path = os.path.join(JOB_DATA_DIR, f"job{job_id}.json")
        with open(job_path, "r", encoding="utf-8") as jf:
            return json.load(jf)
    
    @staticmethod
    def prepare_job_description(job_data: Dict[str, Any]) -> str:
        """
        Prepare a job description from job data.
        Supports both beautiful new structure and legacy format.
        
        Args:
            job_data: The job data dictionary
            
        Returns:
            A formatted job description string
        """
        # Check for beautiful new structure first! 🌟
        if "job_content" in job_data:
            job_content = job_data["job_content"]
            job_title = job_content.get("title", "")
            job_description = job_content.get("description", "")
            return f"Position Title: {job_title}\n\n{job_description}"
        
        # Legacy format fallback
        web_details = job_data.get("web_details", {})
        job_title = web_details.get("position_title", "")
        concise_desc = web_details.get("concise_description", "")
        return f"Position Title: {job_title}\n\n{concise_desc}"
    
    @staticmethod
    def extract_job_info(job_data: Dict[str, Any]) -> tuple[str, str]:
        """
        Extract job title and description from job data.
        
        Args:
            job_data: The job data dictionary
            
        Returns:
            Tuple of (job_title, job_description)
        """
        # Check for beautiful new structure first! 🌟
        if "job_content" in job_data:
            job_content = job_data["job_content"]
            job_title = job_content.get("title", "")
            job_description = job_content.get("description", "")
            return job_title, job_description
        
        # Legacy format fallback
        web_details = job_data.get("web_details", {})
        job_title = web_details.get("position_title", "")
        job_description = web_details.get("concise_description", "")
        return job_title, job_description
    
    @staticmethod
    def has_existing_evaluation(job_data: Dict[str, Any]) -> bool:
        """
        Check if job already has LLM evaluation results.
        
        Args:
            job_data: The job data dictionary
            
        Returns:
            True if job has evaluation, False otherwise
        """
        return bool(job_data.get("llama32_evaluation"))
    
    @staticmethod
    def get_evaluation_cache_info(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get cached evaluation information.
        
        Args:
            job_data: The job data dictionary
            
        Returns:
            Dictionary with cached evaluation info
        """
        evaluation = job_data.get("llama32_evaluation", {})
        return {
            "cv_to_role_match": evaluation.get("cv_to_role_match", "Unknown"),
            "from_cache": True,
            "evaluation_date": evaluation.get("evaluation_date", "Unknown")
        }
