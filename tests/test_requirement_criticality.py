#!/usr/bin/env python3
"""
Test script to evaluate job requirements and classify them as critical vs nice-to-have.
This script uses Ollama to assess the criticality of each requirement for a job.
"""

import os
import sys
import json
import requests
from tabulate import tabulate
from pprint import pprint

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import relevant modules
from scripts.utils.skill_decomposer.matching import find_skill_matches
from scripts.utils.skill_decomposer.domain_overlap_rater import _get_llm_domain_overlap
from scripts.utils.skill_decomposer.persistence import load_job_data

# Ollama API settings
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"  # Using llama3.2 model

# Cache for requirement criticality to avoid multiple API calls
criticality_cache = {}

def evaluate_requirement_criticality(job_title, job_description, requirement):
    """
    Use Ollama to evaluate how critical a requirement is for a job.
    
    Args:
        job_title: Title of the job
        job_description: Brief description of the job
        requirement: The specific skill requirement to evaluate
        
    Returns:
        Dict with criticality score (0-1) and classification
    """
    # Check cache first
    cache_key = f"{job_title}|{requirement}"
    if cache_key in criticality_cache:
        return criticality_cache[cache_key]
    
    prompt = f"""You are an experienced hiring manager evaluating job requirements.
For this job: "{job_title}", determine if the following skill requirement is CRITICAL (must-have) or NICE-TO-HAVE.

Job description summary: {job_description}

Skill requirement to evaluate: {requirement}

Consider a skill CRITICAL (must-have) if:
- It's a core competency for the job
- No equivalent substitute exists
- Job performance would be impossible without it
- It requires specialized education/training
- It's mentioned as "required" or "essential"

Consider a skill NICE-TO-HAVE if:
- Alternative skills could substitute for it
- It enhances performance but isn't essential
- It can be learned on the job
- It's mentioned as "preferred" or "desired"

Please rate on a scale of 0.0 to 1.0 how CRITICAL this requirement is:
- 0.0-0.3: Definitely nice-to-have
- 0.4-0.6: Somewhat important
- 0.7-0.9: Very important
- 1.0: Absolutely critical, non-negotiable

Return ONLY a numerical score between 0.0 and 1.0."""
    
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,
                "max_tokens": 10
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            # Extract score from response
            numeric_chars = ''.join([c for c in response_text if c.isdigit() or c == '.'])
            if numeric_chars:
                try:
                    score = float(numeric_chars)
                    # Normalize to 0-1 if necessary
                    if score > 1.0:
                        score /= 100.0
                    score = min(1.0, max(0.0, score))
                    
                    # Classify based on score
                    if score >= 0.7:
                        classification = "CRITICAL"
                    elif score >= 0.4:
                        classification = "IMPORTANT"
                    else:
                        classification = "NICE-TO-HAVE"
                        
                    result = {
                        "requirement": requirement,
                        "criticality_score": score,
                        "classification": classification
                    }
                    
                    # Cache the result
                    criticality_cache[cache_key] = result
                    return result
                    
                except ValueError:
                    print(f"Failed to parse response: {response_text}")
        
        # Default if API call fails
        return {
            "requirement": requirement,
            "criticality_score": 0.5,
            "classification": "IMPORTANT",
            "error": "Failed to evaluate criticality"
        }
        
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        # Default if exception occurs
        return {
            "requirement": requirement, 
            "criticality_score": 0.5,
            "classification": "IMPORTANT",
            "error": str(e)
        }

