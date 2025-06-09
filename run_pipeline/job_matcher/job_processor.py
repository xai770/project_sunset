#!/usr/bin/env python3
"""
Job Processor module for job matching.

This module handles the processing of job data, including loading job files,
running LLM evaluations, and saving results.
"""
import os
import sys
import json
import time
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import local modules
from run_pipeline.config.paths import JOB_DATA_DIR
from run_pipeline.job_matcher.llm_client import call_llama3_api
from run_pipeline.job_matcher.response_parser import (
    extract_match_level, get_lowest_match, extract_domain_knowledge_assessment,
    extract_narrative_or_rationale
)
from run_pipeline.job_matcher.domain_analyzer import (
    get_domain_specific_requirements, extract_job_domain, analyze_domain_knowledge_gaps
)
from run_pipeline.job_matcher.prompt_adapter import get_formatted_prompt
# Import feedback handling module
try:
    from run_pipeline.job_matcher.feedback_handler import (
        save_feedback, analyze_feedback, update_prompt_based_on_feedback
    )
    FEEDBACK_ENABLED = True
except ImportError:
    print("Warning: Feedback handler module not available")
    FEEDBACK_ENABLED = False

import sys

def load_job_data(job_id: str) -> Dict[str, Any]:
    """
    Load job data from a JSON file.
    
    Args:
        job_id: The job ID to load
        
    Returns:
        A dictionary with the job data
        
    Raises:
        FileNotFoundError: If the job file does not exist
        json.JSONDecodeError: If the job file cannot be parsed as JSON
    """
    job_path = os.path.join(JOB_DATA_DIR, f"job{job_id}.json")
    with open(job_path, "r", encoding="utf-8") as jf:
        return json.load(jf)  # type: ignore

def prepare_job_description(job_data: Dict[str, Any]) -> str:
    """
    Prepare a job description from job data.
    
    Args:
        job_data: The job data dictionary
        
    Returns:
        A formatted job description string
    """
    web_details = job_data.get("web_details", {})
    job_title = web_details.get("position_title", "")
    concise_desc = web_details.get("concise_description", "")
    return f"Position Title: {job_title}\n\n{concise_desc}"

