#!/usr/bin/env python3
"""
LLM Base Classes for Daily Report Pipeline
Professional LLM processing core functionality
"""

import time
import logging
import requests
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMProcessingError(Exception):
    """Raised when LLM processing encounters errors"""
    pass

class ProfessionalLLMCore:
    """Core LLM interface for specialist processing"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3.2:latest"):
        self.ollama_url = ollama_url
        self.model = model
        self.stats = {
            'specialists_executed': 0,
            'total_processing_time': 0,
            'success_rate': 0.0
        }
    
    def process_with_llm(self, prompt: str, operation: str = "LLM processing") -> str:
        """Core LLM processing function"""
        start_time = time.time()
        
        try:
            logger.info(f"Processing: {operation}")
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "top_p": 0.9}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '').strip()
                processing_time = time.time() - start_time
                
                # Update stats
                self.stats['total_processing_time'] += processing_time
                
                logger.info(f"Completed {operation} in {processing_time:.2f}s")
                return result
            else:
                raise LLMProcessingError(f"LLM processing failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"LLM processing error: {e}")
            return ""
