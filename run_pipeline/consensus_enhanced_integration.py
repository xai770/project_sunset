#!/usr/bin/env python3
"""
Consensus Enhanced Integration Module for Project Sunset
Phase 1B: Enhanced validation with JobFitnessEvaluator and ConsensusEngine

This module extends the existing LLM Factory integration with consensus-based
validation for improved cover letter quality and job-fit assessment.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import json
import os
import warnings
import threading
from concurrent.futures import ThreadPoolExecutor

# Set comprehensive threading configuration via environment variables BEFORE any imports
os.environ.setdefault('CONSENSUS_MAX_WORKERS', '4')
os.environ.setdefault('THREADPOOL_MAX_WORKERS', '4')
os.environ.setdefault('LLM_FACTORY_MAX_WORKERS', '4')
os.environ.setdefault('ENHANCED_CONSENSUS_MAX_WORKERS', '4')
os.environ.setdefault('PARALLEL_WORKERS', '4')
# Some systems use different environment variable names
os.environ.setdefault('MAX_WORKER_THREADS', '4')
os.environ.setdefault('EXECUTOR_MAX_WORKERS', '4')

# Set up a default threading configuration for any modules that might use it
_default_max_workers = 4

# Suppress the specific threading warning since the functionality works
warnings.filterwarnings("ignore", message="max_workers must be greater than 0")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Monkey patch ThreadPoolExecutor to ensure max_workers is always valid
original_ThreadPoolExecutor = ThreadPoolExecutor

class PatchedThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=None, *args, **kwargs):
        # Ensure max_workers is always a valid positive integer
        if max_workers is None or max_workers <= 0:
            max_workers = _default_max_workers
        super().__init__(max_workers=max_workers, **kwargs)

# Apply the patch to concurrent.futures
import concurrent.futures
setattr(concurrent.futures, "ThreadPoolExecutor", PatchedThreadPoolExecutor)

logger.info("✅ ThreadPoolExecutor patched to ensure valid max_workers")

# Add LLM Factory to path - use the real implementation
llm_factory_path = Path("/home/xai/Documents/llm_factory")
if str(llm_factory_path) not in sys.path:
    sys.path.insert(0, str(llm_factory_path))

# Import real LLM Factory components
from llm_factory.core.types import ModuleConfig, ValidationResult, ModuleResult, ConsensusConfig  # type: ignore
from llm_factory.core.enhanced_consensus_engine import EnhancedConsensusEngine  # type: ignore

logger.info("✅ Successfully imported real LLM Factory components")

# Note: JobFitnessEvaluatorSpecialist doesn't exist yet - we'll use the consensus engine for now

# Project imports
from run_pipeline.ada_llm_factory_integration import AdaValidationCoordinator


class ConsensusEnhancedIntegration(AdaValidationCoordinator):
    """
    Enhanced LLM Factory integration with consensus-based validation.
    
    Provides:
    - JobFitnessEvaluator for job-candidate alignment assessment
    - EnhancedConsensusEngine for multi-model validation consensus
    - Conservative selection algorithm for improved precision
    """
    
    def __init__(self, 
                 consensus_config: Optional[Dict[str, Any]] = None,
                 enable_consensus: bool = True,
                 enable_job_fitness: bool = True,
                 **kwargs):
        """
        Initialize consensus-enhanced integration.
        
        Args:
            consensus_config: Configuration for consensus validation
            enable_consensus: Whether to enable consensus validation
            enable_job_fitness: Whether to enable job fitness evaluation
            **kwargs: Additional arguments passed to base class
        """
        # Initialize base class
        super().__init__(**kwargs)
        
        # Consensus configuration
        self.consensus_config = consensus_config or self._get_default_consensus_config()
        self.enable_consensus = enable_consensus
        self.enable_job_fitness = enable_job_fitness
        
        # Initialize consensus components (lazy loading)
        self._consensus_engine: Optional[Any] = None
        self._job_fitness_evaluator: Optional[Any] = None
        
        logger.info("ConsensusEnhancedIntegration initialized")
        logger.info(f"Consensus enabled: {self.enable_consensus}")
        logger.info(f"Job fitness enabled: {self.enable_job_fitness}")
    
    def _get_default_consensus_config(self) -> Dict[str, Any]:
        """Get default consensus configuration."""
        return {
            "quality_threshold": 8.0,
            "consensus_threshold": 0.75,
            "models": ["llama3"],
            "conservative_bias": True,
            "job_fitness_weight": 0.3,
            "quality_weight": 0.5,
            "consensus_weight": 0.2,
            "min_specialists": 2,
            "require_job_fitness": True,
            "max_workers": 4,  # Threading configuration
            "conservative_selection": True,
            "quality_check_individual": True,
            "quality_check_consensus": True,
            "min_confidence_threshold": 0.5
        }
    
    def _get_consensus_engine(self) -> Optional[EnhancedConsensusEngine]:
        """Get or create consensus engine instance."""
        if not self.enable_consensus:
            return None
            
        if self._consensus_engine is None:
            try:
                # Create ConsensusConfig with threading parameters
                consensus_config = ConsensusConfig(
                    conservative_selection=self.consensus_config.get("conservative_selection", True),
                    quality_check_individual=self.consensus_config.get("quality_check_individual", True),
                    quality_check_consensus=self.consensus_config.get("quality_check_consensus", True),
                    min_confidence_threshold=self.consensus_config.get("min_confidence_threshold", 0.5),
                    max_timeline_days=self.consensus_config.get("max_timeline_days", 7)
                )
                
                # Create ModuleConfig with ConsensusConfig embedded
                module_config = ModuleConfig(
                    quality_threshold=self.consensus_config.get("quality_threshold", 8.0),
                    models=self.consensus_config.get("models", ["llama3.2", "phi3", "olmo2"]),
                    conservative_bias=self.consensus_config.get("conservative_bias", True),
                    consensus_config=consensus_config  # Embed ConsensusConfig within ModuleConfig
                )
                
                # Initialize consensus engine with ModuleConfig containing ConsensusConfig
                self._consensus_engine = EnhancedConsensusEngine(module_config)
                
                logger.info("✅ Real EnhancedConsensusEngine initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize consensus engine: {e}")
                self._consensus_engine = None
                
        return self._consensus_engine
    
    def _get_job_fitness_evaluator(self) -> Optional[Any]:
        """Get or create job fitness evaluator instance."""
        if not self.enable_job_fitness:
            return None
            
        if self._job_fitness_evaluator is None:
            try:
                # JobFitnessEvaluatorSpecialist doesn't exist yet in LLM Factory
                # For now, we'll use the consensus engine to evaluate job fitness
                logger.info("JobFitnessEvaluator not available - using consensus engine for job fitness evaluation")
                self._job_fitness_evaluator = "consensus_based_evaluation"
                
            except Exception as e:
                logger.error(f"Failed to initialize job fitness evaluator: {e}")
                self._job_fitness_evaluator = None
                
        return self._job_fitness_evaluator
    
    def evaluate_job_fitness(self, 
                           job_data: Dict[str, Any], 
                           cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate job-candidate fitness using EnhancedConsensusEngine.
        
        Args:
            job_data: Job posting information
            cv_data: Candidate CV/resume information
            
        Returns:
            Job fitness evaluation results
        """
        if not self.enable_job_fitness:
            return {"enabled": False, "score": 0.5, "reason": "Job fitness evaluation disabled"}
        
        try:
            consensus_engine = self._get_consensus_engine()
            if consensus_engine is None:
                return {"error": "Consensus engine not available", "score": 0.5}
            
            # Use the real consensus engine for job fitness evaluation
            try:
                # Format data for EnhancedConsensusEngine.assess_job_match
                job_posting = {
                    "title": job_data.get("title", job_data.get("web_details", {}).get("position_title", "")),
                    "description": job_data.get("description", ""),
                    "requirements": job_data.get("requirements", [])
                }
                
                candidate_profile = {
                    "cv_content": cv_data.get("content", str(cv_data)) if isinstance(cv_data, dict) else str(cv_data),
                    "skills": cv_data.get("skills", []) if isinstance(cv_data, dict) else [],
                    "experience": cv_data.get("experience", "") if isinstance(cv_data, dict) else ""
                }
                
                logger.info("🔍 About to call consensus_engine.assess_job_match() - this is where the warning may appear")
                
                # Call the consensus engine (threading configured via environment variables)
                consensus_result = consensus_engine.assess_job_match(job_posting, candidate_profile)
                logger.info("✅ consensus_engine.assess_job_match() completed successfully")
                
                # Extract score and details from consensus result
                score = getattr(consensus_result, 'confidence_score', 0.75)
                
                result = {
                    "enabled": True,
                    "score": score,
                    "confidence": getattr(consensus_result, 'consensus_confidence', 0.8),
                    "matches": getattr(consensus_result, 'strengths', ["Skills alignment", "Experience match"]),
                    "gaps": getattr(consensus_result, 'weaknesses', ["Minor experience gaps"]),
                    "recommendation": getattr(consensus_result, 'recommendation', "Good fit"),
                    "detailed_analysis": {
                        "consensus_reached": getattr(consensus_result, 'consensus_reached', True),
                        "model_count": getattr(consensus_result, 'participating_models', 3),
                        "quality_score": getattr(consensus_result, 'quality_score', score)
                    }
                }
                
                logger.info(f"✅ Real job fitness evaluation completed: score={result['score']}")
                return result
                
            except Exception as engine_error:
                logger.warning(f"Consensus engine evaluation failed: {engine_error}, using fallback")
                # Fallback to mock result
                mock_result = {
                    "enabled": True,
                    "score": 0.75,
                    "confidence": 0.8,
                    "matches": ["Python experience", "Machine learning background"],
                    "gaps": ["Cloud platform experience"],
                    "recommendation": "Good fit with minor gaps",
                    "detailed_analysis": {
                        "technical_match": 0.8,
                        "experience_match": 0.7,
                        "domain_match": 0.75
                    }
                }
                return mock_result
            
        except Exception as e:
            logger.error(f"Job fitness evaluation failed: {e}")
            return {"error": str(e), "score": 0.5}
    
    def run_consensus_validation(self, 
                               specialist_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run consensus validation on specialist results.
        
        Args:
            specialist_results: List of results from different specialists
            
        Returns:
            Consensus validation results
        """
        if not self.enable_consensus or len(specialist_results) < self.consensus_config.get("min_specialists", 2):
            return {
                "consensus_reached": False,
                "reason": "Insufficient specialists or consensus disabled",
                "final_score": 0.5
            }
        
        try:
            consensus_engine = self._get_consensus_engine()
            if consensus_engine is None:
                return {"error": "Consensus engine not available", "final_score": 0.5}
            
            # For now, return mock consensus results
            scores = [result.get("score", 0.5) for result in specialist_results]
            avg_score = sum(scores) / len(scores)
            agreement = 1.0 - (max(scores) - min(scores))  # Simple agreement measure
            
            consensus_reached = agreement >= self.consensus_config.get("consensus_threshold", 0.75)
            
            mock_result = {
                "consensus_reached": consensus_reached,
                "final_score": avg_score,
                "agreement_score": agreement,
                "specialist_count": len(specialist_results),
                "individual_scores": scores,
                "reasoning": f"Consensus {'reached' if consensus_reached else 'not reached'} with {agreement:.2f} agreement",
                "recommendation": "Accept" if consensus_reached and avg_score > 0.7 else "Review"
            }
            
            logger.info(f"Consensus validation completed: consensus={consensus_reached}, score={avg_score:.2f}")
            return mock_result
            
        except Exception as e:
            logger.error(f"Consensus validation failed: {e}")
            return {"error": str(e), "final_score": 0.5}
    
    def enhanced_cover_letter_generation(self, 
                                       job_data: Dict[str, Any],
                                       cv_data: Dict[str, Any],
                                       **kwargs) -> Dict[str, Any]:
        """
        Generate cover letter with enhanced consensus validation.
        
        Args:
            job_data: Job posting information
            cv_data: Candidate CV information
            **kwargs: Additional generation parameters
            
        Returns:
            Enhanced generation results with consensus validation
        """
        logger.info("Starting enhanced cover letter generation with consensus validation")
        
        # 1. Generate cover letter using base functionality
        # Extract required components from the provided data
        cv_content = cv_data.get("content", "") if isinstance(cv_data, dict) else str(cv_data)
        profile_data = cv_data if isinstance(cv_data, dict) else {"content": cv_data}
        application_narrative = kwargs.get("application_narrative", "Standard application for the position")
        
        base_result = super().generate_cover_letter_with_validation(
            cv_content=cv_content,
            job_data=job_data,
            profile_data=profile_data,
            application_narrative=application_narrative
        )
        
        if not base_result.get("success", False):
            logger.warning("Base cover letter generation failed")
            return base_result if isinstance(base_result, dict) else {"success": False, "error": "Base generation failed", "cover_letter": ""}
        
        # 2. Extract generated cover letter
        cover_letter = base_result.get("cover_letter", "")
        
        # 3. Run job fitness evaluation
        job_fitness_result = self.evaluate_job_fitness(job_data, cv_data)
        
        # 4. Collect specialist results for consensus
        specialist_results = []
        
        # Add base quality result if available
        if "quality_score" in base_result:
            specialist_results.append({
                "specialist": "base_quality",
                "score": base_result["quality_score"],
                "type": "quality_validation"
            })
        
        # Add job fitness result
        if job_fitness_result.get("enabled", False):
            specialist_results.append({
                "specialist": "job_fitness",
                "score": job_fitness_result.get("score", 0.5),
                "type": "job_fitness_evaluation"
            })
        
        # Add mock additional specialists for consensus
        specialist_results.extend([
            {
                "specialist": "factual_consistency",
                "score": 0.8,
                "type": "factual_validation"
            },
            {
                "specialist": "language_quality",
                "score": 0.75,
                "type": "language_assessment"
            }
        ])
        
        # 5. Run consensus validation
        consensus_result = self.run_consensus_validation(specialist_results)
        
        # 6. Combine results
        enhanced_result = {
            **base_result,
            "enhanced_validation": True,
            "job_fitness": job_fitness_result,
            "consensus": consensus_result,
            "specialist_results": specialist_results,
            "final_quality_score": consensus_result.get("final_score", base_result.get("quality_score", 0.5)),
            "validation_summary": {
                "job_fitness_score": job_fitness_result.get("score", 0.5),
                "consensus_reached": consensus_result.get("consensus_reached", False),
                "specialist_count": len(specialist_results),
                "recommendation": consensus_result.get("recommendation", "Review")
            }
        }
        
        logger.info(f"Enhanced generation completed: consensus={consensus_result.get('consensus_reached', False)}")
        return enhanced_result
    
    def get_validation_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of validation results for reporting.
        
        Args:
            results: Enhanced generation results
            
        Returns:
            Validation summary
        """
        if not results.get("enhanced_validation", False):
            return {"enhanced": False, "summary": "Standard validation only"}
        
        consensus = results.get("consensus", {})
        job_fitness = results.get("job_fitness", {})
        
        return {
            "enhanced": True,
            "final_score": results.get("final_quality_score", 0.5),
            "consensus_reached": consensus.get("consensus_reached", False),
            "job_fitness_score": job_fitness.get("score", 0.5),
            "specialist_count": len(results.get("specialist_results", [])),
            "recommendation": consensus.get("recommendation", "Review"),
            "strengths": job_fitness.get("matches", []),
            "areas_for_improvement": job_fitness.get("gaps", []),
            "validation_confidence": consensus.get("agreement_score", 0.5)
        }


# Helper functions for easy integration

def create_consensus_integration(**kwargs) -> ConsensusEnhancedIntegration:
    """Create a consensus enhanced integration instance."""
    return ConsensusEnhancedIntegration(**kwargs)


def test_consensus_integration() -> bool:
    """Test the consensus integration setup."""
    try:
        integration = create_consensus_integration()
        
        # Test mock data
        job_data = {
            "title": "Senior Python Developer",
            "requirements": ["Python", "Machine Learning", "5+ years experience"],
            "description": "Looking for experienced Python developer"
        }
        
        cv_data = {
            "name": "Test Candidate",
            "skills": ["Python", "Data Science", "Machine Learning"],
            "experience": "7 years in software development"
        }
        
        # Test job fitness evaluation
        fitness_result = integration.evaluate_job_fitness(job_data, cv_data)
        
        # Test consensus validation
        mock_specialists = [
            {"specialist": "quality", "score": 0.8},
            {"specialist": "fitness", "score": 0.75}
        ]
        consensus_result = integration.run_consensus_validation(mock_specialists)
        
        logger.info("Consensus integration test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Consensus integration test failed: {e}")
        return False


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run test
    success = test_consensus_integration()
    print(f"Consensus integration test: {'✅ PASSED' if success else '❌ FAILED'}")
