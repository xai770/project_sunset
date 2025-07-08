"""
Job Processor - Business Logic Layer
==================================

Coordinates specialist services to process job data and extract insights.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from ..specialists.content_extraction import ContentExtractionSpecialist
from ..specialists.location_validation_enhanced import LocationValidationEnhanced
from ..specialists.text_summarization import TextSummarizationSpecialist
from ..specialists.domain_classification import DomainClassificationSpecialist

class JobProcessor:
    """Processes jobs using specialist services to extract insights"""
    
    def __init__(self):
        """Initialize the job processor with required specialists"""
        self.content_specialist = ContentExtractionSpecialist()
        self.location_specialist = LocationValidationEnhanced()
        self.summarization_specialist = TextSummarizationSpecialist()
        self.domain_specialist = DomainClassificationSpecialist()

    def process_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single job to extract insights
        
        Args:
            job_data: Raw job data dictionary
            
        Returns:
            Dictionary containing processed job data and insights
        """
        # Get job ID and content
        job_id = str(job_data.get('job_id', 'unknown'))
        job_content = job_data.get('job_content', {})
        
        # Extract and normalize job description
        job_description = self._get_job_description(job_content)
        location_str = self._format_location(job_content.get('location', ''))
        
        print(f"\n📋 Processing job: {job_id}")
        print(f"    Job: {job_content.get('title', 'Unknown')} | Length: {len(job_description)} chars")
        
        # Get insights from specialists
        job_title = job_content.get('title', 'Unknown')
        job_insights = self._extract_job_insights(job_description, location_str, job_id, job_title)
        
        # Format location validation details
        location_validation_details = self._format_location_validation(job_insights)
        
        # Prepare standardized report entry
        return self._create_report_entry(job_id, job_content, job_insights, location_str, location_validation_details)
    
    def _get_job_description(self, job_content: Dict[str, Any]) -> str:
        """Extract and normalize job description from content"""
        description = (
            job_content.get('description', '') or 
            job_content.get('summary', '') or 
            job_content.get('description', '')
        )
        
        if not description:
            description = f"Job Title: {job_content.get('title', 'Unknown')} at location {self._format_location(job_content.get('location', ''))}"
        
        return description
    
    def _format_location(self, location: Any) -> str:
        """Format location data consistently"""
        if isinstance(location, dict):
            return f"{location.get('city', '')}, {location.get('country', '')}"
        return str(location)
    
    def _extract_job_insights(self, description: str, location: str, job_id: str, title: str) -> Dict[str, Any]:
        """Extract insights using specialist services"""
        print("  Processing Content Extraction Specialist...")
        content_result = self.content_specialist.extract_content(description)
        
        print("  Processing Location Validation Specialist (Enhanced LLM v2.0)...")
        location_result = self.location_specialist.validate_job_location(
            {'location': location, 'description': description}, 
            job_id
        )
        
        print("  Processing Domain Classification Specialist (v1.1)...")
        domain_result = self.domain_specialist.classify_domain({
            'job_description': description,
            'job_metadata': {'title': title, 'id': job_id}
        })
        
        print("  Processing Text Summarization Specialist...")
        summary_result = self.summarization_specialist.summarize_job_description(description)
        
        return {
            'technical_skills': getattr(content_result, 'technical_skills', []) or [],
            'business_skills': getattr(content_result, 'business_skills', []) or [],
            'soft_skills': getattr(content_result, 'soft_skills', []) or [],
            'all_skills': getattr(content_result, 'all_skills', []) or [],
            'location_validation_result': location_result,
            'domain_classification_result': domain_result,
            'summary': self._get_summary_text(summary_result),
            'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _get_summary_text(self, summary_result: Any) -> str:
        """Extract summary text from summary result object"""
        if hasattr(summary_result, 'summary'):
            return summary_result.summary
        elif hasattr(summary_result, 'text'):
            return summary_result.text
        return str(summary_result)
    
    def _format_location_validation(self, job_insights: Dict[str, Any]) -> str:
        """Format location validation details for report"""
        validation_result = job_insights.get('location_validation_result', {})
        if not validation_result or not isinstance(validation_result, dict):
            return "{}"
            
        # Get fields from the root level where the Enhanced specialist puts them
        conflict = validation_result.get('conflict_detected', False)
        confidence = validation_result.get('confidence_score', 0)
        auth_location = validation_result.get('authoritative_location', 'UNKNOWN')
        risk = validation_result.get('risk_level', 'UNKNOWN').upper()
        reasoning = validation_result.get('reasoning', 'N/A')
        extracted_locs = ', '.join(validation_result.get('extracted_locations', []))
        metadata_accurate = validation_result.get('metadata_location_accurate', False)
        processing_time = validation_result.get('processing_time', 0)
        specialist_version = validation_result.get('specialist_version', 'UNKNOWN')
        
        # Format multi-line validation details with all relevant information
        details = []
        details.append(f"Metadata Location Accurate: {'YES' if metadata_accurate else 'NO'}")
        details.append(f"Conflict: {'DETECTED' if conflict else 'NONE'}")
        details.append(f"Confidence: {confidence:.2f}")
        details.append(f"Risk Level: {risk}")
        details.append(f"Processing Time: {processing_time:.2f}s")
        details.append(f"Specialist Version: {specialist_version}")
        details.append(f"\nAuthoritative Location: {auth_location}")
        details.append(f"Found Locations: {extracted_locs}")
        details.append(f"\nReasoning: {reasoning}")
        
        # Join details with newlines for readability
        return '\n'.join(details)
    
    def _create_report_entry(
        self, 
        job_id: str,
        job_content: Dict[str, Any],
        job_insights: Dict[str, Any],
        location_str: str,
        location_validation_details: str
    ) -> Dict[str, Any]:
        """Create a standardized report entry following Sandy's 27-column format"""
        all_skills = job_insights.get('all_skills', [])
        validation_result = job_insights.get('location_validation_result', {})
        confidence = getattr(validation_result, 'confidence_score', 0)
        
        return {
            'job_id': job_id,
            'full_content': job_content.get('description', ''),
            'concise_description': job_insights.get('summary', ''),
            'position_title': job_content.get('title', 'Unknown'),
            'location': location_str,
            'location_validation_details': location_validation_details,
            'job_domain': job_content.get('domain', 'Unknown'),
            'match_level': job_insights.get('match_level', 'Unknown'),
            'evaluation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'has_domain_gap': 'No',
            'domain_assessment': job_insights.get('domain_assessment', ''),
            'no_go_rationale': '',
            'application_narrative': '',
            'export_job_matches_log': '',
            'generate_cover_letters_log': '',
            'reviewer_feedback': '',
            'mailman_log': '',
            'process_feedback_log': '',
            'reviewer_support_log': '',
            'workflow_status': 'Initial Analysis',
            'technical_evaluation': f"Skills: {len(all_skills)} | Location confidence: {confidence:.2f}",
            'human_story_interpretation': '',
            'opportunity_bridge_assessment': '',
            'growth_path_illumination': '',
            'encouragement_synthesis': '',
            'confidence_score': confidence,
            'joy_level': ''
        }
