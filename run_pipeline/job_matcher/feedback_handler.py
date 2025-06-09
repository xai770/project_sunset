#!/usr/bin/env python3
"""
Feedback Handler module for job matching.

This module handles the processing of user feedback and integrates with the
existing feedback processing system.
"""
import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import local modulesmd
# from run_pipeline.job_matcher.prompt_adapter import get_formatted_prompt
from run_pipeline.utils.prompt_manager import add_prompt_version

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('feedback_handler')

# LLM Factory Integration for Feedback Analysis
try:
    import sys
    sys.path.insert(0, '/home/xai/Documents/llm_factory')
    from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
    from llm_factory.core.types import ModuleConfig
    from llm_factory.core.ollama_client import OllamaClient
    LLM_FACTORY_AVAILABLE = True
    logger.info("✅ LLM Factory integration available for feedback analysis")
except ImportError as e:
    logger.warning(f"⚠️ LLM Factory not available, falling back to basic implementation: {e}")
    from run_pipeline.utils.llm_client import call_ollama_api
    LLM_FACTORY_AVAILABLE = False

# Define constants
FEEDBACK_DIR = PROJECT_ROOT / "data" / "feedback"
PROMPT_CATEGORY = "job_matching"
PROMPT_NAME = "llama3_cv_match"
FEEDBACK_ANALYSIS_MODEL = "llama3.2:latest"

def ensure_feedback_dir() -> Path:
    """
    Ensure the feedback directory exists.
    
    Returns:
        Path to the feedback directory
    """
    os.makedirs(FEEDBACK_DIR, exist_ok=True)
    return FEEDBACK_DIR

def save_feedback(job_id: str, match_level: str, domain_assessment: str, 
                 feedback_text: str, feedback_source: str = "user") -> bool:
    """
    Save feedback for a job match to a JSON file.
    
    Args:
        job_id: The ID of the job
        match_level: The match level (Low, Moderate, Good)
        domain_assessment: The domain assessment from the job match
        feedback_text: The feedback text from the user
        feedback_source: Source of the feedback (default: "user")
        
    Returns:
        True if feedback was successfully saved, False otherwise
    """
    try:
        feedback_dir = ensure_feedback_dir()
        feedback_file = feedback_dir / f"feedback_{job_id}.json"
        
        timestamp = Path.stat(feedback_file).st_mtime if feedback_file.exists() else None
        
        feedback_data = {
            "job_id": job_id,
            "match_level": match_level,
            "domain_assessment": domain_assessment,
            "feedback_text": feedback_text,
            "source": feedback_source,
            "timestamp": timestamp
        }
        
        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump(feedback_data, f, indent=2)
        
        logger.info(f"Saved feedback for job {job_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving feedback for job {job_id}: {e}")
        return False

