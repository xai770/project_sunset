#!/usr/bin/env python3
"""
Project Sunset - Enhanced Job Fetcher with Wireguard
==================================================

Combines the working job fetching approach from the backup with Wireguard rotation
to successfully get job descriptions that bypass 403 Forbidden errors.

Key features:
• Uses the proven API approach from backup (including jobhtml endpoint)
• Wireguard IP rotation to avoid blocking
• Beautiful JSON structure
• Fallback mechanisms
• Complete error handling

Author: GitHub Copilot 💜
Date: June 11, 2025
Version: 7.0.0 (Wireguard Enhanced)
"""

import json
import logging
import requests
import time
import subprocess
import glob
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import quote
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config_manager import get_config
from core.beautiful_cli import print_info, print_success, print_warning, print_error

class WireguardRotator:
    """Handle Wireguard IP rotation"""
    
    def __init__(self):
        self.config_dir = project_root / "resources" / "network"
        self.current_interface = None
        self.logger = logging.getLogger(f"{__name__}.WireguardRotator")
        
    def get_available_configs(self) -> List[str]:
        """Get list of available Wireguard configs"""
        config_files = glob.glob(str(self.config_dir / "wg-*.conf"))
        return [Path(f).stem for f in config_files]
    
    def check_ip(self) -> Optional[str]:
        """Check current public IP"""
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=10)
            return response.json()['ip']
        except Exception as e:
            self.logger.warning(f"Failed to check IP: {e}")
            return None
    
    def disconnect_wireguard(self) -> bool:
        """Disconnect from Wireguard"""
        if not self.current_interface:
            return True
            
        try:
            subprocess.run(['sudo', 'wg-quick', 'down', self.current_interface], 
                         check=True, capture_output=True, text=True)
            self.logger.info(f"Disconnected from {self.current_interface}")
            self.current_interface = None
            return True
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Failed to disconnect: {e}")
            return False
    
    def connect_wireguard(self, interface: str) -> bool:
        """Connect to Wireguard"""
        config_path = self.config_dir / f"{interface}.conf"
        if not config_path.exists():
            self.logger.error(f"Config not found: {config_path}")
            return False
            
        try:
            subprocess.run(['sudo', 'wg-quick', 'up', str(config_path)], 
                         check=True, capture_output=True, text=True)
            self.current_interface = interface
            self.logger.info(f"Connected to {interface}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Failed to connect to {interface}: {e}")
            return False
    
    def rotate_ip(self, wait_time: int = 5) -> Tuple[bool, Optional[str], Optional[str]]:
        """Rotate IP by switching Wireguard servers"""
        old_ip = self.check_ip()
        
        # Disconnect current connection
        self.disconnect_wireguard()
        time.sleep(wait_time)
        
        # Choose a random config
        configs = self.get_available_configs()
        if not configs:
            self.logger.error("No Wireguard configs available")
            return False, old_ip, None
            
        new_interface = random.choice(configs)
        
        # Connect to new server
        if self.connect_wireguard(new_interface):
            time.sleep(3)  # Wait for connection to establish
            new_ip = self.check_ip()
            self.logger.info(f"IP rotation: {old_ip} → {new_ip}")
            return True, old_ip, new_ip
        
        return False, old_ip, None

