#!/usr/bin/env python3
"""
LLM Client module for job matching - Enhanced with LLM Factory Integration

This module handles the interaction with LLM services using quality-controlled
LLM Factory specialists while maintaining backwards compatibility.
"""
import sys
import logging
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logger = logging.getLogger('job_matcher.llm_client')

# LLM Factory Integration
try:
    sys.path.insert(0, '/home/xai/Documents/llm_factory')
    from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
    from llm_factory.core.types import ModuleConfig
    from llm_factory.core.ollama_client import OllamaClient
    LLM_FACTORY_AVAILABLE = True
    logger.info("✅ LLM Factory integration available for job matching")
except ImportError as e:
    logger.warning(f"⚠️ LLM Factory not available, falling back to basic implementation: {e}")
    from run_pipeline.utils.llm_client import call_ollama_api, get_llm_client, MockLLMClient
    LLM_FACTORY_AVAILABLE = False

def call_llama3_api(prompt):
    """
    Call the LLM API with a prompt using LLM Factory specialists for enhanced quality.
    
    Args:
        prompt: The prompt to send to the LLM
        
    Returns:
        The response from the LLM
        
    Raises:
        RuntimeError: If no LLM service is available or working properly
    """
    if LLM_FACTORY_AVAILABLE:
        return _call_llm_factory_api(prompt)
    else:
        return _call_fallback_api(prompt)

def _call_llm_factory_api(prompt: str) -> str:
    """
    Enhanced LLM call using LLM Factory specialists.
    
    Args:
        prompt: The prompt to process
        
    Returns:
        Quality-controlled response from LLM Factory
    """
    try:
        registry = SpecialistRegistry()
        ollama_client = OllamaClient()
        
        # Use text generation specialist for general prompts
        config = ModuleConfig(
            models=["llama3.2:latest"],
            conservative_bias=False,  # Allow varied responses
            quality_threshold=7.0,
            ollama_client=ollama_client
        )
        
        specialist = registry.load_specialist("text_generation", config)
        
        input_data = {
            "text": prompt,
            "task": "job_matching_analysis",
            "context": "Professional job matching and assessment"
        }
        
        result = specialist.process(input_data)
        
        if result.success and result.data.get('generated_text'):
            logger.info("✅ Used LLM Factory text generation specialist")
            return str(result.data['generated_text'])
        else:
            logger.warning("⚠️ LLM Factory specialist failed, using fallback")
            return _call_fallback_api(prompt)
            
    except Exception as e:
        logger.error(f"❌ LLM Factory API call failed: {e}")
        return _call_fallback_api(prompt)

def _call_fallback_api(prompt: str) -> str:
    """
    Fallback to basic LLM client.
    
    Args:
        prompt: The prompt to process
        
    Returns:
        Response from basic LLM client
        
    Raises:
        RuntimeError: If basic LLM service is unavailable
    """
    from run_pipeline.utils.llm_client import call_ollama_api, get_llm_client, MockLLMClient
    
    # First check if Ollama is actually available
    client = get_llm_client(force_new=True, model="llama3.2")
    if isinstance(client, MockLLMClient):
        raise RuntimeError(
            "Ollama service is not available or not working properly. "
            "Make sure Ollama is running and the service is accessible."
        )
    
    # Enhanced LLM call - try enhanced client first for better quality
    try:
        from run_pipeline.utils.llm_client_enhanced import call_ollama_api as enhanced_call
        response = enhanced_call(prompt, model="llama3.2:latest", temperature=0.9)
    except Exception as e:
        # Fallback to direct call if enhanced client fails
        response = call_ollama_api(prompt, model="llama3.2:latest", temperature=0.9)
    
    # Check if the response looks like a mock response
    if "Mock LLM response" in response:
        raise RuntimeError(
            "Received a mock response from the LLM client. "
            "Make sure Ollama is running and the service is accessible."
        )
    
    return response
