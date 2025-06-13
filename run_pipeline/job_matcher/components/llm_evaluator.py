#!/usr/bin/env python3
"""
LLM Evaluator Component
======================

Handles all LLM evaluation logic for job matching.
Manages multiple runs, response processing, and domain analysis.
"""

import time
import random
import sys
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Handle both module and direct execution imports
try:
    from run_pipeline.job_matcher.llm_client import call_llama3_api
    from run_pipeline.job_matcher.response_parser import (
        extract_match_level, get_lowest_match, extract_domain_knowledge_assessment,
        extract_narrative_or_rationale
    )
    from run_pipeline.job_matcher.domain_analyzer import (
        get_domain_specific_requirements, extract_job_domain, analyze_domain_knowledge_gaps
    )
    from run_pipeline.job_matcher.prompt_adapter import get_formatted_prompt
except ImportError:
    # For direct execution, add project root to path
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from run_pipeline.job_matcher.llm_client import call_llama3_api
    from run_pipeline.job_matcher.response_parser import (
        extract_match_level, get_lowest_match, extract_domain_knowledge_assessment,
        extract_narrative_or_rationale
    )
    from run_pipeline.job_matcher.domain_analyzer import (
        get_domain_specific_requirements, extract_job_domain, analyze_domain_knowledge_gaps
    )
    from run_pipeline.job_matcher.prompt_adapter import get_formatted_prompt


class LLMEvaluator:
    """Handles LLM evaluation for job matching"""
    
    def __init__(self, num_runs: int = 5, max_retries_per_run: int = 3):
        self.num_runs = num_runs
        self.max_retries_per_run = max_retries_per_run
    
    def run_llm_evaluation(self, cv_text: str, job_description: str) -> Dict[str, Any]:
        """
        Run the LLM evaluation multiple times and return the results.
        
        Args:
            cv_text: The CV text
            job_description: The job description text
            
        Returns:
            A dictionary with the evaluation results
        """
        # Get the prompt using the prompt manager
        try:
            prompt = get_formatted_prompt('llama3_cv_match', category='job_matching', 
                                        cv=cv_text, job=job_description)
        except Exception as e:
            print(f"Error loading prompt from prompt manager: {e}")
            # Fall back to a local copy of the prompt
            from run_pipeline.job_matcher.default_prompt import LLAMA3_PROMPT
            prompt = LLAMA3_PROMPT.format(cv=cv_text, job=job_description)
        
        # Run LLM multiple times and collect responses
        print(f"Calling llama3.2:latest LLM {self.num_runs} times...")
        responses = []
        match_levels = []
        
        run_count = 0
        while run_count < self.num_runs:
            print(f"Run {run_count+1}/{self.num_runs}...")
            
            # Add a small random variation to the prompt to prevent caching
            variation = f"Run ID: {run_count+1}-{random.randint(1000, 9999)}"
            modified_prompt = prompt + f"\n\n# Internal: {variation}"
            
            retry_count = 0
            success = False
            
            # Retry logic for cases where match level can't be extracted
            while retry_count < self.max_retries_per_run and not success:
                try:
                    if retry_count > 0:
                        print(f"  Retry {retry_count}/{self.max_retries_per_run} for run {run_count+1}...")
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
                        if retry_count == self.max_retries_per_run - 1:
                            # If this is our last retry, save the response anyway
                            print(f"  After {self.max_retries_per_run} retries, still couldn't extract match level. Continuing...")
                            responses.append(response)
                    
                    retry_count += 1
                except Exception as e:
                    print(f"Error in Run {run_count+1}: {e}")
                    responses.append(f"ERROR: {e}")
                    retry_count += 1
                    if retry_count == self.max_retries_per_run:
                        print(f"  Failed after {retry_count} retries, continuing to next run")
            
            # Increment run count only if we're done with retries
            run_count += 1
            
            # Add a short delay between runs to ensure we're not hitting any rate limits
            if run_count < self.num_runs:  # Don't delay after the last run
                delay = random.uniform(1.0, 2.0)
                print(f"Waiting {delay:.1f} seconds before next run...")
                time.sleep(delay)
        
        # Process the responses and extract the final results
        if not match_levels:
            return {"error": "No match levels could be extracted"}
        
        return self._process_llm_responses(responses, match_levels)
    
    def _process_llm_responses(self, responses: List[str], match_levels: List[str]) -> Dict[str, Any]:
        """
        Process LLM responses and extract final results.
        
        Args:
            responses: List of raw LLM responses
            match_levels: List of extracted match levels
            
        Returns:
            Dictionary with processed results
        """
        # Determine the lowest match level
        lowest_match = get_lowest_match(match_levels)
        print(f"\nMatch levels from {self.num_runs} runs: {', '.join(match_levels)}")
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
        if lowest_match is not None:
            field_type, content = extract_narrative_or_rationale(lowest_match_response, lowest_match)
        else:
            # Default values if match level is None
            lowest_match = "Unknown"
            field_type, content = "No-go rationale", "Could not determine match level properly"
        
        # Ensure we have valid strings for all parameters
        field_type = field_type or "No-go rationale"
        content = content or "Could not extract content"
        
        return self._apply_domain_analysis(responses, lowest_match, domain_assessment, field_type, content)
    
    def _apply_domain_analysis(self, responses: List[str], lowest_match: str, 
                             domain_assessment: Optional[str], field_type: str, 
                             content: str) -> Dict[str, Any]:
        """
        Apply domain knowledge analysis and adjust match levels if needed.
        
        Args:
            responses: List of raw LLM responses
            lowest_match: Current lowest match level
            domain_assessment: Domain knowledge assessment
            field_type: Type of narrative/rationale field
            content: Content of narrative/rationale
            
        Returns:
            Final processed results dictionary
        """
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
    
    def analyze_job_domain(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job domain and extract domain-specific requirements.
        
        Args:
            job_description: The job description text
            
        Returns:
            Dictionary with domain analysis results
        """
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
        
        return {
            "job_domain": job_domain,
            "domain_specific_requirements": domain_specific_requirements
        }
