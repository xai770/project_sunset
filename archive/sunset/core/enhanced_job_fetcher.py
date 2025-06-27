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
    
    def _should_skip_existing_job(self, job_file: Path, job_id: str) -> bool:
        """
        Check if an existing job file should be skipped because it contains valuable AI analysis data.
        
        This prevents the pipeline from removing and recreating jobs that have already been processed
        with AI analysis, preserving valuable data.
        
        Args:
            job_file (Path): Path to the existing job file
            job_id (str): Job ID for logging
            
        Returns:
            bool: True if the job should be skipped (has valuable data), False if it should be updated
        """
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
                'bucketed_skills',
                'skills'
            ]
            
            has_valuable_data = any(field in existing_job for field in valuable_ai_fields)
            
            # Also check for non-placeholder job descriptions in web_details
            web_details = existing_job.get('web_details', {})
            concise_desc = web_details.get('concise_description', '')
            has_real_description = (
                concise_desc.strip() and 
                'placeholder for a concise description' not in concise_desc.lower() and
                len(concise_desc) > 50  # Must be substantial content
            )
            
            # Check for processed skills data in new job structure format
            job_content = existing_job.get('job_content', {})
            has_processed_skills = (
                'skills' in job_content and 
                len(job_content.get('skills', [])) > 0
            )
            
            # Also check job_metadata status for processed jobs
            job_metadata = existing_job.get('job_metadata', {})
            is_processed = job_metadata.get('status') in ['processed', 'analyzed', 'matched']
            
            # Skip if any valuable data exists
            should_skip = has_valuable_data or has_real_description or has_processed_skills or is_processed
            
            if should_skip:
                data_types = []
                if has_valuable_data:
                    present_fields = [field for field in valuable_ai_fields if field in existing_job]
                    data_types.append(f"AI analysis ({', '.join(present_fields)})")
                if has_real_description:
                    data_types.append(f"processed description ({len(concise_desc)} chars)")
                if has_processed_skills:
                    skills_count = len(job_content.get('skills', []))
                    data_types.append(f"skills data ({skills_count} skills)")
                if is_processed:
                    data_types.append(f"processed status ({job_metadata.get('status')})")
                
                self.logger.info(f"🔒 Job {job_id} has valuable data: {'; '.join(data_types)}")
            
            return should_skip
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error checking existing job {job_id}: {e}. Will update file.")
            return False  # If we can't read the file, it's safe to update it
    
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
    
    def fetch_jobs(self, max_jobs: int = 60, quick_mode: bool = False, search_criteria: Optional[Dict] = None, force_reprocess: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch jobs with beautiful structure and full descriptions
        Uses search criteria for Frankfurt-focused job retrieval
        """
        if quick_mode:
            max_jobs = min(max_jobs, self.config.job_search.quick_mode_limit)
        
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
        
        self.logger.info(f"🚀 Fetching up to {max_jobs} jobs (quick_mode: {quick_mode})")
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
                "FirstItem": 1,
                "CountItem": max_jobs,
                "MatchedObjectDescriptor": [
                    "PositionID",
                    "PositionTitle",
                    "PositionURI",
                    "PositionFormattedDescription.Content",  # Still try to get it from API
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
                return []
            
            data = response.json()
            
            if "SearchResult" not in data or "SearchResultItems" not in data["SearchResult"]:
                self.logger.error("❌ Invalid API response structure")
                return []
            
            jobs = data["SearchResult"]["SearchResultItems"]
            self.logger.info(f"📥 Received {len(jobs)} jobs from API")
            
            enhanced_jobs = []
            
            for i, job in enumerate(jobs[:max_jobs], 1):
                try:
                    job_id = job.get("MatchedObjectId", f"unknown_{i}")
                    self.logger.info(f"🔄 Processing job {i}/{len(jobs[:max_jobs])}: {job_id}")
                    
                    # Check if job already exists and has valuable data
                    job_file = self.data_dir / f"job{job_id}.json"
                    if job_file.exists() and not force_reprocess:
                        should_skip = self._should_skip_existing_job(job_file, job_id)
                        if should_skip:
                            self.logger.info(f"⏭️ Skipping job {job_id} - already has processed data")
                            # Load existing job for the return list
                            try:
                                with open(job_file, 'r', encoding='utf-8') as f:
                                    existing_job = json.load(f)
                                    enhanced_jobs.append(existing_job)
                            except Exception as e:
                                self.logger.warning(f"⚠️ Could not load existing job {job_id}: {e}")
                            continue
                        else:
                            self.logger.info(f"🔄 Job {job_id} exists but has no AI analysis - updating with fresh data")
                    elif job_file.exists() and force_reprocess:
                        self.logger.info(f"🔄 Force reprocess enabled - will overwrite job {job_id}")
                    else:
                        self.logger.info(f"➕ Creating new job {job_id}")
                    
                    # Try to get description from API first
                    descriptor = job.get("MatchedObjectDescriptor", {})
                    api_description = descriptor.get("PositionFormattedDescription", {}).get("Content", "")
                    
                    # If no description from API, try web scraping
                    if not api_description:
                        position_uri = descriptor.get("PositionURI", "")
                        if position_uri:
                            api_description = self.fetch_job_description(job_id, position_uri)
                    
                    # Create beautiful job structure
                    beautiful_job = self.create_beautiful_job_structure(
                        job_api_data=job,
                        job_description=api_description
                    )
                    
                    # Save to file
                    with open(job_file, 'w', encoding='utf-8') as f:
                        json.dump(beautiful_job, f, indent=2, ensure_ascii=False)
                    
                    enhanced_jobs.append(beautiful_job)
                    self.logger.info(f"💾 Saved beautiful job {job_id}: {beautiful_job['job_content']['title']}")
                    
                    # Be nice to the servers
                    if not quick_mode:
                        time.sleep(self.config.job_search.search_delay_seconds)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error processing job {i}: {e}")
                    continue
            
            self.logger.info(f"✅ Successfully processed {len(enhanced_jobs)} jobs with beautiful structure!")
            return enhanced_jobs
            
        except Exception as e:
            self.logger.error(f"❌ Job fetching failed: {e}")
            return []

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
