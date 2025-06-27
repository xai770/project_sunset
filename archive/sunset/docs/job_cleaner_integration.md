# Job Description Cleaner Integration

**Date:** May 14, 2025  
**Author:** GitHub Copilot  

## Overview

This document describes the integration of the job description cleaning functionality into the new pipeline structure. The job cleaner module uses Ollama to generate concise job descriptions from HTML content extracted from job postings.

## Implementation Details

### Key Components

The job description cleaner has been refactored from a standalone script into a modular component:

- **Integrated Module**: `run_pipeline/core/cleaner_module.py`
- **Original Script**: `scripts/job_description_cleaner.py`

### Key Functions

The cleaner module provides these main functions:

1. **extract_concise_description**: Interacts with Ollama to generate concise job descriptions
2. **clean_llm_artifacts**: Cleans up common artifacts from LLM responses
3. **process_job_files**: Processes job files and updates with concise descriptions
4. **clean_job_descriptions**: Main entry point that orchestrates the cleaning process

### Testing Support

The module includes testing support for CI/CD environments:

- Environment variable `TEST_MODE=1` enables hardcoded responses for testing
- `test_job_cleaner.py` provides a specialized test script with mock LLM responses

## Usage

The job cleaner can be used in different ways:

### As Part of the Pipeline

```python
from run_pipeline.core.pipeline import run_pipeline
from run_pipeline.config.paths import DEFAULT_MODEL

# Run the complete pipeline with the job cleaner
run_pipeline(max_jobs=10, model=DEFAULT_MODEL)
```

### Standalone Usage

```python
from run_pipeline.core.cleaner_module import clean_job_descriptions

# Just run the job cleaner component
clean_job_descriptions(max_jobs=5, model="phi3")
```

### Test Mode

```bash
# Set environment variable for testing
export TEST_MODE=1

# Run the pipeline in test mode
python run_job_pipeline.py 
```

## Improvements

The refactored job cleaner module offers several improvements over the original implementation:

1. **Direct Integration**: The module directly interacts with Ollama without subprocess calls
2. **Better Error Handling**: Comprehensive error handling and recovery
3. **Detailed Metrics**: Tracks compression ratios and performance metrics
4. **Consistent Logging**: Uses the pipeline's central logging infrastructure
5. **Testing Support**: Easily testable with mock responses

## Future Enhancements

1. Implement adaptive prompt templates based on job types
2. Add fallback models if the primary model fails
3. Implement caching for LLM responses to reduce API calls
4. Add parallel processing for multiple jobs
