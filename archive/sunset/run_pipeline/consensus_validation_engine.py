"""
Consensus Validation Engine for Project Sunset
Phase 1B Implementation - Multi-Specialist Validation System

This module implements a consensus-based validation system that combines
JobFitnessEvaluator and ConsensusEngine for enhanced cover letter quality.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import asyncio
from datetime import datetime

# Import the specialists wrapper
try:
    # Try relative import first (when used as module)
    from .specialists_wrapper import SpecialistsWrapper
    from .llm_factory_stubs import ModuleConfig
except ImportError:
    # Fall back to absolute import (when run directly)
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from run_pipeline.specialists_wrapper import SpecialistsWrapper
    from run_pipeline.llm_factory_stubs import ModuleConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of consensus validation process"""
    score: float
    confidence: float
    feedback: str
    consensus_reached: bool
    specialist_scores: Dict[str, float]
    timestamp: datetime
    quality_metrics: Dict[str, Any]


@dataclass
class ConsensusConfig:
    """Configuration for consensus validation"""
    min_specialists: int = 2
    consensus_threshold: float = 0.7
    quality_threshold: float = 8.0
    max_iterations: int = 3
    enable_detailed_feedback: bool = True
    timeout_seconds: int = 30


class ConsensusValidationEngine:
    """
    Multi-specialist validation engine that combines JobFitnessEvaluator 
    and ConsensusEngine for enhanced cover letter quality assessment.
    """
    
    def __init__(self, config: ConsensusConfig):
        """Initialize the consensus validation engine"""
        self.config = config
        self.specialists_wrapper = SpecialistsWrapper()
        self.validation_history: List[ValidationResult] = []
        
        # Initialize specialists
        self.job_fitness_evaluator = self.specialists_wrapper.get_job_fitness_evaluator()
        self.consensus_engine = self.specialists_wrapper.get_enhanced_consensus_engine()
        
        logger.info("ConsensusValidationEngine initialized with config: %s", config)
    
    async def validate_cover_letter(
        self, 
        cover_letter: str, 
        job_description: str,
        candidate_info: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate a cover letter using consensus-based approach
        
        Args:
            cover_letter: The cover letter text to validate
            job_description: The job description text
            candidate_info: Dictionary containing candidate information
            
        Returns:
            ValidationResult with consensus-based assessment
        """
        start_time = datetime.now()
        logger.info("Starting consensus validation for cover letter")
        
        try:
            # Phase 1: Individual specialist evaluations
            specialist_results = await self._run_specialist_evaluations(
                cover_letter, job_description, candidate_info
            )
            
            # Phase 2: Consensus analysis
            consensus_result = await self._analyze_consensus(specialist_results)
            
            # Phase 3: Generate final validation result
            validation_result = self._create_validation_result(
                specialist_results, consensus_result, start_time
            )
            
            # Store in history
            self.validation_history.append(validation_result)
            
            logger.info(
                "Consensus validation completed. Score: %.2f, Confidence: %.2f",
                validation_result.score, validation_result.confidence
            )
            
            return validation_result
            
        except Exception as e:
            logger.error("Error in consensus validation: %s", str(e))
            return self._create_error_result(str(e), start_time)
    
    async def _run_specialist_evaluations(
        self, 
        cover_letter: str, 
        job_description: str, 
        candidate_info: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Run evaluations from all available specialists"""
        
        results = {}
        
        # JobFitnessEvaluator assessment
        try:
            fitness_result = await self._evaluate_job_fitness(
                cover_letter, job_description, candidate_info
            )
            results['job_fitness'] = fitness_result
            logger.debug("Job fitness evaluation completed: %s", fitness_result)
        except Exception as e:
            logger.warning("Job fitness evaluation failed: %s", str(e))
            results['job_fitness'] = {'error': str(e), 'score': 0.0}
        
        # ConsensusEngine assessment
        try:
            consensus_result = await self._evaluate_consensus_quality(
                cover_letter, job_description
            )
            results['consensus_quality'] = consensus_result
            logger.debug("Consensus quality evaluation completed: %s", consensus_result)
        except Exception as e:
            logger.warning("Consensus quality evaluation failed: %s", str(e))
            results['consensus_quality'] = {'error': str(e), 'score': 0.0}
        
        return results
    
    async def _evaluate_job_fitness(
        self, 
        cover_letter: str, 
        job_description: str, 
        candidate_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate cover letter using JobFitnessEvaluator"""
        
        # Prepare evaluation context
        evaluation_context = {
            'cover_letter': cover_letter,
            'job_description': job_description,
            'candidate_info': candidate_info,
            'evaluation_criteria': [
                'relevance_to_position',
                'skills_alignment',
                'experience_match',
                'communication_quality',
                'cultural_fit_indicators'
            ]
        }
        
        # For now, use mock evaluation until JobFitnessEvaluator constructor is fixed
        if hasattr(self.job_fitness_evaluator, 'evaluate_fitness'):
            result = await self.job_fitness_evaluator.evaluate_fitness(
                evaluation_context
            )
        else:
            # Mock implementation
            result = self._mock_job_fitness_evaluation(evaluation_context)
        
        if not isinstance(result, dict):
            # Ensure the result is always a dictionary
            return {'result': result}
        return result
    
    async def _evaluate_consensus_quality(
        self, 
        cover_letter: str, 
        job_description: str
    ) -> Dict[str, Any]:
        """Evaluate cover letter using ConsensusEngine"""
        
        # Prepare quality assessment prompts
        quality_prompts = [
            f"Evaluate the overall quality of this cover letter: {cover_letter[:500]}...",
            f"Assess how well this cover letter matches the job requirements: {job_description[:300]}...",
            "Rate the professionalism and communication effectiveness of this cover letter."
        ]
        
        try:
            # Use ConsensusEngine for quality assessment
            consensus_scores = []
            for prompt in quality_prompts:
                if hasattr(self.consensus_engine, 'evaluate_with_consensus'):
                    score = await self.consensus_engine.evaluate_with_consensus(prompt)
                    consensus_scores.append(score)
                else:
                    # Mock implementation
                    score = self._mock_consensus_evaluation(prompt)
                    consensus_scores.append(score)
            
            # Calculate average consensus score
            avg_score = sum(consensus_scores) / len(consensus_scores) if consensus_scores else 0.0
            
            return {
                'score': avg_score,
                'individual_scores': consensus_scores,
                'confidence': min(consensus_scores) if consensus_scores else 0.0,
                'assessment_type': 'consensus_quality'
            }
            
        except Exception as e:
            logger.error("Consensus quality evaluation error: %s", str(e))
            return {'error': str(e), 'score': 0.0}
    
    async def _analyze_consensus(self, specialist_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze consensus between specialist evaluations"""
        
        # Extract scores from specialist results
        scores = []
        valid_results = 0
        
        for specialist, result in specialist_results.items():
            if 'error' not in result and 'score' in result:
                scores.append(result['score'])
                valid_results += 1
            else:
                logger.warning("Invalid result from specialist %s: %s", specialist, result)
        
        if valid_results < self.config.min_specialists:
            logger.warning(
                "Insufficient valid specialist results (%d < %d)", 
                valid_results, self.config.min_specialists
            )
            return {
                'consensus_reached': False,
                'confidence': 0.0,
                'reason': f'Insufficient valid results ({valid_results}/{self.config.min_specialists})'
            }
        
        # Calculate consensus metrics
        avg_score = sum(scores) / len(scores)
        score_variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        consensus_strength = 1.0 / (1.0 + score_variance)  # Higher variance = lower consensus
        
        consensus_reached = consensus_strength >= self.config.consensus_threshold
        
        return {
            'consensus_reached': consensus_reached,
            'average_score': avg_score,
            'score_variance': score_variance,
            'consensus_strength': consensus_strength,
            'confidence': consensus_strength,
            'participating_specialists': len(scores)
        }
    
    def _create_validation_result(
        self, 
        specialist_results: Dict[str, Dict[str, Any]],
        consensus_result: Dict[str, Any],
        start_time: datetime
    ) -> ValidationResult:
        """Create final validation result from specialist and consensus analysis"""
        
        # Extract specialist scores
        specialist_scores = {}
        for specialist, result in specialist_results.items():
            if 'score' in result:
                specialist_scores[specialist] = result['score']
        
        # Calculate final score
        if consensus_result.get('consensus_reached', False):
            final_score = consensus_result.get('average_score', 0.0)
            confidence = consensus_result.get('confidence', 0.0)
        else:
            # Use best available score if no consensus
            final_score = max(specialist_scores.values()) if specialist_scores else 0.0
            confidence = 0.3  # Low confidence without consensus
        
        # Generate feedback
        feedback = self._generate_feedback(specialist_results, consensus_result)
        
        # Quality metrics
        quality_metrics = {
            'specialist_count': len(specialist_scores),
            'consensus_strength': consensus_result.get('consensus_strength', 0.0),
            'score_variance': consensus_result.get('score_variance', 0.0),
            'processing_time': (datetime.now() - start_time).total_seconds()
        }
        
        return ValidationResult(
            score=final_score,
            confidence=confidence,
            feedback=feedback,
            consensus_reached=consensus_result.get('consensus_reached', False),
            specialist_scores=specialist_scores,
            timestamp=datetime.now(),
            quality_metrics=quality_metrics
        )
    
    def _generate_feedback(
        self, 
        specialist_results: Dict[str, Dict[str, Any]],
        consensus_result: Dict[str, Any]
    ) -> str:
        """Generate human-readable feedback from validation results"""
        
        feedback_parts = []
        
        # Consensus status
        if consensus_result.get('consensus_reached', False):
            feedback_parts.append(
                f"✅ Consensus reached with {consensus_result.get('confidence', 0):.1%} confidence."
            )
        else:
            feedback_parts.append(
                f"⚠️ Limited consensus achieved. Reason: {consensus_result.get('reason', 'Unknown')}"
            )
        
        # Specialist feedback
        if self.config.enable_detailed_feedback:
            for specialist, result in specialist_results.items():
                if 'error' not in result:
                    score = result.get('score', 0.0)
                    feedback_parts.append(
                        f"• {specialist.replace('_', ' ').title()}: {score:.1f}/10"
                    )
        
        # Quality assessment
        avg_score = consensus_result.get('average_score', 0.0)
        if avg_score >= self.config.quality_threshold:
            feedback_parts.append("🎯 Cover letter meets quality standards.")
        else:
            feedback_parts.append("📝 Cover letter may need improvement.")
        
        return "\n".join(feedback_parts)
    
    def _create_error_result(self, error_message: str, start_time: datetime) -> ValidationResult:
        """Create validation result for error cases"""
        return ValidationResult(
            score=0.0,
            confidence=0.0,
            feedback=f"❌ Validation error: {error_message}",
            consensus_reached=False,
            specialist_scores={},
            timestamp=datetime.now(),
            quality_metrics={
                'error': error_message,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
        )
    
    def _mock_job_fitness_evaluation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation for job fitness evaluation"""
        # Simple mock scoring based on text length and keyword matching
        cover_letter = context.get('cover_letter', '')
        job_description = context.get('job_description', '')
        
        # Basic scoring logic
        base_score = 5.0
        
        # Length bonus
        if 200 <= len(cover_letter) <= 800:
            base_score += 1.5
        
        # Keyword matching (simple implementation)
        job_keywords = job_description.lower().split()[:20]  # First 20 words as keywords
        cover_lower = cover_letter.lower()
        matches = sum(1 for keyword in job_keywords if keyword in cover_lower)
        base_score += min(matches * 0.2, 2.5)
        
        return {
            'score': min(base_score, 10.0),
            'assessment_type': 'job_fitness_mock',
            'details': {
                'length_score': 1.5 if 200 <= len(cover_letter) <= 800 else 0,
                'keyword_matches': matches,
                'total_keywords': len(job_keywords)
            }
        }
    
    def _mock_consensus_evaluation(self, prompt: str) -> float:
        """Mock implementation for consensus evaluation"""
        # Simple mock scoring based on prompt characteristics
        base_score = 6.0
        
        # Adjust based on prompt content
        if 'quality' in prompt.lower():
            base_score += 1.0
        if 'professional' in prompt.lower():
            base_score += 0.5
        if 'match' in prompt.lower():
            base_score += 0.8
        
        return min(base_score, 10.0)
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get statistics about validation history"""
        if not self.validation_history:
            return {'total_validations': 0}
        
        scores = [v.score for v in self.validation_history]
        confidences = [v.confidence for v in self.validation_history]
        consensus_reached = sum(1 for v in self.validation_history if v.consensus_reached)
        
        return {
            'total_validations': len(self.validation_history),
            'average_score': sum(scores) / len(scores),
            'average_confidence': sum(confidences) / len(confidences),
            'consensus_rate': consensus_reached / len(self.validation_history),
            'quality_threshold_met': sum(1 for s in scores if s >= self.config.quality_threshold)
        }


# Example usage and testing functions
async def test_consensus_validation():
    """Test function for consensus validation engine"""
    
    # Create test configuration
    config = ConsensusConfig(
        min_specialists=2,
        consensus_threshold=0.7,
        quality_threshold=8.0,
        enable_detailed_feedback=True
    )
    
    # Initialize engine
    engine = ConsensusValidationEngine(config)
    
    # Test data
    test_cover_letter = """
    Dear Hiring Manager,
    
    I am writing to express my strong interest in the Software Engineer position at your company. 
    With 5 years of experience in Python development and machine learning, I believe I would be 
    a valuable addition to your team.
    
    My experience includes developing web applications using Django and Flask, implementing 
    machine learning models with scikit-learn and TensorFlow, and collaborating with 
    cross-functional teams in Agile environments.
    
    I am particularly excited about this opportunity because of your company's focus on 
    innovative AI solutions and commitment to technical excellence.
    
    Thank you for considering my application.
    
    Sincerely,
    John Doe
    """
    
    test_job_description = """
    We are seeking a Software Engineer with experience in Python, machine learning, 
    and web development. The ideal candidate will have experience with Django, 
    TensorFlow, and Agile methodologies. Strong communication skills and ability 
    to work in a team environment are essential.
    """
    
    test_candidate_info = {
        'name': 'John Doe',
        'experience_years': 5,
        'skills': ['Python', 'Django', 'Machine Learning', 'TensorFlow'],
        'education': 'BS Computer Science'
    }
    
    # Run validation
    result = await engine.validate_cover_letter(
        test_cover_letter, 
        test_job_description, 
        test_candidate_info
    )
    
    print("=== Consensus Validation Result ===")
    print(f"Score: {result.score:.2f}/10")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Consensus Reached: {result.consensus_reached}")
    print(f"Feedback:\n{result.feedback}")
    print(f"Specialist Scores: {result.specialist_scores}")
    print(f"Quality Metrics: {result.quality_metrics}")
    
    # Get engine stats
    stats = engine.get_validation_stats()
    print(f"\n=== Engine Statistics ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    return result


if __name__ == "__main__":
    # Run test
    asyncio.run(test_consensus_validation())
