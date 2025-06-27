# Enhanced Deutsche Bank Job Search

## Overview

This document describes the enhanced job search implementation for retrieving Deutsche Bank job listings. The original implementation was only retrieving around 40-45 job listings while the Deutsche Bank careers website shows over 70 jobs in Frankfurt.

## Problem Analysis

After analyzing the job listings comparison between manually collected job titles and API results, we identified several issues:

1. The API search was too restrictive using only the "Frankfurt*" location filter
2. Many DWS jobs were missing from search results
3. Some jobs might have different location categorization than expected

## Solution

The enhanced job search implementation (`fix_api_job_search.py`) uses four different search strategies to ensure we find all relevant jobs:

1. Standard Frankfurt wildcard search (original approach)
2. Search for all Deutschland jobs and filter client-side
3. Use keyword search for "Frankfurt"
4. Specific search for "DWS" jobs (many missing jobs are DWS-related)

The script also includes logic to deduplicate jobs and filter appropriately:

- Jobs are included if they meet any of these criteria:
  1. Job is located in Frankfurt, Deutschland
  2. Job is a DWS job located in Deutschland 
  3. Job matches the DWS keyword search

## Usage

Run the script with the following command:

```bash
python fix_api_job_search.py [options]
```

Options:
- `--max-jobs`: Maximum number of jobs to fetch (default: 500)
- `--force`: Force reprocessing of existing jobs
- `--output-dir`: Output directory for job files (default: data/postings)

## Integration with Existing Pipeline

The enhanced search logic has now been directly integrated into the `fetch_module.py` file, specifically in the `fetch_frankfurt_jobs()` function. This ensures that all pipeline runs will automatically benefit from the improved job search capabilities.

The implementation:
1. Uses all four search strategies in sequence
2. Tracks and deduplicates jobs by ID
3. Applies appropriate filtering for each strategy
4. Continues until either the maximum job count is reached or all strategies are exhausted

## Results

After implementing the enhanced job search:

1. We've increased job coverage from approximately 45 to over 70 jobs
2. Specifically found DWS jobs that were previously missing
3. Improved the pipeline's ability to capture all relevant job listings without manual intervention
4. Fixed a syntax error in the original implementation that was causing issues

## Verification

To verify that the enhanced search is working correctly, run:

```bash
python check_job_locations.py
```

This will compare the jobs found via API with the manually collected list and show any remaining gaps.

Testing shows this approach finds 70+ jobs matching the Deutsche Bank careers website listing, compared to the 45 jobs found by the original approach.

## Future Improvements

1. Monitor for additional sources of jobs that might be missed
2. Consider adding more search strategies if needed
3. Optimize API request parameters to reduce the number of requests needed
