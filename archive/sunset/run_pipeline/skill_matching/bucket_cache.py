#!/usr/bin/env python3
"""
Cache utilities for bucketed skill matching
"""

import json
import logging
import hashlib
import threading
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucket_cache")

# Get paths from the main config
try:
    from run_pipeline.config.paths import PROJECT_ROOT
except ImportError:
    # Fallback if imported outside the pipeline
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Define paths
CACHE_DIR = PROJECT_ROOT / "data" / "skill_match_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
BUCKET_CACHE_FILE = CACHE_DIR / "bucket_match_cache.json"

class BucketMatchCache:
    """Cache for bucket matching results"""
    
    def __init__(self, cache_file: Path = BUCKET_CACHE_FILE):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.hits = 0
        self.misses = 0
        self.lock = threading.RLock()  # Reentrant lock for thread safety
    
    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load the cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                logger.info(f"Loaded {len(cache)} bucket match entries from cache")
                return cache
        except Exception as e:
            logger.warning(f"Error loading bucket cache: {e}")
        
        return {}
    
    def save_cache(self):
        """Save the cache to disk"""
        with self.lock:
            try:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, indent=2)
                logger.info(f"Saved {len(self.cache)} bucket match entries to cache")
            except Exception as e:
                logger.warning(f"Error saving bucket cache: {e}")
    
    def get_key(self, bucket_name: str, job_skills: List[str], cv_skills: List[str]) -> str:
        """Generate a cache key for bucket comparison"""
        # Sort skills to ensure consistent keys
        job_skills_str = ",".join(sorted(job_skills))
        cv_skills_str = ",".join(sorted(cv_skills))
        key_str = f"{bucket_name}::{job_skills_str}::{cv_skills_str}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, bucket_name: str, job_skills: List[str], cv_skills: List[str]) -> Optional[float]:
        """Get a cached match score (thread-safe)"""
        with self.lock:
            key = self.get_key(bucket_name, job_skills, cv_skills)
            if key in self.cache:
                # Check for TTL if present
                entry = self.cache[key]
                if isinstance(entry, dict) and "timestamp" in entry:
                    # Calculate age in days
                    timestamp = entry.get("timestamp")
                    if timestamp:
                        try:
                            cache_date = datetime.fromisoformat(timestamp)
                            age_days = (datetime.now() - cache_date).days
                            # If entry is older than 30 days, consider it stale
                            if age_days > 30:
                                self.misses += 1
                                return None
                        except (ValueError, TypeError):
                            # If timestamp parsing fails, fall back to using the entry
                            pass
                
                # Get score from entry
                score = entry.get("score") if isinstance(entry, dict) else entry
                self.hits += 1
                # Handle None case explicitly
                if score is not None:
                    return float(score)
                return 0.0
                
            self.misses += 1
            return None
    
    def set(self, bucket_name: str, job_skills: List[str], cv_skills: List[str], score: float):
        """Set a match score in the cache (thread-safe)"""
        with self.lock:
            key = self.get_key(bucket_name, job_skills, cv_skills)
            self.cache[key] = {
                "score": score,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save cache every 10 new entries
            if len(self.cache) % 10 == 0:
                self.save_cache()

# Initialize global cache instance
bucket_cache = BucketMatchCache()
