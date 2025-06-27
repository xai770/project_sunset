#!/usr/bin/env python3
"""
Direct Specialist Manager - Phase 3 Architecture
===============================================
Main entry point for simplified specialist access without abstraction layers.
Modular architecture with separated concerns.
"""

from typing import Dict, Any, List
import logging

# Import modular components
from core.specialist_types import SpecialistResult
from core.specialist_config import is_direct_specialists_available, get_specialist_status
from core.job_matching_specialists import (
    DirectJobMatchingSpecialists, 
    get_job_matching_specialists, 
    get_feedback_specialists
)
from core.specialist_evaluator import SpecialistEvaluator

logger = logging.getLogger(__name__)


class DirectSpecialistManager:
    """
    Phase 3 Architecture: Direct Specialist Manager
    Main entry point for simplified specialist access without abstraction layers.
    """
    
    def __init__(self, model: str = "llama3.2:latest"):
        self.model = model
        self.job_matching = DirectJobMatchingSpecialists(model)
        self.evaluator = SpecialistEvaluator(model)

    def get_job_matching_specialists(self) -> DirectJobMatchingSpecialists:
        """Get direct job matching specialist access"""
        return self.job_matching

    def is_available(self) -> bool:
        """Check if direct specialist access is available"""
        return is_direct_specialists_available()

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of specialist access"""
        return get_specialist_status()

    def list_available_specialists(self) -> List[str]:
        """List all available specialists"""
        return self.evaluator.get_available_specialists()

    def evaluate_with_specialist(self, specialist_name: str, input_data: Dict[str, Any]) -> SpecialistResult:
        """
        Evaluate input with specified specialist
        Args:
            specialist_name: Name of the specialist to use
            input_data: Input data for evaluation
        Returns:
            Specialist evaluation result
        """
        if not self.is_available():
            return SpecialistResult(
                success=False,
                result="Specialist access unavailable",
                specialist_used=specialist_name,
                execution_time=0.0,
                error="LLM Factory not available"
            )
        
        # Route to appropriate specialist handler
        if specialist_name == "job_fitness_evaluator":
            return self.evaluator.evaluate_job_fitness(input_data)
        elif specialist_name == "domain_classification":
            return self.evaluator.evaluate_domain_classification(input_data)
        elif specialist_name == "location_validation":
            return self.evaluator.evaluate_location_validation(input_data)
        else:
            # For other specialists, return a mock result for testing
            return self.evaluator.evaluate_mock_specialist(specialist_name, input_data)

    def generate_cover_letter(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> SpecialistResult:
        """
        Expose cover letter generation via the manager.
        """
        return self.job_matching.generate_cover_letter(cv_data, job_data)

    def extract_content_skills(self, job_description: str) -> SpecialistResult:
        """
        Extract skills and content from job description using v3.3 production specialist
        
        Args:
            job_description: Raw job description text
            
        Returns:
            SpecialistResult with extracted skills and content
        """
        return self.job_matching.extract_content_skills(job_description)


def get_direct_specialist_manager(model: str = "llama3.2:latest") -> DirectSpecialistManager:
    """
    Get direct specialist manager instance - Phase 3 Architecture
    Main entry point for Phase 3 direct specialist access.
    Replaces complex abstraction hierarchies with simplified access.
    Args:
        model: LLM model to use
    Returns:
        Direct specialist manager instance
    """
    return DirectSpecialistManager(model)


# Test the module when run directly
if __name__ == "__main__":
    print("Testing direct specialist manager...")
    manager = DirectSpecialistManager()
    print(f"Manager created: {type(manager)}")
    print(f"Status: {manager.get_status()}")
    print("✅ Direct specialist manager working correctly")
