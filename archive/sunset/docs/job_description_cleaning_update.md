# Job Description Cleaning System - May 2025 Update

## Overview

The job description cleaning system has been upgraded to improve consistency and efficiency. This document outlines the changes made and provides guidance for using the new system.

## Key Updates

### 1. Default Model Changed

- The default model has been changed from **phi3** to **llama3.2:latest**
- Benchmarking showed llama3.2:latest delivers more consistent extraction quality

### 2. Simplified Prompt

The prompt used for extraction has been simplified to ensure consistency:

```
Extract ONLY the English version of this job description from Deutsche Bank. 

Please:
1. Remove all German text completely
2. Remove all website navigation elements and menus
3. Remove company marketing content and benefits sections
4. Remove all HTML formatting and unnecessary whitespace
5. Preserve the exact original wording of the job title, location, responsibilities, and requirements
6. Maintain the contact information
7. Keep the original structure (headings, bullet points) of the core job description
8. Double check that you remove all sections and wordings discussing the company culture, benefits, values, and mission statement

The result should be a clean, professional job description in English only, with all the essential information about the position preserved exactly as written.
```

### 3. New Job Description Update Utility

A new utility `update_job_descriptions.py` has been created in the `run_pipeline/utils/` directory to simplify the maintenance of job descriptions.

#### Features

- **Smart Detection**: Automatically finds jobs missing concise descriptions or containing placeholders
- **Targeted Processing**: Can process specific job IDs or all jobs needing updates
- **Batch Processing**: Allows limiting the number of jobs processed in one run
- **Size Reduction**: Removes HTML content after extraction to reduce file size
- **Metrics**: Reports compression ratios, characters saved, and completion status
- **Dry Run**: Preview which jobs would be processed without making changes
- **Test Mode**: Run with mock responses for testing

#### Usage

```bash
# Basic usage (process all jobs needing updates)
./update_job_descriptions.sh

# Limit processing to specific jobs
./update_job_descriptions.sh --job-ids 55288,55289

# Process only a set number of jobs
./update_job_descriptions.sh --max-jobs 5

# Check which jobs need processing without changing them
./update_job_descriptions.sh --dry-run

# Use test mode with mock responses
./update_job_descriptions.sh --test-mode
```

### 4. HTML Content Removal

The system now removes the full HTML content from job JSON files after extraction to significantly reduce file size:

- Original HTML content is stored in `web_details.full_description`
- After extraction, this field is removed to save space
- Concise descriptions are stored in `web_details.concise_description`
- Average file size reduction: 60-80% compared to original files

### 5. Improved Logging

Enhanced logging now provides metrics on:

- Compression ratios (comparing original HTML, cleaned text, and concise descriptions)
- Characters saved by removing HTML content
- Number of jobs missing descriptions
- Success/failure statistics for each processing run

## Results

- All job descriptions have been processed with llama3.2:latest model
- Average file size reduction: ~75%
- Total job files: 42
- Current average file size: ~4.7 KB per job 
- Total size of job descriptions directory: ~0.19 MB
- Consistent format across all job descriptions

## Future Work

- Consider automated scheduling of the update utility to keep job descriptions current
- Further optimize prompt for better extraction of specific job details
- Explore fine-tuning options for even better extraction quality
