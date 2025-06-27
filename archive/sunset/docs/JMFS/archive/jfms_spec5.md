# JMFS Steps 7-10 Implementation Fix - Change Request

## 🎯 **Objective**
Fix the incorrect implementation of JMFS Steps 7-10 in `pipeline_orchestrator.py`. The current structure is correct, but the function calls, imports, and error handling need to be fixed.

---

## 🔍 **Current Issues**

### **Problem 1: Wrong Import Paths**
```python
# ❌ CURRENT (Broken):
from run_pipeline.process_excel_cover_letters import generate_cover_letters_for_excel
from run_pipeline.email_sender import send_job_matches_email

# ✅ SHOULD BE:
import process_excel_cover_letters  # Root level script
from email_sender import EmailSender, CONFIG  # Existing class
```

### **Problem 2: Non-Existent Functions**
```python
# ❌ CURRENT (Broken):
cover_letter_paths = generate_cover_letters_for_excel(export_path)
send_job_matches_email(export_path, cover_letter_paths)

# ✅ SHOULD BE:
process_excel_cover_letters.main(excel_path=export_path, ...)
EmailSender(CONFIG).send_email(...)
```

### **Problem 3: No Error Handling**
- Missing try/catch blocks
- No defensive coding for optional components
- Will crash if imports fail

---

## 🔧 **Required Changes**

### **1. Replace Current Steps 7-10 Section**

**Remove this broken section:**
```python
# Steps 7-10: JMFS Feedback Loop (if enabled)
if getattr(args, 'enable_feedback_loop', False):
    logger.info("JMFS Feedback Loop enabled. Running export, cover letter generation, email, and feedback processing...")
    try:
        # Step 7: Export Excel with A-R columns
        export_path = export_job_matches(output_format='excel', feedback_system=True)
        logger.info(f"Exported job matches to {export_path}")

        # Step 8: Generate cover letters for 'Good' matches
        from run_pipeline.process_excel_cover_letters import generate_cover_letters_for_excel
        cover_letter_paths = generate_cover_letters_for_excel(export_path)
        logger.info(f"Generated cover letters: {cover_letter_paths}")

        # Step 9: Email Excel + cover letters to reviewer
        from run_pipeline.email_sender import send_job_matches_email
        send_job_matches_email(export_path, cover_letter_paths)
        logger.info("Emailed Excel and cover letters to reviewer.")

        # Step 10: Process returned feedback with LLM dispatcher (again, for new feedback)
        feedback_processed = process_feedback()
        if feedback_processed:
            logger.info("Processed returned feedback after reviewer response.")
        else:
            logger.info("No new feedback to process after reviewer response.")
    except Exception as e:
        logger.error(f"JMFS Feedback Loop failed: {e}")
else:
    logger.info("JMFS Feedback Loop not enabled. Skipping export, cover letter, email, and feedback steps.")
```

### **2. Add These New Step Functions**

Add these functions **before the main `run_pipeline()` function**:

```python
def run_excel_export_step(args, log_dir):
    """Step 7: Export Excel with A-R columns and logging"""
    logger.info("Step 7/10: Exporting job matches with feedback structure...")
    try:
        # Use defensive import checking
        import inspect
        sig = inspect.signature(export_job_matches)
        
        # Prepare export parameters
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"job_matches_{timestamp}.xlsx"
        
        export_args = {
            'output_format': 'excel',
            'output_file': output_file
        }
        
        # Add optional parameters if supported
        if 'feedback_system' in sig.parameters:
            export_args['feedback_system'] = True
        if 'reviewer_name' in sig.parameters:
            export_args['reviewer_name'] = getattr(args, 'reviewer_name', 'xai')
        
        # Export with available parameters
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
        # Try to import cover letter processor
        try:
            import process_excel_cover_letters
        except ImportError:
            logger.warning("process_excel_cover_letters module not found - skipping cover letter generation")
            return True  # Non-critical, continue pipeline
        
        # Check if main function exists and what parameters it accepts
        if hasattr(process_excel_cover_letters, 'main'):
            import inspect
            sig = inspect.signature(process_excel_cover_letters.main)
            
            # Prepare arguments based on available parameters
            cover_args = {'excel_path': excel_path}
            
            if 'job_title_col' in sig.parameters:
                cover_args['job_title_col'] = "Position title"
            if 'narrative_col' in sig.parameters:
                cover_args['narrative_col'] = "Application narrative"
            if 'update_excel_log' in sig.parameters:
                cover_args['update_excel_log'] = True
            
            # Call with available parameters
            result = process_excel_cover_letters.main(**cover_args)
            
            if isinstance(result, int):
                logger.info(f"Generated {result} cover letters")
            else:
                logger.info("Cover letter generation completed")
            return True
        else:
            logger.warning("process_excel_cover_letters.main function not found")
            return True  # Continue pipeline
            
    except Exception as e:
        logger.error(f"Error in cover letter generation step: {e}")
        return True  # Non-critical, continue pipeline

def run_email_delivery_step(args, excel_path, log_dir):
    """Step 9: Email Excel and cover letters to reviewer"""
    logger.info("Step 9/10: Emailing Excel and cover letters to reviewer...")
    try:
        # Try to import email sender
        try:
            from email_sender import EmailSender, CONFIG
        except ImportError:
            logger.warning("email_sender module not found - skipping email delivery")
            return True  # Continue pipeline
        
        import glob
        import os
        
        # Find cover letter files
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
        
        # Prepare email details
        reviewer_name = getattr(args, 'reviewer_name', 'xai')
        reviewer_email = getattr(args, 'reviewer_email', CONFIG.get('work_email'))
        
        if not reviewer_email:
            logger.warning("No reviewer email configured - skipping email delivery")
            return True
        
        subject = f"{reviewer_name} {os.path.basename(excel_path)}"
        body = f"""Hi {reviewer_name},

Attached are your job matches for review:

- Excel file: {os.path.basename(excel_path)}
- {len(cover_letters)} cover letters (if any)

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
            logger.warning("Failed to send email - continuing pipeline")
            
        return True  # Always continue, email is not critical
        
    except Exception as e:
        logger.error(f"Error in email delivery step: {e}")
        return True  # Non-critical, continue pipeline

def run_feedback_processing_step(args, log_dir):
    """Step 10: Process returned Excel feedback"""
    logger.info("Step 10/10: Processing returned feedback...")
    try:
        # Try to use full JMFS feedback processing
        try:
            from run_pipeline.core.mailman_service import MailmanService, MAILMAN_CONFIG
            
            # Full JMFS feedback processing
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
            
            # Fallback: Basic feedback processing
            try:
                from run_pipeline.job_matcher.feedback_handler import process_feedback
                
                # Check if function accepts parameters
                import inspect
                sig = inspect.signature(process_feedback)
                
                if len(sig.parameters) > 0:
                    # Function expects parameters, skip for now
                    logger.info("Basic feedback processing requires parameters - skipping")
                else:
                    # Function takes no parameters
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
        return True  # Non-critical, don't fail pipeline
```

