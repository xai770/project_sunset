#!/usr/bin/env python3
"""
Run Pipeline Batch Script
========================

Run the job processing pipeline on a batch of 10 jobs.
"""

import logging
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from daily_report_pipeline.processing.job_processor import JobProcessor
from core.job_matching_specialists import DirectJobMatchingSpecialists
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_jobs(data_dir: str = 'data/postings', max_jobs: int = 10) -> List[Dict[str, Any]]:
    """Load jobs from data directory."""
    jobs = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return jobs
        
    for job_file in data_path.glob('job*.json'):
        if len(jobs) >= max_jobs:
            break
            
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                
                # Extract relevant fields from nested structure
                job_data = {
                    'id': raw_data['job_metadata']['job_id'],
                    'title': raw_data['job_content']['title'],
                    'description': raw_data['job_content']['description'],
                    'company': raw_data['job_content']['organization']['name'],
                    'location': raw_data['job_content']['location']['city']
                }
                
                if job_data['location'] and raw_data['job_content']['location'].get('country'):
                    job_data['location'] = f"{job_data['location']}, {raw_data['job_content']['location']['country']}"
                
                jobs.append(job_data)
                logger.info(f"Loaded job {job_data['id']}: {job_data['title']}")
        except Exception as e:
            logger.error(f"Error loading {job_file}: {e}")
            
    return jobs

def save_results(results: List[Dict[str, Any]], output_dir: str = 'reports'):
    """Save processing results to JSON, Excel and generate summary."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save detailed JSON results
    json_path = output_path / f'job_processing_results_{timestamp}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved detailed results to {json_path}")
    
    # Create Excel report
    excel_path = output_path / f'job_processing_results_{timestamp}.xlsx'
    df = pd.DataFrame(results)
    
    # Reorder columns for better readability
    columns_order = [
        'job_id', 'title', 'company', 
        'domain', 'domain_confidence', 'domain_signals', 'domain_assessment',
        'location', 'location_validation', 'location_confidence',
        'match_score', 'match_details', 
        'proceed'
    ]
    # Only include columns that exist in the results
    columns = [col for col in columns_order if col in df.columns]
    df = df[columns]
    
    # Format specific columns
    if 'domain_confidence' in df.columns:
        df['domain_confidence'] = df['domain_confidence'].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "N/A")
    if 'location_confidence' in df.columns:
        df['location_confidence'] = df['location_confidence'].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "N/A")
    if 'match_score' in df.columns:
        df['match_score'] = df['match_score'].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "N/A")
    if 'domain_signals' in df.columns:
        df['domain_signals'] = df['domain_signals'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))
    if 'proceed' in df.columns:
        df['proceed'] = df['proceed'].apply(lambda x: '✅' if x else '❌')
    
    # Save to Excel with formatting
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Job Processing Results')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Job Processing Results']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
    
    logger.info(f"Saved Excel report to {excel_path}")
    
    # Generate markdown summary
    summary = ["# Job Processing Results Summary", "", f"Processing Date: {timestamp}", ""]
    
    for result in results:
        job_id = result.get('job_id', 'unknown')
        title = result.get('title', 'No title')
        domain = result.get('domain', 'unknown')
        confidence = result.get('domain_confidence', 0)
        proceed = '✅' if result.get('proceed', False) else '❌'
        
        summary.append(f"## Job {job_id}: {title}")
        summary.append(f"- Domain: {domain} (Confidence: {confidence:.1f}%)")
        summary.append(f"- Proceed: {proceed}")
        summary.append("")
        
    md_path = output_path / f'job_processing_summary_{timestamp}.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary))
    logger.info(f"Saved summary to {md_path}")

def main():
    """Main entry point for running the pipeline batch."""
    try:
        # Initialize specialists and processor
        specialist = DirectJobMatchingSpecialists()
        processor = JobProcessor(specialist)
        
        # Load jobs
        jobs = load_jobs(max_jobs=10)
        if not jobs:
            logger.error("No jobs loaded, exiting")
            return
            
        # Process jobs
        results = processor.process_batch(jobs)
        
        # Save results
        save_results(results)
        
    except Exception as e:
        logger.error(f"Pipeline batch processing failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