def run_llm_evaluation(cv_text: str, job_description: str, num_runs: int = 5) -> Dict[str, Any]:
    """
    Run the LLM evaluation multiple times and return the results.
    
    Args:
        cv_text: The CV text
        job_description: The job description text
        num_runs: Number of times to run the LLM (default: 5)
        
    Returns:
        A dictionary with the evaluation results
    """
    # Get the prompt using the prompt manager
    try:
        prompt = get_formatted_prompt('llama3_cv_match', category='job_matching', cv=cv_text, job=job_description)
    except Exception as e:
        print(f"Error loading prompt from prompt manager: {e}")
        # Fall back to a local copy of the prompt
        from run_pipeline.job_matcher.default_prompt import LLAMA3_PROMPT
        prompt = LLAMA3_PROMPT.format(cv=cv_text, job=job_description)
    
    # Run LLM multiple times and collect responses
    print(f"Calling llama3.2:latest LLM {num_runs} times...")
    responses = []
    match_levels = []
    max_retries_per_run = 3  # Maximum number of retries per run
    
    run_count = 0
    while run_count < num_runs:
        print(f"Run {run_count+1}/{num_runs}...")
        
        # Add a small random variation to the prompt to prevent caching
        variation = f"Run ID: {run_count+1}-{random.randint(1000, 9999)}"
        modified_prompt = prompt + f"\n\n# Internal: {variation}"
        
        retry_count = 0
        success = False
        
        # Retry logic for cases where match level can't be extracted
        while retry_count < max_retries_per_run and not success:
            # Call LLM with the slightly modified prompt
            try:
                if retry_count > 0:
                    print(f"  Retry {retry_count}/{max_retries_per_run} for run {run_count+1}...")
                    # Add even more randomness to the prompt for retries
                    variation = f"Run ID: {run_count+1}-Retry{retry_count}-{random.randint(10000, 99999)}"
                    modified_prompt = prompt + f"\n\n# Internal: {variation}"
                
                response = call_llama3_api(modified_prompt)
                
                match_level = extract_match_level(response)
                if match_level:
                    responses.append(response)
                    match_levels.append(match_level)
                    print(f"Run {run_count+1} match level: {match_level}")
                    success = True
                else:
                    print(f"Run {run_count+1}: Could not extract match level")
                    if retry_count == max_retries_per_run - 1:
                        # If this is our last retry, save the response anyway
                        print(f"  After {max_retries_per_run} retries, still couldn't extract match level. Continuing...")
                        responses.append(response)
                
                retry_count += 1
            except Exception as e:
                print(f"Error in Run {run_count+1}: {e}")
                responses.append(f"ERROR: {e}")
                retry_count += 1
                if retry_count == max_retries_per_run:
                    print(f"  Failed after {retry_count} retries, continuing to next run")
        
        # Increment run count only if we're done with retries
        run_count += 1
        
        # Add a short delay between runs to ensure we're not hitting any rate limits
        if run_count < num_runs:  # Don't delay after the last run
            delay = random.uniform(1.0, 2.0)
            print(f"Waiting {delay:.1f} seconds before next run...")
            time.sleep(delay)
    
    # Process the responses and extract the final results
    if not match_levels:
        return {"error": "No match levels could be extracted"}
    
    # Determine the lowest match level
    lowest_match = get_lowest_match(match_levels)
    print(f"\nMatch levels from {num_runs} runs: {', '.join(match_levels)}")
    print(f"Lowest match level: {lowest_match}")
    
    # Simple check for "Low" matches in responses - if any run returns "Low", use that
    # This is a strict enforcement of the "THIS RULE IS ALWAYS VALID!" directive in the prompt
    if "Low" in match_levels:
        print("At least one run returned 'Low match' - enforcing strict rule")
        lowest_match = "Low"
    
    # Find a response with the lowest match level
    lowest_match_response = None
    for response in responses:
        if extract_match_level(response) == lowest_match:
            lowest_match_response = response
            break
    
    if not lowest_match_response:
        return {"error": "Could not find response with lowest match level"}
    
    # Extract the domain knowledge assessment
    domain_assessment = extract_domain_knowledge_assessment(lowest_match_response)
    
    # Extract the narrative or rationale
    # Handle the case where lowest_match might be None
    if lowest_match is not None:
        field_type, content = extract_narrative_or_rationale(lowest_match_response, lowest_match)
    else:
        # Default values if match level is None
        field_type, content = "No-go rationale", "Could not determine match level properly"
    
    # Improve match level determination by checking domain knowledge gaps
    if domain_assessment:
        has_critical_gap, has_domain_reqs, domain_gap_severity, domain_req_percentage = analyze_domain_knowledge_gaps(domain_assessment)
        
        # More aggressively analyze domain gap severity and adjust match level accordingly
        # Lower the threshold for critical gaps (from 2 to 1) and for domain requirement percentage (from 25 to 15)
        if (domain_gap_severity >= 1 or domain_req_percentage > 15 or "gap" in domain_assessment.lower()) and lowest_match == "Good":
            print(f"Critical domain knowledge gap detected despite 'Good' match - downgrading to 'Low' match")
            print(f"Domain gap severity: {domain_gap_severity}, Domain requirements mentioned: {domain_req_percentage:.1f}%")
            lowest_match = "Low"
            
            # If we have an Application narrative but we're downgrading the match, convert it to a No-go rationale
            if field_type == "Application narrative":
                field_type = "No-go rationale"
                content = f"I have compared my CV and the role description and decided not to apply due to critical domain knowledge gaps: {domain_assessment}"
        # Check for specific keywords indicating a skill gap that would make this a Moderate match at best
        elif (has_domain_reqs or "experience" in domain_assessment.lower() or 
              "skill" in domain_assessment.lower() or "knowledge" in domain_assessment.lower()) and lowest_match == "Good":
            print(f"Moderate domain knowledge gap detected in 'Good' match - downgrading to 'Moderate' match")
            print(f"Domain gap severity: {domain_gap_severity}, Domain requirements mentioned: {domain_req_percentage:.1f}%")
            lowest_match = "Moderate"
            
            # If we have an Application narrative but we're downgrading the match, convert it to a No-go rationale
            if field_type == "Application narrative":
                field_type = "No-go rationale"
                content = f"I have compared my CV and the role description and decided not to apply due to the following domain knowledge gaps: {domain_assessment}"
    
    # If we detect a No-go rationale in the response, override the match level to "Low"
    # But only if the field_type is actually "No-go rationale" to prevent false positives
    if field_type == "No-go rationale":
        lowest_match = "Low"
        print("Detected No-go rationale - overriding match level to Low")
    
    # Check for missing or very short content
    if content and len(content.strip()) < 15:  # Content is too short or near empty
        print(f"\nWARNING: Extracted content is too short: '{content}'")
        if lowest_match != "Good":
            # For Low/Moderate, provide a generic no-go rationale if extracted content is too short
            field_type = "No-go rationale"
            content = "I have compared my CV and the role description and decided not to apply due to the missing skills or experience that would be required for this position."
            print("Using generic no-go rationale instead")
        else:
            # For Good match, provide generic application narrative
            field_type = "Application narrative"
            content = "My skills and experience align well with this position based on the match assessment."
            print("Using generic application narrative instead")
    
    # Create the final output dictionary with proper type annotations
    results: Dict[str, Any] = {
        "cv_to_role_match": lowest_match if lowest_match is not None else "Unknown",
        "domain_knowledge_assessment": domain_assessment if domain_assessment is not None else "",
        "llama32_responses": [
            {"match_level": extract_match_level(resp) or "Unknown", 
             "response": resp} 
            for resp in responses
        ]
    }
    
    # Add the narrative or rationale with proper key
    if field_type is not None:
        results[field_type] = content if content is not None else ""
    
    return results

