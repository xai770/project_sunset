# Job Directory Fix Documentation

## Issue
The pipeline was looking for job files in `/home/xai/Documents/sunset/data/postings/` but actually saving them to `/home/xai/Documents/sunset/profile/data/postings/`, causing the jobs to appear missing when later steps in the pipeline tried to access them.

## Solution
We've implemented a two-part solution:

1. **Immediate Fix**: A symbolic link from the expected directory to the actual directory.
2. **Ongoing Solution**: A script (`ensure_job_directory.py`) that checks for and recreates this symbolic link whenever needed.

## How to Use

### Running the Fix Script
```bash
python /home/xai/Documents/sunset/ensure_job_directory.py
```

This script will:
- Check if the actual directory exists and create it if needed
- Back up and remove any existing non-symlink directory at the expected path
- Create or update the symbolic link
- Verify the setup is working correctly

### Integration with Pipeline
For a more robust solution, consider:

1. Adding a call to this script at the beginning of your pipeline execution:
```python
import subprocess
subprocess.run(['/home/xai/Documents/sunset/ensure_job_directory.py'], check=True)
```

2. Add this to your pipeline startup script or main entry point.

## Long-term Recommendations

For a more permanent solution, consider one of these approaches:

1. **Update Configuration**:
   - Modify `/home/xai/Documents/sunset/run_pipeline/config/paths.py` to use the correct path directly.
   - Update `JOB_DATA_DIR` to point to `/home/xai/Documents/sunset/profile/data/postings/`.

2. **Centralized Configuration**:
   - Implement a more flexible configuration system using environment variables or a dedicated config file.
   - This would allow changing paths without modifying code.

3. **Standardize Directory Structure**:
   - Reorganize the project to have a more consistent directory structure.
   - Document this structure clearly for all developers.

## Verification
After implementing these changes, verify by:
1. Running the pipeline with `--force-reprocess` flag.
2. Checking that job files are properly created and accessible.
3. Confirming that subsequent pipeline steps can find and use the job files.
