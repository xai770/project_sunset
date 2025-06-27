"""
Skill Matching Framework Module

This module contains implementations for skill matching approaches:
1. Domain Relationship (SDR) Framework - uses domain relationships between skills
2. Bucketed Skill Matching - groups skills into buckets for faster matching
"""

# SDR Framework components
from run_pipeline.skill_matching.skill_analyzer import SkillAnalyzer
from run_pipeline.skill_matching.domain_relationship_classifier import DomainRelationshipClassifier
from run_pipeline.skill_matching.domain_aware_matcher import DomainAwareMatchingAlgorithm
from run_pipeline.skill_matching.cache import SkillMatchCache
from run_pipeline.skill_matching.category_utils import get_skill_category, should_compare_skills, SKILL_CATEGORIES, COMPATIBLE_CATEGORIES
from run_pipeline.skill_matching.embedding_matching import generate_skill_embeddings, find_embedding_matches, EMBEDDINGS_AVAILABLE
from run_pipeline.skill_matching.llm_matching import batch_llm_domain_overlap

# Bucketed Skill Matcher components
from run_pipeline.skill_matching.bucketed_skill_matcher import match_job_to_your_skills, batch_match_all_jobs
from run_pipeline.skill_matching.bucketed_cache import BucketMatchCache
from run_pipeline.skill_matching.bucketed_utils import categorize_skill, extract_cv_skills, extract_job_skills, SKILL_BUCKETS
from run_pipeline.skill_matching.bucketed_llm import compare_skill_buckets_llm
from run_pipeline.skill_matching.bucketed_weights import calculate_bucket_weights

__all__ = [
    # SDR Framework
    'SkillAnalyzer', 'DomainRelationshipClassifier', 'DomainAwareMatchingAlgorithm',
    'SkillMatchCache', 'get_skill_category', 'should_compare_skills', 'SKILL_CATEGORIES', 'COMPATIBLE_CATEGORIES',
    'generate_skill_embeddings', 'find_embedding_matches', 'EMBEDDINGS_AVAILABLE', 'batch_llm_domain_overlap',
    
    # Bucketed Matcher
    'match_job_to_your_skills', 'batch_match_all_jobs', 'BucketMatchCache',
    'categorize_skill', 'extract_cv_skills', 'extract_job_skills', 'SKILL_BUCKETS',
    'compare_skill_buckets_llm', 'calculate_bucket_weights'
]
