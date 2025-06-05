# Project Sunset Open Topics

This document tracks ongoing work, planned improvements, and technical debt that needs to be addressed in Project Sunset. Use this as a reference when starting new development sessions to quickly understand what needs attention.

## Recently Completed Work

### Translation System Modernization (May 6, 2025)

- ✅ Separated the translation dictionary from code
  - Created translation_dictionary.json with categorized translations (technical terms, job roles, etc.)
  - Added more translations including common prepositions and job-related terms
  
- ✅ Implemented LLM-based fallback translation
  - Created clear strategy: dictionary for 1-2 word phrases, LLM for 3+ words
  - Added caching to improve performance
  - Integrated with langdetect for better language detection
  
- ✅ Benchmarked multiple LLM models for translation quality and speed
  - Tested llama3.2, phi3, mistral, and qwen2.5
  - phi3 provided the best balance of speed and quality (avg 1.70s/translation)
  - All models successfully translated phrases like "in der Projektleitung" that previously caused issues
  
- ✅ Created test and benchmark scripts for the translation system
  - tests/test_translator.py for basic functionality testing
  - tests/benchmark_translator.py for comparing model performance

### Self-Assessment System Fixes (May 6, 2025)

- ✅ Fixed missing functions and imports in the self-assessment system
  - Added missing `find_job_file` function to utils.py
  - Removed references to non-existent `CONSOLIDATED_JOBS_DIR` across all files
  - Fixed circular imports in controller.py by creating a separate version.py module
  - Implemented missing search functions in skill_decomposer/searcher.py
  - Fixed incorrect function name references (e.g., `is_semantic_match` → `find_best_semantic_match`)
  - Fixed `is_requirement_blacklisted` and similar functions

- ✅ Prevented duplicate assessment file creation
  - Modified test_self_assessment_controller.py to avoid creating separate JSON files
  - Self-assessments are now stored only in job JSON files as intended

- ✅ Updated ISA documentation with our recent fixes

## Current Work In Progress

### 1. Translation System Enhancements (ON HOLD - May 6, 2025)
- Testing new Ollama models for improved translation performance
- Planning to commit final changes after model testing is complete
- Need to decide on default model (currently phi3 is recommended)

## Next Tasks

### 1. Codebase Organization and Cleanup

Review and reorganize outdated code:

- Identify which scripts are actually used by the job processing pipeline
- Move unused or legacy scripts to a new "legacy" or "archive" folder
- Document which scripts are still in active use
- Remove duplication between similar modules

### 2. Rename Job Scraper to Better Reflect Functionality

The current name "job_scraper" doesn't accurately represent the full functionality:

- Rename to something more descriptive (e.g., "job_processor", "career_pipeline", or "opportunity_manager")
- Update all imports and references to maintain compatibility
- Update documentation to reflect the new name

### 3. Cover Letter Generation Review

Once other improvements are complete:

- Review and enhance the cover letter generation system
- Ensure proper integration with the improved self-assessment system
- Add more personalization based on job requirements
- Improve template variety and adaptability

### 4. Additional Topics for Future Work

- Fix any remaining path inconsistencies across the codebase
- Consider more extensive unit testing for critical components
- Implement proper error reporting and recovery mechanisms
- Improve logging system for better traceability
- Add data validation to prevent malformed job data

## Technical Debt

### Import Structure Issues

- Multiple circular imports need to be resolved
- Some imports use relative paths while others use absolute paths
- Need consistent import strategy across the codebase

### Inconsistent File Structures

- Some modules use different file organization patterns
- Inconsistent naming conventions across modules

### Code Duplication

- Duplicate functionality exists between some utility modules
- Need to centralize common operations

## Ideas for Future Enhancements

- AI-based job matching score improvements
- Enhanced CV customization for specific job applications
- Dashboard for tracking job application status
- Integration with email for automated follow-ups
- Improved visualization of skill gaps and recommendations

## Notes and Concerns

*Add any additional topics or concerns here as they arise.*