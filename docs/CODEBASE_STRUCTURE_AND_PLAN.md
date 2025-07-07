# Codebase Structure Analysis and Forward Plan

## Current Structure Overview

### 1. Active Core Components

#### 1.1 `daily_report_pipeline/`
This is our main active pipeline where all the current development is happening. It contains:
- Specialists (like our CV matching specialist)
- Data models
- Core pipeline logic
- Modern, modular structure with clear separation of concerns

#### 1.2 `core/`
Contains essential infrastructure that supports the pipeline:
- Configuration management
- Job matching API
- Specialist types and management
- State management
- Status tracking

### 2. Legacy/Transition Components

#### 2.1 `monitoring/`
STATUS: Should be evaluated and potentially integrated
- Contains monitoring tools that were part of the old system
- Some functionality might be worth preserving
- Plan: Evaluate monitoring needs and either:
  a) Integrate useful parts into daily_report_pipeline
  b) Create a new monitoring module with modern architecture

#### 2.2 `run_pipeline/`
STATUS: Deprecated, should be archived
- Contains old pipeline implementation
- Has been superseded by daily_report_pipeline
- Any useful components have already been migrated
- Plan: Move to _legacy_archive after final verification

### 3. Supporting Directories

#### 3.1 Active and Needed
- `config/` - Configuration files and credentials
- `resources/` - Static resources including CV files
- `docs/` - Project documentation
- `scripts/` - Utility scripts and tools

#### 3.2 To Be Evaluated
- `archives/` - Old scripts that need review
- `development_tools/` - Development utilities that might still be useful
- `testing/` - Test files that need to be updated for new architecture

## Forward Plan

### 1. Immediate Actions
1. Create a new monitoring strategy:
   - Review current monitoring code
   - Identify essential metrics and alerts
   - Design a new monitoring system that integrates with daily_report_pipeline
   - Implement monitoring as a specialist component if appropriate

2. Archive run_pipeline:
   - Final review of run_pipeline components
   - Move to _legacy_archive
   - Update any remaining imports or references
   - Remove from active development

### 2. Near-term Tasks
1. Consolidate utility functions:
   - Review functions in development_tools
   - Move useful utilities to core/
   - Archive or remove unused tools

2. Update test infrastructure:
   - Move tests alongside their components
   - Update test framework to match new architecture
   - Implement missing tests for new components

### 3. Long-term Goals
1. Complete modularization:
   - All functionality should be specialist-based
   - Clear interfaces between components
   - Well-defined data models

2. Improve monitoring and observability:
   - Real-time pipeline status
   - Performance metrics
   - Error tracking and alerts

3. Documentation and maintenance:
   - Complete API documentation
   - Update architecture diagrams
   - Regular cleanup of archived code

## Directory Structure Vision

```
sandy/
├── daily_report_pipeline/    # Main active codebase
│   ├── specialists/         # Individual specialists
│   ├── models/             # Data models
│   └── core/              # Core pipeline logic
├── core/                   # Shared infrastructure
├── config/                 # Configuration files
├── resources/              # Static resources
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── _legacy_archive/        # Archived code
    └── run_pipeline/      # Old pipeline implementation
```

## Next Steps

1. Create tasks for monitoring evaluation and integration
2. Set up archival process for run_pipeline
3. Review and consolidate utility functions
4. Update test infrastructure
5. Document any remaining technical debt

This plan will help us maintain a clean, modular, and maintainable codebase while preserving useful functionality from the older components.
