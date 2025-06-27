# Job Description Cleaning System - Update Notice

**Date:** May 14, 2025

## Changes Summary

1. **Upgraded Default Model**: Changed from phi3 to llama3.2:latest for better consistency

2. **Simplified Extraction Prompt**: More consistent extraction across all job descriptions

3. **New Utility Script**: Added `update_job_descriptions.py` in `run_pipeline/utils/` for job description maintenance 

4. **Convenience Shell Script**: Added `update_job_descriptions.sh` in project root for easy access

5. **Space Optimization**: Now removing HTML content after extraction, reducing file size by ~75%

6. **Processed All Jobs**: All 42 job descriptions now have concise descriptions

## Using the New System

Run the update utility to maintain job descriptions:

```bash
# Process all jobs needing updates
./update_job_descriptions.sh

# Check which jobs need updates without processing
./update_job_descriptions.sh --dry-run

# Process specific jobs only
./update_job_descriptions.sh --job-ids 55288,55289
```

## Documentation

For more details, see:

- Main Pipeline Documentation: `run_pipeline/README.md`
- Detailed Update Documentation: `docs/job_description_cleaning_update.md`

## Metrics

- **Total job files**: 42
- **Average file size**: 4.7 KB (down from ~20KB)
- **Total size**: 0.19 MB
- **Space saved**: ~75%
