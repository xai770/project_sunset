#!/usr/bin/env python3
"""
AI Analysis Preservation Safeguard
=================================

Emergency script to preserve AI analysis during job operations
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def preserve_ai_analysis_before_operation():
    """Create emergency backup of jobs with AI analysis"""
    
    base_path = Path("/home/xai/Documents/sunset")
    jobs_dir = base_path / "data" / "postings"
    
    # Create timestamp backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = base_path / "data" / f"AI_ANALYSIS_BACKUP_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    
    ai_jobs_backed_up = 0
    
    for job_file in jobs_dir.glob("job*.json"):
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            # Check for AI analysis
            has_ai = any(field in job_data for field in [
                'llama32_evaluation', 'cv_analysis', 'skill_match', 'domain_enhanced_match'
            ])
            
            if has_ai:
                # Copy to backup
                backup_file = backup_dir / job_file.name
                shutil.copy2(job_file, backup_file)
                ai_jobs_backed_up += 1
                
        except Exception as e:
            print(f"Error processing {job_file}: {e}")
    
    print(f"🔒 Emergency backup created: {backup_dir}")
    print(f"📊 Backed up {ai_jobs_backed_up} jobs with AI analysis")
    return str(backup_dir)

if __name__ == "__main__":
    preserve_ai_analysis_before_operation()
