# JMFS Pipeline Integration - Implementation Request

## 🎯 **Objective**
Integrate the JMFS (Job Matching Feedback System) components into the existing `pipeline_orchestrator.py` as Steps 7-10, and fix the broken Step 0 feedback logic.

---

## 🔧 **Required Changes**

### **1. Fix Step 0 in `pipeline_orchestrator.py`**

**Current (Broken) Code:**
```python
# Step 0: Export job matches and check for feedback before running the pipeline
logger.info("Step 0: Exporting job matches and checking for feedback...")
export_path = export_job_matches(output_format='excel')
if export_path:
    import pandas as pd
    df = pd.read_excel(export_path)
    if 'Feedback' in df.columns and df['Feedback'].str.strip().any():
        logger.info("Feedback detected in exported job matches. Skipping pipeline run until feedback is processed.")
        return True  # ← PROBLEM: This stops everything!
```

**New (Fixed) Code:**
```python
# Step 0: Check for and process any existing feedback
logger.info("Step 0: Checking for existing feedback to process...")
feedback_processed = run_feedback_processing_step(args, log_dir)
if feedback_processed and not getattr(args, 'continue_after_feedback', False):
    logger.info("Feedback processed. Use --continue-after-feedback to run full pipeline afterward.")
    return True
```

### **2. Add JMFS Steps 7-10 Functions**

Add these new step functions to `pipeline_orchestrator.py`:

```python
def run_excel_export_step(args, log_dir):
    """Step 7: Export job matches with feedback system structure"""
    logger.info("Step 7/10: Exporting job matches with feedback structure...")
    try:
        # Use enhanced export_job_matches with feedback system format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"job_matches_{timestamp}.xlsx"
        
        # Call export with feedback system flag
        export_path = export_job_matches.export_job_matches(
            output_format='excel',
            output_file=output_file,
            feedback_system=True,
            reviewer_name=getattr(args, 'reviewer_name', 'xai')
        )
        
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
        # Use enhanced process_excel_cover_letters
        import process_excel_cover_letters
        
        cover_letter_count = process_excel_cover_letters.main(
            excel_path=excel_path,
            job_title_col="Position title",
            narrative_col="Application narrative", 
            update_excel_log=True
        )
        
        logger.info(f"Generated {cover_letter_count} cover letters")
        return cover_letter_count > 0
        
    except Exception as e:
        logger.error(f"Error in cover letter generation step: {e}")
        return False

def run_email_delivery_step(args, excel_path, log_dir):
    """Step 9: Email Excel and cover letters to reviewer"""
    logger.info("Step 9/10: Emailing Excel and cover letters to reviewer...")
    try:
        from email_sender import EmailSender, CONFIG
        import glob
        
        # Find generated cover letters
        cover_letter_dir = os.path.join(os.path.dirname(__file__), "../docs/cover_letters")
        cover_letters = glob.glob(os.path.join(cover_letter_dir, "cover_letter_*.md"))
        
        # Prepare email
        reviewer_name = getattr(args, 'reviewer_name', 'xai')
        reviewer_email = getattr(args, 'reviewer_email', CONFIG.get('work_email'))
        
        subject = f"{reviewer_name} {os.path.basename(excel_path)}"
        body = f"""Hi {reviewer_name},

Attached are your job matches and cover letters for review:

- Excel file: {os.path.basename(excel_path)}
- {len(cover_letters)} cover letters for Good matches

Please review and add feedback in the 'reviewer_feedback' column if needed.

Best regards,
Job Matching System"""

        # Send email
        sender = EmailSender(CONFIG)
        attachments = [excel_path] + cover_letters
        
        success = sender.send_email(reviewer_email, subject, body, attachments)
        
        if success:
            logger.info(f"Successfully emailed {len(attachments)} files to {reviewer_email}")
        else:
            logger.error("Failed to send email")
            
        return success
        
    except Exception as e:
        logger.error(f"Error in email delivery step: {e}")
        return False

def run_feedback_processing_step(args, log_dir):
    """Step 10: Process returned Excel feedback"""
    logger.info("Step 10/10: Processing returned Excel feedback...")
    try:
        # Check if we have mailman and feedback dispatcher available
        try:
            from run_pipeline.core.mailman_service import MailmanService, MAILMAN_CONFIG
            from run_pipeline.core.feedback_dispatcher import FeedbackDispatcher, FEEDBACK_DISPATCHER_CONFIG
            
            # Scan for feedback emails
            mailman = MailmanService(MAILMAN_CONFIG)
            reviewer_name = getattr(args, 'reviewer_name', 'xai')
            feedback_results = mailman.scan_and_process(reviewer_name)
            
            if feedback_results:
                successful = sum(1 for r in feedback_results if r.get('status') == 'success')
                logger.info(f"Processed {successful} feedback emails successfully")
                return True
            else:
                logger.info("No feedback emails found to process")
                return True
                
        except ImportError:
            logger.warning("Mailman service not available - skipping feedback processing")
            return True
            
    except Exception as e:
        logger.error(f"Error in feedback processing step: {e}")
        return False
```

