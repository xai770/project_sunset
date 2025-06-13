#!/usr/bin/env python3
"""
Beautiful Job Processor 🌟
==========================

Slim, elegant orchestrator for job matching using modular components.
This file is now clean, focused, and beautiful!

Main responsibilities:
- Orchestrate the job processing pipeline
- Coordinate between components
- Handle high-level error management
- Provide a clean API for job processing

Heavy lifting is delegated to focused, single-responsibility components.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import our beautiful modular components
try:
    from .components import (
        JobDataLoader, LLMEvaluator, JobUpdater, 
        FailureTracker, FeedbackProcessor
    )
except ImportError:
    # For direct execution
    from components import (
        JobDataLoader, LLMEvaluator, JobUpdater, 
        FailureTracker, FeedbackProcessor
    )
from run_pipeline.job_matcher.cv_loader import load_cv_text


class JobProcessor:
    """Beautiful, modular job processor"""
    
    def __init__(self, num_runs: int = 5):
        self.num_runs = num_runs
        self.data_loader = JobDataLoader()
        self.llm_evaluator = LLMEvaluator(num_runs=num_runs)
        self.job_updater = JobUpdater()
        self.failure_tracker = FailureTracker()
        self.feedback_processor = FeedbackProcessor()
    
    def process_job(self, job_id: str, cv_text: str, force_reprocess: bool = False, 
                   dump_input: bool = False) -> Dict[str, Any]:
        """
        Process a single job with LLM evaluation.
        
        Args:
            job_id: The job ID to process
            cv_text: The CV text
            force_reprocess: Whether to force reprocessing even if already evaluated
            dump_input: Whether to dump the LLM input to a file
            
        Returns:
            A dictionary with the processing results
        """
        print(f"\n{'='*80}\n🌟 Processing job ID: {job_id}\n{'='*80}")
        
        try:
            # Load job data
            job_data = self.data_loader.load_job_data(job_id)
        except FileNotFoundError:
            return {"error": "Job file not found"}
        except Exception as e:
            return {"error": f"Job file error: {str(e)}"}
        
        # Check if already processed (unless forcing reprocess)
        if not force_reprocess and self.data_loader.has_existing_evaluation(job_data):
            print(f"✅ Job {job_id} already processed with llama32_evaluation - skipping")
            return self.data_loader.get_evaluation_cache_info(job_data)
        
        # Check failure tracking - skip jobs that have failed too many times
        failure_status = self.failure_tracker.check_failure_status(job_data)
        if failure_status["should_skip"]:
            failed_attempts = failure_status["failed_attempts"]
            print(f"💀 Job {job_id} has failed {failed_attempts} times - permanently skipping")
            return {
                "error": f"Job permanently failed after {failed_attempts} attempts",
                "permanently_failed": True,
                "failed_attempts": failed_attempts
            }
        
        # Extract job information
        job_title, job_description = self.data_loader.extract_job_info(job_data)
        
        # Prepare full job description
        full_job_description = self.data_loader.prepare_job_description(job_data)
        
        # Ensure we have content to work with
        if not job_description:
            print(f"⚠️ Warning: No description available for job {job_id}")
            job_description = f"Position: {job_title}" if job_title else "No description available"
            full_job_description = job_description
        
        # Analyze job domain
        domain_analysis = self.llm_evaluator.analyze_job_domain(full_job_description)
        
        # Run LLM evaluation
        print(f"\n🚀 Starting LLM evaluation for job {job_id}...")
        results = self.llm_evaluator.run_llm_evaluation(cv_text, full_job_description)
        
        # Handle evaluation errors
        if "error" in results:
            print(f"❌ Error in LLM evaluation: {results['error']}")
            self.failure_tracker.track_job_failure(job_id, results['error'])
            return results
        
        # Save output files for debugging
        try:
            prompt = f"CV: {cv_text}\n\nJob: {full_job_description}"  # Simplified for file output
            self.job_updater.save_output_files(job_id, prompt, results, job_title, dump_input)
        except Exception as e:
            print(f"⚠️ Warning: Could not save output files: {e}")
        
        # Log extraction results
        self.job_updater.log_extraction_results(results)
        
        print(f"\n✨ Job {job_id} processed successfully!")
        return results
    
    def update_job_json(self, job_id: str, results: Dict[str, Any]) -> bool:
        """
        Update job JSON with evaluation results.
        
        Args:
            job_id: The job ID to update
            results: The evaluation results
            
        Returns:
            True if successful, False otherwise
        """
        return self.job_updater.update_job_json(job_id, results)
    
    def process_feedback(self, job_id: str, feedback_text: str, auto_update: bool = False) -> Dict[str, Any]:
        """
        Process feedback for a job evaluation.
        
        Args:
            job_id: The job ID
            feedback_text: The feedback text
            auto_update: Whether to auto-update prompts
            
        Returns:
            Dictionary with feedback processing results
        """
        return self.feedback_processor.process_feedback(job_id, feedback_text, auto_update)
    
    def reset_job_failures(self, job_id: str) -> bool:
        """
        Reset failure tracking for a job.
        
        Args:
            job_id: The job ID to reset
            
        Returns:
            True if successful, False otherwise
        """
        return self.failure_tracker.reset_job_failures(job_id)
    
    def get_failure_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all failed jobs.
        
        Returns:
            Dictionary with failure statistics
        """
        return self.failure_tracker.get_failure_summary()


