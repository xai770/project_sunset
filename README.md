# Project Sunset

A comprehensive workspace for managing job applications, document automation, and related resources.

## Project Overview (As of May 25, 2025)

### Purpose
Project Sunset is a comprehensive system for automating job application processes, particularly focused on Deutsche Bank careers. The project handles job scraping, skill analysis, document generation (cover letters), and job application management.

### Core Components

#### 1. Career Pipeline
The central workflow component handling the extraction, processing and analysis of job postings.

- **New Modular Pipeline (`run_pipeline/`)**: A complete modular reimplementation of the job expansion workflow with the following key components:
  - **Pipeline Orchestration**:
    - Main orchestrator (`run_pipeline/core/pipeline_orchestrator.py`): Coordinates all pipeline steps
    - Job Scanner (`run_pipeline/core/job_scanner.py`): Discovers new or missing jobs
    - Job Matcher (`run_pipeline/core/job_matcher.py`): Matches CV to jobs using LLM
    - Feedback Loop (`run_pipeline/core/feedback_loop.py`): Handles Excel export, cover letters, email
    - Test Integration (`run_pipeline/core/test_integration.py`): Testing utilities
  - **LLM Factory Integration**:
    - Ada Integration (`run_pipeline/ada_llm_factory_integration.py`): Integrates LLM Factory specialists
    - Type Stubs (`run_pipeline/llm_factory_stubs.py`): Type definitions for LLM Factory components
    - Cover Letter Generator V2 integration with proper type checking
  - Job Metadata Fetcher (`run_pipeline/core/fetch_module.py`): Retrieves job listings from the Deutsche Bank careers API
  - Job Details Scraper (`run_pipeline/core/scraper_module.py`): Extracts detailed job descriptions using Firefox
  - Job Description Cleaner (`run_pipeline/core/cleaner_module.py`): Generates concise job descriptions using the staged job processor
  - Staged Job Description Processor (`run_pipeline/utils/staged_job_description_processor.py`): Advanced multi-stage processing with language handling
  - Job Description Updater (`run_pipeline/utils/update_job_descriptions.py`): Utility for maintaining job descriptions
  - Utility modules for logging, process execution, and Firefox management
- **Original Pipeline Components**:
  - Orchestrator (`scripts/career_pipeline/orchestrator.py`): Original coordination module
  - Job Fetcher (`scripts/career_pipeline/job_fetcher.py`): Original job listing retrieval
  - Job Extractors:
    - Legacy extractor (`scripts/career_pipeline/job_detail_extractor.py`) 
    - TLM-powered extractor (`scripts/career_pipeline/tlm_job_extractor.py`)
- **Job Processor (`scripts/career_pipeline/job_processor/`)**: Processes and enriches job data
- **Document Generation**:
  - Cover letter generation (`scripts/career_pipeline/generate_cover_letter.py`)

#### 2. Job Matching System with Feedback Loop
The job matching system analyzes job descriptions against CV data to determine match levels and provide application guidance.

- **Job Matcher Package** (`job_matcher/`): A refactored, modular implementation:
  - LLM Client (`llm_client.py`): Handles API calls to the LLM service
  - Response Parser (`response_parser.py`): Extracts structured data from LLM responses
  - Domain Analyzer (`domain_analyzer.py`): Analyzes job domain requirements
  - Job Processor (`job_processor.py`): Main processing logic
  - CV Utilities (`cv_utils.py`): Handles CV-related operations
  - Prompt Adapter (`prompt_adapter.py`): Manages prompt access and formatting
  - CLI Interface (`cli.py`): Command-line interface
  - Feedback Handler (`feedback_handler.py`): Processes user feedback to improve matching accuracy

- **Feedback Loop System**:
  - Excel Export with Feedback Column (`export_job_matches.py`)
  - Feedback Storage and Analysis (`process_feedback.py`, `job_matcher/feedback_handler.py`)
  - Prompt Management System (`run_pipeline/utils/prompt_manager.py`)
  - Integrated Testing (`test_integrated_feedback.py`, `test_feedback_system.py`)

#### 3. Task-centric LLM Management (TLM) Framework
A sophisticated system for managing LLM-based tasks with verification and validation:

- **Core Components**:
  - Task Executor (`scripts/tlm/task_executor.py`): Executes task definitions using LLMs
  - Model Selection (`scripts/tlm/models.py`): Selects optimal models for specific tasks
  - Task Migration (`scripts/tlm/task_migration.py`): Migration tool for converting legacy code to TLM
  - Concise Job Description Extractor (`scripts/test_concise_extraction.py`): Transforms verbose job postings into concise, structured summaries with 90-94% text reduction while preserving all essential information
  - Multi-Model Testing Framework (`scripts/test_concise_extraction_all_models.sh`): Automatically tests extraction quality across all available LLM models
  - Optimal Model Selector (`scripts/optimal_model_selector.py`): Dynamically selects the best-performing model for each task based on test results
