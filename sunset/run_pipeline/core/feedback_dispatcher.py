"""
Feedback Dispatcher for JMFS: Orchestrates LLM-powered feedback routing, action dispatch, and Excel logging.
"""
import argparse
import os
import logging
from typing import Dict, Any, List, Optional

import pandas as pd

# Import the new modular components
from run_pipeline.core.feedback_config import get_config
from run_pipeline.core.feedback.llm_handlers import (
    analyze_feedback_with_master_llm,
    handle_cover_letter_generation, 
    handle_conflict_resolution,
    handle_gibberish_clarification,
    handle_learning_feedback
)
from run_pipeline.core.feedback.email_handlers import (
    email_cover_letter,
    send_clarification_email
)
from run_pipeline.core.feedback.excel_handlers import (
    extract_jobs_with_feedback,
    update_excel_row
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("jmfs.feedback_dispatcher")

class FeedbackDispatcher:
    def __init__(self, config=None):
        if config is None:
            config_dict = get_config()
            self.config = config_dict['feedback_dispatcher']
        else:
            self.config = config
        logger.info("Feedback Dispatcher initialized")
            
    def dispatch_feedback(self, excel_path: str, reviewer_name: str = "xai") -> dict:
        """
        Main method to process feedback from Excel file.
        
        Args:
            excel_path: Path to Excel file with reviewer feedback
            reviewer: Name of reviewer
            
        Returns:
            Processing results
        """
        try:
            logger.info(f"Processing feedback from {excel_path} for reviewer {reviewer_name}")
            
            # Load Excel file with pandas
            df = pd.read_excel(excel_path)
            
            # Extract jobs with feedback
            jobs_with_feedback = extract_jobs_with_feedback(df)
            
            if not jobs_with_feedback:
                logger.info("No feedback found in Excel file")
                return {"processed": 0, "results": []}
            
            logger.info(f"Found {len(jobs_with_feedback)} jobs with feedback")
            
            # Analyze feedback with Master LLM
            action_plan = analyze_feedback_with_master_llm(jobs_with_feedback, self.config)
            
            # Process each action
            results = []
            for action in action_plan.get('actions', []):
                job_id = action.get('job_id', '')
                action_type = action.get('action_type', '')
                
                # Find corresponding job data
                job_data = next((job for job in jobs_with_feedback if str(job['job_id']) == str(job_id)), None)
                if not job_data:
                    logger.warning(f"Could not find job data for {job_id}")
                    continue
                
                # Dispatch to appropriate handler
                result = None
                if action_type == 'GENERATE_COVER_LETTER':
                    result = handle_cover_letter_generation(action, job_data, self.config)
                    # If successful, also email the cover letter
                    if result['status'] == 'success' and 'file_path' in result:
                        email_sent = email_cover_letter(
                            job_id,
                            result['file_path'],
                            action.get('feedback_text', ''),
                            self.config
                        )
                        if email_sent:
                            result['log_message'] += " and emailed"
                
                elif action_type == 'RESOLVE_CONFLICT':
                    result = handle_conflict_resolution(action, job_data, self.config)
                    # If successful, send the email
                    if result['status'] == 'success' and 'email_content' in result:
                        email_sent = send_clarification_email(
                            job_id,
                            job_data.get('position_title', 'Unknown Position'),
                            result['email_content'],
                            "Clarification needed on job match assessment",
                            self.config
                        )
                        if email_sent:
                            result['log_message'] = f"Sent conflict resolution email"
                        else:
                            result['log_message'] = f"Generated conflict resolution email (not sent)"
                
                elif action_type == 'CLARIFY_GIBBERISH':
                    result = handle_gibberish_clarification(action, job_data, self.config)
                    # If successful, send the email
                    if result['status'] == 'success' and 'email_content' in result:
                        email_sent = send_clarification_email(
                            job_id,
                            job_data.get('position_title', 'Unknown Position'),
                            result['email_content'],
                            "Could you help clarify your feedback?",
                            self.config
                        )
                        if email_sent:
                            result['log_message'] = f"Sent gibberish clarification email"
                        else:
                            result['log_message'] = f"Generated gibberish clarification email (not sent)"
                
                elif action_type == 'PROCESS_LEARNING':
                    result = handle_learning_feedback(action, job_data, self.config)
                
                else:  # IGNORE
                    result = {
                        'job_id': job_id,
                        'action': 'IGNORE',
                        'status': 'success',
                        'log_message': "No action needed for this feedback"
                    }
                
                if result:
                    results.append(result)
                    # Update Excel with results
                    update_excel_row(df, job_data['row_index'], result)
            
            # Save updated Excel
            df.to_excel(excel_path, index=False)
            logger.info(f"Updated Excel file with processing results")
            
            return {
                "processed": len(results),
                "results": results,
                "summary": action_plan.get('summary', ''),
                "excel_updated": True
            }
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            return {"error": str(e), "processed": 0}

def main():
    parser = argparse.ArgumentParser(description="Feedback Dispatcher for JMFS feedback loop")
    parser.add_argument("--excel", required=True, help="Path to feedback Excel file")
    parser.add_argument("--reviewer", default="xai", help="Reviewer name")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    # Configure logging based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Initialize dispatcher
    dispatcher = FeedbackDispatcher()
    
    # Process feedback
    result = dispatcher.dispatch_feedback(args.excel, args.reviewer)
    
    # Print summary
    if "error" in result:
        print(f"Error: {result['error']}")
        return 1
        
    print(f"Feedback processing complete!")
    print(f"Processed {result['processed']} feedback items")
    if result.get('summary'):
        print(f"Summary: {result['summary']}")
    
    return 0

if __name__ == "__main__":
    exit(main())
