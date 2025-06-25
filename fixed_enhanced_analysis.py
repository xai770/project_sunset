#!/usr/bin/env python3
"""
Fixed Enhanced Analysis - Using Working v1_1 Domain Classification Specialist
===========================================================================

Switch from broken v1_0 to working v1_1 specialist for domain classification.
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
    print('🚀 FIXED ENHANCED JOB ANALYSIS - USING WORKING v1_1 SPECIALIST!')
    
    try:
        # Import the WORKING v1_1 specialist directly (like Terminator's demo)
        sys.path.append('/home/xai/Documents/llm_factory')
        from llm_factory.modules.quality_validation.specialists_versioned.domain_classification.v1_1.src.domain_classification_specialist_llm import classify_job_domain_llm
        
        # Still use location validation from our working DirectSpecialistManager
        from core.direct_specialist_manager import DirectSpecialistManager
        specialist_manager = DirectSpecialistManager()
        
        print('✅ Working v1_1 domain specialist imported!')
        print('✅ Location validation specialist manager initialized')
        print(f'📊 Manager Status: {specialist_manager.get_status()}')
        
        # Load the Excel file we created
        excel_path = 'reports/fresh_review/job_matches_20250623_194618.xlsx'
        df = pd.read_excel(excel_path)
        print(f'📊 Loaded {len(df)} jobs from Excel')
        
        # Add new columns for specialist analysis
        df['Location_Validated'] = ''
        df['Domain_Classification'] = ''
        df['Should_Proceed'] = ''
        df['Recommendation'] = ''
        df['Analysis_Notes'] = ''
        
        print('\n🔍 Running FIXED specialist analysis...')
        
        # Process all jobs with WORKING specialists
        for idx, row in df.iterrows():
            job_id = row['Job ID']
            print(f'   🎯 Analyzing Job {job_id}...')
            
            try:
                # Load full job data
                job_file = Path(row['File Path'])
                if job_file.exists():
                    with open(job_file, 'r') as f:
                        job_data = json.load(f)
                    
                    job_content = job_data.get('job_content', {})
                    job_description = job_content.get('description', '')
                    job_title = job_content.get('title', '')
                    
                    print(f'      📝 Title: {job_title[:60]}...' if len(job_title) > 60 else f'      📝 Title: {job_title}')
                    print(f'      📄 Description length: {len(job_description)} chars')
                    
                    # Location validation (working v1_0)
                    try:
                        input_data = {
                            'job_metadata': {
                                'location': job_content.get('location', {}),
                                'title': job_title,
                                'id': job_data.get('job_metadata', {}).get('job_id', job_id)
                            },
                            'job_description': job_description
                        }
                        
                        location_result = specialist_manager.evaluate_with_specialist('location_validation', input_data)
                        if location_result.success:
                            location_valid = not location_result.result.get('conflict', False)
                            location_status = '✅ Valid' if location_valid else '❌ Conflict'
                            df.at[idx, 'Location_Validated'] = location_status
                            print(f'      📍 Location: {location_status}')
                        else:
                            df.at[idx, 'Location_Validated'] = '❓ Error'
                            print(f'      📍 Location validation failed: {location_result.error}')
                    except Exception as e:
                        print(f'      ❌ Location validation error: {e}')
                        df.at[idx, 'Location_Validated'] = f'Error: {str(e)[:50]}'
                        location_valid = True  # Default to true for domain testing
                    
                    # Domain classification (working v1_1)
                    try:
                        # Use the WORKING v1_1 specialist API
                        job_metadata = {
                            'title': job_title,
                            'id': job_id
                        }
                        
                        domain_result = classify_job_domain_llm(job_metadata, job_description)
                        
                        domain = domain_result.get('primary_domain_classification', 'unknown')
                        should_proceed = domain_result.get('should_proceed_with_evaluation', True)
                        confidence = domain_result.get('analysis_details', {}).get('domain_confidence', 0.0)
                        reasoning = domain_result.get('analysis_details', {}).get('decision_reasoning', 'No reasoning provided')
                        
                        df.at[idx, 'Domain_Classification'] = f'{domain} (conf: {confidence:.2f})'
                        df.at[idx, 'Should_Proceed'] = '✅ Yes' if should_proceed else '❌ No'
                        
                        print(f'      🏷️ Domain: {domain} (Confidence: {confidence:.2f})')
                        print(f'      🎯 Should Proceed: {should_proceed}')
                        if not should_proceed:
                            print(f'      💭 Reasoning: {reasoning[:80]}...')
                        
                    except Exception as e:
                        print(f'      ❌ Domain classification error: {e}')
                        df.at[idx, 'Domain_Classification'] = f'Error: {str(e)[:50]}'
                        df.at[idx, 'Should_Proceed'] = '❓ Error'
                        should_proceed = True  # Default for recommendation
                    
                    # Generate intelligent recommendation using BOTH specialists
                    location_ok = '✅' in df.at[idx, 'Location_Validated']
                    domain_proceed = '✅' in df.at[idx, 'Should_Proceed']
                    
                    if not location_ok:
                        recommendation = 'DO NOT APPLY - Location Conflict'
                    elif not domain_proceed:
                        recommendation = 'DO NOT APPLY - Domain Mismatch'
                    else:
                        recommendation = 'REVIEW REQUIRED - Passed Specialist Filtering'
                    
                    df.at[idx, 'Recommendation'] = recommendation
                    df.at[idx, 'Analysis_Notes'] = f'v1_1 specialist used at {datetime.now().strftime("%H:%M:%S")}'
                    
                else:
                    df.at[idx, 'Analysis_Notes'] = 'Job file not found'
                    print(f'      ❌ File not found: {job_file}')
                    
            except Exception as e:
                print(f'      ❌ Error analyzing {job_id}: {e}')
                df.at[idx, 'Analysis_Notes'] = f'Analysis error: {str(e)[:100]}'
        
        # Generate FIXED enhanced Excel report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        enhanced_path = f'reports/fresh_review/FIXED_enhanced_job_analysis_{timestamp}.xlsx'
        df.to_excel(enhanced_path, index=False, engine='openpyxl')
        
        print(f'\n✨ FIXED ENHANCED ANALYSIS COMPLETE!')
        print(f'📊 Enhanced report: {enhanced_path}')
        
        # Summary statistics
        total_jobs = len(df)
        location_conflicts = sum(df['Location_Validated'].str.contains('Conflict', na=False))
        domain_rejects = sum(df['Should_Proceed'].str.contains('No', na=False))
        do_not_apply = sum(df['Recommendation'].str.contains('DO NOT APPLY', na=False))
        
        print(f'\n📋 FIXED ANALYSIS SUMMARY:')
        print(f'   Total Jobs: {total_jobs}')
        print(f'   Location Conflicts: {location_conflicts} ({location_conflicts/total_jobs*100:.1f}%)')
        print(f'   Domain Rejects: {domain_rejects} ({domain_rejects/total_jobs*100:.1f}%)')
        print(f'   Total Do Not Apply: {do_not_apply} ({do_not_apply/total_jobs*100:.1f}%)')
        print(f'   Review Required: {total_jobs - do_not_apply}')
        
        print(f'\n🎯 NOW using WORKING v1_1 specialist - should see actual domain classification!')
        
        # Test our golden cases specifically
        print(f'\n🧪 GOLDEN CASE VALIDATION:')
        golden_jobs = ['60955', '58432', '63144']
        for job_id in golden_jobs:
            job_row = df[df['Job ID'] == job_id]
            if not job_row.empty:
                recommendation = job_row['Recommendation'].iloc[0]
                domain = job_row['Domain_Classification'].iloc[0]
                print(f'   Job {job_id}: {recommendation} | Domain: {domain}')
        
    except Exception as e:
        print(f'❌ Error in FIXED specialist analysis: {e}')
        print(f'🔍 Traceback: {traceback.format_exc()}')

if __name__ == "__main__":
    main()
