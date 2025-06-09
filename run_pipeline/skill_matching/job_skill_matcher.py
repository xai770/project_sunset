import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import re
import requests

logger = logging.getLogger("job_skill_matcher")

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
postings_DIR = PROJECT_ROOT / "data" / "postings"
YOUR_SKILLS_FILE = PROJECT_ROOT / "profile" / "skills" / "skill_decompositions.json"

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")


def load_job_data(job_path: Path) -> Optional[Dict[str, Any]]:
    try:
        with open(job_path, "r", encoding="utf-8") as f:
            return json.load(f)  # type: ignore
    except Exception as e:
        logger.error(f"Failed to load job file {job_path}: {e}")
        return None

def save_job_data(job_path: Path, job_data: Dict[str, Any]) -> None:
    try:
        with open(job_path, "w", encoding="utf-8") as f:
            json.dump(job_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save job file {job_path}: {e}")

def load_your_skills() -> Optional[Dict[str, Any]]:
    if not YOUR_SKILLS_FILE.exists():
        logger.error(f"Your skills file not found: {YOUR_SKILLS_FILE}")
        return None
    try:
        with open(YOUR_SKILLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load your skills: {e}")
        return None

def domain_overlap(job_skill: Dict[str, Any], your_skill: Dict[str, Any]) -> float:
    # Simple domain overlap: intersection over union of domains
    job_domains = set(job_skill.get("domains", []))
    your_domains = set(your_skill.get("domains", []))
    if not job_domains or not your_domains:
        return 0.0
    intersection = job_domains & your_domains
    union = job_domains | your_domains
    return len(intersection) / len(union) if union else 0.0

def llm_domain_overlap(skill1: str, skill2: str) -> float:
    """
    Use Ollama LLM (e.g., Gemma) to compute domain overlap between two skills.
    Returns a float between 0 and 1 (compatibility percentage).
    """
    prompt = f"""Analyze domain overlap between:
SKILL 1: {skill1}
SKILL 2: {skill2}

Consider: domain relatedness, knowledge overlap, context similarity, function similarity.
Respond ONLY with a compatibility percentage (0-100)."""
    try:
        url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 512, "num_ctx": 4096}
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            text = data.get("response", "")
            match = re.search(r"(\d+(?:\.\d+)?)", text)
            if match:
                pct = float(match.group(1))
                return min(1.0, max(0.0, pct / 100.0))
        logger.warning(f"LLM response error: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"LLM domain overlap failed: {e}")
    return 0.0

def match_job_to_your_skills(job_data: Dict[str, Any], your_skills: Dict[str, Any], domain_threshold: float = 0.3) -> List[Dict[str, Any]]:
    # Match each job SDR skill to your skills using domain overlap
    job_sdr_skills = job_data.get("sdr_skills", {}).get("enriched", {})
    matches = []
    for job_skill_name, job_skill in job_sdr_skills.items():
        best_match = None
        best_score = 0.0
        for your_skill_name, your_skill in your_skills.items():
            score = domain_overlap(job_skill, your_skill)
            if score > best_score:
                best_score = score
                best_match = your_skill_name
        if best_score >= domain_threshold and best_match:
            matches.append({
                "job_skill": job_skill_name,
                "your_skill": best_match,
                "domain_overlap": best_score
            })
    return matches

def match_job_to_your_skills_llm(job_data: Dict[str, Any], your_skills: Dict[str, Any], threshold: float = 0.3) -> List[Dict[str, Any]]:
    # Match each job SDR skill to your skills using LLM-based domain overlap
    job_sdr_skills = job_data.get("sdr_skills", {}).get("enriched", {})
    matches = []
    for job_skill_name, job_skill in job_sdr_skills.items():
        best_match = None
        best_score = 0.0
        for your_skill_name, your_skill in your_skills.items():
            score = llm_domain_overlap(job_skill_name, your_skill_name)
            if score > best_score:
                best_score = score
                best_match = your_skill_name
        if best_score >= threshold and best_match:
            matches.append({
                "job_skill": job_skill_name,
                "your_skill": best_match,
                "llm_domain_overlap": best_score
            })
    return matches

def batch_match_all_jobs(domain_threshold: float = 0.3, use_llm: bool = True, job_ids: Optional[List[int]] = None) -> None:
    your_skills = load_your_skills()
    if not your_skills:
        logger.error("No user skills loaded. Aborting batch match.")
        return
    
    # Filter by job IDs if specified
    if job_ids:
        job_files = []
        for job_id in job_ids:
            job_path = postings_DIR / f"job{job_id}.json"
            if job_path.exists():
                job_files.append(job_path)
        logger.info(f"Found {len(job_files)} job files matching the specified IDs.")
    else:
        job_files = sorted(postings_DIR.glob("job*.json"))
        logger.info(f"Found {len(job_files)} job files to process for matching.")
    
    for i, job_path in enumerate(job_files):
        job_data = load_job_data(job_path)
        if not job_data:
            continue
        if use_llm:
            matches = match_job_to_your_skills_llm(job_data, your_skills, domain_threshold)
        else:
            matches = match_job_to_your_skills(job_data, your_skills, domain_threshold)
        # Calculate match percentage: percent of job SDR skills that have a match above threshold
        job_sdr_skills = job_data.get("sdr_skills", {}).get("enriched", {})
        total_skills = len(job_sdr_skills)
        match_percentage = (len(matches) / total_skills) if total_skills > 0 else 0.0
        job_data["skill_matches"] = {
            "matches": matches,
            "domain_threshold": domain_threshold,
            "llm": use_llm,
            "match_percentage": match_percentage,
            "timestamp": datetime.now().isoformat()
        }
        save_job_data(job_path, job_data)
        if (i+1) % 25 == 0 or i+1 == len(job_files):
            logger.info(f"Processed {i+1}/{len(job_files)} job files for skill matching.")
    logger.info(f"Batch skill matching complete. Updated {len(job_files)} job files.")

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Batch match CV skills to job SDR skills using LLM-based domain overlap.")
    parser.add_argument('--domain-threshold', type=float, default=0.3, help='Domain overlap threshold (default: 0.3)')
    parser.add_argument('--no-llm', action='store_true', help='Disable LLM-based matching (use basic domain overlap)')
    parser.add_argument('--job-ids', type=int, nargs='*', help='Specific job IDs to match (e.g., --job-ids 1 2 3)')
    args = parser.parse_args()
    batch_match_all_jobs(domain_threshold=args.domain_threshold, use_llm=not args.no_llm, job_ids=args.job_ids)
