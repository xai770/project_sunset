#!/usr/bin/env python3
"""
Job Format Adapter for Project Sunset Phase 7
============================================

Provides compatibility between the new beautiful JSON structure 
and legacy processors that expect the old web_details format.

This adapter allows seamless transition while maintaining backward compatibility.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

def convert_enhanced_to_legacy_format(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert enhanced JSON structure to legacy web_details format
    
    Args:
        job_data: Job data in enhanced format
        
    Returns:
        Job data in legacy format compatible with existing processors
    """
    # If already in legacy format, return as-is
    if "web_details" in job_data:
        return job_data
    
    # Check if this is the new enhanced format
    if "job_metadata" not in job_data or "job_content" not in job_data:
        logger.warning("Unknown job data format - returning as-is")
        return job_data
    
    logger.info("Converting enhanced JSON format to legacy web_details format")
    
    # Extract data from enhanced structure
    metadata = job_data.get("job_metadata", {})
    content = job_data.get("job_content", {})
    location = content.get("location", {})
    employment = content.get("employment_details", {})
    organization = content.get("organization", {})
    
    # Build description from available content
    title = content.get("title", "")
    description = content.get("description", "")
    requirements = content.get("requirements", [])
    
    # Create concise description if we have content
    concise_description = ""
    if title:
        concise_description = f"Position Title: {title}\n\n"
    
    if description:
        concise_description += f"Description:\n{description}\n\n"
    elif not description and title:
        # Create basic description from title if no description available
        concise_description += f"This is a {title} position at {organization.get('name', 'Deutsche Bank')}.\n\n"
    
    if requirements:
        concise_description += "Requirements:\n"
        for req in requirements:
            concise_description += f"- {req}\n"
        concise_description += "\n"
    
    # Build location string
    location_parts = []
    if location.get("city"):
        location_parts.append(location["city"])
    if location.get("state"):
        location_parts.append(location["state"])
    if location.get("country"):
        location_parts.append(location["country"])
    location_str = ", ".join(location_parts)
    
    # Create legacy format
    legacy_data = {
        "job_id": metadata.get("job_id", ""),
        "title": title,
        "web_details": {
            "position_title": title,
            "concise_description": concise_description.strip() or f"Position: {title}",
            "url": f"https://careers.db.com/professionals/search-roles/#/professional/job/{metadata.get('job_id', '')}",
            "location": location_str,
            "career_level": employment.get("career_level", ""),
            "employment_type": employment.get("type", ""),
            "schedule": employment.get("schedule", ""),
            "organization": organization.get("name", "Deutsche Bank"),
            "division": organization.get("division", ""),
            "description_metadata": {
                "timestamp": metadata.get("created_at", ""),
                "model_used": "enhanced_job_fetcher",
                "is_placeholder": not bool(description),
                "extraction_status": "converted_from_enhanced",
                "source": metadata.get("source", "deutsche_bank_api")
            }
        },
        # Copy any existing evaluation results
        "llama32_evaluation": job_data.get("evaluation_results", {}),
        # Preserve original enhanced data
        "enhanced_format": job_data
    }
    
    logger.info(f"Successfully converted job {metadata.get('job_id', 'unknown')} to legacy format")
    return legacy_data

def ensure_legacy_compatibility(job_id: str, postings_dir: Path) -> bool:
    """
    Ensure a job file is in legacy-compatible format
    
    Args:
        job_id: Job ID to process
        postings_dir: Directory containing job files
        
    Returns:
        True if conversion was successful or not needed
    """
    job_file = postings_dir / f"job{job_id}.json"
    
    if not job_file.exists():
        logger.error(f"Job file {job_file} not found")
        return False
    
    try:
        # Load job data
        with open(job_file, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
        
        # Convert if needed
        converted_data = convert_enhanced_to_legacy_format(job_data)
        
        # Save back if conversion happened
        if converted_data != job_data:
            with open(job_file, 'w', encoding='utf-8') as f:
                json.dump(converted_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Updated job {job_id} to legacy-compatible format")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to ensure legacy compatibility for job {job_id}: {e}")
        return False

def batch_convert_jobs(job_ids: list, postings_dir: Path) -> Dict[str, bool]:
    """
    Convert multiple jobs to legacy format
    
    Args:
        job_ids: List of job IDs to convert
        postings_dir: Directory containing job files
        
    Returns:
        Dictionary mapping job_id to success status
    """
    results = {}
    
    for job_id in job_ids:
        try:
            results[job_id] = ensure_legacy_compatibility(job_id, postings_dir)
            if results[job_id]:
                logger.info(f"✅ Job {job_id} ready for processing")
            else:
                logger.error(f"❌ Job {job_id} conversion failed")
        except Exception as e:
            logger.error(f"❌ Error converting job {job_id}: {e}")
            results[job_id] = False
    
    successful = sum(1 for success in results.values() if success)
    total = len(job_ids)
    logger.info(f"Conversion summary: {successful}/{total} jobs successfully converted")
    
    return results

if __name__ == "__main__":
    # Test with the newly fetched jobs
    import sys
    from pathlib import Path
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test conversion
    postings_dir = Path("/home/xai/Documents/sunset/data/postings")
    test_jobs = ["63183", "64222", "64223", "64226", "64227"]
    
    print("🔄 Testing job format conversion...")
    results = batch_convert_jobs(test_jobs, postings_dir)
    
    success_count = sum(1 for success in results.values() if success)
    print(f"✅ Conversion complete: {success_count}/{len(test_jobs)} jobs converted successfully")
