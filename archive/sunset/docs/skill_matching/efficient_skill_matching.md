# Efficient Skill Matching

This document describes the new efficient skill matching system and how to use it.

## Overview

The new skill matching system addresses efficiency issues with the original implementation, especially when dealing with large numbers of skills. It includes:

1. **Category-based pre-filtering**: Groups skills by categories and only compares compatible categories
2. **Batched LLM processing**: Processes multiple skill comparisons in a single LLM API call
3. **Caching mechanism**: Remembers previous skill comparisons to avoid redundant API calls
4. **Improved domain overlap**: More accurate and efficient skill matching algorithm

## How It Works

The new approach significantly reduces the number of comparisons and API calls:

1. Skills are categorized into high-level categories like "Technical", "Management", etc.
2. Only compatible categories are compared (e.g., "Technical" skills might be compared with "Technical" and "Management" skills)
3. LLM calls are batched to process multiple skill pairs in a single API request
4. Results are cached so repeated comparisons don't require additional API calls

## Benefits

- **Speed**: 5-10x faster than the original implementation when using LLM matching
- **Scalability**: Performance improves as you process more jobs due to increased cache hits
- **Accuracy**: Still uses LLM for accuracy, but more efficiently
- **Lower resource usage**: Fewer API calls means less load on your Ollama server

## Usage

### Running the Pipeline with Efficient Matching

The main pipeline has been updated to use the efficient matcher by default:

```bash
python -m run_pipeline.core.pipeline --run-skill-matching --batch-size 10
```

### Command Line Arguments

New command line arguments:

- `--batch-size`: Number of skill pairs to process in a single LLM API call (default: 10)

### Running Benchmarks

To compare the performance of the original and new implementation:

```bash
python -m run_pipeline.skill_matching.benchmark_skill_matcher --job-ids 48444 50570 50571 --batch-sizes 5 10 20
```

This will:
1. Run benchmarks for individual job matching
2. Run benchmarks for batch job matching
3. Generate a report showing speedup factors

## How to Choose Batch Size

The optimal batch size depends on:

- Your available CPU and memory
- The Ollama model you're using
- How many comparisons you need to make

Guidelines:
- **Small batch (5-8)**: Good for smaller models or limited resources
- **Medium batch (10-15)**: Good balance for most use cases
- **Large batch (20+)**: Better for high-end systems with powerful models

## Cache Management

The skill match cache is stored in `data/skill_match_cache/skill_match_cache.json` and grows over time. If it becomes too large:

```bash
# Clear the cache (creates a new empty cache)
rm -f /home/xai/Documents/sunset/data/skill_match_cache/skill_match_cache.json
```
