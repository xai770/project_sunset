# run_pipeline Directory Overview

This directory contains all scripts and modules for the main job matching and skill matching pipeline. Below is a summary of the main scripts and their status.

## Main Scripts

- **run.py**: Main entry point for running the job expansion pipeline. Now also supports the feedback loop via CLI.
- **run_domain_enhanced_matcher.py**: Runs the domain-enhanced matcher pipeline.
- **register_prompt.py**: Registers prompts with the prompt manager system.
- **process_excel_feedback.py**: Reads exported Excel, processes feedback for each job, and runs the feedback loop.
- **export_job_matches.py**: (If present) Exports job match results to Excel. (If missing, please add or document location.)
- **test_feedback_loop.py**: Script to test the feedback loop logic.
- **test_job_match.py**: Script to test job matching logic.
- **test_migration.py**: Script to verify migration of job_matcher to run_pipeline.
- **test_feedback.py**: Script to test feedback processing.

## Analyzers

- **analyzers/**: Contains advanced analysis scripts (e.g., synergy_analyzer.py, match_analyzer.py, etc.).
  - All analyzers in this folder are current and should be used from here.

## Job Matcher

- **job_matcher/**: Main job matching logic and feedback system. See job_matcher/README.md for details.

## Skill Matching

- **skill_matching/**: Contains all scripts and modules for skill matching and related pipelines.

## Utilities

- **utils/**: Utility scripts and helpers for the pipeline.

## Other Scripts

- **demo_llm_logging.py**: Demo script for LLM logging. (If not used in production, consider marking as demo/obsolete.)
- **manual_job_analyzer.py**: Manual job analysis script. (If not used, mark as obsolete.)
- **job_match_reviewer.py**: Script for reviewing job matches. (If not used, mark as obsolete.)
- **backup_local_project.sh, restore_from_backup.sh**: Project backup/restore scripts.

## Obsolete or Legacy Scripts

- **manual_job_analyzer.py**: OBSOLETE: Not used in current pipeline, kept for reference only.
- **job_match_reviewer.py**: OBSOLETE: Not used in current pipeline, kept for reference only.
- **demo_llm_logging.py**: DEMO: For demonstration purposes, not used in production pipeline.
- **register_job_matching_prompt.py**: Possibly redundant with register_prompt.py. Use register_prompt.py for new prompt registration.

## Cover Letter Generator

You can generate a custom cover letter using the integrated CLI:

```bash
python run.py --cover-letter --cover-letter-args [additional args]
```

- The cover letter generator supports interactive and non-interactive modes.
- See `run_pipeline/cover_letter/README.md` for details on arguments and template customization.

---

**Please update this README as you add, remove, or deprecate scripts!**
