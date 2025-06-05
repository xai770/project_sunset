# TLM Framework Code Organization

## Structure and Organization

The Task-centric LLM Management (TLM) framework is organized with all core components located in the `scripts/tlm/` directory. This is the official location for all TLM-related code.

### Key Components

- `scripts/tlm/task_executor.py` - The main TaskExecutor class implementation
- `scripts/tlm/models.py` - Model selection and management
- `scripts/tlm/template_engine.py` - Template rendering for prompts
- `scripts/tlm/validation.py` - Input/output validation utilities
- `scripts/tlm/verification/` - Output verification methods
- `scripts/tlm/execution_logger.py` - Execution logging functionality
- `scripts/tlm/task_migration.py` - Utilities to migrate legacy code to TLM

### Task Definitions

Task definitions are stored as JSON files in the `config/task_definitions/` directory. These files define:

- Task inputs and outputs with JSON schemas
- Example inputs and outputs for testing
- Prompt templates with variable placeholders
- Verification methods and parameters
- Model selection criteria

### Execution Logs

Task execution logs are stored in the `data/task_executions/` directory, organized by task ID and timestamp.

## Avoiding Code Duplication

To maintain a clean and maintainable codebase, we should avoid duplicate implementations of the same functionality. In particular:

1. **Keep TLM code in one place**: All TLM-related code should be in `scripts/tlm/` directory
2. **Avoid duplicate class names**: Don't create classes with the same name in different directories
3. **Use proper imports**: When importing TLM components, use the full path (`from scripts.tlm.X import Y`)

## Migration Strategy

When migrating existing code to use the TLM framework:

1. Use the migration utilities in `scripts/tlm/task_migration.py`
2. Create appropriate task definition files in `config/task_definitions/`
3. Update imports to reference the official TLM components in `scripts/tlm/`
4. Run integration tests to validate the migration

## Testing

The TLM framework can be tested using:

1. Unit tests for individual components
2. Integration tests that verify components work together correctly
3. The CLI tool (`scripts/tlm/tlm_cli.py`) for manual testing of task execution

All tests should import from the official `scripts.tlm` module path.
