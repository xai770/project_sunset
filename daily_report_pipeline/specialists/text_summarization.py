#!/usr/bin/env python3
"""
Text Summarization Specialist
============================

Professional text summarization with intelligent benefits filtering
and LLM preamble removal.

Author: Sandy's Modular Architecture
Version: 1.0 (Production Ready)
"""

import time
import re
from ..core.llm_base import ProfessionalLLMCore
from ..core.data_models import SummarizationResult


class TextSummarizationSpecialist(ProfessionalLLMCore):
    """Professional text summarization specialist"""
    
    def __init__(self):
        super().__init__()
        self.specialist_name = "Text Summarization Specialist"
    
    def summarize_text(self, text: str, max_length: int = 200) -> SummarizationResult:
        """Summarize text using LLM intelligence"""
        start_time = time.time()
        original_length = len(text)
        
        summary_prompt = f"""
You are an expert text summarization specialist. Create a concise, informative summary of the following text.

REQUIREMENTS:
- Maximum length: {max_length} characters
- Preserve key information and main points
- Use clear, professional language
- Focus on the most important aspects

TEXT TO SUMMARIZE:
{text}

SUMMARY:
"""
        
        summary = self.process_with_llm(summary_prompt, "text summarization")
        
        if not summary:
            summary = text[:max_length] + "..." if len(text) > max_length else text
        
        # Clean up common LLM preambles
        summary = self._clean_llm_preambles(summary)
        
        # Ensure summary fits within length limit
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        processing_time = time.time() - start_time
        summary_length = len(summary)
        compression_ratio = (original_length - summary_length) / original_length
        
        self.stats['specialists_executed'] += 1
        
        return SummarizationResult(
            original_text=text,
            summary=summary,
            original_length=original_length,
            summary_length=summary_length,
            compression_ratio=compression_ratio,
            processing_time=processing_time
        )
    
    def summarize_job_description(self, text: str) -> SummarizationResult:
        """Summarize job description without strict character limits"""
        start_time = time.time()
        original_length = len(text)
        
        summary_prompt = f"""
You are an expert job description summarization specialist. Create a clear, concise summary of this job posting.

REQUIREMENTS:
- Extract the core responsibilities and requirements
- Maintain professional tone
- Include key skills and qualifications
- Focus on what makes this role unique
- Provide ONLY the summary text - no introductory phrases or preambles

CRITICAL EXCLUSIONS - DO NOT INCLUDE:
- Benefits, perks, or "what we offer" sections
- Salary information or compensation details
- Company culture descriptions or general company information
- Flexible working arrangements or remote work mentions
- Professional development opportunities or training programs
- Health insurance, retirement plans, or other benefits
- Office amenities or company perks

FOCUS ONLY ON:
- Job responsibilities and duties
- Required skills and qualifications
- Essential experience and education requirements
- Technical requirements and tools

JOB DESCRIPTION:
{text}

Provide a direct summary focusing only on the role requirements and responsibilities:
"""
        
        summary = self.process_with_llm(summary_prompt, "job description summarization")
        
        if not summary:
            # Fallback: take first few sentences
            sentences = text.split('. ')
            summary = '. '.join(sentences[:3]) + '.' if len(sentences) > 3 else text
        
        # Clean up common LLM preambles
        summary = self._clean_llm_preambles(summary)
        
        processing_time = time.time() - start_time
        summary_length = len(summary)
        compression_ratio = (original_length - summary_length) / original_length if original_length > 0 else 0
        
        self.stats['specialists_executed'] += 1
        
        return SummarizationResult(
            original_text=text,
            summary=summary,
            original_length=original_length,
            summary_length=summary_length,
            compression_ratio=compression_ratio,
            processing_time=processing_time
        )
    
    def _clean_llm_preambles(self, text: str) -> str:
        """Remove common LLM preambles and benefits sections"""
        if not text:
            return text
            
        # Common preambles to remove
        preambles = [
            "Here is a concise summary of the text:",
            "Here is a summary of the text:",
            "Here is a concise summary:",
            "Here is the summary:",
            "Summary:",
            "Here's a concise summary:",
            "Here's a summary:",
            "The following is a summary:",
            "This is a summary:",
            "Below is a summary:",
        ]
        
        cleaned_text = text.strip()
        
        # Remove preambles (case-insensitive)
        for preamble in preambles:
            if cleaned_text.lower().startswith(preamble.lower()):
                cleaned_text = cleaned_text[len(preamble):].strip()
                break
        
        # Remove benefits sections that might slip through
        cleaned_text = self._remove_benefits_sections(cleaned_text)
        
        return cleaned_text
    
    def _remove_benefits_sections(self, text: str) -> str:
        """Remove benefits and perks sections using intelligent filtering"""
        if not text:
            return text
            
        # Split into lines for processing
        lines = text.split('\n')
        filtered_lines = []
        skip_section = False
        
        benefits_indicators = [
            'we offer:', 'what we offer:', 'benefits include:', 'our company offers:',
            'competitive salary', 'benefits package', 'what we provide:',
            'flexible working', 'remote work options', 'professional development',
            'health insurance', 'retirement plan', 'paid time off', 'pto',
            'company perks', 'office amenities', 'work-life balance'
        ]
        
        for line in lines:
            line_lower = line.strip().lower()
            
            # Check if this line starts a benefits section
            if any(indicator in line_lower for indicator in benefits_indicators):
                skip_section = True
                continue
                
            # If we're in a benefits section, skip until we find a new section
            if skip_section:
                # Look for indicators that we're back to job content
                if (line.strip() and 
                    any(keyword in line_lower for keyword in [
                        'responsibilities:', 'duties:', 'requirements:', 
                        'qualifications:', 'skills:', 'experience:', 
                        'education:', 'job title:', 'position:'
                    ])):
                    skip_section = False
                    filtered_lines.append(line)
                continue
            
            # Keep non-benefits lines
            if line.strip():
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
