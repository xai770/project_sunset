#!/usr/bin/env python3
"""
Main matching logic for bucketed skill matching
"""

import os
import logging
import requests
import concurrent.futures
import time
import random
from functools import partial
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucket_matcher")

# Import bucket utilities
from run_pipeline.skill_matching.bucket_utils import (
    SKILL_BUCKETS, extract_cv_skills, extract_job_skills, 
    calculate_bucket_weights, extract_percentage
)
from run_pipeline.skill_matching.bucket_cache import bucket_cache

# Ollama settings
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")

# Retry settings
MAX_RETRIES = 3
BASE_TIMEOUT = 30  # Base timeout in seconds
RETRY_DELAY = 2  # Initial delay between retries in seconds

def compare_skill_buckets_llm(bucket_name: str, job_skills: List[str], cv_skills: List[str]) -> float:
    """
    Compare job and CV skills within a bucket using LLM
    
    Args:
        bucket_name: Name of the skill bucket
        job_skills: List of job skills in this bucket
        cv_skills: List of CV skills in this bucket
    
    Returns:
        float: Match score between 0.0 and 1.0
    """
    # Check cache first
    cached_score = bucket_cache.get(bucket_name, job_skills, cv_skills)
    if cached_score is not None:
        logger.info(f"Cache hit for {bucket_name} bucket comparison")
        return cached_score
    
    # If either skill list is empty, return 0
    if not job_skills or not cv_skills:
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
    
    # Adjust timeout based on skill list sizes - larger lists need more time
    list_size = len(job_skills) + len(cv_skills)
    adaptive_timeout = min(120, BASE_TIMEOUT + (list_size // 5))
    
    # Implement retry with exponential backoff
    for attempt in range(MAX_RETRIES):
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
                timeout=adaptive_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get("message", {}).get("content", "")
                
                # Extract percentage from response
                percentage_match = extract_percentage(llm_response)
                
                # Cache the result
                bucket_cache.set(bucket_name, job_skills, cv_skills, percentage_match)
                
                return percentage_match
            elif response.status_code == 429 or response.status_code >= 500:
                # Rate limiting or server error - worth retrying
                retry_delay = RETRY_DELAY * (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                logger.warning(f"LLM API error (attempt {attempt+1}/{MAX_RETRIES}): {response.status_code}. Retrying in {retry_delay:.2f}s")
                time.sleep(retry_delay)
            else:
                # Client error - not worth retrying
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                return 0.0
                
        except requests.exceptions.Timeout:
            retry_delay = RETRY_DELAY * (2 ** attempt) + random.uniform(0, 1)
            logger.warning(f"LLM API timeout (attempt {attempt+1}/{MAX_RETRIES}). Retrying in {retry_delay:.2f}s with longer timeout")
            # Increase timeout for next attempt
            adaptive_timeout = int(adaptive_timeout * 1.5)
            time.sleep(retry_delay)
            
        except Exception as e:
            retry_delay = RETRY_DELAY * (2 ** attempt) + random.uniform(0, 1)
            logger.warning(f"Error comparing buckets with LLM (attempt {attempt+1}/{MAX_RETRIES}): {str(e)}. Retrying in {retry_delay:.2f}s")
            time.sleep(retry_delay)
    
    logger.error(f"Failed to compare buckets after {MAX_RETRIES} attempts. Returning 0 match.")
    return 0.0

def match_job_to_your_skills(job_data: Dict[str, Any], your_skills: Dict[str, Any], max_workers: int = 4) -> Dict[str, Any]:
    """
    Match job skills to your skills using the bucketed approach with parallel processing
    
    Args:
        job_data: Job data structure
        your_skills: Your skills data structure
        max_workers: Maximum number of worker threads
    
    Returns:
        Dict[str, Any]: Match results
    """
    # Extract and bucket skills
    job_skills_buckets = extract_job_skills(job_data)
    cv_skills_buckets = extract_cv_skills(your_skills)
    
    # Calculate bucket weights based on job requirements
    bucket_weights = calculate_bucket_weights(job_skills_buckets)
    
    def process_bucket(bucket):
        """Process a single bucket and return results"""
        job_bucket_skills = job_skills_buckets.get(bucket, [])
        cv_bucket_skills = cv_skills_buckets.get(bucket, [])
        
        # Skip empty buckets
        if not job_bucket_skills:
            return bucket, {
                "match_percentage": 0.0,
                "weight": bucket_weights.get(bucket, 0.0),
                "job_skills": job_bucket_skills,
                "cv_skills": cv_bucket_skills
            }
        
        # Compare skills in this bucket
        match_percentage = compare_skill_buckets_llm(bucket, job_bucket_skills, cv_bucket_skills)
        
        return bucket, {
            "match_percentage": match_percentage,
            "weight": bucket_weights.get(bucket, 0.0),
            "job_skills": job_bucket_skills,
            "cv_skills": cv_bucket_skills
        }
    
    # Compare buckets in parallel
    bucket_results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all bucket comparison tasks
        future_to_bucket = {
            executor.submit(process_bucket, bucket): bucket 
            for bucket in SKILL_BUCKETS.keys()
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_bucket):
            bucket, result = future.result()
            bucket_results[bucket] = result
    
    # Calculate weighted average for overall match
    overall_match = 0.0
    for result in bucket_results.values():
        try:
            match_percentage = float(result["match_percentage"])
            weight = float(result["weight"])
            overall_match += match_percentage * weight
        except (ValueError, TypeError):
            # Skip invalid values
            continue
    
    return {
        "overall_match": overall_match,
        "bucket_results": bucket_results,
        "timestamp": datetime.now().isoformat()
    }
