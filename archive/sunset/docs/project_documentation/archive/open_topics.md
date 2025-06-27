# Project Sunset - Open Topics

This document tracks features, improvements, bug fixes, and other work items for Project Sunset.

## Status Legend
- 💡 **Idea** - Initial concept, not yet discussed in detail
- 🔍 **Under Discussion** - Being evaluated for feasibility and priority
- 🚧 **In Progress** - Currently being implemented
- ✅ **Implemented** - Implementation complete
- 🧪 **Testing** - Implementation complete, undergoing testing
- ✔️ **Complete** - Fully implemented and tested
- ❌ **Rejected** - Decided not to pursue this item

## Core System Improvements

| Item | Description | Status | Notes |
|------|-------------|--------|-------|
| Consolidated Configuration | Create a central configuration mechanism so paths, thresholds, and other settings are in one place | 💡 | Currently config is scattered across multiple files |
| Error Recovery Mechanisms | Implement automated recovery procedures for the error conditions | 🔍 | Need to define standard error handling protocols |
| Process CV Project Summary | Update CV inference module to analyze Project Summary markdown file | 🚧 | Work started May 4, 2025 |
| Historical Analytics | Add a component to analyze which skills are most valuable based on successful applications | 💡 | Could help prioritize skill development |
| Standardize Job Data Format | Ensure all job data follows a consistent structure with a single job{id}.json file per job | 🚧 | First phase implemented May 4, 2025 - Updated self-assessment module |
| Add DATA FLOW Documentation | Add standardized DATA FLOW documentation section to all scripts | 🚧 | First phase implemented May 4, 2025 - Updated self-assessment module and process_job.py |
| Remove Compatibility Layers | Remove legacy compatibility code for separate decomposition files | 🚧 | First phase implemented May 4, 2025 - Updated self-assessment module |
| Add Script Operation Logs | Add logging section to job JSONs to track script actions with timestamps | 🚧 | First phase implemented May 4, 2025 - Updated self-assessment module and process_job.py |

## Unified Job Data Standard Implementation

| Script/Module | DATA FLOW Added | Remove Compatibility | Add Logging | Tested | Notes |
|---------------|----------------|---------------------|------------|-------|-------|
| process_job.py | ✅ | ✅ | ✅ | 🚧 | Main coordinator script updated |
| self_assessment/__init__.py | ✅ | ✅ | ✅ | 🚧 | Updated to use consolidated files only |
| self_assessment/data_loader.py | ✅ | ✅ | ✅ | 🚧 | Simplified to work with consolidated files |
| self_assessment/utils.py | ✅ | ✅ | ✅ | 🚧 | Removed legacy path references |
| self_assessment/generator.py | ✅ | ✅ | ✅ | 🚧 | Added proper logging metadata |
| skill_decomposer/decomposition.py | 🚧 | 🚧 | 🚧 | ❌ | Pending implementation |
| skill_decomposer/matching.py | 🚧 | 🚧 | 🚧 | ❌ | Pending implementation |
| doc_generator/*.py | 🚧 | 🚧 | 🚧 | ❌ | Pending implementation |

## New Features

| Feature | Description | Status | Notes |
|---------|-------------|--------|-------|
| Application Status Dashboard | Build a simple dashboard to visualize application statuses | 💡 | Would provide better overview of application pipeline |
| Resume Tailoring | Add component to tailor CV for specific job applications | 💡 | Similar to how cover letters are customized |
| Mock Interview Preparation | Generate potential interview questions based on job requirements and skill gaps | 💡 | For high-match jobs |
| Job Requirement Trend Analysis | Analyze trends in job requirements over time | 💡 | Help identify emerging skills to develop |
| Email Notification System | Send notifications for new matching jobs | 💡 | Reduce manual checking |

## Documentation Improvements

| Item | Description | Status | Notes |
|------|-------------|--------|-------|
| System Data Flow Documentation | Add detailed data flow comments to code files | 🚧 | Several key files already updated |
| System Data Flow Diagrams | Create Mermaid diagrams showing data flow | ✅ | Created in docs/system_data_flow.md and resources/system_data_flow.md |
| User Guide | Create comprehensive user guide for all system components | 🔍 | Should include setup guide and usage instructions |
| Code Style Guide | Define consistent code style and documentation standards | 💡 | Would help with maintainability |

## Testing & Quality Assurance

| Item | Description | Status | Notes |
|------|-------------|--------|-------|
| Automated Testing | Expand automated tests for LLM-based components | 🔍 | Need to determine best approach for testing LLMs |
| Test Coverage Analysis | Measure and improve test coverage | 💡 | Currently testing is ad-hoc |
| Integration Tests | Create end-to-end tests for full workflow | 💡 | Test complete job pipeline |
| Performance Benchmarks | Establish performance metrics and benchmarks | 💡 | Track system performance over time |

## Technical Debt

| Item | Description | Status | Notes |
|------|-------------|--------|-------|
| Code Duplication | Remove duplicate code across modules | 🔍 | Several utility functions appear in multiple places |
| Deprecate Legacy File Structure | Move fully to consolidated job files | 🚧 | First phase implemented May 4, 2025 - self-assessment module now uses only consolidated files |
| Update Dependencies | Review and update external dependencies | 💡 | Some libraries may have newer versions |
| Refactor Error Handling | Implement consistent error handling | 💡 | Currently varies between modules |

## Infrastructure

| Item | Description | Status | Notes |
|------|-------------|--------|-------|
| Backup System | Implement automated backup for all data | 🔍 | Currently manual backups only |
| Logging Consolidation | Standardize logging across all components | 🚧 | Started implementing in self-assessment module |
| Deployment Process | Document deployment process for system updates | 💡 | Currently ad-hoc updates |

*Last updated: May 4, 2025*