def evaluate_job_requirements(job_id):
    """
    Evaluate all requirements for a specific job.
    
    Args:
        job_id: ID of the job to evaluate
        
    Returns:
        List of requirements with criticality assessments
    """
    # Load job data
    job_data = load_job_data(job_id)
    if not job_data or "requirements" not in job_data:
        print(f"No requirements found for job {job_id}")
        return []
    
    # Extract requirements from job data
    job_requirements = []
    if "complex_requirements" in job_data["requirements"]:
        job_requirements = job_data["requirements"]["complex_requirements"]
    
    if not job_requirements:
        print(f"No requirements found for job {job_id}")
        return []
    
    # Get job title and description
    job_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'data', 'postings', f'job{job_id}.json'
    )
    
    job_title = "Unknown Job"
    job_description = "No description available"
    
    try:
        with open(job_file_path, 'r') as f:
            job_data = json.load(f)
            job_title = job_data.get('title', 'Unknown Job')
            # Try to get a useful description
            if 'sections' in job_data:
                for section in job_data['sections']:
                    if section.get('type') in ['job_description', 'description', 'about_role', 'responsibilities']:
                        job_description = section.get('content', '')[:300]  # Truncate for API context limits
                        break
    except Exception as e:
        print(f"Error loading job details: {e}")
    
    print(f"Evaluating requirements for job {job_id}: {job_title}")
    print(f"Description preview: {job_description[:100]}...")
    
    # Evaluate each requirement
    evaluated_requirements = []
    for req in job_requirements:
        req_name = req.get('name', '')
        if not req_name:
            continue
            
        print(f"Evaluating requirement: {req_name}")
        evaluation = evaluate_requirement_criticality(job_title, job_description, req_name)
        evaluated_requirements.append(evaluation)
        print(f"  Classification: {evaluation['classification']} (Score: {evaluation['criticality_score']:.2f})")
    
    # Sort by criticality score
    evaluated_requirements.sort(key=lambda x: x.get('criticality_score', 0), reverse=True)
    return evaluated_requirements

def process_all_requirements_and_save():
    """
    Process all job requirements for all jobs and save to a JSON file.
    """
    job_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'postings')
    job_files = [f for f in os.listdir(job_dir) if f.startswith("job") and f.endswith(".json")]
    
    all_job_criticality = {}
    
    for job_file in job_files:
        job_id = job_file.replace("job", "").replace(".json", "")
        print(f"\nProcessing job {job_id}...")
        
        evaluated_reqs = evaluate_job_requirements(job_id)
        if evaluated_reqs:
            all_job_criticality[job_id] = {
                "requirements": evaluated_reqs,
                "critical_count": sum(1 for r in evaluated_reqs if r.get('classification') == "CRITICAL"),
                "important_count": sum(1 for r in evaluated_reqs if r.get('classification') == "IMPORTANT"),
                "nice_to_have_count": sum(1 for r in evaluated_reqs if r.get('classification') == "NICE-TO-HAVE")
            }
    
    # Save to file
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'requirement_criticality.json')
    with open(output_path, 'w') as f:
        json.dump(all_job_criticality, f, indent=2)
    
    print(f"\nSaved requirement criticality data to {output_path}")
    return all_job_criticality

def display_job_criticality_summary(job_criticality_data):
    """
    Display a summary of job requirement criticality.
    """
    headers = ["Job ID", "Critical", "Important", "Nice-to-Have", "Total"]
    table_data = []
    
    for job_id, data in job_criticality_data.items():
        critical_count = data.get('critical_count', 0)
        important_count = data.get('important_count', 0)
        nice_to_have_count = data.get('nice_to_have_count', 0)
        total_count = critical_count + important_count + nice_to_have_count
        
        table_data.append([
            job_id,
            f"{critical_count} ({critical_count/total_count*100:.1f}%)" if total_count else "0",
            f"{important_count} ({important_count/total_count*100:.1f}%)" if total_count else "0",
            f"{nice_to_have_count} ({nice_to_have_count/total_count*100:.1f}%)" if total_count else "0",
            total_count
        ])
    
    print("\nRequirement Criticality Summary:")
    print(tabulate(table_data, headers=headers, tablefmt="pretty"))

