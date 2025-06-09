#!/usr/bin/env python3
"""
LLM Client Module - Enhanced with LLM Factory Integration

Provides standardized access to LLM capabilities across the application.
This module now integrates with the LLM Factory specialists for quality-controlled
processing while maintaining backwards compatibility with existing code.
"""

import os
import sys
import logging
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger("run_pipeline.utils.llm_client")

# LLM Factory Integration
try:
    sys.path.insert(0, '/home/xai/Documents/llm_factory')
    from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
    from llm_factory.core.types import ModuleConfig
    from llm_factory.core.ollama_client import OllamaClient as FactoryOllamaClient
    LLM_FACTORY_AVAILABLE = True
    logger.info("✅ LLM Factory integration available")
except ImportError as e:
    logger.warning(f"⚠️ LLM Factory not available: {e}")
    LLM_FACTORY_AVAILABLE = False

class LLMClient:
    """
    Base LLM client class providing standard interface to LLMs.
    Now enhanced with LLM Factory integration for quality control.
    """
    
    def __init__(self, model: str = "llama3.2:latest"):
        """
        Initialize the LLM client
        
        Args:
            model: The model name to use
        """
        self.model = model
        self._initialize()
    
    def _initialize(self):
        """Initialize any required resources or connections"""
        pass
    
    def get_completion(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2048, system_prompt: Optional[str] = None) -> str:
        """
        Get a completion from the LLM
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: The temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt to define model behavior
            
        Returns:
            The generated completion text
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def available_models(self) -> List[str]:
        """
        Get list of available models
        
        Returns:
            List of available model names
        """
        return []

class EnhancedOllamaClient(LLMClient):
    """
    Enhanced LLM client with LLM Factory integration and fallback to standard Ollama.
    Maintains full backwards compatibility while adding quality control features.
    """
    
    def __init__(self, model: str = "llama3.2:latest", api_url: str = "http://localhost:11434"):
        self.api_url = api_url
        self.registry = None
        self._setup_llm_factory()
        super().__init__(model)
        
    def _setup_llm_factory(self):
        """Set up LLM Factory registry if available"""
        if LLM_FACTORY_AVAILABLE:
            try:
                self.registry = SpecialistRegistry()
                logger.info("✅ LLM Factory specialists loaded")
            except Exception as e:
                logger.warning(f"⚠️ LLM Factory setup failed: {e}")
                self.registry = None
        
    def _check_ollama_available(self):
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def _get_base_config(self, temperature: float = 0.3) -> Optional['ModuleConfig']:
        """Get configuration for LLM Factory specialists"""
        if LLM_FACTORY_AVAILABLE:
            try:
                from llm_factory.core.ollama_client import OllamaClient
                ollama_client = OllamaClient()
                return ModuleConfig(
                    models=[self.model],
                    conservative_bias=True,
                    quality_threshold=8.0,
                    ollama_client=ollama_client
                )
            except Exception:
                pass
        # Return None when LLM Factory is not available
        return None
    
    def _use_text_generation_specialist(self, prompt: str, temperature: float = 0.3, 
                                      max_tokens: int = 2048, system_prompt: Optional[str] = None) -> Optional[str]:
        """Try to use LLM Factory text generation specialist"""
        if not LLM_FACTORY_AVAILABLE:
            return None
        
        if not self.registry:
            return None

        try:  # type: ignore[unreachable]
            config = self._get_base_config(temperature)
            
            # Skip LLM Factory if config is None (fallback mode)
            if config is None:
                return None
            
            # Try to load text generation specialist
            specialist = self.registry.load_specialist("text_generation", config)
            
            input_data = {
                "text": prompt,
                "task": "generation",
                "context": system_prompt or "Generate a helpful response"
            }
            
            result = specialist.process(input_data)
            
            if result.success and result.data.get('generated_text'):
                logger.debug("✅ Used LLM Factory text generation specialist")
                return result.data['generated_text']
                
        except Exception as e:  # type: ignore[unreachable]
            logger.debug(f"LLM Factory specialist unavailable: {e}")
            
        return None
    
    def get_completion(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2048, system_prompt: Optional[str] = None) -> str:
        """
        Get a completion from Ollama with LLM Factory enhancement when available
        
        Args:
            prompt: The prompt to send to Ollama
            temperature: The temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt to define model behavior
            
        Returns:
            The generated completion text
        """
        
        # Try LLM Factory specialist first for enhanced quality
        if LLM_FACTORY_AVAILABLE:
            factory_result = self._use_text_generation_specialist(prompt, temperature, max_tokens, system_prompt)
            if factory_result:
                return factory_result
        
        # Fallback to standard Ollama processing
        try:
            # Check if Ollama is available
            if not self._check_ollama_available():
                logger.error("Ollama service is not available")
                return "Error: Ollama service is not available"
            
            # Prepare the API request
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Add system prompt if provided
            if system_prompt:
                data["system"] = system_prompt
            
            # Call the Ollama API
            response = requests.post(
                f"{self.api_url}/api/generate",
                json=data,
                timeout=120  # Allow up to 120 seconds for generation
            )
            
            # Check for successful response
            if response.status_code == 200:
                result = response.json()
                if "response" in result:
                    return str(result["response"])  # Ensure string return
                else:
                    logger.error(f"Unexpected response format from Ollama: {result}")
                    return "Error: Unexpected response format from Ollama"
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return f"Error: Ollama API returned status code {response.status_code}"
                
        except requests.RequestException as e:
            logger.error(f"Error communicating with Ollama API: {e}")
            return "Error communicating with Ollama API"
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding Ollama response: {e}")
            return "Error decoding response from Ollama"
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}")
            return f"Error: {str(e)}"
    
    def available_models(self) -> List[str]:
        """Get list of available models from Ollama"""
        try:
            if not self._check_ollama_available():
                return []
            
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                if "models" in models_data:
                    return [model["name"] for model in models_data["models"]]
            return []
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []

# Maintain backwards compatibility with original class name
OllamaClient = EnhancedOllamaClient

class MockLLMClient(LLMClient):
    """Mock LLM client for testing without an actual LLM service"""
    
    def get_completion(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2048, system_prompt: Optional[str] = None) -> str:
        """Mock completion for testing"""
        # Handle translation requests
        if "translate" in prompt.lower() and "german" in prompt.lower():
            # Extract German text in quotes
            import re
            german_match = re.search(r'"([^"]*)"', prompt)
            if german_match:
                german_text = german_match.group(1)
                translations = {
                    "Datenverarbeitung": "Experience with data processing and visualization",
                    "Softwareentwicklungsmethoden": "Knowledge of agile software development methods", 
                    "Problemlösung": "Ability for problem solving and teamwork"
                }
                for german, english in translations.items():
                    if german in german_text:
                        return english
                return f"Mock translation of '{german_text}'"
            return "Mock translation: [text not found in quotes]"  # type: ignore[unreachable]
        
        # Generic mock response for all other cases
        return f"Mock LLM response for: {prompt[:50]}..."

class OLMoClient(EnhancedOllamaClient):
    """Specialized client for OLMo2 with LLM Factory enhancement"""
    
    def __init__(self, version: str = "latest", api_url: str = "http://localhost:11434"):
        """
        Initialize the OLMo client
        
        Args:
            version: The OLMo version to use (defaults to latest)
            api_url: The Ollama API URL
        """
        model = f"olmo2:{version}"
        super().__init__(model, api_url)

# Global client instance
_llm_client_instance: Optional[LLMClient] = None

def get_llm_client(force_new: bool = False, model: str = "llama3.2") -> LLMClient:
    """
    Get or create an LLM client instance (Singleton pattern)
    Now returns Enhanced LLM client with LLM Factory integration
    
    Args:
        force_new: Force creation of a new client instance
        model: The model to use (default: llama3.2)
        
    Returns:
        An LLMClient instance
    """
    global _llm_client_instance
    
    # Always return a new instance if force_new is True, or if no instance exists
    if force_new or _llm_client_instance is None:
        # Try to create the enhanced Ollama client
        if "llama3.2" in model or "llama3" in model:
            try:
                model_name = f"{model}:latest" if ":" not in model else model
                ollama_client = EnhancedOllamaClient(model_name)
                if ollama_client._check_ollama_available():
                    _llm_client_instance = ollama_client
                else:
                    logger.warning("Ollama not available, falling back to mock LLM client")
                    _llm_client_instance = MockLLMClient(model)
            except Exception:
                # Fall back to mock if there's any error
                logger.warning("Error initializing Enhanced Ollama client, falling back to mock LLM client")
                _llm_client_instance = MockLLMClient(model)
        else:
            # For non-llama models, use mock client
            _llm_client_instance = MockLLMClient(model)
    
    # Ensure we never return None
    if _llm_client_instance is None:
        _llm_client_instance = MockLLMClient(model)
    
    return _llm_client_instance

def get_olmo_client(version: str = "latest") -> LLMClient:
    """
    Get a specialized OLMo client with LLM Factory enhancement
    
    Args:
        version: The OLMo version to use
        
    Returns:
        An LLMClient instance (either Enhanced OLMoClient or MockLLMClient as fallback)
    """
    try:
        olmo_client = OLMoClient(version)
        if olmo_client._check_ollama_available():
            return olmo_client
        else:
            logger.warning("Ollama service not available for OLMo")
            return MockLLMClient(f"olmo2:{version}")
    except Exception as e:
        logger.warning(f"Error initializing OLMo client: {e}")
        return MockLLMClient(f"olmo2:{version}")

# Enhanced standalone functions with LLM Factory integration
def call_ollama_api(
    prompt: str,
    model: str = "llama3.2:latest",
    temperature: float = 0.3,
    max_tokens: int = 2048,
    system_prompt: Optional[str] = None
) -> str:
    """
    Call Ollama API with the given prompt - Enhanced with LLM Factory integration
    
    Args:
        prompt: The user prompt to send to the model
        model: The model to use (default: llama3.2:latest)
        temperature: The temperature setting (0.0 to 1.0)
        max_tokens: Maximum tokens to generate
        system_prompt: Optional system prompt to define behavior
        
    Returns:
        The generated response as a string
    """
    try:
        # Create and use the Enhanced OllamaClient
        client = EnhancedOllamaClient(model=model)
        return client.get_completion(
            prompt=prompt, 
            temperature=temperature, 
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
        
    except Exception as e:
        logger.error(f"Error in call_ollama_api: {e}")
        raise Exception(f"LLM API call failed: {str(e)}")

def call_ollama_api_json(
    prompt: str, 
    model: str = "llama3.2:latest",
    temperature: float = 0.3,
    max_tokens: int = 2048,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Call Ollama API and parse the response as JSON - Enhanced with LLM Factory integration
    
    Args:
        prompt: The user prompt to send to the model
        model: The model to use (default: llama3.2:latest)
        temperature: The temperature setting (0.0 to 1.0)
        max_tokens: Maximum tokens to generate
        system_prompt: Optional system prompt to define behavior
        
    Returns:
        The parsed JSON response as a dictionary
    """
    # First get the text response using enhanced client
    response_text = call_ollama_api(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt
    )
    
    try:
        # Try to extract JSON from the response (models sometimes add extra text)
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group()
            parsed_json: Dict[str, Any] = json.loads(json_str)
            return parsed_json
        
        # If no JSON object found, try parsing the whole thing
        try:
            parsed_json = json.loads(response_text) # type: ignore[unreachable]
            return parsed_json
        except json.JSONDecodeError:  # type: ignore[unreachable]
            # If still no valid JSON, return a default structure
            return {"error": "No valid JSON found in response", "raw_response": response_text}
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from LLM response: {e}")
        logger.debug(f"Raw response: {response_text}")
        raise Exception(f"Failed to parse JSON from LLM response: {str(e)}") 
    except Exception as e:
        logger.error(f"Error in JSON LLM call: {e}")
        raise Exception(f"JSON LLM call failed: {str(e)}")

def get_available_models() -> List[str]:
    """
    Get a list of available models from Ollama
    
    Returns:
        List of available model names
    """
    try:
        # Create a temporary Enhanced OllamaClient to check models
        client = EnhancedOllamaClient()
        return client.available_models()
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        return []
