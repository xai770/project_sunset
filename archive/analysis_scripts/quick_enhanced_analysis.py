#!/usr/bin/env python3
"""
Quick Enhanced Analysis - Create Enhanced Excel with Specialists
==============================================================

Apply our production specialists to the fresh job data and create enhanced analysis.
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import sys
import traceback

# Add project paths
sys.path.append('/home/xai/Documents/sunset')

def main():
    print('🚀 RUNNING ENHANCED JOB ANALYSIS WITH PRODUCTION SPECIALISTS!')
    
    try:
        from core.direct_specialist_manager import DirectSpecialistManager
        
        # Initialize specialist manager
        specialist_manager = DirectSpecialistManager()
        print('✅ Specialist manager initialized')
        print(f'📊 Status: {specialist_manager.get_status()}')
        
        # Load the Excel file we just created
        excel_path = 'reports/fresh_review/job_matches_20250623_194618.xlsx'
        df = pd.read_excel(excel_path)
        print(f'📊 Loaded {len(df)} jobs from Excel')
        
        # Add new columns for specialist analysis
        df['Location_Validated'] = ''
        df['Domain_Classification'] = ''
        df['Recommendation'] = ''
        df['Analysis_Notes'] = ''
        
        print('\n🔍 Running specialist analysis...')
        
        # Process all jobs with our production specialists
        for idx, row in df.iterrows():
            job_id = row['Job ID']
            print(f'   🎯 Analyzing Job {job_id}...')
            
            try:
                # Load full job data
                job_file = Path(row['File Path'])
                if job_file.exists():
                    with open(job_file, 'r') as f:
                        job_data = json.load(f)
                    
                    # Prepare data in the format specialists expect
                    job_content = job_data.get('job_content', {})
                    job_description = job_content.get('description', '')
                    job_title = job_content.get('title', '')
                    
                    input_data = {
                        'job_metadata': {
                            'location': job_content.get('location', {}),
                            'title': job_title,
                            'id': job_data.get('job_metadata', {}).get('job_id', job_id)
                        },
                        'job_description': job_description,
                        'job_title': job_title,
                        'full_content': f"{job_title}\n\n{job_description}"
                    }
                    
                    print(f'      📝 Title: {job_title[:60]}...' if len(job_title) > 60 else f'      📝 Title: {job_title}')
                    print(f'      📄 Description length: {len(job_description)} chars')
                    
                    print(f'      📍 Location data: {input_data["job_metadata"]["location"]}')
                    
                    # Try location validation
                    try:
                        location_result = specialist_manager.evaluate_with_specialist('location_validation', input_data)
                        if location_result.success:
                            location_status = '✅ Valid' if not location_result.result.get('conflict', False) else '❌ Conflict'
                            df.at[idx, 'Location_Validated'] = location_status
                            print(f'      📍 Location: {location_status}')
                        else:
                            df.at[idx, 'Location_Validated'] = '❓ Error'
                            print(f'      📍 Location validation failed: {location_result.error}')
                    except Exception as e:
                        print(f'      ❌ Location validation error: {e}')
                        df.at[idx, 'Location_Validated'] = f'Error: {str(e)[:50]}'
                    
                    # Try domain classification with debug info
                    try:
                        if len(job_description) < 100:
                            print(f'      ⚠️ Short description ({len(job_description)} chars): {job_description[:200]}...')
                        
                        domain_result = specialist_manager.evaluate_with_specialist('domain_classification', input_data)
                        if domain_result.success:
                            domain = domain_result.result.get('domain', 'unknown')
                            should_proceed = domain_result.result.get('should_proceed', True)
                            confidence = domain_result.result.get('confidence', 0.0)
                            df.at[idx, 'Domain_Classification'] = f'{domain} {"✅" if should_proceed else "❌"} ({confidence:.2f})'
                            print(f'      🏷️ Domain: {domain} (Proceed: {should_proceed}, Confidence: {confidence:.2f})')
                            
                            # Show domain classification reasoning if available
                            if 'reasoning' in domain_result.result:
                                print(f'      💭 Reasoning: {domain_result.result["reasoning"][:100]}...')
                        else:
                            df.at[idx, 'Domain_Classification'] = '❓ Error'
                            print(f'      🏷️ Domain classification failed: {domain_result.error}')
                    except Exception as e:
                        print(f'      ❌ Domain classification error: {e}')
                        df.at[idx, 'Domain_Classification'] = f'Error: {str(e)[:50]}'
                    
                    # Generate intelligent recommendation using our systematic review learnings
                    location_ok = '✅' in df.at[idx, 'Location_Validated']
                    domain_proceed = '✅' in df.at[idx, 'Domain_Classification']
                    
                    if not location_ok:
                        recommendation = 'DO NOT APPLY - Location Conflict'
                    elif not domain_proceed:
                        recommendation = 'DO NOT APPLY - Domain Mismatch'
                    else:
                        recommendation = 'REVIEW REQUIRED - Passed Initial Screening'
                    
                    df.at[idx, 'Recommendation'] = recommendation
                    df.at[idx, 'Analysis_Notes'] = f'Processed at {datetime.now().strftime("%H:%M:%S")}'
                    
                else:
                    df.at[idx, 'Analysis_Notes'] = 'Job file not found'
                    print(f'      ❌ File not found: {job_file}')
                    
            except Exception as e:
                print(f'      ❌ Error analyzing {job_id}: {e}')
                df.at[idx, 'Analysis_Notes'] = f'Analysis error: {str(e)[:100]}'
        
        # Generate enhanced Excel report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        enhanced_path = f'reports/fresh_review/enhanced_job_analysis_{timestamp}.xlsx'
        df.to_excel(enhanced_path, index=False, engine='openpyxl')
        
        print(f'\n✨ ENHANCED ANALYSIS COMPLETE!')
        print(f'📊 Enhanced report: {enhanced_path}')
        
        # Summary statistics
        total_jobs = len(df)
        location_conflicts = sum(df['Location_Validated'].str.contains('Conflict', na=False))
        do_not_apply = sum(df['Recommendation'].str.contains('DO NOT APPLY', na=False))
        
        print(f'\n📋 ANALYSIS SUMMARY:')
        print(f'   Total Jobs: {total_jobs}')
        print(f'   Location Conflicts: {location_conflicts} ({location_conflicts/total_jobs*100:.1f}%)')
        print(f'   Do Not Apply: {do_not_apply} ({do_not_apply/total_jobs*100:.1f}%)')
        print(f'   Review Required: {total_jobs - do_not_apply}')
        
        print(f'\n🎯 Ready for systematic review using our proven methodology!')
        
    except Exception as e:
        print(f'❌ Error in specialist analysis: {e}')
        print(f'🔍 Traceback: {traceback.format_exc()}')
        print('\n📋 Creating basic analysis template...')
        
        # Fallback: Load basic Excel and add analysis structure
        excel_path = 'reports/fresh_review/job_matches_20250623_194618.xlsx'
        df = pd.read_excel(excel_path)
        
        # Add placeholder columns for manual review
        df['Manual_Review_Status'] = 'PENDING'
        df['Location_Check'] = 'NEEDS_VALIDATION'
        df['Domain_Assessment'] = 'NEEDS_CLASSIFICATION'
        df['Final_Decision'] = 'TBD'
        df['Review_Notes'] = ''
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        manual_path = f'reports/fresh_review/manual_review_template_{timestamp}.xlsx'
        df.to_excel(manual_path, index=False, engine='openpyxl')
        
        print(f'✅ Manual review template: {manual_path}')
        print('🎯 Ready for systematic manual review!')

if __name__ == "__main__":
    main()
