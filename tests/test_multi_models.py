#!/usr/bin/env python3
"""
Test job extraction with multiple Ollama models for comparison
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
logger = logging.getLogger('ollama_multi_test')

# Get the current project root
PROJECT_ROOT = Path(__file__).resolve().parent

def test_multiple_models():
    """Test job extraction with multiple Ollama models"""
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
            available_models = result.stdout.strip()
            logger.info(f"Available models: {available_models}")
    except Exception as e:
        logger.error(f"Error checking ollama: {str(e)}")
        return False

    # Models to test - select diverse models with different sizes

# "lets test all of our models:

    models = [
        "phi3",           # 2.2 GB
        "llama3",         # 4.7 GB
        "mistral",        # 4.1 GB
        "phi4-mini-reasoning",  # 3.2 GB
        "qwen3:4b",       # 2.6 GB
        "gemma3:4b",      # 3.3 GB
    ]
    logger.info(f"Testing {len(models)} Ollama models: {', '.join(models)}")

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

    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = PROJECT_ROOT / "data" / "test_results" / f"model_comparison_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Summary of results
    summary = {
        "job_id": job_id,
        "models_tested": models,
        "test_timestamp": timestamp,
        "results": {}
    }
    
    # Test each model
    for model in models:
        model_success = False
        logger.info(f"Testing model: {model}")
        print(f"\n\n{'=' * 20} Testing model: {model} {'=' * 20}")
        
        try:
            # Run ollama with the prompt and a longer timeout for larger models
            start_time = datetime.now()
            result = subprocess.run(
                ["ollama", "run", model, prompt], 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minute timeout
            )
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            # Check if extraction was successful
            if result.returncode == 0 and result.stdout:
                response = result.stdout.strip()
                
                # Log the result
                print("\nResponse:")
                print("-" * 80)
                print(response)
                print("-" * 80)
                
                response_length = len(response)
                logger.info(f"{model}: Response length: {response_length} characters, processing time: {processing_time:.2f} seconds")

                # Save the response for reference
                model_output_file = output_dir / f"{model}_response.txt"
                with open(model_output_file, 'w', encoding='utf-8') as f:
                    f.write(response)
                
                # Update summary
                summary["results"][model] = {
                    "success": True,
                    "response_length": response_length,
                    "processing_time_seconds": round(processing_time, 2),
                    "output_file": str(model_output_file)
                }
                
                model_success = True
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logger.error(f"{model}: Ollama error: {error_msg}")
                
                # Update summary
                summary["results"][model] = {
                    "success": False,
                    "error": error_msg,
                    "processing_time_seconds": round(processing_time, 2)
                }
        except subprocess.TimeoutExpired:
            logger.error(f"{model}: Ollama extraction timed out after 5 minutes")
            summary["results"][model] = {
                "success": False,
                "error": "Timeout after 5 minutes"
            }
        except Exception as e:
            logger.error(f"{model}: Error running Ollama: {str(e)}")
            summary["results"][model] = {
                "success": False,
                "error": str(e)
            }
    
    # Save summary
    summary_file = output_dir / "comparison_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Model comparison complete. Results saved to: {output_dir}")
    print(f"\nModel comparison complete. Results saved to: {output_dir}")
    
    # Count successful models
    successful_models = sum(1 for model_result in summary["results"].values() if model_result.get("success", False))
    logger.info(f"Successful models: {successful_models} out of {len(models)}")
    
    return successful_models > 0

if __name__ == "__main__":
    success = test_multiple_models()
    sys.exit(0 if success else 1)
