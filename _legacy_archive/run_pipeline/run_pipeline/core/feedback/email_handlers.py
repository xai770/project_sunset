"""
Email Handlers Module for JMFS

Contains methods for sending emails with feedback and clarifications
"""
import logging
from typing import Dict, Any, Optional, List

# Configure logging
logger = logging.getLogger("jmfs.feedback.email_handlers")

def email_cover_letter(job_id, cover_letter_path, reason, config):
    """Email generated cover letter to reviewer."""
    try:
        # If email_sender module is available, use it
        try:
            from run_pipeline.email_sender import EmailSender, CONFIG
            
            sender = EmailSender(CONFIG)
            
            subject = f"New Cover Letter Generated - Job {job_id}"
            body = f"""Hi!

We've generated a new cover letter for Job {job_id} based on your feedback.

Your feedback: "{reason}"

The cover letter is attached. Let us know if you'd like any adjustments!

Best regards,
Job Matching System
"""
            
            reviewer_email = config.get('reviewer_email')
            if not reviewer_email:
                logger.warning("No reviewer email configured, skipping email")
                return False
                
            success = sender.send_email(
                reviewer_email,
                subject, 
                body,
                [cover_letter_path]
            )
            
            return success
        except ImportError:
            logger.warning("EmailSender not available, logging cover letter path instead")
            logger.info(f"Cover letter saved to: {cover_letter_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error emailing cover letter: {e}")
        return False

def send_clarification_email(job_id, position_title, email_content, subject_prefix, config):
    """Send clarification email to reviewer."""
    try:
        # If email_sender module is available, use it
        try:
            from run_pipeline.email_sender import EmailSender, CONFIG
            
            sender = EmailSender(CONFIG)
            
            subject = f"{subject_prefix} - {position_title} (Job {job_id})"
            
            reviewer_email = config.get('reviewer_email')
            if not reviewer_email:
                logger.warning("No reviewer email configured, skipping email")
                return False
                
            success = sender.send_email(
                reviewer_email,
                subject,
                email_content
            )
            
            return success
        except ImportError:
            logger.warning("EmailSender not available, logging email content instead")
            logger.info(f"Email content: {email_content}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending clarification email: {e}")
        return False
