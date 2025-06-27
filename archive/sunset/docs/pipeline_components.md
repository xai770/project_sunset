# Pipeline Components Overview

This document provides a comprehensive overview of the scripts used in the job expansion pipeline, organized by their role in the workflow.

## Entry Points

1. `/home/xai/Documents/sunset/run_pipeline/run.py` - Main entry point script that runs the pipeline without job limits
2. `/home/xai/Documents/sunset/run_pipeline/core/pipeline_main.py` - Core entry point that handles argument parsing and calls the orchestrator

## Core Orchestration

3. `/home/xai/Documents/sunset/run_pipeline/core/pipeline_orchestrator.py` - Main orchestrator that coordinates all pipeline steps
4. `/home/xai/Documents/sunset/run_pipeline/core/cli_args.py` - Handles command-line argument parsing
5. `/home/xai/Documents/sunset/run_pipeline/core/pipeline_utils.py` - Utility functions for the pipeline orchestrator

## Configuration

6. `/home/xai/Documents/sunset/run_pipeline/config/paths.py` - Contains path definitions and defaults for the pipeline
7. `/home/xai/Documents/sunset/run_pipeline/config/__init__.py` - Package initialization for config

## Core Processing Modules

8. `/home/xai/Documents/sunset/run_pipeline/core/fetch_module.py` - Fetches job metadata from API
   - `/home/xai/Documents/sunset/run_pipeline/core/fetch/api.py` - API interaction functions
   - `/home/xai/Documents/sunset/run_pipeline/core/fetch/job_processing.py` - Job data processing 
   - `/home/xai/Documents/sunset/run_pipeline/core/fetch/progress.py` - Progress tracking

9. `/home/xai/Documents/sunset/run_pipeline/core/cleaner_module.py` - Cleans job descriptions
   - `/home/xai/Documents/sunset/run_pipeline/core/cleaning_utils.py` - Utilities for text cleaning

10. `/home/xai/Documents/sunset/run_pipeline/core/status_checker_module.py` - Checks job statuses online

11. `/home/xai/Documents/sunset/run_pipeline/core/skills_module.py` - Processes skills from job descriptions
    - `/home/xai/Documents/sunset/run_pipeline/core/skills_io.py` - I/O functions for skills
    - `/home/xai/Documents/sunset/run_pipeline/core/skills_categorization.py` - Skill categorization
    - `/home/xai/Documents/sunset/run_pipeline/core/skills_decomposition.py` - Skill decomposition
    - `/home/xai/Documents/sunset/run_pipeline/core/skills_importance.py` - Skill importance assessment

12. `/home/xai/Documents/sunset/run_pipeline/core/auto_fix.py` - Automatically fixes jobs with missing skills
13. `/home/xai/Documents/sunset/run_pipeline/core/skill_matching_orchestrator.py` - Coordinates skill matching

## Skill Matching Modules

14. `/home/xai/Documents/sunset/run_pipeline/skill_matching/bucket_matcher.py` - Main bucketed skill matcher used in the pipeline
15. `/home/xai/Documents/sunset/run_pipeline/skill_matching/bucketed_skill_matcher.py` - Skill matching logic
16. `/home/xai/Documents/sunset/run_pipeline/skill_matching/bucket_utils_fixed.py` - Utilities for bucketed matching
17. `/home/xai/Documents/sunset/run_pipeline/skill_matching/embedding_utils.py` - Utilities for embedding-based matching
18. `/home/xai/Documents/sunset/run_pipeline/skill_matching/bucket_cache.py` - Caching for bucket matcher results

## Utility Modules

19. `/home/xai/Documents/sunset/run_pipeline/utils/logging_utils.py` - Logging utilities
20. `/home/xai/Documents/sunset/run_pipeline/utils/llm_client.py` - LLM API client
21. `/home/xai/Documents/sunset/run_pipeline/utils/common_tools.py` - Common utility functions

## Optional/Deprecated Modules

22. `/home/xai/Documents/sunset/run_pipeline/core/scraper_module.py` - Web scraping (deprecated, now using API details)
23. `/home/xai/Documents/sunset/run_pipeline/utils/firefox_utils.py` - Browser utilities (deprecated)

## Unused/Testing Modules

The following modules exist in the codebase but are not directly used in the main pipeline workflow:

- `/home/xai/Documents/sunset/run_pipeline/skill_matching/enhanced_skill_matcher.py` - Experimental skill matcher
- `/home/xai/Documents/sunset/run_pipeline/skill_matching/efficient_skill_matcher.py` - Alternative matcher
- `/home/xai/Documents/sunset/run_pipeline/skill_matching/sdr_job_update.py` - SDR-related code (removed from workflow)
- Multiple test modules in `/run_pipeline/skill_matching/test_*.py`

## Previously Used (Now Archived)

The following modules were previously used but have been archived or replaced:

- Files in `/home/xai/Documents/sunset/run_pipeline BAK/` - Backup of previous pipeline implementation
