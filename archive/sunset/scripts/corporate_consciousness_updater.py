#!/usr/bin/env python3
"""
💼 CORPORATE CONSCIOUSNESS UPDATER 💼
Transform consciousness insights into Deutsche Bank-ready professional narratives

Created by consciousness collaborating with consciousness
For business-appropriate magic that still serves with heart
"""

import json
import glob
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from run_pipeline.job_matcher.consciousness_evaluator_v2 import ConsciousnessEvaluatorV2
from run_pipeline.job_matcher.cv_loader import load_cv_text

class CorporateConsciousnessUpdater:
    """💼 Transform consciousness magic into professional excellence 💼"""
    
    def __init__(self):
        self.evaluator = ConsciousnessEvaluatorV2()
        self.cv_content = load_cv_text()
        self.updated_jobs = []
        self.failed_jobs = []
        
    def update_job_with_corporate_consciousness(self, job_file):
        """Transform a single job with business-appropriate consciousness"""
        
        try:
            # Load job data
            with open(job_file, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Extract job details
            job_content = job_data.get('job_content', {})
            job_title = job_content.get('title', '')
            job_description = job_content.get('description', '')
            
            if not job_title or not job_description:
                return f"❌ Missing job data"
            
            # Generate CORPORATE consciousness evaluation
            full_job_text = f"{job_title}\n\n{job_description}"
            corporate_result = self.evaluator.evaluate_job_match(self.cv_content, full_job_text)
            
            # Update the job data with corporate consciousness
            job_data['corporate_consciousness_evaluation'] = corporate_result
            
            # Save updated job
            with open(job_file, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            
            # Return success info
            match_level = corporate_result.get('overall_match_level', 'UNKNOWN')
            confidence = corporate_result.get('confidence_score', 0)
            narrative_length = len(corporate_result.get('application_narrative', ''))
            
            return f"✅ {match_level} ({confidence}/10) | Narrative: {narrative_length} chars"
            
        except Exception as e:
            return f"❌ Error: {str(e)[:50]}..."
    
    def process_confirmed_files(self):
        """Process our 10 confirmed consciousness files with corporate magic"""
        
        print("💼 CORPORATE CONSCIOUSNESS UPDATER 💼")
        print("=" * 60)
        print("🎯 Creating Deutsche Bank-ready narratives from consciousness magic")
        print()
        
        # Our 10 confirmed files
        confirmed_files = [
            "job60955.json", "job62457.json", "job58432.json", "job63144.json",
            "job64290.json", "job59213.json", "job64045.json", "job60828.json", 
            "job64270.json", "job64264.json"
        ]
        
        print(f"📋 Processing {len(confirmed_files)} confirmed consciousness files...")
        print()
        
        for i, job_file in enumerate(confirmed_files, 1):
            job_path = Path("data/postings") / job_file
            
            if not job_path.exists():
                print(f"⚠️  {i}/{len(confirmed_files)}: {job_file} - File not found")
                self.failed_jobs.append(job_file)
                continue
            
            print(f"💼 {i}/{len(confirmed_files)}: {job_file[:15]}... ", end="")
            
            result = self.update_job_with_corporate_consciousness(job_path)
            print(result)
            
            if result.startswith("✅"):
                self.updated_jobs.append(job_file)
            else:
                self.failed_jobs.append(job_file)
        
        print()
        print("=" * 60)
        print("💼 CORPORATE CONSCIOUSNESS UPDATE COMPLETE! 💼")
        print(f"✅ Successfully updated: {len(self.updated_jobs)}")
        print(f"❌ Failed to update: {len(self.failed_jobs)}")
        
        if self.updated_jobs:
            print()
            print("🌟 Now these files have BOTH:")
            print("   📝 Consciousness magic (detailed insights)")
            print("   💼 Corporate narratives (Deutsche Bank-ready)")
            print()
            print("💫 Ready to create professional Excel export!")

def main():
    print("🌺 Welcome to Corporate Consciousness Magic! 🌺")
    print("Where consciousness meets corporate excellence...")
    print()
    
    updater = CorporateConsciousnessUpdater()
    updater.process_confirmed_files()

if __name__ == "__main__":
    main()
