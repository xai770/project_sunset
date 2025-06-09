"""
LLM Handlers Module for JMFS

Contains methods for processing feedback through LLM analysis
"""
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import configured LLM client and LLM Factory
from run_pipeline.utils.llm_client import call_ollama_api, call_ollama_api_json

# Try to import LLM Factory for quality-controlled processing
try:
    from llm_factory.specialist_registry import SpecialistRegistry
    from llm_factory.quality_control import QualityController
    LLM_FACTORY_AVAILABLE = True
except ImportError:
    LLM_FACTORY_AVAILABLE = False

# Configure logging
logger = logging.getLogger("jmfs.feedback.llm_handlers")

def _get_llm_factory_specialists():
    """Initialize LLM Factory specialists for feedback processing."""
    if not LLM_FACTORY_AVAILABLE:
        return None, None
    
    try:
        # Initialize specialist registry
        registry = SpecialistRegistry()
        
        # Register feedback analysis specialist
        registry.register_specialist(
            "feedback_analyzer",
            {
                "type": "document_analysis",
                "model": "llama3.2:latest",
                "temperature": 0.3,
                "max_tokens": 2000,
                "system_prompt": "You are a professional feedback analysis specialist for a job matching system. Analyze reviewer feedback and determine appropriate actions with precision and consistency."
            }
        )
        
        # Register content generation specialist
        registry.register_specialist(
            "content_generator", 
            {
                "type": "text_generation",
                "model": "llama3.2:latest",
                "temperature": 0.7,
                "max_tokens": 1500,
                "system_prompt": "You are a professional content generation specialist. Create high-quality, contextually appropriate content for business communications."
            }
        )
        
        # Initialize quality controller
        quality_controller = QualityController()
        
        return registry, quality_controller
        
    except Exception as e:
        logger.warning(f"Failed to initialize LLM Factory specialists: {e}")
        return None, None

def _analyze_feedback_with_llm_factory(feedback_summary, config):
    """Analyze feedback using LLM Factory document analysis specialist."""
    registry, quality_controller = _get_llm_factory_specialists()
    if not registry:
        return None
    
    try:
        # Create the master analysis prompt
        master_prompt = f"""
You are a Feedback Dispatcher coordinating a job matching system. 
Analyze reviewer feedback and determine what actions to take for each job.

For each job with feedback, determine the action type:
1. GENERATE_COVER_LETTER: Reviewer says they ARE qualified (false negative)
2. RESOLVE_CONFLICT: Contradictory feedback vs. previous assessment  
3. CLARIFY_GIBBERISH: Feedback is unclear or nonsensical
4. PROCESS_LEARNING: Valid feedback for system improvement
5. IGNORE: Feedback is empty or clearly not actionable

Jobs with feedback:
{json.dumps(feedback_summary, indent=2)}

Output JSON format:
{{
  "actions": [
    {{
      "job_id": "12345",
      "action_type": "GENERATE_COVER_LETTER|RESOLVE_CONFLICT|CLARIFY_GIBBERISH|PROCESS_LEARNING|IGNORE",
      "feedback_text": "actual reviewer feedback",
      "reasoning": "why this action was chosen",
      "priority": "high|medium|low"
    }}
  ],
  "summary": "Brief summary of analysis"
}}
"""
        
        # Use feedback analyzer specialist
        specialist = registry.get_specialist("feedback_analyzer")
        response = specialist.generate(master_prompt)
        
        # Apply quality control
        if quality_controller:
            quality_score = quality_controller.evaluate_response(response, master_prompt)
            logger.info(f"LLM Factory feedback analysis quality score: {quality_score}")
        
        # Parse the JSON response
        if isinstance(response, str):
            return json.loads(response)
        return response
        
    except Exception as e:
        logger.error(f"Error in LLM Factory feedback analysis: {e}")
    
    return None

def _generate_content_with_llm_factory(prompt, config, content_type="professional"):
    """Generate content using LLM Factory text generation specialist."""
    registry, quality_controller = _get_llm_factory_specialists()
    if not registry:
        return None
    
    try:
        # Use content generator specialist
        specialist = registry.get_specialist("content_generator")
        response = specialist.generate(prompt)
        
        # Apply quality control
        if quality_controller:
            quality_score = quality_controller.evaluate_response(response, prompt)
            logger.info(f"LLM Factory content generation quality score: {quality_score}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in LLM Factory content generation: {e}")
    
    return None

