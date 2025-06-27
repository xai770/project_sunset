#!/usr/bin/env python3
"""
Integration test for the job expansion pipeline
"""

import os
import sys
import unittest
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR
from run_pipeline.utils.process_utils import check_command_available

class TestPipelineIntegration(unittest.TestCase):
    """Integration tests for the pipeline"""
    
    def test_basic_command(self):
        """Test that we can run a basic command"""
        from run_pipeline.utils.process_utils import run_process
        success, output = run_process(["echo", "test"], "Test command")
        self.assertTrue(success)
        self.assertIn("test", output)
    
    def test_firefox_check(self):
        """Test the Firefox check utility"""
        from run_pipeline.utils.firefox_utils import check_firefox_installed
        # This just tests that the function runs, not that Firefox is actually installed
        try:
            result = check_firefox_installed()
            print(f"Firefox installed: {result}")
        except Exception as e:
            self.fail(f"Firefox check raised exception: {str(e)}")

    def test_specific_job_ids_processing(self):
        """Test processing specific job IDs (simulate only)"""
        # Mock job IDs string
        job_ids_str = "63141,63142,63143"
        
        # Import the function to process job IDs
        from run_pipeline.core.pipeline_utils import process_job_ids
        
        # Process job IDs
        job_ids = process_job_ids(job_ids_str)
        
        # Check results
        self.assertEqual(job_ids, [63141, 63142, 63143])
        
if __name__ == "__main__":
    unittest.main()
