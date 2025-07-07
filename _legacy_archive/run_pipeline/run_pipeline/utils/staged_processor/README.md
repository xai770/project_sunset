# Staged Job Description Processor Package

## Overview

The Staged Job Description Processor is a modular package that processes job descriptions through multiple sequential stages:

1. **HTML Cleaning**: Removes HTML tags and formatting from raw job descriptions
2. **Language Handling**: Detects language, extracts English sections from bilingual content, or translates if necessary
3. **Text Extraction**: Extracts and structures relevant job details using LLM

This package is a refactored and modularized version of the original monolithic `staged_job_description_processor.py` script, improving maintainability, readability, and extensibility while maintaining backward compatibility.

## Package Structure

```
staged_processor/
├── __init__.py           # Package initialization and exports  
├── processor.py          # Main processor class and job processing logic
├── html_cleaner.py       # HTML tag and formatting removal
├── language_handler.py   # Language detection and translation
├── extractors.py         # Text extraction and structured formatting
├── file_handler.py       # File loading and saving operations
├── utils.py              # Common utilities and helper functions
├── cli.py                # Command-line interface (optional)
└── README.md             # This documentation
```

## Key Components

### StagedJobProcessor Class

The main class that orchestrates the job description processing pipeline:

```python
from run_pipeline.utils.staged_processor.processor import StagedJobProcessor

# Initialize the processor
processor = StagedJobProcessor(model="llama3.2:latest")

# Process a job
result = processor.process_job(
    job_id="12345",
    dry_run=False,
    output_format="text"
)
```

### process_jobs Function

A high-level function that processes multiple jobs:

```python
from run_pipeline.utils.staged_processor.processor import process_jobs

# Process multiple jobs
processed, success, failure = process_jobs(
    job_ids=["12345", "67890"],
    model="llama3.2:latest",
    dry_run=False,
    output_format="text"
)
```

## Module Details

### processor.py

The core module containing the `StagedJobProcessor` class and `process_jobs` function that orchestrate the entire job processing pipeline.

### html_cleaner.py

Contains functions for cleaning HTML from job descriptions:
- Removes HTML tags and attributes
- Normalizes whitespace and line breaks
- Handles specific formatting patterns

### language_handler.py

Handles language detection and translation:
- Detects the primary language of job descriptions
- Extracts English portions from bilingual content
- Translates non-English content to English when necessary

### extractors.py

Extracts and formats job details:
- Uses LLM to extract relevant job information
- Structures the output in consistent format
- Supports both text and JSON output formats

### file_handler.py

Manages file input and output operations:
- Loads job data from JSON files
- Extracts HTML content from job data
- Saves processed job data back to files

### utils.py

Provides common utilities used across the package:
- Logging configuration
- Text cleaning functions
- Language detection patterns
- Common constants

## Usage Examples

### Basic Usage

```python
from run_pipeline.utils.staged_processor import StagedJobProcessor

processor = StagedJobProcessor()
result = processor.process_job("12345")
```

### Processing Multiple Jobs

```python
from run_pipeline.utils.staged_processor.processor import process_jobs

processed, success, failure = process_jobs(
    job_ids=["12345", "67890"],
    model="llama3.2:latest"
)
```

### Command-line Usage (via Wrapper)

```bash
# Process specific jobs
python run_pipeline/utils/staged_job_description_processor.py --job-ids 12345,67890

# Dry run with JSON output
python run_pipeline/utils/staged_job_description_processor.py --job-ids 12345 --dry-run --output-format json
```

## Integration with Pipeline

The processor is integrated with the main pipeline through:
1. The backward compatibility wrapper at `run_pipeline/utils/staged_job_description_processor.py`
2. Direct imports in `run_pipeline/core/cleaner_module.py`

## Implementation Notes

### Handling Circular Imports

This package uses dynamic imports to avoid circular dependencies between modules, particularly between `processor.py` and `cleaner_module.py`.

### Code Design Principles

1. **Separation of Concerns**: Each module has a clear, focused responsibility
2. **Single Responsibility Principle**: Classes and functions perform one specific task
3. **DRY (Don't Repeat Yourself)**: Common utilities are centralized
4. **Backward Compatibility**: Original API is preserved

## Testing

Test the package functionality with:

```bash
# Test basic functionality
python test_staged_processor.py

# Test with multiple jobs and formats
python test_staged_processor_batch.py
```

## Future Improvements

Potential enhancements for future versions:

1. Add more comprehensive error handling and recovery mechanisms
2. Implement caching for LLM responses to improve performance
3. Add unit tests and integration tests for each module
4. Extend language support for less common languages
5. Add configuration options for HTML cleaning and extraction rules
