#!/usr/bin/env python3
"""
LLM Client module for job matching.

This module handles the interaction with the LLM API (Ollama).
"""
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.utils.llm_client import call_ollama_api, get_llm_client, MockLLMClient

def call_llama3_api(prompt):
    """
    Call the llama3.2 API with a prompt.
    
    Args:
        prompt: The prompt to send to the LLM
        
    Returns:
        The response from the LLM
        
    Raises:
        RuntimeError: If Ollama service is not available or not working properly
    """
    # First check if Ollama is actually available
    client = get_llm_client(force_new=True, model="llama3.2")
    if isinstance(client, MockLLMClient):
        raise RuntimeError(
            "Ollama service is not available or not working properly. "
            "Make sure Ollama is running and the service is accessible."
        )
    
    # Use a higher temperature (0.9) to get more varied responses
    response = call_ollama_api(prompt, model="llama3.2:latest", temperature=0.9)
    
    # Check if the response looks like a mock response
    if "Mock LLM response" in response:
        raise RuntimeError(
            "Received a mock response from the LLM client. "
            "Make sure Ollama is running and the service is accessible."
        )
    
    return response
