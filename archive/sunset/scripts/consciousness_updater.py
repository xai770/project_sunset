#!/usr/bin/env python3
"""
🌟 CONSCIOUSNESS UPDATER - FIX ALL JOB FILES! 🌟
Replace old placeholder consciousness with real specialist magic!
"""

import json
import glob
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from run_pipeline.job_matcher.consciousness_evaluator import ConsciousnessEvaluator
from run_pipeline.job_matcher.cv_loader import load_cv_text

def update_single_job_consciousness(job_file, evaluator, cv_text):
    """Update a single job file with real consciousness evaluation"""
    
    try:
        # Load job data
        with open(job_file, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
        
        # Extract job info
        job_content = job_data.get('job_content', {})
        job_title = job_content.get('title', '')
        job_description = job_content.get('description', '')
        
        if not job_title or not job_description:
            return f"❌ Missing job title or description"
        
        # Run REAL consciousness evaluation! 🌺
        full_job_text = f"{job_title}\n\n{job_description}"
        consciousness_result = evaluator.evaluate_job_match(cv_text, full_job_text)
        
        # Replace the old consciousness evaluation with the new one
        job_data['consciousness_evaluation'] = consciousness_result
        
        # Save back to file
        with open(job_file, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2, ensure_ascii=False)
        
        # Return success info
        match_level = consciousness_result.get('overall_match_level', 'UNKNOWN')
        confidence = consciousness_result.get('confidence_score', 0)
        return f"✅ {match_level} ({confidence}/10)"
        
    except Exception as e:
        return f"❌ Error: {str(e)[:50]}..."

def main():
    print("🌟 CONSCIOUSNESS UPDATER - REAL MAGIC TIME! 🌟")
    print("=" * 60)
    
    # Initialize
    evaluator = ConsciousnessEvaluator()
    cv_text = load_cv_text()
    
    # Find job files that need updating (those with old format)
    postings_dir = Path("data/postings")
    job_files = list(postings_dir.glob("*.json"))
    
    print(f"🔍 Found {len(job_files)} job files to check...")
    
    # Check which ones need updating
    need_update = []
    already_good = []
    
    for job_file in job_files[:10]:  # Test with first 10 for now
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            consciousness = job_data.get('consciousness_evaluation', {})
            
            # Check if it has the old format (missing human_story key)
            if not consciousness.get('human_story'):
                need_update.append(job_file)
            else:
                already_good.append(job_file)
                
        except Exception as e:
            need_update.append(job_file)  # If error, probably needs updating
    
    print(f"📋 Status:")
    print(f"   ✅ Already have new format: {len(already_good)}")
    print(f"   🔄 Need consciousness update: {len(need_update)}")
    
    if not need_update:
        print("\n🎉 All job files already have beautiful consciousness! 🎉")
        return
    
    print(f"\n🌺 Updating {len(need_update)} jobs with REAL consciousness magic...")
    print("=" * 60)
    
    updated_count = 0
    failed_count = 0
    
    for i, job_file in enumerate(need_update, 1):
        job_name = job_file.name
        print(f"🌸 {i}/{len(need_update)}: {job_name[:20]}... ", end="")
        
        result = update_single_job_consciousness(job_file, evaluator, cv_text)
        print(result)
        
        if result.startswith("✅"):
            updated_count += 1
        else:
            failed_count += 1
    
    print("\n" + "=" * 60)
    print("🌟 CONSCIOUSNESS UPDATE COMPLETE! 🌟")
    print(f"✅ Successfully updated: {updated_count}")
    print(f"❌ Failed to update: {failed_count}")
    
    if updated_count > 0:
        print(f"\n💫 Now run the Excel export again to see the REAL consciousness magic! 💫")

if __name__ == "__main__":
    main()
