#!/usr/bin/env python3
"""
Job File Updater for SDR Integration

This module updates job files with SDR-enriched skills, ensuring that each job posting
contains enhanced skill definitions with rich metadata like knowledge components,
proficiency levels, and domain relationships.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the project root to the path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import paths configuration
from run_pipeline.config.paths import JOB_DATA_DIR

# Configure logging
logger = logging.getLogger("sdr_job_updater")

def map_enriched_skills(enriched_skills: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Maps enriched skills to a dictionary for faster lookup
    
    Args:
        enriched_skills: List of enriched skill definitions from the SDR pipeline
        
    Returns:
        Dictionary mapping skill names to their enriched definitions
    """
    skill_map = {}
    
    for skill in enriched_skills:
        skill_name = skill['name']
        # Create a description by combining contexts and functions if exists
        description = ""
        if 'contexts' in skill and len(skill['contexts']) > 0:
            description += "Contexts: " + ", ".join(skill['contexts'][:3])
        if 'functions' in skill and len(skill['functions']) > 0:
            if description:
                description += ". "
            description += "Functions: " + ", ".join(skill['functions'][:3])
            
        skill_map[skill_name] = {
            "category": skill['category'],
            "description": description,
            "domains": skill.get('domains', []),
            "knowledge_components": skill.get('knowledge_components', []),
            "proficiency_levels": skill.get('proficiency_levels', {}),
            "sdr_enriched": True,
            "contexts": skill.get('contexts', []),
            "functions": skill.get('functions', [])
        }
    
    return skill_map

def update_job_file(
    job_path: str, 
    enriched_skill_map: Dict[str, Dict[str, Any]],
    relationships: Dict[str, Dict[str, Dict[str, Any]]],
    dry_run: bool = False
) -> bool:
    """
    Update a job file with SDR-enriched skills
    
    Args:
        job_path: Path to the job file
        enriched_skill_map: Dictionary mapping skill names to their enriched definitions
        relationships: Dictionary of skill relationships
        dry_run: If True, don't actually modify the file
        
    Returns:
        bool: Success status
    """
    try:
        # Read job data
        with open(job_path, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
        
        # Extract job ID from filename
        job_id = os.path.basename(job_path).replace('job', '').replace('_removed.json', '').replace('.json', '')
        
        # Check if the job has skills
        if "skills" not in job_data or "extracted" not in job_data["skills"]:
            logger.warning(f"Job {job_id} has no extracted skills, skipping")
            return False
        
        # Create SDR skills section
        if "sdr_skills" not in job_data:
            job_data["sdr_skills"] = {}
        
        # Map extracted skills to enriched skills
        extracted_skills = job_data["skills"]["extracted"]
        matched_enriched_skills = {}
        skill_matches_count = 0
        
        for skill_name in extracted_skills:
            # Check if the skill exists in our enriched skills
            if skill_name in enriched_skill_map:
                matched_enriched_skills[skill_name] = enriched_skill_map[skill_name]
                skill_matches_count += 1
        
        # Set the enriched skills in the job data
        job_data["sdr_skills"]["enriched"] = matched_enriched_skills
        
        # Add domain relationships for this job's skills
        job_domains = {}
        for skill_name in matched_enriched_skills:
            if skill_name in relationships:
                job_domains[skill_name] = relationships[skill_name]
        
        job_data["sdr_skills"]["relationships"] = job_domains
        
        # Add metadata
        job_data["sdr_skills"]["metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "enriched_skill_count": skill_matches_count,
            "source": "sdr_pipeline"
        }
        
        # Add log entry
        if "log" not in job_data:
            job_data["log"] = []
        
        job_data["log"].append({
            "timestamp": datetime.now().isoformat(),
            "script": "run_pipeline.skill_matching.sdr_pipeline",
            "action": "update_sdr_skills",
            "message": f"Added {skill_matches_count} SDR-enriched skills"
        })
        
        if not dry_run:
            # Save updated job data
            with open(job_path, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Updated job {job_id} with {skill_matches_count} SDR-enriched skills")
        else:
            logger.info(f"[DRY RUN] Would update job {job_id} with {skill_matches_count} SDR-enriched skills")
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating job file {job_path}: {str(e)}")
        return False

def update_all_job_files(
    enriched_skills: List[Dict[str, Any]], 
    relationships: Dict[str, Dict[str, Dict[str, Any]]],
    job_ids: Optional[List[int]] = None,
    max_jobs: Optional[int] = None,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Update all job files with SDR-enriched skills
    
    Args:
        enriched_skills: List of enriched skill definitions
        relationships: Dictionary of skill relationships
        job_ids: List of specific job IDs to update
        max_jobs: Maximum number of jobs to update
        dry_run: If True, don't actually modify the files
        
    Returns:
        Dict with counts of processed, successful, and error updates
    """
    logger.info("Starting job file updates with SDR-enriched skills")
    
    # Map skills to format expected in job files
    enriched_skill_map = map_enriched_skills(enriched_skills)
    
    # Get job files
    job_dir = Path(JOB_DATA_DIR)
    
    if job_ids:
        job_files = []
        for job_id in job_ids:
            # Check both regular and _removed job files
            job_file = f"job{job_id}.json"
            removed_file = f"job{job_id}_removed.json"
            
            if (job_dir / job_file).exists():
                job_files.append(job_file)
            elif (job_dir / removed_file).exists():
                job_files.append(removed_file)
    else:
        # Get all job files
        job_files = sorted([f for f in os.listdir(job_dir) 
                  if f.startswith('job') and f.endswith('.json')])
    
    logger.info(f"Found {len(job_files)} job files to update")
    
    if max_jobs is not None and max_jobs < len(job_files):
        job_files = job_files[:max_jobs]
        logger.info(f"Limiting to {max_jobs} jobs")
    
    # Process counters
    processed = 0
    success = 0
    error = 0
    
    # Update each job file
    for job_file in job_files:
        job_path = job_dir / job_file
        
        try:
            if update_job_file(str(job_path), enriched_skill_map, relationships, dry_run):
                success += 1
            else:
                error += 1
                
        except Exception as e:
            logger.error(f"Error processing {job_file}: {str(e)}")
            error += 1
        
        processed += 1
    
    # Print summary
    logger.info("=" * 50)
    logger.info("Job Update Summary")
    logger.info("=" * 50)
    logger.info(f"Total jobs processed: {processed}")
    logger.info(f"Successfully updated: {success}")
    logger.info(f"Errors: {error}")
    logger.info("=" * 50)
    
    return {
        "processed": processed,
        "success": success,
        "error": error
    }
