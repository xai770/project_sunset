#!/usr/bin/env python3
"""
Embedding utilities for skill matching

This module provides functions for generating and comparing embeddings
to optimize skill matching by pre-filtering candidates using vector similarity.
"""

import os
import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("embedding_utils")

# Try to import sentence-transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not available. Using fallback embedding method.")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Get paths from the main config
try:
    from run_pipeline.config.paths import PROJECT_ROOT
except ImportError:
    # Fallback if imported outside the pipeline
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Define paths
EMBEDDING_CACHE_DIR = PROJECT_ROOT / "data" / "skill_embeddings"
EMBEDDING_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Default model for embeddings
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"

class EmbeddingGenerator:
    """Class for generating and caching embeddings for skills"""

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        self.model_name = model_name
        self.cache_file = EMBEDDING_CACHE_DIR / f"{model_name.replace('/', '_')}_embeddings.json"
        self.embedding_cache = self._load_cache()
        self.model = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f"Initialized embedding model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load embedding model {model_name}: {e}")
        
    def _load_cache(self) -> Dict[str, List[float]]:
        """Load embedding cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                logger.info(f"Loaded {len(cache)} skill embeddings from cache")
                return cache
        except Exception as e:
            logger.warning(f"Error loading embedding cache: {e}")
        
        return {}
    
    def save_cache(self):
        """Save embedding cache to disk"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.embedding_cache, f)
            logger.info(f"Saved {len(self.embedding_cache)} skill embeddings to cache")
        except Exception as e:
            logger.warning(f"Error saving embedding cache: {e}")
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for a text, from cache or by generating it"""
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        if self.model is None:
            return self._fallback_embedding(text)
        
        try:
            embedding = self.model.encode(text)
            embedding_list = embedding.tolist()
            self.embedding_cache[text] = embedding_list
            
            # Save cache every 100 new embeddings
            if len(self.embedding_cache) % 100 == 0:
                self.save_cache()
                
            return embedding_list
        except Exception as e:
            logger.error(f"Error generating embedding for '{text}': {e}")
            return self._fallback_embedding(text)
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """Generate a simple fallback embedding when the model is not available"""
        # This is a very basic fallback that shouldn't be used in production
        import hashlib
        
        # Generate a pseudo-random embedding from text hash
        hash_val = hashlib.md5(text.encode()).hexdigest()
        # Convert hash to a list of 20 float values between -1 and 1
        embedding = []
        for i in range(0, len(hash_val), 2):
            if i+2 <= len(hash_val):
                val = int(hash_val[i:i+2], 16)
                embedding.append((val / 255) * 2 - 1)
        
        # Pad to 20 dimensions if needed
        while len(embedding) < 20:
            embedding.append(0.0)
            
        return embedding[:20]  # Limit to 20 dimensions
    
    def batch_get_embeddings(self, texts: List[str]) -> Dict[str, List[float]]:
        """Get embeddings for multiple texts at once"""
        result = {}
        uncached_texts = []
        
        # First check cache
        for text in texts:
            if text in self.embedding_cache:
                result[text] = self.embedding_cache[text]
            else:
                uncached_texts.append(text)
        
        # Generate embeddings for uncached texts
        if uncached_texts and self.model is not None:
            try:
                embeddings = self.model.encode(uncached_texts)
                for i, text in enumerate(uncached_texts):
                    embedding_list = embeddings[i].tolist()
                    self.embedding_cache[text] = embedding_list
                    result[text] = embedding_list
                
                # Save cache if we generated new embeddings
                if uncached_texts:
                    self.save_cache()
            except Exception as e:
                logger.error(f"Error batch generating embeddings: {e}")
                # Fall back to individual generation
                for text in uncached_texts:
                    result[text] = self._fallback_embedding(text)
        else:
            # Use fallback for each text if model not available
            for text in uncached_texts:
                result[text] = self._fallback_embedding(text)
        
        return result


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if not vec1 or not vec2:
        return 0.0
        
    try:
        # Convert to numpy arrays for efficient calculation
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
            
        similarity = dot_product / (norm_v1 * norm_v2)
        # Ensure the result is between 0 and 1
        return max(0.0, min(1.0, similarity))
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {e}")
        return 0.0


def find_matches_using_embeddings(query_embedding, embedding_dict, top_n=10):
    # Add None check before calling len()
    if query_embedding is None:
        return []
    
    # Sort the embeddings based on similarity to the query embedding
    sorted_embeddings = sorted(
        embedding_dict.items(),
        key=lambda item: cosine_similarity(query_embedding, item[1]),
        reverse=True
    )
    
    # Get the top N matches
    top_matches = sorted_embeddings[:top_n]
    
    return top_matches


def find_top_matches(
    query_embedding: List[float],
    candidate_embeddings: Dict[str, List[float]],
    top_k: int = 10,
    threshold: float = 0.5
) -> List[Tuple[str, float]]:
    """Find top K matches based on embedding similarity"""
    # Handle None query embedding
    if query_embedding is None:
        return []
    
    # Filter out any None values in candidate embeddings
    valid_candidates = {k: v for k, v in candidate_embeddings.items() if v is not None}
    
    # Proceed with valid embeddings
    scores = []
    
    for candidate, embedding in valid_candidates.items():
        similarity = cosine_similarity(query_embedding, embedding)
        # Only include results above threshold
        if similarity >= threshold:
            scores.append((candidate, similarity))
    
    # Sort by similarity score in descending order
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]


def enrich_skill_with_embedding(skill_data: Dict[str, Any], generator: EmbeddingGenerator) -> Dict[str, Any]:
    """Enrich a skill dictionary with its embedding"""
    # Create a description for embedding generation
    skill_name = skill_data.get("name", "")
    skill_desc = skill_data.get("description", "")
    domains = skill_data.get("domains", [])
    
    embedding_text = f"{skill_name}. {skill_desc} Domains: {', '.join(domains)}"
    
    # Generate and add embedding
    embedding = generator.get_embedding(embedding_text)
    if embedding:
        skill_data["embedding"] = embedding
    
    return skill_data


# Main function for testing
if __name__ == "__main__":
    generator = EmbeddingGenerator()
    
    # Test with some sample skills
    skills = [
        "Python Programming",
        "JavaScript Development",
        "Project Management",
        "Team Leadership",
        "Data Analysis"
    ]
    
    # Generate embeddings
    embeddings = {}
    for skill in skills:
        embedding = generator.get_embedding(skill)
        embeddings[skill] = embedding
        if embedding is not None:
            print(f"Generated embedding for {skill}: {len(embedding)} dimensions")
        else:
            print(f"No embedding generated for {skill}")
    
    # Test similarity
    query = "Python Software Development"
    query_embedding = generator.get_embedding(query)
    
    if query_embedding is not None:
        # Filter out None values from embeddings
        filtered_embeddings = {k: v for k, v in embeddings.items() if v is not None}
        top_matches = find_top_matches(query_embedding, filtered_embeddings)
        print(f"\nTop matches for '{query}':")
        for skill, score in top_matches:
            print(f"- {skill}: {score:.4f}")
    else:
        print(f"No embedding generated for query: {query}")
