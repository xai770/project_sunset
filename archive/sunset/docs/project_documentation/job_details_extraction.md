# Job Details Extraction with LLMs

## Overview

The Job Details Extraction module uses LLMs to automatically extract essential information from job postings in a structured format. It leverages our task optimizer framework to select the most effective model for extracting key job details while filtering out non-essential information. Our enhanced system now employs a consensus-based approach using multiple models for higher reliability.

## Features

- **Multi-Model Consensus Verification**: Uses multiple LLMs and verifies agreement between their outputs
- **Intelligent Model Selection**: Uses the task optimizer to select the best LLMs for job extraction
- **Focused Extraction**: Extracts only essential job information (title, location, responsibilities, requirements, contact)
- **Performance Tracking**: Records model performance to continuously improve extraction quality
- **Benchmarking**: Supports benchmarking multiple models to identify the most effective one
- **Structured Output**: Provides extracted data in both structured JSON and formatted text

## Usage

### Basic Usage

Extract job details from a specific job:

```bash
python scripts/extract_job_details.py 62914
```

Extract job details from multiple jobs:

```bash
python scripts/extract_job_details.py 62914 63144 64321
```

Process all available job postings:

```bash
python scripts/extract_job_details.py
```

### Advanced Options

Specify a particular model:

```bash
python scripts/extract_job_details.py 62914 --model llama3.2:latest
```

Save extracted details to a specific directory:

```bash
python scripts/extract_job_details.py 62914 --output-dir data/extracted_jobs
```

Benchmark all available models:

```bash
python scripts/extract_job_details.py --benchmark
```

## Output Format

The script produces JSON files with the following structure:

```json
{
  "title": "Senior Site Reliability Engineer (f/m/x) – Bulk Payments Tribe",
  "location": "Frankfurt",
  "responsibilities": [
    "Develop deployment automation (CI/CD)",
    "Create test automation framework using Java 17, SpringBoot, Cucumber, Mockito, Junit5, Lombok, OpenAPI",
    "Implement integration and deployment automation for test environments and production",
    "Upgrade systems with Oracle databases, MQ, Kafka, Unix, and NFS components"
  ],
  "requirements": [
    "Computer science or equivalent degree",
    "Experience with Java 17, Spring Boot, Cucumber, Mockito, Junit5, Lombok, OpenAPI",
    "Knowledge of Oracle Databases, MQ, Kafka, Unix and NFS",
    "CI/CD expertise: TeamCity/Jenkins, Docker, Kubernetes, cloud environments",
    "JMeter for Java experience",
    "Payment systems knowledge (SEPA, B@fir) is a plus"
  ],
  "contact_info": "Ayse Kartal-Isik: +49 69 910-42410",
  "extracted_text": "[Full extracted text]",
  "extraction_model": "gemma3:1b",
  "extraction_time": 1.25,
  "job_id": "62914",
  "extraction_timestamp": "2025-05-09 15:30:45"
}
```

## Integration with Existing Systems

The extracted job details can be used to:

1. **Enhance job matching**: Focus on essential skills and responsibilities
2. **Improve self-assessment**: Generate more targeted self-assessment narratives
3. **Simplify job exploration**: Allow users to quickly scan key job requirements
4. **Optimize skill decomposition**: Concentrate on the most relevant job aspects

## Technical Implementation

The job extraction mechanism registers a new task type (`job_extraction`) with the task optimizer system and defines appropriate quality and speed priorities. It uses a concise prompt that instructs the LLM to focus only on essential details while excluding marketing content, cultural statements, and benefit descriptions.

The implementation includes:
- Performance tracking for continuous improvement
- Automatic ranking updates based on extraction quality
- Structural parsing of the LLM output for consistent JSON formatting
- Consensus verification between multiple LLM models

### Testing Consensus-Based Extraction

To test the reliability of the consensus-based extraction approach, use:

```bash
python scripts/tests/test_consensus_extraction.py --jobs 10
```

This will test the extraction on 10 random job postings and evaluate:
- Success rate of extractions
- Rate of consensus agreement between models
- Execution time of different models

You can also test specific jobs:

```bash
python scripts/tests/test_consensus_extraction.py --ids 62914,63144,64321
```

Test results are saved to the `data/test_results` directory for analysis.

## Model Recommendations

Initial benchmarking suggests that models with strong instruction-following capabilities perform best at this task, with `gemma3:1b` offering an excellent balance of quality and speed for most job postings. For consensus verification, pairing `gemma3:1b` with `llama3.2:latest` provides high reliability.
