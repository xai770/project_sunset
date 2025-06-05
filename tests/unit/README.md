# Unit Tests

This directory contains unit tests for individual components and modules of Project Sunset.

## Test Files

### `test_cover_letter_generation.py`
Unit tests for cover letter generation functionality, testing individual components and edge cases.

### `test_custom_filename.py`
Tests for custom filename generation and file naming conventions.

### `test_modular_pipeline.py`
Unit tests for the modular pipeline architecture, testing individual pipeline components in isolation.

### `test_modular_structure.py`
Tests for the modular structure and component organization of the system.

## Purpose

Unit tests verify:
- Individual component functionality
- Input/output validation
- Error handling and edge cases
- Component isolation and modularity

## Running Tests

```bash
# From project root
python tests/unit/test_cover_letter_generation.py
python tests/unit/test_modular_pipeline.py
python tests/unit/test_modular_structure.py
python tests/unit/test_custom_filename.py

# Run all unit tests
python -m pytest tests/unit/ -v
```

## Test Structure

Unit tests should:
- Test one component at a time
- Use mock data and dependencies
- Be fast and independent
- Have clear, descriptive names
- Include edge cases and error conditions

## Dependencies

- pytest framework
- Mock objects for external dependencies
- Test fixtures and sample data
