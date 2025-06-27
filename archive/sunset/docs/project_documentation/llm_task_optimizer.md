# LLM Task Optimizer for Job Self-Assessment System

## Project Overview

The LLM Task Optimizer system enhances the job self-assessment pipeline by automatically selecting the optimal language model for different task types based on performance metrics and quality assessments. This document summarizes the implementation, features, and future directions of this enhancement.

## Key Features

### 1. Task-Specific Model Ranking

The system maintains performance rankings of different LLMs for various task types, including:
- Self-assessment narrative generation
- Skill decomposition
- Domain relationship analysis
- Cover letter generation
- Job requirements extraction
- Job detail extraction (with consensus verification)

Each task type has configurable priority weights for quality vs. speed, allowing the system to balance these factors appropriately for each use case.

### 2. Intelligent Model Selection

The task optimizer automatically:
- Identifies available models from the Ollama service
- Evaluates models based on weighted quality and speed scores
- Selects the optimal model for each task type

This capability is exposed through a simple `--best-model` flag in tools like `rerun_self_assessment.py`, making it easy to leverage the optimal model without manual selection.

### 3. Performance Metrics Collection

The system includes a comprehensive feedback collection mechanism that:
- Records execution time, success rate, and quality metrics for all model usages
- Maintains a historical performance database in `config/model_performance_feedback.json`
- Provides insights into model performance across different tasks

### 4. Consensus-Based Verification

For critical tasks like job detail extraction, the system employs a consensus approach:
- Multiple models process the same input independently
- Results are compared using similarity metrics
- If two models reach consensus (similarity ≥75%), their output is considered reliable
- If the first two models disagree, a third model breaks the tie
- This approach significantly improves output reliability

The consensus verification system is implemented in `scripts/llm_optimization/consensus_job_extractor.py` and works as follows:
1. The top 2-3 ranked models for job detail extraction are selected
2. Each model independently extracts the key details from the job posting
3. The system calculates similarity between extractions using difflib's SequenceMatcher
4. If any two models agree (similarity ≥75%), their output is considered valid
5. If no consensus is reached, it falls back to the highest-ranked model's output
6. Performance metrics are recorded to continuously improve model selection

### 5. Quality Assessment Framework

A sophisticated quality assessment module evaluates model outputs by:
- Analyzing content structure, length, and complexity 
- Applying task-specific quality criteria (e.g., skill mentions for self-assessments)
- Computing normalized quality scores that feed back into the ranking system

### 6. Automatic Ranking Updates

The system continuously improves through:
- Automated ranking updates based on real-world performance data
- Detection and integration of new models as they become available
- Scheduled updates through a configurable cron job

### 7. Benchmarking Tools

Comprehensive benchmarking tools allow for:
- Systematic testing of all models across all task types
- Parallel benchmarking for efficient evaluation
- Detailed performance reports to guide model selection
- Testing of job detail extraction with various real job postings

## Implementation

### Core Components

1. **LLM Task Optimizer (`scripts/utils/llm_task_optimizer.py`)**
   - Defines task types and their quality/speed priorities
   - Maintains and loads model rankings
   - Selects the best model for each task

2. **Model Feedback System (`scripts/utils/model_feedback.py`)**
   - Records model performance metrics
   - Updates rankings based on collected data

3. **Quality Assessment (`scripts/utils/quality_assessment.py`)**
   - Evaluates output quality using task-specific criteria
   - Computes normalized quality scores

4. **Consensus Verification (`scripts/llm_optimization/consensus_job_extractor.py`)**
   - Implements multi-model consensus for critical tasks
   - Ensures higher reliability through agreement verification
   - Falls back gracefully when consensus cannot be reached

5. **Automation Scripts**
   - `auto_update_rankings.py` - Scheduled ranking updates
   - `benchmark_models.py` - Comprehensive model evaluation
   - `setup_auto_rankings.sh` - Configures automated updates

### Configuration Files

1. **Model Rankings (`config/model_rankings.json`)**
   - Contains ranked models for each task type
   - Stores quality and speed scores for each model

2. **Performance Feedback (`config/model_performance_feedback.json`)**
   - Tracks execution metrics for model-task combinations
   - Records success rates and execution times

## Usage Examples

### Using the Best Model for Self-Assessment

```bash
python rerun_self_assessment.py --best-model
```

### Viewing Current Model Rankings

```bash
python rerun_self_assessment.py --list-rankings
```

### Running Comprehensive Model Benchmarks

```bash
python scripts/llm_optimization/benchmark_models.py
```

### Testing Specific Models on Specific Tasks

```bash
python scripts/llm_optimization/benchmark_models.py --models gemma3:1b,llama3.2:latest --tasks self_assessment,skill_decomposition
```

### Using Consensus-Based Job Detail Extraction

```bash
python scripts/llm_optimization/consensus_job_extractor.py 62914
```

### Setting Up Automated Ranking Updates

```bash
./scripts/bin/setup_auto_rankings.sh
```

## Performance Results

Initial benchmarks have shown that:

- `gemma3:1b` performs best for self-assessment tasks, offering an excellent balance of quality (0.90) and speed (0.85)
- For skill decomposition, `llama3.2:latest` and `phi3:3.8b` excel in different scenarios, with the former being faster and the latter producing higher quality outputs
- Domain relationship tasks benefit most from larger models like `phi3:3.8b` due to their complex reasoning requirements
- Smaller models are generally preferred for tasks where speed is critical and quality requirements are more moderate
- For job detail extraction, consensus verification between `phi3:3.8b` and `gemma3:1b` achieves the highest reliability

## Future Enhancements

1. **Meta-Model Quality Assessment**
   - Using a separate LLM to evaluate the quality of outputs from task models
   - Implementing comparative rankings through A/B testing of outputs

2. **Multi-Model Ensemble Approach**
   - Extending consensus verification to more task types
   - Implementing weighted voting mechanisms for highest quality
   - Creating ensemble approaches that combine strengths of multiple models

3. **Adaptive Learning System**
   - Dynamically adjusting task priorities based on user feedback
   - Implementing reinforcement learning from human preferences
   - Fine-tuning optimization parameters based on historical performance

4. **Integration with Additional Tasks**
   - Expanding the system to cover more components of the job application process
   - Creating specialized model rankings for sub-tasks within major categories
   - Developing pipelines for complex multi-step workflows

## Conclusion

The LLM Task Optimizer system represents a significant enhancement to the job self-assessment pipeline by automatically selecting the best model for each task. By collecting performance metrics and continuously updating rankings, the system ensures optimal performance while adapting to new models as they become available.

This framework provides both immediate performance improvements and a foundation for future enhancements as LLM technology continues to evolve.
