#!/usr/bin/env python3
"""
Confidence Scoring Module for Skill Matching

This module provides functions to calculate confidence scores for skill matches
based on multiple factors:
1. Embedding similarity
2. Bucket relevance
3. LLM confidence assessment
4. Text pattern matching
5. Contextual relevance

The confidence score helps provide a more reliable measure of match quality
and prioritize skills with higher confidence.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("confidence_scorer")

def calculate_confidence_score(
    match_percentage: float,
    embedding_similarity: Optional[float] = None,
    bucket_relevance: Optional[float] = None,
    llm_confidence: Optional[float] = None,
    text_pattern_match: Optional[bool] = None,
    contextual_relevance: Optional[float] = None
) -> float:
    """
    Calculate a confidence score based on multiple factors
    
    Args:
        match_percentage: Primary match percentage (0.0-1.0)
        embedding_similarity: Vector similarity score (0.0-1.0) if available
        bucket_relevance: Relevance of the skill to its bucket (0.0-1.0)
        llm_confidence: LLM's confidence in its assessment (0.0-1.0)
        text_pattern_match: Whether exact text patterns were found
        contextual_relevance: Relevance to the job context (0.0-1.0)
    
    Returns:
        float: Confidence score between 0.0 and 1.0
    """
    # Weights for each factor
    weights = {
        "match_percentage": 0.4,
        "embedding_similarity": 0.2,
        "bucket_relevance": 0.1,
        "llm_confidence": 0.2,
        "text_pattern_match": 0.05,
        "contextual_relevance": 0.05
    }
    
    # Start with base match percentage (required)
    weighted_sum = match_percentage * weights["match_percentage"]
    total_weight = weights["match_percentage"]
    
    # Add other factors if available
    if embedding_similarity is not None:
        weighted_sum += embedding_similarity * weights["embedding_similarity"]
        total_weight += weights["embedding_similarity"]
    
    if bucket_relevance is not None:
        weighted_sum += bucket_relevance * weights["bucket_relevance"]
        total_weight += weights["bucket_relevance"]
    
    if llm_confidence is not None:
        weighted_sum += llm_confidence * weights["llm_confidence"]
        total_weight += weights["llm_confidence"]
    
    if text_pattern_match is not None:
        pattern_value = 1.0 if text_pattern_match else 0.0
        weighted_sum += pattern_value * weights["text_pattern_match"]
        total_weight += weights["text_pattern_match"]
    
    if contextual_relevance is not None:
        weighted_sum += contextual_relevance * weights["contextual_relevance"]
        total_weight += weights["contextual_relevance"]
    
    # Normalize by total weight
    if total_weight > 0:
        return weighted_sum / total_weight
    else:
        return 0.0

def extract_llm_confidence(llm_response: str) -> Optional[float]:
    """
    Extract confidence value from LLM response
    
    Args:
        llm_response: LLM response text that might contain confidence information
    
    Returns:
        Optional[float]: Confidence value (0.0-1.0) if found, None otherwise
    """
    # Look for confidence patterns in the response
    confidence_patterns = [
        r"confidence(?:\s+of)?\s*[:=]\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*%\s*confidence",
        r"confidence(?:\s+level)?\s*(?:is|at)\s*(\d+(?:\.\d+)?)",
        r"with\s+(\d+(?:\.\d+)?)\s*%\s*confidence"
    ]
    
    for pattern in confidence_patterns:
        matches = re.search(pattern, llm_response.lower())
        if matches:
            try:
                confidence = float(matches.group(1))
                # If confidence is expressed as percentage, convert to 0-1 scale
                if confidence > 1.0:
                    confidence /= 100.0
                return max(0.0, min(1.0, confidence))
            except (ValueError, IndexError):
                pass
    
    return None

def calculate_bucket_relevance(
    skill: str, 
    bucket: str, 
    bucket_keywords: List[str]
) -> float:
    """
    Calculate relevance of a skill to its bucket
    
    Args:
        skill: The skill name
        bucket: The bucket name
        bucket_keywords: List of keywords associated with the bucket
    
    Returns:
        float: Relevance score (0.0-1.0)
    """
    skill_lower = skill.lower()
    
    # Direct match to bucket name is high relevance
    if bucket.lower() in skill_lower:
        return 1.0
    
    # Count keyword matches
    matches = sum(1 for keyword in bucket_keywords if keyword.lower() in skill_lower)
    
    # Calculate relevance based on number of matching keywords
    if not bucket_keywords:
        return 0.5  # Default if no keywords defined
    
    relevance = min(1.0, matches / min(3, len(bucket_keywords)))
    return relevance

def has_text_pattern_match(skill: str, job_text: str) -> bool:
    """
    Check if the skill has an exact or close match in the job text
    
    Args:
        skill: The skill to search for
        job_text: The job description or related text
    
    Returns:
        bool: True if a pattern match is found, False otherwise
    """
    if not job_text or not skill:
        return False
    
    # Normalize texts
    skill_normalized = skill.lower()
    job_text_normalized = job_text.lower()
    
    # Direct match check
    if skill_normalized in job_text_normalized:
        return True
    
    # Check for skill with punctuation variants
    skill_pattern = re.escape(skill_normalized)
    skill_pattern = skill_pattern.replace(r"\ ", r"[\s\-_.,]+")
    
    if re.search(f"\\b{skill_pattern}\\b", job_text_normalized):
        return True
    
    return False

def calculate_contextual_relevance(
    skill: str,
    job_title: str,
    job_type: Optional[str] = None
) -> float:
    """
    Calculate relevance of a skill to the job context
    
    Args:
        skill: The skill name
        job_title: The job title
        job_type: Optional job type or category
    
    Returns:
        float: Contextual relevance score (0.0-1.0)
    """
    relevance = 0.0
    skill_lower = skill.lower()
    
    # Check if skill appears in job title
    if skill_lower in job_title.lower():
        relevance += 0.7
    
    # Check if job type relates to skill
    if job_type and skill_lower in job_type.lower():
        relevance += 0.3
    
    return min(1.0, relevance)

def enrich_match_with_confidence(
    match_data: Dict[str, Any],
    job_text: str,
    job_title: str,
    embedding_similarity: Optional[float] = None,
    llm_response: Optional[str] = None,
    bucket_keywords: Optional[Dict[str, List[str]]] = None
) -> Dict[str, Any]:
    """
    Enrich a match result with confidence scoring
    
    Args:
        match_data: The match data to enrich
        job_text: Full job description for pattern matching
        job_title: Job title for contextual relevance
        embedding_similarity: Optional embedding similarity score
        llm_response: Optional LLM response for confidence extraction
        bucket_keywords: Optional bucket keywords for relevance calculation
    
    Returns:
        Dict[str, Any]: Enriched match data with confidence information
    """
    # Get match percentage from data
    match_percentage = match_data.get("match_percentage", 0.0)
    if isinstance(match_percentage, str) and match_percentage.endswith("%"):
        match_percentage = float(match_percentage.rstrip("%")) / 100
    
    # Extract LLM confidence if available
    llm_confidence = None
    if llm_response:
        llm_confidence = extract_llm_confidence(llm_response)
    
    # Get bucket information if available
    bucket = match_data.get("bucket", "")
    bucket_relevance = None
    if bucket and bucket_keywords and bucket in bucket_keywords:
        skill = match_data.get("skill_name", "")
        if skill:
            bucket_relevance = calculate_bucket_relevance(
                skill, bucket, bucket_keywords[bucket]
            )
    
    # Check text pattern match
    text_pattern_match = None
    if job_text:
        skill = match_data.get("skill_name", "")
        if skill:
            text_pattern_match = has_text_pattern_match(skill, job_text)
    
    # Calculate contextual relevance
    contextual_relevance = None
    if job_title:
        skill = match_data.get("skill_name", "")
        if skill:
            contextual_relevance = calculate_contextual_relevance(
                skill, job_title, match_data.get("job_type", "")
            )
    
    # Calculate overall confidence score
    confidence_score = calculate_confidence_score(
        match_percentage=match_percentage,
        embedding_similarity=embedding_similarity,
        bucket_relevance=bucket_relevance,
        llm_confidence=llm_confidence,
        text_pattern_match=text_pattern_match,
        contextual_relevance=contextual_relevance
    )
    
    # Enrich match data with confidence information
    enriched_data = match_data.copy()
    enriched_data["confidence_score"] = confidence_score
    enriched_data["confidence_details"] = {
        "embedding_similarity": embedding_similarity,
        "bucket_relevance": bucket_relevance,
        "llm_confidence": llm_confidence,
        "text_pattern_match": text_pattern_match,
        "contextual_relevance": contextual_relevance
    }
    
    return enriched_data

def get_confidence_level(score: float) -> str:
    """
    Convert a confidence score to a descriptive level
    
    Args:
        score: Confidence score between 0.0 and 1.0
    
    Returns:
        str: Confidence level description
    """
    if score >= 0.9:
        return "Very High"
    elif score >= 0.75:
        return "High"
    elif score >= 0.5:
        return "Medium"
    elif score >= 0.25:
        return "Low"
    else:
        return "Very Low"
