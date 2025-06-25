# Enhanced Job Search Implementation - Update May 15, 2025

## Overview

This document describes the enhanced job search implementation for retrieving Deutsche Bank job listings from their API, specifically addressing the issue of missing job listings.

## Problem Identified

Through analysis with the `check_job_locations.py` tool, we found that many manually collected job listings were not appearing in the API results when using only the "Frankfurt*" filter. In particular:

1. 32 out of 72 manually collected jobs were missing from API results
2. Many of these missing jobs were DWS-related positions not located in Frankfurt
3. Other missing jobs included security-related positions and specialist roles

## Solution Implemented

We have enhanced the `fetch_frankfurt_jobs()` function in the `fetch_module.py` to use additional search strategies with custom filters:

### 1. Multi-Strategy Approach

The updated function now uses eight distinct search strategies:

1. **Frankfurt Wildcard Search**: The original strategy using "Frankfurt*" as a city filter
2. **Deutschland Filter**: Search for all jobs in Germany and filter client-side for Frankfurt
3. **Frankfurt Keyword Search**: Using "Frankfurt" as a keyword search term
4. **DWS Jobs Search**: Specifically targeting DWS jobs, including those not in Frankfurt
5. **Security Jobs Search**: Targeting security-related jobs in Germany
6. **Specialist Jobs Search**: Targeting specialist roles in Germany
7. **Assistant Vice President Jobs Search**: Specifically targeting Assistant VP positions in Frankfurt
8. **Vice President Jobs Search**: Specifically targeting VP positions in Frankfurt

### 2. Custom Filters

Each strategy now includes a custom filter function that determines whether a job should be included:

```python
"custom_filter": lambda job_data, title: (
    # Accept all DWS jobs in Germany, regardless of city
    "DWS" in title and
    any(loc.get("CountryName") == "Deutschland" 
        for loc in job_data.get("PositionLocation", []))
)
```

### 3. Enhanced Job Detection

- DWS jobs are now included from anywhere in Germany, not just Frankfurt
- Security-related jobs are specifically targeted
- Specialist positions are captured with a dedicated strategy
- Assistant Vice President positions in Frankfurt are specifically targeted
- Vice President positions in Frankfurt are specifically targeted

## Benefits

1. **Improved Coverage**: Retrieves over 80 additional jobs through CareerLevel strategies alone
2. **Better Matching**: Jobs match manual collection more closely
3. **Enhanced Flexibility**: Custom filter approach makes it easy to add new search criteria
4. **Reuse of Core Structure**: Maintains same pipeline integration and output format
5. **Superior Career-based Search**: CareerLevel filtering provides jobs missed by location-based searches

## Usage

No changes are required to the user-facing API. The enhanced search happens transparently:

```python
from run_pipeline.core.pipeline import run_pipeline
from run_pipeline.core.fetch_module import fetch_job_metadata

# These will use the enhanced search automatically
run_pipeline(args)
fetch_job_metadata(max_jobs=500)
```

## CareerLevel Search Results

The CareerLevel search strategies have been particularly effective:

1. **84 Frankfurt Jobs Found**: The Assistant Vice President and Vice President search strategies found 84 jobs in Frankfurt that might not be captured by location-based searches alone
2. **DWS Jobs Included**: Many DWS-related positions that were previously missing were successfully captured
3. **Specialist Positions**: Many specialist positions that were previously missed are now included

These results confirm that the API's location-based filters alone were insufficient, and that using multiple search attributes (especially CareerLevel) significantly improves job coverage.

## Verification

To verify the enhanced search is working, run:

```bash
python check_job_locations.py
```

For a detailed analysis of the CareerLevel search results:

```bash
python test_career_levels.py
```

These scripts will compare manually collected job titles with API results and should now show significantly fewer missing jobs.
