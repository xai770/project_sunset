#!/usr/bin/env python3
"""
Test script to diagnose job decomposition issues with Ollama
"""

import requests
import json
import sys
import time
import os
from pathlib import Path

# Settings from config
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:latest"

# Base directories (matching config.py)
BASE_DIR = Path(os.environ.get("SUNSET_BASE_DIR", "/home/xai/Documents/sunset"))
DATA_DIR = BASE_DIR / "data"
postings_DIR = DATA_DIR / "postings"

def load_job_posting(job_id):
    """Load job posting data from file"""
    job_file = postings_DIR / f"job{job_id}_full.json"
    if not job_file.exists():
        print(f"Job file not found: {job_file}")
        return None
    
    try:
        with open(job_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading job file: {e}")
        return None

def create_job_decomposition_prompt(job_data):
    """Create a prompt for job decomposition (simplified version)"""
    job_title = job_data.get("title", "Unknown position")
    job_description = job_data.get("description", "")
    
    # Create a simplified prompt similar to what the skill decomposer would use
    prompt = f"""Analyze the following job description and extract key requirements:

Job Title: {job_title}

Description:
{job_description}

Please identify the top 5 key requirements for this job."""
    
    return prompt

def test_job_decomposition(job_id, timeout=120):
    """Test job decomposition with Ollama"""
    print(f"Testing job decomposition for job ID {job_id} with {timeout}s timeout...")
    
    # Load job data
    job_data = load_job_posting(job_id)
    if not job_data:
        return False
    
    # Create prompt
    prompt = create_job_decomposition_prompt(job_data)
    print(f"\nPrompt length: {len(prompt)} characters")
    
    # Test with Ollama
    try:
        url = f"{OLLAMA_HOST}/api/generate"
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 1000  # Limiting response size
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"Sending request to Ollama (timeout: {timeout}s)...")
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        end_time = time.time()
        
        elapsed = end_time - start_time
        print(f"Request completed in {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")
            print(f"\nResponse snippet:")
            print(response_text[:300] + "..." if len(response_text) > 300 else response_text)
            print("\n✓ Successfully processed job decomposition")
            return True
        else:
            print(f"✗ Failed to process: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ReadTimeout:
        print(f"✗ Request timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"✗ Error during request: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_job_decomposition.py JOB_ID [TIMEOUT]")
        print("Example: python test_job_decomposition.py 62675 120")
        sys.exit(1)
    
    job_id = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    
    test_job_decomposition(job_id, timeout)

if __name__ == "__main__":
    main()