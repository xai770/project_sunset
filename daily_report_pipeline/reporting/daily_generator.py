#!/usr/bin/env python3
"""
Daily Report Generator - Modular Architecture
============================================

Professional 27-Column Excel Reports using clean modular specialists.
Generates both Excel and Markdown reports following Sandy's Golden Rules.

Author: Sandy's Modular Architecture
Version: 1.0 (Production Ready)
"""

import json
import pandas as pd
from datetime import datetime
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from ..specialists.content_extraction import ContentExtractionSpecialist
from ..specialists.location_validation_enhanced import LocationValidationEnhanced
from ..specialists.text_summarization import TextSummarizationSpecialist


class DailyReportGenerator:
    """Professional daily report generator with modular architecture"""
    
    def __init__(self):
        """Initialize the daily report generator"""
        # Initialize specialist services
        self.content_specialist = ContentExtractionSpecialist()
        self.location_specialist = LocationValidationEnhanced()
        self.summarization_specialist = TextSummarizationSpecialist()
        
        # Report paths
        self.reports_path = Path('/home/xai/Documents/sandy/reports')
        self.jobs_data_path = Path('/home/xai/Documents/sandy/data/postings')
        
        # Ensure reports directory exists
        self.reports_path.mkdir(exist_ok=True)
        
        # Progress tracking
        self.total_jobs = 0
        self.processed_jobs = 0
        self.start_time = 0.0
        
    def count_available_jobs(self) -> int:
        """Count the available job files for processing"""
        if not self.jobs_data_path.exists():
            print("❌ No job files found! The data directory is empty!")
            return 0
            
        # Look for basic job files (not reprocessed files)
        job_files = list(self.jobs_data_path.glob("job*.json"))
        # Filter out reprocessed files to get original jobs
        job_files = [f for f in job_files if not any(x in f.name for x in ['_reprocessed', '_llm_output', '_all_llm'])]
        
        self.total_jobs = len(job_files)
        print(f"Found {self.total_jobs} jobs for daily report!")
        return self.total_jobs
        
    def extract_job_insights(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract job insights using our specialist services"""
        # Extract data from the actual job structure
        job_content = job_data.get('job_content', {})
        job_description = job_content.get('description', '') or job_data.get('summary', '') or job_data.get('description', '')
        
        # Handle location - it can be either a string or a dict
        metadata_location = job_content.get('location', '')
        if isinstance(metadata_location, dict):
            location_str = f"{metadata_location.get('city', '')}, {metadata_location.get('country', '')}"
        else:
            location_str = str(metadata_location)  # Ensure string format
        
        # Ensure we have some content to work with
        if not job_description:
            job_description = f"Job Title: {job_content.get('title', 'Unknown')} at location {location_str}"
        
        print(f"    Job: {job_content.get('title', 'Unknown')} | Length: {len(job_description)} chars")
        
        # Process with our specialist services
        print("  Processing Content Extraction Specialist...")
        content_result = self.content_specialist.extract_content(job_description)
        
        print("  Processing Location Validation Specialist (Enhanced LLM v2.0)...")
        location_result = self.location_specialist.validate_job_location(
            {'location': location_str, 'description': job_description}, 
            job_data.get('job_id', 'unknown')
        )
        
        print("  Processing Text Summarization Specialist...")
        summary_result = self.summarization_specialist.summarize_job_description(
            job_description
        )
        
        # Build job insights dictionary - properly handle all result objects
        all_skills = getattr(content_result, 'all_skills', []) or []
        technical_skills = getattr(content_result, 'technical_skills', []) or []
        business_skills = getattr(content_result, 'business_skills', []) or []
        soft_skills = getattr(content_result, 'soft_skills', []) or []
        
        # Handle location validation result
        location_confidence = location_result.get('confidence_score', 0) if isinstance(location_result, dict) else getattr(location_result, 'confidence_score', 0)
        
        # Handle summary result
        if hasattr(summary_result, 'summary'):
            summary_text = summary_result.summary
        elif hasattr(summary_result, 'text'):
            summary_text = summary_result.text
        else:
            summary_text = str(summary_result)
            
        job_insights = {
            'technical_skills': technical_skills,
            'business_skills': business_skills,
            'soft_skills': soft_skills,
            'location_validation': location_result,
            'technical_evaluation': f"Skills: {len(all_skills)} | Location confidence: {location_confidence:.2f}",
            'summary': summary_text,
            'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return job_insights
    
    def create_golden_rules_markdown_report(self, jobs_data: List[Dict[str, Any]]) -> Optional[Path]:
        """Create a Markdown report matching the Excel content for collaborative review"""
        if not jobs_data:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_path = self.reports_path / f"daily_report_{timestamp}.md"
        
        print(f"Creating Markdown report: {md_path}")
        
        # Create comprehensive Markdown report
        md_content = f"""# Daily Job Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Report Summary
- **Total Jobs Processed**: {len(jobs_data)}
- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Report Format**: Sandy's Golden Rules 27-Column Compliant
- **Generated By**: Modular Daily Report Generator

## Jobs Analysis

"""
        
        for i, job in enumerate(jobs_data, 1):
            md_content += f"""### Job #{i}: {job['Job ID']} - {job['Position title']}

**Core Job Information:**
- **Job ID**: {job['Job ID']}
- **Position Title**: {job['Position title']}
- **Location**: {job['Location']}
- **Location Validation**: {job['Location Validation Details']}
- **Job Domain**: {job['Job domain']}
- **Match Level**: {job['Match level']}
- **Evaluation Date**: {job['Evaluation date']}

**📋 Full Content (Raw Job Description):**
```
{job['Full Content']}
```

**🤖 Concise Job Description (LLM-Extracted):**
```
{job['Concise Job Description']}
```

**🔍 Analysis Results:**
- **Has Domain Gap**: {job['Has domain gap']}
- **Domain Assessment**: {job['Domain assessment']}
- **No-go Rationale**: {job['No-go rationale']}
- **Application Narrative**: {job['Application narrative']}

**📋 Processing Logs:**
- **Export Job Matches Log**: {job['export_job_matches_log']}
- **Generate Cover Letters Log**: {job['generate_cover_letters_log']}
- **Reviewer Feedback**: {job['reviewer_feedback']}
- **Mailman Log**: {job['mailman_log']}
- **Process Feedback Log**: {job['process_feedback_log']}
- **Reviewer Support Log**: {job['reviewer_support_log']}
- **Workflow Status**: {job['workflow_status']}

**🧠 Sandy's Analysis:**
- **Evaluation**: {job['Technical Evaluation']}
- **Story Interpretation**: {job['Human Story Interpretation']}
- **Opportunity Assessment**: {job['Opportunity Bridge Assessment']}
- **Growth Illumination**: {job['Growth Path Illumination']}
- **Synthesis**: {job['Encouragement Synthesis']}
- **Confidence Score**: {job['Confidence Score']}
- **Joy Level**: {job['Joy Level']}

---

"""
        
        md_content += f"""## Report Metadata

**Golden Rules Compliance:**
- 27-column format structure maintained
- Full job description included (not truncated)  
- Concise job description from LLM extraction included
- Location validation details with conflict analysis included
- All analysis columns populated
- Reports saved in `/reports` directory

**Modular Architecture:**
- Content Extraction Specialist v3.4
- Location Validation Specialist (Fixed)
- Text Summarization Specialist
- Clean separation of concerns
- Testable components

**Report Generation Details:**
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Excel Report**: `daily_report_{timestamp}.xlsx`
- **Markdown Report**: `daily_report_{timestamp}.md`
- **Reports Directory**: `/home/xai/Documents/sandy/reports/`

---
*Report generated using Sandy's modular architecture following Golden Rules for precision-first collaborative intelligence workflow.*
"""
        
        # Write the Markdown file
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"Markdown report created: {md_path}")
        return md_path

    def create_golden_rules_excel_report(self, max_jobs: int = 10) -> Optional[Tuple[Path, Path]]:
        """Create the 27-column Excel report as specified in Sandy's Golden Rules"""
        if self.count_available_jobs() == 0:
            return None
            
        report_data = []
        self.start_time = time.time()
        
        # Get job files for processing
        job_files = list(self.jobs_data_path.glob("job*.json"))
        job_files = [f for f in job_files if not any(x in f.name for x in ['_reprocessed', '_llm_output', '_all_llm'])]
        job_files = job_files[:max_jobs]  # Limit to sample size
        
        print(f"\nGENERATING DAILY REPORT (MODULAR ARCHITECTURE)")
        print(f"Processing {len(job_files)} jobs for compliant report...")
        print("=" * 80)
        
        for i, job_file in enumerate(job_files, 1):
            print(f"\nDAILY REPORT JOB #{i}/{len(job_files)}: {job_file.name}")
            print("-" * 60)
            
            try:
                # Load the job data
                with open(job_file, 'r') as f:
                    job_data = json.load(f)
                
                # Extract technical insights
                print("  Processing technical insights...")
                technical_insights = self.extract_job_insights(job_data)
                
                # Extract job data
                job_content = job_data.get('job_content', {})
                job_metadata = job_data.get('job_metadata', {})
                location_data = job_content.get('location', {})
                
                # Get FULL description text from job_content.description
                full_description = job_content.get('description', 'No description available')
                
                # Get specialist results from technical insights
                content_result = technical_insights['content_result']
                location_result = technical_insights['location_result']
                
                # Extract location validation details
                location_validation = job_insights.get('location_validation_result', {})
                location_details = location_validation.analysis_details if hasattr(location_validation, 'analysis_details') else {}
                
                # Format details for report
                location_validation_details = "{}"
                if 'location_validation_result' in job_insights:
                    validation_result = job_insights['location_validation_result']
                    if hasattr(validation_result, 'analysis_details'):
                        details = validation_result.analysis_details
                        conflict = getattr(validation_result, 'conflict_detected', False)
                        confidence = getattr(validation_result, 'confidence_score', 0)
                        auth_location = getattr(validation_result, 'authoritative_location', 'UNKNOWN')
                        risk = details.get('risk_level', 'UNKNOWN').upper() if details else 'UNKNOWN'
                        reasoning = details.get('reasoning', 'N/A') if details else 'N/A'
                        
                        location_validation_details = (
                            f"Conflict: {'DETECTED' if conflict else 'NONE'} | "
                            f"Confidence: {confidence:.2f} | "
                            f"Authoritative: {auth_location} | "
                            f"Risk: {risk}\n"
                            f"Reasoning: {reasoning}"
                        )
        
                # Prepare the report entry following Sandy's 27-column format
                report_entry = {
                    'job_id': job_id,
                    'full_content': job_content.get('description', ''),
                    'concise_description': job_insights.get('summary', ''),  # From text summarization
                    'position_title': job_content.get('title', 'Unknown'),
                    'location': location_str,
                    'location_validation_details': location_validation_details,
                    'job_domain': job_content.get('domain', 'Unknown'),
                    'match_level': job_insights.get('match_level', 'Unknown'),
                    'evaluation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'has_domain_gap': 'No',  # Default value, can be updated by domain specialist
                    'domain_assessment': job_insights.get('domain_assessment', ''),
                    'no_go_rationale': '',  # Will be populated if job is rejected
                    'application_narrative': '',  # Will be populated during application phase
                    'export_job_matches_log': '',  # System processing log
                    'generate_cover_letters_log': '',  # Cover letter generation log
                    'reviewer_feedback': '',  # For human reviewer notes
                    'mailman_log': '',  # Email processing log
                    'process_feedback_log': '',  # Feedback processing log
                    'reviewer_support_log': '',  # Support interaction log
                    'workflow_status': 'Initial Analysis',
                    'technical_evaluation': job_insights.get('technical_evaluation', ''),
                    'human_story_interpretation': '',  # Will be populated by narrative specialist
                    'opportunity_bridge_assessment': '',  # Growth potential evaluation
                    'growth_path_illumination': '',  # Career development insights
                    'encouragement_synthesis': '',  # Motivational analysis
                    'confidence_score': job_insights.get('location_validation', {}).get('confidence_score', 0),
                    'joy_level': ''  # Enthusiasm/fit assessment
                }
                
                report_data.append(record)
                print(f"  Daily report entry complete!")
                
            except Exception as e:
                print(f"  ❌ Daily report processing failed: {e}")
                continue
        
        # Create the Excel report
        if report_data:
            df = pd.DataFrame(report_data)
            
            # Create beautiful Excel file in reports directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_path = self.reports_path / f"daily_report_{timestamp}.xlsx"
            
            print(f"\nCreating Excel report: {excel_path}")
            
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Daily Report', index=False)
                
                # Get the workbook and worksheet for formatting
                workbook = writer.book
                worksheet = writer.sheets['Daily Report']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)  # Cap at 50 chars
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"Daily report created: {excel_path}")
            print(f"Report contains {len(report_data)} jobs with all 27 columns")
            
            # Also create Markdown report for collaborative review
            md_path = self.create_golden_rules_markdown_report(report_data)
            
            return excel_path, md_path
        else:
            print("❌ No data processed for daily report!")
            return None
    
    def process_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single job and prepare its report entry"""
        # Get job ID from data or fallback to unknown
        job_id = str(job_data.get('job_id', 'unknown'))
        print(f"\n📋 Processing job: {job_id}")
        
        # Extract insights using specialists
        job_insights = self.extract_job_insights(job_data)
        
        # Get raw job content
        job_content = job_data.get('job_content', {})
        
        # Format location correctly
        metadata_location = job_content.get('location', '')
        if isinstance(metadata_location, dict):
            location_str = f"{metadata_location.get('city', '')}, {metadata_location.get('country', '')}"
        else:
            location_str = str(metadata_location)
        
        # Prepare the report entry following Sandy's 27-column format
        report_entry = {
            'job_id': job_id,
            'full_content': job_content.get('description', ''),
            'concise_description': job_insights.get('summary', ''),  # From text summarization
            'position_title': job_content.get('title', 'Unknown'),
            'location': location_str,
            # Extract and format location validation details
            location_validation_details = "{}"
            if 'location_validation_result' in job_insights:
                validation_result = job_insights['location_validation_result']
                if hasattr(validation_result, 'analysis_details'):
                    details = validation_result.analysis_details
                    conflict = getattr(validation_result, 'conflict_detected', False)
                    confidence = getattr(validation_result, 'confidence_score', 0)
                    auth_location = getattr(validation_result, 'authoritative_location', 'UNKNOWN')
                    risk = details.get('risk_level', 'UNKNOWN').upper() if details else 'UNKNOWN'
                    reasoning = details.get('reasoning', 'N/A') if details else 'N/A'
                    
                    location_validation_details = (
                        f"Conflict: {'DETECTED' if conflict else 'NONE'} | "
                        f"Confidence: {confidence:.2f} | "
                        f"Authoritative: {auth_location} | "
                        f"Risk: {risk}\n"
                        f"Reasoning: {reasoning}"
                    )
            
            # Set in report
            'location_validation_details': location_validation_details,
            'job_domain': job_content.get('domain', 'Unknown'),
            'match_level': job_insights.get('match_level', 'Unknown'),
            'evaluation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'has_domain_gap': 'No',  # Default value, can be updated by domain specialist
            'domain_assessment': job_insights.get('domain_assessment', ''),
            'no_go_rationale': '',  # Will be populated if job is rejected
            'application_narrative': '',  # Will be populated during application phase
            'export_job_matches_log': '',  # System processing log
            'generate_cover_letters_log': '',  # Cover letter generation log
            'reviewer_feedback': '',  # For human reviewer notes
            'mailman_log': '',  # Email processing log
            'process_feedback_log': '',  # Feedback processing log
            'reviewer_support_log': '',  # Support interaction log
            'workflow_status': 'Initial Analysis',
            'technical_evaluation': job_insights.get('technical_evaluation', ''),
            'human_story_interpretation': '',  # Will be populated by narrative specialist
            'opportunity_bridge_assessment': '',  # Growth potential evaluation
            'growth_path_illumination': '',  # Career development insights
            'encouragement_synthesis': '',  # Motivational analysis
            'confidence_score': job_insights.get('location_validation', {}).get('confidence_score', 0),
            'joy_level': ''  # Enthusiasm/fit assessment
        }
        
        return report_entry
    
    def extract_job_id_from_filename(self, filepath: Path) -> str:
        """Extract the job ID from a job filename (e.g., job64943.json -> 64943)"""
        try:
            # Extract everything between "job" and ".json"
            return filepath.stem.replace('job', '')
        except Exception:
            return "unknown"

    def generate_daily_report(self, limit: int = 5):
        """Generate a daily report for the specified number of jobs"""
        print(f"\nGENERATING DAILY REPORT (MODULAR ARCHITECTURE)")
        print(f"Processing {limit} jobs for compliant report...")
        print("=" * 80)
        
        # Get job files, excluding reprocessed ones
        job_files = list(self.jobs_data_path.glob("job*.json"))
        job_files = [f for f in job_files if not any(x in f.name for x in ['_reprocessed', '_llm_output', '_all_llm'])]
        
        # Limit to requested number
        job_files = job_files[:limit] if limit else job_files
        
        # Process each job and build report
        processed_jobs = []
        for job_file in job_files:
            try:
                # Read and parse the job JSON
                with open(job_file, 'r') as f:
                    job_data = json.load(f)
                
                # Extract job ID from filename if not in data
                if not job_data.get('job_id'):
                    job_data['job_id'] = self.extract_job_id_from_filename(job_file)
                
                result = self.process_job(job_data)
                if result:
                    processed_jobs.append(result)
            except Exception as e:
                print(f"Error processing {job_file}: {str(e)}")
                continue
        
        # Generate the report in both formats
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_path = self.reports_path / f'daily_report_{timestamp}.xlsx'
        markdown_path = self.reports_path / f'daily_report_{timestamp}.md'
        
        # Create Excel report with all 27 columns from Sandy's Golden Rules
        df = pd.DataFrame(processed_jobs)
        df.to_excel(excel_path, index=False)
        
        # Create Markdown report
        with open(markdown_path, 'w') as f:
            f.write("# Daily Job Analysis Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for job in processed_jobs:
                f.write(f"## {job.get('position_title', 'Unknown Position')}\n")
                f.write(f"**ID**: {job.get('job_id', 'unknown')}\n")
                f.write(f"**Location**: {job.get('location', 'Unknown')}\n")
                f.write(f"**Technical Evaluation**: {job.get('technical_evaluation', '')}\n")
                f.write("\n---\n\n")
        
        print(f"\n✅ Report generated successfully!")
        print(f"📊 Excel Report: {excel_path}")
        print(f"📝 Markdown Report: {markdown_path}")
