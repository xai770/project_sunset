"""
I/O and process orchestration logic for the skills pipeline
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger('skills_io')

# File paths (update as needed)
SKILL_DECOMPOSITIONS_FILE = Path("/home/xai/Documents/sunset/profile/models/skill_decompositions.json")
SEMANTIC_CACHE_FILE = Path("/home/xai/Documents/sunset/profile/models/semantic_cache.json")

# Caches
skill_match_cache: Dict[str, Dict[str, float]] = {}
skill_decomposition_cache: Dict[str, List[str]] = {}

def load_caches():
    """Load skill caches from files"""
    global skill_match_cache
    global skill_decomposition_cache
    if SEMANTIC_CACHE_FILE.exists():
        try:
            with open(SEMANTIC_CACHE_FILE, 'r') as f:
                data = json.load(f)
                skill_match_cache = data.get("cache", {})
            logger.debug(f"Loaded {len(skill_match_cache)} skill match entries from cache")
        except Exception as e:
            logger.error(f"Error loading semantic cache: {str(e)}")
    if SKILL_DECOMPOSITIONS_FILE.exists():
        try:
            with open(SKILL_DECOMPOSITIONS_FILE, 'r') as f:
                data = json.load(f)
                for skill in data.get("complex_skills", []):
                    skill_name = skill.get("name", "")
                    elementary_skills = skill.get("elementary_skills", [])
                    if skill_name and elementary_skills:
                        skill_decomposition_cache[skill_name.lower()] = elementary_skills
            logger.debug(f"Loaded {len(skill_decomposition_cache)} skill decompositions from cache")
        except Exception as e:
            logger.error(f"Error loading skill decompositions: {str(e)}")

def save_caches():
    """Save skill caches to files"""
    try:
        cache_data = {
            "version": "1.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "cache": skill_match_cache
        }
        with open(SEMANTIC_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
        logger.debug(f"Saved {len(skill_match_cache)} skill match entries to cache")
    except Exception as e:
        logger.error(f"Error saving semantic cache: {str(e)}")

def add_skill_match(base_skill: str, related_skill: str, score: float) -> None:
    """Add a skill match to the cache"""
    base = base_skill.lower()
    related = related_skill.lower()
    if base not in skill_match_cache:
        skill_match_cache[base] = {}
    skill_match_cache[base][related] = score

def get_skill_match(base_skill: str, related_skill: str) -> Optional[float]:
    """Get a skill match score from the cache"""
    base = base_skill.lower()
    related = related_skill.lower()
    return skill_match_cache.get(base, {}).get(related)

def add_skill_decomposition(skill: str, components: List[str]) -> None:
    """Add a skill decomposition to the cache and file"""
    skill_lower = skill.lower()
    skill_decomposition_cache[skill_lower] = components
    # Also update the decompositions file
    if SKILL_DECOMPOSITIONS_FILE.exists():
        try:
            with open(SKILL_DECOMPOSITIONS_FILE, 'r') as f:
                decompositions = json.load(f)
        except Exception:
            decompositions = {"complex_skills": [], "last_updated": None}
    else:
        decompositions = {"complex_skills": [], "last_updated": None}
    skill_found = False
    for i, existing in enumerate(decompositions.get("complex_skills", [])):
        if existing.get("name", "").lower() == skill_lower:
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

def get_skill_decomposition(skill: str) -> Optional[List[str]]:
    """Get a skill decomposition from the cache"""
    return skill_decomposition_cache.get(skill.lower())

def process_job_skills(job_data: Dict[str, Any], job_id: str) -> Dict[str, Any]:
    """
    Process skills for a job posting
    Args:
        job_data: Job data dictionary
        job_id: Job ID
    Returns:
        Updated job data
    """
    from run_pipeline.core.skills_extraction import extract_skills_from_job
    from run_pipeline.core.skills_decomposition import get_skill_decomposition, add_skill_decomposition
    from run_pipeline.core.skills_categorization import categorize_skills
    from run_pipeline.core.skills_importance import analyze_skill_importance
    skills = extract_skills_from_job(job_data)
    decomposed_skills = {}
    for skill in skills:
        components = get_skill_decomposition(skill)
        if components:
            decomposed_skills[skill] = components
        else:
            skill_lower = skill.lower()
            if "tax compliance" in skill_lower:
                decomposed_skills[skill] = ["Tax Law Knowledge", "Attention to Detail", "Regulatory Awareness", "Documentation", "Deadline Management"]
            elif "tax preparation" in skill_lower:
                decomposed_skills[skill] = ["Tax Form Knowledge", "Tax Calculations", "Tax Software Proficiency", "Client Communication"]
            elif "financial analysis" in skill_lower:
                decomposed_skills[skill] = ["Financial Statement Analysis", "Excel", "Data Analysis", "Financial Modeling", "Critical Thinking"]
            elif "project management" in skill_lower:
                decomposed_skills[skill] = ["Task Planning", "Resource Allocation", "Timeline Management", "Risk Assessment", "Team Coordination"]
            elif "machine learning" in skill_lower:
                decomposed_skills[skill] = ["Statistics", "Programming", "Data Processing", "Algorithm Development", "Model Evaluation"]
            else:
                decomposed_skills[skill] = [skill]
            add_skill_decomposition(skill, decomposed_skills[skill])
    categorized_skills = categorize_skills(skills)
    skill_importance = analyze_skill_importance(job_data, skills)
    if "skills" not in job_data:
        job_data["skills"] = {}
    job_data["skills"]["extracted"] = skills
    job_data["skills"]["decomposed"] = decomposed_skills
    job_data["skills"]["categorized"] = categorized_skills
    job_data["skills"]["importance"] = skill_importance
    if "log" not in job_data:
        job_data["log"] = []
    job_data["log"].append({
        "timestamp": datetime.now().isoformat(),
        "script": "run_pipeline.core.skills_module",
        "action": "process_job_skills",
        "message": f"Processed {len(skills)} skills for job {job_id}"
    })
    return job_data

def process_job_files(job_dir: Path, max_jobs=None, specific_job_ids=None) -> Tuple[int, int, int]:
    """
    Process skills for job files
    Args:
        job_dir: Directory containing job files
        max_jobs: Maximum number of jobs to process
        specific_job_ids: List of specific job IDs to process
    Returns:
        tuple: (processed_count, success_count, error_count)
    """
    import os
    job_dir = Path(job_dir)
    if specific_job_ids:
        job_files = []
        for job_id in specific_job_ids:
            job_file = f"job{job_id}.json"
            removed_file = f"job{job_id}_removed.json"
            if (job_dir / job_file).exists():
                job_files.append(job_file)
            elif (job_dir / removed_file).exists():
                job_files.append(removed_file)
    else:
        job_files = sorted([f for f in os.listdir(job_dir) if f.startswith('job') and f.endswith('.json')])
    logger.info(f"Found {len(job_files)} job files to process")
    processed = 0
    success = 0
    error = 0
    for job_file in job_files:
        if '_removed' in job_file:
            job_id = job_file.replace('job', '').replace('_removed.json', '')
        else:
            job_id = job_file.replace('job', '').replace('.json', '')
        job_path = job_dir / job_file
        logger.info(f"Processing skills for job ID {job_id} ({processed+1} of {len(job_files)})")
        try:
            with open(job_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            job_data = process_job_skills(job_data, job_id)
            with open(job_path, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            success += 1
        except Exception as e:
            logger.error(f"Error processing skills for job {job_id}: {str(e)}")
            error += 1
        processed += 1
        if max_jobs and processed >= max_jobs:
            logger.info(f"Reached maximum number of jobs to process ({max_jobs})")
            break
    logger.info(f"Processing complete. Total: {processed}, Success: {success}, Error: {error}")
    return (processed, success, error)

def process_skills(max_jobs=None, job_ids=None, log_dir=None):
    """
    Process skills for job postings
    Args:
        max_jobs: Maximum number of jobs to process
        job_ids: Specific job IDs to process
        log_dir: Directory for log files
    Returns:
        bool: Success status
    """
    logger.info("Processing job skills...")
    if log_dir:
        skills_log_path = os.path.join(log_dir, "skills_module.log")
        skills_handler = logging.FileHandler(skills_log_path)
        skills_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(skills_handler)
        logger.info(f"Added log handler. Writing to {skills_log_path}")
    try:
        from run_pipeline.config.paths import SKILL_DATA_DIR, JOB_DATA_DIR
        os.makedirs(SKILL_DATA_DIR, exist_ok=True)
        load_caches()
        processed, success, error = process_job_files(
            job_dir=JOB_DATA_DIR,
            max_jobs=max_jobs,
            specific_job_ids=job_ids
        )
        save_caches()
        logger.info("=" * 50)
        logger.info("Job Skills Processing Summary")
        logger.info("=" * 50)
        logger.info(f"Total jobs processed: {processed}")
        logger.info(f"Successfully processed: {success}")
        logger.info(f"Errors: {error}")
        logger.info("=" * 50)
        return processed > 0
    except Exception as e:
        logger.error(f"Critical error in job skills processing: {str(e)}")
        return False

__all__ = [
    'process_skills',
    'load_caches',
    'save_caches',
    'skill_match_cache',
    'skill_decomposition_cache',
]