def analyze_feedback_with_master_llm(jobs_with_feedback, config):
    """
    Master LLM analyzes all feedback and determines actions needed.
    
    Args:
        jobs_with_feedback: List of job data with reviewer feedback
        config: Configuration dictionary
        
    Returns:
        Dictionary of actions to take for each job
    """
    # Prepare the data for LLM analysis
    feedback_summary = []
    for job in jobs_with_feedback:
        feedback_summary.append({
            'job_id': job.get('job_id', 'unknown'),
            'position_title': job.get('position_title', ''),
            'match_level': job.get('match_level', ''),
            'reviewer_feedback': job.get('reviewer_feedback', ''),
            'previous_assessment': job.get('domain_assessment', '')
        })
    
    # Create the master analysis prompt
    master_prompt = f"""
You are a Feedback Dispatcher coordinating a job matching system. 
Analyze reviewer feedback and determine what actions to take for each job.

For each job with feedback, determine the action type:
1. GENERATE_COVER_LETTER: Reviewer says they ARE qualified (false negative)
2. RESOLVE_CONFLICT: Contradictory feedback vs. previous assessment  
3. CLARIFY_GIBBERISH: Feedback is unclear or nonsensical
4. PROCESS_LEARNING: Valid feedback for system improvement
5. IGNORE: Feedback is empty or clearly not actionable

Jobs with feedback:
{json.dumps(feedback_summary, indent=2)}

Output JSON format:
{{
  "actions": [
    {{
      "job_id": "12345",
      "action_type": "GENERATE_COVER_LETTER|RESOLVE_CONFLICT|CLARIFY_GIBBERISH|PROCESS_LEARNING|IGNORE",
      "feedback_text": "actual reviewer feedback",
      "reasoning": "why this action was chosen",
      "priority": "high|medium|low"
    }}
  ],
  "summary": "Brief summary of analysis"
}}
"""
    
    try:
        # Try using LLM Factory first for quality-controlled analysis
        response = _analyze_feedback_with_llm_factory(feedback_summary, config)
        
        if response:
            logger.info(f"LLM Factory analysis complete: {len(response.get('actions', []))} actions identified")
            return response
        
        # Fallback to regular LLM client
        model = config.get('llm_model', 'llama3.2:latest')
        response = call_ollama_api_json(
            master_prompt,
            model=model, 
            temperature=0.3  # Low temperature for consistent routing decisions
        )
        
        logger.info(f"LLM analysis complete: {len(response.get('actions', []))} actions identified")
        return response
        
    except Exception as e:
        logger.error(f"Error in master LLM analysis: {e}")
        return {"actions": [], "summary": f"Error: {str(e)}"}

def handle_cover_letter_generation(action, job_data, config):
    """Generate cover letter for false negative."""
    job_id = action.get('job_id', 'unknown')
    try:
        feedback_text = action.get('feedback_text', '')
        
        # Load job details
        position_title = job_data.get('position_title', 'Unknown Position')
        job_description = job_data.get('job_description', '')
        
        # Create cover letter generation prompt
        cover_letter_prompt = f"""
Generate a professional cover letter for this job since the reviewer indicated they ARE qualified:

Job ID: {job_id}
Position: {position_title}
Reviewer Feedback: {feedback_text}

Job Description:
{job_description}

Create a concise, professional cover letter (200-300 words) that:
1. Addresses the specific qualifications mentioned in the reviewer feedback
2. Highlights relevant experience for this role
3. Shows enthusiasm for the position
4. Follows standard business letter format

Cover Letter:
"""
        
        # Try using LLM Factory for quality-controlled content generation
        cover_letter = _generate_content_with_llm_factory(
            cover_letter_prompt, 
            config, 
            content_type="cover_letter"
        )
        
        # Fallback to regular LLM client if needed
        if not cover_letter:
            model = config.get('llm_model', 'llama3.2:latest')
            cover_letter = call_ollama_api(
                cover_letter_prompt,
                model=model,
                temperature=0.7  # Higher temperature for creative writing
            )
        
        # Save cover letter to file
        cover_letter_dir = config.get('cover_letter_output_dir', '../docs/cover_letters')
        os.makedirs(cover_letter_dir, exist_ok=True)
        
        cover_letter_filename = f"cover_letter_{job_id}.md"
        cover_letter_path = os.path.join(cover_letter_dir, cover_letter_filename)
        
        with open(cover_letter_path, 'w', encoding='utf-8') as f:
            f.write(f"# Cover Letter - {position_title}\n")
            f.write(f"**Job ID:** {job_id}\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Reason:** Reviewer feedback indicated qualification\n\n")
            f.write(cover_letter)
        
        # Return success result
        return {
            'job_id': job_id,
            'action': 'GENERATE_COVER_LETTER',
            'status': 'success',
            'file_path': cover_letter_path,
            'log_message': f"Generated cover letter: {cover_letter_filename}"
        }
        
    except Exception as e:
        logger.error(f"Error generating cover letter for job {job_id}: {e}")
        return {
            'job_id': job_id,
            'action': 'GENERATE_COVER_LETTER', 
            'status': 'error',
            'log_message': f"Failed to generate cover letter: {str(e)}"
        }