# Convenience functions for backward compatibility
def process_job(job_id: str, cv_text: str, num_runs: int = 5, dump_input: bool = False, 
               force_reprocess: bool = False) -> Dict[str, Any]:
    """Backward compatibility function for process_job"""
    processor = JobProcessor(num_runs=num_runs)
    return processor.process_job(job_id, cv_text, force_reprocess, dump_input)


def update_job_json(job_id: str, results: Dict[str, Any]) -> bool:
    """Backward compatibility function for update_job_json"""
    processor = JobProcessor()
    return processor.update_job_json(job_id, results)


def process_feedback(job_id: str, feedback_text: str, auto_update: bool = False) -> Dict[str, Any]:
    """Backward compatibility function for process_feedback"""
    processor = JobProcessor()
    return processor.process_feedback(job_id, feedback_text, auto_update)


def track_job_failure(job_id: str, error_message: str) -> None:
    """Backward compatibility function for track_job_failure"""
    FailureTracker.track_job_failure(job_id, error_message)


def reset_job_failures(job_id: str) -> bool:
    """Backward compatibility function for reset_job_failures"""
    return FailureTracker.reset_job_failures(job_id)


def load_job_data(job_id: str) -> Dict[str, Any]:
    """Backward compatibility function for load_job_data"""
    return JobDataLoader.load_job_data(job_id)


# Legacy function imports for compatibility
try:
    from .response_parser import (
        extract_match_level, get_lowest_match, extract_domain_knowledge_assessment,
        extract_narrative_or_rationale
    )
    from .domain_analyzer import (
        get_domain_specific_requirements, extract_job_domain, analyze_domain_knowledge_gaps
    )
except ImportError:
    # For direct execution
    from response_parser import (
        extract_match_level, get_lowest_match, extract_domain_knowledge_assessment,
        extract_narrative_or_rationale
    )
    from domain_analyzer import (
        get_domain_specific_requirements, extract_job_domain, analyze_domain_knowledge_gaps
    )


if __name__ == "__main__":
    print("🌟 Beautiful Job Processor - Modular Architecture")
    print("This file now coordinates between focused, single-responsibility components!")
    print("\nComponents:")
    print("  📁 JobDataLoader - Handles job data loading and preparation")
    print("  🤖 LLMEvaluator - Manages LLM evaluation and response processing")
    print("  💾 JobUpdater - Handles job JSON updates and output files")
    print("  📊 FailureTracker - Manages failure tracking and retry logic")
    print("  💬 FeedbackProcessor - Processes user feedback and prompt optimization")
