# Project Organization Summary

## Key Directories

* **run_pipeline/**: Main code for the pipeline system
  * **job_matcher/**: Job matching modules
  * **prompts/**: Prompt templates
  * **utils/**: Utility functions
* **scripts/**: Standalone scripts and utilities
  * **analyzers/**: Analysis modules including synergy_analyzer.py
* **data/**: Data files and caches
* **tests/**: Test files
* **docs/**: Documentation
* **logs/**: Log files

## Recent Changes

* Migrated job_matcher to run_pipeline/job_matcher
* Migrated prompts/job_matching to run_pipeline/prompts/job_matching
* Removed redundant 'run_pipeline copy' directory
* Created test scripts for feedback handling in run_pipeline/
