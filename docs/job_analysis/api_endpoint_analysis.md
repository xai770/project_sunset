# Deutsche Bank API Endpoint Analysis

**Date:** May 15, 2025

## Current Situation

We have identified a discrepancy between the job listings displayed on the Deutsche Bank careers website and what we're able to retrieve through our API:

- The documentation lists 72 Frankfurt-based jobs
- Our current API implementation only captures 47 jobs (65%)
- 28 jobs are completely missing from our database

## API Endpoint Analysis

### Current API Configuration

Currently, we're using a single API endpoint with multiple search strategies:

```
API Endpoint: https://api-deutschebank.beesite.de/search/
```

We make POST requests to this endpoint with various search parameters in the payload.

### Current Search Strategies

Our current implementation uses 8 search strategies:

1. **Frankfurt wildcard**: LocationFilter.City = ["Frankfurt*"]
2. **Deutschland filter**: LocationFilter.CountryName = ["Deutschland"] with client-side filtering for Frankfurt
3. **Frankfurt keyword**: Keyword = "Frankfurt"
4. **DWS jobs**: Keyword = "DWS" with filtering for Germany
5. **Security jobs**: Keyword = "Security" with filtering for Germany
6. **Specialist jobs**: Keyword = "Specialist" with filtering for Germany
7. **AVP level jobs**: CareerLevel.Name = ["Assistant Vice President"] with Frankfurt filtering
8. **VP level jobs**: CareerLevel.Name = ["Vice President"] with Frankfurt filtering

### Potential API Limitations

After analyzing the missing jobs, we've identified several potential limitations:

1. **Career Level Coverage**: We only query for "Assistant Vice President" and "Vice President" levels, missing other levels like "Director", "Managing Director", "Associate", etc.

2. **Job Classification**: The API may use specific JobCategory values for certain roles that we're not explicitly searching for.

3. **Alternative API Endpoints**: There could be additional API endpoints beyond the main search endpoint that might contain some of the missing jobs:
   - Specialized endpoint for management/executive positions
   - Internal job listings endpoint
   - DWS-specific job endpoint
   - Specific geographic endpoints

4. **API Versioning**: We might be using an outdated version of the API.

5. **Parameter Restrictions**: The API might have limitations on how many jobs it returns based on certain parameters.

6. **Pagination Issues**: We might be missing jobs due to pagination limits.

7. **Mobile vs. Desktop API**: There might be separate endpoints for mobile and desktop websites.

## Missing Job Pattern Analysis

Looking at the 28 missing jobs, several patterns emerge:

1. **Senior Leadership Roles**: Many missing jobs are senior roles:
   - DWS - Senior Product Development Manager
   - Senior Sales Specialist
   - Senior Consultant
   - Senior SAP ABAP Engineer

2. **Specialized Technical Roles**:
   - Domain Architect DA Network Security
   - Information Security Expert
   - SAP S4HANA Consultant
   - Model Validation Senior Specialist

3. **DWS-Specific Roles**: Despite our DWS search strategy, we're missing several DWS-specific roles:
   - DWS - Cybersecurity Vulnerability Management Lead
   - DWS - Domain Architect
   - DWS - Senior Product Specialist Private Debt (Real Estate)

4. **Specialized Management/Consulting**:
   - Management Consulting Engagement Manager
   - Communications Manager - Public Affairs & Regulatory Strategy
   - Phoenix Initiative – Processes & Products – Project & Change Lead

## Recommended Actions

1. **Expand Career Level Searches**:
   - Add searches for "Director", "Managing Director", "Associate" career levels
   - Add a search for jobs with no specified career level

2. **Add Job Title Pattern Searches**:
   - Add searches for common patterns in missing jobs: "Manager", "Lead", "Senior", "Architect"
   - Add searches for specialized terms: "SAP", "Consultant", "Analyst", "Engineer"

3. **Investigate Alternative Endpoints**:
   - Test if there are dedicated endpoints for DWS positions
   - Check if certain job types might use different API endpoints

4. **Direct Job ID Search**:
   - For high-priority missing jobs, attempt direct job ID searches if possible

5. **Inspect Network Traffic**:
   - Monitor network traffic on the Deutsche Bank careers website to identify if it's using alternative endpoints or parameters 

6. **Update API Parameters**:
   - Review API documentation if available to check for additional filter parameters
   - Test combining multiple parameters (e.g., Career Level + Job Category)

7. **Consider Web Scraping Fallback**:
   - For jobs that consistently fail to appear in API results, implement a targeted web scraping approach as a fallback

## Next Steps

1. Implement the recommended search strategies in `fetch_module.py`
2. Create a script to directly test each of the missing job IDs (if available)
3. Monitor and compare results over time to identify patterns
4. Document any newly discovered API endpoints or parameters for future reference
