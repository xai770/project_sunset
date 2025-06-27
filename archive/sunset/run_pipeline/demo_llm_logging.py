#!/usr/bin/env python3
"""
Simple demo script to showcase LLM dialogue logging functionality.

This script:
1. Sends sample prompts to the LLM
2. Logs both prompts and responses
3. Generates HTML and JSON logs for review
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the dialogue logger functionality
from run_pipeline.utils.logging_llm_client import call_logging_ollama_api

def main():
    """Main function to demonstrate LLM dialogue logging"""
    print("\n" + "="*80)
    print("LLM DIALOGUE LOGGING DEMO")
    print("="*80 + "\n")
    
    print("Sending a series of prompts to the LLM and logging the dialogues...\n")
    
    # Sample 1: Job skills analysis
    prompt1 = """
    You are a career counselor specializing in skills analysis.
    
    Please analyze the following job description and list the top 5 skills required:
    
    Job: Data Scientist
    
    We are looking for a Data Scientist who will help us discover insights from data.
    The ideal candidate is skilled in machine learning, statistical analysis, and
    data visualization. Experience with Python, R, SQL, and big data technologies
    such as Hadoop or Spark is required. The ability to communicate complex findings
    to non-technical stakeholders is essential.
    """
    
    print("Prompt 1: Analyzing Data Scientist job skills...")
    response1 = call_logging_ollama_api(prompt1)
    print("✓ Response received and logged")
    
    # Sample 2: Resume feedback
    prompt2 = """
    You are a professional resume reviewer.
    
    Please review the following resume summary and provide specific feedback on how to improve it:
    
    "Experienced software developer with 5 years of experience in web development.
    Good at coding in JavaScript, HTML, and CSS. Worked on many projects and
    have good communication skills. Team player who can work well with others."
    """
    
    print("\nPrompt 2: Resume feedback...")
    response2 = call_logging_ollama_api(prompt2)
    print("✓ Response received and logged")
    
    # Show where the logs are located
    print("\nAll dialogues have been logged to:")
    log_dir = PROJECT_ROOT / "logs" / "llm_dialogue"
    print(f"- JSON logs: {log_dir}")
    print("  (Open the most recent JSON file to see the raw dialogue data)\n")
    
    # Find the most recent log file
    try:
        log_files = list(log_dir.glob("llm_dialogue_*.json"))
        if log_files:
            latest_log = max(log_files, key=lambda f: os.path.getmtime(f))
            print(f"Latest log file: {latest_log}")
            
            # Show a sample of the logged content
            with open(latest_log, "r") as f:
                log_data = json.load(f)
                print(f"\nTotal dialogues logged: {len(log_data['dialogues'])}")
                print("\nDialogue contents include:")
                print("- Timestamps for each interaction")
                print("- Complete prompts sent to the LLM")
                print("- Full responses received from the LLM")
                print("- Any errors that occurred during processing")
        else:
            print("No log files found. There may have been an error with logging.")
            
    except Exception as e:
        print(f"Error accessing log files: {e}")
    
    print("\nYou can use these logs to analyze the LLM's behavior and improve your prompts.")

if __name__ == "__main__":
    main()
