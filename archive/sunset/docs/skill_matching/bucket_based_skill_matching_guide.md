# Bucket-Based Skill Matching System

## Overview

The bucket-based skill matching system provides an efficient and accurate method for matching job skills to CV skills. It groups skills into predefined categories (buckets) and performs matching at the bucket level rather than individual skills, resulting in faster processing and more meaningful match results.

## Implementation Versions

The system has three implementation versions available:

1. **Standard Version**: Basic implementation of bucket-based matching
2. **Fixed Version**: Improved implementation with better error handling and performance
3. **Enhanced Version**: Advanced implementation with comprehensive improvements

## Key Features

### Standard Features (All Versions)

- **Skill Categorization**: Skills are grouped into 5 primary buckets:
  - Technical: Programming, development, engineering skills
  - Management: Leadership, project management, coordination
  - Domain Knowledge: Industry-specific knowledge
  - Soft Skills: Communication, teamwork, problem-solving
  - Analytics: Data analysis, business intelligence, reporting

- **Bucket-Level Matching**: Compares skills at category level rather than individually

- **Weighted Scoring**: Overall match score based on weighted bucket scores

### Additional Features (Enhanced Version)

- **Improved Error Handling**: Retry mechanism with exponential backoff
- **Advanced Skill Extraction**: Better identification from unstructured text
- **Optimized Performance**: Two-level parallelism and batch processing
- **Auto-Fix Integration**: Seamless integration with the pipeline's auto-fix functionality

## Using the Bucket-Based Skill Matcher

### Direct Command Line Usage

Run the bucket matcher directly:

```bash
# Standard version
python -m run_pipeline.skill_matching.bucketed_skill_matcher --job-ids 123 456 --max-workers 4

# Enhanced version (recommended)
python -m run_pipeline.skill_matching.run_bucket_matcher --job-ids 123 456 --max-workers 6
```

### Pipeline Integration

Use within the main pipeline with the `--bucketed` flag:

```bash
python -m run_pipeline.core.pipeline --run-skill-matching --bucketed --max-workers 6
```

### Auto-Fix Integration

Run the auto-fix functionality with bucketed matching:

```bash
python -m run_pipeline.skill_matching.run_bucket_matcher --fix-issues
```

### Testing the Implementation

Test the bucket matcher with a small set of jobs:

```bash
python -m run_pipeline.skill_matching.test_bucket_matcher --job-ids 123 456
```

## Command Line Options

### Main Options

- `--job-ids`: Specific job IDs to process
- `--batch-size`: Batch size for processing (default: 10)
- `--max-workers`: Maximum worker threads (default: 4 or 6 for enhanced)
- `--force-reprocess`: Force reprocessing even if jobs already have matches
- `--fix-issues`: Detect and fix issues with job skills and matches

### Pipeline-Specific Options

- `--bucketed`: Enable bucket-based skill matching
- `--run-skill-matching`: Run skill matching in the pipeline

## Understanding Match Results

The match results include:

1. **Overall Match Score**: A weighted average of all bucket matches
2. **Bucket Results**: Detailed information for each bucket:
   - Match percentage: How well CV skills match job skills in this bucket
   - Weight: The importance of this bucket for the job
   - Job skills: List of job skills in this bucket
   - CV skills: List of CV skills in this bucket

## Examples

### Example Result Structure

```json
{
  "skill_match": {
    "overall_match": 0.65,
    "bucket_results": {
      "Technical": {
        "match_percentage": 0.8,
        "weight": 0.4,
        "job_skills": ["Python", "SQL", "Docker"],
        "cv_skills": ["Python", "JavaScript", "SQL", "Git"]
      },
      "Management": {
        "match_percentage": 0.6,
        "weight": 0.2,
        "job_skills": ["Project Management", "Team Leadership"],
        "cv_skills": ["Project Management", "Agile"]
      },
      "Domain_Knowledge": {
        "match_percentage": 0.4,
        "weight": 0.1,
        "job_skills": ["E-commerce", "Retail"],
        "cv_skills": ["E-commerce"]
      },
      "Soft_Skills": {
        "match_percentage": 0.7,
        "weight": 0.2,
        "job_skills": ["Communication", "Teamwork", "Problem Solving"],
        "cv_skills": ["Communication", "Critical Thinking", "Teamwork"]
      },
      "Analytics": {
        "match_percentage": 0.5,
        "weight": 0.1,
        "job_skills": ["Business Intelligence", "Data Analysis", "Reporting"],
        "cv_skills": ["Data Analysis", "Tableau"]
      }
    },
    "timestamp": "2025-05-21T14:30:45.123456"
  }
}
```

## Troubleshooting

### Common Issues

1. **Timeout Errors**: If you encounter timeout errors with LLM API calls, try:
   - Reducing batch size
   - Using the enhanced version with retry mechanism
   - Increasing worker threads for better parallelism

2. **Missing Skills**: If jobs lack extracted skills:
   - Use the enhanced version with improved skill extraction
   - Run with `--fix-issues` flag to detect and fix missing skills
   - Check job descriptions for valid skill information

3. **Performance Issues**: For large job datasets:
   - Use batch processing with appropriate batch size
   - Adjust worker thread count based on available resources
   - Use the enhanced version with optimized performance

### LLM Connectivity

The bucket-based skill matcher relies on LLM API calls. Ensure:
- Ollama service is running locally (default: http://localhost:11434)
- The specified model is available (default: gemma3:4b)
- Environment variables OLLAMA_HOST and OLLAMA_MODEL are set if using custom configuration

## Advanced Usage

### Running Benchmarks

Compare different skill matching approaches:

```bash
python -m run_pipeline.skill_matching.run_bucket_matcher --benchmark
```

### Customizing Buckets

Edit the SKILL_BUCKETS dictionary in bucket_utils.py to customize skill categories.

### Combining with SDR

For maximum accuracy, you can run both SDR and bucketed matching:

```bash
python -m run_pipeline.core.pipeline --use-sdr --sdr-use-llm --run-skill-matching --bucketed
```

This will enrich job skills with SDR first, then perform bucket-based matching.
