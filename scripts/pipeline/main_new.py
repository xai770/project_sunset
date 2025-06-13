#!/usr/bin/env python3
"""
Project Sunset Phase 7 - Complete Pipeline Entry Point
====================================================

Modular, streamlined entry point for the full modernized pipeline including:
- Job fetching (JobFetcherP5)
- Job processing with specialists (JobMatchingAPI)
- Excel export (JMFS format)
- Cover letter generation
- Email delivery

Enhanced with beautiful CLI interface and centralized configuration.
Using specialists for ALL LLM interactions.

This file now uses a modular architecture with organized components.
All heavy lifting is done by the modules in the modules/ directory.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.config_manager import get_config, display_config_banner
from core.beautiful_cli import print_sunset_banner

# Import the modular pipeline orchestrator
try:
    from .modules.pipeline_orchestrator import main as orchestrator_main
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "modules"))
    from pipeline_orchestrator import main as orchestrator_main

def main():
    """Main entry point for Project Sunset Phase 7 with beautiful CLI"""
    
    # Display beautiful banner
    print_sunset_banner()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load and display configuration
    config = get_config()
    if config.debug:
        display_config_banner()
    
    # All the heavy lifting is now done by the orchestrator
    return orchestrator_main()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
