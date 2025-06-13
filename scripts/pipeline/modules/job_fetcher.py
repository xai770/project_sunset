#!/usr/bin/env python3
"""
Job Fetcher Module
==================

Handles job fetching using the enhanced job fetcher with search criteria.
"""

import logging
from core.enhanced_job_fetcher import EnhancedJobFetcher
from core.beautiful_cli import print_info, print_success, print_warning, print_error, show_progress_spinner, display_job_summary
from .config_loader import load_search_criteria


def fetch_jobs(max_jobs=60, quick=False, profile_name="xai_frankfurt_focus", force_reprocess=False):
    """Fetch jobs using the beautiful enhanced fetcher with search criteria"""
    logger = logging.getLogger(__name__)
    logger.info("=== FETCHING JOBS (Phase 7) ===")
    
    print_info("Starting beautiful job fetching with integrated search criteria...")
    
    # Load search criteria
    search_criteria = load_search_criteria(profile_name)
    
    # Extract max jobs from search criteria if available
    criteria_max_jobs = search_criteria.get("fetching", {}).get("max_jobs_per_run", max_jobs)
    final_max_jobs = max_jobs if max_jobs > criteria_max_jobs else criteria_max_jobs
    
    # For Frankfurt focus, we want to get ALL Frankfurt jobs (~60)
    if "frankfurt" in profile_name.lower():
        final_max_jobs = max(final_max_jobs, 60)  # Ensure we get at least 60 jobs for Frankfurt
    
    show_progress_spinner("Initializing enhanced job fetcher...", 1.0)
    
    try:
        # Use the enhanced fetcher with beautiful JSON structure
        fetcher = EnhancedJobFetcher()
        job_count = 5 if quick else final_max_jobs
        
        print_info(f"Fetching up to {job_count} jobs using profile '{profile_name}' (quick_mode: {quick})")
        print_info(f"Search criteria: {search_criteria.get('description', 'No description')}")
        
        jobs = fetcher.fetch_jobs(max_jobs=job_count, quick_mode=quick, search_criteria=search_criteria, force_reprocess=force_reprocess)
        
        if jobs:
            print_success(f"Successfully fetched {len(jobs)} jobs with beautiful structure!")
            
            # Display summary using our beautiful CLI
            job_summary_data = []
            for job in jobs:
                job_summary_data.append({
                    'job_id': job['job_metadata']['job_id'],
                    'web_details': {'position_title': job['job_content']['title']},
                    'llama32_evaluation': {},  # Not evaluated yet
                    'search_details': {
                        'PositionLocation': [{
                            'CityName': job['job_content']['location']['city'],
                            'CountryName': job['job_content']['location']['country']
                        }]
                    }
                })
            
            display_job_summary(job_summary_data)
            logger.info(f"✅ Successfully fetched {len(jobs)} jobs using profile '{profile_name}'")
            return len(jobs)
        else:
            print_warning("No jobs were fetched")
            logger.warning("⚠️ No jobs were fetched") 
            return 0
            
    except Exception as e:
        logger.error(f"❌ Error during job fetching: {e}")
        print_error(f"Job fetching failed: {e}")
        return 0
