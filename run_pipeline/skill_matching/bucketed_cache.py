"""
Thread-safe cache for bucketed skill matching results (extracted from bucketed_skill_matcher.py)
"""
# Implementation will be extracted from bucketed_skill_matcher.py

import json
import threading
from pathlib import Path
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger("bucketed_skill_matcher.cache")

class BucketMatchCache:
    """Cache for bucket matching results"""
    def __init__(self, cache_file: Path):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.hits = 0
        self.misses = 0
        self.lock = threading.RLock()

    def _load_cache(self) -> Dict[str, Any]:
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache: Dict[str, Any] = json.load(f)
                logger.info(f"Loaded {len(cache)} bucket match entries from cache")
                return cache
        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
        return {}

    def save_cache(self):
        with self.lock:
            try:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, indent=2)
                logger.info(f"Saved {len(self.cache)} bucket match entries to cache")
            except Exception as e:
                logger.warning(f"Error saving cache: {e}")

    def get_key(self, bucket_name: str, job_skills: list, cv_skills: list) -> str:
        # Sort skills for consistent key
        job_skills_sorted = sorted(job_skills)
        cv_skills_sorted = sorted(cv_skills)
        return f"{bucket_name}::{'|'.join(job_skills_sorted)}::{'|'.join(cv_skills_sorted)}"

    def get(self, bucket_name: str, job_skills: list, cv_skills: list) -> Any:
        with self.lock:
            key = self.get_key(bucket_name, job_skills, cv_skills)
            if key in self.cache:
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None

    def set(self, bucket_name: str, job_skills: list, cv_skills: list, score: float):
        with self.lock:
            key = self.get_key(bucket_name, job_skills, cv_skills)
            self.cache[key] = {
                "score": score,
                "timestamp": datetime.now().isoformat()
            }
            if len(self.cache) % 100 == 0:
                self.save_cache()

    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "total_entries": len(self.cache),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
            }
