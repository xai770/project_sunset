#!/usr/bin/env python3
"""
Pipeline Test Runner
==================

Runs the job processing pipeline with 10 test jobs to verify:
1. Domain classification
2. Location validation
3. Excel and Markdown report generation
"""

import logging
from pathlib import Path
import json
from datetime import datetime
from daily_report_pipeline.processing.job_processor import JobProcessor
from core.excel_exporter import ExcelExporter
from core.markdown_exporter import MarkdownExporter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_test_jobs(data_dir: str = 'data/postings', max_jobs: int = 10):
    """Load test jobs from the data directory."""
    jobs = []
    job_dir = Path(data_dir)
    
    if not job_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return jobs

    # Load all job files
    for job_file in job_dir.glob('job*.json'):
        if len(jobs) >= max_jobs:
            break
            
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
                # Extract id from filename (job12345.json -> 12345)
                job_id = job_file.stem.replace('job', '')
                job_data['job_id'] = job_id  # Use 'job_id' to match processor expectations
                jobs.append(job_data)
                logger.info(f"Loaded job {job_id}")
        except Exception as e:
            logger.error(f"Error loading {job_file}: {e}")
            continue

    return jobs

def export_reports(results, timestamp=None):
    """Export results to Excel and Markdown formats."""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    # Ensure output directories exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Export Excel report
    excel_exporter = ExcelExporter()
    excel_path = output_dir / f"job_matches_{timestamp}.xlsx"
    excel_exporter.export_matches(results, excel_path)
    logger.info(f"Excel report saved to: {excel_path}")
    
    # Export Markdown report
    markdown_exporter = MarkdownExporter()
    md_path = output_dir / f"job_matches_{timestamp}.md"
    markdown_exporter.export_matches(results, md_path)
    logger.info(f"Markdown report saved to: {md_path}")
    
    # Save raw JSON results
    json_path = output_dir / f"job_matches_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    logger.info(f"JSON results saved to: {json_path}")

def main():
    """Run the pipeline test."""
    logger.info("Starting pipeline test with 10 jobs")
    
    # Initialize processor
    processor = JobProcessor()
    
    # Load test jobs
    jobs = load_test_jobs(max_jobs=10)
    if not jobs:
        logger.error("No jobs loaded. Aborting.")
        return
    
    logger.info(f"Loaded {len(jobs)} jobs for processing")
    
    # Process jobs in a batch
    try:
        results = []
        for job in jobs:
            result = processor.process_job(job)
            results.append(result)
            
        # Export all reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_reports(results, timestamp)
    except Exception as e:
        logger.error(f"Error processing jobs: {e}", exc_info=True)
        return
    
    # Print results summary
    print("\nResults Summary:")
    print("=" * 50)
    for result in results:
        job_id = result.get('job_id', 'unknown')
        if 'error' in result:
            print(f"❌ Job {job_id}: {result['error']}")
            continue
            
        domain = result.get('domain', 'unknown')
        confidence = result.get('domain_confidence', 0)
        location_valid = result.get('location_validation', {}).get('is_valid', False)
        proceed = result.get('proceed', False)
        
        status = "✅" if proceed else "❌"
        print(f"{status} Job {job_id}:")
        print(f"   Domain: {domain} ({confidence:.1f}% confidence)")
        print(f"   Location: {'Valid' if location_valid else 'Invalid'}")
        print(f"   Proceed: {proceed}")
        print()

if __name__ == "__main__":
    main()
