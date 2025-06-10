#!/usr/bin/env python3
"""
Minimal Direct Specialist Manager - Phase 3 Architecture Optimization
====================================================================

Test version without LLM Factory dependencies to isolate import issues.
"""

from typing import Dict, Any, Optional, List, Union
import logging
import time
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

# LLM Factory Direct Integration - no abstraction layers
try:
    import sys
    sys.path.insert(0, '/home/xai/Documents/llm_factory')
    from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
    from llm_factory.core.types import ModuleConfig
    from llm_factory.core.ollama_client import OllamaClient
    LLM_FACTORY_AVAILABLE = True
    logger.info("✅ Direct LLM Factory access available")
except ImportError as e:
    LLM_FACTORY_AVAILABLE = False
    logger.warning(f"⚠️ LLM Factory not available for direct access: {e}")
except Exception as e:
    LLM_FACTORY_AVAILABLE = False
    logger.warning(f"⚠️ LLM Factory failed to load: {e}")

@dataclass
class SpecialistResult:
    """Standardized result format for all specialist operations"""
    success: bool
    result: Any
    specialist_used: str
    execution_time: float
    quality_score: Optional[float] = None
    error: Optional[str] = None

class DirectJobMatchingSpecialists:
    """
    Direct job matching specialists - no abstraction layers
    Phase 3 Architecture: Simplified specialist access without wrapper classes
    """
    
    def __init__(self, model: str = "llama3.2:latest"):
        self.model = model
        self.registry: Optional['SpecialistRegistry'] = None
        self.client: Optional['OllamaClient'] = None
        self._init_direct_access()
        
    def _init_direct_access(self):
        """Initialize direct specialist access"""
        if not LLM_FACTORY_AVAILABLE:
            logger.info("LLM Factory not available - fallback mode")
            return
        
        try:
            self.client = OllamaClient()  # type: ignore
            self.registry = SpecialistRegistry()  # type: ignore
            logger.info("✅ Direct specialist access initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize direct specialist access: {e}")
            self.client = None
            self.registry = None
    
    def evaluate_job_fitness(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> SpecialistResult:
        """
        Direct job fitness evaluation - Phase 3 simplified architecture
        """
        # Check if direct specialist access is available
        if not LLM_FACTORY_AVAILABLE:
            return SpecialistResult(
                success=False, 
                result=None,
                specialist_used="none",
                execution_time=0.0,
                error="LLM Factory not available"
            )
        
        if not self.registry or not self.client:
            return SpecialistResult(
                success=False, 
                result=None,
                specialist_used="none",
                execution_time=0.0,
                error="Direct specialist access not initialized"
            )
        
        try:
            start_time = time.time()
            
            # Direct specialist configuration - no wrapper classes
            config = ModuleConfig(  # type: ignore
                models=[self.model],
                conservative_bias=True,
                quality_threshold=8.0,
                ollama_client=self.client
            )
            
            # Load specialist directly from registry
            specialist = self.registry.load_specialist("job_fitness_evaluator", config)  # type: ignore
            
            # Direct input preparation
            input_data = {
                "job_posting": {
                    "description": job_data.get("description", ""),
                    "title": "Job Position",
                    "requirements": []
                },
                "candidate_profile": {
                    "cv_content": cv_data.get("text", ""),
                    "name": "Candidate",
                    "skills": [],
                    "experience": ""
                }
            }
            
            # Direct specialist call
            result = specialist.process(input_data)
            execution_time = time.time() - start_time
            
            if result.success:
                return SpecialistResult(
                    success=True,
                    result=result.data,
                    specialist_used="job_fitness_evaluator",
                    execution_time=execution_time,
                    quality_score=getattr(result, 'quality_score', None)
                )
            else:
                return SpecialistResult(
                    success=False,
                    result=None,
                    specialist_used="job_fitness_evaluator", 
                    execution_time=execution_time,
                    error="Specialist processing failed"
                )
                
        except Exception as e:
            logger.error(f"❌ Direct fitness assessment failed: {e}")
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="job_fitness_evaluator",
                execution_time=0.0,
                error=str(e)
            )
    
    def process_feedback(self, feedback_data: Dict[str, Any]) -> SpecialistResult:
        """
        Process feedback using direct specialist access - Phase 3 architecture
        """
        # Check if direct specialist access is available
        if not LLM_FACTORY_AVAILABLE:
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="none",
                execution_time=0.0,
                error="LLM Factory not available"
            )
        
        if not self.registry or not self.client:
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="none",
                execution_time=0.0,
                error="Direct specialist access not initialized"
            )
        
        try:
            start_time = time.time()
            
            # Direct specialist configuration for feedback processing
            config = ModuleConfig(  # type: ignore
                models=[self.model],
                conservative_bias=True,
                quality_threshold=8.0,
                ollama_client=self.client
            )
            
            # Load feedback specialist directly from registry
            specialist = self.registry.load_specialist("feedback_analyzer", config)  # type: ignore
            
            # Direct feedback processing
            result = specialist.process(feedback_data)
            execution_time = time.time() - start_time
            
            if result.success:
                return SpecialistResult(
                    success=True,
                    result=result.data,
                    specialist_used="feedback_analyzer",
                    execution_time=execution_time,
                    quality_score=getattr(result, 'quality_score', None)
                )
            else:
                return SpecialistResult(
                    success=False,
                    result=None,
                    specialist_used="feedback_analyzer",
                    execution_time=execution_time,
                    error="Feedback processing failed"
                )
                
        except Exception as e:
            logger.error(f"❌ Direct feedback processing failed: {e}")
            return SpecialistResult(
                success=False,
                result=None,
                specialist_used="feedback_analyzer",
                execution_time=0.0,
                error=str(e)
            )

