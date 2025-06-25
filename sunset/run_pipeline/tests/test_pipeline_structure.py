#!/usr/bin/env python3
"""
Basic test to verify the new run_pipeline module
"""

import os
import sys
import unittest
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR
from run_pipeline.utils.logging_utils import setup_logger

class TestPipeline(unittest.TestCase):
    """Tests for the new pipeline structure"""
    
    def setUp(self):
        """Set up the test environment"""
        self.logger, _ = setup_logger('test_pipeline')
    
    def test_import_modules(self):
        """Test that all modules can be imported without errors"""
        # This will fail if imports are broken
        try:
            from run_pipeline.core import pipeline
            from run_pipeline.core import fetch_module
            from run_pipeline.core import scraper_module
            from run_pipeline.core import cleaner_module
            from run_pipeline.utils import logging_utils
            from run_pipeline.utils import process_utils
            from run_pipeline.utils import firefox_utils
            from run_pipeline.config import paths
            
            self.logger.info("All modules imported successfully")
        except ImportError as e:
            self.fail(f"Import failed: {str(e)}")
    
    def test_config_paths(self):
        """Test that config paths are correctly set up"""
        from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR
        
        self.assertTrue(PROJECT_ROOT.exists(), f"Project root doesn't exist: {PROJECT_ROOT}")
        self.assertEqual(PROJECT_ROOT.name, "sunset", "Project root should be 'sunset'")
        
        # Create JOB_DATA_DIR if it doesn't exist for the test
        JOB_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.assertTrue(JOB_DATA_DIR.exists(), f"Job data directory doesn't exist: {JOB_DATA_DIR}")

if __name__ == "__main__":
    unittest.main()
