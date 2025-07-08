#!/usr/bin/env python3
"""
Content Extraction Specialist v4.0 - ENHANCED 5-DIMENSIONAL EXTRACTION
====================================================================

ENHANCED VERSION - Now includes Arden's 5-dimensional requirements framework
with German localization and structured extraction patterns.

Author: Sandy + Arden Enhancement Integration
Version: 4.0 (5D Enhanced)
"""

import time
from typing import List, Optional
from ..core.llm_base import ProfessionalLLMCore
from ..core.data_models import ContentExtractionResult

# Import enhanced requirements extractor
try:
    from .enhanced_requirements_extraction import EnhancedRequirementsExtractor, FiveDimensionalRequirements
except ImportError:
    EnhancedRequirementsExtractor = None
    FiveDimensionalRequirements = None
    print("⚠️ Enhanced requirements extraction not available - using LLM fallback only")


class ContentExtractionSpecialist(ProfessionalLLMCore):
    """ENHANCED Content Extraction Specialist v4.0 - 5-Dimensional Requirements Framework"""
    
    def __init__(self):
        super().__init__()
        self.specialist_name = "Content Extraction Specialist v4.0 ENHANCED (5D Framework)"
        self.ollama_url = "http://localhost:11434"
        self.preferred_model = "mistral:latest"
        self.fallback_models = ["olmo2:latest", "dolphin3:8b", "qwen3:latest", "llama3.2:latest"]
        
        # Initialize enhanced requirements extractor
        if EnhancedRequirementsExtractor:
            self.enhanced_extractor = EnhancedRequirementsExtractor()
            print("✅ Enhanced 5D Requirements Extractor initialized")
        else:
            self.enhanced_extractor = None
            print("⚠️ Enhanced extractor not available - using LLM fallback only")
    
    def extract_content(self, job_description: str) -> ContentExtractionResult:
        """Extract skills using ENHANCED v4.0 with 5-dimensional framework"""
        start_time = time.time()
        
        # Enhanced requirements data
        enhanced_requirements = None
        
        try:
            # PRIMARY: Use enhanced 5D extraction if available
            if self.enhanced_extractor:
                enhanced_requirements = self.enhanced_extractor.extract_requirements(job_description)
                
                # Convert enhanced data to backward-compatible format
                technical_skills = [req.skill for req in enhanced_requirements.technical]
                business_skills = [req.domain if hasattr(req, 'domain') else req.experience_type 
                                 for req in enhanced_requirements.business]
                soft_skills = [req.skill for req in enhanced_requirements.soft_skills]
                
                print(f"  ✅ Enhanced 5D extraction: {len(technical_skills)} technical, {len(business_skills)} business, {len(soft_skills)} soft skills")
                
            else:
                # FALLBACK: Use existing LLM-based extraction
                print("  ⚠️ Using LLM fallback extraction (enhanced not available)")
                technical_skills = self._extract_technical_skills_v34(job_description)
                business_skills = self._extract_business_skills_v34(job_description)
                soft_skills = self._extract_soft_skills_v34(job_description)
                
        except Exception as e:
            print(f"  ⚠️ Enhanced extraction error: {e} - falling back to LLM")
            # FALLBACK: Use existing LLM-based extraction
            technical_skills = self._extract_technical_skills_v34(job_description)
            business_skills = self._extract_business_skills_v34(job_description)
            soft_skills = self._extract_soft_skills_v34(job_description)
        
        # Combine and deduplicate with case-insensitive matching
        all_skills = []
        seen = set()
        
        for skill_list in [technical_skills, soft_skills, business_skills]:
            for skill in skill_list:
                skill_clean = skill.strip()
                skill_lower = skill_clean.lower()
                if skill_clean and skill_lower not in seen:
                    all_skills.append(skill_clean)
                    seen.add(skill_lower)
        
        processing_time = time.time() - start_time
        self.stats['specialists_executed'] += 1
        
        return ContentExtractionResult(
            technical_skills=technical_skills,
            soft_skills=soft_skills, 
            business_skills=business_skills,
            all_skills=all_skills,
            enhanced_requirements=enhanced_requirements,  # NEW: Enhanced 5D data
            processing_time=processing_time
        )
    
    def _call_ollama_v34(self, prompt: str, model: str = None) -> str:
        """Enhanced Ollama integration with robust error handling - v3.4"""
        try:
            import requests
        except ImportError:
            print("⚠️  Warning: requests library not found.")
            return ""
            
        model = model or self.preferred_model
        payload = {"model": model, "prompt": prompt, "stream": False}
        
        try:
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"⚠️  Model {model} failed: {str(e)}")
            # Try fallback models
            for fallback in self.fallback_models:
                if fallback != model:
                    try:
                        payload_fallback = {"model": fallback, "prompt": prompt, "stream": False}
                        response = requests.post(f"{self.ollama_url}/api/generate", json=payload_fallback, timeout=30)
                        if response.status_code == 200:
                            result = response.json()
                            return result.get('response', '').strip()
                    except:
                        continue
            return ""
    
    def _parse_skills_precise_v34(self, response: str) -> List[str]:
        """Enhanced skill parsing with robust error handling - v3.4"""
        import re
        skills = []
        
        # Handle empty or invalid responses
        if not response or not response.strip():
            return skills
            
        for line in response.split('\n'):
            line = line.strip()
            if not line or len(line) < 2:
                continue
                
            # Remove any formatting artifacts
            line = re.sub(r'^\d+\.\s*', '', line)  # Remove numbers
            line = re.sub(r'^[-•*]\s*', '', line)  # Remove bullets
            line = re.sub(r'\s*\([^)]*\)', '', line)  # Remove parentheses
            
            # Clean whitespace
            line = re.sub(r'\s+', ' ', line).strip()
            
            # Skip if too long (likely explanation, not skill name)
            if len(line.split()) > 4:
                continue
                
            # Skip verbose indicators
            if any(indicator in line.lower() for indicator in ['knowledge of', 'experience in', 'familiarity with']):
                continue
                
            if line and len(line) > 1:
                skills.append(line)
                
        return skills
    
    def _extract_technical_skills_v34(self, job_description: str) -> List[str]:
        """Extract technical skills with precision prompts - v3.4 WORKING"""
        prompt = f"""You are a PRECISION TECHNICAL SKILLS EXTRACTOR.

CRITICAL INSTRUCTION: Extract ONLY technical skills and tools that are EXPLICITLY MENTIONED in the job description text. DO NOT add common technical skills for the role.

EXAMPLE - CORRECT EXTRACTION:
Job text: "Programming knowledge in VBA, Python or similar programming languages"
CORRECT OUTPUT: VBA, Python, Programming Languages
WRONG OUTPUT: VBA, Python, Programming Languages, SQL, JavaScript (these weren't mentioned!)

EXAMPLE - CORRECT EXTRACTION:
Job text: "Perfect handling of MS Office, especially Excel and Access"
CORRECT OUTPUT: MS Office, Excel, Access
WRONG OUTPUT: MS Office, Excel, Access, Word, PowerPoint (these weren't mentioned!)

YOUR TASK: Read the job description and extract ONLY the technical skills, programming languages, software, and tools that are explicitly mentioned by name.

STRICT RULES:
1. ONLY extract what is directly stated in the text
2. DO NOT add typical technical skills for the role
3. DO NOT infer technologies from job responsibilities
4. Output clean names only

SKILL NAME STANDARDIZATION:
- "MS Office" → "MS Office"
- "programming languages" → "Programming Languages"
- "database systems" → "Database Systems"

JOB DESCRIPTION:
{job_description}

TECHNICAL SKILLS (one per line):"""
        response = self._call_ollama_v34(prompt)
        return self._parse_skills_precise_v34(response)
    
    def _extract_soft_skills_v34(self, job_description: str) -> List[str]:
        """Extract soft skills with precision prompts - v3.4 WORKING"""
        prompt = f"""You are a PRECISION SOFT SKILLS EXTRACTOR.

CRITICAL INSTRUCTION: Extract ONLY soft/interpersonal skills that are EXPLICITLY MENTIONED in the job description text. DO NOT add skills from your domain knowledge.

EXAMPLE - CORRECT EXTRACTION:
Job text: "Strong communication skills and ability to work with clients"
CORRECT OUTPUT: Communication, Client Relations  
WRONG OUTPUT: Communication, Client Relations, Leadership, Teamwork, Presentation (these weren't mentioned!)

EXAMPLE - CORRECT EXTRACTION:  
Job text: "Excellent written and spoken English and German"
CORRECT OUTPUT: English, German
WRONG OUTPUT: English, German, Communication, Multilingual (these weren't explicitly stated!)

YOUR TASK: Read the job description and extract ONLY the soft skills, communication abilities, languages, and interpersonal capabilities that are explicitly mentioned.

STRICT RULES:
1. ONLY extract what is directly stated in the text
2. DO NOT add typical soft skills for the role
3. DO NOT infer skills from job responsibilities  
4. Output clean names only

SKILL NAME STANDARDIZATION:
- "communication skills" → "Communication"
- "client relationship management" → "Client Relationship Management"  
- "written and spoken English" → "English"
- "sales and business development" → "Sales"

JOB DESCRIPTION:
{job_description}

SOFT SKILLS (one per line):"""
        response = self._call_ollama_v34(prompt)
        return self._parse_skills_precise_v34(response)
    
    def _extract_business_skills_v34(self, job_description: str) -> List[str]:
        """Extract business domain skills with precision prompts - v3.4 WORKING"""
        prompt = f"""You are a PRECISION BUSINESS DOMAIN EXTRACTOR.

CRITICAL INSTRUCTION: Extract ONLY business domain knowledge and industry expertise that is EXPLICITLY MENTIONED in the job description text. DO NOT add domain knowledge.

EXAMPLE - CORRECT EXTRACTION:
Job text: "Experience in investment accounting and risk analysis for FX products"
CORRECT OUTPUT: Investment Accounting, Risk Analysis, FX Trading
WRONG OUTPUT: Investment Accounting, Risk Analysis, FX Trading, Derivatives, Performance Measurement (these weren't mentioned!)

EXAMPLE - CORRECT EXTRACTION:
Job text: "Knowledge of vulnerability management and penetration testing methodologies"  
CORRECT OUTPUT: Vulnerability Management, Penetration Testing
WRONG OUTPUT: Vulnerability Management, Penetration Testing, Cybersecurity, Information Security (these weren't explicitly stated!)

YOUR TASK: Read the job description and extract ONLY the business domain knowledge, industry expertise, and specialized methodologies that are explicitly mentioned by name.

STRICT RULES:
1. ONLY extract what is directly named in the text
2. DO NOT add typical domain knowledge for the industry
3. DO NOT infer expertise from job title or responsibilities
4. Output clean names only

SKILL NAME STANDARDIZATION:
- "risk management" → "Risk Management"  
- "quantitative analysis" → "Quantitative Analysis"
- "hedge accounting concepts" → "Hedge Accounting"
- "financial markets" → "Financial Markets"

JOB DESCRIPTION:
{job_description}

BUSINESS DOMAIN SKILLS (one per line):"""
        response = self._call_ollama_v34(prompt)
        return self._parse_skills_precise_v34(response)
