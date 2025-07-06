#!/usr/bin/env python3
"""
Project Sunset - Enhanced Job Fetcher Phase 6
============================================

Beautiful, modern job fetcher with:
• Clean JSON structure with proper logging
• Full job description fetching  
• Robust error handling and fallback mechanisms
• Integration with your configuration system

Author: GitHub Copilot 💜
Date: June 11, 2025  
Version: 6.1.0 (Enhanced with Beautiful Structure)
"""

import json
import logging
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import sys
import re
from urllib.parse import urljoin
import hashlib
from bs4 import BeautifulSoup

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import DirectSpecialistManager
from core.config_manager import get_config

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedJobFetcher:
    """
    Enhanced job fetcher with beautiful JSON structure and full description support
    """
    
    def __init__(self):
        self.config = get_config()
        self.logger = self._setup_logging()
        self.specialist_manager = DirectSpecialistManager()
        
        # Directory setup
        self.data_dir = self.config.job_data_dir
        self.scan_progress_file = self.data_dir.parent / "job_scans" / "search_api_scan_progress.json"
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.scan_progress_file.parent.mkdir(parents=True, exist_ok=True)
        
        # API Configuration
        self.api_base_url = "https://api-deutschebank.beesite.de/search/"
        self.career_site_base = "https://careers.db.com"
        self.api_headers = {
            "Content-Type": "application/json",
            "User-Agent": self.config.job_search.user_agent
        }
        
        self.logger.info("✨ Enhanced Job Fetcher initialized with beautiful architecture!")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup beautiful logging with proper duplicate handler prevention"""
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Prevent duplicate handlers by checking if any handlers exist for this specific logger
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            # Prevent propagation to root logger to avoid double logging
            logger.propagate = False
        return logger
    
    def create_beautiful_job_structure(self, 
                                     job_api_data: Dict[str, Any], 
                                     job_description: str = "", 
                                     specialist_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create the beautiful JSON structure you designed
        """
        descriptor = job_api_data.get("MatchedObjectDescriptor", {})
        job_id = job_api_data.get("MatchedObjectId", "unknown")
        
        # Extract location data
        location_data = descriptor.get("PositionLocation", [{}])[0] if descriptor.get("PositionLocation") else {}
        
        # Extract employment details
        employment_type = descriptor.get("PositionOfferingType", [{}])[0].get("Name", "") if descriptor.get("PositionOfferingType") else ""
        schedule = descriptor.get("PositionSchedule", [{}])[0].get("Name", "") if descriptor.get("PositionSchedule") else ""
        career_level = descriptor.get("CareerLevel", [{}])[0].get("Name", "") if descriptor.get("CareerLevel") else ""
        
        # Create processing log entry
        now = datetime.now().isoformat()
        processing_log = [
            {
                "timestamp": now,
                "action": "job_fetched",
                "processor": "enhanced_job_fetcher_v6.1",
                "status": "success",
                "details": f"Successfully fetched job {job_id} from Deutsche Bank API"
            }
        ]
        
        # Add description enrichment log if we got it
        if job_description:
            processing_log.append({
                "timestamp": now,
                "action": "description_enriched", 
                "processor": "web_scraper",
                "status": "success",
                "details": f"Successfully fetched job description ({len(job_description)} characters)"
            })
        else:
            processing_log.append({
                "timestamp": now,
                "action": "description_enriched",
                "processor": "web_scraper", 
                "status": "partial_failure",
                "details": "Job description not available from source",
                "warning": "Description field will be empty"
            })
        
        # Add specialist analysis log if available
        if specialist_analysis:
            processing_log.append({
                "timestamp": now,
                "action": "specialist_analysis",
                "processor": "direct_specialist_manager",
                "status": "success",
                "details": f"Specialist analysis completed with {specialist_analysis.get('specialist_used', 'unknown')} specialist"
            })
        
        # Create the beautiful structure
        beautiful_job = {
            "job_metadata": {
                "job_id": job_id,
                "version": "1.0",
                "created_at": now,
                "last_modified": now,
                "source": "deutsche_bank_api",
                "processor": "enhanced_job_fetcher_v6.1",
                "status": "fetched"
            },
            
            "job_content": {
                "title": descriptor.get("PositionTitle", ""),
                "description": job_description,
                "requirements": self._extract_requirements(job_description),
                "location": {
                    "city": location_data.get("CityName", ""),
                    "state": location_data.get("CountrySubDivisionName", ""),
                    "country": location_data.get("CountryName", ""),
                    "remote_options": False  # Default, could be enhanced
                },
                "employment_details": {
                    "type": employment_type,
                    "schedule": schedule,
                    "career_level": career_level,
                    "salary_range": None,  # Not available in API
                    "benefits": []  # Could be extracted from description
                },
                "organization": {
                    "name": "Deutsche Bank",
                    "division": descriptor.get("OrganizationName", ""),
                    "division_id": descriptor.get("UserArea", {}).get("ProDivision")
                },
                "posting_details": {
                    "publication_date": descriptor.get("PublicationStartDate", ""),
                    "position_uri": descriptor.get("PositionURI", ""),
                    "hiring_year": descriptor.get("PositionHiringYear", "")
                }
            },
            
            "evaluation_results": {
                # Will be populated later during evaluation
                "cv_to_role_match": None,
                "match_confidence": None,
                "evaluation_date": None,
                "evaluator": None,
                "domain_knowledge_assessment": None,
                "decision": {
                    "apply": None,
                    "rationale": None,
                    "estimated_prep_time": None
                },
                "strengths": [],
                "weaknesses": []
            },
            
            "processing_log": processing_log,
            
            "raw_source_data": {
                "api_response": job_api_data,
                "specialist_analysis": specialist_analysis or {},
                "description_source": "web_scraping" if job_description else "unavailable"
            }
        }
        
        return beautiful_job
    
    def _extract_requirements(self, description: str) -> List[str]:
        """
        Extract requirements from job description using simple pattern matching
        """
        if not description:
            return []
            
        requirements = []
        
        # Look for common requirement patterns
        patterns = [
            r"(?:require[sd]?|must have|essential|mandatory):\s*(.+?)(?:\n|$)",
            r"(?:qualifications?|requirements?):\s*(.+?)(?:\n|$)",
            r"(?:experience in|experience with|knowledge of)\s+(.+?)(?:\n|,|$)",
            r"(?:minimum|at least)\s+(\d+\+?\s*years?.+?)(?:\n|,|$)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                clean_req = match.strip().rstrip('.,;')
                if clean_req and len(clean_req) > 10:  # Filter out too short matches
                    requirements.append(clean_req)
        
        return list(set(requirements))  # Remove duplicates
    
    def _should_skip_existing_job(self, job_file: Path, job_id: str, allow_processed: bool = False) -> bool:
        """
        Check if an existing job file should be skipped because it contains valuable AI analysis data.
        
        Args:
            job_file (Path): Path to the existing job file
            job_id (str): Job ID for logging
            allow_processed (bool): If True, will not skip processed jobs
            
        Returns:
            bool: True if the job should be skipped (has valuable data), False if it should be updated
        """
        if allow_processed:
            return False
            
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                existing_job = json.load(f)
            
            # Check for valuable AI analysis fields that indicate processing has been done
            valuable_ai_fields = [
                'llama32_evaluation',
                'cv_analysis', 
                'skill_match',
                'domain_enhanced_match',
                'ai_processed',
                'evaluation_results',
                'job_insights'  # Added to catch any processed jobs
            ]
            
            # If any valuable AI fields exist, skip this job
            for field in valuable_ai_fields:
                if existing_job.get(field):
                    logger.debug(f"Skipping job {job_id} - contains valuable {field} data")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking job {job_id}: {str(e)}")
            return False  # Don't skip on error
    
    def fetch_job_description(self, job_id: str, position_uri: str = "") -> str:
        """
        Fetch full job description using the working API approach
        """
        try:
            # Use the proven API endpoint for job details
            api_url = f"https://api-deutschebank.beesite.de/jobhtml/{job_id}.json"
            
            self.logger.info(f"🔍 Fetching description for job {job_id} from API")
            
            response = requests.get(api_url, headers=self.api_headers, timeout=15)
            
            if response.status_code == 200:
                try:
                    job_data = response.json()
                    
                    # Extract HTML content
                    html_content = job_data.get('html', '').strip()
                    
                    if html_content:
                        # Clean the HTML and extract meaningful text
                        import re
                        
                        # Parse HTML properly
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get clean text
                        text_content = soup.get_text()
                        
                        # Clean up whitespace
                        text_content = re.sub(r'\s+', ' ', text_content).strip()
                        
                        if len(text_content) > 100:
                            self.logger.info(f"✅ Found description: {len(text_content)} characters")
                            return text_content
                    
                    self.logger.warning(f"⚠️ No HTML content found for job {job_id}")
                    return ""
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"❌ Failed to parse API response for job {job_id}: {e}")
                    return ""
            else:
                self.logger.warning(f"⚠️ API request failed for job {job_id}: Status {response.status_code}")
                return ""
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching description for job {job_id}: {e}")
            return ""
    
    def _get_existing_job_ids(self) -> set:
        """Get a set of job IDs that already exist in the data directory"""
        job_files = self.data_dir.glob("job*.json")
        return {f.stem.replace('job', '') for f in job_files}

    def fetch_jobs(self, max_jobs: int = 60, quick_mode: bool = False, search_criteria: Optional[Dict] = None, force_reprocess: bool = False, allow_processed: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch jobs with beautiful structure and full descriptions
        Uses search criteria for Frankfurt-focused job retrieval
        """
        if quick_mode:
            max_jobs = min(max_jobs, self.config.job_search.quick_mode_limit)
            
        # Track which jobs we've seen to ensure we find enough new ones
        existing_job_ids = self._get_existing_job_ids()
        current_job_count = 0
        page = 1
        page_size = max(max_jobs * 2, 100)  # Request more jobs to find new ones
        enhanced_jobs = []
        
        while current_job_count < max_jobs:
            # Load search criteria if not provided
            if search_criteria is None:
                try:
                    search_criteria_path = project_root / "config" / "search_criteria.json"
                    with open(search_criteria_path, 'r') as f:
                        config_data = json.load(f)
                    search_criteria = config_data.get("search_profiles", {}).get("xai_frankfurt_focus", {})
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not load search criteria: {e}")
                    search_criteria = {}
            
            # Extract location criteria for Frankfurt focus
            location_criteria = search_criteria.get("criteria", {}).get("locations", {}) if search_criteria else {}
            country_codes = location_criteria.get("country_codes", [46])  # Germany
            city_codes = location_criteria.get("city_codes", [1698])      # Frankfurt
            
            self.logger.info(f"🚀 Fetching up to {page_size} jobs (quick_mode: {quick_mode})")
            self.logger.info(f"🎯 Using search criteria: Country codes {country_codes}, City codes {city_codes}")
            
            # Prepare API request with search criteria
            search_criteria_list = []
            
            # Add country filter
            if country_codes:
                search_criteria_list.append({
                    "CriterionName": "PositionLocation.Country",
                    "CriterionValue": country_codes[0]  # Use first country code
                })
            
            # Add city filter
            if city_codes:
                search_criteria_list.append({
                    "CriterionName": "PositionLocation.City", 
                    "CriterionValue": city_codes[0]  # Use first city code
                })
            
            api_params = {
                "LanguageCode": "en",
                "SearchParameters": {
                    "FirstItem": (page - 1) * page_size + 1,
                    "CountItem": page_size,
                    "MatchedObjectDescriptor": [
                        "PositionID",
                        "PositionTitle",
                        "PositionURI",
                        "PositionFormattedDescription.Content",  
                        "PositionLocation.CountryName",
                        "PositionLocation.CountrySubDivisionName", 
                        "PositionLocation.CityName",
                        "OrganizationName",
                        "PositionOfferingType.Name",
                        "PositionSchedule.Name",
                        "CareerLevel.Name",
                        "PublicationStartDate",
                        "PositionHiringYear",
                        "UserArea.ProDivision"
                    ],
                    "Sort": [{"Criterion": "PublicationStartDate", "Direction": "DESC"}]
                },
                "SearchCriteria": search_criteria_list
            }
            
            try:
                response = requests.post(
                    self.api_base_url,
                    json=api_params,
                    headers=self.api_headers,
                    timeout=30
                )
                
                if response.status_code != 200:
                    self.logger.error(f"❌ API request failed: {response.status_code}")
                    break
                
                data = response.json()
                
                if "SearchResult" not in data or "SearchResultItems" not in data["SearchResult"]:
                    self.logger.error("❌ Invalid API response structure")
                    break
                
                jobs = data["SearchResult"]["SearchResultItems"]
                self.logger.info(f"📥 Received {len(jobs)} jobs from API")
                
                if not jobs:  # No more jobs found
                    break
                
                for job in jobs:
                    job_id = job.get("MatchedObjectId", "")
                    if not job_id:
                        continue
                        
                    # Skip if we already have enough jobs
                    if current_job_count >= max_jobs:
                        break
                        
                    # Skip if we've already seen this job and we're not reprocessing
                    if job_id in existing_job_ids and not allow_processed and not force_reprocess:
                        continue
                    
                    try:
                        job_file = self.data_dir / f"job{job_id}.json"
                        if job_file.exists() and not force_reprocess:
                            if allow_processed:
                                self.logger.info(f"🔄 Job {job_id} exists and allow_processed=True - using it")
                                with open(job_file, 'r', encoding='utf-8') as f:
                                    existing_job = json.load(f)
                                    enhanced_jobs.append(existing_job)
                                    current_job_count += 1
                                continue
                            else:
                                should_skip = self._should_skip_existing_job(job_file, job_id, allow_processed)
                                if should_skip:
                                    continue
                                
                        # Get job description
                        descriptor = job.get("MatchedObjectDescriptor", {})
                        api_description = descriptor.get("PositionFormattedDescription", {}).get("Content", "")
                        
                        if not api_description:
                            position_uri = descriptor.get("PositionURI", "")
                            if position_uri:
                                api_description = self.fetch_job_description(job_id, position_uri)
                        
                        # Create and save job
                        beautiful_job = self.create_beautiful_job_structure(
                            job_api_data=job,
                            job_description=api_description
                        )
                        
                        with open(job_file, 'w', encoding='utf-8') as f:
                            json.dump(beautiful_job, f, indent=2, ensure_ascii=False)
                        
                        enhanced_jobs.append(beautiful_job)
                        current_job_count += 1
                        
                        self.logger.info(f"💾 Saved beautiful job {job_id}: {beautiful_job['job_content']['title']}")
                        
                        # Be nice to the servers
                        if not quick_mode:
                            time.sleep(self.config.job_search.search_delay_seconds)
                            
                    except Exception as e:
                        self.logger.error(f"❌ Error processing job {job_id}: {e}")
                        continue
                
                # If no new jobs were found in this batch, move to next page
                if current_job_count == 0:
                    page += 1
                    continue
                    
                # If we found some jobs but need more, move to next page
                if current_job_count < max_jobs:
                    page += 1
                    continue
                    
                break  # We have enough jobs
                
            except Exception as e:
                self.logger.error(f"❌ Job fetching failed: {e}")
                break
        
        self.logger.info(f"✅ Successfully processed {len(enhanced_jobs)} jobs with beautiful structure!")
        return enhanced_jobs
# Convenience function for backward compatibility
def fetch_jobs_beautiful(max_jobs: int = 10, quick_mode: bool = False) -> List[Dict[str, Any]]:
    """Convenience function to fetch jobs with beautiful structure"""
    fetcher = EnhancedJobFetcher()
    return fetcher.fetch_jobs(max_jobs=max_jobs, quick_mode=quick_mode)

if __name__ == "__main__":
    # Test the enhanced fetcher
    from core.rich_cli import print_sunset_banner, print_success
    
    print_sunset_banner()
    
    fetcher = EnhancedJobFetcher()
    jobs = fetcher.fetch_jobs(max_jobs=2, quick_mode=True)
    
    if jobs:
        print_success(f"Successfully fetched {len(jobs)} jobs with beautiful structure!")
        for job in jobs:
            title = job['job_content']['title']
            desc_length = len(job['job_content']['description'])
            print(f"  📋 {title} (description: {desc_length} chars)")
    else:
        print("❌ No jobs fetched")
