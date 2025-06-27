# LLM Model Benchmarks for Self-Assessment

This document provides benchmark results for different LLM models when generating self-assessments for job postings.

## Benchmark Results - May 9, 2025

We tested various Ollama models to determine the most efficient option for running self-assessments.

| Model | Execution Time (seconds) |
|-------|--------------------------|
| gemma3:1b | 1.32 |
| llama3.2:latest | 2.25 |
| qwen3:0.6b | 2.50 |
| mistral:latest | 2.71 |
| dolphin3:latest | 3.64 |
| phi3:3.8b | 9.03 |

## Observations

- **Fastest Model**: gemma3:1b is significantly faster (~1.3s) while still providing quality output
- **Good Balance**: llama3.2:latest and qwen3:0.6b offer a good balance of speed (~2.5s) and quality
- **Slowest Model**: phi3:3.8b takes nearly 7x longer than the fastest model (~9s)

## Implementation Notes

To switch between models, use the `--model` command line argument:

```bash
python rerun_self_assessment.py 61951 --model gemma3:1b
```

All models can be listed with:

```bash
python rerun_self_assessment.py --list-models
```

Test a specific model with:

```bash
python rerun_self_assessment.py --test-model gemma3:1b
```

## Fix for Requirement Parsing Issue

We identified and fixed an issue where string requirements weren't being properly handled in the `requirement_matcher.py` file. The issue manifested as:

```
Error processing requirement 'Tax Compliance': string indices must be integers, not 'str'
```

The fixes implemented:

1. Added proper type handling in `match_requirement()` to handle both string requirements and complex requirement objects
2. Updated error handling in `match_all_requirements()` to properly handle and report errors regardless of requirement format

These changes ensure the system can work with different requirement formats across job descriptions.
