#!/usr/bin/env python3
"""
Direct cleaner test to find what's going wrong with Ollama extraction
"""
import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Set up basic logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ollama_test')

# Get the current project root
PROJECT_ROOT = Path(__file__).resolve().parent

def test_ollama_direct():
    """Test extraction directly with ollama to debug"""
    # Check if ollama is available
    try:
        result = subprocess.run(
            ["ollama", "list"], 
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Ollama not available: {result.stderr}")
            return False
        else:
            logger.info(f"Available models: {result.stdout}")
    except Exception as e:
        logger.error(f"Error checking ollama: {str(e)}")
        return False

    # Set the models to use - select a variety of models to test
    models = ["llama3.2:latest", "mistral:latest", "gemma3:4b"]
    logger.info(f"Testing Ollama extraction with models: {', '.join(models)}")

    # Get the test job file
    job_id = "55263"
    html_content_dir = PROJECT_ROOT / "data" / "postings" / "html_content"
    html_content_file = html_content_dir / f"db_job_{job_id}_content.txt"

    if not os.path.exists(html_content_file):
        logger.error(f"HTML content file not found: {html_content_file}")
        return False

    # Read the HTML content
    with open(html_content_file, 'r', encoding='utf-8') as f:
        job_content = f.read()

    logger.info(f"Full content length: {len(job_content)} characters")

    # No longer truncate content as per user request
    logger.info("Using full job content without truncation")

    # Create a specialized prompt for extraction that preserves more content
    prompt = f"""Extract ONLY the English version of this job description from Deutsche Bank. 

Please:
1. Remove all German text completely
2. Remove all website navigation elements and menus
3. Remove company marketing content and benefits sections
4. Remove all HTML formatting and unnecessary whitespace
5. Preserve the exact original wording of the job title, location, responsibilities, and requirements
6. Maintain the contact information
7. Keep the original structure (headings, bullet points) of the core job description
8. Double check that you remove all sections and wordings discussing the company culture, benefits, values, and mission statement

The result should be a clean, professional job description in English only, with all the essential information about the position preserved exactly as written.

Job posting content:
{job_content}"""

    # Test all selected models
    success = True
    output_dir = PROJECT_ROOT / "data" / "test_results" / "ollama_test"
    os.makedirs(output_dir, exist_ok=True)
    
    # Variable to track overall success
    overall_success = True
    
    # Create directory for saving results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = PROJECT_ROOT / "data" / "test_results" / f"model_comparison_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each model
    for model in models:
        logger.info(f"Testing model: {model}")
        print(f"\n\n======= Testing model: {model} =======")
        
        try:
            # Run ollama with the prompt
            result = subprocess.run(
                ["ollama", "run", model, prompt], 
                capture_output=True, 
                text=True, 
                timeout=180  # 3 minute timeout
            )

            # Check if extraction was successful
            if result.returncode == 0 and result.stdout:
                response = result.stdout.strip()
                
                # Log the result
                print("\nOllama Response:")
                print("=" * 50)
                print(response)
                print("=" * 50)
                
                logger.info(f"Response length: {len(response)} characters")

                # Save the response for reference
                model_output_file = output_dir / f"{model}_response.txt"
                with open(model_output_file, 'w', encoding='utf-8') as f:
                    f.write(response)
                
                # Also save as JSON
                json_output_file = output_dir / f"{model}_response.json"
                with open(json_output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "job_id": job_id, 
                        "model": model,
                        "response": response
                    }, f, indent=2, ensure_ascii=False)
                    
                logger.info(f"Response saved to: {model_output_file}")
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logger.error(f"{model}: Ollama error: {error_msg}")
                overall_success = False
        except subprocess.TimeoutExpired:
            logger.error(f"{model}: Ollama extraction timed out")
            overall_success = False
        except Exception as e:
            logger.error(f"{model}: Error running Ollama: {str(e)}")
            overall_success = False
    
    logger.info(f"All models tested. Results saved to: {output_dir}")
    return overall_success

if __name__ == "__main__":
    success = test_ollama_direct()
    sys.exit(0 if success else 1)
