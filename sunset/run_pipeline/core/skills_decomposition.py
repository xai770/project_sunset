"""
Skill decomposition and caching logic for the job expansion pipeline
"""
from typing import List, Dict, Optional
from datetime import datetime
from run_pipeline.config.paths import SKILL_DECOMPOSITIONS_FILE
import json
import logging

skill_decomposition_cache: Dict[str, List[str]] = {}

logger = logging.getLogger('skills_decomposition')

def get_skill_decomposition(skill: str) -> Optional[List[str]]:
    return skill_decomposition_cache.get(skill.lower())

def add_skill_decomposition(skill: str, components: List[str]) -> None:
    skill_decomposition_cache[skill.lower()] = components
    if SKILL_DECOMPOSITIONS_FILE.exists():
        try:
            with open(SKILL_DECOMPOSITIONS_FILE, 'r') as f:
                decompositions = json.load(f)
        except Exception:
            decompositions = {
                "version": "1.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "complex_skills": []
            }
    else:
        decompositions = {
            "version": "1.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "complex_skills": []
        }
    skill_found = False
    for i, existing in enumerate(decompositions.get("complex_skills", [])):
        if existing.get("name", "").lower() == skill.lower():
            decompositions["complex_skills"][i]["elementary_skills"] = components
            decompositions["complex_skills"][i]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            skill_found = True
            break
    if not skill_found:
        decompositions["complex_skills"].append({
            "name": skill,
            "description": "",
            "elementary_skills": components,
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        })
    decompositions["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(SKILL_DECOMPOSITIONS_FILE, 'w') as f:
            json.dump(decompositions, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving skill decomposition: {str(e)}")
