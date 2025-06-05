# JMFS Pipeline Changelog

This file tracks changes made to the Job Match Feedback System (JMFS) pipeline.

## May 28, 2025

### Added

- Modularized pipeline architecture for improved maintainability:
  - Split pipeline_orchestrator.py into smaller, focused modules:
    - job_scanner.py - For job scanning functionality
    - job_matcher.py - For job matching using LLM
    - feedback_loop.py - For Excel export, cover letter generation, and email delivery
    - test_integration.py - For testing utilities
  - Added comprehensive documentation for the new modular structure
  - Created test_modular_structure.py for testing the new architecture

- Enhanced cover letter generation with revolutionary features:
  - Added SkillsGapAnalyzer for analyzing job requirements vs. candidate skills
  - Added ProjectValueMapper to match candidate projects with job requirements
  - Added VisualEnhancer for improved cover letter formatting and visual presentation
  - Implemented skill match charts and qualification summaries in cover letters
  - Added support for highlighting quantifiable achievements in cover letters
  - Created supporting data files (CV skills and project data JSON files)
  - Added type stubs (.pyi files) for MyPy type checking support
  - Enhanced job-specific targeting in cover letters

### Fixed

- Fixed MyPy errors in process_excel_cover_letters.py:
  - Resolved duplicate class definition issues
  - Added type ignores where appropriate
  - Improved module import handling
  - Fixed import resolution for the new cover letter modules

### Changed

- Updated cover letter output format with improved visual styling
- Enhanced cover letter template with modern formatting elements
- Improved documentation for cover letter generation features

## May 27, 2025

### Fixed

- Updated CV file path to correctly load from `/home/xai/Documents/sunset/config/cv.txt`
- Fixed bug in `determine_domain_gap` function in `export_job_matches.py` that was causing NoneType errors
- Added proper null-checking for `llama_eval` fields to prevent errors in Excel export
- Removed redundant `run_pipeline.py` script from root directory in favor of using the modular pipeline structure in `run_pipeline/core/`
- Fixed empty Application narrative column in Excel export by adding appropriate default values
- Ensured the generated verify_fixes.py script correctly checks all fixed issues
- Modified pipeline_main.py to backup and remove files from data/postings when using --reset-progress
- Created a simple verification script (simple_verify.py) to avoid openpyxl memory issues
- Verified all fixes are working correctly with the comprehensive tests

### Added

- Added exact prompt to LLM response files for better debugging
- Created `reset_pipeline.py` utility for:
  - Resetting scan progress to run pipeline from scratch
  - Resetting job evaluations (all or specific jobs)
  - Deleting response files to free up space
  - Full pipeline reset option
- Added this changelog file to track modifications
- Enhanced `--reset-progress` option to automatically backup and remove files in data/postings directory

### Changed

- Modified CV loader to only look in the correct location and throw appropriate errors
- Updated test scripts to use centralized CV loader
- Improved error handling throughout the pipeline

## May 26, 2025

### Fixed

- Fixed critical LLM job evaluation bug where jobs were incorrectly rated as "Good match"
- Added "THIS RULE IS ALWAYS VALID!" to the Low match criterion in prompt
- Implemented strict rule that if any LLM run returns "Low match", the final result is "Low match"
- Fixed empty columns in Excel export (Job domain, Application narrative, generate_cover_letters_log)

### Added

- Added domain gap detection to downgrade potential misclassifications
- Created test scripts to verify fixes (test_fixes.py and comprehensive_test.py)
- Added print statement to show generated file after export

### Changed

- Renamed column 'URL' to 'Job ID' in Excel export
- Made domain knowledge gap detection more sensitive
- Lowered thresholds for domain gap severity
