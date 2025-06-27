#!/usr/bin/env python3
"""
Data Bridge Module

Handles data structure bridging and compatibility between different components
of the pipeline. This module ensures that job data from different sources
(JobFetcherP5, legacy systems, etc.) is compatible with Excel export and
other pipeline components.
"""

import logging
import sys
import json
import glob
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

def bridge_job_data_structure() -> int:
    """
    Bridge function to ensure compatibility between JobFetcherP5 and legacy Excel export
    
    Returns:
        Number of job files updated
    """
    logger.info("🔧 Bridging job data structure for Excel export compatibility...")
    
    # Find all job files in data/postings
    job_files = glob.glob(str(project_root / "data" / "postings" / "job*.json"))
    updated_count = 0
    
    for job_file in job_files:
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            # Check if this job needs structure bridging
            needs_update = False
            
            # If job has 'title' but no 'web_details.position_title', create the bridge
            if 'title' in job_data and ('web_details' not in job_data or 
                                       'position_title' not in job_data.get('web_details', {})):
                
                # Ensure web_details exists
                if 'web_details' not in job_data:
                    job_data['web_details'] = {}
                
                # Bridge the title
                job_data['web_details']['position_title'] = job_data['title']
                needs_update = True
            
            # Bridge other common fields for Excel export compatibility
            if 'raw_data' in job_data and isinstance(job_data['raw_data'], dict):
                raw_data = job_data['raw_data']
                
                # Extract from MatchedObjectDescriptor if available
                if 'MatchedObjectDescriptor' in raw_data:
                    descriptor = raw_data['MatchedObjectDescriptor']
                    
                    # Bridge location
                    if 'LocationName' in descriptor and 'location' not in job_data.get('web_details', {}):
                        if 'web_details' not in job_data:
                            job_data['web_details'] = {}
                        job_data['web_details']['location'] = descriptor['LocationName']
                        needs_update = True
                    
                    # Bridge department/organizational unit
                    if 'OrganizationalUnit' in descriptor and 'department' not in job_data.get('web_details', {}):
                        if 'web_details' not in job_data:
                            job_data['web_details'] = {}
                        job_data['web_details']['department'] = descriptor['OrganizationalUnit']
                        needs_update = True
            
            # Save updated job data if changes were made
            if needs_update:
                with open(job_file, 'w') as f:
                    json.dump(job_data, f, indent=2)
                updated_count += 1
                
        except Exception as e:
            logger.warning(f"⚠️ Could not bridge job file {job_file}: {e}")
    
    logger.info(f"✅ Bridged data structure for {updated_count} job files")
    return updated_count

