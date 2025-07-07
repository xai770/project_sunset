#!/usr/bin/env python3
"""
HTML cleaning functionality for staged job processing
"""

import re
import html
import logging
from typing import Optional
from bs4 import BeautifulSoup

from run_pipeline.utils.staged_processor.utils import logger

def clean_html(html_content: str) -> str:
    """
    Clean HTML content to plain text
    
    Args:
        html_content: Raw HTML content
        
    Returns:
        Clean plain text
    """
    # Parse with BeautifulSoup
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text
        text = soup.get_text(separator=" ")
        
        # Remove HTML entities
        text = html.unescape(text)
        
        # Normalize whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception as e:
        logger.error(f"Error cleaning HTML: {str(e)}")
        # Fallback to basic HTML tag removal
        text = re.sub('<[^<]+?>', '', html_content)
        text = html.unescape(text)
        return text
