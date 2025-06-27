#!/usr/bin/env python3
"""
Specialist Access Configuration and Status
=========================================
Configuration and status checking for specialist access.
"""

import logging
from typing import Dict, Any, Optional

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

# Content Extraction Specialist v3.3 Production Integration
try:
    from core.content_extraction_specialist import ContentExtractionSpecialistV33
    CONTENT_EXTRACTION_AVAILABLE = True
    logger.info("✅ Content Extraction Specialist v3.3 loaded")
except ImportError as e:
    CONTENT_EXTRACTION_AVAILABLE = False
    logger.warning(f"⚠️ Content Extraction Specialist not available: {e}")

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
        from core.job_matching_specialists import DirectJobMatchingSpecialists
        specialists = DirectJobMatchingSpecialists()
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
