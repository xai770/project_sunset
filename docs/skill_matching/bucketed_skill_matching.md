# Bucketed Skill Matching

## Overview

The bucketed skill matching approach provides a significantly faster and more efficient method for matching job skills to CV skills compared to the previous implementations. Instead of comparing individual skills, this approach:

1. Categorizes skills into predefined buckets (Technical, Management, Domain Knowledge, etc.)
2. Compares skills within each bucket
3. Calculates a weighted match score based on the importance of each bucket in the job description

This approach addresses the performance issues with previous implementations while still providing meaningful match results.

## Key Components

### 1. Skill Categorization

Skills are automatically categorized into the following buckets:

- **Technical**: Programming languages, software development, engineering skills
- **Management**: Leadership, project management, team coordination
- **Domain Knowledge**: Industry-specific knowledge (finance, healthcare, etc.)
- **Soft Skills**: Communication, teamwork, problem-solving
- **Analytics**: Data analysis, business intelligence, reporting

The categorization uses keyword matching for fast and reliable bucket assignment.

### 2. Bucket-Based Matching

Instead of comparing every job skill with every CV skill (which grows quadratically), this approach:

- Groups job skills into buckets
- Groups CV skills into the same buckets
- Compares only within relevant buckets
- Uses a single LLM call per bucket to determine match quality

### 3. Weighted Scoring

The final match score is weighted based on:

- The proportion of skills in each bucket (indicating bucket importance)
- The match quality within each bucket
- A minimum weight for buckets with at least one skill

This ensures a fair and representative overall match score.

### 4. Performance Optimizations

The latest version includes significant performance optimizations:

- **Parallel Processing**: Multiple buckets are processed simultaneously using thread pools
- **Two-Level Parallelism**: Both job processing and bucket comparison are parallelized
- **Thread-Safe Caching**: All LLM responses are cached with TTL support
- **Optimized LLM Prompts**: More focused prompts produce faster responses
- **Efficient Resource Distribution**: Worker threads are optimally allocated

## Code Structure

The implementation is split across multiple files for better maintainability:

- `bucket_cache.py`: Thread-safe caching for bucket matching results
- `bucket_utils.py`: Utility functions for skill extraction and categorization
- `bucket_matcher.py`: Core matching logic using LLM
- `bucketed_skill_matcher.py`: Main module coordinating the matching process
- `bucketed_benchmark.py`: Comprehensive benchmarking tool
- `bucketed_pipeline.py`: Integration with the main pipeline

## Usage

### Command Line Usage

Run the bucketed skill matcher directly:

```bash
python -m run_pipeline.skill_matching.bucketed_skill_matcher \
  --job-ids 123 456 789 \
  --batch-size 10 \
  --max-workers 4
```

### Pipeline Integration

Use the bucketed approach in the main pipeline:

```bash
python -m run_pipeline.core.pipeline \
  --run-skill-matching \
  --bucketed \
  --max-workers 6
```

### Run Benchmarks

Compare performance against other implementations:

```bash
python -m run_pipeline.skill_matching.bucketed_benchmark \
  --job-ids 123 456 789 \
  --single --batch \
  --batch-size 10 \
  --max-workers 4
```

## Performance Benefits

Based on comprehensive benchmarks, the optimized bucketed approach offers:

1. **Improved Speed**: Now 5-10x faster than the initial bucketed implementation
2. **Parallel Efficiency**: Better utilization of available CPU cores
3. **Reduced API Costs**: Significantly fewer LLM API calls through strategic caching
4. **Balanced Workload**: Adaptive job and bucket parallelism for optimal performance

## Implementation Details

### Skill Extraction

The system extracts skills from:

1. SDR skills in job files (if available)
2. Job descriptions (using pattern matching if no SDR skills found)
3. CV skills from the skill_decompositions.json file

### LLM Prompting

For each bucket comparison, the LLM receives:

- A list of job skills in the bucket
- A list of CV skills in the bucket
- Instructions to evaluate match quality and provide a percentage

### Caching

The system includes:

- Thread-safe caching of bucket match results
- TTL-based cache expiration (30 days)
- Automatic cache persistence

## Hybrid Approach

The latest enhancement to skill matching combines the best features of bucketed matching and embedding-based techniques:

### 1. Combined Methodology

The hybrid approach uses:

- **Embedding-based Initial Filtering**: Fast vector similarity for preliminary matching
- **Granular Bucketing**: More detailed skill categories for domain-specific matching
- **LLM-based Detailed Analysis**: In-depth comparison for high-quality matches
- **Confidence Scoring**: Quantified reliability for each match

### 2. Enhanced Granular Buckets

Technical skills are now divided into more specific categories:

- Programming Languages
- Web Development
- Mobile Development
- Data Engineering
- DevOps & Cloud
- Security
- AI & Machine Learning
- Database Systems
- Network Infrastructure

Management skills are also more granularly categorized:

- Project Management
- Team Leadership
- Change Management
- Strategic Planning

### 3. Confidence Scoring

Each match now includes a confidence score based on:

- Embedding similarity
- Bucket relevance
- LLM confidence assessment
- Text pattern matching
- Contextual relevance

This provides a more reliable measure of match quality and helps prioritize skills.

## Future Improvements

Potential enhancements:

1. Improved skill extraction from raw job descriptions
2. Better skill categorization using embedding-based clustering
3. Auto-tuning of bucket weights based on feedback
4. Integration with multi-lingual skills
5. Personalized skill matching based on user preferences
