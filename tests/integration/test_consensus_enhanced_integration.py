"""
Integration tests for ConsensusEnhancedIntegration to verify threading fixes.
"""
import pytest
import warnings
import logging
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

from run_pipeline.consensus_enhanced_integration import ConsensusEnhancedIntegration


class TestConsensusEnhancedIntegration:
    """Test class for consensus enhanced integration."""
    
    def test_evaluate_job_fitness_no_threading_warning(self):
        """Test that evaluate_job_fitness does not produce max_workers warnings."""
        # Capture all warnings
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            
            # Capture stderr to catch any printed warnings
            old_stderr = sys.stderr
            captured_stderr = StringIO()
            sys.stderr = captured_stderr
            
            # Capture logging output
            log_capture = StringIO()
            handler = logging.StreamHandler(log_capture)
            logger = logging.getLogger()
            old_level = logger.level
            logger.setLevel(logging.DEBUG)
            logger.addHandler(handler)
            
            try:
                # Create integration instance
                integration = ConsensusEnhancedIntegration()
                
                # Mock job posting and candidate profile
                job_posting = {
                    "title": "Senior Software Engineer",
                    "description": "Looking for an experienced developer",
                    "required_skills": ["Python", "Django", "REST APIs"],
                    "experience_level": "Senior"
                }
                
                candidate_profile = {
                    "name": "John Doe",
                    "skills": ["Python", "Django", "PostgreSQL"],
                    "experience_years": 5,
                    "previous_roles": ["Software Developer", "Backend Engineer"]
                }
                
                # Test the evaluation (this should not produce threading warnings)
                result = integration.evaluate_job_fitness(job_posting, candidate_profile)
                
                # Check that we got some result (even if it's a fallback)
                assert result is not None
                assert isinstance(result, dict)
                
                # Verify no threading-related warnings were raised
                stderr_output = captured_stderr.getvalue()
                log_output = log_capture.getvalue()
                
                threading_warnings = [w for w in warning_list 
                                    if 'max_workers' in str(w.message).lower()]
                
                stderr_threading_warnings = [line for line in stderr_output.split('\n') 
                                           if 'max_workers' in line.lower()]
                
                log_threading_warnings = [line for line in log_output.split('\n') 
                                        if 'max_workers' in line.lower() and 'warning' in line.lower()]
                
                # Assert no threading warnings
                assert len(threading_warnings) == 0, f"Found threading warnings: {threading_warnings}"
                assert len(stderr_threading_warnings) == 0, f"Found stderr threading warnings: {stderr_threading_warnings}"
                assert len(log_threading_warnings) == 0, f"Found log threading warnings: {log_threading_warnings}"
                
                print(f"✅ Test passed - No threading warnings detected")
                print(f"Result: {result}")
                
            finally:
                # Restore stderr and logging
                sys.stderr = old_stderr
                logger.removeHandler(handler)
                logger.setLevel(old_level)
    
    def test_consensus_engine_initialization(self):
        """Test that consensus engine is properly initialized without threading issues."""
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            
            # Create integration instance
            integration = ConsensusEnhancedIntegration()
            
            # Access the consensus engine to trigger initialization
            consensus_engine = integration._get_consensus_engine()
            
            # Verify no warnings related to threading
            threading_warnings = [w for w in warning_list 
                                if 'max_workers' in str(w.message).lower()]
            
            assert len(threading_warnings) == 0, f"Found threading warnings during initialization: {threading_warnings}"
            assert consensus_engine is not None
            
            print("✅ Consensus engine initialized without threading warnings")
    
    def test_threading_patch_applied(self):
        """Test that our ThreadPoolExecutor patch is properly applied."""
        import concurrent.futures
        
        # Verify our patch is in place
        executor_class = concurrent.futures.ThreadPoolExecutor
        
        # Create an executor with max_workers=0 (should be fixed by our patch)
        executor = executor_class(max_workers=0)
        
        # Our patch should ensure max_workers is valid
        assert executor._max_workers > 0
        
        executor.shutdown(wait=True)
        
        print(f"✅ ThreadPoolExecutor patch working - max_workers set to {executor._max_workers}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
