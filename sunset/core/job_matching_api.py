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
        """Initialize with DirectSpecialistManager"""
        self.specialist_manager = DirectSpecialistManager()
        logger.info("✅ JobMatchingAPI initialized with DirectSpecialistManager")
    
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
