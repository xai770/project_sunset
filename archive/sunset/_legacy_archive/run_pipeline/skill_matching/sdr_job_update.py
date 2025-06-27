import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from run_pipeline.config.paths import JOB_DATA_DIR

logger = logging.getLogger("sdr_pipeline")

# Constants
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(project_root, 'docs', 'skill_matching')

def _create_skill_description(skill: Dict[str, Any]) -> str:
    description = ""
    if "contexts" in skill and len(skill["contexts"]) > 0:
        description += "Contexts: " + ", ".join(skill["contexts"][:3])
    if "functions" in skill and len(skill["functions"]) > 0:
        if description:
            description += ". "
        description += "Functions: " + ", ".join(skill["functions"][:3])
    if not description and "knowledge_components" in skill and len(skill["knowledge_components"]) > 0:
        description = "Knowledge areas: " + ", ".join(skill["knowledge_components"][:3])
    return description

def update_job_files_with_enriched_skills(
    enriched_skills: List[Dict[str, Any]], 
    max_jobs: Optional[int] = None, 
    job_ids: Optional[List[int]] = None,
    force_reprocess: bool = False
) -> List[str]:
    logger.info(f"Starting job file updates with {len(enriched_skills)} enriched skills")
    skill_map = {skill['name']: skill for skill in enriched_skills}
    skill_names = set(skill_map.keys())
    relationships_file = os.path.join(OUTPUT_DIR, 'skill_relationships.json')
    relationships = {}
    if os.path.exists(relationships_file):
        try:
            with open(relationships_file, 'r') as f:
                relationships = json.load(f)
            logger.info(f"Loaded relationships for {len(relationships)} skills")
        except Exception as e:
            logger.warning(f"Could not load relationships file: {e}")
    job_dir = Path(JOB_DATA_DIR)
    updated_files = []
    if job_ids:
        job_files = []
        for job_id in job_ids:
            job_file = job_dir / f"job{job_id}.json"
            removed_file = job_dir / f"job{job_id}_removed.json"
            if job_file.exists():
                job_files.append(job_file)
            elif removed_file.exists():
                job_files.append(removed_file)
    else:
        job_files = sorted(list(job_dir.glob("job*.json")))
        if max_jobs and max_jobs < len(job_files):
            job_files = job_files[:max_jobs]
    logger.info(f"Found {len(job_files)} job files to process")
    for i, job_file in enumerate(job_files):
        job_id_str = job_file.stem.replace("job", "").split("_")[0]
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            if not force_reprocess and "sdr_skills" in job_data:
                logger.debug(f"Skipping job {job_id_str} - already has SDR skills")
                continue
            job_skills = []
            if "skills" in job_data and "extracted" in job_data["skills"]:
                job_skills = job_data["skills"]["extracted"]
            matched_skills = {}
            for skill_name in job_skills:
                if skill_name in skill_names:
                    matched_skills[skill_name] = skill_map[skill_name]
            if not matched_skills:
                logger.debug(f"No skills matched for job {job_id_str}")
                continue
            if "sdr_skills" not in job_data:
                job_data["sdr_skills"] = {}
            job_data["sdr_skills"]["enriched"] = {
                name: {
                    "category": skill["category"],
                    "description": _create_skill_description(skill),
                    "domains": skill.get("domains", []),
                    "knowledge_components": skill.get("knowledge_components", []),
                    "proficiency_levels": skill.get("proficiency_levels", {}),
                    "sdr_enriched": True,
                    "contexts": skill.get("contexts", []),
                    "functions": skill.get("functions", [])
                } for name, skill in matched_skills.items()
            }
            job_domains = {}
            for skill_name in matched_skills.keys():
                if skill_name in relationships:
                    job_domains[skill_name] = relationships[skill_name]
            job_data["sdr_skills"]["relationships"] = job_domains
            job_data["sdr_skills"]["metadata"] = {
                "timestamp": datetime.now().isoformat(),
                "enriched_skill_count": len(matched_skills),
                "source": "sdr_pipeline"
            }
            if "log" not in job_data:
                job_data["log"] = []
            job_data["log"].append({
                "timestamp": datetime.now().isoformat(),
                "script": "run_pipeline.skill_matching.sdr_job_update",
                "action": "update_sdr_skills",
                "message": f"Added {len(matched_skills)} SDR-enriched skills"
            })
            with open(job_file, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            updated_files.append(str(job_file))
            if (i+1) % 100 == 0 or i+1 == len(job_files):
                logger.info(f"Processed {i+1}/{len(job_files)} job files")
        except Exception as e:
            logger.error(f"Error processing job {job_id_str}: {str(e)}")
    logger.info(f"Updated {len(updated_files)} job files with SDR-enriched skills")
    return updated_files
