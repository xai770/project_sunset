# Job Directory Issue: Resolution Guide

## Problem Overview

Job files were being saved to `/home/xai/Documents/sunset/profile/data/postings/` instead of the expected directory `/home/xai/Documents/sunset/data/postings/`. This caused confusion and functionality issues because some components expected files in one location while they were actually being saved to another.

## Root Cause Analysis

1. The issue was in the configuration file `run_pipeline/config/paths.py` where the `JOB_DATA_DIR` was set to `PROJECT_ROOT / "profile" / "data" / "postings"`.
2. Debug scripts were using `PROJECT_ROOT / "data" / "postings"` which is a different location.
3. No error was appearing because both directories were being properly created, but files were only being written to the location in the config file.

## Implemented Solution

We've implemented a robust solution that addresses this issue in multiple ways:

1. **Improved Configuration in `paths.py`**:
   - Added support for both directory locations
   - Added an environment variable option for flexibility
   - Updated the ensure_directories() function to create a symbolic link

2. **Enhanced Error Logging**:
   - Added more detailed logging in the job processing module
   - Added directory existence verification
   - Improved path normalization

3. **New Utility Script**:
   - Created `scripts/job_directory_manager.py` to help manage job directories
   - Features include checking directory status, creating symbolic links, and syncing files

## How to Use the Solution

### Option 1: Use the Symbolic Link (Recommended)

The updated `ensure_directories()` function will automatically create a symbolic link from the expected directory to the actual directory. This means that regardless of which path is used, the files will be found in the correct location.

### Option 2: Set Environment Variable

You can set the `SUNSET_JOB_DIR` environment variable to specify which directory should be used:

```bash
export SUNSET_JOB_DIR="/home/xai/Documents/sunset/data/postings"
```

Add this to your `.bashrc` or `.zshrc` file to make it permanent.

### Option 3: Use the Utility Script

The new utility script provides several options for managing job directories:

```bash
# Check job directory status
python /home/xai/Documents/sunset/scripts/job_directory_manager.py --check

# Create a symbolic link
python /home/xai/Documents/sunset/scripts/job_directory_manager.py --symlink

# Sync files between directories
python /home/xai/Documents/sunset/scripts/job_directory_manager.py --sync

# Set environment variable
python /home/xai/Documents/sunset/scripts/job_directory_manager.py --env
```

## Verification Steps

To verify that the solution is working:

1. Run the pipeline to process jobs
2. Check both directory locations to ensure files are accessible
3. Use the utility script with the `--check` option to verify directory status

## Long-term Considerations

For future development:

1. Standardize on a single convention for file paths
2. Consider adding configuration options to explicitly set the job directory
3. Add validation checks to ensure directory permissions are correct
4. Consider using a database for job storage instead of the filesystem for better reliability