def process_job(job_id: str, cv_text: str, num_runs: int = 5, dump_input: bool = False) -> Dict[str, Any]:
    """
    Process a single job with LLM evaluation.
    
    Args:
        job_id: The job ID to process
        cv_text: The CV text
        num_runs: Number of times to run the LLM (default: 5)
        dump_input: Whether to dump the LLM input to a file (default: False)
        
    Returns:
        A dictionary with the processing results
    """
    print(f"\n{'='*80}\nProcessing job ID: {job_id}\n{'='*80}")
    
    # Prepare LLM input
    try:
        job_data = load_job_data(job_id)
    except FileNotFoundError:
        print(f"Job file not found: {os.path.join(JOB_DATA_DIR, f'job{job_id}.json')}")
        return {"error": "Job file not found"}
    except json.JSONDecodeError:
        print(f"Error decoding job file: {os.path.join(JOB_DATA_DIR, f'job{job_id}.json')}")
        return {"error": "Job file decode error"}
    
    web_details = job_data.get("web_details")
    if not web_details:
        print(f"No web_details found in job{job_id}.json")
        return {"error": "No web_details found"}
    
    job_title = web_details.get("position_title", "")
    concise_desc = web_details.get("concise_description", "")
    job_description = prepare_job_description(job_data)
    
    # Extract domain-specific requirements and job domain for better analysis
    domain_specific_requirements = get_domain_specific_requirements(job_description)
    job_domain = extract_job_domain(job_description)
    
    print(f"\nAnalyzing job domain: {job_domain}")
    if domain_specific_requirements:
        print(f"Extracted {len(domain_specific_requirements)} domain-specific requirements:")
        for idx, req in enumerate(domain_specific_requirements[:5], 1):
            print(f"  {idx}. {req}")
        if len(domain_specific_requirements) > 5:
            print(f"  ... and {len(domain_specific_requirements) - 5} more")
    
    # Get the prompt using the prompt manager
    try:
        prompt = get_formatted_prompt('llama3_cv_match', category='job_matching', cv=cv_text, job=job_description)
    except Exception as e:
        print(f"Error loading prompt from prompt manager: {e}")
        # Fall back to a local copy of the prompt
        from run_pipeline.job_matcher.default_prompt import LLAMA3_PROMPT
        prompt = LLAMA3_PROMPT.format(cv=cv_text, job=job_description)
            
    # If --dump-input is set, dump the LLM input to a text file
    if dump_input:
        job_path = os.path.join(JOB_DATA_DIR, f"job{job_id}.json")
        dump_path = os.path.join(os.path.dirname(job_path), f"job{job_id}_llm_input.txt")
        with open(dump_path, "w", encoding="utf-8") as outf:
            # First include the full prompt (which already contains the CV and job details)
            # Then add the job information after the separator for easier reference
            outf.write(f"PROMPT SENT TO LLM:\n\n{prompt}\n\n---\n\njob_title: {job_title}\n\nconcise_desc:\n{concise_desc}\n\njob_description:\n{job_description}\n")
        print(f"LLM input dumped to {dump_path}")
    
    # Run LLM evaluation
    results = run_llm_evaluation(cv_text, job_description, num_runs)
    
    if "error" in results:
        print(f"Error in LLM evaluation: {results['error']}")
        return results
    
    # Save all responses to a file
    job_path = os.path.join(JOB_DATA_DIR, f"job{job_id}.json")
    all_responses_path = os.path.join(os.path.dirname(job_path), f"job{job_id}_all_llm_responses.txt")
    with open(all_responses_path, "w", encoding="utf-8") as outf:
        # Start with the exact prompt that was sent to the LLM
        outf.write(f"=== EXACT PROMPT SENT TO LLM ===\n\n{prompt}\n\n")
        outf.write("=== LLM RESPONSES ===\n\n")
        
        # Then include all individual LLM responses
        for i, resp_obj in enumerate(results.get("llama32_responses", [])):
            outf.write(f"--- Run {i+1}/{num_runs} ---\n\n")
            outf.write(resp_obj.get("response", "ERROR: No response"))
            outf.write("\n\n")
    print(f"\nAll LLM responses saved to {all_responses_path}")
    
    # Create the final output
    final_output = f"**CV-to-role match:** {results.get('cv_to_role_match')} match\n"
    domain_assessment = results.get("domain_knowledge_assessment")
    if domain_assessment:
        final_output += f"**Domain knowledge assessment:** {domain_assessment}\n"
    
    # Add the appropriate narrative based on match level
    if results.get("cv_to_role_match") == "Good" and results.get("Application narrative"):
        final_output += f"**Application narrative:** {results.get('Application narrative')}\n"
    elif results.get("No-go rationale"):
        final_output += f"**No-go rationale:** {results.get('No-go rationale')}\n"
    
    # Log what content was successfully extracted
    if domain_assessment:
        print("\nSuccessfully extracted domain knowledge assessment")
    else:
        print("\nWARNING: No domain knowledge assessment found")
    
    if results.get("cv_to_role_match") == "Good":
        if results.get("Application narrative") and len(results.get("Application narrative", "")) > 10:
            print("Successfully extracted application narrative")
        else:
            print("WARNING: Expected application narrative for 'Good' match but got nothing")
    else:  # Low or Moderate
        if results.get("No-go rationale") and len(results.get("No-go rationale", "")) > 10:
            print("Successfully extracted no-go rationale")
        else:
            print("WARNING: Expected no-go rationale for 'Low/Moderate' match but got nothing")
    
    print("\n--- FINAL LLM RESPONSE (Lowest Match Level) ---\n")
    print(final_output)
    
    # Save the final output to a text file
    out_path = os.path.join(os.path.dirname(job_path), f"job{job_id}_llm_output.txt")
    with open(out_path, "w", encoding="utf-8") as outf:
        outf.write(final_output)
    print(f"Final LLM output (lowest match) saved to {out_path}")
    
    return results

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
        
        # Save the updated job data
        with open(job_path, "w", encoding="utf-8") as jf:
            json.dump(job_data, jf, indent=2)
        
        print(f"Job {job_id} JSON updated with LLM evaluation results")
        return True
    
    except Exception as e:
        print(f"Error updating job {job_id} JSON: {e}")
        return False

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
        job_data = load_job_data(job_id)
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
