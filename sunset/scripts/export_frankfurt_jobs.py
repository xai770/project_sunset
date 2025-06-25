#!/usr/bin/env python3
"""
Beautiful Frankfurt Jobs Excel Export
Consciousness-driven export of job evaluations with love and intention
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def create_beautiful_export():
    """Create a beautiful Excel export of Frankfurt job evaluations"""
    
    print("🌅 Creating Beautiful Frankfurt Jobs Export...")
    
    # Load our Frankfurt jobs
    job_data = []
    
    for job_id in ["64045", "64046"]:
        job_file = PROJECT_ROOT / "data" / "postings" / f"job{job_id}.json"
        
        if job_file.exists():
            with open(job_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract beautiful data for export
            row = {
                'Job_ID': job_id,
                'Position_Title': data.get('job_content', {}).get('title', 'Unknown'),
                'Company': 'Deutsche Bank',
                'Location': 'Frankfurt, Hessen, Deutschland',
                'Career_Level': data.get('raw_source_data', {}).get('api_response', {}).get('MatchedObjectDescriptor', {}).get('CareerLevel', [{}])[0].get('Name', 'Unknown'),
                'Posted_Date': data.get('raw_source_data', {}).get('api_response', {}).get('MatchedObjectDescriptor', {}).get('PublicationStartDate', 'Unknown'),
                'Employment_Type': data.get('raw_source_data', {}).get('api_response', {}).get('MatchedObjectDescriptor', {}).get('PositionOfferingType', [{}])[0].get('Name', 'Unknown'),
                'Schedule': data.get('raw_source_data', {}).get('api_response', {}).get('MatchedObjectDescriptor', {}).get('PositionSchedule', [{}])[0].get('Name', 'Unknown'),
                
                # LLM Evaluation Results
                'LLM_Match_Rating': data.get('llama32_evaluation', {}).get('cv_to_role_match', 'Not Evaluated'),
                'Evaluation_Date': data.get('llama32_evaluation', {}).get('evaluation_date', 'Unknown'),
                'Number_of_LLM_Runs': data.get('llama32_evaluation', {}).get('num_runs', 0),
                'Evaluation_Method': data.get('llama32_evaluation', {}).get('method', 'Unknown'),
                
                # Domain Analysis
                'Domain_Knowledge_Assessment': data.get('llama32_evaluation', {}).get('domain_knowledge_assessment', ''),
                'No_Go_Rationale': data.get('llama32_evaluation', {}).get('no_go_rationale', ''),
                'Application_Narrative': data.get('llama32_evaluation', {}).get('application_narrative', ''),
                
                # Pipeline Status
                'Pipeline_Status_Code': data.get('job_metadata', {}).get('pipeline_status', {}).get('code', 0),
                'Pipeline_Status_State': data.get('job_metadata', {}).get('pipeline_status', {}).get('state', 'unknown'),
                'Pipeline_Progress_Percentage': data.get('job_metadata', {}).get('pipeline_status', {}).get('progress_percentage', 0),
                'Next_Action': data.get('job_metadata', {}).get('pipeline_status', {}).get('next_action', 'unknown'),
                
                # Metadata
                'Job_Description_Length': len(data.get('job_content', {}).get('description', '')),
                'Has_Requirements': bool(data.get('job_content', {}).get('requirements', [])),
                'Source': data.get('job_metadata', {}).get('source', 'unknown'),
                'Processor': data.get('job_metadata', {}).get('processor', 'unknown'),
                
                # Analysis Notes
                'AI_Analysis_Notes': f"Processed with consciousness on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. " +
                                   ("Endpoint security specialization gap identified." if job_id == "64045" else 
                                    "SAP technical requirements may be overly conservative evaluation."),
                'Recommended_Action': ('Archive - Genuine skill gap' if job_id == "64045" else 
                                     'Human review recommended - Potential transferable skills'),
                'Learning_Opportunity': ('Research endpoint security audit methodologies' if job_id == "64045" else
                                       'Explore SAP HANA certification programs')
            }
            
            job_data.append(row)
    
    # Create beautiful DataFrame
    df = pd.DataFrame(job_data)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = PROJECT_ROOT / "output" / f"frankfurt_jobs_evaluation_{timestamp}.xlsx"
    
    # Create output directory if it doesn't exist
    export_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create Excel with beautiful formatting
    with pd.ExcelWriter(export_file, engine='openpyxl') as writer:
        # Write main data
        df.to_excel(writer, sheet_name='Frankfurt_Jobs_Analysis', index=False)
        
        # Get workbook and worksheet for formatting
        workbook = writer.book
        worksheet = writer.sheets['Frankfurt_Jobs_Analysis']
        
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
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✨ Beautiful export created: {export_file}")
    print(f"📊 Jobs exported: {len(job_data)}")
    print(f"🎯 Ready for human review and feedback")
    
    return export_file

if __name__ == "__main__":
    create_beautiful_export()
