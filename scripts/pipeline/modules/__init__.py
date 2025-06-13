"""
Pipeline Modules Package

This package contains modularized components for Project Sunset Phase 7 pipeline.
Each module handles a specific aspect of the pipeline workflow.

Modules:
- health_check: System health validation
- config_loader: Configuration loading and management
- job_fetcher: Job fetching functionality
- job_processor: Job processing with specialists
- excel_exporter: Excel export functionality
- cover_letter_generator: Cover letter generation
- email_sender: Email delivery
- job_recovery: Missing job detection and recovery
- data_bridge: Data structure compatibility
- simple_orchestrator: Main pipeline coordination

Usage:
    from scripts.pipeline.modules import simple_orchestrator
    
    # Run complete pipeline
    exit_code = simple_orchestrator.main()
"""

__version__ = "1.0.0"
__author__ = "Project Sunset Team"
