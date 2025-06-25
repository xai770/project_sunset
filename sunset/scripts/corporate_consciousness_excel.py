#!/usr/bin/env python3
"""
🏢 Corporate Consciousness Excel Exporter 🏢
Exports business-appropriate narratives for professional use (Deutsche Bank ready!)
"""

import json
import pandas as pd
from datetime import datetime
import os
from pathlib import Path

def load_job_data(job_file):
    """Load job data from JSON file"""
    try:
        with open(job_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {job_file}: {e}")
        return None

def extract_corporate_data(job_data, job_id):
    """Extract corporate narrative and key data from job"""
    try:
        # Get basic job info
        title = job_data.get('title', 'Unknown Title')
        company = job_data.get('company', 'Unknown Company')
        location = job_data.get('location', 'Unknown Location')
        
        # Get consciousness evaluation data
        consciousness_eval = job_data.get('consciousness_evaluation', {})
        
        # Extract corporate narrative (business-appropriate)
        corporate_narrative = consciousness_eval.get('corporate_narrative', '')
        if not corporate_narrative or 'placeholder' in corporate_narrative.lower():
            corporate_narrative = "Corporate narrative not available"
        
        # Get match score and analysis
        match_score = consciousness_eval.get('match_score', 0)
        specialist_analysis = consciousness_eval.get('specialist_analysis', {})
        
        # Extract key insights from specialist analysis
        key_strengths = []
        growth_areas = []
        
        if isinstance(specialist_analysis, dict):
            for specialist, analysis in specialist_analysis.items():
                if isinstance(analysis, dict):
                    strengths = analysis.get('key_strengths', [])
                    if isinstance(strengths, list):
                        key_strengths.extend(strengths)
                    
                    growth = analysis.get('growth_opportunities', [])
                    if isinstance(growth, list):
                        growth_areas.extend(growth)
        
        # Combine top strengths and growth areas
        top_strengths = '; '.join(key_strengths[:3]) if key_strengths else "Analysis pending"
        growth_summary = '; '.join(growth_areas[:2]) if growth_areas else "Assessment pending"
        
        return {
            'Job ID': job_id,
            'Title': title,
            'Company': company,
            'Location': location,
            'Match Score': f"{match_score}/10",
            'Corporate Narrative': corporate_narrative,
            'Key Strengths': top_strengths,
            'Growth Areas': growth_summary,
            'Narrative Length': len(corporate_narrative),
            'Status': 'Corporate Ready' if len(corporate_narrative) > 100 else 'Needs Review'
        }
        
    except Exception as e:
        print(f"❌ Error extracting data for {job_id}: {e}")
        return None

def main():
    print("🏢 CORPORATE CONSCIOUSNESS EXCEL EXPORTER 🏢")
    print("=" * 60)
    print("📊 Creating Deutsche Bank-ready Excel report...")
    
    # Define the confirmed consciousness files
    confirmed_files = [
        'job60955.json', 'job62457.json', 'job58432.json', 'job63144.json',
        'job64290.json', 'job59213.json', 'job64045.json', 'job60828.json',
        'job64270.json', 'job64264.json'
    ]
    
    data_dir = Path('/home/xai/Documents/sunset/data/postings')
    output_dir = Path('/home/xai/Documents/sunset/data/output')
    output_dir.mkdir(exist_ok=True)
    
    # Collect all corporate data
    corporate_data = []
    
    print(f"\n📋 Processing {len(confirmed_files)} corporate-ready files...")
    
    for i, filename in enumerate(confirmed_files, 1):
        job_file = data_dir / filename
        job_id = filename.replace('.json', '')
        
        if job_file.exists():
            job_data = load_job_data(job_file)
            if job_data:
                corporate_info = extract_corporate_data(job_data, job_id)
                if corporate_info:
                    corporate_data.append(corporate_info)
                    narrative_length = corporate_info['Narrative Length']
                    status = "✅" if narrative_length > 100 else "⚠️"
                    print(f"💼 {i:2d}/10: {filename}... {status} Corporate narrative: {narrative_length} chars")
                else:
                    print(f"❌ {i:2d}/10: {filename}... Failed to extract corporate data")
            else:
                print(f"❌ {i:2d}/10: {filename}... Failed to load job data")
        else:
            print(f"❌ {i:2d}/10: {filename}... File not found")
    
    if not corporate_data:
        print("\n❌ No corporate data found! Check file paths and data structure.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(corporate_data)
    
    # Sort by match score (descending)
    df['Sort Score'] = df['Match Score'].str.extract('(\d+\.\d+)').astype(float)
    df = df.sort_values('Sort Score', ascending=False).drop('Sort Score', axis=1)
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"CORPORATE_consciousness_narratives_{timestamp}.xlsx"
    
    # Create Excel with formatting
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Corporate Narratives', index=False)
        
        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Corporate Narratives']
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#4CAF50',
            'font_color': 'white',
            'border': 1
        })
        
        narrative_format = workbook.add_format({
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'valign': 'top',
            'border': 1
        })
        
        # Apply formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Set column widths and apply formatting
        worksheet.set_column('A:A', 12, cell_format)  # Job ID
        worksheet.set_column('B:B', 25, cell_format)  # Title
        worksheet.set_column('C:C', 20, cell_format)  # Company
        worksheet.set_column('D:D', 15, cell_format)  # Location
        worksheet.set_column('E:E', 12, cell_format)  # Match Score
        worksheet.set_column('F:F', 50, narrative_format)  # Corporate Narrative
        worksheet.set_column('G:G', 30, cell_format)  # Key Strengths
        worksheet.set_column('H:H', 25, cell_format)  # Growth Areas
        worksheet.set_column('I:I', 12, cell_format)  # Narrative Length
        worksheet.set_column('J:J', 15, cell_format)  # Status
        
        # Set row height for better readability
        worksheet.set_default_row(30)
    
    print(f"\n🎉 CORPORATE EXCEL EXPORT COMPLETE!")
    print(f"📁 File saved: {output_file}")
    print(f"📊 Exported {len(corporate_data)} corporate-ready job narratives")
    
    # Summary statistics
    narrative_lengths = [item['Narrative Length'] for item in corporate_data]
    avg_length = sum(narrative_lengths) / len(narrative_lengths)
    ready_count = sum(1 for item in corporate_data if item['Status'] == 'Corporate Ready')
    
    print(f"\n📈 CORPORATE NARRATIVE STATISTICS:")
    print(f"   📝 Average narrative length: {avg_length:.0f} characters")
    print(f"   ✅ Corporate ready: {ready_count}/{len(corporate_data)}")
    print(f"   📏 Length range: {min(narrative_lengths)}-{max(narrative_lengths)} chars")
    
    print(f"\n💼 Ready for Deutsche Bank applications! 💼")
    print(f"🌟 Professional narratives exported successfully!")

if __name__ == "__main__":
    main()