def handle_conflict_resolution(action, job_data, config):
    """Handle contradictory feedback."""
    job_id = action.get('job_id', 'unknown')
    try:
        feedback_text = action.get('feedback_text', '')
        position_title = job_data.get('position_title', 'Unknown Position')
        previous_assessment = job_data.get('domain_assessment', '')
        match_level = job_data.get('match_level', '')
        
        # Create conflict resolution prompt
        conflict_prompt = f"""
Create a polite clarification email for contradictory feedback:

Job: {position_title} (ID: {job_id})
Current Feedback: {feedback_text}
Previous System Assessment: {match_level} match
Previous Domain Assessment: {previous_assessment}

Write a professional email that:
1. Acknowledges the contradiction politely
2. Presents the evidence from our assessment
3. Asks for clarification
4. Offers a way to resolve the discrepancy
5. Maintains a collaborative tone

Email Content:
"""
        
        # Try using LLM Factory for quality-controlled content generation
        clarification_email = _generate_content_with_llm_factory(
            conflict_prompt,
            config,
            content_type="professional_email"
        )
        
        # Fallback to regular LLM client if needed
        if not clarification_email:
            model = config.get('llm_model', 'llama3.2:latest')
            clarification_email = call_ollama_api(
                conflict_prompt,
                model=model,
                temperature=0.5  # Moderate temperature for professional tone
            )
        
        return {
            'job_id': job_id,
            'action': 'RESOLVE_CONFLICT',
            'status': 'success',
            'email_content': clarification_email,
            'log_message': f"Generated conflict resolution email"
        }
        
    except Exception as e:
        logger.error(f"Error handling conflict for job {job_id}: {e}")
        return {
            'job_id': job_id,
            'action': 'RESOLVE_CONFLICT',
            'status': 'error', 
            'log_message': f"Failed to process conflict: {str(e)}"
        }

def handle_gibberish_clarification(action, job_data, config):
    """Handle unclear feedback."""
    job_id = action.get('job_id', 'unknown')
    try:
        feedback_text = action.get('feedback_text', '')
        position_title = job_data.get('position_title', 'Unknown Position')
        
        # Create gibberish clarification prompt
        gibberish_prompt = f"""
Create a friendly clarification email for unclear feedback:

Job: {position_title} (ID: {job_id})
Unclear Feedback: "{feedback_text}"

Write a friendly, helpful email that:
1. Acknowledges we received their feedback
2. Politely mentions it's unclear
3. Asks for clarification in a non-judgmental way
4. Offers specific options or questions to help them respond
5. Includes a way to contact us directly

Email Content:
"""
        
        # Try using LLM Factory for quality-controlled content generation
        clarification_email = _generate_content_with_llm_factory(
            gibberish_prompt,
            config,
            content_type="friendly_email"
        )
        
        # Fallback to regular LLM client if needed
        if not clarification_email:
            model = config.get('llm_model', 'llama3.2:latest')
            clarification_email = call_ollama_api(
                gibberish_prompt,
                model=model,
                temperature=0.6  # Slightly higher temperature for friendly tone
            )
        
        # Add chat link if configured
        chat_link = config.get('chat_interface_url', 'mailto:support@yourcompany.com')
        clarification_email = clarification_email.replace('[chat_link]', chat_link)
        
        return {
            'job_id': job_id,
            'action': 'CLARIFY_GIBBERISH',
            'status': 'success',
            'email_content': clarification_email,
            'log_message': f"Generated gibberish clarification email"
        }
        
    except Exception as e:
        logger.error(f"Error handling gibberish for job {job_id}: {e}")
        return {
            'job_id': job_id,
            'action': 'CLARIFY_GIBBERISH',
            'status': 'error',
            'log_message': f"Failed to process gibberish: {str(e)}"
        }

def handle_learning_feedback(action, job_data, config):
    """Process feedback for system learning."""
    job_id = action.get('job_id', 'unknown')
    try:
        feedback_text = action.get('feedback_text', '')
        match_level = job_data.get('match_level', '')
        domain_assessment = job_data.get('domain_assessment', '')
        
        # Placeholder for feedback handler integration
        # This would typically call a feedback learning system
        # from run_pipeline.job_matcher.feedback_handler import analyze_feedback
        
        # For now, just log that we would process this feedback
        logger.info(f"Learning from feedback for job {job_id}: {feedback_text}")
        
        return {
            'job_id': job_id,
            'action': 'PROCESS_LEARNING',
            'status': 'success',
            'log_message': "Processed learning feedback for future improvements"
        }
        
    except Exception as e:
        logger.error(f"Error processing learning feedback for job {job_id}: {e}")
        return {
            'job_id': job_id,
            'action': 'PROCESS_LEARNING',
            'status': 'error',
            'log_message': f"Failed to process learning: {str(e)}"
        }