def test_specific_requirements():
    """
    Test a specific set of requirements to see how they're classified.
    """
    test_cases = [
        {
            "job_title": "Senior Tax Accountant",
            "description": "Responsible for preparing and filing tax returns, providing tax advice, and ensuring compliance with tax laws.",
            "requirements": [
                "Tax Compliance",
                "CPA Certification",
                "Microsoft Office Skills",
                "Team Leadership",
                "German Language Proficiency"
            ]
        },
        {
            "job_title": "Software Engineer",
            "description": "Develop and maintain software applications, collaborate with cross-functional teams, and implement new features.",
            "requirements": [
                "Python Programming",
                "JavaScript Experience",
                "AWS Knowledge",
                "Bachelor's Degree in Computer Science",
                "Communication Skills"
            ]
        },
        {
            "job_title": "Site Reliability Engineer",
            "description": "Ensure system reliability, implement automation for deployment and operations, and manage infrastructure.",
            "requirements": [
                "DevOps Experience",
                "Kubernetes",
                "CI/CD Pipeline Management",
                "Linux Administration",
                "Documentation Skills"
            ]
        }
    ]
    
    results = []
    
    for case in test_cases:
        job_title = case["job_title"]
        description = case["description"]
        print(f"\nEvaluating test case: {job_title}")
        
        job_results = []
        for req in case["requirements"]:
            evaluation = evaluate_requirement_criticality(job_title, description, req)
            job_results.append(evaluation)
            print(f"  {req}: {evaluation['classification']} (Score: {evaluation['criticality_score']:.2f})")
        
        # Sort by criticality
        job_results.sort(key=lambda x: x.get('criticality_score', 0), reverse=True)
        results.append({
            "job_title": job_title,
            "requirements": job_results
        })
    
    print("\nTest Results Summary:")
    for job_result in results:
        print(f"\n{job_result['job_title']}:")
        headers = ["Requirement", "Classification", "Score"]
        table_data = [[r['requirement'], r['classification'], f"{r['criticality_score']:.2f}"] for r in job_result['requirements']]
        print(tabulate(table_data, headers=headers, tablefmt="pretty"))

def evaluate_real_job(job_id):
    """
    Evaluate requirements for a specific real job.
    """
    evaluated_reqs = evaluate_job_requirements(job_id)
    
    if not evaluated_reqs:
        print(f"No requirements found or evaluated for job {job_id}")
        return
    
    print("\nRequirement Criticality Results:")
    headers = ["Requirement", "Classification", "Score"]
    table_data = [[r['requirement'], r['classification'], f"{r['criticality_score']:.2f}"] for r in evaluated_reqs]
    print(tabulate(table_data, headers=headers, tablefmt="pretty"))
    
    # Print summary
    critical_count = sum(1 for r in evaluated_reqs if r.get('classification') == "CRITICAL")
    important_count = sum(1 for r in evaluated_reqs if r.get('classification') == "IMPORTANT")
    nice_to_have_count = sum(1 for r in evaluated_reqs if r.get('classification') == "NICE-TO-HAVE")
    total_count = len(evaluated_reqs)
    
    print("\nSummary:")
    print(f"Critical requirements: {critical_count}/{total_count} ({critical_count/total_count*100:.1f}%)")
    print(f"Important requirements: {important_count}/{total_count} ({important_count/total_count*100:.1f}%)")
    print(f"Nice-to-have requirements: {nice_to_have_count}/{total_count} ({nice_to_have_count/total_count*100:.1f}%)")

if __name__ == "__main__":
    # Set environment variables for LLM API
    os.environ["LLM_API_ENABLED"] = "true"
    os.environ["LLM_API_MODEL"] = OLLAMA_MODEL
    os.environ["LLM_API_URL"] = OLLAMA_API_URL
    
    print("Test script for evaluating job requirement criticality")
    print("======================================================")
    
    # Process command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            # Process all jobs
            all_job_data = process_all_requirements_and_save()
            display_job_criticality_summary(all_job_data)
        elif sys.argv[1] == "--test":
            # Run test cases
            test_specific_requirements()
        else:
            # Process specific job ID
            job_id = sys.argv[1]
            evaluate_real_job(job_id)
    else:
        # Default to running the tax job test case
        print("Running test cases and evaluating the tax job (ID: 61964)...")
        test_specific_requirements()
        print("\nNow evaluating the actual tax job...")
        evaluate_real_job("61964")