def analyze_feedback(job_id: str, match_level: str, domain_assessment: str, 
                    feedback_text: str) -> Dict[str, Any]:
    """
    Analyze feedback using LLM to generate recommendations.
    
    Args:
        job_id: The ID of the job
        match_level: The match level (Low, Moderate, Good)
        domain_assessment: The domain assessment from the job match
        feedback_text: The feedback text from the user
        
    Returns:
        A dictionary with analysis results and recommendations
    """
    try:
        # Try to load job data
        from run_pipeline.job_matcher.job_processor import load_job_data
        try:
            job_data = load_job_data(job_id)
            job_title = job_data.get("job_title", "Unknown")
            job_description = job_data.get("description", "Unknown")
        except Exception:
            job_title = "Unknown"
            job_description = "Not available"
        
        # Create a prompt for feedback analysis
        analysis_prompt = f"""
You are an expert job application assistant helping to improve a job matching system.
You have been given:
1. Information about a job match that received user feedback
2. The user's feedback explaining their assessment of the match
3. The match level and domain assessment that the system provided

Please analyze the feedback and provide specific recommendations to improve job matching accuracy
for similar cases in the future. Focus on:

1. What pattern might have led to any discrepancy between the system assessment and user feedback
2. How the prompt or matching logic could be adjusted
3. Specific language or criteria that should be added to the prompt

Job Information:
Job ID: {job_id}
Job Title: {job_title}
Match Level: {match_level}
Domain Assessment: {domain_assessment}

User Feedback:
{feedback_text}

Please provide your analysis and recommendations in the following format:

Analysis:
[Your analysis of the feedback and what it suggests about the system's current performance]

Recommendations:
1. [First specific recommendation]
2. [Second specific recommendation]
3. [Third specific recommendation]

Proposed Prompt Changes:
[Specific text that should be added, removed or modified in the prompt]
"""
        
        # Call the LLM for analysis using LLM Factory if available
        if LLM_FACTORY_AVAILABLE:
            analysis_response = _analyze_feedback_with_llm_factory(analysis_prompt)
        else:
            analysis_response = call_ollama_api(
                analysis_prompt, 
                model=FEEDBACK_ANALYSIS_MODEL,
                temperature=0.7
            )
        
        # Extract parts from the response
        analysis_section = None
        recommendations_section = None
        prompt_changes_section = None
        
        sections = analysis_response.split("\n\n")
        current_section = None
        
        for section in sections:
            if "Analysis:" in section:
                analysis_section = section.replace("Analysis:", "").strip()
                current_section = "analysis"
            elif "Recommendations:" in section:
                recommendations_section = section.replace("Recommendations:", "").strip()
                current_section = "recommendations"
            elif "Proposed Prompt Changes:" in section:
                prompt_changes_section = section.replace("Proposed Prompt Changes:", "").strip()
                current_section = "prompt_changes"
            elif current_section:
                if current_section == "analysis" and analysis_section is not None:
                    analysis_section += "\n" + section.strip()
                elif current_section == "recommendations" and recommendations_section is not None:
                    recommendations_section += "\n" + section.strip()
                elif current_section == "prompt_changes" and prompt_changes_section is not None:
                    prompt_changes_section += "\n" + section.strip()
        
        # Return structured results
        return {
            "job_id": job_id,
            "match_level": match_level,
            "feedback": feedback_text,
            "analysis": analysis_section or "No analysis provided",
            "recommendations": recommendations_section or "No recommendations provided",
            "prompt_changes": prompt_changes_section or "No prompt changes proposed"
        }
    except Exception as e:
        logger.error(f"Error analyzing feedback for job {job_id}: {e}")
        return {
            "job_id": job_id,
            "error": str(e)
        }

def update_prompt_based_on_feedback(feedback_analysis: Dict[str, Any], 
                                   auto_update: bool = False) -> Optional[str]:
    """
    Update the job matching prompt based on feedback analysis.
    
    Args:
        feedback_analysis: Results from feedback analysis
        auto_update: Whether to automatically update the prompt or just suggest changes
        
    Returns:
        New version ID if prompt was updated, otherwise None
    """
    try:
        # Get the current prompt
        from run_pipeline.job_matcher.prompt_adapter import get_formatted_prompt
        
        current_prompt = get_formatted_prompt(
            PROMPT_NAME, 
            category=PROMPT_CATEGORY,
            cv="$CV_PLACEHOLDER$",
            job="$JOB_PLACEHOLDER$"
        )
        
        prompt_changes = feedback_analysis.get("prompt_changes", "")
        if not prompt_changes or prompt_changes == "No prompt changes proposed":
            logger.info("No prompt changes proposed")
            return None
        
        if auto_update:
            # Call LLM to apply the changes to the prompt
            update_prompt = f"""
You are a prompt engineering expert. You need to update a job matching prompt based on 
feedback analysis. 

Current prompt:
```
{current_prompt}
```

Proposed changes based on feedback:
```
{prompt_changes}
```

Please provide the complete updated prompt that incorporates these changes while
maintaining the original structure and intent of the prompt.
Ensure the updated prompt still uses the placeholders $CV_PLACEHOLDER$ and $JOB_PLACEHOLDER$
which will be replaced with the actual CV and job description.

Updated prompt:
"""
            
            # Update prompt using LLM Factory if available
            if LLM_FACTORY_AVAILABLE:
                updated_prompt = _analyze_feedback_with_llm_factory(update_prompt)
            else:
                updated_prompt = call_ollama_api(
                    update_prompt, 
                    model=FEEDBACK_ANALYSIS_MODEL,
                    temperature=0.3
                )
            
            # Extract the updated prompt
            if "Updated prompt:" in updated_prompt:
                updated_prompt = updated_prompt.split("Updated prompt:")[1].strip()
            
            # Replace back the placeholders if they were modified
            updated_prompt = updated_prompt.replace("$CV_PLACEHOLDER$", "{cv}")
            updated_prompt = updated_prompt.replace("$JOB_PLACEHOLDER$", "{job}")
            
            # Save the updated prompt as a new version
            # Use the correct parameters for add_prompt_version
            new_version = str(add_prompt_version(
                PROMPT_NAME, 
                updated_prompt,
                description="Updated based on feedback analysis",
                author="FeedbackSystem",
                set_active=True
            ))
            
            logger.info(f"Updated prompt to version {new_version} based on feedback")
            return new_version
        else:
            # Just log the suggested changes
            logger.info(f"Suggested prompt changes based on feedback: {prompt_changes}")
            return None
    except Exception as e:
        logger.error(f"Error updating prompt based on feedback: {e}")
        return None

