#!/usr/bin/env python3
"""
Job Matching API - Phase 5 Modern Architecture
==============================================

Clean, production-ready API interface for AI-powered job matching.
"""

from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass
from .direct_specialist_manager import DirectSpecialistManager
from datetime import datetime
from pathlib import Path
from .config_manager import get_config
from .location_validation_specialist_llm import LocationValidationSpecialistLLM, LocationValidationResult

logger = logging.getLogger(__name__)

@dataclass
class JobMatchRequest:
    """Request structure for job matching"""
    candidate_profile: Dict[str, Any]
    job_requirements: Dict[str, Any]
    additional_context: Optional[Dict[str, Any]] = None

@dataclass
class JobMatchResponse:
    """Response structure for job matching results"""
    success: bool
    match_score: float
    analysis: Dict[str, Any]
    recommendations: List[str]
    processing_time: float
    error_message: Optional[str] = None

class JobMatchingAPI:
    """
    Clean, production-ready API for job matching using DirectSpecialistManager
    """
    
    def __init__(self):
        """Initialize with DirectSpecialistManager and LocationValidationSpecialist"""
        self.specialist_manager = DirectSpecialistManager()
        self.location_specialist = LocationValidationSpecialistLLM()
        logger.info("✅ JobMatchingAPI initialized with DirectSpecialistManager and LocationValidationSpecialist")
    
    def validate_location(self, metadata_location: str, job_description: str, job_id: str) -> LocationValidationResult:
        """
        Validate the job location using the location validation specialist
        
        Args:
            metadata_location: The location from job metadata
            job_description: The full job description text
            job_id: Unique identifier for the job
            
        Returns:
            LocationValidationResult with the analysis
        """
        return self.location_specialist.validate_location(
            metadata_location=metadata_location,
            job_description=job_description,
            job_id=job_id
        )

    def format_location_validation(self, result: LocationValidationResult) -> str:
        """Format location validation results according to Sandy's golden rules"""
        # Get the analysis details
        details = result.analysis_details
        conflict_type = details.get('conflict_type', 'unknown')
        risk_level = details.get('risk_level', 'unknown')
        reasoning = details.get('reasoning', '')
        metadata_location = details.get('metadata_location', '')
        extracted_locations = details.get('extracted_locations', [])
        
        # Get just the primary location without state/country if possible
        primary_loc = next((loc for loc in extracted_locations if metadata_location.startswith(loc)), metadata_location)
        other_locs = [loc for loc in extracted_locations if loc != primary_loc]
        
        # Format status with emphasis
        status = "⚠️ CONFLICT" if result.conflict_detected else "✅ VALID"
        risk = {
            'critical': '❗HIGH RISK',
            'high': '⚠️ MEDIUM RISK',
            'medium': '⚠️ MEDIUM RISK',
            'low': '✅ LOW RISK',
        }.get(risk_level.lower(), f"❓ {risk_level.upper()}")

        # Format the main validation details
        validation = [
            f"Status: {status}",
            f"Risk: {risk}",
            f"Primary Location: {primary_loc}",
            f"Listed Location: {metadata_location}"
        ]
        
        # Add other mentioned locations if any
        if other_locs:
            validation.append(f"Also Mentioned: {', '.join(other_locs)}")
        
        # Add confidence score
        validation.append(f"Confidence: {int(result.confidence_score)}%")
        
        # Add a focused analysis summary
        if reasoning:
            key_points = reasoning.split('.')
            if key_points:
                main_point = key_points[0].strip()
                if len(main_point) > 100:
                    main_point = main_point[:97] + "..."
                validation.append(f"Analysis: {main_point}")

        # Log the details for debugging
        logger.info(f"Location validation details for job {result.job_id}:")
        logger.info(f"Result: {result}")
        logger.info(f"Analysis details: {details}")
        logger.info(f"Formatted output: {' | '.join(validation)}")
            
        return " | ".join(validation)

    def match_job(self, request: JobMatchRequest) -> JobMatchResponse:
        """
        Primary job matching endpoint
        
        Args:
            request: JobMatchRequest with candidate and job data
            
        Returns:
            JobMatchResponse with matching results
        """
        try:
            import time
            start_time = time.time()
            
            # Use DirectSpecialistManager for job fitness evaluation
            result = self.specialist_manager.evaluate_with_specialist(
                specialist_name="job_fitness_evaluator",
                input_data={
                    "candidate_profile": request.candidate_profile,
                    "job_requirements": request.job_requirements,
                    "additional_context": request.additional_context or {}
                }
            )
            
            processing_time = time.time() - start_time
            
            if result.success:
                # Extract match score and analysis from specialist result
                analysis = result.result
                match_score = analysis.get("overall_score", 0.0) if isinstance(analysis, dict) else 0.0
                recommendations = analysis.get("recommendations", []) if isinstance(analysis, dict) else []
                
                return JobMatchResponse(
                    success=True,
                    match_score=match_score,
                    analysis=analysis if isinstance(analysis, dict) else {"result": str(analysis)},
                    recommendations=recommendations,
                    processing_time=processing_time
                )
            else:
                return JobMatchResponse(
                    success=False,
                    match_score=0.0,
                    analysis={},
                    recommendations=[],
                    processing_time=processing_time,
                    error_message=f"Specialist evaluation failed: {result.error}"
                )
                
        except Exception as e:
            logger.error(f"❌ Job matching failed: {e}")
            return JobMatchResponse(
                success=False,
                match_score=0.0,
                analysis={},
                recommendations=[],
                processing_time=0.0,
                error_message=str(e)
            )
    
    def health_check(self) -> Dict[str, Any]:
        """
        API health check endpoint
        
        Returns:
            Health status information
        """
        try:
            # Test specialist manager availability
            specialists = self.specialist_manager.list_available_specialists()
            
            return {
                "status": "healthy",
                "specialist_manager": "operational",
                "available_specialists": len(specialists),
                "core_specialists": specialists[:5],  # First 5 for display
                "api_version": "5.0.0"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_version": "5.0.0"
            }
    
    def export_matches(self, output_format='excel', feedback_system=True, reviewer_name=None):
        """
        Export job matches to Excel or other formats
        
        Args:
            output_format: Format to export ('excel' or 'json')
            feedback_system: Whether to include feedback system columns
            reviewer_name: Name of the reviewer for feedback
            
        Returns:
            str: Path to the exported file
        """
        logger.info(f"📊 Exporting job matches to {output_format}")
        
        config = get_config()
        output_dir = Path(config.excel.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"job_matches_{timestamp}.xlsx"
        
        # TODO: Implement actual export logic here
        # For now return dummy file path
        return str(output_file)
