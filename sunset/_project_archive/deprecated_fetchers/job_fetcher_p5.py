#!/usr/bin/env python3
"""
Project Sunset - Phase 5 Job Fetcher
===================================

Phase 5 job fetching module using modern architecture.
Integrates with DirectSpecialistManager for intelligent job processing.

Author: HAL 9000
Date: June 10, 2025
Version: 6.0.0 (Phase 5 Modern Architecture)
"""

import json
import logging
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import DirectSpecialistManager

class JobFetcherP5:
    """
    Modern job fetcher using Phase 5 architecture with specialist integration
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.specialist_manager = DirectSpecialistManager()
        self.data_dir = Path("data")
        self.postings_dir = self.data_dir / "postings"
        self.scan_progress_file = self.data_dir / "job_scans" / "search_api_scan_progress.json"
        
        # Ensure directories exist
        self.postings_dir.mkdir(parents=True, exist_ok=True)
        self.scan_progress_file.parent.mkdir(parents=True, exist_ok=True)
        
        # API Configuration - Enhanced format with full job descriptions
        self.api_base_url = "https://api-deutschebank.beesite.de/search/"
        self.api_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
    def _setup_logging(self):
        """Setup logging for job fetcher"""
        logger = logging.getLogger("modern_job_fetcher")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def load_scan_progress(self) -> Dict[str, Any]:
        """Load scan progress from file"""
        try:
            if self.scan_progress_file.exists():
                with open(self.scan_progress_file, 'r') as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) else {}
            else:
                return {
                    "last_page_fetched": 0,
                    "jobs_processed": [],
                    "timestamp": datetime.now().isoformat(),
                    "stats": {
                        "total_jobs_found": 0,
                        "total_jobs_processed": 0,
                        "total_pages_fetched": 0
                    }
                }
        except Exception as e:
            self.logger.error(f"❌ Failed to load scan progress: {e}")
            return {
                "last_page_fetched": 0,
                "jobs_processed": [],
                "timestamp": datetime.now().isoformat(),
                "stats": {
                    "total_jobs_found": 0,
                    "total_jobs_processed": 0,
                    "total_pages_fetched": 0
                }
            }
    
    def save_scan_progress(self, progress: Dict[str, Any]):
        """Save scan progress to file"""
        try:
            progress["timestamp"] = datetime.now().isoformat()
            with open(self.scan_progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            self.logger.error(f"❌ Failed to save scan progress: {e}")
    
    def fetch_jobs_from_api(self, max_jobs: int = 50, page_size: int = 25) -> List[Dict[str, Any]]:
        """
        Fetch jobs from Deutsche Bank API
        
        Args:
            max_jobs: Maximum number of jobs to fetch
            page_size: Number of jobs per API request
            
        Returns:
            List of job dictionaries
        """
        self.logger.info(f"🚀 Starting job fetch - Target: {max_jobs} jobs")
        
        jobs = []
        first_item = 1
        total_fetched = 0
        
        # Load progress
        progress = self.load_scan_progress()
        processed_jobs = set(progress.get("jobs_processed", []))
        
        # Enhanced API payload with comprehensive data fields - DAVE'S CORRECT FORMAT
        payload = {
            "LanguageCode": "en",
            "SearchParameters": {
                "FirstItem": first_item,
                "CountItem": page_size,
                "Sort": [{"Criterion": "PublicationStartDate", "Direction": "DESC"}],
                "MatchedObjectDescriptor": [
                    # Facets for rich data extraction
                    "Facet:ProfessionCategory",
                    "Facet:UserArea.ProDivision",
                    "Facet:Profession",
                    "Facet:PositionLocation.CountrySubDivision",
                    "Facet:PositionOfferingType.Code",
                    "Facet:PositionSchedule.Code",
                    "Facet:PositionLocation.City",
                    "Facet:PositionLocation.Country",
                    "Facet:JobCategory.Code",
                    "Facet:CareerLevel.Code",
                    "Facet:PositionHiringYear",
                    "Facet:PositionFormattedDescription.Content",  # KEY FOR RICH CONTENT!
                    
                    # Core job information
                    "PositionID",
                    "PositionTitle",
                    "PositionURI",
                    "ScoreThreshold",
                    "OrganizationName",
                    "PositionFormattedDescription.Content",  # THE CRITICAL FIELD FOR DESCRIPTIONS
                    
                    # Location details
                    "PositionLocation.CountryName",
                    "PositionLocation.CountrySubDivisionName",
                    "PositionLocation.CityName",
                    "PositionLocation.Longitude",
                    "PositionLocation.Latitude",
                    
                    # Job classification
                    "PositionIndustry.Name",
                    "JobCategory.Name",
                    "CareerLevel.Name",
                    "PositionSchedule.Name",
                    "PositionOfferingType.Name",
                    
                    # Additional metadata
                    "PublicationStartDate",
                    "UserArea.GradEduInstCountry",
                    "PositionImport",
                    "PositionHiringYear"
                ]
            },
            "SearchCriteria": [
                {
                    "CriterionName": "PositionLocation.Country",
                    "CriterionValue": 46  # Germany
                },
                {
                    "CriterionName": "PositionLocation.City",
                    "CriterionValue": 1698  # Frankfurt
                }
            ]
        }
        
        try:
            while total_fetched < max_jobs:
                # Enhanced API payload with comprehensive data fields
                payload = {
                    "LanguageCode": "en",
                    "SearchParameters": {
                        "FirstItem": first_item,
                        "CountItem": page_size,
                        "Sort": [{"Criterion": "PublicationStartDate", "Direction": "Desc"}],
                        "MatchedObjectDescriptor": [
                            # Core job information
                            "PositionID", "PositionTitle", "PositionURI", "OrganizationName",
                            "PublicationStartDate", "ApplicationDeadline",
                            
                            # Location details
                            "PositionLocation.CountryName", "PositionLocation.CountrySubDivisionName",
                            "PositionLocation.CityName", "PositionLocation.Longitude", "PositionLocation.Latitude",
                            
                            # Job content - THE KEY FIELD FOR RICH DESCRIPTIONS
                            "PositionFormattedDescription.Content",
                            "QualificationsRequired.Text", "PositionSkills",
                            
                            # Job classification
                            "EmploymentType.Name", "PositionSchedule.Name", "PositionOfferingType.Name",
                            "CareerLevel.Name", "JobCategory.Name", "PositionIndustry.Name",
                            "JobClassification.PrimaryCode", "PositionOpenings",
                            
                            # Additional metadata
                            "PositionHiringYear", "UserArea.ProDivision", "PositionImport",
                            
                            # Facets for enhanced filtering
                            "Facet:ProfessionCategory", "Facet:UserArea.ProDivision", "Facet:Profession",
                            "Facet:PositionLocation.CountrySubDivision", "Facet:PositionOfferingType.Code",
                            "Facet:PositionSchedule.Code", "Facet:PositionLocation.City",
                            "Facet:PositionLocation.Country", "Facet:JobCategory.Code",
                            "Facet:CareerLevel.Code", "Facet:PositionHiringYear",
                            "Facet:PositionFormattedDescription.Content"
                        ]
                    },
                    "SearchCriteria": [
                        {
                            "CriterionName": "PositionLocation.Country",
                            "CriterionValue": 46  # Germany
                        },
                        {
                            "CriterionName": "PositionLocation.City", 
                            "CriterionValue": 1698  # Frankfurt
                        }
                    ]
                }
                
                self.logger.info(f"📡 Fetching page {(first_item-1)//page_size + 1} (items {first_item}-{first_item+page_size-1})")
                
                # Send API request
                response = requests.post(self.api_base_url, json=payload, headers=self.api_headers)
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        
                        if "SearchResult" in response_data and "SearchResultItems" in response_data["SearchResult"]:
                            items = response_data["SearchResult"]["SearchResultItems"]
                            
                            if not items:
                                self.logger.info("📄 No more jobs found")
                                break
                            
                            # Process each job
                            for item in items:
                                job_id = item.get("MatchedObjectId")
                                
                                if job_id and job_id not in processed_jobs:
                                    jobs.append(item)
                                    processed_jobs.add(job_id)
                                    total_fetched += 1
                                    
                                    if total_fetched >= max_jobs:
                                        break
                            
                            self.logger.info(f"✅ Fetched {len(items)} jobs from API (Total: {total_fetched})")
                            
                            # Update progress
                            progress["jobs_processed"] = list(processed_jobs)
                            progress["stats"]["total_jobs_found"] = len(items)
                            progress["stats"]["total_jobs_processed"] = total_fetched
                            progress["stats"]["total_pages_fetched"] = (first_item-1)//page_size + 1
                            self.save_scan_progress(progress)
                            
                            # Prepare for next page
                            first_item += page_size
                            
                            # Rate limiting
                            time.sleep(0.5)
                        
                        else:
                            self.logger.warning("⚠️ No SearchResult in API response")
                            break
                            
                    except json.JSONDecodeError as e:
                        self.logger.error(f"❌ JSON decode error: {e}")
                        break
                        
                else:
                    self.logger.error(f"❌ API request failed: {response.status_code}")
                    self.logger.error(f"Response: {response.text[:500]}")
                    break
                    
        except Exception as e:
            self.logger.error(f"❌ Error during job fetching: {e}")
        
        self.logger.info(f"🎯 Job fetch complete: {len(jobs)} new jobs retrieved")
        return jobs
    
    def save_job_posting(self, job: Dict[str, Any]) -> bool:
        """
        Save individual job posting to file
        
        Args:
            job: Job dictionary
            
        Returns:
            Success status
        """
        try:
            job_id = job.get("MatchedObjectId")
            if not job_id:
                self.logger.warning("⚠️ Job missing ID, skipping save")
                return False
            
            # Extract job descriptor data (API has nested structure)
            job_descriptor = job.get("MatchedObjectDescriptor", {})
            position_location = job_descriptor.get("PositionLocation", [{}])[0] if job_descriptor.get("PositionLocation") else {}
            position_offering = job_descriptor.get("PositionOfferingType", [{}])[0] if job_descriptor.get("PositionOfferingType") else {}
            position_schedule = job_descriptor.get("PositionSchedule", [{}])[0] if job_descriptor.get("PositionSchedule") else {}
            career_level = job_descriptor.get("CareerLevel", [{}])[0] if job_descriptor.get("CareerLevel") else {}
            
            # Create enhanced job data with metadata
            enhanced_job = {
                "job_id": job_id,
                "fetched_timestamp": datetime.now().isoformat(),
                "source": "deutsche_bank_api",
                "processed_by": "modern_job_fetcher_v6",
                "raw_data": job,
                "title": job_descriptor.get("PositionTitle", "Unknown Title"),
                "location": {
                    "city": position_location.get("CityName", ""),
                    "country": position_location.get("CountryName", "")
                },
                "organization": job_descriptor.get("OrganizationName", ""),
                "publication_date": job_descriptor.get("PublicationStartDate", ""),
                "deadline": job_descriptor.get("ApplicationDeadline", ""),
                "description": job_descriptor.get("PositionFormattedDescription", {}).get("Content", ""),
                "requirements": job_descriptor.get("QualificationsRequired", {}).get("Text", ""),
                "skills": job_descriptor.get("PositionSkills", []),
                "employment_type": position_offering.get("Name", ""),
                "career_level": career_level.get("Name", ""),
                "schedule": position_schedule.get("Name", ""),
                "position_uri": job_descriptor.get("PositionURI", "")
            }
            
            # Save to file
            job_file = self.postings_dir / f"job{job_id}.json"
            with open(job_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_job, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Saved job {job_id}: {enhanced_job['title']}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save job {job.get('MatchedObjectId', 'unknown')}: {e}")
            return False
    
    def process_jobs_with_specialists(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process jobs using DirectSpecialistManager for enhanced analysis
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            List of processed jobs with specialist analysis
        """
        self.logger.info(f"🧠 Processing {len(jobs)} jobs with specialist analysis...")
        
        processed_jobs = []
        
        for i, job in enumerate(jobs, 1):
            self.logger.info(f"🔍 Processing job {i}/{len(jobs)}: {job.get('PositionTitle', 'Unknown')}")
            
            try:
                # Extract job descriptor from API response
                job_descriptor = job.get("MatchedObjectDescriptor", {})
                
                # Prepare job data for specialist analysis
                job_data = {
                    "description": job_descriptor.get("PositionFormattedDescription", {}).get("Content", ""),
                    "title": job_descriptor.get("PositionTitle", ""),
                    "requirements": job_descriptor.get("QualificationsRequired", {}).get("Text", ""),
                    "skills": job_descriptor.get("PositionSkills", []),
                    "career_level": job_descriptor.get("CareerLevel", [{}])[0].get("Name", "") if job_descriptor.get("CareerLevel") else "",
                    "organization": job_descriptor.get("OrganizationName", "")
                }
                
                # Use job_fitness_evaluator specialist for basic analysis
                # Note: This would normally require candidate data too, but we'll use it for job analysis
                specialist_input = {
                    "job_requirements": str(job_data),
                    "candidate_profile": "General analysis request"  # Placeholder
                }
                
                # Get specialist analysis using DirectSpecialistManager
                specialist_result = self.specialist_manager.evaluate_with_specialist(
                    "job_fitness_evaluator", 
                    specialist_input
                )
                
                # Add specialist analysis to job
                enhanced_job = job.copy()
                enhanced_job["specialist_analysis"] = {
                    "success": specialist_result.success,
                    "execution_time": specialist_result.execution_time,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "specialist_used": specialist_result.specialist_used
                }
                
                if specialist_result.success:
                    # Convert result to serializable format
                    if hasattr(specialist_result.result, '__dict__'):
                        enhanced_job["specialist_analysis"]["insights"] = specialist_result.result.__dict__
                    else:
                        enhanced_job["specialist_analysis"]["insights"] = str(specialist_result.result)
                else:
                    enhanced_job["specialist_analysis"]["error"] = specialist_result.error
                
                processed_jobs.append(enhanced_job)
                
            except Exception as e:
                self.logger.error(f"❌ Failed to process job with specialists: {e}")
                # Add job without specialist analysis
                processed_jobs.append(job)
        
        self.logger.info(f"✅ Specialist processing complete: {len(processed_jobs)} jobs processed")
        return processed_jobs
    
    def run_full_fetch_and_process(self, max_jobs: int = 20) -> Dict[str, Any]:
        """
        Run complete job fetching and processing pipeline
        
        Args:
            max_jobs: Maximum number of jobs to fetch
            
        Returns:
            Summary of operation
        """
        self.logger.info("🚀 HAL 9000 - Starting Full Job Fetch and Process Operation")
        self.logger.info("=" * 70)
        
        start_time = time.time()
        
        try:
            # 1. Fetch jobs from API
            self.logger.info("1️⃣ Fetching jobs from Deutsche Bank API...")
            jobs = self.fetch_jobs_from_api(max_jobs=max_jobs)
            
            if not jobs:
                self.logger.warning("⚠️ No new jobs fetched")
                return {
                    "success": False,
                    "message": "No new jobs found",
                    "jobs_processed": 0,
                    "execution_time": time.time() - start_time
                }
            
            # 2. Process with specialists
            self.logger.info("2️⃣ Processing jobs with specialist analysis...")
            processed_jobs = self.process_jobs_with_specialists(jobs)
            
            # 3. Save processed jobs
            self.logger.info("3️⃣ Saving processed jobs to disk...")
            saved_count = 0
            for job in processed_jobs:
                if self.save_job_posting(job):
                    saved_count += 1
            
            execution_time = time.time() - start_time
            
            # 4. Generate summary
            summary = {
                "success": True,
                "jobs_fetched": len(jobs),
                "jobs_processed": len(processed_jobs),
                "jobs_saved": saved_count,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "specialist_manager_available": self.specialist_manager.is_available()
            }
            
            self.logger.info("=" * 70)
            self.logger.info("🏆 OPERATION COMPLETE")
            self.logger.info("=" * 70)
            self.logger.info(f"📊 Jobs Fetched: {summary['jobs_fetched']}")
            self.logger.info(f"🧠 Jobs Processed: {summary['jobs_processed']}")
            self.logger.info(f"💾 Jobs Saved: {summary['jobs_saved']}")
            self.logger.info(f"⚡ Execution Time: {summary['execution_time']:.2f}s")
            self.logger.info(f"🤖 Specialist Available: {summary['specialist_manager_available']}")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }

def main():
    """Main entry point for modern job fetcher"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Project Sunset Phase 5 Job Fetcher"
    )
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=20,
        help="Maximum number of jobs to fetch (default: 20)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick fetch (5 jobs only)"
    )
    
    args = parser.parse_args()
    
    # Determine job count
    max_jobs = 5 if args.quick else args.max_jobs
    
    # Create and run fetcher
    fetcher = JobFetcherP5()
    result = fetcher.run_full_fetch_and_process(max_jobs=max_jobs)
    
    # Exit with appropriate code
    if result["success"]:
        print("\n🎉 HAL 9000: Job fetching mission accomplished, Dave!")
        return 0
    else:
        print(f"\n❌ HAL 9000: Mission failed, Dave. Error: {result.get('error', 'Unknown error')}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🤖 HAL 9000: Operation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n🤖 HAL 9000: Critical error detected: {e}")
        sys.exit(1)
