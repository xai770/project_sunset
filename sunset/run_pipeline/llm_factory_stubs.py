"""
Type stubs for llm_factory to satisfy mypy type checking

This module provides type stubs for llm_factory modules that are imported 
but do not have proper type annotations. This allows the Sunset project to 
use proper type checking without requiring changes to the upstream LLM Factory
codebase.

Usage:
    These stubs are used as fallbacks when the real LLM Factory modules 
    don't have type information available. They define the structure of the 
    expected classes and methods without actually implementing functionality.

Note:
    This file should be kept in sync with changes to the LLM Factory API.
    When LLM Factory adds proper type annotations, this file can be removed.
"""
from typing import Dict, Any, Optional, List, Union, Callable, Iterator, Match
import re

# Core types stubs
class ModuleConfig:
    def __init__(
        self, 
        ollama_client: Any = None,
        model_name: str = "",
        quality_threshold: float = 0.0,
        temperature: float = 0.0,
        max_tokens: int = 0, 
        conservative_bias: bool = False,
        consensus_config: Optional['ConsensusConfig'] = None
    ):
        self.ollama_client = ollama_client
        self.model_name = model_name
        self.quality_threshold = quality_threshold
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.conservative_bias = conservative_bias
        self.consensus_config = consensus_config

class ValidationResult:
    def __init__(self, success: bool = False, score: float = 0.0, data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.score = score
        self.data = data or {}

class ModuleResult:
    def __init__(self, success: bool = False, data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.data = data or {}

class ConsensusConfig:
    def __init__(
        self,
        conservative_selection: bool = False,
        quality_check_individual: bool = False,
        quality_check_consensus: bool = False,
        min_confidence_threshold: float = 0.0,
        max_timeline_days: int = 0
    ):
        self.conservative_selection = conservative_selection
        self.quality_check_individual = quality_check_individual
        self.quality_check_consensus = quality_check_consensus
        self.min_confidence_threshold = min_confidence_threshold
        self.max_timeline_days = max_timeline_days

# OllamaClient stub
class OllamaClient:
    def __init__(self, model: str = "", base_url: str = ""):
        self.model = model
        self.base_url = base_url
    
    def generate(self, prompt: str, **kwargs) -> str:
        return ""

# Specialist stubs
class CoverLetterGeneratorV2:
    def __init__(self, config: Optional[ModuleConfig] = None):
        self.config = config or ModuleConfig()
        self._description = "CoverLetterGeneratorV2 Specialist"
    
    def process(self, input_data: Dict[str, Any]) -> ModuleResult:
        return ModuleResult(True, {"cover_letter": ""})

class FactualConsistencySpecialist:
    def __init__(self, config: Optional[ModuleConfig] = None):
        self.config = config or ModuleConfig()
    
    def verify_cover_letter_consistency(
        self, cover_letter: str, job_posting: Dict[str, Any], cv_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"consistency_score": 1.0, "issues": []}

class LanguageCoherenceSpecialist:
    def __init__(self, config: Optional[ModuleConfig] = None):
        self.config = config or ModuleConfig()
    
    def enforce_language_consistency(self, cover_letter: str) -> Dict[str, Any]:
        return {"coherence_score": 1.0, "issues": []}

class AILanguageDetectionSpecialist:
    def __init__(self, config: Optional[ModuleConfig] = None):
        self.config = config or ModuleConfig()
    
    def detect_ai_markers(self, cover_letter: str) -> Dict[str, Any]:
        return {"ai_probability": 0.0, "issues": []}
