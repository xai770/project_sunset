#!/usr/bin/env python3
"""
LLM interaction functions for bucketed skill matching
"""

import os
import re
import logging
import requests
from typing import Dict, List, Any
from run_pipeline.skill_matching.bucketed_utils import extract_percentage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucketed_llm")

# Ollama settings
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")

def compare_skill_buckets_llm(bucket_name: str, job_skills: List[str], cv_skills: List[str], bucket_cache=None) -> float:
    """
    Compare job and CV skills within a bucket using LLM
    
    Args:
        bucket_name: Name of the skill bucket
        job_skills: List of job skills in this bucket
        cv_skills: List of CV skills in this bucket
        bucket_cache: Optional cache object to use for caching results
    
    Returns:
        float: Match score between 0.0 and 1.0
    """
    # Check cache first if provided
    if bucket_cache is not None:
        cached_score = bucket_cache.get(bucket_name, job_skills, cv_skills)
        if cached_score is not None:
            logger.info(f"Cache hit for {bucket_name} bucket comparison")
            return cached_score
    
    # If either skill list is empty, return 0
    if not job_skills or not cv_skills:
        if bucket_cache is not None:
            bucket_cache.set(bucket_name, job_skills, cv_skills, 0.0)
        return 0.0
    
    # Prepare prompt for LLM
    system_prompt = f"""
    You are a skilled job skill analyzer. Your task is to assess how well a person's skills match the required skills for a job.
    
    For each skill category, you will receive two lists:
    1. Skills required by the job (Job Skills)
    2. Skills the person has (CV Skills)
    
    Consider these factors in your assessment:
    - Direct matches between job skills and CV skills
    - Skills in the CV that are similar or equivalent to job skills
    - The breadth and depth of skills in both lists
    - The relevance of the CV skills to the job skills
    
    You must provide:
    1. An assessment of the match quality as a percentage from 0-100%
    2. A brief explanation of your reasoning
    
    Focus on the {bucket_name} skill category for this assessment.
    """
    
    user_prompt = f"""
    Job Skills ({bucket_name}):
    {', '.join(job_skills)}
    
    CV Skills ({bucket_name}):
    {', '.join(cv_skills)}
    
    Evaluate the match quality and provide a matching percentage.
    """
    
    try:
        # Call LLM API
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,  # Low temperature for more consistent responses
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result.get("message", {}).get("content", "")
            
            # Extract percentage from response
            percentage_match = extract_percentage(llm_response)
            
            # Cache the result if cache is provided
            if bucket_cache is not None:
                bucket_cache.set(bucket_name, job_skills, cv_skills, percentage_match)
            
            return percentage_match
        else:
            logger.error(f"LLM API error: {response.status_code} - {response.text}")
            return 0.0
            
    except Exception as e:
        logger.error(f"Error comparing buckets with LLM: {str(e)}")
        return 0.0
