# Core pipeline initialization file
"""
Core pipeline module for job processing.

This package contains the core functionality for job processing pipelines:
- Pipeline orchestration
- Command-line argument parsing
- Skill matching coordination
- Utility functions for pipeline operations
- Auto-fix functionality for jobs with issues
"""

# Import the main pipeline components
from run_pipeline.core.pipeline_main import main
from run_pipeline.core.pipeline_orchestrator import run_pipeline
from run_pipeline.core.cli_args import parse_args
from run_pipeline.core.pipeline_utils import process_job_ids, check_for_missing_skills
from run_pipeline.core.auto_fix import auto_fix_missing_skills_and_matches
from run_pipeline.core.skill_matching_orchestrator import run_skill_matching

__all__ = [
    'main', 
    'run_pipeline', 
    'parse_args', 
    'process_job_ids', 
    'check_for_missing_skills',
    'auto_fix_missing_skills_and_matches',
    'run_skill_matching'
]