### **3. Replace JMFS Section with Function Calls**

**Replace the broken section with this:**
```python
    # Steps 7-10: JMFS Feedback Loop (if enabled)
    if getattr(args, 'enable_feedback_loop', False):
        logger.info("Starting JMFS feedback loop steps...")
        
        # Step 7: Export Excel with A-R columns
        excel_path = run_excel_export_step(args, log_dir)
        if not excel_path:
            logger.warning("Step 7 (Excel export) failed - continuing without JMFS")
        else:
            # Step 8: Generate cover letters
            run_cover_letter_generation_step(args, excel_path, log_dir)
            
            # Step 9: Email delivery
            run_email_delivery_step(args, excel_path, log_dir)
        
        # Step 10: Process feedback (independent of Steps 7-9)
        run_feedback_processing_step(args, log_dir)
        
        logger.info("JMFS feedback loop completed")
    else:
        logger.info("JMFS feedback loop not enabled. Use --enable-feedback-loop to activate.")
```

### **4. Add Required CLI Arguments**

Make sure these arguments exist in your CLI args file:
```python
parser.add_argument("--enable-feedback-loop", action="store_true",
                   help="Enable JMFS Steps 7-10: Excel export, cover letters, email delivery, feedback processing")
parser.add_argument("--reviewer-name", default="xai",
                   help="Name of reviewer for email and feedback processing (default: xai)")
parser.add_argument("--reviewer-email",
                   help="Email address of reviewer (overrides config)")
```

---

## ✅ **Expected Behavior After Fix**

### **Normal Pipeline (No JMFS):**
```bash
python pipeline_main.py --max-jobs 10
# Runs Steps 1-6 only, no JMFS steps
```

### **Pipeline with JMFS:**
```bash
python pipeline_main.py --max-jobs 10 --enable-feedback-loop --reviewer-name xai
# Runs Steps 1-6, then Steps 7-10 with proper error handling
```

### **Graceful Degradation:**
- If `export_job_matches` doesn't support `feedback_system` parameter → uses basic export
- If `process_excel_cover_letters` not found → skips cover letter generation
- If `email_sender` not available → skips email delivery
- If JMFS components missing → uses basic feedback processing
- **Pipeline never crashes due to missing optional components**

---

## 🧪 **Testing Checklist**

1. **Test without JMFS flag** - ensure normal pipeline still works
2. **Test with JMFS flag** - ensure Steps 7-10 execute without crashing
3. **Test with missing components** - ensure graceful fallbacks
4. **Check logs** - verify proper step execution and error handling

---

## 📁 **Files to Modify**

1. **`run_pipeline/core/pipeline_orchestrator.py`** - Add step functions and fix JMFS section
2. **`run_pipeline/core/cli_args.py`** - Ensure CLI arguments exist

---

## 🎯 **Success Criteria**

- ✅ Steps 7-10 use correct imports and function calls
- ✅ Defensive coding prevents crashes from missing components  
- ✅ Each step logs its progress clearly
- ✅ Non-critical failures don't stop the pipeline
- ✅ JMFS can be enabled/disabled via CLI flag
- ✅ Backward compatibility maintained for normal pipeline usage

---

This fix maintains your correct structure while implementing the Steps 7-10 functionality properly with robust error handling and defensive coding.