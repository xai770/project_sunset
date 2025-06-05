# Integration Tests

This directory contains integration tests that verify the interaction between different components of Project Sunset, particularly LLM Factory specialists and pipeline components.

## Test Files

### `cover_letter_integration_test.py`
Tests the integration of cover letter generation with the LLM Factory system.

### `migrate_to_llm_factory.py`
Migration script and test for transitioning from legacy LLM calls to LLM Factory specialists.

### `test_job_fitness_integration.py`
Tests the JobFitnessEvaluator integration with the pipeline system.

### `test_job_fitness_integration_fixed.py`
Updated and fixed version of the job fitness integration test.

## Purpose

Integration tests verify:
- LLM Factory specialist integration
- Pipeline component interactions
- End-to-end system functionality
- Migration compatibility

## Running Tests

```bash
# From project root
python tests/integration/test_job_fitness_integration_fixed.py
python tests/integration/cover_letter_integration_test.py
python tests/integration/migrate_to_llm_factory.py
```

## Dependencies

- LLM Factory must be properly installed and configured
- Ollama service should be running for full functionality
- All project dependencies must be installed
