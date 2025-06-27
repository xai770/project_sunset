# 👑 Royal Archives Index
**Sandy's Organized Project Archive**

Welcome to the royal archives! This directory contains all the tools, scripts, and documentation that support the Sandy job analysis pipeline but aren't needed for daily operations.

## 📁 Directory Structure

### 🔧 `development_tools/`
**Infrastructure and Development Configuration**
- `mypy.ini`, `pyrightconfig.json`, `setup.cfg` - Code quality and type checking
- `requirements-pipeline.txt` - Python dependencies
- `bash_history` - Development command history

### 📊 `analysis_scripts/`
**Analysis and Utility Scripts**
- `check_excel_content.py` - Excel report validation
- `clear_job_cache.py` - Cache management
- `create_comprehensive_excel_report.py` - Legacy comprehensive reporting
- `create_content_extraction_validation_excel.py` - Content extraction validation
- `daily_consciousness_report_generator.py` - Legacy report generator (pre-cleanup)
- `debug_job_structure.py` - Job data structure debugging
- `domain_classification_debug.py` - Domain classification debugging
- `fixed_enhanced_analysis.py` - Enhanced analysis scripts
- `quick_enhanced_analysis.py` - Quick analysis tools
- `quick_specialist_health_check.py` - Specialist performance validation

### 🧪 `test_validation/`
**Testing and Validation Scripts**
- `test_*.py` - Unit and integration tests
- `golden_test_validation.py` - Golden standard validation
- `validate_location_specialist_full_dataset.py` - Full dataset validation

### 📚 `project_documentation/`
**Project Management and Documentation**
- `PROJECT_SUNSET_LLM_INTEGRATION_SUCCESS_REPORT.md` - Project milestone reports
- `PROJECT_WORKLIST.md` - Project task management
- `WORKSPACE_ORGANIZATION_COMPLETE.md` - Organization completion records

## 🎯 Daily Operations (Root Directory)
The main project directory contains only what's needed for daily operations:
- `daily_report_generator.py` - **Main production script**
- `README.md` - Project overview
- `force_reprocess_jobs.py` - Job reprocessing utility
- `location_validation_integration.py` & `location_validation_specialist_llm.py` - Core specialists
- Core directories: `config/`, `core/`, `data/`, `reports/`, `0_mailboxes/`

---
*Archive organized by Sandy, Queen of the Codebase* 👑
