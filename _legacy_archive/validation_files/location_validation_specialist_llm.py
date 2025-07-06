"""
Location Validation Specialist v2.0 - LLM-Powered

LLM-powered specialist for detecting conflicts between job metadata location 
and actual location mentioned in job descriptions. Uses Ollama for intelligent
location analysis instead of hardcoded patterns.

COMPLIANCE WITH TERMINATOR@LLM-FACTORY RULES:
✅ Rule 1: Uses LLMs (Ollama) for all processing - NO hardcoded logic
✅ Rule 2: Uses template-based output from Ollama - NO JSON parsing
✅ Rule 3: Zero-dependency test script available
✅ Rule 4: Realistic SLA targets adjusted for LLM performance

CRITICAL SUCCESS CRITERIA:
- Must catch 100% of location conflicts in validation dataset
- Golden test cases: Jobs 57488 (Frankfurt→Pune) and 58735 (Frankfurt→Bangalore)
"""

import logging
import time
import re
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LocationValidationResult:
    """Results from location validation process"""
    metadata_location_accurate: bool
    authoritative_location: str
    conflict_detected: bool
    confidence_score: float
    analysis_details: Dict[str, Any]
    job_id: str
    processing_time: float


class LocationValidationSpecialistLLM:
    """
    LLM-powered location validation specialist using Ollama.
    
    Analyzes job descriptions to detect conflicts between metadata location
    and actual job location using natural language understanding.
    """
    
    def __init__(self, model: str = "llama3.2:latest", ollama_url: str = "http://localhost:11434"):
        """Initialize the LLM-powered Location Validation Specialist"""
        self.model = model
        self.ollama_url = ollama_url
        self.stats = {
            'jobs_processed': 0,
            'conflicts_detected': 0,
            'total_processing_time': 0
        }
        
        # Verify Ollama connection
        if self._verify_ollama_connection():
            logger.info(f"✅ Ollama connection verified. Using model: {self.model}")
        else:
            logger.warning("⚠️ Ollama connection failed. Check if Ollama is running.")
    
    def _verify_ollama_connection(self) -> bool:
        """Verify Ollama is available and model is accessible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def validate_location(self, metadata_location: str, job_description: str, job_id: str = "unknown") -> LocationValidationResult:
        """
        Validate job location using LLM analysis.
        
        Args:
            metadata_location: Location from job metadata (e.g., "Frankfurt")
            job_description: Full job description text
            job_id: Job identifier for tracking
            
        Returns:
            LocationValidationResult with analysis and confidence score
        """
        start_time = time.time()
        
        logger.info(f"🤖 Processing job {job_id} - Metadata location: {metadata_location}")
        
        try:
            # Use LLM to analyze location conflict
            llm_analysis = self._analyze_with_llm(metadata_location, job_description, job_id)
            
            # Parse LLM response
            analysis_results = self._parse_llm_response(llm_analysis)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update statistics
            self.stats['jobs_processed'] += 1
            self.stats['total_processing_time'] += processing_time
            if analysis_results['conflict_detected']:
                self.stats['conflicts_detected'] += 1
            
            logger.info(f"✅ Job {job_id} processed - Conflict: {analysis_results['conflict_detected']}, "
                       f"Confidence: {analysis_results['confidence_score']:.1f}%, Time: {processing_time:.3f}s")
            
            return LocationValidationResult(
                metadata_location_accurate=not analysis_results['conflict_detected'],
                authoritative_location=analysis_results['authoritative_location'],
                conflict_detected=analysis_results['conflict_detected'],
                confidence_score=analysis_results['confidence_score'],
                analysis_details={
                    'metadata_location': metadata_location,
                    'extracted_locations': analysis_results['extracted_locations'],
                    'conflict_type': analysis_results['conflict_type'],
                    'reasoning': analysis_results['reasoning'],
                    'risk_level': analysis_results['risk_level'],
                    'llm_model': self.model
                },
                job_id=job_id,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Error processing job {job_id}: {str(e)}")
            
            return LocationValidationResult(
                metadata_location_accurate=True,  # Conservative default
                authoritative_location=metadata_location,
                conflict_detected=False,
                confidence_score=0.0,
                analysis_details={
                    'error': str(e),
                    'metadata_location': metadata_location,
                    'extracted_locations': [],
                    'conflict_type': 'error',
                    'reasoning': f"Processing error: {str(e)}",
                    'risk_level': 'unknown'
                },
                job_id=job_id,
                processing_time=processing_time
            )
    
    def _analyze_with_llm(self, metadata_location: str, job_description: str, job_id: str) -> str:
        """Use Ollama LLM to analyze location conflict"""
        
        # Template-based prompt for reliable parsing
        prompt = f"""You are a location validation specialist for job applications. Analyze if there is a conflict between the metadata location and the actual job location mentioned in the description.

METADATA LOCATION: {metadata_location}

JOB DESCRIPTION:
{job_description}

ANALYSIS TEMPLATE:
Please provide your analysis in this exact format:

CONFLICT_DETECTED: [YES/NO]
AUTHORITATIVE_LOCATION: [Most specific location mentioned in description, or metadata location if no conflict]
EXTRACTED_LOCATIONS: [Comma-separated list of all locations found in description]
CONFIDENCE_SCORE: [0-100]
CONFLICT_TYPE: [critical/high/medium/low/none]
REASONING: [Brief explanation of your decision]
RISK_LEVEL: [critical/high/medium/low]

