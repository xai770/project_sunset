#!/usr/bin/env python3
"""
Sample script demonstrating how to log LLM dialogues.

This script sends a simple prompt to the LLM and logs the dialogue.
"""
import os
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the logging LLM client
from run_pipeline.utils.logging_llm_client import call_logging_ollama_api

def main():
    """Main function"""
    print("Sending test prompt to LLM with logging enabled...")
    
    # Define a simple test prompt
    prompt = """
    You are a job matching assistant.
    
    Please analyze the following job description and provide three key requirements:
    
    Job Title: Senior Python Developer
    
    We are looking for an experienced Python developer with at least 5 years of experience
    in building web applications using Django. The ideal candidate will have experience
    with containerization, CI/CD pipelines, and cloud deployment (preferably AWS).
    Experience with data analysis and machine learning is a plus.
    
    The candidate should be comfortable working in an Agile environment and have good
    communication skills.
    """
    
    # Send the prompt to the LLM
    response = call_logging_ollama_api(prompt)
    
    # Print the response
    print("\nLLM Response:\n")
    print(response)
    
    # Print information about log location
    print("\nThe dialogue has been logged to the logs/llm_dialogue/ directory")
    print("Check the most recent .json and .html files for the dialogue details.")

if __name__ == "__main__":
    main()
