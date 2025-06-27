# Versioning System Documentation

## Overview

The job processing pipeline now includes a comprehensive versioning system that tracks module versions and processing history. This system ensures efficient processing by avoiding redundant regeneration of job descriptions while maintaining flexibility to update specific components.

## Key Components

### 1. Version Definitions

All component versions are centrally defined in `run_pipeline/utils/staged_processor/versions.py`:

```python
# Module versions using semantic versioning: MAJOR.MINOR.PATCH
HTML_CLEANER_VERSION = "1.0.0"
LANGUAGE_HANDLER_VERSION = "1.0.0"
EXTRACTORS_VERSION = "1.0.0"
FILE_HANDLER_VERSION = "1.0.0"
PROCESSOR_VERSION = "1.0.0"

# Overall staged processor package version
STAGED_PROCESSOR_VERSION = "1.0.0"

# Module dependencies define ripple effects
MODULE_DEPENDENCIES = {
    "html_cleaner": ["language_handler", "extractors", "file_handler"],
    "language_handler": ["extractors", "file_handler"],
    "extractors": ["file_handler"],
    "file_handler": [],
    "processor": ["html_cleaner", "language_handler", "extractors", "file_handler"]
}
```

### 2. Version Checking System

The system verifies if a job needs reprocessing in the `check_version_and_needs_processing` function in `file_handler.py`:

- Checks if version information exists in job logs
- Compares saved versions with current versions
- Checks for downstream dependencies
- Verifies job description quality

### 3. Version Logging

When a job is processed, version information is included in log entries:

```json
{
  "timestamp": "2025-05-19T07:13:58.134996",
  "script": "run_pipeline.utils.staged_job_description_processor",
  "action": "process_job_description",
  "message": "Processed job description for job ID 53554 using staged approach",
  "staged_processor_version": "1.0.0",
  "html_cleaner_version": "1.0.0",
  "language_handler_version": "1.0.0",
  "extractors_version": "1.0.0",
  "file_handler_version": "1.0.0",
  "processor_version": "1.0.0"
}
```

## How It Works

### Processing Flow

1. The `process_job` function first checks if processing is needed:
   ```python
   needs_processing, reason = check_version_and_needs_processing(job_data)
   
   if not needs_processing and not dry_run:
       logger.info(f"Skipping job {job_id} - {reason}")
       return job_data
   else:
       logger.info(f"Processing job {job_id} - {reason}")
   ```

2. When saving processed jobs, version information is included in the log entry:
   ```python
   log_entry = {
       "timestamp": datetime.now().isoformat(),
       "script": "run_pipeline.utils.staged_job_description_processor",
       "action": "process_job_description",
       "message": f"Processed job description for job ID {job_id} using staged approach",
       "staged_processor_version": STAGED_PROCESSOR_VERSION,
       "html_cleaner_version": HTML_CLEANER_VERSION,
       "language_handler_version": LANGUAGE_HANDLER_VERSION,
       "extractors_version": EXTRACTORS_VERSION,
       "file_handler_version": FILE_HANDLER_VERSION,
       "processor_version": PROCESSOR_VERSION
   }
   ```

### Triggering Reprocessing

The system will trigger reprocessing when:

1. **Version changes**: Any module version in the pipeline is updated
2. **Missing versions**: The job lacks version information in its log
3. **Quality issues**: The concise description is missing or malformed
4. **Forced reprocessing**: The `--force-reprocess` flag is used

### Module Dependencies (Ripple Effect)

When a module is updated, all dependent modules are also considered updated:

```
html_cleaner → language_handler → extractors → file_handler
```

For example, if `html_cleaner` is updated, all jobs will be reprocessed through the entire pipeline. If only `extractors` is updated, the HTML cleaning and language handling results can be reused.

## Maintaining the System

### Updating Module Versions

When making changes to a module, update its version in `versions.py`:

1. **Patch version** (1.0.0 → 1.0.1): For bug fixes and minor changes
2. **Minor version** (1.0.0 → 1.1.0): For new features that maintain backward compatibility
3. **Major version** (1.0.0 → 2.0.0): For breaking changes

Also update the overall `STAGED_PROCESSOR_VERSION` to reflect the change.

### Adding New Modules

When adding a new module:

1. Define its version in `versions.py`
2. Add it to the `MODULE_DEPENDENCIES` dictionary
3. Include its version in the log entries

### Utility Scripts

The system includes utility scripts for managing versions:

1. `update_version.py`: Update component versions
2. `test_version_tracking.py`: Test the versioning system
3. `fix_job_titles_v2.py`: Example script for targeted fixes using the versioning system

## Benefits

1. **Efficiency**: Avoids redundant processing of jobs
2. **Traceability**: Tracks which version of each component processed each job
3. **Selective Processing**: Enables targeted fixes without full reprocessing
4. **Quality Control**: Ensures all jobs meet minimum quality standards

## Example Use Cases

### 1. Fixing Specific Issues Without Full Reprocessing

The `fix_job_titles_v2.py` script demonstrates how to fix specific issues (missing job titles) without reprocessing the entire job description:

```python
# Find jobs with title issues
jobs_with_title_issues = find_jobs_with_title_issues()

# Fix only those jobs by directly updating the structured_description
success, failure = fix_job_titles(jobs_with_title_issues)
```

### 2. Forcing Reprocessing After Algorithm Improvements

When making significant improvements to a module:

1. Update the module's version in `versions.py`
2. The pipeline will automatically reprocess affected jobs on the next run

### 3. Quality Verification

The system checks job quality and reprocesses if needed:

```python
# Check for good existing description
if "concise_description" not in job_data["web_details"]:
    return True, "Missing concise_description"
    
concise_desc = job_data["web_details"]["concise_description"]
if not concise_desc or len(concise_desc) < 500:
    return True, "Concise description too short or empty"
```

## Future Enhancements

Potential improvements to consider:

1. **Versioned Prompt Templates**: Track prompt versions separately
2. **Partial Reprocessing**: Ability to reprocess only specific stages
3. **Version Migration**: Tools to batch-update version information without reprocessing
4. **Performance Metrics**: Track quality metrics by version 

## Conclusion

The versioning system significantly improves the pipeline's maintainability and efficiency by:

- Avoiding unnecessary regeneration of job descriptions
- Providing clear tracking of processing history
- Enabling targeted fixes for specific issues
- Supporting the evolution of the pipeline components

This makes the pipeline more robust and adaptable for future development.
