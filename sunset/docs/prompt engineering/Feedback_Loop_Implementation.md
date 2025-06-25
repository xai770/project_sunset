# Job Matching Feedback Loop

This document describes the implementation of the feedback loop system for improving job matching accuracy based on user feedback.

## Overview

The feedback loop system consists of three components:

1. **Export with Feedback Column**: The job matching export now includes a 'Feedback' column where users can provide feedback on job matches.
2. **Prompt Management System**: A system for storing and versioning prompts used for job matching.
3. **Feedback Processing System**: A system that analyzes feedback and generates suggestions for prompt improvements.

## How It Works

![Feedback Loop Diagram](docs/images/feedback_loop_diagram.png)

1. Users review job matches in Excel and add feedback in the 'Feedback' column for incorrect matches
2. The feedback processor script reads Excel files and finds rows with feedback
3. Each feedback item is analyzed by the LLM to identify patterns and suggest improvements
4. The system generates consolidated recommendations for prompt improvements
5. The prompt is updated based on these recommendations (either automatically or manually)
6. Future job matching uses the improved prompt

## Components

### Export with Feedback Column

The `export_job_matches.py` script now includes a 'Feedback' column in the Excel export. This column is:
- Set to 36 characters width (3 inches)
- Has text wrapping enabled
- Uses the same font (Liberation Sans) as other columns

Users can enter their feedback directly in this column, such as:
- "Not a good match due to lack of specific tech experience"
- "Match level too high - position requires 5+ years experience in hedge funds"
- "Good match incorrectly classified as low"

### Prompt Management System

The project already has a prompt management system in `run_pipeline/utils/prompt_manager.py`. This system:
- Stores prompts with versioning
- Tracks the active version for each prompt type
- Allows retrieving and updating prompts

Job matching prompts are now stored in text files in the `prompts/job_matching/v1/` directory, with the first version being `llama3_cv_match.txt`. This approach provides several benefits:
- Prompts are no longer hardcoded in scripts
- Multiple prompt versions can be maintained simultaneously
- Changes to prompts can be tracked and versioned
- Prompts can be updated automatically based on feedback

### Feedback Processing System

The feedback processing system consists of the following components:

1. **Feedback Handler Module** (`job_matcher/feedback_handler.py`):
   - Saves feedback data to the file system
   - Analyzes feedback using LLM to identify patterns
   - Generates recommendations for prompt improvements
   - Optionally updates prompts based on feedback

2. **Feedback Integration in Job Processor** (`job_matcher/job_processor.py`):
   - Added `process_feedback` function to handle user feedback
   - Integrates with the feedback handler module

3. **CLI Support for Feedback** (`job_matcher/cli.py`):
   - Added command-line options for processing feedback
   - Added support for automatic prompt updates based on feedback

4. **Integrated Feedback Test** (`test_integrated_feedback.py`):
   - Tests the complete feedback loop in one script
   - Verifies that feedback is processed correctly
   - Optionally tests that prompt updates improve results

## Code Refactoring

The original `test_llama32.py` script (700+ lines) has been refactored into a more maintainable and modular structure:

- `job_matcher/` package:
  - `__init__.py`: Package definition
  - `llm_client.py`: Client for interacting with LLM API
  - `response_parser.py`: Tools for parsing LLM responses
  - `domain_analyzer.py`: Functions for job domain analysis 
  - `job_processor.py`: Core logic for processing jobs
  - `cv_utils.py`: Utilities for CV data
  - `default_prompt.py`: Default prompt as fallback
  - `cli.py`: Command line interface functions
  - `feedback_handler.py`: Feedback processing and analysis

- `test_llama32_new.py`: Backward-compatible wrapper script

This modular structure makes the code more maintainable, testable, and easier to extend with new features like the feedback system.

## Using the Feedback System

### Manual Feedback Collection

1. Run job matching to generate job matches
2. Export job matches to Excel using `export_job_matches.py`
3. Review matches and add feedback in the 'Feedback' column
4. Process feedback using `process_feedback.py`

### Command-Line Feedback Processing

Process feedback for a specific job using the command line:

```bash
python test_llama32_new.py --job-ids 61691 --feedback --feedback-text "This match should be Moderate instead of Low due to relevant experience"
```

To automatically update prompts based on feedback:

```bash
python test_llama32_new.py --job-ids 61691 --feedback --feedback-text "This match should be Moderate instead of Low due to relevant experience" --auto-update
```

### Testing the Feedback Loop

Run an integrated test of the feedback loop:

```bash
python test_integrated_feedback.py --job-id 61691 --feedback "The match level should be Good instead of Moderate because the CV shows experience in all required domain-specific areas" --auto-update
```

## Implementation Status

- ✅ Export with Feedback Column
- ✅ Prompt Management System 
- ✅ Refactored codebase into modules
- ✅ Feedback Handler Module
- ✅ CLI Support for Feedback
- ✅ Integrated Feedback Test
- ✅ Documentation Update
