#!/usr/bin/env python3
"""
Corporate Narratives Excel Export
Extract business-appropriate application narratives from corporate consciousness evaluations
Perfect for Deutsche Bank and professional cover letters
"""

import json
import pandas as pd
from pathlib import Path
import os
from datetime import datetime

def extract_corporate_narratives():
    """Extract corporate application narratives from jobs with corporate consciousness evaluations"""
    
    # Our confirmed jobs with corporate evaluations
    confirmed_jobs = [
        'job60955.json', 'job65109.json', 'job65115.json', 'job65142.json', 'job65227.json',
        'job65228.json', 'job65229.json', 'job65230.json', 'job65231.json', 'job65232.json'
    ]
    
    postings_dir = Path('data/postings')
    data_rows = []
    
    print("🏢 Extracting Corporate Application Narratives...")
    print("=" * 60)
    
    for job_file in confirmed_jobs:
        job_path = postings_dir / job_file
        
        if not job_path.exists():
            print(f"❌ Missing: {job_file}")
            continue
            
        try:
            with open(job_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Check for corporate consciousness evaluation
            if 'corporate_consciousness_evaluation' not in job_data:
                print(f"⚠️  No corporate evaluation: {job_file}")
                continue
                
            corp_eval = job_data['corporate_consciousness_evaluation']
            
            # Extract the professional application narrative
            application_narrative = corp_eval.get('application_narrative', '')
            
            if not application_narrative or len(application_narrative) < 100:
                print(f"⚠️  Short/missing narrative: {job_file} ({len(application_narrative)} chars)")
                continue
            
            # Get job basic info
            company = job_data.get('company', 'Unknown Company')
            title = job_data.get('title', 'Unknown Role')
            match_level = corp_eval.get('overall_match_level', 'UNKNOWN')
            confidence = corp_eval.get('confidence_score', 0.0)
            empowering_msg = corp_eval.get('empowering_message', '')
            
            # Create row for Excel
            row = {
                'Job_File': job_file,
                'Company': company,
                'Position': title,
                'Match_Level': match_level,
                'Confidence_Score': confidence,
                'Empowering_Message': empowering_msg,
                'Corporate_Application_Narrative': application_narrative,
                'Narrative_Length': len(application_narrative),
                'Ready_for_Cover_Letter': 'YES' if len(application_narrative) > 500 else 'REVIEW'
            }
            
            data_rows.append(row)
            
            print(f"✅ {company} - {title}")
            print(f"   📝 Narrative: {len(application_narrative)} chars")
            print(f"   🎯 Match: {match_level} ({confidence:.2f})")
            print(f"   💼 Preview: {application_narrative[:120]}...")
            print()
            
        except Exception as e:
            print(f"❌ Error processing {job_file}: {e}")
            continue
    
    # Create DataFrame and Excel export
    if data_rows:
        df = pd.DataFrame(data_rows)
        
        # Sort by confidence score (highest first)
        df = df.sort_values('Confidence_Score', ascending=False)
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/output/CORPORATE_narratives_{timestamp}.xlsx"
        
        # Ensure output directory exists
        os.makedirs('data/output', exist_ok=True)
        
        # Create Excel with formatting
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Corporate_Narratives', index=False)
            
            # Get the workbook and worksheet for formatting
            workbook = writer.book
            worksheet = writer.sheets['Corporate_Narratives']
            
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
                
                # Set reasonable max width for narrative column
                if column_letter == 'G':  # Corporate_Application_Narrative column
                    adjusted_width = min(max_length + 2, 80)  # Max 80 chars wide
                else:
                    adjusted_width = min(max_length + 2, 30)
                    
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Wrap text for the narrative column
            from openpyxl.styles import Alignment
            for row in worksheet.iter_rows(min_row=2, max_row=len(df)+1, min_col=7, max_col=7):
                for cell in row:
                    cell.alignment = Alignment(wrap_text=True, vertical='top')
        
        print("=" * 60)
        print(f"🎉 SUCCESS! Corporate narratives exported to:")
        print(f"   📊 {output_file}")
        print(f"   📈 {len(data_rows)} professional narratives ready for Deutsche Bank!")
        print()
        print("🏢 BUSINESS INSIGHTS:")
        print(f"   • Average narrative length: {df['Narrative_Length'].mean():.0f} characters")
        print(f"   • Average confidence: {df['Confidence_Score'].mean():.2f}")
        print(f"   • Strong matches: {len(df[df['Match_Level'] == 'STRONG MATCH'])}")
        print(f"   • Cover letter ready: {len(df[df['Ready_for_Cover_Letter'] == 'YES'])}")
        
        return output_file
    else:
        print("❌ No corporate narratives found!")
        return None

if __name__ == "__main__":
    extract_corporate_narratives()
