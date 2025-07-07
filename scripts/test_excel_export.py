#!/usr/bin/env python3
"""
Test script for Excel export functionality.
"""
import json
from pathlib import Path
from datetime import datetime

from core.excel_exporter import ExcelExporter
from core.markdown_exporter import MarkdownExporter
from core.config_manager import get_config
from core.content_extraction_specialist import ContentExtractionSpecialistV33
from core.job_matching_api import JobMatchingAPI

def main():
    """Main test function"""
    config = get_config()
    
    # Initialize the specialists
    extractor = ContentExtractionSpecialistV33()
    job_matcher = JobMatchingAPI()
    
    # Get some test job data
    job_files = list(config.job_data_dir.glob("job*.json"))[:5]  # Test with first 5 jobs
    
    if not job_files:
        print("No job files found to test with!")
        return
    
    # Load job data
    matches = []
    for job_file in job_files:
        with open(job_file) as f:
            job_data = json.load(f)
            
            # Extract content and metadata
            content = job_data.get('job_content', {})
            metadata = job_data.get('job_metadata', {})
            location = content.get('location', {})
            
            # Generate concise description using the specialist
            raw_description = content.get('description', '')
            concise_description = extractor.extract_concise_description(raw_description) if raw_description else ''
            
            # Validate location
            metadata_location = f"{location.get('city', '')}, {location.get('state', '')}, {location.get('country', '')}".strip(', ')
            job_id = metadata.get('job_id', job_file.stem.replace('job', ''))
            
            location_result = job_matcher.validate_location(
                metadata_location=metadata_location,
                job_description=raw_description,
                job_id=job_id
            )
            location_validation = job_matcher.format_location_validation(location_result)
            
            matches.append({
                'Job ID': job_id,
                'Full Content': content.get('description', ''),
                'Concise Job Description': concise_description,
                'Position title': content.get('title', ''),
                'Location': metadata_location,
                'Location Validation Details': location_validation,
                'Job domain': content.get('domain', ''),
                'Match level': metadata.get('match_level', ''),
                'Evaluation date': metadata.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                'Has domain gap': metadata.get('has_domain_gap', ''),
                'Domain assessment': metadata.get('domain_assessment', ''),
                'No-go rationale': metadata.get('no_go_rationale', ''),
            })
    
    # Export to Excel
    excel_exporter = ExcelExporter(config)
    excel_path = excel_exporter.export_matches(
        matches, 
        Path(config.output_dir) / 'excel' / f'job_matches_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )
    print(f"Excel export completed: {excel_path}")
    
    # Export to Markdown
    markdown_exporter = MarkdownExporter(config)
    markdown_path = markdown_exporter.export_matches(
        matches, 
        Path(config.output_dir) / 'reports' / f'job_matches_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    )
    print(f"Markdown export completed: {markdown_path}")

if __name__ == '__main__':
    main()
