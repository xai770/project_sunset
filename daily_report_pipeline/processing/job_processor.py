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
from ..core.cv_data_manager import CVDataManager
from ..core.job_cv_matcher import JobCVMatcher

class JobProcessor:
    """Processes jobs using specialist services to extract insights"""
    
    def __init__(self):
        """Initialize the job processor with required specialists"""
        self.content_specialist = ContentExtractionSpecialist()
        self.location_specialist = LocationValidationEnhanced()
        self.summarization_specialist = TextSummarizationSpecialist()
        self.domain_specialist = DomainClassificationSpecialist()
        
        # Initialize CV matching components
        self.cv_manager = CVDataManager()
        self.job_cv_matcher = JobCVMatcher(self.cv_manager)

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
        
        print("  Processing CV-Job Matching Engine...")
        # Prepare job data for CV matching
        job_match_data = {
            'technical_skills': getattr(content_result, 'technical_skills', []) or [],
            'business_skills': getattr(content_result, 'business_skills', []) or [],
            'all_skills': getattr(content_result, 'all_skills', []) or [],
            'domain_classification_result': domain_result,
            'full_content': description,
            'job_description': description
        }
        
        cv_match_result = self.job_cv_matcher.calculate_match_score(job_match_data)
        
        return {
            'technical_skills': getattr(content_result, 'technical_skills', []) or [],
            'business_skills': getattr(content_result, 'business_skills', []) or [],
            'soft_skills': getattr(content_result, 'soft_skills', []) or [],
            'all_skills': getattr(content_result, 'all_skills', []) or [],
            'location_validation_result': location_result,
            'domain_classification_result': domain_result,
            'cv_match_result': cv_match_result,
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
    
    def _format_domain_assessment(self, domain_result: Dict[str, Any]) -> str:
        """Format domain classification details for report"""
        if not domain_result:
            return "Domain classification not available"
            
        primary_domain = domain_result.get('primary_domain', 'Unknown')
        confidence = domain_result.get('confidence', 0.0)
        reasoning = domain_result.get('reasoning', 'N/A')
        should_proceed = domain_result.get('should_proceed', True)
        specialist_version = domain_result.get('specialist_version', 'Unknown')
        domain_requirements = domain_result.get('domain_requirements', [])
        domain_gaps = domain_result.get('domain_gaps', [])
        
        # Format comprehensive domain assessment
        assessment_lines = []
        assessment_lines.append(f"Primary Domain: {primary_domain}")
        assessment_lines.append(f"Confidence: {confidence:.2f}")
        assessment_lines.append(f"Should Proceed: {'YES' if should_proceed else 'NO'}")
        assessment_lines.append(f"Specialist Version: {specialist_version}")
        
        if domain_requirements:
            assessment_lines.append(f"\nDomain Requirements: {', '.join(domain_requirements)}")
        
        if domain_gaps:
            assessment_lines.append(f"Domain Gaps: {', '.join(domain_gaps)}")
            
        assessment_lines.append(f"\nReasoning: {reasoning}")
        
        return '\n'.join(assessment_lines)
    
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
        
        # Extract domain classification results
        domain_result = job_insights.get('domain_classification_result', {})
        job_domain = domain_result.get('primary_domain', 'Unknown')
        domain_confidence = domain_result.get('confidence', 0.0)
        domain_reasoning = domain_result.get('reasoning', '')
        should_proceed = domain_result.get('should_proceed', True)
        
        # Extract CV match results
        cv_match = job_insights.get('cv_match_result', {})
        match_level = cv_match.get('match_level', 'Unknown')
        go_no_go = cv_match.get('go_no_go', 'Unknown')
        match_reasoning = cv_match.get('reasoning', '')
        
        # Format enhanced domain assessment
        domain_assessment = self._format_domain_assessment(domain_result)
        
        # Generate application narrative or no-go rationale based on match result
        application_narrative = ""
        no_go_rationale = ""
        
        if go_no_go == "GO":
            application_narrative = f"RECOMMENDATION: APPLY\n\nMatch Level: {match_level}\nReasoning: {match_reasoning}\n\nThis position aligns well with your background and should be pursued."
        elif go_no_go == "NO GO":
            no_go_rationale = f"RECOMMENDATION: SKIP\n\nMatch Level: {match_level}\nReasoning: {match_reasoning}\n\nThis position does not align sufficiently with your background."
        else:  # CONSIDER
            application_narrative = f"RECOMMENDATION: CONSIDER CAREFULLY\n\nMatch Level: {match_level}\nReasoning: {match_reasoning}\n\nThis position has mixed alignment - review carefully before applying."
        
        return {
            'job_id': job_id,
            'full_content': job_content.get('description', ''),
            'concise_description': job_insights.get('summary', ''),
            'position_title': job_content.get('title', 'Unknown'),
            'location': location_str,
            'location_validation_details': location_validation_details,
            'job_domain': job_domain,
            'match_level': match_level,
            'evaluation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'has_domain_gap': 'Yes' if not should_proceed else 'No',
            'domain_assessment': domain_assessment,
            'no_go_rationale': no_go_rationale,
            'application_narrative': application_narrative,
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
