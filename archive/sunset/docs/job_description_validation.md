# Job Description Validation and Improvement

## Overview

This document describes a new utility for validating and improving job descriptions in the pipeline. The tool addresses three main issues identified in the current job description extraction process:

1. Non-English content (primarily German job descriptions)
2. Unstructured or incorrectly formatted descriptions
3. Descriptions with introductory remarks or unrelated content

> **Note: Updated May 18, 2025** - The staged job description processor has been integrated directly into the main pipeline. See [Staged Processor Integration](/docs/project_documentation/staged_processor_integration.md) for details.

## Features

The new utility provides the following features:

- **Language Detection**: Automatically detects non-English job descriptions
- **Translation**: Translates non-English descriptions to English 
- **Format Validation**: Ensures proper structure with Job Title, Responsibilities, and Requirements
- **Content Cleanup**: Removes introductory remarks and unrelated content
- **JSON Structuring**: Optionally converts descriptions to structured JSON format
- **Batch Processing**: Processes jobs in configurable batch sizes for efficiency

## Usage

### Command Line Interface

The utility can be run from the command line:

```bash
python run_pipeline/utils/validate_and_improve_job_descriptions.py [options]
```

Options:
- `--batch-size BATCH_SIZE`: Number of jobs to process in each batch (default: 10)
- `--model MODEL`: Model to use for translation and improvement (default: llama3.2:latest)
- `--job-ids JOB_IDS`: Comma-separated list of specific job IDs to process
- `--json-output`: Generate structured JSON output for job descriptions
- `--dry-run`: Identify and report issues without making changes

### Helper Scripts

Two helper scripts are provided:

1. `test_job_validation.py`: Tests validation on specific problematic job IDs
   ```bash
   python test_job_validation.py
   ```

2. `validate_job_descriptions.sh`: Batch script for processing all job descriptions
   ```bash
   ./validate_job_descriptions.sh
   ```

## Technical Details

### Language Detection

The tool uses two approaches for language detection:

1. Pattern-based detection using known markers in German texts
2. Library-based detection using `langdetect` (when available)

### Job Description Improvement Process

1. **Validation**: Checks for issues such as wrong language, improper structure, or unrelated content
2. **Translation**: If non-English, translates the content to English
3. **Restructuring**: Ensures proper format with Job Title, Responsibilities, and Requirements
4. **JSON Conversion**: Optionally extracts structured data into a JSON format

### Integration with Existing Pipeline

This tool builds on top of the existing job description extraction pipeline and uses the same underlying models and utilities. It does not modify the core extraction process but adds a validation and improvement layer on top.

## Example Usage

To process specific problematic job descriptions:

```bash
python run_pipeline/utils/validate_and_improve_job_descriptions.py --job-ids 48444,53231,58649 --json-output
```

To validate all job descriptions without making changes:

```bash
python run_pipeline/utils/validate_and_improve_job_descriptions.py --dry-run
```

To process all job descriptions with JSON output:

```bash
python run_pipeline/utils/validate_and_improve_job_descriptions.py --json-output
```

## Dependencies

- `langdetect` (optional): For improved language detection
  ```bash
  pip install langdetect
  ```
