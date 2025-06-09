"""
Thread-safe cache for skill matching results (extracted from enhanced_skill_matcher.py)
"""
import json
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("enhanced_skill_matcher.cache")

class SkillMatchCache:
    """Cache for skill matching results to avoid redundant computations"""
    def __init__(self, cache_file: Path):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.hits = 0
        self.misses = 0
        self.lock = threading.RLock()  # Reentrant lock for thread safety

    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache: Dict[str, Dict[str, Any]] = json.load(f)
                logger.info(f"Loaded {len(cache)} skill match entries from cache")
                return cache
        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
        return {}

    def save_cache(self):
        with self.lock:
            try:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, indent=2)
                logger.info(f"Saved {len(self.cache)} skill match entries to cache")
            except Exception as e:
                logger.warning(f"Error saving cache: {e}")

    def get_key(self, skill1: str, skill2: str) -> str:
        sorted_skills = sorted([skill1, skill2])
        return hashlib.md5(f"{sorted_skills[0]}::{sorted_skills[1]}".encode()).hexdigest()

    def get(self, skill1: str, skill2: str) -> Optional[float]:
        with self.lock:
            key = self.get_key(skill1, skill2)
            if key in self.cache:
                entry = self.cache[key]
                if isinstance(entry, dict) and "timestamp" in entry:
                    timestamp = entry.get("timestamp")
                    if timestamp:
                        try:
                            cache_date = datetime.fromisoformat(timestamp)
                            age_days = (datetime.now() - cache_date).days
                            if age_days > 30:
                                self.misses += 1
                                return None
                        except (ValueError, TypeError):
                            pass
                score = entry.get("score") if isinstance(entry, dict) else entry
                self.hits += 1
                if score is not None:
                    return float(score)
                else:
                    return None
            self.misses += 1
            return None

    def set(self, skill1: str, skill2: str, score: float):
        with self.lock:
            key = self.get_key(skill1, skill2)
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
