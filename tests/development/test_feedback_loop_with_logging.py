#!/usr/bin/env python3
"""
Test script to verify the new feedback loop and prompt management functionality
with LLM dialogue logging.

This script performs the same tests as test_feedback_loop.py but uses
the logging LLM client to record all interactions with the LLM.
"""
import os
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the original test script
import test_feedback_loop

# Import the logging LLM client
from run_pipeline.utils.logging_llm_client import get_logging_llm_client, call_logging_ollama_api

# Patch the LLM client functions to use our logging versions
def setup_logging_llm_client():
    """Patch the llm_client module to use our logging versions"""
    import run_pipeline.utils.llm_client as llm_client
    
    # Save original functions
    original_get_llm_client = llm_client.get_llm_client
    original_call_ollama_api = llm_client.call_ollama_api
    
    # Replace with logging versions
    llm_client.get_llm_client = get_logging_llm_client
    llm_client.call_ollama_api = call_logging_ollama_api
    
    print("LLM client patched to use logging versions")
    print("Dialogue logs will be saved in logs/llm_dialogue/")
    
    return original_get_llm_client, original_call_ollama_api

def teardown_logging_llm_client(originals):
    """Restore the original LLM client functions"""
    import run_pipeline.utils.llm_client as llm_client
    
    original_get_llm_client, original_call_ollama_api = originals
    llm_client.get_llm_client = original_get_llm_client
    llm_client.call_ollama_api = original_call_ollama_api

if __name__ == "__main__":
    # Patch the LLM client functions
    original_functions = setup_logging_llm_client()
    
    try:
        # Run the original main function
        sys.exit(test_feedback_loop.main())
    finally:
        # Restore original functions
        teardown_logging_llm_client(original_functions)
