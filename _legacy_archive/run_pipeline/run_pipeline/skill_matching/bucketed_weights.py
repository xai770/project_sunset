#!/usr/bin/env python3
"""
Bucket weight calculation and related logic for the bucketed skill matching system
"""

import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucketed_weights")

def calculate_bucket_weights(job_skills_buckets: Dict[str, List[str]]) -> Dict[str, float]:
    """
    Calculate weights for each skill bucket based on job requirements
    
    Args:
        job_skills_buckets: Job skills organized by bucket
    
    Returns:
        Dict[str, float]: Weight for each bucket (0.0-1.0)
    """
    # Count skills in each bucket
    bucket_counts = {bucket: len(skills) for bucket, skills in job_skills_buckets.items()}
    total_skills = sum(bucket_counts.values())
    
    if total_skills == 0:
        # Equal weight if no skills
        return {bucket: 1.0 / len(job_skills_buckets) for bucket in job_skills_buckets}
    
    # Calculate weights based on proportion of skills
    weights = {bucket: count / total_skills for bucket, count in bucket_counts.items()}
    
    # Ensure minimum weight for each bucket with at least one skill
    min_weight = 0.1
    for bucket, count in bucket_counts.items():
        if count > 0 and weights[bucket] < min_weight:
            weights[bucket] = min_weight
    
    # Normalize weights to sum to 1.0
    weight_sum = sum(weights.values())
    return {bucket: weight / weight_sum for bucket, weight in weights.items()}
