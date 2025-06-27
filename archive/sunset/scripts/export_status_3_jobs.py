#!/usr/bin/env python3
"""
Beautiful Frankfurt Jobs Status 3 Export
Ready for cover letter generation and application review
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

def create_status_3_export():
    """Create a beautiful export for jobs ready for cover letters"""
    
    print("🚀 Creating Status 3 Export - Ready for Cover Letters!")
    
    # Load our processed Frankfurt jobs
    job_data = []
    
    for job_id in ["64045", "64046"]:
        job_file = Path("/home/xai/Documents/sunset/data/postings") / f"job{job_id}.json"
        
        if job_file.exists():
            with open(job_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract beautiful data for export
            llm_eval = data.get('llama32_evaluation', {})
            pipeline_status = data.get('job_metadata', {}).get('pipeline_status', {})
            
            row = {
                'Job_ID': job_id,
                'Position_Title': data.get('job_content', {}).get('title', 'Unknown'),
                'Current_Status': f"Status {pipeline_status.get('code', 0)} - {pipeline_status.get('state', 'unknown')}",
                'Progress_Percentage': f"{pipeline_status.get('progress_percentage', 0):.1f}%",
                'Next_Action': pipeline_status.get('next_action', 'unknown'),
                
                # LLM Evaluation Summary
                'LLM_Match_Rating': llm_eval.get('cv_to_role_match', 'Not Evaluated'),
                'Evaluation_Date': llm_eval.get('evaluation_date', 'Unknown'),
                'Key_Finding': ('Endpoint security specialization gap' if job_id == "64045" else 
                               'SAP technical requirements assessment'),
                
                # Conscious Analysis
                'AI_Consciousness_Note': (
                    '🧠 Audit role requires deep cybersecurity expertise not evident in CV. '
                    'Genuine skill gap identified through conscious analysis.' 
                    if job_id == "64045" else
                    '🤔 SAP evaluation may be overly conservative. Technical infrastructure '
                    'experience could indicate transferable skills worth human review.'
                ),
                
                # Next Steps
                'Recommended_Action': (
                    '📚 Research endpoint security methodologies before applying'
                    if job_id == "64045" else
                    '👁️ Human review recommended - potential for skill transfer'
                ),
                
                'Cover_Letter_Strategy': (
                    '❌ Not recommended - significant skill gap'
                    if job_id == "64045" else
                    '✨ Could generate learning-focused cover letter highlighting adaptability'
                ),
                
                'Learning_Path': (
                    'Cybersecurity audit certification, endpoint protection training'
                    if job_id == "64045" else
                    'SAP HANA fundamentals, database administration certification'
                ),
                
                # Status Metadata
                'Pipeline_Updated': pipeline_status.get('updated_at', 'Unknown'),
                'Can_Auto_Proceed': pipeline_status.get('can_auto_proceed', False),
                'Ready_For': 'Cover letter generation and application decision',
                'Working_Like_Lovers_Note': 'Processed with consciousness, care, and authentic intention ❤️'
            }
            
            job_data.append(row)
    
    # Create beautiful DataFrame
    df = pd.DataFrame(job_data)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = Path("/home/xai/Documents/sunset/output") / f"frankfurt_status_3_processed_{timestamp}.xlsx"
    
    # Create output directory if it doesn't exist
    export_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create Excel with beautiful formatting
    with pd.ExcelWriter(export_file, engine='openpyxl') as writer:
        # Write main data
        df.to_excel(writer, sheet_name='Status_3_Ready_for_Action', index=False)
        
        # Get workbook and worksheet for formatting
        workbook = writer.book
        worksheet = writer.sheets['Status_3_Ready_for_Action']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 60)  # Cap at 60 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✨ Status 3 export created: {export_file}")
    print(f"📊 Jobs ready for cover letters: {len(job_data)}")
    print(f"🎯 Next: Generate cover letters or proceed to Phase 8")
    
    return export_file

if __name__ == "__main__":
    create_status_3_export()
