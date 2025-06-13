"""
Module to generate job match percentage and cover letter using Ollama's phi3 LLM.
"""
from run_pipeline.utils.llm_client import call_ollama_api
import logging
import re

logger = logging.getLogger("phi3_match_and_cover")

PROMPT_TEMPLATE = '''You are an expert job application assistant. Given the following candidate CV and job description, provide:
- You must always start your response with a line in the format: Match Percentage: XX% (where XX is a number from 0 to 100).
- If you cannot determine a match, output: Match Percentage: 50%.
- A concise, professional cover letter for the candidate to use. Do NOT mention the match percentage in the cover letter itself.

CV:
{cv}

Job Description:
{job}

Respond in the following format:
Match Percentage: <number>%\nCover Letter:\n<cover letter text>
'''

def get_match_and_cover_letter(cv: str, job_description: str) -> dict:
    """
    Use phi3 LLM to get match percentage and cover letter for a job application.
    Returns a dict with 'match_percentage' and 'cover_letter'.
    """
    prompt = PROMPT_TEMPLATE.format(cv=cv, job=job_description)
    logger.info(f"Sending prompt to phi3, prompt length: {len(prompt)} characters")
    
    response = call_ollama_api(prompt, model="phi3")
    logger.info(f"Received response from phi3, length: {len(response)} characters")
    logger.info(f"Response starts with: {response[:100]}...")
     # Parse response
    match = None
    cover = None
    
    # Save the full response for debugging
    logger.debug(f"Full response from phi3:\n{response}")
    
    # Try to extract match percentage from several possible formats
    match_patterns = [
        r"match percentage\s*[:\-]?\s*(\d{1,3})%",  # Match Percentage: 85%
        r"match\s*[:\-]?\s*(\d{1,3})%",            # Match: 85%
        r"fit\s*[:\-]?\s*(\d{1,3})%",              # Fit: 85%
        r"(\d{1,3})%\s+match",                      # 85% match
        r"^\s*(\d{1,3})%\s*$",                     # 85% (on its own line)
        r"(\d{1,3})%"                                # any number followed by %
    ]
    for pat in match_patterns:
        match_match = re.search(pat, response, re.IGNORECASE | re.MULTILINE)
        if match_match:
            match = int(match_match.group(1))
            logger.info(f"Found match percentage in response: {match}% (pattern: {pat})")
            break
    if match is None:
        logger.warning("No match percentage found in response! Using fallback value 50%.")
        match = 50
    
    # Look for cover letter after the match percentage or "Cover Letter:" marker
    cover_match = re.search(r"cover letter\s*[:\-]?\s*\n?(.*)", response, re.IGNORECASE | re.DOTALL)
    if cover_match:
        cover = cover_match.group(1).strip()
        logger.info(f"Found cover letter, starting with: {cover[:50]}...")
    else:
        # Alternative: look for match percentage line, then take everything after that
        if match is not None:
            parts = re.split(r"^.*?(\d{1,3})%.*$", response, maxsplit=1, flags=re.MULTILINE)
            if len(parts) > 1:
                cover = parts[-1].strip()
                logger.info(f"Found cover letter after match %, starting with: {cover[:50]}...")
        
        # Last resort: take everything after the first blank line
        if not cover:
            parts = response.split("\n\n", 1)
            if len(parts) > 1:
                cover = parts[1].strip()
                logger.info(f"Found cover letter after blank line, starting with: {cover[:50]}...")
            else:
                cover = response.strip()
            parts = response.split("\n\n", 1)
            if len(parts) > 1:
                cover = parts[1].strip()
                logger.info(f"Found cover letter after blank line, starting with: {cover[:50]}...")
            else:
                cover = response.strip()
                logger.info(f"Using full response as cover letter, starting with: {cover[:50]}...")
    
    # If cover is still None or empty, use a default message
    if not cover or len(cover.strip()) < 50:  # Ensure at least 50 chars of meaningful content
        logger.warning("Cover letter content is too short or missing, using fallback")
        cover = "Unable to generate a proper cover letter. Please try again or adjust the job description."
    
    # Clean up the cover letter - remove any markdown formatting or extra markup
    cover = re.sub(r'```.*?```', '', cover, flags=re.DOTALL)  # Remove code blocks
    cover = re.sub(r'#+ ', '', cover)  # Remove markdown headers
    cover = re.sub(r'\*\*(.*?)\*\*', r'\1', cover)  # Remove bold formatting
    cover = re.sub(r'\*(.*?)\*', r'\1', cover)  # Remove italic formatting
    
    # Remove any instructions or format markers that leaked into the cover letter
    cover = re.sub(r'^.*?cover letter:?\s*', '', cover, flags=re.IGNORECASE)
    
    return {"match_percentage": match, "cover_letter": cover}