- **Task Definitions**:
  - Job detail extraction (`config/task_definitions/job_detail_extraction.json`)
  - Skill decomposition (`config/task_definitions/skill_decomposition.json`)
  - Self-assessment (`config/task_definitions/self_assessment_generation.json`)

#### 4. Skill Analysis System
Components for analyzing job requirements and matching them to candidate skills:

- **Skill Decomposition (`scripts/utils/skill_decomposer/`)**: Breaks down complex skills into elementary components
- **Matching (`scripts/utils/skill_decomposer/matching.py`)**: Matches candidate skills against job requirements
- **Skill Data**:
  - Technical skills (`skills/technical_skills.json`)
  - Soft skills (`skills/soft_skills.json`)
  - Elementary skills (`skills/elementary_skills.json`)
  - Various caching files for skill relationships and decompositions

#### 5. Utilities and Support Systems
- **Anti-Scraping** (`scripts/career_pipeline/utils/anti_scraping.py`): Helps avoid detection during web scraping
- **Browser Automation** (`scripts/career_pipeline/utils/browser_automation.py`): For scraping browser-rendered content
- **LLM Task Optimization** (`scripts/llm_optimization/`): Tools for selecting optimal LLM models for specific tasks

### Data Flow Architecture

1. **Job Data Collection**:
   - Job listings are scraped from Deutsche Bank careers API
   - Full job details are extracted from individual job pages
   - Anti-scraping measures are employed to avoid detection

2. **Job Processing and Analysis**:
   - Job data is processed, cleaned, and structured
   - TLM framework extracts key details like job title, responsibilities, and requirements
   - Skill decomposer analyzes requirements and matches them against candidate skills

3. **Document Generation**:
   - Cover letters are generated based on job requirements and candidate skills
   - Documents are converted from Markdown to Word format
   - Reports are generated showing skill matches and application status

4. **Application Automation**:
   - Email automation for sending applications

### Areas for Potential Restructuring

1. **Complete TLM Migration**: Finish migrating all LLM-dependent tasks to the TLM framework
2. **Modularization**: Reorganize some of the tightly coupled components in the career pipeline
3. **Configuration Management**: Consolidate configuration files and improve dependency injection
4. **Testing Strategy**: Enhance end-to-end testing coverage, particularly for the TLM framework
5. **Documentation**: Improve inline documentation and add architecture diagrams

## Directory Structure

```
sunset/
├── README.md                     # This file
├── credentials.json              # Google API credentials
├── token.pickle                  # Authentication token
│
├── scripts/                      # All automation scripts
│   ├── job_scraper/              # Job scraping scripts
│   ├── doc_generator/            # Document generation scripts
│   ├── email_sender/             # Email automation scripts
│   └── utils/                    # Utility scripts
│       └── skill_decomposer/     # Skill decomposition module
│
├── templates/                    # Templates for document generation
│   └── cover_letter_template.md  # Cover letter template
│
├── data/                         # Raw data collected
│   ├── postings/             # Raw job postings data
│   ├── job_decompositions/       # Decomposed job requirements
│   └── logs/                     # Log files
│
├── docs/                         # Generated documents
│   ├── cover_letters/            # Generated cover letters (MD and DOCX)
│   ├── job_descriptions/         # Job description documents
│   └── match_reports/            # Skill match reports and visualizations
│
├── profile/                      # Profile information
│   ├── cv/                       # CV documents
│   └── models/                   # Skill models and data
│
├── tests/                        # Test scripts and files
│   ├── test_skill_core.py        # Tests for skill_decomposer core module
│   ├── test_skill_decomposer.py  # Tests for skill_decomposer compatibility
│   └── test_skill_integration.py # Integration tests for skill_decomposer
│
└── resources/                    # Support materials
    ├── financial/                # Financial baseline information
    ├── legal/                    # Legal documentation
    └── network/                  # Network configurations
```

## Recent Improvements (May 2025)

### Cover Letter Generation Enhancement
- ✅ Integrated match recommendations into cover letter generation
  - Cover letters now automatically highlight strongest skills for each job
  - Qualification paragraphs dynamically generated from self-assessment
  - Development areas professionally addressed in a dedicated paragraph
  - Smart default values generated based on job type

### Consistent Skill Match Reporting  
- ✅ Fixed inconsistency in summary reporting of matched requirements
  - Created new skill match report generator (`skill_match_report.py`)
  - Reports include overall score, strong/moderate matches and development areas
  - Reports saved to `/data/reports/` directory for reference
  - Format is consistent across all job applications

### Future Enhancements
- ⏳ Improve visualization of skill matches with interactive features
  - Not implemented yet - will be considered for future development when needed
  - Would provide interactive graphs/charts showing skill match distributions
  - Would allow for filtering and sorting of matches

## Workflow

