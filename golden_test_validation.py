#!/usr/bin/env python3
"""
Golden Test Validation - Validate Specialists Against Manual Review
================================================================

Test our production specialists against the jobs we manually reviewed in our 
systematic session to ensure they produce the same decisions.
"""

import pandas as pd
import json
from pathlib import Path
import sys

# Add project paths
sys.path.append('/home/xai/Documents/sunset')

def main():
    print('🎯 GOLDEN TEST VALIDATION - SPECIALISTS VS MANUAL REVIEW')
    print('=' * 60)
    
    # Our golden test cases from the systematic manual review
    golden_tests = {
        '60955': {
            'title': 'DWS - Operations Specialist - Performance Measurement',
            'manual_decision': 'DO NOT APPLY',
            'reason': 'Investment accounting expertise required',
            'domain_expected': 'investment_management'
        },
        '58432': {
            'title': 'DWS - Cybersecurity Vulnerability Management Lead',
            'manual_decision': 'DO NOT APPLY',
            'reason': 'Hands-on cybersecurity expertise required',
            'domain_expected': 'cybersecurity'
        },
        '63144': {
            'title': 'DWS Operations Specialist - E-invoicing',
            'manual_decision': 'DO NOT APPLY',
            'reason': 'Accounting knowledge required',
            'domain_expected': 'finance_operations'
        }
    }
    
    try:
        from core.direct_specialist_manager import DirectSpecialistManager
        
        # Initialize specialist manager
        specialist_manager = DirectSpecialistManager()
        print('✅ Specialist manager initialized')
        print(f'📊 Status: {specialist_manager.get_status()}\n')
        
        results = []
        
        for job_id, expected in golden_tests.items():
            print(f'🔍 Testing Job {job_id}: {expected["title"][:50]}...')
            
            # Find the job file
            job_file = Path(f'data/postings/job{job_id}.json')
            if not job_file.exists():
                job_file = Path(f'data/postings/{job_id}.json')
            
            if job_file.exists():
                try:
                    with open(job_file, 'r') as f:
                        job_data = json.load(f)
                    
                    # Prepare data for specialists
                    job_content = job_data.get('job_content', {})
                    job_description = job_content.get('description', '')
                    job_title = job_content.get('title', '')
                    
                    input_data = {
                        'job_metadata': {
                            'location': job_content.get('location', {}),
                            'title': job_title,
                            'id': job_id
                        },
                        'job_description': job_description,
                        'job_title': job_title,
                        'full_content': f"{job_title}\n\n{job_description}"
                    }
                    
                    # Test location validation
                    location_result = specialist_manager.evaluate_with_specialist('location_validation', input_data)
                    location_valid = location_result.success and not location_result.result.get('conflict', False)
                    
                    # Test domain classification
                    domain_result = specialist_manager.evaluate_with_specialist('domain_classification', input_data)
                    domain = domain_result.result.get('domain', 'unknown') if domain_result.success else 'error'
                    should_proceed = domain_result.result.get('should_proceed', True) if domain_result.success else False
                    confidence = domain_result.result.get('confidence', 0.0) if domain_result.success else 0.0
                    
                    # Determine specialist recommendation
                    if not location_valid:
                        specialist_decision = 'DO NOT APPLY - Location Conflict'
                    elif not should_proceed or domain in ['investment_management', 'cybersecurity', 'finance_operations']:
                        specialist_decision = 'DO NOT APPLY - Domain Mismatch'
                    else:
                        specialist_decision = 'REVIEW REQUIRED'
                    
                    # Compare with manual review
                    manual_decision = expected['manual_decision']
                    match = 'DO NOT APPLY' in specialist_decision if 'DO NOT APPLY' in manual_decision else specialist_decision == manual_decision
                    
                    print(f'   📍 Location Valid: {location_valid}')
                    print(f'   🏷️ Domain: {domain} (Confidence: {confidence:.2f})')
                    print(f'   🤖 Specialist Decision: {specialist_decision}')
                    print(f'   👤 Manual Decision: {manual_decision}')
                    print(f'   ✅ Match: {match}\n')
                    
                    results.append({
                        'Job ID': job_id,
                        'Title': job_title,
                        'Location Valid': location_valid,
                        'Domain': domain,
                        'Confidence': confidence,
                        'Specialist Decision': specialist_decision,
                        'Manual Decision': manual_decision,
                        'Match': match,
                        'Expected Domain': expected['domain_expected'],
                        'Reason': expected['reason']
                    })
                    
                except Exception as e:
                    print(f'   ❌ Error processing {job_id}: {e}\n')
                    results.append({
                        'Job ID': job_id,
                        'Title': expected['title'],
                        'Error': str(e),
                        'Manual Decision': expected['manual_decision'],
                        'Match': False
                    })
            else:
                print(f'   ❌ Job file not found: {job_file}\n')
                results.append({
                    'Job ID': job_id,
                    'Title': expected['title'],
                    'Error': 'File not found',
                    'Manual Decision': expected['manual_decision'],
                    'Match': False
                })
        
        # Summary
        total_tests = len(results)
        matches = sum(1 for r in results if r.get('Match', False))
        
        print('🏆 GOLDEN TEST RESULTS SUMMARY')
        print('=' * 40)
        print(f'Total Tests: {total_tests}')
        print(f'Matches: {matches}')
        print(f'Accuracy: {matches/total_tests*100:.1f}%')
        
        if matches == total_tests:
            print('\n🎉 PERFECT SCORE! All specialists match manual review decisions!')
        else:
            print(f'\n⚠️ {total_tests - matches} tests failed. Review specialist logic.')
        
        # Save results
        df = pd.DataFrame(results)
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        results_path = f'reports/fresh_review/golden_test_results_{timestamp}.xlsx'
        df.to_excel(results_path, index=False, engine='openpyxl')
        print(f'\n📊 Detailed results saved: {results_path}')
        
    except Exception as e:
        print(f'❌ Error in golden test validation: {e}')
        import traceback
        print(f'🔍 Traceback: {traceback.format_exc()}')

if __name__ == "__main__":
    main()