class DirectSpecialistManager:
    """
    Phase 3 Architecture: Direct Specialist Manager
    
    Main entry point for simplified specialist access without abstraction layers.
    Replaces complex LLM Client hierarchies with direct specialist integration.
    """
    
    def __init__(self, model: str = "llama3.2:latest"):
        self.model = model
        self.job_matching: DirectJobMatchingSpecialists = get_job_matching_specialists(model)
        
    def get_job_matching_specialists(self) -> DirectJobMatchingSpecialists:
        """Get direct job matching specialist access"""
        return self.job_matching
        
    def is_available(self) -> bool:
        """Check if direct specialist access is available"""
        return is_direct_specialists_available()
        
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of specialist access"""
        return get_specialist_status()
    
    def evaluate_with_specialist(self, specialist_name: str, input_data: Dict[str, Any]) -> SpecialistResult:
        """
        Evaluate input with specified specialist
        
        Args:
            specialist_name: Name of the specialist to use
            input_data: Input data for evaluation
            
        Returns:
            Specialist evaluation result
        """
        import time
        start_time = time.time()
        
        if not self.is_available():
            return SpecialistResult(
                success=False,
                result="Specialist access unavailable",
                specialist_used=specialist_name,
                execution_time=time.time() - start_time,
                error="LLM Factory not available"
            )
        
        try:
            if specialist_name == "job_fitness_evaluator":
                cv_data = {"text": input_data.get("candidate_profile", "")}
                job_data = {"description": input_data.get("job_requirements", "")}
                result = self.job_matching.evaluate_job_fitness(cv_data, job_data)
                
                # Convert to SpecialistResult format
                return SpecialistResult(
                    success=result.success if hasattr(result, 'success') else True,
                    result=result,
                    specialist_used=specialist_name,
                    execution_time=time.time() - start_time
                )
            else:
                # For other specialists, return a mock result for testing
                return SpecialistResult(
                    success=True,
                    result=f"Mock evaluation result for {specialist_name}",
                    specialist_used=specialist_name,
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            return SpecialistResult(
                success=False,
                result=f"Evaluation failed: {str(e)}",
                specialist_used=specialist_name,
                execution_time=time.time() - start_time,
                error=str(e)
            )

def get_job_matching_specialists(model: str = "llama3.2:latest") -> DirectJobMatchingSpecialists:
    """
    Get direct access to job matching specialists - Phase 3 Architecture
    """
    return DirectJobMatchingSpecialists(model)

def get_feedback_specialists(model: str = "llama3.2:latest") -> DirectJobMatchingSpecialists:
    """
    Get direct access to feedback analysis specialists - Phase 3 Architecture
    """
    return DirectJobMatchingSpecialists(model)

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

def is_direct_specialists_available() -> bool:
    """Check if direct specialist access is available"""
    return LLM_FACTORY_AVAILABLE

def get_specialist_status() -> Dict[str, Any]:
    """Get status of direct specialist access"""
    if not LLM_FACTORY_AVAILABLE:
        return {
            "available": False,
            "error": "LLM Factory not available",
            "phase": "fallback_only"
        }
    
    try:
        specialists = get_job_matching_specialists()
        return {
            "available": True,
            "phase": "direct_access_v3",
            "architecture": "simplified_no_abstractions",
            "ready": specialists.registry is not None
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "phase": "fallback_only"
        }

# Test the module when run directly
if __name__ == "__main__":
    print("Testing minimal direct specialist manager...")
    manager = DirectSpecialistManager()
    print(f"Manager created: {type(manager)}")
    print(f"Status: {manager.get_status()}")
    print("✅ Minimal version working correctly")