class EnhancedJobFetcherWithWireguard:
    """Enhanced job fetcher with working API approach and Wireguard rotation"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = self._setup_logging()
        self.wireguard = WireguardRotator()
        
        # API endpoints from the working backup
        self.search_api_url = "https://api-deutschebank.beesite.de/search/"
        self.job_html_api_url = "https://api-deutschebank.beesite.de/jobhtml/{job_id}.json"
        
        # Headers that worked in the backup
        self.api_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Directory setup
        self.data_dir = self.config.job_data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        print_success("Enhanced Job Fetcher with Wireguard initialized! 🌟")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def create_search_payload(self, page: int = 1, count_per_page: int = 50, country_code: int = 46, city_code: int = 1698) -> Dict[str, Any]:
        """Create the search payload using the working format from backup with Frankfurt filtering"""
        first_item = ((page - 1) * count_per_page) + 1
        
        # Build search criteria for Frankfurt, Germany
        search_criteria = []
        if country_code is not None:
            search_criteria.append({
                "CriterionName": "PositionLocation.Country",
                "CriterionValue": country_code
            })
        
        if city_code is not None:
            search_criteria.append({
                "CriterionName": "PositionLocation.City", 
                "CriterionValue": city_code
            })
        
        # Always add a null element at the end (as seen in the original API call)
        search_criteria.append(None)
        
        return {
            "LanguageCode": "en",
            "SearchParameters": {
                "FirstItem": first_item,
                "CountItem": count_per_page,
                "MatchedObjectDescriptor": [
                    # THIS IS THE KEY! Include the description field!
                    "PositionFormattedDescription.Content",
                    "PositionID",
                    "PositionTitle", 
                    "PositionURI",
                    "OrganizationName",
                    "PositionLocation.CountryName",
                    "PositionLocation.CountrySubDivisionName", 
                    "PositionLocation.CityName",
                    "PositionIndustry.Name",
                    "JobCategory.Name",
                    "CareerLevel.Name",
                    "PositionSchedule.Name",
                    "PositionOfferingType.Name",
                    "PublicationStartDate",
                    "PositionHiringYear"
                ],
                "Sort": [{"Criterion": "PublicationStartDate", "Direction": "DESC"}]
            },
            "SearchCriteria": search_criteria
        }
    
    def fetch_jobs_from_api(self, max_jobs: int = 10, use_wireguard: bool = True) -> List[Dict[str, Any]]:
        """Fetch jobs using the proven API approach from backup"""
        print_info(f"🚀 Fetching up to {max_jobs} jobs from Deutsche Bank API")
        
        if use_wireguard:
            print_info("🔄 Rotating IP with Wireguard...")
            success, old_ip, new_ip = self.wireguard.rotate_ip()
            if success:
                print_success(f"✅ IP rotated: {old_ip} → {new_ip}")
            else:
                print_warning("⚠️ Wireguard rotation failed, continuing with current IP")
        
        all_jobs = []
        page = 1
        
        while len(all_jobs) < max_jobs:
            # Create search payload
            payload = self.create_search_payload(page=page, count_per_page=min(50, max_jobs - len(all_jobs)))
            
            # Convert to URL parameter (as in backup)
            data_param = quote(json.dumps(payload))
            url = f"{self.search_api_url}?data={data_param}"
            
            try:
                print_info(f"📡 Fetching page {page}...")
                response = requests.get(url, headers=self.api_headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    search_result = data.get("SearchResult", {})
                    job_list = search_result.get("SearchResultItems", [])
                    total_results = search_result.get("SearchResultCount", 0)
                    
                    print_success(f"✅ Found {len(job_list)} jobs on page {page} (Total: {total_results})")
                    
                    if not job_list:
                        break
                        
                    all_jobs.extend(job_list)
                    page += 1
                    
                    # Small delay between requests
                    time.sleep(1)
                    
                else:
                    print_error(f"❌ API returned status {response.status_code}")
                    if response.status_code == 403 and use_wireguard:
                        print_info("🔄 Got 403, rotating IP...")
                        self.wireguard.rotate_ip()
                        time.sleep(3)
                        continue
                    break
                    
            except Exception as e:
                print_error(f"❌ Error fetching page {page}: {e}")
                break
        
        return all_jobs[:max_jobs]
    
    def fetch_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed job HTML using the backup's jobhtml endpoint"""
        url = self.job_html_api_url.format(job_id=job_id)
        
        try:
            print_info(f"📄 Fetching details for job {job_id}...")
            response = requests.get(url, headers=self.api_headers, timeout=30)
            
            if response.status_code == 200:
                job_data = response.json()
                
                # Check if we got actual content
                html_content = job_data.get('html', '').strip()
                if html_content:
                    print_success(f"✅ Got {len(html_content)} chars of job details")
                    return job_data
                else:
                    print_warning(f"⚠️ Job {job_id} returned empty content")
                    return None
            else:
                print_warning(f"⚠️ Failed to fetch job {job_id}: Status {response.status_code}")
                return None
                
        except Exception as e:
            print_error(f"❌ Error fetching job {job_id} details: {e}")
            return None
    
    def create_beautiful_job_structure(self, job_api_data: Dict[str, Any], job_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create beautiful JSON structure with actual job descriptions"""
        descriptor = job_api_data.get("MatchedObjectDescriptor", {})
        job_id = job_api_data.get("MatchedObjectId", "unknown")
        
        # Extract location
        location_data = descriptor.get("PositionLocation", [{}])[0] if descriptor.get("PositionLocation") else {}
        
        # Extract employment details
        employment_type = descriptor.get("PositionOfferingType", [{}])[0].get("Name", "") if descriptor.get("PositionOfferingType") else ""
        schedule = descriptor.get("PositionSchedule", [{}])[0].get("Name", "") if descriptor.get("PositionSchedule") else ""
        career_level = descriptor.get("CareerLevel", [{}])[0].get("Name", "") if descriptor.get("CareerLevel") else ""
        
        # Get job description from either API response or separate fetch
        job_description = ""
        if "PositionFormattedDescription" in descriptor:
            job_description = descriptor["PositionFormattedDescription"].get("Content", "")
        elif job_details and job_details.get("html"):
            # Extract description from HTML if we fetched it separately
            html = job_details.get("html", "")
            # Simple text extraction - could be enhanced with proper HTML parsing
            import re
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
            job_description = text[:2000]  # Truncate to reasonable length
        
        # Create processing log
        now = datetime.now().isoformat()
        processing_log = [
            {
                "timestamp": now,
                "action": "job_fetched",
                "processor": "enhanced_job_fetcher_with_wireguard_v7.0",
                "status": "success",
                "details": f"Successfully fetched job {job_id} using backup API approach"
            }
        ]
        
        if job_description:
            processing_log.append({
                "timestamp": now,
                "action": "description_enriched",
                "processor": "api_with_html_fallback",
                "status": "success", 
                "details": f"Successfully got job description ({len(job_description)} characters)"
            })
        else:
            processing_log.append({
                "timestamp": now,
                "action": "description_enriched",
                "processor": "api_with_html_fallback",
                "status": "failed",
                "details": "No job description available from any source"
            })
        
        # Create the beautiful structure with ACTUAL job descriptions!
        return {
            "job_metadata": {
                "job_id": job_id,
                "version": "1.0",
                "created_at": now,
                "last_modified": now,
                "source": "deutsche_bank_api_with_wireguard",
                "processor": "enhanced_job_fetcher_with_wireguard_v7.0",
                "status": "fetched"
            },
            
            "job_content": {
                "title": descriptor.get("PositionTitle", ""),
                "description": job_description,  # 🎉 ACTUAL DESCRIPTIONS!
                "requirements": [],  # Could be extracted from description
                "location": {
                    "city": location_data.get("CityName", ""),
                    "state": location_data.get("CountrySubDivisionName", ""),
                    "country": location_data.get("CountryName", ""),
                    "remote_options": False
                },
                "employment_details": {
                    "type": employment_type,
                    "schedule": schedule,
                    "career_level": career_level,
                    "salary_range": None,
                    "benefits": []
                },
                "organization": {
                    "name": "Deutsche Bank",
                    "division": descriptor.get("OrganizationName", ""),
                    "division_id": None
                },
                "posting_details": {
                    "publication_date": descriptor.get("PublicationStartDate", ""),
                    "position_uri": descriptor.get("PositionURI", ""),
                    "hiring_year": descriptor.get("PositionHiringYear", "")
                }
            },
            
            "evaluation_results": {
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
                "job_details": job_details or {},
                "description_source": "api_direct" if job_description else "unavailable"
            }
        }
    
    def fetch_jobs(self, max_jobs: int = 10, use_wireguard: bool = True, fetch_details: bool = True) -> List[Dict[str, Any]]:
        """Main method to fetch jobs with beautiful structure and descriptions"""
        print_info(f"🌟 Starting enhanced job fetch with Wireguard (max: {max_jobs})")
        
        # Step 1: Fetch jobs from API
        raw_jobs = self.fetch_jobs_from_api(max_jobs, use_wireguard)
        if not raw_jobs:
            print_error("❌ Failed to fetch any jobs from API")
            return []
        
        print_success(f"✅ Fetched {len(raw_jobs)} jobs from API")
        
        # Step 2: Process each job
        beautiful_jobs = []
        for i, job in enumerate(raw_jobs):
            job_id = job.get("MatchedObjectId", f"unknown_{i}")
            print_info(f"🔄 Processing job {i+1}/{len(raw_jobs)}: {job_id}")
            
            # Optionally fetch detailed HTML
            job_details = None
            if fetch_details:
                job_details = self.fetch_job_details(job_id)
            
            # Create beautiful structure
            beautiful_job = self.create_beautiful_job_structure(job, job_details)
            beautiful_jobs.append(beautiful_job)
            
            # Save individual job file
            job_file = self.data_dir / f"job{job_id}.json"
            try:
                with open(job_file, 'w', encoding='utf-8') as f:
                    json.dump(beautiful_job, f, indent=2, ensure_ascii=False)
                print_success(f"💾 Saved job {job_id}")
            except Exception as e:
                print_error(f"❌ Failed to save job {job_id}: {e}")
            
            # Small delay between jobs
            time.sleep(1)
        
        print_success(f"🎉 Successfully processed {len(beautiful_jobs)} jobs!")
        return beautiful_jobs

def main():
    """Test the enhanced job fetcher"""
    print_info("🧪 Testing Enhanced Job Fetcher with Wireguard")
    
    fetcher = EnhancedJobFetcherWithWireguard()
    jobs = fetcher.fetch_jobs(max_jobs=3, use_wireguard=True, fetch_details=True)
    
    print_info(f"📊 Fetched {len(jobs)} jobs")
    for job in jobs:
        job_id = job.get("job_metadata", {}).get("job_id", "unknown")
        title = job.get("job_content", {}).get("title", "Unknown")
        desc_len = len(job.get("job_content", {}).get("description", ""))
        print_info(f"  • Job {job_id}: {title} ({desc_len} chars description)")

if __name__ == "__main__":
    main()
