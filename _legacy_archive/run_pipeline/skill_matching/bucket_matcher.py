#!/usr/bin/env python3
"""
Main matching logic for bucketed skill matching
"""

import os
import logging
import requests
import concurrent.futures
from typing import Dict, List, Any, Optional, Tuple
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

# Import confidence scoring functionality
try:
    from run_pipeline.skill_matching.confidence_scorer import (
        calculate_confidence_score, extract_llm_confidence, 
        calculate_bucket_relevance, has_text_pattern_match,
        calculate_contextual_relevance, get_confidence_level
    )
    CONFIDENCE_SCORING_AVAILABLE = True
    logger.info("Confidence scoring module available and will be used for enhanced matching")
except ImportError:
    CONFIDENCE_SCORING_AVAILABLE = False
    logger.warning("Confidence scoring module not available - falling back to basic scoring")

# Try to import embedding utilities for similarity scoring
try:
    from run_pipeline.skill_matching.embedding_utils import (
        EmbeddingGenerator, cosine_similarity
    )
    EMBEDDINGS_AVAILABLE = True
    # Initialize embedding generator
    embedding_generator = EmbeddingGenerator()
    logger.info("Embedding utilities available - will use for similarity calculations")
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("Embedding utilities not available - similarity scores will not be calculated")

# Ollama settings
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")

def compare_skill_buckets_llm(
    bucket_name: str, 
    job_skills: List[str], 
    cv_skills: List[str],
    job_text: Optional[str] = None,
    job_title: Optional[str] = None
) -> Tuple[float, Optional[Dict[str, Any]]]:
    """
    Compare job and CV skills within a bucket using LLM
    
    Args:
        bucket_name: Name of the skill bucket
        job_skills: List of job skills in this bucket
        cv_skills: List of CV skills in this bucket
        job_text: Optional full job description for context
        job_title: Optional job title for relevance calculation
    
    Returns:
        Tuple[float, Optional[Dict[str, Any]]]: Match score between 0.0 and 1.0, and optional confidence details
    """
    # Check cache first
    cached_score = bucket_cache.get(bucket_name, job_skills, cv_skills)
    if cached_score is not None:
        logger.info(f"Cache hit for {bucket_name} bucket comparison")
        # For backwards compatibility with cache entries that don't have confidence info
        if isinstance(cached_score, dict) and "score" in cached_score:
            return cached_score["score"], cached_score.get("confidence_details")
        else:
            return float(cached_score), None
    
    # If either skill list is empty, return 0
    if not job_skills or not cv_skills:
        bucket_cache.set(bucket_name, job_skills, cv_skills, 0.0)
        return 0.0, None
    
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
    2. Your confidence in your assessment as a percentage from 0-100%
    3. A brief explanation of your reasoning
    
    Focus on the {bucket_name} skill category for this assessment.
    """
    
    user_prompt = f"""
    Job Skills ({bucket_name}):
    {', '.join(job_skills)}
    
    CV Skills ({bucket_name}):
    {', '.join(cv_skills)}
    
    Evaluate the match quality, provide a matching percentage, and state your confidence level (0-100%).
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
            
            # Extract confidence information if available
            confidence_details: Optional[Dict[str, Any]] = None
            if CONFIDENCE_SCORING_AVAILABLE:
                # Extract LLM confidence
                llm_confidence = extract_llm_confidence(llm_response)
                
                # Calculate embedding similarity if available
                embedding_similarity = None
                if EMBEDDINGS_AVAILABLE and embedding_generator:
                    try:
                        # Calculate average similarity between job and CV skills
                        job_embeddings = embedding_generator.batch_get_embeddings(job_skills)
                        cv_embeddings = embedding_generator.batch_get_embeddings(cv_skills)
                        
                        # Calculate average similarity
                        total_similarity = 0.0
                        count = 0
                        for job_skill, job_emb in job_embeddings.items():
                            best_similarity = 0.0
                            for cv_skill, cv_emb in cv_embeddings.items():
                                similarity = cosine_similarity(job_emb, cv_emb)
                                best_similarity = max(best_similarity, similarity)
                            total_similarity += best_similarity
                            count += 1
                        
                        if count > 0:
                            embedding_similarity = total_similarity / count
                    except Exception as e:
                        logger.warning(f"Error calculating embedding similarity: {e}")
                
                # Calculate bucket relevance
                bucket_relevance = None
                if bucket_name in SKILL_BUCKETS:
                    bucket_keywords = SKILL_BUCKETS[bucket_name]
                    # Average relevance for all CV skills
                    total_relevance = 0.0
                    for skill in cv_skills:
                        total_relevance += calculate_bucket_relevance(skill, bucket_name, bucket_keywords)
                    if cv_skills:
                        bucket_relevance = total_relevance / len(cv_skills)
                
                # Build confidence details
                confidence_details = {
                    "embedding_similarity": embedding_similarity,
                    "bucket_relevance": bucket_relevance,
                    "llm_confidence": llm_confidence,
                    "job_skills_count": len(job_skills),
                    "cv_skills_count": len(cv_skills)
                }
                
                # Calculate overall confidence score
                confidence_score = None
                score_str = percentage_match  # Assign from the correct source
                if isinstance(score_str, (str, int, float)):
                    try:
                        confidence_score = float(score_str)
                    except (ValueError, TypeError):
                        confidence_score = None
                
                if confidence_score is not None:
                    assert confidence_details is not None
                    confidence_details["confidence_score"] = confidence_score  # float
                    confidence_details["confidence_level"] = str(get_confidence_level(confidence_score))  # str
            
            # Cache the result with confidence information if available
            if confidence_details:
                cache_data = {
                    "score": percentage_match,
                    "confidence_details": confidence_details,
                    "timestamp": datetime.now().isoformat()
                }
                # Only pass the float score to set if that's the expected type
                bucket_cache.set(bucket_name, job_skills, cv_skills, percentage_match)
            else:
                bucket_cache.set(bucket_name, job_skills, cv_skills, percentage_match)
            
            return percentage_match, confidence_details
        else:
            logger.error(f"LLM API error: {response.status_code} - {response.text}")
            bucket_cache.set(bucket_name, job_skills, cv_skills, 0.0)
            return 0.0, None
            
    except Exception as e:
        logger.error(f"Error comparing buckets with LLM: {str(e)}")
        bucket_cache.set(bucket_name, job_skills, cv_skills, 0.0)
        return 0.0, None

