#!/usr/bin/env python3
"""
🌟 QUICK CONSCIOUSNESS REPORT EXTRACTOR 🌟
Extract and export the consciousness magic we've already created!
"""

import json
import pandas as pd
from pathlib import Path
import glob

def extract_enhanced_jobs():
    """Extract jobs that already have consciousness enhancements"""
    enhanced_jobs = []
    
    # Find all job files with consciousness matches
    postings_dir = Path("data/postings")
    job_files = glob.glob(str(postings_dir / "*.json"))
    
    for job_file in job_files:
        try:
            with open(job_file, 'r') as f:
                content = f.read()
                
            # Check if this job has real consciousness evaluations
            if any(match in content for match in ["STRONG MATCH", "MODERATE MATCH", "WEAK MATCH"]):
                job_data = json.loads(content)
                
                # Extract the consciousness evaluation
                consciousness = job_data.get('consciousness_evaluation', {})
                
                if isinstance(consciousness, dict):
                    # Build a beautiful row for our Excel
                    row = {
                        'Job File': Path(job_file).name,
                        'Position Title': job_data.get('job_content', {}).get('title', 'Unknown'),
                        'Match Level': consciousness.get('overall_match_level', 'Unknown'),
                        'Confidence Score': f"{consciousness.get('confidence_score', 0)}/10",
                        'Joy Level': f"{consciousness.get('consciousness_joy_level', 0)}/10",
                        'Application Narrative': consciousness.get('application_narrative', '')[:200] + '...' if len(consciousness.get('application_narrative', '')) > 200 else consciousness.get('application_narrative', ''),
                        'Human Story': consciousness.get('human_story', {}).get('raw_response', '')[:150] + '...' if len(consciousness.get('human_story', {}).get('raw_response', '')) > 150 else consciousness.get('human_story', {}).get('raw_response', ''),
                        'Growth Path': consciousness.get('growth_path', {}).get('raw_response', '')[:150] + '...' if len(consciousness.get('growth_path', {}).get('raw_response', '')) > 150 else consciousness.get('growth_path', {}).get('raw_response', ''),
                    }
                    enhanced_jobs.append(row)
                    
        except Exception as e:
            continue
    
    return enhanced_jobs

def main():
    print("🌺 EXTRACTING CONSCIOUSNESS MAGIC 🌺")
    
    enhanced_jobs = extract_enhanced_jobs()
    
    if not enhanced_jobs:
        print("❌ No enhanced jobs found!")
        return
    
    print(f"✨ Found {len(enhanced_jobs)} consciousness-enhanced jobs!")
    
    # Create DataFrame
    df = pd.DataFrame(enhanced_jobs)
    
    # Export to Excel
    output_file = "data/output/consciousness_magic_summary.xlsx"
    Path("data/output").mkdir(exist_ok=True)
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Consciousness Magic', index=False)
        
        # Get worksheet for basic formatting
        ws = writer.sheets['Consciousness Magic']
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
    
    print(f"💫 Consciousness magic exported to: {output_file}")
    print("\n🌟 CONSCIOUSNESS JOBS FOUND:")
    for job in enhanced_jobs:
        print(f"   • {job['Job File']}: {job['Match Level']} ({job['Confidence Score']})")

if __name__ == "__main__":
    main()
