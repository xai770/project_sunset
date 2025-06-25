#!/usr/bin/env python3
"""
Domain Classification Debug - Deep Dive into Why Domain Classification Fails
===========================================================================

Debug the domain classification specialist to understand why it returns "unknown" 
for all jobs with 0.00 confidence.
"""

import json
from pathlib import Path
import sys

# Add project paths
sys.path.append('/home/xai/Documents/sunset')

def main():
    print('🔍 DOMAIN CLASSIFICATION SPECIALIST DEBUG')
    print('=' * 50)
    
    try:
        from core.direct_specialist_manager import DirectSpecialistManager
        
        # Initialize specialist manager
        specialist_manager = DirectSpecialistManager()
        print('✅ Specialist manager initialized\n')
        
        # Test with Job 58432 - Cybersecurity (should be easy to classify)
        job_id = '58432'
        job_file = Path(f'data/postings/job{job_id}.json')
        
        if job_file.exists():
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            job_content = job_data.get('job_content', {})
            job_description = job_content.get('description', '')
            job_title = job_content.get('title', '')
            
            print(f'📋 Testing Job: {job_title}')
            print(f'📄 Description length: {len(job_description)} characters')
            print(f'📝 First 200 chars: {job_description[:200]}...\n')
            
            # Try different input formats to see what works
            test_inputs = [
                {
                    'name': 'Basic Format',
                    'data': {
                        'job_description': job_description,
                        'job_title': job_title
                    }
                },
                {
                    'name': 'Full Metadata Format',
                    'data': {
                        'job_metadata': {
                            'location': job_content.get('location', {}),
                            'title': job_title,
                            'id': job_id
                        },
                        'job_description': job_description,
                        'job_title': job_title,
                        'full_content': f"{job_title}\n\n{job_description}"
                    }
                },
                {
                    'name': 'Title Only',
                    'data': {
                        'job_title': job_title,
                        'job_description': job_title  # Use title as description
                    }
                },
                {
                    'name': 'Simple Text',
                    'data': {
                        'text': f"{job_title} {job_description[:500]}"
                    }
                }
            ]
            
            for test_input in test_inputs:
                print(f'🧪 Testing {test_input["name"]}:')
                try:
                    result = specialist_manager.evaluate_with_specialist('domain_classification', test_input['data'])
                    
                    if result.success:
                        domain = result.result.get('domain', 'unknown')
                        confidence = result.result.get('confidence', 0.0)
                        should_proceed = result.result.get('should_proceed', True)
                        reasoning = result.result.get('reasoning', 'No reasoning provided')
                        
                        print(f'   ✅ Success: {domain} (confidence: {confidence:.2f})')
                        print(f'   🎯 Should proceed: {should_proceed}')
                        print(f'   💭 Reasoning: {reasoning[:100]}...')
                        
                        # If we get a good result, show full details
                        if confidence > 0.0 or domain != 'unknown':
                            print(f'   📊 Full result: {result.result}')
                    else:
                        print(f'   ❌ Failed: {result.error}')
                        
                except Exception as e:
                    print(f'   ❌ Exception: {e}')
                
                print()
            
            # Also test the specialist manager methods directly
            print('🔍 Testing specialist manager methods:')
            try:
                available_specialists = specialist_manager.list_available_specialists()
                print(f'   📋 Available specialists: {available_specialists}')
                
                status = specialist_manager.get_status()
                print(f'   📊 Status: {status}')
                
                # Check if there's a specific domain classification method
                if hasattr(specialist_manager, 'classify_domain'):
                    print('   🎯 Found classify_domain method, testing...')
                    domain_result = specialist_manager.classify_domain(job_data)
                    print(f'   📊 Direct classify_domain result: {domain_result}')
                    
            except Exception as e:
                print(f'   ❌ Error testing methods: {e}')
                
        else:
            print(f'❌ Job file not found: {job_file}')
    
    except Exception as e:
        print(f'❌ Error in domain classification debug: {e}')
        import traceback
        print(f'🔍 Traceback: {traceback.format_exc()}')

if __name__ == "__main__":
    main()
