# Job Matcher Module

This module has been migrated from the standalone `job_matcher` package to be integrated with the `run_pipeline` system.

## Components

- **job_processor.py**: Main module for processing job matches
- **feedback_handler.py**: Handles user feedback on job matches
- **prompt_adapter.py**: Adapts prompts for the job matcher
- **cv_utils.py**: Utilities for CV processing
- **response_parser.py**: Parses LLM responses
- **domain_analyzer.py**: Analyzes job domain requirements
- **llm_client.py**: Client for LLM interactions

## Usage

### Job Matching

```python
from run_pipeline.job_matcher.job_processor import process_job
from run_pipeline.job_matcher.cv_utils import get_cv_markdown_text

# Get CV text
cv_text = get_cv_markdown_text()

# Process a job match
job_id = "61691"
results = process_job(job_id, cv_text=cv_text, num_runs=3)

# Access results
match_level = results.get("cv_to_role_match")
domain_assessment = results.get("domain_knowledge_assessment")
```

### Feedback Processing

```python
from run_pipeline.job_matcher.job_processor import process_feedback

# Process feedback for a job
job_id = "61691"
feedback_text = "The match level should be Good instead of Moderate because the CV shows experience in all required domain-specific areas"
feedback_result = process_feedback(job_id, feedback_text, auto_update=False)
```

### Testing

The `run_pipeline/test_feedback_loop.py` script provides a way to test the feedback loop:

```bash
# Basic usage
./test_feedback_loop.py 61691 "The match level should be Good due to domain expertise"

# Save results automatically
./test_feedback_loop.py 61691 "The match level should be Good" --save

# Update prompts automatically based on feedback analysis
./test_feedback_loop.py 61691 "The match level should be Good" --auto-update

# Specify custom output file
./test_feedback_loop.py 61691 "The match level should be Good" --output results.json
```

## Integration Notes

- The module is now fully integrated with `run_pipeline/utils/prompt_manager.py` for prompt management
- All paths are now relative to the main project root
- The feedback system can still save feedback, analyze it, and optionally update prompts
