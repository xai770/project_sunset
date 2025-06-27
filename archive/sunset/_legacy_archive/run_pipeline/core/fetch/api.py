#!/usr/bin/env python3
"""
API-related functions for the fetch module.
Contains functions for interacting with the Deutsche Bank career API.
"""

import json
import logging
import random
import time
import requests
import urllib.parse

logger = logging.getLogger('fetch_module.api')

# Constants for API access
SEARCH_API_URL = "https://api-deutschebank.beesite.de/search/"
JOB_HTML_API_URL = "https://api-deutschebank.beesite.de/jobhtml/{job_id}.json"

# API headers
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Default search parameters
DEFAULT_RESULTS_PER_PAGE = 100  # Fetch more results per request

def create_search_payload(page=1, count_per_page=DEFAULT_RESULTS_PER_PAGE, country_code=None, city_code=None):
    """
    Create the search payload for the API request.
    
    Args:
        page (int): Page number (1-based)
        count_per_page (int): Number of results per page
        country_code (int): Country code filter (optional)
        city_code (int): City code filter (optional)
        
    Returns:
        dict: Search payload ready to be JSON-encoded
    """
    # Calculate first item based on page number
    first_item = ((page - 1) * count_per_page) + 1
    
    # Build search criteria
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
    
    # Construct the full payload
    payload = {
        "LanguageCode": "en",
        "SearchParameters": {
            "FirstItem": first_item,
            "CountItem": count_per_page,
            "MatchedObjectDescriptor": [
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
                "Facet:PositionFormattedDescription.Content",
                "PositionID",
                "PositionTitle",
                "PositionURI",
                "ScoreThreshold",
                "OrganizationName",
                "PositionFormattedDescription.Content",
                "PositionLocation.CountryName",
                "PositionLocation.CountrySubDivisionName",
                "PositionLocation.CityName",
                "PositionLocation.Longitude",
                "PositionLocation.Latitude",
                "PositionIndustry.Name",
                "JobCategory.Name",
                "CareerLevel.Name",
                "PositionSchedule.Name",
                "PositionOfferingType.Name",
                "PublicationStartDate",
                "UserArea.GradEduInstCountry",
                "PositionImport",
                "PositionHiringYear",
                "PositionID"
            ],
            "Sort": [
                {
                    "Criterion": "PublicationStartDate",
                    "Direction": "DESC"
                }
            ]
        },
        "SearchCriteria": search_criteria
    }
    
    return payload


def fetch_job_batch(page=1, count_per_page=DEFAULT_RESULTS_PER_PAGE, country_code=None, city_code=None):
    """
    Fetch a batch of jobs from the search API.
    
    Args:
        page (int): Page number (1-based)
        count_per_page (int): Number of results per page
        country_code (int): Country code filter (optional)
        city_code (int): City code filter (optional)
        
    Returns:
        tuple: (success, job_list, total_results)
    """
    # Prepare the search payload
    payload = create_search_payload(
        page=page, 
        count_per_page=count_per_page,
        country_code=country_code,
        city_code=city_code
    )
    
    # Convert payload to URL parameter
    data_param = urllib.parse.quote(json.dumps(payload))
    url = f"{SEARCH_API_URL}?data={data_param}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'Accept': 'application/json',
    }
    
    try:
        logger.info(f"Fetching page {page} with {count_per_page} results per page")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            try:
                # Parse JSON response
                data = response.json()
                
                # Extract search results
                search_result = data.get("SearchResult", {})
                total_results = search_result.get("SearchResultCount", 0)
                job_list = search_result.get("SearchResultItems", [])
                
                logger.info(f"Found {len(job_list)} jobs on page {page} (Total results: {total_results})")
                return True, job_list, total_results
                
            except ValueError as e:
                logger.warning(f"Failed to parse API response for page {page}: {e}")
                return False, [], 0
        else:
            logger.warning(f"Failed to fetch page {page}: Status code {response.status_code}")
            return False, [], 0
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error accessing API for page {page}: {e}")
        return False, [], 0


def fetch_job_details(job_id, session=None):
    """
    Fetch detailed job information using the jobhtml API endpoint.
    
    Args:
        job_id (int): Job ID to fetch
        session (requests.Session): Optional session object
        
    Returns:
        tuple: (success, job_data)
    """
    if session is None:
        session = requests.Session()
        
    url = JOB_HTML_API_URL.format(job_id=job_id)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'Accept': 'application/json',
    }
    
    try:
        logger.info(f"Fetching details for job ID {job_id}...")
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            try:
                # Parse JSON response
                job_data = response.json()
                
                # Check if the HTML content is empty
                if not job_data.get('html', '').strip():
                    logger.info(f"Job ID {job_id} returns empty content, no actual job exists")
                    return False, None
                
                logger.info(f"Successfully fetched details for job ID {job_id}")
                return True, job_data
                
            except ValueError as e:
                logger.warning(f"Failed to parse API response for job {job_id}: {e}")
                return False, None
        else:
            logger.warning(f"Failed to fetch details for job ID {job_id}: Status code {response.status_code}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error accessing API for job ID {job_id}: {e}")
        return False, None
