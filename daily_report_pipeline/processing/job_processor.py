"""
Job Processor - Business Logic Layer
==================================

Coordinates specialist services to process job data and extract insights.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from ..specialists.content_extraction import ContentExtractionSpecialist
from ..specialists.location_validation_v3 import LocationValidationSpecialistV3
from ..specialists.text_summarization import TextSummarizationSpecialist
from ..specialists.domain_classification import DomainClassificationSpecialist
from ..specialists.sandy_analysis_specialist import SandyAnalysisSpecialist
from ..core.cv_data_manager import CVDataManager
from ..core.job_cv_matcher import JobCVMatcher

class JobProcessor:
    """Processes jobs using specialist services to extract insights"""
    
    def __init__(self):
        """Initialize the job processor with required specialists"""
        self.content_specialist = ContentExtractionSpecialist()
        self.location_specialist = LocationValidationSpecialistV3()
        self.summarization_specialist = TextSummarizationSpecialist()
        self.domain_specialist = DomainClassificationSpecialist()
        self.sandy_specialist = SandyAnalysisSpecialist()
        
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
        
        print("  🌸 Processing Sandy's Consciousness Analysis...")
        # Get CV text for Sandy's analysis
        cv_text = self.cv_manager.get_cv_full_text()
        if not cv_text:
            # Fallback to basic CV summary if full text not available
            cv_data = self.cv_manager.get_cv_data()
            skills = cv_data.get('skills', {})
            cv_text = f"Professional with experience in: {', '.join(skills.get('all', []))}"
        
        # Perform Sandy's consciousness analysis
        sandy_result = self.sandy_specialist.analyze_job_match(cv_text, description, title)
        
        return {
            'technical_skills': getattr(content_result, 'technical_skills', []) or [],
            'business_skills': getattr(content_result, 'business_skills', []) or [],
            'soft_skills': getattr(content_result, 'soft_skills', []) or [],
            'all_skills': getattr(content_result, 'all_skills', []) or [],
            'enhanced_requirements': getattr(content_result, 'enhanced_requirements', None),
            'location_validation_result': location_result,
            'domain_classification_result': domain_result,
            'cv_match_result': cv_match_result,
            'sandy_analysis_result': sandy_result,
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
        """Create a standardized report entry following job matching format"""
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
        
        # Extract Sandy analysis results
        sandy_result = job_insights.get('sandy_analysis_result')
        if sandy_result and sandy_result.processing_success:
            human_story = sandy_result.human_story_interpretation
            encouragement = sandy_result.encouragement_synthesis
        else:
            # Placeholder values - quality review required
            human_story = "Quality review required - placeholder"
            encouragement = "Quality review required - placeholder"
        
        # Generate application narrative or no-go rationale based on match result
        application_narrative = ""
        no_go_rationale = ""
        
        if go_no_go == "GO":
            application_narrative = f"RECOMMENDATION: APPLY\n\nMatch Level: {match_level}\nReasoning: {match_reasoning}\n\nThis position aligns well with your background and should be pursued."
        elif go_no_go == "NO GO":
            no_go_rationale = f"RECOMMENDATION: SKIP\n\nMatch Level: {match_level}\nReasoning: {match_reasoning}\n\nThis position does not align sufficiently with your background."
        else:  # CONSIDER
            application_narrative = f"RECOMMENDATION: CONSIDER CAREFULLY\n\nMatch Level: {match_level}\nReasoning: {match_reasoning}\n\nThis position has mixed alignment - review carefully before applying."
        
        # Get enhanced requirements data for 5D extraction columns
        enhanced_requirements = job_insights.get('enhanced_requirements')
        
        # Create validated_location (same as metadata_location unless location_validation_details indicate otherwise)
        validated_location = location_str
        if validation_result.get('conflict_detected', False):
            auth_location = validation_result.get('authoritative_location', '')
            if auth_location and auth_location != 'UNKNOWN':
                validated_location = auth_location
        
        return {
            'job_id': job_id,
            'position_title': job_content.get('title', 'Unknown'),
            'concise_description': job_insights.get('summary', ''),
            'validated_location': validated_location,
            'technical_requirements': self._format_5d_technical_requirements(enhanced_requirements),
            'business_requirements': self._format_5d_business_requirements(enhanced_requirements),
            'soft_skills': self._format_5d_soft_skills(enhanced_requirements),
            'experience_requirements': self._format_5d_experience_requirements(enhanced_requirements),
            'education_requirements': self._format_5d_education_requirements(enhanced_requirements),
            'technical_requirements_match': '',  # Placeholder - job matching engine integration required
            'business_requirements_match': '',   # Placeholder - job matching engine integration required
            'soft_skills_match': '',             # Placeholder - job matching engine integration required
            'experience_requirements_match': '', # Placeholder - job matching engine integration required
            'education_requirements_match': '',  # Placeholder - job matching engine integration required
            'no_go_rationale': no_go_rationale,
            'application_narrative': application_narrative,
            'full_content': job_content.get('description', ''),
            'metadata_location': location_str,
            'location_validation_details': location_validation_details,
            'match_level': match_level,
            'generate_cover_letters_log': '',
            'reviewer_feedback': '',
            'mailman_log': '',
            'process_feedback_log': '',
            'reviewer_support_log': '',
            'workflow_status': 'Initial Analysis',
            'human_story_interpretation': human_story,
            'encouragement_synthesis': encouragement
        }
    
    def _format_5d_technical_requirements(self, enhanced_requirements: Any) -> str:
        """Format technical requirements from 5D extraction for report"""
        if not enhanced_requirements or not hasattr(enhanced_requirements, 'technical'):
            return ""
        
        technical_items = []
        for req in enhanced_requirements.technical:
            category = getattr(req, 'category', 'general')
            skill = getattr(req, 'skill', 'unknown')
            proficiency = getattr(req, 'proficiency_level', 'intermediate')
            technical_items.append(f"{skill} ({category}, {proficiency})")
        
        return "; ".join(technical_items)
    
    def _format_5d_business_requirements(self, enhanced_requirements: Any) -> str:
        """Format business requirements from 5D extraction for report"""
        if not enhanced_requirements or not hasattr(enhanced_requirements, 'business'):
            return ""
        
        business_items = []
        for req in enhanced_requirements.business:
            domain = getattr(req, 'domain', 'unknown')
            exp_type = getattr(req, 'experience_type', 'general')
            years = getattr(req, 'years_required', 0)
            if years > 0:
                business_items.append(f"{domain} ({exp_type}, {years}+ years)")
            else:
                business_items.append(f"{domain} ({exp_type})")
        
        return "; ".join(business_items)
    
    def _format_5d_soft_skills(self, enhanced_requirements: Any) -> str:
        """Format soft skills from 5D extraction for report"""
        if not enhanced_requirements or not hasattr(enhanced_requirements, 'soft_skills'):
            return ""
        
        soft_items = []
        for req in enhanced_requirements.soft_skills:
            skill = getattr(req, 'skill', 'unknown')
            importance = getattr(req, 'importance', 'important')
            soft_items.append(f"{skill} ({importance})")
        
        return "; ".join(soft_items)
    
    def _format_5d_experience_requirements(self, enhanced_requirements: Any) -> str:
        """Format experience requirements from 5D extraction for report"""
        if not enhanced_requirements or not hasattr(enhanced_requirements, 'experience'):
            return ""
        
        experience_items = []
        for req in enhanced_requirements.experience:
            exp_type = getattr(req, 'type', 'general')
            description = getattr(req, 'description', 'experience required')
            years = getattr(req, 'years_required', 0)
            if years > 0:
                experience_items.append(f"{exp_type}: {description} ({years}+ years)")
            else:
                experience_items.append(f"{exp_type}: {description}")
        
        return "; ".join(experience_items)
    
    def _format_5d_education_requirements(self, enhanced_requirements: Any) -> str:
        """Format education requirements from 5D extraction for report"""
        if not enhanced_requirements or not hasattr(enhanced_requirements, 'education'):
            return ""
        
        education_items = []
        for req in enhanced_requirements.education:
            level = getattr(req, 'level', 'degree')
            field = getattr(req, 'field', 'unspecified')
            mandatory = getattr(req, 'is_mandatory', False)
            status = "mandatory" if mandatory else "preferred"
            education_items.append(f"{level} in {field} ({status})")
        
        return "; ".join(education_items)