def _analyze_feedback_with_llm_factory(prompt: str) -> str:
    """
    Enhanced feedback analysis using LLM Factory with multi-layer fallback strategy.
    
    Args:
        prompt: The analysis prompt to process
        
    Returns:
        Analysis response from best available method
    """
    try:
        registry = SpecialistRegistry()
        ollama_client = OllamaClient()
        
        # Primary: Try multiple specialists for consensus
        try:
            # Method 1: Document analysis specialist
            doc_config = ModuleConfig(
                models=["llama3.2:latest"],
                conservative_bias=True,
                quality_threshold=8.0,
                ollama_client=ollama_client
            )
            
            doc_specialist = registry.load_specialist("document_analysis", doc_config)
            doc_input = {
                "text": prompt,
                "task": "feedback_analysis",
                "context": "Analyze user feedback for job matching system improvement"
            }
            
            doc_result = doc_specialist.process(doc_input)
            
            # Method 2: Text generation specialist for comparison
            text_config = ModuleConfig(
                models=["llama3.2:latest"],
                conservative_bias=True,
                quality_threshold=7.5,
                ollama_client=ollama_client
            )
            
            text_specialist = registry.load_specialist("text_generation", text_config)
            text_input = {
                "text": prompt,
                "task": "analysis",
                "context": "Generate comprehensive feedback analysis"
            }
            
            text_result = text_specialist.process(text_input)
            
            # Use the best result or combine insights
            if doc_result.success and doc_result.data.get('analysis'):
                if text_result.success and text_result.data.get('generated_text'):
                    # Both succeeded - use document analysis as primary
                    logger.info("✅ Used LLM Factory consensus feedback analysis")
                    analysis = doc_result.data['analysis']
                    # Add any additional insights from text generation
                    if len(str(text_result.data['generated_text'])) > len(str(analysis)):
                        analysis += f"\n\nAdditional insights: {text_result.data['generated_text'][:200]}..."
                    return str(analysis)
                else:
                    logger.info("✅ Used LLM Factory document analysis for feedback")
                    return str(doc_result.data['analysis'])
            elif text_result.success and text_result.data.get('generated_text'):
                logger.info("✅ Used LLM Factory text generation for feedback")
                return str(text_result.data['generated_text'])
            else:
                logger.warning("⚠️ Both LLM Factory specialists failed")
                
        except Exception as e:
            logger.warning(f"⚠️ LLM Factory multi-specialist approach failed: {e}")
        
        # Secondary: Single specialist fallback
        try:
            config = ModuleConfig(
                models=["llama3.2:latest"],
                conservative_bias=True,
                quality_threshold=7.0,
                ollama_client=ollama_client
            )
            
            specialist = registry.load_specialist("text_generation", config)
            input_data = {
                "text": prompt,
                "task": "feedback_analysis",
                "context": "Analyze feedback for system improvement"
            }
            
            result = specialist.process(input_data)
            
            if result.success and result.data.get('generated_text'):
                logger.info("✅ Used LLM Factory single specialist fallback")
                return str(result.data['generated_text'])
            else:
                logger.warning("⚠️ LLM Factory single specialist failed")
                
        except Exception as e:
            logger.warning(f"⚠️ LLM Factory single specialist failed: {e}")
        
    except Exception as e:
        logger.warning(f"⚠️ LLM Factory registry failed: {e}")
    
    # Tertiary: Enhanced client fallback (still better than direct calls)
    try:
        from run_pipeline.utils.llm_client_enhanced import call_ollama_api
        logger.info("🔄 Using enhanced client fallback for feedback analysis")
        return call_ollama_api(prompt, model=FEEDBACK_ANALYSIS_MODEL, temperature=0.7)
    except Exception as e:
        logger.warning(f"⚠️ Enhanced client fallback failed: {e}")
    
    # Final: Direct client (existing behavior)
    try:
        from run_pipeline.utils.llm_client import call_ollama_api
        logger.info("🔄 Using direct client fallback for feedback analysis")
        return call_ollama_api(prompt, model=FEEDBACK_ANALYSIS_MODEL, temperature=0.7)
    except Exception as e:
        logger.error(f"❌ All feedback analysis methods failed: {e}")
        return f"Error: Unable to analyze feedback - {str(e)}"
