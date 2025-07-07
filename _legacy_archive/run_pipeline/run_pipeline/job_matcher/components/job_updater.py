#!/usr/bin/env python3
"""
Job Updater Component
====================

Handles updating job JSON files with evaluation results.
Manages output file generation and data persistence.
"""

import os
import json
import sys
import time
from typing import Dict, Any
from pathlib import Path

# Get paths - handle both module and direct execution
try:
    from run_pipeline.config.paths import JOB_DATA_DIR
    from .failure_tracker import FailureTracker
except ImportError:
    # For direct execution, add project root to path
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from run_pipeline.config.paths import JOB_DATA_DIR
    from failure_tracker import FailureTracker


class JobUpdater:
    """Handles updating job JSON files with evaluation results"""
    
    @staticmethod
    def update_job_json(job_id: str, results: Dict[str, Any]) -> bool:
        """
        Update a job JSON file with the LLM evaluation results.
        
        Args:
            job_id: The job ID to update
            results: The evaluation results
            
        Returns:
            True if the update was successful, False otherwise
        """
        job_path = os.path.join(JOB_DATA_DIR, f"job{job_id}.json")
        try:
            with open(job_path, "r", encoding="utf-8") as jf:
                job_data = json.load(jf)
            
            # Get the match level
            cv_to_role_match = results.get("cv_to_role_match")
            
            # For consistency, ensure we have the right content based on match level
            application_narrative = None
            no_go_rationale = None
            
            if cv_to_role_match == "Good":
                application_narrative = results.get("Application narrative")
            else:  # Low or Moderate match
                # If we have a No-go rationale, use it
                no_go_rationale = results.get("No-go rationale")
                
                # If we somehow still have an Application narrative despite not being "Good", 
                # convert it into a No-go rationale
                if not no_go_rationale and results.get("Application narrative"):
                    no_go_rationale = f"I have compared my CV and the role description and decided not to apply due to the following reasons: [Missing explicit rationale, but match level is {cv_to_role_match}]"
            
            # Add LLM evaluation results
            llama32_evaluation = {
                "cv_to_role_match": cv_to_role_match,
                "evaluation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "num_runs": len(results.get("llama32_responses", [])),
                "method": "multiple_runs_lowest_match"
            }
            
            # Include domain knowledge assessment if available
            domain_knowledge_assessment = results.get("domain_knowledge_assessment")
            if domain_knowledge_assessment:
                llama32_evaluation["domain_knowledge_assessment"] = domain_knowledge_assessment
                print(f"Domain knowledge assessment available: Yes")
            else:
                print(f"Domain knowledge assessment available: No")
            
            # Only include the appropriate narrative field based on match level
            if cv_to_role_match == "Good":
                llama32_evaluation["application_narrative"] = application_narrative
                llama32_evaluation["no_go_rationale"] = None
                print(f"Storing 'Good' match with application narrative " +
                      ("(content available)" if application_narrative else "(NO CONTENT)"))
            else:  # Low or Moderate match
                llama32_evaluation["no_go_rationale"] = no_go_rationale
                llama32_evaluation["application_narrative"] = None
                print(f"Storing '{cv_to_role_match}' match with no-go rationale " +
                      ("(content available)" if no_go_rationale else "(NO CONTENT)"))
            
            job_data["llama32_evaluation"] = llama32_evaluation
            
            # Clear any failure tracking on successful evaluation
            job_data = FailureTracker.clear_failure_tracking(job_data)
            if "failure_tracking" in job_data:
                print(f"✅ Clearing failure tracking for successful evaluation of job {job_id}")
            
            # Save the updated job data
            with open(job_path, "w", encoding="utf-8") as jf:
                json.dump(job_data, jf, indent=2)
            
            print(f"Job {job_id} JSON updated with LLM evaluation results")
            return True
        
        except Exception as e:
            print(f"Error updating job {job_id} JSON: {e}")
            return False
    
    @staticmethod
    def save_output_files(job_id: str, prompt: str, results: Dict[str, Any], 
                         job_title: str = "", dump_input: bool = False) -> None:
        """
        Save LLM input/output files for debugging and analysis.
        
        Args:
            job_id: The job ID
            prompt: The LLM prompt that was used
            results: The evaluation results
            job_title: The job title (optional)
            dump_input: Whether to save the input file
        """
        job_path = os.path.join(JOB_DATA_DIR, f"job{job_id}.json")
        base_dir = os.path.dirname(job_path)
        
        # Save LLM input if requested
        if dump_input:
            dump_path = os.path.join(base_dir, f"job{job_id}_llm_input.txt")
            with open(dump_path, "w", encoding="utf-8") as outf:
                outf.write(f"PROMPT SENT TO LLM:\n\n{prompt}\n\n---\n\njob_title: {job_title}\n")
            print(f"LLM input dumped to {dump_path}")
        
        # Save all responses to a file
        all_responses_path = os.path.join(base_dir, f"job{job_id}_all_llm_responses.txt")
        with open(all_responses_path, "w", encoding="utf-8") as outf:
            # Start with the exact prompt that was sent to the LLM
            outf.write(f"=== EXACT PROMPT SENT TO LLM ===\n\n{prompt}\n\n")
            outf.write("=== LLM RESPONSES ===\n\n")
            
            # Then include all individual LLM responses
            for i, resp_obj in enumerate(results.get("llama32_responses", [])):
                outf.write(f"--- Run {i+1} ---\n\n")
                outf.write(resp_obj.get("response", "ERROR: No response"))
                outf.write("\n\n")
        print(f"\nAll LLM responses saved to {all_responses_path}")
        
        # Create and save the final output
        final_output = f"**CV-to-role match:** {results.get('cv_to_role_match')} match\n"
        domain_assessment = results.get("domain_knowledge_assessment")
        if domain_assessment:
            final_output += f"**Domain knowledge assessment:** {domain_assessment}\n"
        
        # Add the appropriate narrative based on match level
        if results.get("cv_to_role_match") == "Good" and results.get("Application narrative"):
            final_output += f"**Application narrative:** {results.get('Application narrative')}\n"
        elif results.get("No-go rationale"):
            final_output += f"**No-go rationale:** {results.get('No-go rationale')}\n"
        
        # Save the final output to a text file
        out_path = os.path.join(base_dir, f"job{job_id}_llm_output.txt")
        with open(out_path, "w", encoding="utf-8") as outf:
            outf.write(final_output)
        print(f"Final LLM output (lowest match) saved to {out_path}")
    
    @staticmethod
    def log_extraction_results(results: Dict[str, Any]) -> None:
        """
        Log what content was successfully extracted from LLM responses.
        
        Args:
            results: The evaluation results
        """
        domain_assessment = results.get("domain_knowledge_assessment")
        match_level = results.get("cv_to_role_match")
        
        # Log what content was successfully extracted
        if domain_assessment:
            print("\nSuccessfully extracted domain knowledge assessment")
        else:
            print("\nWARNING: No domain knowledge assessment found")
        
        if match_level == "Good":
            app_narrative = results.get("Application narrative")
            if app_narrative and len(app_narrative) > 10:
                print("Successfully extracted application narrative")
            else:
                print("WARNING: Expected application narrative for 'Good' match but got nothing")
        else:  # Low or Moderate
            no_go_rationale = results.get("No-go rationale")
            if no_go_rationale and len(no_go_rationale) > 10:
                print("Successfully extracted no-go rationale")
            else:
                print("WARNING: Expected no-go rationale for 'Low/Moderate' match but got nothing")
        
        # Display final results
        final_output = f"**CV-to-role match:** {match_level} match\n"
        if domain_assessment:
            final_output += f"**Domain knowledge assessment:** {domain_assessment}\n"
        
        if match_level == "Good" and results.get("Application narrative"):
            final_output += f"**Application narrative:** {results.get('Application narrative')}\n"
        elif results.get("No-go rationale"):
            final_output += f"**No-go rationale:** {results.get('No-go rationale')}\n"
        
        print("\n--- FINAL LLM RESPONSE (Lowest Match Level) ---\n")
        print(final_output)
