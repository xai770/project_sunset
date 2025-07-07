# Codebase Structure Analysis and Forward Plan

## Current Structure Overview

### 1. Active Core Components

#### 1.1 `daily_report_pipeline/`
This is our main active pipeline where all the current development is happening. It contains:
- Specialists (like our CV matching specialist and monitoring specialists)
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

### 2. Completed Actions ✅

1. Monitoring Integration:
   - Created PerformanceMonitoringSpecialist
   - Created LLMPerformanceSpecialist
   - Added comprehensive monitoring data models
   - Added monitoring evaluation documentation

2. Run Pipeline Migration:
   - Moved to _legacy_archive
   - Preserved git history
   - Updated documentation
   - Removed from active development

3. Development Infrastructure:
   - Organized development tools in development_tools/
   - Consolidated test files in testing/
   - Removed duplicate files
   - Cleaned up root directory

### 3. Supporting Directories

#### 3.1 Active and Needed
- `config/` - Configuration files and credentials
- `resources/` - Static resources including CV files
- `docs/` - Project documentation
- `scripts/` - Utility scripts and tools
- `development_tools/` - Development utilities
- `testing/` - Test infrastructure

#### 3.2 Archived
- `_legacy_archive/` - Contains archived code including old run_pipeline

## Remaining Tasks

1. Test Infrastructure Updates:
   - Create test plan for each specialist
   - Add integration tests
   - Set up CI/CD pipeline

2. Documentation Updates:
   - Add API documentation
   - Create specialist usage guides
   - Update architecture diagrams

3. Final Cleanup:
   - Review remaining utility functions
   - Document any technical debt
   - Plan regular maintenance schedule

## Directory Structure (Current)

```
sandy/
├── daily_report_pipeline/    # Main active codebase
│   ├── specialists/         # Individual specialists
│   │   ├── cv_matching/    # CV matching specialist
│   │   └── monitoring/     # Monitoring specialists
│   ├── models/             # Data models
│   └── core/              # Core pipeline logic
├── core/                   # Shared infrastructure
├── config/                 # Configuration files
├── resources/              # Static resources
├── docs/                   # Documentation
├── development_tools/      # Development utilities
├── testing/               # Test infrastructure
└── _legacy_archive/        # Archived code
    └── run_pipeline/      # Old pipeline implementation
```

This plan has helped us achieve a clean, modular, and maintainable codebase. We've successfully:
1. ✅ Integrated monitoring as specialists
2. ✅ Archived deprecated code
3. ✅ Organized development tools
4. ✅ Consolidated test files

Moving forward, we'll focus on improving test coverage, documentation, and maintaining the modular architecture.
