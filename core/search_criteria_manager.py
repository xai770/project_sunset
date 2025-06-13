#!/usr/bin/env python3
"""
Multi-User Search Criteria Manager

Manages search profiles for different users and websites, supporting
the multi-user, multi-website vision of Project Sunset.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LocationCriteria:
    cities: List[str]
    countries: List[str]
    country_codes: List[int]
    city_codes: List[int]
    remote_allowed: bool

@dataclass
class JobTypeCriteria:
    employment_types: List[str]
    career_levels: List[str]
    exclude_keywords: List[str]

@dataclass
class DomainCriteria:
    preferred: List[str]
    excluded: List[str]

@dataclass
class SearchProfile:
    name: str
    description: str
    active: bool
    criteria: Dict[str, Any]
    fetching: Dict[str, Any]
    processing: Dict[str, Any]

class SearchCriteriaManager:
    """Manages search criteria for multi-user, multi-website job fetching"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "/home/xai/Documents/sunset/config/search_criteria.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load search criteria configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data: Dict[str, Any] = json.load(f)
                return config_data
        except FileNotFoundError:
            raise FileNotFoundError(f"Search criteria config not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in search criteria config: {e}")
    
    def get_active_profile(self) -> SearchProfile:
        """Get the currently active search profile"""
        default_profile_name = self.config["global_settings"]["default_profile"]
        
        for profile_name, profile_data in self.config["search_profiles"].items():
            if profile_data.get("active", False):
                return SearchProfile(
                    name=profile_name,
                    description=profile_data["description"],
                    active=profile_data["active"],
                    criteria=profile_data["criteria"],
                    fetching=profile_data.get("fetching", {}),
                    processing=profile_data.get("processing", {})
                )
        
        # Fallback to default profile
        if default_profile_name in self.config["search_profiles"]:
            profile_data = self.config["search_profiles"][default_profile_name]
            return SearchProfile(
                name=default_profile_name,
                description=profile_data["description"],
                active=True,
                criteria=profile_data["criteria"],
                fetching=profile_data.get("fetching", {}),
                processing=profile_data.get("processing", {})
            )
        
        raise ValueError("No active search profile found")
    
    def matches_criteria(self, job_data: Dict[str, Any], profile: Optional[SearchProfile] = None) -> bool:
        """Check if a job matches the search criteria"""
        if profile is None:
            profile = self.get_active_profile()
        
        # Extract job information
        job_content = job_data.get("job_content", {})
        location = job_content.get("location", {})
        
        # Check location criteria
        if not self._matches_location(location, profile.criteria.get("locations", {})):
            return False
        
        # Check job type criteria
        if not self._matches_job_type(job_content, profile.criteria.get("job_types", {})):
            return False
        
        # Check domain criteria
        if not self._matches_domain(job_content, profile.criteria.get("domains", {})):
            return False
        
        return True
    
    def _matches_location(self, location: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if job location matches criteria"""
        if not criteria:
            return True
        
        city = location.get("city", "").strip()
        country = location.get("country", "").strip()
        
        # Check cities
        if criteria.get("cities") and city:
            if not any(c.lower() in city.lower() for c in criteria["cities"]):
                return False
        
        # Check countries
        if criteria.get("countries") and country:
            if not any(c.lower() in country.lower() for c in criteria["countries"]):
                return False
        
        return True
    
    def _matches_job_type(self, job_content: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if job type matches criteria"""
        if not criteria:
            return True
        
        title = job_content.get("title", "").lower()
        description = job_content.get("description", "").lower()
        
        # Check exclude keywords
        exclude_keywords = criteria.get("exclude_keywords", [])
        for keyword in exclude_keywords:
            if keyword.lower() in title or keyword.lower() in description:
                return False
        
        return True
    
    def _matches_domain(self, job_content: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if job domain matches criteria"""
        if not criteria:
            return True
        
        title = job_content.get("title", "").lower()
        description = job_content.get("description", "").lower()
        organization = job_content.get("organization", {})
        division = organization.get("division", "").lower()
        
        # Check excluded domains
        excluded = criteria.get("excluded", [])
        for domain in excluded:
            if (domain.lower() in title or 
                domain.lower() in description or 
                domain.lower() in division):
                return False
        
        return True
    
    def cleanup_non_matching_jobs(self, job_directory: Optional[str] = None) -> List[str]:
        """Remove jobs that don't match current search criteria"""
        if job_directory is None:
            job_directory = "/home/xai/Documents/sunset/data/postings"
        
        cleanup_policy = self.config["global_settings"]["cleanup_policy"]
        active_profile = self.get_active_profile()
        
        removed_jobs = []
        job_files = list(Path(job_directory).glob("job*.json"))
        
        for job_file in job_files:
            try:
                with open(job_file, 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                
                # Skip backup files
                if "backup" in job_file.name.lower():
                    continue
                
                if not self.matches_criteria(job_data, active_profile):
                    job_id = job_data.get("job_metadata", {}).get("job_id", job_file.stem)
                    
                    # Archive before removal if configured
                    if cleanup_policy.get("archive_before_removal", False):
                        self._archive_job(job_file, cleanup_policy.get("archive_directory"))
                    
                    # Remove the job file
                    if cleanup_policy.get("remove_non_matching_jobs", False):
                        job_file.unlink()
                        removed_jobs.append(job_id)
                        print(f"🗑️  Removed non-matching job: {job_id}")
                
            except Exception as e:
                print(f"⚠️  Error processing {job_file}: {e}")
                continue
        
        return removed_jobs
    
    def _archive_job(self, job_file: Path, archive_dir: Optional[str]):
        """Archive a job file before removal"""
        if not archive_dir:
            return
        
        archive_path = Path(archive_dir)
        archive_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archived_name = f"{job_file.stem}_archived_{timestamp}.json"
        archive_file = archive_path / archived_name
        
        job_file.rename(archive_file)
        print(f"📦 Archived {job_file.name} to {archive_file}")
    
    def get_profile_summary(self, profile_name: Optional[str] = None) -> str:
        """Get a human-readable summary of search criteria"""
        if profile_name is None:
            profile = self.get_active_profile()
            profile_name = profile.name
        else:
            profile_data = self.config["search_profiles"].get(profile_name)
            if not profile_data:
                return f"Profile '{profile_name}' not found"
            
            profile = SearchProfile(
                name=profile_name,
                description=profile_data["description"],
                active=profile_data.get("active", False),
                criteria=profile_data["criteria"],
                fetching=profile_data.get("fetching", {}),
                processing=profile_data.get("processing", {})
            )
        
        summary = []
        summary.append(f"🎯 Search Profile: {profile.name}")
        summary.append(f"📝 Description: {profile.description}")
        summary.append(f"✅ Active: {profile.active}")
        summary.append("")
        
        # Location criteria
        locations = profile.criteria.get("locations", {})
        if locations:
            summary.append("📍 Location Criteria:")
            if locations.get("cities"):
                summary.append(f"   Cities: {', '.join(locations['cities'])}")
            if locations.get("countries"):
                summary.append(f"   Countries: {', '.join(locations['countries'])}")
            summary.append(f"   Remote allowed: {locations.get('remote_allowed', False)}")
            summary.append("")
        
        # Domain criteria
        domains = profile.criteria.get("domains", {})
        if domains:
            summary.append("🏢 Domain Criteria:")
            if domains.get("preferred"):
                summary.append(f"   Preferred: {', '.join(domains['preferred'])}")
            if domains.get("excluded"):
                summary.append(f"   Excluded: {', '.join(domains['excluded'])}")
            summary.append("")
        
        return "\n".join(summary)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage search criteria for multi-user job fetching")
    parser.add_argument("--profile", help="Show profile summary")
    parser.add_argument("--cleanup", action="store_true", help="Remove non-matching jobs")
    parser.add_argument("--list-profiles", action="store_true", help="List all profiles")
    
    args = parser.parse_args()
    
    manager = SearchCriteriaManager()
    
    if args.list_profiles:
        for name, data in manager.config["search_profiles"].items():
            status = "✅ ACTIVE" if data.get("active", False) else "💤 inactive"
            print(f"{name}: {data['description']} [{status}]")
    
    elif args.profile:
        print(manager.get_profile_summary(args.profile))
    
    elif args.cleanup:
        removed = manager.cleanup_non_matching_jobs()
        print(f"\n🧹 Cleanup complete! Removed {len(removed)} non-matching jobs.")
    
    else:
        # Show active profile by default
        print(manager.get_profile_summary())
