#!/usr/bin/env python3
# mypy: disable-error-code=unreachable
"""
LLM Client Module

Provides standardized access to LLM capabilities across the application.
This module abstracts the specific LLM implementation being used and provides
a consistent interface for making prompts. Enhanced with LLM Factory integration
for quality-controlled processing.
"""

import os
import sys
import logging
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# Try to import LLM Factory for quality-controlled processing
try:
    from llm_factory.specialist_registry import SpecialistRegistry  # type: ignore
    from llm_factory.quality_control import QualityController  # type: ignore
    LLM_FACTORY_AVAILABLE = True
except ImportError:
    LLM_FACTORY_AVAILABLE = False

logger = logging.getLogger("run_pipeline.utils.llm_client")

class LLMFactoryEnhancer:
    """
    LLM Factory integration layer for enhanced LLM capabilities
    """
    
    def __init__(self):
        self.registry = None
        self.quality_controller = None
        self._init_factory()
    
    def _init_factory(self):
        """Initialize LLM Factory if available"""
        if not LLM_FACTORY_AVAILABLE:
            logger.info("LLM Factory not available, using standard LLM client")
            return
        
        try:
            # Initialize specialist registry
            self.registry = SpecialistRegistry()
            
            # Register general purpose specialist
            self.registry.register_specialist(
                "general_assistant",
                {
                    "type": "text_generation",
                    "model": "llama3.2:latest",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "system_prompt": "You are a helpful AI assistant providing high-quality responses with accuracy and clarity."
                }
            )
            
            # Initialize quality controller
            self.quality_controller = QualityController()
            logger.info("LLM Factory initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize LLM Factory: {e}")
            self.registry = None
            self.quality_controller = None
    
    def enhanced_completion(self, prompt: str, model: str = "llama3.2:latest", 
                          temperature: float = 0.3, max_tokens: int = 2048,
                          system_prompt: Optional[str] = None) -> Optional[str]:
        """Get quality-controlled completion using LLM Factory"""
        if not self.registry:
            return None
        
        try:
            # Update specialist config for this specific request
            specialist_config = {
                "type": "text_generation",
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "system_prompt": system_prompt or "You are a helpful AI assistant."
            }
            
            # Register or update specialist
            self.registry.register_specialist("dynamic_specialist", specialist_config)
            specialist = self.registry.get_specialist("dynamic_specialist")
            
            # Generate response
            response = specialist.generate(prompt)
            
            # Apply quality control
            if self.quality_controller:
                quality_score = self.quality_controller.evaluate_response(response, prompt)
                logger.info(f"LLM Factory response quality score: {quality_score}")
            
            return response  # type: ignore
            
        except Exception as e:
            logger.error(f"Error in LLM Factory enhanced completion: {e}")
            return None

# Global LLM Factory enhancer instance
_llm_factory_enhancer = None

def get_llm_factory_enhancer() -> LLMFactoryEnhancer:
    """Get singleton LLM Factory enhancer"""
    global _llm_factory_enhancer
    if _llm_factory_enhancer is None:
        _llm_factory_enhancer = LLMFactoryEnhancer()
    return _llm_factory_enhancer

