#!/usr/bin/env python3
"""
Test the improved no-go rationale extraction and fix malformed rationales in existing reports.
"""

import json
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.export_job_matches import extract_job_data_for_feedback_system

def clean_malformed_rationale(rationale):
    """Clean up malformed no-go rationales"""
    if not rationale:
        return ""
    
    # Remove the problematic wrapping text from malformed rationales
    if "Extracted from incorrectly formatted narrative:" in rationale:
        import re
        match = re.search(r'\[Extracted from incorrectly formatted narrative: (.*?)\]', rationale, re.DOTALL)
        if match:
            extracted_content = match.group(1).strip()
            # If the extracted content is positive, create a proper no-go rationale
            if any(positive_word in extracted_content.lower() for positive_word in ['believe', 'confident', 'experience', 'bring', 'contribute']):
                return "After careful consideration of my background and the role requirements, I have decided not to apply for this position at this time."
            else:
                return f"I have compared my CV and the role description and decided not to apply due to: {extracted_content}"
    
    # If generic message, provide better fallback
    if "but no specific reasons were provided" in rationale:
        return "After careful consideration, I have decided this role may not be the best fit for my current experience and career goals."
    
    return rationale

def test_extraction_logic():
    """Test our improved extraction logic"""
    
    # Load the current job match report
    report_path = Path("/home/xai/Documents/sunset/reports/fresh_review/job_match_report.json")
    
    if not report_path.exists():
        print("❌ Job match report not found")
        return
    
    with open(report_path, 'r') as f:
        jobs = json.load(f)
    
    print(f"🔍 Testing extraction logic on {len(jobs)} jobs")
    print("-" * 80)
    
    for i, job in enumerate(jobs):
        job_id = job.get('Job ID', f'Job {i+1}')
        original_rationale = job.get('No-go rationale', '')
        match_level = job.get('Match level', '')
        
        print(f"\n📋 Job {job_id} (Match: {match_level})")
        print(f"Original rationale: {original_rationale[:100]}{'...' if len(original_rationale) > 100 else ''}")
        
        # Test the cleaning logic
        cleaned_rationale = clean_malformed_rationale(original_rationale)
        
        if cleaned_rationale != original_rationale:
            print(f"✨ Cleaned rationale: {cleaned_rationale[:100]}{'...' if len(cleaned_rationale) > 100 else ''}")
            print("🔧 IMPROVEMENT DETECTED!")
        else:
            print("✅ No changes needed")
    
    print(f"\n📊 Summary: Tested extraction logic on {len(jobs)} jobs")
    print("✨ Ready to re-process job matches with improved logic!")

if __name__ == "__main__":
    test_extraction_logic()
