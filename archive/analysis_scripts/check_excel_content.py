#!/usr/bin/env python3
"""
Simple Excel Content Checker
"""
import pandas as pd

try:
    # Load the latest Excel file
    df = pd.read_excel('reports/content_extraction_validation_20250624_200449.xlsx')
    
    print("📊 EXCEL CONTENT CHECK")
    print("=" * 50)
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    print(f"Job IDs: {df['Job ID'].tolist()}")
    
    # Check job 52953 specifically
    print("\n🔍 CHECKING JOB 52953:")
    job_52953 = df[df['Job ID'] == 52953]
    
    if len(job_52953) > 0:
        print("✅ Job 52953 found!")
        
        # Check the generate_cover_letters_log column
        log_content = job_52953['generate_cover_letters_log'].iloc[0]
        print(f"generate_cover_letters_log length: {len(str(log_content))}")
        print(f"First 200 chars: {str(log_content)[:200]}")
        
        # Check if it contains our expected content
        content_str = str(log_content)
        if "ORIGINAL MESSY CONTENT" in content_str:
            print("✅ Contains 'ORIGINAL MESSY CONTENT' prefix")
        else:
            print("❌ Missing 'ORIGINAL MESSY CONTENT' prefix")
            
        if "QA & Testing Engineer" in content_str:
            print("✅ Contains original job content")
        else:
            print("❌ Original job content not found")
            
    else:
        print("❌ Job 52953 not found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
