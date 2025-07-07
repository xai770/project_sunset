"""
Embedding-based skill matching utilities (extracted from enhanced_skill_matcher.py)
"""
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("enhanced_skill_matcher.embedding")

try:
    from run_pipeline.skill_matching.embedding_utils import (
        EmbeddingGenerator, find_top_matches, cosine_similarity
    )
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("Embedding utilities not available - embedding-based matching disabled")

def generate_skill_embeddings(skills_data: Dict[str, Dict[str, Any]]) -> Dict[str, List[float]]:
    if not EMBEDDINGS_AVAILABLE:
        logger.warning("Embeddings not available, skipping embedding generation")
        return {}
    try:
        generator = EmbeddingGenerator()
        skill_embeddings = {}
        for skill_name, skill_data in skills_data.items():
            domains = skill_data.get("domains", [])
            description = skill_data.get("description", "")
            embedding_text = f"{skill_name}. {description} Domains: {', '.join(domains)}"
            embedding = generator.get_embedding(embedding_text)
            if embedding:
                skill_embeddings[skill_name] = embedding
            if len(skill_embeddings) % 50 == 0:
                generator.save_cache()
        generator.save_cache()
        logger.info(f"Generated {len(skill_embeddings)} skill embeddings")
        return skill_embeddings
    except Exception as e:
        logger.error(f"Failed to generate skill embeddings: {e}")
        return {}

def find_embedding_matches(
    job_skill_name: str,
    job_skill_embedding: List[float],
    your_skills_embeddings: Dict[str, List[float]],
    threshold: float = 0.6,
    top_k: int = 5
) -> List[Tuple[str, float]]:
    if not job_skill_embedding or not your_skills_embeddings:
        return []
    matches = []
    for your_skill_name, your_embedding in your_skills_embeddings.items():
        similarity = cosine_similarity(job_skill_embedding, your_embedding)
        if similarity >= threshold:
            matches.append((your_skill_name, similarity))
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:top_k]
