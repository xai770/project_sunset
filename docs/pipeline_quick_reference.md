# Quick Reference: JMFS Pipeline Components

## Main Pipeline Commands

```bash
# Run the complete pipeline
python run_pipeline.py --job-ids 12345 --enable-feedback-loop

# Force a job to have a "Good" match for testing
python run_pipeline.py --job-ids 12345 --force-good-match 12345 --enable-feedback-loop

# Run without feedback loop
python run_pipeline.py --job-ids 12345

# Skip certain steps
python run_pipeline.py --job-ids 12345 --skip-fetch --skip-status-check
```

## Testing Commands

```bash
# Test the modular pipeline structure
python test_modular_structure.py

# Run cover letter integration test
python cover_letter_integration_test.py --job-id 12345

# Test cover letter generation
python test_cover_letter_generation.py
```

## Key Modules and Functions

### Pipeline Orchestration
```python
from run_pipeline.core.pipeline_orchestrator import run_pipeline
from run_pipeline.core.cli_args import parse_args

# Get default arguments
args = parse_args()

# Override specific arguments
args.job_ids = "12345"
args.enable_feedback_loop = True

# Run the pipeline
success = run_pipeline(args)
```

### Job Scanning
```python
from run_pipeline.core.job_scanner import run_job_scanner

# Scan for jobs
success, discovered_jobs = run_job_scanner(args, job_ids=None, log_dir=log_dir)
```

### Job Matching
```python
from run_pipeline.core.job_matcher import run_job_matcher

# Match jobs
run_job_matcher(args, job_ids=["12345"])
```

### Feedback Loop
```python
from run_pipeline.core.feedback_loop import execute_feedback_loop

# Run all feedback loop steps
execute_feedback_loop(args, log_dir)

# Or run individual steps
from run_pipeline.core.feedback_loop import (
    run_excel_export_step,
    run_cover_letter_generation_step,
    run_email_delivery_step,
    run_feedback_processing_step
)

excel_path = run_excel_export_step(args, log_dir)
run_cover_letter_generation_step(args, excel_path, log_dir)
run_email_delivery_step(args, excel_path, log_dir)
run_feedback_processing_step(args, log_dir)
```

### Testing Utilities
```python
from run_pipeline.core.test_utils import force_good_match_for_testing

# Force a job to have a "Good" match
job_data = force_good_match_for_testing("12345")
```

## Directory Structure

```
run_pipeline/
├── core/
│   ├── pipeline_orchestrator.py   # Main pipeline orchestration
│   ├── job_scanner.py             # Job scanning functionality
│   ├── job_matcher.py             # Job matching functionality
│   ├── feedback_loop.py           # Feedback loop steps 7-10
│   ├── test_integration.py        # Testing integration utilities
│   └── test_utils.py              # Testing utilities
```

## Common Issues and Solutions

1. **Missing job IDs in Excel**: Make sure the Excel file format matches expected columns. Use `--force-reprocess` to refresh data.

2. **Cover letters not generated**: Verify jobs have "Good" match level. Use `--force-good-match` to test.

3. **Email delivery fails**: Check email configuration in credentials.json.

4. **Feedback not processed**: Ensure correct excel format with feedback column.
