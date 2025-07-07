#!/usr/bin/env python3
"""
Feedback Processor Component
===========================

Handles feedback processing for job match evaluations.
Manages feedback analysis and prompt optimization.
"""

import sys
from typing import Dict, Any
from pathlib import Path

# Handle both module and direct execution imports
try:
    from .job_data_loader import JobDataLoader
    # Import feedback handling module
    try:
        from run_pipeline.job_matcher.feedback_handler import (
            save_feedback, analyze_feedback, update_prompt_based_on_feedback
        )
        FEEDBACK_ENABLED = True
    except ImportError:
        print("Warning: Feedback handler module not available")
        FEEDBACK_ENABLED = False
except ImportError:
    # For direct execution
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from job_data_loader import JobDataLoader
    try:
        from run_pipeline.job_matcher.feedback_handler import (
            save_feedback, analyze_feedback, update_prompt_based_on_feedback
        )
        FEEDBACK_ENABLED = True
    except ImportError:
        print("Warning: Feedback handler module not available")
        FEEDBACK_ENABLED = False


class FeedbackProcessor:
    """Handles feedback processing for job evaluations"""
    
    @staticmethod
    def process_feedback(job_id: str, feedback_text: str, auto_update: bool = False) -> Dict[str, Any]:
        """
        Process feedback for a job match and optionally update prompts.
        
        Args:
            job_id: ID of the job to process feedback for
            feedback_text: Feedback text from the user
            auto_update: Whether to automatically update prompts based on feedback
            
        Returns:
            Dictionary with feedback processing results
        """
        if not FEEDBACK_ENABLED:
            return {"error": "Feedback handling is not enabled", "job_id": job_id}
        
        try:
            # Load job data to get the current match level and domain assessment
            job_data = JobDataLoader.load_job_data(job_id)
            llama_eval = job_data.get("llama32_evaluation", {})
            
            # Use the correct field names - cv_to_role_match instead of match_level
            match_level = llama_eval.get("cv_to_role_match")
            domain_assessment = llama_eval.get("domain_knowledge_assessment")
            
            if not match_level:
                return {"error": f"No match level found for job {job_id}", "job_id": job_id}
            
            # Save the feedback
            save_feedback(job_id, match_level, domain_assessment, feedback_text)
            
            # Analyze the feedback
            analysis_results = analyze_feedback(job_id, match_level, domain_assessment, feedback_text)
            
            # Optionally update the prompt based on feedback
            if auto_update:
                new_version = update_prompt_based_on_feedback(analysis_results, auto_update=True)
                analysis_results["prompt_updated"] = bool(new_version)
                analysis_results["new_prompt_version"] = new_version
            
            return {
                "job_id": job_id,
                "feedback_processed": True,
                "analysis": analysis_results
            }
        except Exception as e:
            print(f"Error processing feedback for job {job_id}: {e}")
            return {
                "job_id": job_id,
                "error": str(e)
            }