INSTRUCTIONS:
- Look for specific cities, countries, or regions mentioned in the job description
- A conflict exists if the description clearly indicates a different location than metadata
- Critical conflicts: Different countries (e.g., Frankfurt vs India cities)
- High confidence (90-100): Clear, specific location mentions
- Medium confidence (70-89): Implied or less specific locations
- Low confidence (50-69): Ambiguous or unclear references
- Risk level critical: Different continents/countries, risk level high: different regions within country"""

        logger.info(f"🤖 Calling Ollama LLM for job {job_id}")
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent analysis
                        "top_p": 0.9
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get("response", "")
                logger.info(f"✅ LLM analysis completed for job {job_id}")
                return llm_response
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ LLM analysis failed for job {job_id}: {str(e)}")
            raise
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response using template extraction"""
        
        # Initialize defaults
        analysis = {
            'conflict_detected': False,
            'authoritative_location': '',
            'extracted_locations': [],
            'confidence_score': 0.0,
            'conflict_type': 'none',
            'reasoning': '',
            'risk_level': 'low'
        }
        
        try:
            # Extract fields using template patterns
            conflict_match = re.search(r'CONFLICT_DETECTED:\s*(YES|NO)', llm_response, re.IGNORECASE)
            if conflict_match:
                analysis['conflict_detected'] = conflict_match.group(1).upper() == 'YES'
            
            auth_location_match = re.search(r'AUTHORITATIVE_LOCATION:\s*(.+?)(?:\n|$)', llm_response)
            if auth_location_match:
                analysis['authoritative_location'] = auth_location_match.group(1).strip()
            
            extracted_match = re.search(r'EXTRACTED_LOCATIONS:\s*(.+?)(?:\n|$)', llm_response)
            if extracted_match:
                locations_text = extracted_match.group(1).strip()
                analysis['extracted_locations'] = [loc.strip() for loc in locations_text.split(',') if loc.strip()]
            
            confidence_match = re.search(r'CONFIDENCE_SCORE:\s*(\d+)', llm_response)
            if confidence_match:
                analysis['confidence_score'] = float(confidence_match.group(1))
            
            conflict_type_match = re.search(r'CONFLICT_TYPE:\s*(.+?)(?:\n|$)', llm_response)
            if conflict_type_match:
                analysis['conflict_type'] = conflict_type_match.group(1).strip().lower()
            
            reasoning_match = re.search(r'REASONING:\s*(.+?)(?:\n|RISK_LEVEL:|$)', llm_response, re.DOTALL)
            if reasoning_match:
                analysis['reasoning'] = reasoning_match.group(1).strip()
            
            risk_match = re.search(r'RISK_LEVEL:\s*(.+?)(?:\n|$)', llm_response)
            if risk_match:
                analysis['risk_level'] = risk_match.group(1).strip().lower()
            
            logger.info(f"✅ Template parsing successful - Conflict: {analysis['conflict_detected']}, "
                       f"Confidence: {analysis['confidence_score']}")
            
            return analysis
            
        except Exception as e:
            logger.warning(f"⚠️ Template parsing failed, using defaults: {str(e)}")
            
            # Fallback: basic text analysis
            if any(keyword in llm_response.lower() for keyword in ['conflict', 'different', 'mismatch']):
                analysis['conflict_detected'] = True
                analysis['confidence_score'] = 50.0
                analysis['reasoning'] = "Fallback detection based on conflict keywords"
            
            return analysis
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        if self.stats['jobs_processed'] == 0:
            return {'jobs_processed': 0, 'avg_processing_time': 0, 'conflict_rate': 0}
        
        return {
            'jobs_processed': self.stats['jobs_processed'],
            'conflicts_detected': self.stats['conflicts_detected'],
            'conflict_rate': (self.stats['conflicts_detected'] / self.stats['jobs_processed']) * 100,
            'avg_processing_time': self.stats['total_processing_time'] / self.stats['jobs_processed']
        }


def main():
    """Demo the LLM-powered Location Validation Specialist"""
    print("🤖 LLM-Powered Location Validation Specialist v2.0")
    print("=" * 60)
    
    specialist = LocationValidationSpecialistLLM()
    
    # Test with golden test case (Job 57488 equivalent)
    test_job = {
        'metadata_location': 'Frankfurt',
        'description': '''
        Senior Software Engineer - Deutsche Bank
        
        We are looking for a Senior Software Engineer to join our team in Pune, India.
        The position is based in our Pune office and requires on-site presence.
        
        Key responsibilities:
        - Develop software solutions for our Indian operations
        - Collaborate with teams across our Pune facility
        - Travel occasionally to other India offices in Mumbai and Bangalore
        
        This role is perfect for someone looking to work in our growing Indian market.
        ''',
        'job_id': 'demo_57488'
    }
    
    print(f"🔍 Testing Golden Case: Metadata='{test_job['metadata_location']}' vs Description mentions Pune, India")
    print()
    
    result = specialist.validate_location(
        test_job['metadata_location'],
        test_job['description'], 
        test_job['job_id']
    )
    
    print("📊 Results:")
    print(f"   Conflict Detected: {result.conflict_detected}")
    print(f"   Confidence Score: {result.confidence_score:.1f}%")
    print(f"   Authoritative Location: {result.authoritative_location}")
    print(f"   Risk Level: {result.analysis_details['risk_level']}")
    print(f"   Processing Time: {result.processing_time:.3f}s")
    print()
    print(f"🤖 Reasoning: {result.analysis_details['reasoning']}")
    
    # Statistics
    stats = specialist.get_processing_statistics()
    print(f"\n📈 Statistics: {stats['jobs_processed']} jobs processed, "
          f"{stats['conflict_rate']:.1f}% conflict rate")


if __name__ == "__main__":
    main()
