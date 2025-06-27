# Job Profile Acquisition Process

## Overview

This document outlines the exact process for acquiring job profiles from Deutsche Bank careers website, which is a core functionality of Project Sunset. This process forms the foundation for all subsequent operations in the application pipeline.

## Process Flow

The job profile acquisition follows these specific steps:

1. **API Access**
   - Connect to the Deutsche Bank careers website API
   - Submit a request for available job listings
   - Retrieve job metadata in JSON format

2. **Job Filtering**
   - Filter received jobs for locations containing "Frankfurt"
   - Process only jobs matching the location filter
   - Preserve all original metadata from the API

3. **Detail Page Scraping**
   - For each filtered job, access its detail URL
   - Use Firefox browser automation to load the page
   - Wait for dynamic content to fully render
   - Extract the complete HTML content
   - Handle any anti-scraping mechanisms

4. **TLM-based Content Extraction**
   - Submit the scraped HTML to the TLM framework
   - Task the TLM to extract a clean, structured job description
   - Extract key components: title, responsibilities, requirements
   - Validate the structured output against schema

5. **Data Storage**
   - Create a consolidated job record with:
     - Original API metadata
     - Scraped HTML content
     - TLM-extracted structured description
   - Save to the postings folder as `job_XXXXX.json` (where XXXXX is the job ID)

## Success Criteria

A successful job profile acquisition must deliver:

1. Complete original job metadata from the API
2. Full HTML content from the detail page
3. Structured job details extracted via TLM, including:
   - Job title
   - Responsibilities (as a list)
   - Requirements (as a list)
4. Properly saved JSON file in the designated location

## Testing Focus

Testing should verify:

1. **API Connection**: Can successfully retrieve job listings
2. **Frankfurt Filtering**: Correctly identifies Frankfurt jobs
3. **Browser Scraping**: Successfully retrieves HTML from detail pages
4. **TLM Extraction**: Properly extracts structured content from HTML
5. **Storage**: Correctly saves complete job information to filesystem

## Existing Implementation

The current implementation involves:
- `scripts/career_pipeline/job_fetcher.py` - Fetches job listings
- `scripts/career_pipeline/job_detail_extractor.py` - Legacy detail extractor
- `scripts/career_pipeline/tlm_job_extractor.py` - TLM-based detail extractor
- `scripts/career_pipeline/orchestrator.py` - Coordinates the process

## Future Improvements

1. All job extraction should use only TLM-powered extraction
2. Browser automation should be refined to better handle website changes
3. Error handling and recovery should be strengthened
4. Rate limiting and session management should be improved

## Sample Job Object Structure

```json
{
  "id": "63141",
  "job_id": "63141",
  "title": "Senior Software Engineer",
  "location": "Frankfurt, Germany",
  "url": "https://careers.db.com/job/63141",
  "posted_date": "2025-05-01",
  "business_division": "Technology",
  "html_content": "...[full HTML content from the detail page]...",
  "tlm_extracted": {
    "job_title": "Senior Software Engineer",
    "responsibilities": [
      "Design and implement scalable software solutions",
      "Collaborate with cross-functional teams",
      "Lead code reviews and mentor junior developers"
    ],
    "requirements": [
      "5+ years of experience in software development",
      "Proficiency in Python and JavaScript",
      "Experience with cloud platforms (AWS, Azure)"
    ],
    "location": "Frankfurt, Germany",
    "department": "Technology",
    "company_description": "Deutsche Bank is a leading global investment bank..."
  },
  "processing_metadata": {
    "extraction_timestamp": "2025-05-12T14:30:00",
    "tlm_success": true,
    "tlm_model": "llama3.1",
    "extraction_time_ms": 1240
  }
}
```
