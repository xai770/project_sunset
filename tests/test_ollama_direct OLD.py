#!/usr/bin/env python3
"""
Simple test script to directly interact with Ollama using a simplified job content
"""

import subprocess
import json
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

def test_ollama_extraction(model="phi3", use_shortened_content=True):
    """
    Test direct extraction with Ollama using minimal job content
    
    Args:
        model (str): Ollama model to use
        use_shortened_content (bool): Whether to use a shortened version of the job content
    """
    print(f"Testing Ollama extraction with model: {model}")
    
    try:
        # Get job content from the file
        job_file_path = PROJECT_ROOT / "data" / "postings" / "html_content" / "db_job_55263_content.txt"
        
        if not job_file_path.exists():
            print(f"Job content file not found: {job_file_path}")
            return False
        
        with open(job_file_path, 'r', encoding='utf-8') as f:
            job_content = f.read()
            
        print(f"Full content length: {len(job_content)} characters")
        
        # Create a shortened version if needed
        if use_shortened_content:
            lines = job_content.split("\n")
            # Take just enough lines to capture the essence but keep it small
            # Start after navigation elements and take key sections
            start_idx = 0
            for i, line in enumerate(lines):
                if "Position Overview" in line:
                    start_idx = i
                    break
            
            # Get about 100 lines which should be manageable
            shortened_content = "\n".join(lines[start_idx:start_idx+100])
            print(f"Shortened content length: {len(shortened_content)} characters")
            content_to_use = shortened_content
        else:
            content_to_use = job_content
        
        # Create the prompt for Ollama
        prompt = f"""Extract ONLY the essential job details from this Deutsche Bank job posting into an EXTREMELY concise format. 
Include ONLY the following in brief form:
1. Job title and location (one line)
2. Job ID and posting date (one line)
3. 3-5 core responsibilities as very short bullet points
4. 3-5 key requirements as very short bullet points
5. Contact information (one line)

BE EXTREMELY BRIEF - use the shortest phrases possible while maintaining clarity.
OMIT all marketing content, explanatory text, and non-essential information.
FORMAT as plain text with section headers.

YOUR RESPONSE MUST BE UNDER 500 CHARACTERS TOTAL.

Job posting content:
{content_to_use}"""

        print("Sending request to Ollama...")
        
        # Run Ollama with the prompt
        result = subprocess.run(
            ["ollama", "run", model, prompt], 
            capture_output=True, 
            text=True, 
            timeout=120  # 2 minutes timeout
        )
        
        # Check if extraction was successful
        if result.returncode == 0 and result.stdout:
            response = result.stdout.strip()
            
            print("\nOllama Response:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            print(f"Response length: {len(response)} characters")
            
            # Save the output to a file
            output_dir = PROJECT_ROOT / "data" / "test_results" / "ollama_test"
            os.makedirs(output_dir, exist_ok=True)
            output_file = output_dir / "direct_ollama_response.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "prompt": prompt,
                    "model": model,
                    "response": response,
                    "response_length": len(response)
                }, f, indent=2, ensure_ascii=False)
                
            print(f"Response saved to: {output_file}")
            return True
        else:
            print(f"Ollama error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("Ollama extraction timed out")
        return False
    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Ollama Extraction")
    parser.add_argument("--model", type=str, default="phi3", help="Model to use (default: phi3)")
    parser.add_argument("--full-content", action="store_true", help="Use the full content instead of shortened version")
    
    args = parser.parse_args()
    
    # Check if Ollama is available
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        print(f"Available models: {result.stdout.strip()}")
    except Exception as e:
        print(f"Warning: Ollama may not be installed or accessible: {str(e)}")
        print("You can install Ollama from: https://ollama.com/")
        exit(1)
    
    # Run the test
    test_ollama_extraction(args.model, not args.full_content)