def normalize_job_structure(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a single job data structure to ensure compatibility
    
    Args:
        job_data: Raw job data dictionary
        
    Returns:
        Normalized job data dictionary
    """
    normalized = job_data.copy()
    
    # Ensure required top-level fields exist
    if 'web_details' not in normalized:
        normalized['web_details'] = {}
    
    if 'job_content' not in normalized:
        normalized['job_content'] = {}
    
    # Bridge title fields
    title = (normalized.get('title') or 
             normalized.get('web_details', {}).get('position_title') or 
             normalized.get('job_content', {}).get('title') or 
             'Unknown Position')
    
    normalized['title'] = title
    normalized['web_details']['position_title'] = title
    normalized['job_content']['title'] = title
    
    # Bridge location fields
    location = (normalized.get('web_details', {}).get('location') or 
                normalized.get('job_content', {}).get('location', {}).get('city') or 
                'Frankfurt am Main, Germany')
    
    normalized['web_details']['location'] = location
    
    # Ensure job_content has proper structure
    if 'location' not in normalized['job_content']:
        normalized['job_content']['location'] = {
            'city': 'Frankfurt am Main',
            'country': 'Germany',
            'remote_options': False
        }
    
    # Ensure employment details exist
    if 'employment_details' not in normalized['job_content']:
        normalized['job_content']['employment_details'] = {
            'type': 'Full-time',
            'schedule': 'Regular',
            'career_level': 'Professional'
        }
    
    # Ensure organization details exist
    if 'organization' not in normalized['job_content']:
        normalized['job_content']['organization'] = {
            'name': 'Deutsche Bank',
            'division': 'Unknown'
        }
    
    return normalized

def validate_job_structure(job_data: Dict[str, Any]) -> List[str]:
    """
    Validate job data structure and return list of issues
    
    Args:
        job_data: Job data to validate
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    # Check required top-level fields
    required_fields = ['title', 'web_details', 'job_content']
    for field in required_fields:
        if field not in job_data:
            issues.append(f"Missing required field: {field}")
    
    # Check web_details structure
    if 'web_details' in job_data:
        web_details = job_data['web_details']
        if 'position_title' not in web_details:
            issues.append("Missing web_details.position_title")
        if 'location' not in web_details:
            issues.append("Missing web_details.location")
    
    # Check job_content structure
    if 'job_content' in job_data:
        job_content = job_data['job_content']
        if 'title' not in job_content:
            issues.append("Missing job_content.title")
        if 'description' not in job_content:
            issues.append("Missing job_content.description")
    
    return issues

def bridge_all_job_files() -> Dict[str, int]:
    """
    Bridge all job files in the data directory
    
    Returns:
        Dictionary with bridging statistics
    """
    logger.info("🔧 Starting comprehensive job data bridging...")
    
    stats = {
        'total_files': 0,
        'updated_files': 0,
        'error_files': 0,
        'valid_files': 0
    }
    
    job_files = glob.glob(str(project_root / "data" / "postings" / "job*.json"))
    stats['total_files'] = len(job_files)
    
    for job_file in job_files:
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            # Validate current structure
            issues = validate_job_structure(job_data)
            
            if issues:
                # Normalize the structure
                normalized_data = normalize_job_structure(job_data)
                
                # Validate after normalization
                remaining_issues = validate_job_structure(normalized_data)
                
                if len(remaining_issues) < len(issues):
                    # Save improved structure
                    with open(job_file, 'w') as f:
                        json.dump(normalized_data, f, indent=2)
                    stats['updated_files'] += 1
                    logger.debug(f"✅ Updated job file: {job_file}")
                else:
                    stats['error_files'] += 1
                    logger.warning(f"⚠️ Could not fully normalize: {job_file}")
            else:
                stats['valid_files'] += 1
                logger.debug(f"✅ Job file already valid: {job_file}")
                
        except Exception as e:
            stats['error_files'] += 1
            logger.error(f"❌ Error processing {job_file}: {e}")
    
    logger.info(f"🔧 Bridging complete: {stats['updated_files']} updated, "
                f"{stats['valid_files']} already valid, {stats['error_files']} errors")
    
    return stats

def create_test_job_data(job_id: str = "test123") -> Dict[str, Any]:
    """
    Create test job data with proper structure for testing
    
    Args:
        job_id: Job ID for the test data
        
    Returns:
        Test job data dictionary
    """
    from datetime import datetime
    
    return {
        "job_id": job_id,
        "title": f"Test Position {job_id}",
        "web_details": {
            "position_title": f"Test Position {job_id}",
            "location": "Frankfurt am Main, Germany",
            "department": "Test Department"
        },
        "job_content": {
            "title": f"Test Position {job_id}",
            "description": "This is a test job description for validation purposes.",
            "requirements": ["Test requirement 1", "Test requirement 2"],
            "location": {
                "city": "Frankfurt am Main",
                "country": "Germany",
                "remote_options": False
            },
            "employment_details": {
                "type": "Full-time",
                "schedule": "Regular",
                "career_level": "Professional"
            },
            "organization": {
                "name": "Deutsche Bank",
                "division": "Test Division"
            }
        },
        "evaluation_results": {
            "cv_to_role_match": None,
            "match_confidence": None
        },
        "processing_log": [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "test_creation",
                "processor": "data_bridge_module",
                "status": "success",
                "details": f"Created test job data for {job_id}"
            }
        ],
        "raw_source_data": {
            "description_source": "test_creation"
        }
    }

if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    print("Testing data bridge module...")
    
    # Test job structure validation
    test_job = create_test_job_data("test123")
    issues = validate_job_structure(test_job)
    print(f"Test job validation issues: {len(issues)}")
    
    # Test bridging (dry run)
    stats = bridge_all_job_files()
    print(f"Bridging stats: {stats}")
    
    print("Data bridge module ready for use")
