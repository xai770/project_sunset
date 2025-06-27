"""
Excel Handlers Module for JMFS

Contains methods for processing Excel files and updating rows
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

import pandas as pd

# Configure logging
logger = logging.getLogger("jmfs.feedback.excel_handlers")

def extract_jobs_with_feedback(df):
    """
    Extract jobs with feedback from Excel dataframe.
    
    Args:
        df: Pandas DataFrame with job data
        
    Returns:
        List of dictionaries with job data including feedback
    """
    jobs_with_feedback = []
    
    for idx, row in df.iterrows():
        feedback = str(row.get('reviewer_feedback', '')).strip()
        if feedback and feedback.lower() not in ['', 'nan', 'none']:
            # Extract job data from row
            job_data = {
                'row_index': idx,
                'job_id': str(row.get('job_id', '')),
                'position_title': str(row.get('position_title', '')),
                'match_level': str(row.get('match_level', '')),
                'reviewer_feedback': feedback,
                'domain_assessment': str(row.get('domain_assessment', '')),
                'job_description': str(row.get('job_description', ''))
            }
            jobs_with_feedback.append(job_data)
            
    return jobs_with_feedback

def update_excel_row(df, row_index, result):
    """
    Update Excel row with processing results.
    
    Args:
        df: Pandas DataFrame with job data
        row_index: Index of the row to update
        result: Dictionary with processing results
        
    Returns:
        None (updates DataFrame in place)
    """
    # Update column P (process_feedback_log)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp}: {result.get('log_message', '')}"
    
    # Check if column exists and create if needed
    if 'process_feedback_log' not in df.columns:
        df['process_feedback_log'] = ""
    
    # Append log entry to existing log content
    existing_log = str(df.at[row_index, 'process_feedback_log'])
    if existing_log and existing_log.lower() not in ['nan', 'none', '']:
        log_entry = f"{existing_log}\n{log_entry}"
    
    df.at[row_index, 'process_feedback_log'] = log_entry
    
    # Update column R (workflow_status)
    if 'workflow_status' not in df.columns:
        df['workflow_status'] = ""
        
    if result.get('status') == 'success':
        df.at[row_index, 'workflow_status'] = 'Feedback Processed'
    elif result.get('status') == 'error':
        df.at[row_index, 'workflow_status'] = 'Processing Error'
    else:
        df.at[row_index, 'workflow_status'] = 'Feedback Reviewed'
