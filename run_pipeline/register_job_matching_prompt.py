#!/usr/bin/env python3
"""
Script to register the job matching prompt with the prompt manager system.
"""
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.utils.prompt_manager import add_prompt_version, get_prompt

def register_job_matching_prompt():
    """Register the job matching prompt with the prompt manager system."""
    # Path to the prompt file
    prompt_path = PROJECT_ROOT / "run_pipeline" / "prompts" / "job_matching" / "v1" / "llama3_cv_match.txt"
    
    # Read the prompt file
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_text = f.read()
    
    # Add the prompt to the prompt manager
    prompt_type = "job_matching_llama3_cv_match"
    version = add_prompt_version(
        prompt_type=prompt_type,
        prompt_text=prompt_text,
        description="Job matching prompt for CV-to-role matching using llama3",
        author="Migration Script",
        set_active=True
    )
    
    print(f"Registered job matching prompt as {prompt_type} version {version}")
    
    # Verify that we can retrieve it
    prompt_result = get_prompt(prompt_type)
    if prompt_result and prompt_result[0]:
        print("Successfully retrieved prompt from the prompt manager")
    else:
        print("Failed to retrieve prompt from the prompt manager")

if __name__ == "__main__":
    register_job_matching_prompt()
