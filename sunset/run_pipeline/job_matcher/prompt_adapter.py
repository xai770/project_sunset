#!/usr/bin/env python3
"""
Prompt Manager Adapter for job_matcher package.

This module adapts the run_pipeline.utils.prompt_manager to work with
file-based prompts stored in prompts/job_matching/ directory.
"""
import os
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import the existing prompt manager
from run_pipeline.utils.prompt_manager import get_prompt

def get_formatted_prompt(prompt_name: str, category: str = 'job_matching', **kwargs) -> str:
    """
    Load and format a prompt from the prompts directory.
    
    Args:
        prompt_name: The name of the prompt file (without extension)
        category: The category/directory where the prompt is stored
        **kwargs: The variables to use for formatting
        
    Returns:
        The formatted prompt text
    """
    try:
        # Attempt to get the prompt from the existing prompt manager
        # The get_prompt function returns a tuple (prompt_text, version, metadata)
        prompt_result = get_prompt(f"{category}_{prompt_name}")
        
        # Extract the prompt text from the tuple
        if prompt_result and isinstance(prompt_result, tuple) and prompt_result[0]:
            prompt_text = prompt_result[0]
        else:
            prompt_text = None
            
        if not prompt_text:
            # If not found in the prompt manager, try to read from file
            # First try the new location in run_pipeline
            prompt_path = PROJECT_ROOT / "run_pipeline" / "prompts" / category / "v1" / f"{prompt_name}.txt"
            
            if not prompt_path.exists():
                # Try the old location
                prompt_path = PROJECT_ROOT / "prompts" / category / "v1" / f"{prompt_name}.txt"
            
            if not prompt_path.exists():
                # Fall back to default prompt if all else fails
                if prompt_name == 'llama3_cv_match':
                    from run_pipeline.job_matcher.default_prompt import LLAMA3_PROMPT
                    return LLAMA3_PROMPT.format(**kwargs)
                else:
                    raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_text = f.read()
    except Exception as e:
        print(f"Warning: Could not load prompt '{prompt_name}' from prompt manager: {e}")
        # Fall back to default prompt if system manager fails
        if prompt_name == 'llama3_cv_match':
            from run_pipeline.job_matcher.default_prompt import LLAMA3_PROMPT
            return LLAMA3_PROMPT.format(**kwargs)
        else:
            raise ValueError(f"No default prompt available for '{prompt_name}'")
    
    # Format the prompt with the provided variables
    try:
        return prompt_text.format(**kwargs)
    except Exception as e:
        print(f"Error formatting prompt: {e}")
        # In case of formatting errors, return the unformatted prompt
        return prompt_text

def list_available_prompts() -> dict:
    """
    List all available prompts in the prompts directory.
    
    Returns:
        Dictionary mapping categories to lists of (prompt_name, version) tuples
    """
    available_prompts: dict[str, list[tuple[str, str]]] = {}
    
    # Check prompt directories
    prompts_dir = PROJECT_ROOT / "prompts"
    if not prompts_dir.exists():
        return {"job_matching": [("llama3_cv_match", "default")]}
    
    # Look for subdirectories (categories)
    for category_dir in prompts_dir.iterdir():
        if category_dir.is_dir():
            category_name = category_dir.name
            available_prompts[category_name] = []
            
            # Look for version directories
            for version_dir in category_dir.iterdir():
                if version_dir.is_dir():
                    version = version_dir.name
                    
                    # Look for prompt files
                    for prompt_file in version_dir.iterdir():
                        if prompt_file.suffix == '.txt':
                            prompt_name = prompt_file.stem
                            available_prompts[category_name].append((prompt_name, version))
    
    # If no prompts found, return defaults
    if not available_prompts:
        return {"job_matching": [("llama3_cv_match", "default")]}
        
    return available_prompts