### **3. Modify Main Pipeline Function**

Add JMFS steps to the end of `run_pipeline()` function:

```python
# Add this after the existing Step 6/7 (phi3 processing):

    # JMFS Steps 7-10: Feedback Loop
    if getattr(args, 'enable_feedback_loop', False):
        
        # Step 7: Export Excel with feedback structure
        excel_path = run_excel_export_step(args, log_dir)
        if not excel_path:
            logger.error("Step 7 (Excel export) failed")
            return False
            
        # Step 8: Generate cover letters
        if not run_cover_letter_generation_step(args, excel_path, log_dir):
            logger.error("Step 8 (cover letter generation) failed")
            return False
            
        # Step 9: Email delivery
        if not run_email_delivery_step(args, excel_path, log_dir):
            logger.error("Step 9 (email delivery) failed") 
            return False
            
        # Step 10: Process feedback (if any exists)
        if not run_feedback_processing_step(args, log_dir):
            logger.error("Step 10 (feedback processing) failed")
            return False
            
        logger.info("JMFS feedback loop completed successfully!")

    final_step = "Pipeline with JMFS completed successfully!" if getattr(args, 'enable_feedback_loop', False) else "Pipeline completed successfully!"
    logger.info(final_step)
    return True
```

### **4. Add CLI Arguments**

Add these arguments to `cli_args.py`:

```python
# JMFS Integration Arguments
parser.add_argument("--enable-feedback-loop", action="store_true",
                   help="Enable JMFS Steps 7-10: Excel export, cover letters, email delivery, feedback processing")
parser.add_argument("--reviewer-name", default="xai", 
                   help="Name of reviewer for email and feedback processing (default: xai)")
parser.add_argument("--reviewer-email", 
                   help="Email address of reviewer (overrides config)")
parser.add_argument("--continue-after-feedback", action="store_true",
                   help="Continue with full pipeline after processing feedback in Step 0")
parser.add_argument("--feedback-only", action="store_true",
                   help="Only process feedback (Steps 0 & 10), skip job processing")
```

### **5. Add Feedback-Only Mode**

Add this logic at the beginning of `run_pipeline()`:

```python
# Handle feedback-only mode
if getattr(args, 'feedback_only', False):
    logger.info("Running in feedback-only mode...")
    feedback_processed = run_feedback_processing_step(args, log_dir)
    if feedback_processed:
        logger.info("Feedback-only processing completed successfully!")
    else:
        logger.error("Feedback-only processing failed!")
    return feedback_processed
```

---

## ✅ **Expected Behavior After Implementation**

### **Normal Pipeline (Steps 1-6 only):**
```bash
python pipeline_main.py --max-jobs 10
# Runs job processing steps 1-6, no JMFS
```

### **Pipeline with JMFS (Steps 1-10):**
```bash
python pipeline_main.py --max-jobs 10 --enable-feedback-loop --reviewer-name xai
# Runs complete pipeline: job processing + JMFS feedback loop
```

### **Feedback Only:**
```bash
python pipeline_main.py --feedback-only --reviewer-name xai  
# Only processes existing feedback, skips job processing
```

---

## 🧪 **Testing Requirements**

1. **Test normal pipeline** - ensure Steps 1-6 still work unchanged
2. **Test JMFS integration** - verify Steps 7-10 execute correctly
3. **Test feedback-only mode** - verify it processes feedback without job processing
4. **Test error handling** - ensure pipeline fails gracefully if JMFS components missing

---

## 📁 **Files to Modify**

1. `run_pipeline/core/pipeline_orchestrator.py` - Main changes
2. `run_pipeline/core/cli_args.py` - Add CLI arguments
3. **Dependencies:** Ensure `export_job_matches.py` and `process_excel_cover_letters.py` are importable

---

## 🎯 **Success Criteria**

- ✅ Step 0 processes feedback instead of stopping pipeline
- ✅ Steps 7-10 execute when `--enable-feedback-loop` is used
- ✅ Excel export uses feedback system format (A-R columns)
- ✅ Cover letters generated for "Good" matches only
- ✅ Email delivery works with existing `email_sender.py`
- ✅ Feedback processing integrates with mailman/dispatcher (if available)
- ✅ Backward compatibility: normal pipeline unchanged without flags
- ✅ Error handling: graceful failures with proper logging

---

This implementation will integrate the complete JMFS system into the existing pipeline architecture while maintaining backward compatibility and adding flexible control via CLI arguments.