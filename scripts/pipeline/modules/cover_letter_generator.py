#!/usr/bin/env python3
"""
Cover Letter Generator Module

Handles cover letter generation for jobs marked as 'Good' matches.
This module integrates with the existing cover letter system while providing
a clean interface for the main pipeline.
"""

import logging
import sys
from pathlib import Path
from typing import List, Union, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

def generate_cover_letters_for_good_matches(excel_path: str) -> Union[int, List[str]]:
    """
    Generate cover letters for jobs marked as 'Good' matches
    
    Args:
        excel_path: Path to the Excel file containing job matches
        
    Returns:
        Number of cover letters generated or list of generated files
    """
    logger.info("=== GENERATING COVER LETTERS ===")
    
    try:
        # Use the existing cover letter generation system
        from run_pipeline.process_excel_cover_letters import main as process_cover_letters
        
        # Call the cover letter processor with the Excel file
        # This system uses specialists internally for LLM work
        cover_letter_results = process_cover_letters(
            excel_path=excel_path,
            update_excel_log=True
        )
        
        if cover_letter_results:
            logger.info(f"✅ Generated cover letters for good matches")
            return cover_letter_results
        else:
            logger.warning("⚠️ No cover letters generated (no 'Good' matches found)")
            return []
            
    except Exception as e:
        logger.error(f"❌ Error during cover letter generation: {e}")
        return []

def validate_cover_letter_system() -> bool:
    """
    Validate that the cover letter generation system is available and working
    
    Returns:
        True if system is available, False otherwise
    """
    try:
        from run_pipeline.process_excel_cover_letters import main as process_cover_letters
        from run_pipeline.cover_letter import template_manager
        
        logger.info("✅ Cover letter generation system available")
        return True
        
    except ImportError as e:
        logger.warning(f"⚠️ Cover letter generation system not available: {e}")
        return False

def get_cover_letter_files(cover_letter_dir: Optional[Path] = None) -> List[str]:
    """
    Get list of generated cover letter files
    
    Args:
        cover_letter_dir: Directory to search for cover letters
        
    Returns:
        List of cover letter file paths
    """
    if cover_letter_dir is None:
        cover_letter_dir = project_root / "docs" / "cover_letters"
    
    cover_letter_files = []
    
    if cover_letter_dir.exists():
        # Find all cover letter files
        cover_letter_files.extend(list(cover_letter_dir.glob("cover_letter_*.md")))
        cover_letter_files.extend(list(cover_letter_dir.glob("Cover_Letter_*.md")))
        
        # Convert to strings
        cover_letter_files = [str(f) for f in cover_letter_files]
        
        logger.info(f"📄 Found {len(cover_letter_files)} cover letter files")
    else:
        logger.warning(f"⚠️ Cover letter directory not found: {cover_letter_dir}")
    
    return cover_letter_files

if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    print("Testing cover letter generator module...")
    
    # Test validation
    is_available = validate_cover_letter_system()
    print(f"Cover letter system available: {is_available}")
    
    # Test file discovery
    files = get_cover_letter_files()
    print(f"Found {len(files)} cover letter files")