1. **Job Scraping**: Scripts in `scripts/job_scraper/` scrape job postings and save them to `data/postings/`
2. **Document Generation**: 
   - Cover letters are generated using `scripts/doc_generator/generate_cover_letter.py`
   - These are saved to `docs/cover_letters/` in Markdown format
   - Converted to Word using `scripts/doc_generator/md_to_word_converter.py`
3. **Email Sending**: Documents are sent using `scripts/email_sender/email_sender.py`

## Key Scripts

### Job Scraping
- `scripts/job_scraper/cli.py` - Main entry point for job scraping
- `scripts/job_scraper/scraper.py` - Core scraping logic
- `scripts/job_scraper/job_processor.py` - Processes scraped jobs

### Document Generation
- `scripts/doc_generator/generate_cover_letter.py` - Creates cover letters from templates
- `scripts/doc_generator/md_to_word_converter.py` - Converts MD to DOCX
- `scripts/doc_generator/json_to_word.py` - Converts job JSON to DOCX

### Email Automation
- `scripts/email_sender/email_sender.py` - Sends generated documents via email

### Skill Decomposition
- `scripts/utils/skill_decomposer/` - Module for decomposing complex skills into elementary components
- `scripts/utils/skill_decomposer/cli.py` - Command-line interface for the skill decomposer
- `scripts/utils/skill_decomposer/matching.py` - Matches job requirements against user skills
- `scripts/utils/skill_decomposer/decomposition.py` - Decomposes skills and job requirements
- `scripts/utils/skill_decomposer/visualization.py` - Generates visual reports of skill matches

### Job Matching with Feedback Loop
- `job_matcher/llm_client.py` - LLM API client for job matching
- `job_matcher/response_parser.py` - Parses LLM responses
- `job_matcher/domain_analyzer.py` - Analyzes job domain requirements
- `job_matcher/job_processor.py` - Main job processing logic
- `job_matcher/cv_utils.py` - CV-related utilities
- `job_matcher/prompt_adapter.py` - Manages prompt access and formatting
- `job_matcher/cli.py` - Command-line interface for job matching
- `job_matcher/feedback_handler.py` - Processes user feedback for matching improvement

## Usage Examples

### Generating Cover Letters
```bash
cd /home/xai/Documents/sunset
python -m scripts.doc_generator.generate_cover_letter -i
```

### Enhanced Cover Letter Generation

```bash
# Interactive mode with skill match integration
python -m scripts.doc_generator.generate_cover_letter -i

# Command line mode with skill match integration
python -m scripts.doc_generator.generate_cover_letter -j JOB_ID --job-title "Job Title" --use-self-assessment
```

### Converting Cover Letters to Word
```bash
cd /home/xai/Documents/sunset
python -m scripts.doc_generator.md_to_word_converter
```

### Sending Application Materials
```bash
cd /home/xai/Documents/sunset
python -m scripts.email_sender.email_sender
```

### Analyzing and Matching Job Skills
```bash
cd /home/xai/Documents/sunset
# Initialize skill decomposer files (first-time setup)
python -m scripts.utils.skill_decomposer.cli init

# Decompose a skill into elementary components
python -m scripts.utils.skill_decomposer.cli decompose "Project Management" --description "Managing project lifecycles"

# Decompose job requirements
python -m scripts.utils.skill_decomposer.cli job 62940

# Match your skills with job requirements
python -m scripts.utils.skill_decomposer.cli match 62940

# Generate a match summary
python -m scripts.utils.skill_decomposer.cli summary 62940 > job62940_match_summary.md

# Generate a visual HTML report of matches
python -m scripts.utils.skill_decomposer.cli report 62940

# Validate an inferred skill from your CV
python -m scripts.utils.skill_decomposer.cli validate "Technical Writing" --validate --add

# Export skill graph data for custom visualizations
python -m scripts.utils.skill_decomposer.cli export --output skill_graph.json
```

### Skill Match Reports

```bash
# Generate a full skill match summary report
python -m scripts.doc_generator.skill_match_report --job-id JOB_ID --summary

# Print just a skill match table to the console
python -m scripts.doc_generator.skill_match_report --job-id JOB_ID
```

### Automatic Job Analysis Workflow
The skill decomposer is automatically integrated with the job scraper:

```bash
# Scrape jobs and automatically analyze skill matches
cd /home/xai/Documents/sunset
python -m scripts.job_scraper.cli --max-jobs 10

# For each new job, the system will:
# 1. Create job decomposition files
# 2. Match job requirements against your skills
# 3. Generate match summaries and reports
```

### Running Tests
```bash
cd /home/xai/Documents/sunset
# Run the skill decomposer integration test
python tests/test_skill_integration.py

# Run a basic test of the core module
python tests/test_skill_core.py

# Run the skill decomposer example (shows basic usage)
python tests/skill_decomposer_example.py
```
