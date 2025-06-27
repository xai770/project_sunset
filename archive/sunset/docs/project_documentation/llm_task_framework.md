### LLM Task Optimization Framework

This document provides an overview of the framework for optimizing LLM model selection and prompt engineering for different tasks in Project Sunset.

## Framework Components

1. **Task Optimizer** - Finds the best LLM and prompt for a specific task
2. **Task Configuration System** - Manages optimal configurations for all tasks
3. **Integration Utilities** - Tools to apply configurations to workflows

## Getting Started

### Step 1: Set Up Task Samples

Create a directory with sample input files for your task:

```bash
mkdir -p data/task_samples/skill_matching
```

You can use the built-in sample creation utility:

```bash
./scripts/llm_optimization/optimize_task.sh skill_matching --create-samples
```

### Step 2: Run Task Optimization

Run the task optimizer to find the best LLM and prompt combination:

```bash
./scripts/llm_optimization/optimize_task.sh skill_matching --models "llama3.2:latest,phi3:latest,gemma3:1b"
```

The optimization will:
1. Test all combinations of models and prompt templates
2. Evaluate each combination based on success rate, format adherence, and speed
3. Generate detailed reports and visualizations
4. Register the optimal configuration in the task registry

### Step 3: Use the Optimal Configuration

In your Python code, use the task configuration system:

```python
from scripts.llm_optimization.task_configuration import run_with_task_config

# Process content using optimal configuration
result = run_with_task_config(content, "skill_matching")
```

## Command Line Utilities

### Task Optimizer

```bash
./scripts/llm_optimization/optimize_task.sh [task_name] [options]
```

Options:
- `--models MODEL1,MODEL2,...` - Comma-separated list of models to test
- `--samples-dir DIR` - Directory with samples for the task
- `--create-samples` - Create sample templates if directory is empty

### Task Configuration Manager

```bash
./scripts/llm_optimization/task_config.sh [command] [args]
```

Commands:
- `list` - List all configured tasks
- `get [task_name]` - Get configuration for a task
- `apply [results_dir] [task]` - Apply test results to task registry
- `set [task] [model] [prompt]` - Manually set task configuration
- `test [task] [input_file]` - Test task with current configuration

## Extending the Framework

### Adding New Tasks

1. Add a task definition in `task_optimizer.py` and `task_configuration.py`:

```python
TASK_DEFINITIONS = {
    # ... existing tasks ...
    "new_task_name": {
        "task_description": "new task description",
        "task_instruction": "Instructions for the task",
        "domain_expert": "relevant domain expert",
        "domain_name": "domain name",
        "task_context": "context of the task",
        "format_spec": """Expected format:
- Item 1
- Item 2"""
    }
}
```

2. Create samples in `data/task_samples/new_task_name/`
3. Run optimization: `./scripts/llm_optimization/optimize_task.sh new_task_name`

### Adding New Prompt Templates

Add a new prompt template in `task_optimizer.py` and `task_configuration.py`:

```python
DEFAULT_PROMPT_VARIATIONS = {
    # ... existing templates ...
    "new_template": {
        "name": "Template Name",
        "description": "Template description",
        "template": """Your template with {task_description} and other variables

{content}"""
    }
}
```

### Adding New Evaluation Metrics

Extend the `evaluate_results()` function in `task_optimizer.py` with task-specific evaluation metrics.