class LLMClient:
    """
    Base LLM client class providing standard interface to LLMs.
    Currently implemented for Ollama, but can be extended for other systems.
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
    

class OllamaClient(LLMClient):
    """LLM client implementation for Ollama"""
    
    def __init__(self, model: str = "llama3.2:latest", api_url: str = "http://localhost:11434"):
        self.api_url = api_url
        super().__init__(model)
        
    def _check_ollama_available(self):
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_completion(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2048, system_prompt: Optional[str] = None) -> str:
        """
        Get a completion from Ollama using the requests library
        
        Args:
            prompt: The prompt to send to Ollama
            temperature: The temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt to define model behavior
            
        Returns:
            The generated completion text
        """
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
                    return result["response"]  # type: ignore
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


class MockLLMClient(LLMClient):
    """Mock LLM client for testing without an actual LLM service"""
    
    def get_completion(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2048, system_prompt: Optional[str] = None) -> str:
        """
        Return a mock completion for testing
        
        Args:
            prompt: The input prompt
            temperature: The temperature parameter (ignored in mock)
            max_tokens: Maximum tokens to generate (ignored in mock)
            system_prompt: Optional system prompt (ignored in mock)
            
        Returns:
            A mock response based on the prompt
        """
        logger.warning("Using mock LLM client - not suitable for production use")
        
        if "translate" in prompt.lower():
            # Extract German text from the prompt
            start_quote = prompt.find('"')
            end_quote = prompt.rfind('"')
            
            if start_quote >= 0 and end_quote > start_quote:
                german_text = prompt[start_quote+1:end_quote]
                
                # Create mock translations for testing
                if "Datenverarbeitung" in german_text:
                    return "Experience with data processing and visualization"
                elif "Softwareentwicklungsmethoden" in german_text:
                    return "Knowledge of agile software development methods"
                elif "Problemlösung" in german_text:
                    return "Ability for problem solving and teamwork"
                else:
                    return f"Mock translation of '{german_text}'"
            else:
                return "Mock translation: [text not found in quotes]"
        
        # Generic mock response
        return f"Mock LLM response for: {prompt[:50]}..."


class OLMoClient(OllamaClient):
    """Specialized client for OLMo2"""
    
    def __init__(self, version: str = "latest", api_url: str = "http://localhost:11434"):
        """
        Initialize the OLMo client
        
        Args:
            version: The OLMo version to use (defaults to latest)
            api_url: The Ollama API URL
        """
        model = f"olmo2:{version}"
        super().__init__(model, api_url)


_llm_client_instance = None

def get_llm_client(force_new: bool = False, model: str = "llama3.2") -> LLMClient:
    """
    Get a singleton instance of the LLM client
    
    Args:
        force_new: Whether to create a new instance even if one exists
        model: The model name to use
        
    Returns:
        An LLMClient instance
    """
    global _llm_client_instance
    
    if _llm_client_instance is None or force_new:  # type: ignore[unreachable]
        # Check if we're in a testing environment
        if 'pytest' in sys.modules or 'PYTEST_CURRENT_TEST' in os.environ:
            _llm_client_instance = MockLLMClient(model)
        else:
            # Try to use Ollama first
            try:
                ollama_client = OllamaClient(model)
                if ollama_client._check_ollama_available():
                    _llm_client_instance = ollama_client  # type: ignore
                    logger.info(f"Using Ollama with model {model}")
                else:
                    logger.warning("Ollama not available, falling back to mock LLM client")
                    _llm_client_instance = MockLLMClient(model)
            except Exception:
                # Fall back to mock if there's any error
                logger.warning("Error initializing Ollama client, falling back to mock LLM client")
                _llm_client_instance = MockLLMClient(model)
    
    # Ensure we always return a valid instance
    if _llm_client_instance is None:
        _llm_client_instance = MockLLMClient(model)
    
    return _llm_client_instance

def get_olmo_client(version: str = "latest") -> LLMClient:
    """
    Get a specialized OLMo client
    
    Args:
        version: The OLMo version to use
        
    Returns:
        An LLMClient instance (either OLMoClient or MockLLMClient as fallback)
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

# Add these standalone functions for JMFS integration
def call_ollama_api(
    prompt: str,
    model: str = "llama3.2:latest",
    temperature: float = 0.3,
    max_tokens: int = 2048,
    system_prompt: Optional[str] = None
) -> str:
    """
    Call Ollama API with the given prompt - enhanced with LLM Factory integration
    
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
        # Try LLM Factory for enhanced quality first
        enhancer = get_llm_factory_enhancer()
        enhanced_response = enhancer.enhanced_completion(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
        
        if enhanced_response:
            return enhanced_response
        
        # Fallback to standard Ollama client
        client = OllamaClient(model=model)
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
    Call Ollama API and parse the response as JSON - enhanced with LLM Factory
    
    Args:
        prompt: The user prompt to send to the model
        model: The model to use (default: llama3.2:latest)
        temperature: The temperature setting (0.0 to 1.0)
        max_tokens: Maximum tokens to generate
        system_prompt: Optional system prompt to define behavior
        
    Returns:
        The parsed JSON response as a dictionary
    """
    try:
        # First get the text response (already enhanced with LLM Factory)
        response_text = call_ollama_api(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
        
        # Try to extract JSON from the response (models sometimes add extra text)
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group()
            result: Dict[str, Any] = json.loads(json_str)
            return result
        else:
            # If no JSON object found, try parsing the whole thing
            result = json.loads(response_text)  # type: ignore[unreachable]
            return result  # type: ignore[unreachable]
            
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
        # Create a temporary OllamaClient to check models
        client = OllamaClient()
        
        if not client._check_ollama_available():
            logger.warning("Ollama service not available")
            return []
            
        response = requests.get(f"{client.api_url}/api/tags", timeout=5)
        
        if response.status_code != 200:
            logger.error(f"Error getting models: {response.status_code}")
            return []
            
        models_data = response.json()
        
        if "models" in models_data:
            # Extract model names (without tags)
            return [model["name"].split(":")[0] for model in models_data["models"]]
        else:
            logger.warning("Unexpected response format from Ollama API")
            return []
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        return []
