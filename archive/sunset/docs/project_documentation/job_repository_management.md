# Deutsche Bank Job Repository Management

This document explains how to properly use the Deutsche Bank job repository management tools.

## Prerequisites

Before running any job scraping operations, ensure that:

1. **Firefox is running** - This is critical because our scraping technique relies on an active Firefox instance for tab management.
2. The scripts are being run from the project root directory (`/home/xai/Documents/sunset`)
3. You have sufficient permissions to create and modify files in the data directory

## Job Repository Management Commands

### Complete Reset and Rebuild

To completely reset and rebuild the job repository:

```bash
# Make sure Firefox is running first!
firefox &

# Then run the reset and rebuild script
bash scripts/reset_and_rebuild_jobs.sh
```

This script will:
1. Back up existing job files
2. Clear the job repository
3. Fetch job metadata from the Deutsche Bank API
4. Scrape job details using Firefox tab automation
5. Extract clean job descriptions
6. Verify all jobs have clean descriptions
7. Provide a summary of the results

### Job Details Scraping Only

If you want to scrape job details for existing job files:

```bash
# Ensure Firefox is running
firefox &

# Run the scraper with the Firefox helper
bash scripts/ensure_firefox_and_scrape.sh 50  # Scrape up to 50 jobs
```

### Clean Description Extraction

To extract clean descriptions from already scraped jobs:

```bash
python scripts/job_description_cleaner.py --max-jobs 50
```

### Verify and Fix Missing Clean Descriptions

To verify and fix any missing clean descriptions:

```bash
python scripts/verify_and_fix_clean_descriptions.py
```

## Troubleshooting

### Placeholder Descriptions Issue

If you see placeholder descriptions like this in your job files:

```
This is a [Career Level] position at Deutsche Bank. The full job description could not be extracted.
```

This usually means one of these problems occurred:

1. **Firefox was not running** during the job scraping step.
2. The scraping process encountered errors but continued with the workflow.
3. The web content could not be properly extracted from the job posting pages.

**Solution:**
1. Ensure Firefox is running before starting the process.
2. Run the ensure_firefox_and_scrape.sh script directly to only focus on the scraping step.
3. Check the logs for any errors during the scraping process.

### Firefox Not Running Error

If you get an error about Firefox not running:

```
ERROR: Firefox is not running! Please start Firefox before running this script.
```

Simply start Firefox and try again:

```bash
firefox &
bash scripts/ensure_firefox_and_scrape.sh 50
```

## Best Practices

1. Always ensure Firefox is running before starting any scraping operation.
2. Check the logs for any errors after each step of the process.
3. Use the ensure_firefox_and_scrape.sh script for reliable scraping.
4. When running complete_job_workflow.sh or reset_and_rebuild_jobs.sh, make sure Firefox is running first.
