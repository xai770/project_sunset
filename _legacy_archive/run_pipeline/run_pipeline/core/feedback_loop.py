#!/usr/bin/env python3
"""
Feedback loop module for managing the JMFS feedback workflow steps:
- Excel export
- Cover letter generation
- Email delivery
- Feedback processing
"""

import os
import glob
import logging
from datetime import datetime
import inspect

logger = logging.getLogger('pipeline')

def run_excel_export_step(args, log_dir):
    """Step 7: Export Excel with A-R columns and logging"""
    logger.info("Step 7/10: Exporting job matches with feedback structure...")
    try:
        from run_pipeline.export_job_matches import export_job_matches
        sig = inspect.signature(export_job_matches)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"job_matches_{timestamp}.xlsx"
        export_args = {
            'output_format': 'excel',
            'output_file': output_file
        }
        if 'feedback_system' in sig.parameters:
            export_args['feedback_system'] = True
        if 'reviewer_name' in sig.parameters:
            export_args['reviewer_name'] = getattr(args, 'reviewer_name', 'xai')
        export_path = export_job_matches(**export_args)
        if export_path:
            logger.info(f"Successfully exported job matches to {export_path}")
            return export_path
        else:
            logger.error("Failed to export job matches")
            return None
    except Exception as e:
        logger.error(f"Error in Excel export step: {e}")
        return None

def run_cover_letter_generation_step(args, excel_path, log_dir):
    """Step 8: Generate cover letters for Good matches"""
    logger.info("Step 8/10: Generating cover letters for Good matches...")
    try:
        from run_pipeline import process_excel_cover_letters
    except ImportError:
        process_excel_cover_letters = None
        logger.warning("process_excel_cover_letters module not found - skipping cover letter generation")
        return True

    try:
        if hasattr(process_excel_cover_letters, 'main'):
            import inspect
            sig = inspect.signature(process_excel_cover_letters.main)
            cover_args = {'excel_path': excel_path}
            if 'job_title_col' in sig.parameters:
                cover_args['job_title_col'] = "Position title"
            if 'narrative_col' in sig.parameters:
                cover_args['narrative_col'] = "Application narrative"
            if 'update_excel_log' in sig.parameters:
                cover_args['update_excel_log'] = True
            result = process_excel_cover_letters.main(**cover_args)
            if isinstance(result, int):
                logger.info(f"Generated {result} cover letters")
            else:
                logger.info("Cover letter generation completed")
            return True
        else:
            logger.warning("process_excel_cover_letters.main function not found")
            return True
    except Exception as e:
        logger.error(f"Error in cover letter generation step: {e}")
        return True


def run_email_delivery_step(args, excel_path, log_dir):
    """Step 9: Email Excel and cover letters to reviewer"""
    logger.info("Step 9/10: Emailing Excel and cover letters to reviewer...")
    try:
        from run_pipeline import email_sender
    except ImportError:
        email_sender = None
        logger.warning("email_sender module not found - skipping email delivery")
        return True

    try:
        import glob
        import os
        possible_cover_dirs = [
            "docs/cover_letters",
            "./docs/cover_letters",
            "../docs/cover_letters"
        ]
        cover_letters = []
        for cover_dir in possible_cover_dirs:
            if os.path.exists(cover_dir):
                cover_letters = glob.glob(os.path.join(cover_dir, "cover_letter_*.md"))
                if cover_letters:
                    logger.info(f"Found {len(cover_letters)} cover letters in {cover_dir}")
                    break
        reviewer_name = getattr(args, 'reviewer_name', 'xai')
        reviewer_email = getattr(args, 'reviewer_email', email_sender.CONFIG.get('work_email'))
        if not reviewer_email:
            logger.warning("No reviewer email configured - skipping email delivery")
            return True
        subject = f"{reviewer_name} {os.path.basename(excel_path)}"
        body = f"""Hi {reviewer_name},\n\nAttached are your job matches for review:\n\n- Excel file: {os.path.basename(excel_path)}\n- {len(cover_letters)} cover letters (if any)\n\nPlease review and add feedback in the 'reviewer_feedback' column if needed.\n\nBest regards,\nJob Matching System"""
        sender = email_sender.EmailSender(email_sender.CONFIG)
        attachments = [excel_path] + cover_letters
        success = sender.send_email(reviewer_email, subject, body, attachments)
        if success:
            logger.info(f"Successfully emailed {len(attachments)} files to {reviewer_email}")
        else:
            logger.warning("Failed to send email - continuing pipeline")
        return True
    except Exception as e:
        logger.error(f"Error in email delivery step: {e}")
        return True


def run_feedback_processing_step(args, log_dir):
    """Step 10: Process returned Excel feedback"""
    logger.info("Step 10/10: Processing returned feedback...")
    try:
        try:
            from run_pipeline.core.mailman_service import MailmanService, MAILMAN_CONFIG
            mailman = MailmanService(MAILMAN_CONFIG)
            reviewer_name = getattr(args, 'reviewer_name', 'xai')
            feedback_results = mailman.scan_and_process(reviewer_name)
            if feedback_results:
                successful = sum(1 for r in feedback_results if r.get('status') == 'success')
                logger.info(f"Processed {successful} feedback emails successfully")
            else:
                logger.info("No feedback emails found to process")
            return True
        except ImportError:
            logger.info("JMFS components not available - using basic feedback processing")
            try:
                from run_pipeline.job_matcher.feedback_handler import process_feedback
                import inspect
                sig = inspect.signature(process_feedback)
                if len(sig.parameters) > 0:
                    logger.info("Basic feedback processing requires parameters - skipping")
                else:
                    result = process_feedback()
                    if result:
                        logger.info("Basic feedback processing completed")
                    else:
                        logger.info("No feedback to process")
            except Exception as fallback_error:
                logger.warning(f"Basic feedback processing failed: {fallback_error}")
            return True
    except Exception as e:
        logger.error(f"Error in feedback processing step: {e}")
        return True

def execute_feedback_loop(args, log_dir):
    """Execute all steps in the feedback loop"""
    logger.info("Starting JMFS feedback loop steps...")
    excel_path = run_excel_export_step(args, log_dir)
    if not excel_path:
        logger.warning("Step 7 (Excel export) failed - continuing without JMFS")
    else:
        run_cover_letter_generation_step(args, excel_path, log_dir)
        run_email_delivery_step(args, excel_path, log_dir)
    run_feedback_processing_step(args, log_dir)
    logger.info("JMFS feedback loop completed")
    return True

# Export functions
__all__ = [
    'run_excel_export_step', 
    'run_cover_letter_generation_step',
    'run_email_delivery_step',
    'run_feedback_processing_step',
    'execute_feedback_loop'
]
