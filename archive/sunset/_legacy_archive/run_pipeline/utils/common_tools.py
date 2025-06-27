#!/usr/bin/env python3
"""
Common tools and utilities shared across the run_pipeline package.

This module contains shared functions and utilities to avoid circular imports
between the cleaner_module and staged_processor modules.
"""

import os
import logging
import json
from pathlib import Path
from typing import Dict, Optional, Any

logger = logging.getLogger('common_tools')

def clean_llm_artifacts(text: str) -> str:
    """
    Clean up LLM-generated text artifacts
    
    Args:
        text: Text with potential artifacts
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove common LLM formatting artifacts
    lines = []
    for line in text.split("\n"):
        # Skip markdown code block markers
        if line.strip() in ["```", "```json", "```markdown", "```text", "```html"]:
            continue
            
        # Skip lines that are LLM thinking/context markers
        if any(marker in line.lower() for marker in [
            "here's a concise",
            "i'll create",
            "i'll extract",
            "i'll provide",
        ]):
            continue
            
        lines.append(line)
    
    return "\n".join(lines)

# Add any other shared functions from cleaner_module.py that are needed by staged_processor here
