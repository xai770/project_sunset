#!/usr/bin/env python3
"""
Debug script for the job description cleaner module
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import modules
from run_pipeline.utils.logging_utils import setup_logger, create_timestamped_dir
from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR, LOG_BASE_DIR

# Set up basic logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cleaner_debug')

def debug_extraction():
    """Debug the extraction process"""
    # Set up logging
    log_dir = create_timestamped_dir(LOG_BASE_DIR, "cleaner_debug")
    logger, log_file = setup_logger("cleaner_debug", log_dir)
    
    # Job details
    job_id = "55263"
    job_path = JOB_DATA_DIR / f"job{job_id}.json"
    
    print(f"Debug log: {log_file}")
    print(f"Processing job: {job_path}")
    
    try:
        # Read job data
        with open(job_path, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
        
        # Get title
        job_title = job_data.get("title", f"Job {job_id}")
        print(f"Job title: {job_title}")
        
        # Try to get HTML content
        content_file = PROJECT_ROOT / "data" / "postings" / "html_content" / f"db_job_{job_id}_content.txt"
        print(f"Content file path: {content_file}")
        print(f"Content file exists: {content_file.exists()}")
        
        # Read the content
        with open(content_file, 'r', encoding='utf-8') as f:
            job_content = f.read()
            
        print(f"Content length: {len(job_content)} characters")
        print(f"Content preview: {job_content[:200]}...\n")
        
        # Set the models to use - same as in test_direct_ollama.py
        models = ["llama3.2:latest", "mistral:latest", "gemma3:4b"]
        print(f"Testing Ollama extraction with models: {', '.join(models)}")
        
        # Create directory for saving results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = PROJECT_ROOT / "data" / "test_results" / f"model_comparison_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        print(f"Results will be saved to: {output_dir}")
        
        # Create the prompt - same as in test_direct_ollama.py
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

        # Variable to track overall success
        overall_success = True
        
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
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_extraction()
    sys.exit(0 if success else 1)
