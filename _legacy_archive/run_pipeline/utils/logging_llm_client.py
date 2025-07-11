#!/usr/bin/env python3
"""
Logging LLM Client Module

Extends the standard LLM client to log all prompts and responses for debugging purposes.
"""

import os
import sys
import logging
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the original LLM client
from run_pipeline.utils.llm_client import LLMClient, OllamaClient

# Configure logging
logger = logging.getLogger("run_pipeline.utils.logging_llm_client")

class LoggingOllamaClient(OllamaClient):
    """LLM client implementation for Ollama with logging of all prompts and responses"""
    
    def __init__(self, model: str = "llama3.2:latest", api_url: str = "http://localhost:11434", log_dir: Optional[str] = None):
        super().__init__(model, api_url)
        
        # Set up logging directory
        if log_dir is None:
            self.log_dir: Path = PROJECT_ROOT / "logs" / "llm_dialogue"
        else:
            self.log_dir = Path(log_dir)
            
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create a unique log file for this session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"llm_dialogue_{timestamp}.json"
        
        # Initialize the log file
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump({"model": model, "dialogues": []}, f, indent=2)
            
        logger.info(f"Logging LLM dialogues to {self.log_file}")
    
    def get_completion(self, prompt: str) -> str:
        """
        Get a completion from Ollama and log both the prompt and response
        
        Args:
            prompt: The prompt to send to Ollama
            
        Returns:
            The generated completion text
        """
        # Log the prompt
        dialogue_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": None
        }
        
        try:
            # Call the original method to get the response
            response = super().get_completion(prompt)
            
            # Log the response
            dialogue_entry["response"] = response
            
            # Append to the log file
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
                
                log_data["dialogues"].append(dialogue_entry)
                
                with open(self.log_file, "w", encoding="utf-8") as f:
                    json.dump(log_data, f, indent=2)
            except Exception as e:
                logger.error(f"Error logging dialogue: {e}")
            
            return response
            
        except Exception as e:
            # Log the error
            dialogue_entry["error"] = str(e)
            
            # Attempt to append to the log file even on error
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
                
                log_data["dialogues"].append(dialogue_entry)
                
                with open(self.log_file, "w", encoding="utf-8") as f:
                    json.dump(log_data, f, indent=2)
            except Exception as log_err:
                logger.error(f"Error logging dialogue error: {log_err}")
            
            # Re-raise the original exception
            raise

# Factory function to get a logging LLM client instance
_logging_llm_client_instance = None

def get_logging_llm_client(model: str = "llama3.2:latest", force_new: bool = False) -> LoggingOllamaClient:
    """
    Get a logging LLM client instance
    
    Args:
        model: The model name to use
        force_new: Whether to create a new instance even if one exists
        
    Returns:
        A LoggingOllamaClient instance
    """
    global _logging_llm_client_instance
    
    if _logging_llm_client_instance is None or force_new:
        _logging_llm_client_instance = LoggingOllamaClient(model)
    
    return _logging_llm_client_instance

def call_logging_ollama_api(prompt: str, model: str = "llama3.2", temperature: float = 0.7, max_tokens: int = 2048) -> str:
    """
    Call Ollama API with logging to generate a response to the given prompt.
    
    Args:
        prompt: The prompt to send to the LLM
        model: The model name to use
        temperature: The temperature for generation (0.0 to 1.0)
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        The generated text response
    """
    client = get_logging_llm_client(model=model)
    
    # Set additional parameters if using OllamaClient
    if isinstance(client, OllamaClient):
        # TODO: Add support for temperature and max_tokens in OllamaClient
        pass
        
    response = client.get_completion(prompt)
    return response