from functools import partial

def match_job_to_your_skills(job_data: Dict[str, Any], your_skills: Dict[str, Any], max_workers: int = 4) -> Dict[str, Any]:
    """
    Match job skills to your skills using the bucketed approach
    
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
        
        # Get job text and title for additional context if available
        job_text = job_data.get("web_details", {}).get("concise_description", "")
        if not job_text:
            job_text = job_data.get("api_details", {}).get("html", "")
        
        job_title = job_data.get("web_details", {}).get("position_title", "")
        
        # Compare skills in this bucket with confidence scoring
        match_percentage, confidence_details = compare_skill_buckets_llm(
            bucket, 
            job_bucket_skills, 
            cv_bucket_skills,
            job_text=job_text,
            job_title=job_title
        )
        
        # Prepare result dictionary
        result = {
            "match_percentage": match_percentage,
            "weight": bucket_weights.get(bucket, 0.0),
            "job_skills": job_bucket_skills,
            "cv_skills": cv_bucket_skills
        }
        
        # Add confidence details if available
        if confidence_details:
            result["confidence"] = confidence_details
        
        return bucket, result
    
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
    total_confidence = 0.0
    weighted_confidence = 0.0
    total_weight = 0.0
    
    for bucket, result in bucket_results.items():
        try:
            match_percentage = float(result["match_percentage"])
            weight = float(result["weight"])
            overall_match += match_percentage * weight
            total_weight += weight
            
            # Track confidence if available
            if "confidence" in result and result["confidence"].get("confidence_score") is not None:
                confidence = float(result["confidence"]["confidence_score"])
                weighted_confidence += confidence * weight
                total_confidence += weight
        except (ValueError, TypeError):
            # Skip invalid values
            continue
    
    # Calculate overall confidence
    overall_confidence = None
    if total_confidence > 0:
        overall_confidence = weighted_confidence / total_confidence
    
    # Add timestamp and confidence information to result
    result = {
        "overall_match": overall_match,
        "bucket_results": bucket_results,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add confidence information if available
    if overall_confidence is not None:
        result["overall_confidence"] = overall_confidence
        result["confidence_level"] = get_confidence_level(overall_confidence) if CONFIDENCE_SCORING_AVAILABLE else "Unknown"
    
    return result
