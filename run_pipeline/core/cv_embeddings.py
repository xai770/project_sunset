#!/usr/bin/env python3
"""
Module for creating and managing CV embeddings to improve efficiency of job matching.
Uses sentence_transformers library with fallback options.
"""

import os
import json
import logging
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# Configure logger
logger = logging.getLogger("cv_embeddings")

# Path to CV data
CV_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "profile",
    "cv",
    "combined-cv-json.json"
)

# Path to save embeddings
EMBEDDINGS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
    "data", 
    "cv_embeddings"
)

# Create embeddings directory if it doesn't exist
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

def get_embedding_model():
    """
    Get the sentence transformer model for generating embeddings.
    Returns None if the required libraries are not installed.
    """
    try:
        from sentence_transformers import SentenceTransformer
        # Use a good general-purpose model
        return SentenceTransformer("all-MiniLM-L6-v2")
    except ImportError:
        logger.warning("sentence_transformers not found. Install with: pip install sentence-transformers")
        return None
    except Exception as e:
        logger.error(f"Error loading embedding model: {str(e)}")
        return None

def create_cv_embeddings() -> Dict[str, Any]:
    """
    Generate embeddings for the CV and save them to disk.
    Returns a dictionary with the embeddings and metadata.
    """
    # Check if embeddings file exists and is recent (less than 24 hours old)
    embeddings_file = os.path.join(EMBEDDINGS_DIR, "cv_embeddings.json")
    
    if os.path.exists(embeddings_file):
        try:
            with open(embeddings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                created_at = datetime.fromisoformat(data.get("created_at", "2000-01-01T00:00:00"))
                now = datetime.now()
                # If embeddings are less than 24 hours old, return them
                if (now - created_at).total_seconds() < 86400:  # 24 hours
                    logger.info(f"Using cached CV embeddings from {created_at.isoformat()}")
                    return data
        except Exception as e:
            logger.warning(f"Error loading cached embeddings: {str(e)}")
    
    # Load CV data
    try:
        with open(CV_DATA_PATH, "r", encoding="utf-8") as f:
            cv_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading CV data: {str(e)}")
        return {"error": str(e)}
    
    # Generate embeddings
    model = get_embedding_model()
    
    if model is None:
        # Fallback: return the raw CV data
        logger.warning("Using fallback method (raw CV data) as embedding model couldn't be loaded")
        return {
            "cv_data": cv_data,
            "created_at": datetime.now().isoformat(),
            "embedding_method": "none"
        }
    
    # Create text representation for embedding
    cv_text = json.dumps(cv_data, ensure_ascii=False)
    
    # Generate embeddings for the whole CV
    embedding = model.encode(cv_text)
    
    # Also create section-specific embeddings for more targeted matching
    sections = {}
    if "personal_information" in cv_data:
        sections["personal"] = model.encode(json.dumps(cv_data["personal_information"], ensure_ascii=False))
    
    if "professional_summary" in cv_data:
        sections["summary"] = model.encode(cv_data["professional_summary"])
    
    if "skills" in cv_data:
        skills = cv_data.get("skills", [])
        
        # Handle empty skills list or non-list skills
        if not skills:
            skills_text = ""
        # Check if skills is a list of dictionaries
        elif isinstance(skills, list) and skills and isinstance(skills[0], dict):
            skills_text = " ".join([skill.get("name", "") + " " + skill.get("description", "") 
                                for skill in skills])
        # Check if skills is a dictionary
        elif isinstance(skills, dict):
            skills_text = " ".join([f"{k}: {v}" for k, v in skills.items()])
        else:
            # Handle case where skills are just strings or other types
            skills_text = " ".join([str(skill) for skill in skills])
            
        sections["skills"] = model.encode(skills_text)
    
    if "experience" in cv_data:
        experience = cv_data.get("experience", [])
        
        # Handle empty experience list or non-list experience
        if not experience:
            experience_text = ""
        # Check if experience is a list of dictionaries
        elif isinstance(experience, list) and experience and isinstance(experience[0], dict):
            experience_text = " ".join([exp.get("title", "") + " " + exp.get("description", "") 
                                    for exp in experience])
        # Check if experience is a dictionary
        elif isinstance(experience, dict):
            experience_text = " ".join([f"{k}: {v}" for k, v in experience.items()])
        else:
            # Handle case where experience items are just strings or other types
            experience_text = " ".join([str(exp) for exp in experience])
            
        sections["experience"] = model.encode(experience_text)
    
    # Convert numpy arrays to lists for JSON serialization
    result = {
        "cv_data": cv_data,
        "embedding": embedding.tolist(),
        "sections": {k: v.tolist() for k, v in sections.items()},
        "created_at": datetime.now().isoformat(),
        "embedding_method": "sentence_transformers"
    }
    
    # Save embeddings to disk
    try:
        with open(embeddings_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"CV embeddings saved to {embeddings_file}")
    except Exception as e:
        logger.error(f"Error saving CV embeddings: {str(e)}")
    
    return result

def get_cv_embeddings() -> Dict[str, Any]:
    """
    Get the CV embeddings, creating them if they don't exist.
    Returns a dictionary with the embeddings and CV data.
    """
    return create_cv_embeddings()

def get_cv_data_for_matching() -> Dict[str, Any]:
    """
    Get the CV data in a format suitable for matching.
    If embeddings are available, returns a dict with embeddings and CV data.
    Otherwise, returns just the CV data as a string.
    """
    try:
        embeddings = get_cv_embeddings()
        
        # If we have embeddings, return them
        if isinstance(embeddings, dict) and "embedding" in embeddings and embeddings["embedding"] is not None:
            logger.info("Using CV data with embeddings")
            return embeddings
        
        # Fallback to raw CV data
        if isinstance(embeddings, dict) and "cv_data" in embeddings:
            logger.info("Using CV data without embeddings")
            return {
                "cv_text": json.dumps(embeddings["cv_data"], ensure_ascii=False, indent=2),
                "embedding_method": "none"
            }
        
        # Ultimate fallback - load CV directly
        logger.info("Fallback: Using CV data loaded directly from file")
        try:
            with open(CV_DATA_PATH, "r", encoding="utf-8") as f:
                cv_data = json.load(f)
            return {
                "cv_text": json.dumps(cv_data, ensure_ascii=False, indent=2),
                "embedding_method": "none"
            }
        except Exception as e:
            logger.error(f"Error loading CV data from file: {str(e)}")
            return {"error": str(e)}
            
    except Exception as e:
        logger.error(f"Error in get_cv_data_for_matching: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Ultimate fallback - try to load CV directly
        try:
            with open(CV_DATA_PATH, "r", encoding="utf-8") as f:
                cv_data = json.load(f)
            return {
                "cv_text": json.dumps(cv_data, ensure_ascii=False, indent=2),
                "embedding_method": "none"
            }
        except Exception as e2:
            logger.error(f"Error in final fallback: {str(e2)}")
            return {"error": f"{str(e)} / {str(e2)}"}
def get_cv_json_text(force_regenerate=False) -> str:
    """
    Get the CV data as a formatted JSON text string.
    Args:
        force_regenerate (bool): If True, regenerate the data even if it already exists
    
    Returns:
        str: The CV data as a JSON text string
    """
    try:
        logger.info("Getting CV data for matching...")
        cv_data = get_cv_data_for_matching()
        logger.info(f"CV data type: {type(cv_data)}")
        
        # Check if CV data is None or empty
        if cv_data is None:
            logger.error("CV data is None")
            # Fallback to loading directly
            with open(CV_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        # Check if cv_data contains the cv_text field
        if isinstance(cv_data, dict) and "cv_text" in cv_data:
            logger.info("Found cv_text in cv_data dict")
            return cv_data["cv_text"]
        
        # If cv_data is already a string, return it directly
        if isinstance(cv_data, str):
            logger.info("CV data is a string, returning directly")
            return cv_data
        
        # If cv_data is a dict without cv_text but with embedding data, convert it to text
        if isinstance(cv_data, dict):
            if "cv_data" in cv_data:
                logger.info("Converting cv_data.cv_data to text")
                return json.dumps(cv_data["cv_data"], ensure_ascii=False, indent=2)
            logger.info("Converting cv_data dict to text")
            return json.dumps(cv_data, ensure_ascii=False, indent=2)
        
        # Fallback to loading directly
        logger.info("Using fallback: loading CV data directly from file")
        with open(CV_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)  # type: ignore
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error getting CV JSON text: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return "{}"