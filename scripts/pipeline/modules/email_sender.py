#!/usr/bin/env python3
"""
Email Sender Module

Handles email delivery for the pipeline, including Excel files and cover letters.
This module provides a clean interface for the main pipeline to send email packages.
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

def send_email_package(excel_path: str, cover_letters: List[str], reviewer_email: Optional[str] = None) -> bool:
    """
    Send Excel file and cover letters via email
    
    Args:
        excel_path: Path to Excel file to send
        cover_letters: List of cover letter file paths or count
        reviewer_email: Email address to send to (optional)
        
    Returns:
        True if email sent successfully, False otherwise
    """
    logger.info("=== SENDING EMAIL PACKAGE ===")
    
    try:
        # Try to import email sender
        try:
            from run_pipeline.email_sender import EmailSender, CONFIG
        except ImportError:
            logger.warning("📧 Email sender module not found - email delivery skipped")
            return True  # Non-critical failure
        
        # Prepare email
        reviewer_email = reviewer_email or CONFIG.get('work_email')
        if not reviewer_email:
            logger.warning("📧 No reviewer email configured - email delivery skipped")
            return True
        
        # Prepare attachments
        attachments = [excel_path]
        if cover_letters:
            # Add cover letter files to attachments
            import glob
            cover_letter_dir = project_root / "docs" / "cover_letters"
            if cover_letter_dir.exists():
                cover_letter_files = list(cover_letter_dir.glob("cover_letter_*.md"))
                attachments.extend([str(f) for f in cover_letter_files])
        
        # Send email
        sender = EmailSender(CONFIG)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        subject = f"xai job_matches_{timestamp}.xlsx"
        body = f"""Hi!

Attached are your job matches for review:

- Excel file: {Path(excel_path).name}
- {_get_cover_letter_count(cover_letters)} cover letters generated for 'Good' matches

Please review the matches and add any feedback in the 'reviewer_feedback' column if needed.

Best regards,
Project Sunset Phase 7 Pipeline
"""
        
        success = sender.send_email(reviewer_email, subject, body, attachments)
        
        if success:
            logger.info(f"✅ Successfully emailed {len(attachments)} files to {reviewer_email}")
            return True
        else:
            logger.warning("⚠️ Email delivery failed - continuing pipeline")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during email delivery: {e}")
        return False

def _get_cover_letter_count(cover_letters) -> int:
    """
    Get count of cover letters, handling both integer count and list types
    
    Args:
        cover_letters: Either an integer count or list of cover letters
        
    Returns:
        Number of cover letters
    """
    if isinstance(cover_letters, int):
        return cover_letters
    elif isinstance(cover_letters, list):
        return len(cover_letters)
    else:
        return 0

def validate_email_system() -> bool:
    """
    Validate that the email system is available and configured
    
    Returns:
        True if email system is available, False otherwise
    """
    try:
        from run_pipeline.email_sender import EmailSender, CONFIG
        
        # Check if email is configured
        if not CONFIG.get('work_email'):
            logger.warning("⚠️ No work email configured in email system")
            return False
        
        logger.info("✅ Email system available and configured")
        return True
        
    except ImportError as e:
        logger.warning(f"⚠️ Email system not available: {e}")
        return False

def send_notification_email(subject: str, body: str, reviewer_email: Optional[str] = None) -> bool:
    """
    Send a simple notification email without attachments
    
    Args:
        subject: Email subject
        body: Email body
        reviewer_email: Email address to send to (optional)
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        from run_pipeline.email_sender import EmailSender, CONFIG
        
        reviewer_email = reviewer_email or CONFIG.get('work_email')
        if not reviewer_email:
            logger.warning("📧 No reviewer email configured")
            return False
        
        sender = EmailSender(CONFIG)
        success = sender.send_email(reviewer_email, subject, body)
        
        if success:
            logger.info(f"✅ Notification email sent to {reviewer_email}")
        else:
            logger.warning("⚠️ Failed to send notification email")
            
        return success
        
    except Exception as e:
        logger.error(f"❌ Error sending notification email: {e}")
        return False

if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    print("Testing email sender module...")
    
    # Test validation
    is_available = validate_email_system()
    print(f"Email system available: {is_available}")
    
    # Test notification (won't actually send)
    print("Email sender module ready for use")
