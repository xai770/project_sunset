#!/usr/bin/env python3
"""
Comprehensive test script to verify job matching and Excel export with the new simplified prompt.
"""
import sys
import json
import os
from pathlib import Path
import shutil

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.job_matcher.job_processor import process_job, update_job_json
from run_pipeline.export_job_matches import export_job_matches
from run_pipeline.config.paths import JOB_DATA_DIR

# Test problematic job IDs
TEST_JOB_IDS = [61907, 63587, 63625]

def setup_test_environment():
    """Setup the test environment"""
    # Ensure job data directory exists
    output_dir = PROJECT_ROOT / "output" / "test_run"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def run_tests():
    """Run tests on the problematic job IDs"""
    output_dir = setup_test_environment()
    print(f"Testing job matching with simplified prompt on {len(TEST_JOB_IDS)} problematic job IDs...")
    
    # Load CV text using the cv_loader module
    from run_pipeline.job_matcher.cv_loader import load_cv_text
    cv_text = load_cv_text()
    
    results = {}
    
    # Process each job
    for job_id in TEST_JOB_IDS:
        print(f"\n\nProcessing job {job_id}...")
        job_result = process_job(str(job_id), cv_text, num_runs=2, dump_input=True)
        
        # Store results
        results[job_id] = {
            "cv_to_role_match": job_result.get("cv_to_role_match", "Unknown"),
            "domain_knowledge_assessment": job_result.get("domain_knowledge_assessment", "")
        }
        
        # Add narrative or rationale
        if job_result.get("Application narrative"):
            results[job_id]["narrative"] = job_result.get("Application narrative")
        elif job_result.get("No-go rationale"):
            results[job_id]["rationale"] = job_result.get("No-go rationale")
        
        # Update job JSON
        update_job_json(str(job_id), job_result)
    
    # Print summary
    print("\n\n=== TEST RESULTS SUMMARY ===")
    for job_id, result in results.items():
        print(f"Job {job_id}: {result.get('cv_to_role_match')} match")
    
    # Export results to Excel with feedback system format
    print("\nExporting results to Excel with feedback system format...")
    
    # Work around the job ID issue by creating a direct list including all job IDs
    job_list = []
    for job_id in TEST_JOB_IDS:
        job_path = os.path.join(JOB_DATA_DIR, f"job{job_id}.json")
        if os.path.exists(job_path):
            with open(job_path, 'r', encoding='utf-8') as f:
                try:
                    job_data = json.load(f)
                    job_list.append(job_data)
                except Exception as e:
                    print(f"Error loading job {job_id}: {e}")
    
    # Create output directory if it doesn't exist
    output_file = str(output_dir / "job_matches_test.xlsx")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Custom export function for testing
    from run_pipeline.export_job_matches import extract_job_data_for_feedback_system, initialize_logging_columns, export_to_excel_feedback_system
    
    if job_list:
        matches = []
        timestamp = "test_run"
        for job_data in job_list:
            job_match = extract_job_data_for_feedback_system(job_data)
            logging_cols = initialize_logging_columns(timestamp)
            matches.append({**job_match, **logging_cols})
        
        export_to_excel_feedback_system(matches, output_file)
        excel_path = output_file
        print(f"Created Excel file: {excel_path}")
    else:
        print("No job data found to export")
        excel_path = None
    
    if excel_path:
        print(f"Excel export successful: {excel_path}")
        print("\nVerifying Excel export columns...")
        
        # Import pandas to check Excel file
        try:
            import pandas as pd
            df = pd.read_excel(excel_path)
            
            # Check key columns
            print("\nExcel file columns:")
            for column in df.columns:
                print(f"- {column}: {'NOT EMPTY' if df[column].notna().any() else 'EMPTY'}")
            
            # Check specific columns that were problematic
            problem_columns = ['Job domain', 'Application narrative', 'No-go rationale', 'generate_cover_letters_log']
            print("\nProblem column check:")
            for col in problem_columns:
                if col in df.columns:
                    empty_count = df[col].isna().sum()
                    print(f"- {col}: {len(df) - empty_count}/{len(df)} rows have data")
                else:
                    print(f"- {col}: Column not found in export")
            
        except ImportError:
            print("Warning: pandas not available for Excel verification")
    else:
        print("Error: Excel export failed")
    
    return excel_path

if __name__ == "__main__":
    run_tests()
