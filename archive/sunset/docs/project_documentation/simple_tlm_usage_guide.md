# Guide to Using the Simplified TLM Job Extraction

This document explains how to use the newly implemented simplified TLM pipeline for extracting job details from the Deutsche Bank careers website.

## Quick Start

To extract a job posting from the Deutsche Bank careers website:

```bash
# Navigate to the project root
cd /home/xai/Documents/sunset

# Run the simplified TLM pipeline with a job ID
python scripts/career_pipeline/tlm_integrated_pipeline.py 63141
```

This will:
1. Extract the HTML content using Firefox
2. Process the content with TLM to extract job details
3. Run skill decomposition on the extracted requirements
4. Save both the job details and skill decomposition results

## Required Dependencies

- Firefox browser installed (for HTML extraction)
- Python 3.9+
- All Python packages in requirements.txt
- Network access to Deutsche Bank careers website

## Output Files

The pipeline creates the following output files:

- `/home/xai/Documents/sunset/data/extracted_jobs/job_{job_id}.json` - Contains basic job details
- `/home/xai/Documents/sunset/data/extracted_jobs/skills_{job_id}.json` - Contains decomposed skills

## Handling Common Issues

### 403 Forbidden Errors

If you encounter 403 Forbidden errors, try:

1. **Clear Firefox Data**: Remove all Firefox sessions and cached data
   ```bash
   scripts/career_pipeline/utils/cleanup_firefox.sh
   ```

2. **Wait and Retry**: Anti-scraping measures may block repeated requests
   ```bash
   # Wait for a while and try again
   sleep 300
   python scripts/career_pipeline/tlm_integrated_pipeline.py 63141
   ```

3. **Use a Different Network**: Try connecting from a different network or VPN

### Cookie Consent Problems

Cookie consent issues are handled automatically by our Firefox extraction, but if you encounter problems:

1. **Manual Acceptance**: Run Firefox manually once and accept all cookies
2. **Cookie Cache**: Use the provided cookie cache by setting `USE_COOKIE_CACHE=1`

## Key Components

### 1. simple_tlm_extractor.py

```python
# Example usage
from scripts.career_pipeline.utils.simple_tlm_extractor import extract_and_process_job

# Extract a job posting
result = extract_and_process_job("https://careers.db.com/professionals/search-roles/#/professional/job/63141")
```

### 2. TLM Task Definitions

The simplified extraction uses:

- `job_detail_extraction` task - Processes HTML content to extract job details
- `skill_decomposition` task - Processes job requirements to identify skills

## Monitoring Execution

Logs are saved to `/home/xai/Documents/sunset/logs/tlm_pipeline.log` for troubleshooting.

## Next Steps

We plan to further improve the pipeline with:

1. Better error handling
2. Performance optimization
3. More sophisticated field extraction
4. Integration with downstream applications

## Contact

For questions or feedback, contact the TLM implementation team.
