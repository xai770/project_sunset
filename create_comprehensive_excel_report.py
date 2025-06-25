#!/usr/bin/env python3
"""
Comprehensive Job Analysis Report - All 99 Jobs with AI Specialists Results
==========================================================================

Create a comprehensive Excel report showing all 99 jobs processed with our
working v1_1 domain classification and v1_0 location validation specialists.
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import glob

def main():
    print('📊 CREATING COMPREHENSIVE EXCEL REPORT - ALL 99 JOBS!')
    print('=' * 60)
    
    # Find all reprocessed LLM files
    reprocessed_files = glob.glob('data/postings/job*_reprocessed_llm.json')
    print(f'🔍 Found {len(reprocessed_files)} reprocessed LLM files')
    
    jobs_data = []
    
    for file_path in sorted(reprocessed_files):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Extract job info - FIXED DATA STRUCTURE
            job_id = data.get('job_id', Path(file_path).stem.replace('_reprocessed_llm', '').replace('job', ''))
            job_title = data.get('title', 'Unknown Title')
            
            # Extract AI analysis results - CORRECT STRUCTURE
            domain_analysis = data.get('domain_classification', {}).get('result', {})
            domain_details = domain_analysis.get('analysis_details', {})
            location_analysis = data.get('location_validation', {}).get('result', {})
            
            job_info = {
                'Job ID': job_id,
                'Title': job_title,
                'Company': 'Deutsche Bank',
                'Job Description': data.get('description', 'No description available')[:500] + '...' if len(data.get('description', '')) > 500 else data.get('description', 'No description available'),
                'Location (Validated)': location_analysis.get('authoritative_location', 'Not validated'),
                'Location Conflict': '❌ YES' if location_analysis.get('conflict_detected', False) else '✅ NO',
                'Domain Classification': domain_analysis.get('primary_domain_classification', 'unknown'),
                'Domain Confidence': domain_details.get('domain_confidence', 0.0),
                'Should Proceed': '✅ YES' if domain_analysis.get('should_proceed_with_evaluation', True) else '❌ NO',
                'Domain Reasoning': domain_details.get('domain_reasoning', 'No reasoning provided')[:100] + '...' if len(domain_details.get('domain_reasoning', '')) > 100 else domain_details.get('domain_reasoning', ''),
                'Decision Reasoning': domain_details.get('decision_reasoning', 'No reasoning provided')[:150] + '...' if len(domain_details.get('decision_reasoning', '')) > 150 else domain_details.get('decision_reasoning', ''),
                'Compatibility Score': domain_analysis.get('domain_compatibility_score', 0.0),
                'Critical Skill Gaps': ', '.join(domain_analysis.get('critical_skill_gaps', [])),
                'Processing Time (s)': data.get('domain_classification', {}).get('processing_time', 0.0),
                'Reprocessed At': data.get('reprocessed_at', ''),
                'File Path': file_path
            }
            
            jobs_data.append(job_info)
            
        except Exception as e:
            print(f'   ❌ Error reading {file_path}: {e}')
    
    # Create DataFrame
    df = pd.DataFrame(jobs_data)
    
    # Sort by Job ID for better organization
    df['Job ID Numeric'] = pd.to_numeric(df['Job ID'], errors='coerce')
    df = df.sort_values('Job ID Numeric').drop('Job ID Numeric', axis=1)
    
    # Add summary columns
    df['Final Recommendation'] = df.apply(lambda row: 
        'DO NOT APPLY - Location Conflict' if '❌ YES' in row['Location Conflict']
        else 'DO NOT APPLY - Domain Mismatch' if '❌ NO' in row['Should Proceed']
        else 'REVIEW REQUIRED - Passed AI Filtering', axis=1)
    
    # Generate comprehensive Excel report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_path = f'reports/fresh_review/COMPREHENSIVE_job_analysis_all_99_jobs_{timestamp}.xlsx'
    
    # Create Excel with multiple sheets
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Main results sheet
        df.to_excel(writer, sheet_name='All Jobs Analysis', index=False)
        
        # Summary statistics sheet
        summary_data = {
            'Metric': [
                'Total Jobs Processed',
                'Location Conflicts Detected',
                'Domain Rejects (Should NOT Proceed)',
                'Jobs Passed AI Filtering (Should Proceed)',
                'Investment Management Domain',
                'Financial Crime Compliance Domain', 
                'Banking Sales Domain',
                'Cybersecurity Domain',
                'Data Engineering Domain',
                'IT Operations Domain',
                'Average Domain Confidence',
                'Average Processing Time (seconds)'
            ],
            'Count': [
                len(df),
                len(df[df['Location Conflict'].str.contains('YES', na=False)]),
                len(df[df['Should Proceed'].str.contains('NO', na=False)]),
                len(df[df['Should Proceed'].str.contains('YES', na=False)]),
                len(df[df['Domain Classification'] == 'investment_management']),
                len(df[df['Domain Classification'] == 'financial_crime_compliance']),
                len(df[df['Domain Classification'] == 'banking_sales']),
                len(df[df['Domain Classification'] == 'cybersecurity']),
                len(df[df['Domain Classification'] == 'data_engineering']),
                len(df[df['Domain Classification'] == 'it_operations']),
                df['Domain Confidence'].mean(),
                df['Processing Time (s)'].mean()
            ],
            'Percentage': [
                '100%',
                f"{len(df[df['Location Conflict'].str.contains('YES', na=False)])/len(df)*100:.1f}%",
                f"{len(df[df['Should Proceed'].str.contains('NO', na=False)])/len(df)*100:.1f}%",
                f"{len(df[df['Should Proceed'].str.contains('YES', na=False)])/len(df)*100:.1f}%",
                f"{len(df[df['Domain Classification'] == 'investment_management'])/len(df)*100:.1f}%",
                f"{len(df[df['Domain Classification'] == 'financial_crime_compliance'])/len(df)*100:.1f}%",
                f"{len(df[df['Domain Classification'] == 'banking_sales'])/len(df)*100:.1f}%",
                f"{len(df[df['Domain Classification'] == 'cybersecurity'])/len(df)*100:.1f}%",
                f"{len(df[df['Domain Classification'] == 'data_engineering'])/len(df)*100:.1f}%",
                f"{len(df[df['Domain Classification'] == 'it_operations'])/len(df)*100:.1f}%",
                f"{df['Domain Confidence'].mean():.2f}",
                f"{df['Processing Time (s)'].mean():.1f}s"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary Statistics', index=False)
        
        # Jobs that passed filtering (potential matches)
        passed_jobs = df[df['Should Proceed'].str.contains('YES', na=False)]
        passed_jobs.to_excel(writer, sheet_name='Passed AI Filtering', index=False)
        
        # Golden test cases sheet
        golden_jobs = df[df['Job ID'].isin(['60955', '58432', '63144'])]
        golden_jobs.to_excel(writer, sheet_name='Golden Test Cases', index=False)
    
    print(f'\n✨ COMPREHENSIVE EXCEL REPORT CREATED!')
    print(f'📊 Report: {excel_path}')
    
    # Print summary statistics
    total_jobs = len(df)
    location_conflicts = len(df[df['Location Conflict'].str.contains('YES', na=False)])
    domain_rejects = len(df[df['Should Proceed'].str.contains('NO', na=False)])
    passed_filtering = len(df[df['Should Proceed'].str.contains('YES', na=False)])
    
    print(f'\n📋 COMPREHENSIVE ANALYSIS SUMMARY:')
    print(f'   📊 Total Jobs: {total_jobs}')
    print(f'   📍 Location Conflicts: {location_conflicts} ({location_conflicts/total_jobs*100:.1f}%)')
    print(f'   🏷️ Domain Rejects: {domain_rejects} ({domain_rejects/total_jobs*100:.1f}%)')
    print(f'   ✅ Passed AI Filtering: {passed_filtering} ({passed_filtering/total_jobs*100:.1f}%)')
    print(f'   📈 Average Domain Confidence: {df["Domain Confidence"].mean():.2f}')
    print(f'   ⚡ Average Processing Time: {df["Processing Time (s)"].mean():.1f}s')
    
    print(f'\n🎯 DOMAIN BREAKDOWN:')
    domain_counts = df['Domain Classification'].value_counts()
    for domain, count in domain_counts.items():
        print(f'   🏷️ {domain}: {count} jobs ({count/total_jobs*100:.1f}%)')
    
    print(f'\n🧪 GOLDEN TEST VALIDATION:')
    for job_id in ['60955', '58432', '63144']:
        job_row = df[df['Job ID'] == job_id]
        if not job_row.empty:
            title = job_row['Title'].iloc[0][:50] + '...' if len(job_row['Title'].iloc[0]) > 50 else job_row['Title'].iloc[0]
            domain = job_row['Domain Classification'].iloc[0]
            decision = job_row['Should Proceed'].iloc[0]
            confidence = job_row['Domain Confidence'].iloc[0]
            print(f'   🎯 Job {job_id}: {title}')
            print(f'      Domain: {domain} | Decision: {decision} | Confidence: {confidence:.2f}')
    
    print(f'\n🎉 Excel report ready for collaborative review!')
    print(f'📁 File: {excel_path}')

if __name__ == "__main__":
    main()