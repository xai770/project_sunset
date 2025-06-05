# JMFS Pipeline Integration - Revised Implementation Request

## 🎯 **Objective**
Integrate JMFS components into `pipeline_orchestrator.py` as Steps 7-10, addressing dependency requirements and import consistency issues identified by Copilot.

---

## 🔍 **Pre-Implementation Verification**

### **1. Check Existing Dependencies**
Before implementing, verify these components exist and have required functionality:

#### **A. Check `export_job_matches.py`**
```python
# Verify this function exists with these parameters:
def export_job_matches(output_format='excel', output_file=None, job_ids=None, 
                      feedback_system=False, reviewer_name="xai"):
```
- ✅ **If exists**: Proceed with implementation
- ❌ **If missing**: Implement basic version or use existing function with available parameters

#### **B. Check `process_excel_cover_letters.py`**
```python
# Verify this function exists:
def main(excel_path, job_title_col='Position title', narrative_col='Application narrative', 
         update_excel_log=True):
```
- ✅ **If exists**: Proceed with implementation  
- ❌ **If missing**: Implement basic version or use existing function

#### **C. Check JMFS Components (Optional)**
```python
# These are optional - implementation should work without them:
from run_pipeline.core.mailman_service import MailmanService, MAILMAN_CONFIG
from run_pipeline.core.feedback_dispatcher import FeedbackDispatcher, FEEDBACK_DISPATCHER_CONFIG
```
- ✅ **If exists**: Use full feedback processing
- ❌ **If missing**: Skip feedback processing with graceful fallback

---

## 🔧 **Revised Implementation**

### **1. Fix Import Consistency in `pipeline_orchestrator.py`**

**Current Inconsistent Import:**
```python
import export_job_matches  # ← Top level import
# Later used as: export_job_matches.export_job_matches(...)  # ← Inconsistent
```

**Fixed Consistent Import:**
```python
from export_job_matches import export_job_matches  # ← Direct function import
# Later used as: export_job_matches(...)  # ← Consistent
```

### **2. Defensive Step 7 Implementation**

```python
def run_excel_export_step(args, log_dir):
    """Step 7: Export job matches with feedback system structure"""
    logger.info("Step 7/10: Exporting job matches...")
    try:
        # Import with error handling
        try:
            from export_job_matches import export_job_matches
        except ImportError:
            logger.error("export_job_matches module not found")
            return None
        
        # Check available parameters for export_job_matches function
        import inspect
        sig = inspect.signature(export_job_matches)
        has_feedback_system = 'feedback_system' in sig.parameters
        has_reviewer_name = 'reviewer_name' in sig.parameters
        
        # Prepare arguments based on available parameters
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"job_matches_{timestamp}.xlsx"
        
        export_args = {
            'output_format': 'excel',
            'output_file': output_file
        }
        
        # Add optional parameters if supported
        if has_feedback_system:
            export_args['feedback_system'] = True
        if has_reviewer_name:
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
```

### **3. Defensive Step 8 Implementation**

```python
def run_cover_letter_generation_step(args, excel_path, log_dir):
    """Step 8: Generate cover letters for Good matches"""
    logger.info("Step 8/10: Generating cover letters...")
    try:
        # Try to import cover letter processor
        try:
            import process_excel_cover_letters
        except ImportError:
            logger.warning("process_excel_cover_letters module not found - skipping cover letter generation")
            return True  # Not critical, continue pipeline
        
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
                return True
            else:
                logger.info("Cover letter generation completed")
                return True
        else:
            logger.warning("process_excel_cover_letters.main function not found")
            return True  # Continue pipeline
            
    except Exception as e:
        logger.error(f"Error in cover letter generation step: {e}")
        return True  # Non-critical, continue pipeline
```

### **4. Defensive Step 9 Implementation**

```python
def run_email_delivery_step(args, excel_path, log_dir):
    """Step 9: Email Excel and cover letters to reviewer"""
    logger.info("Step 9/10: Emailing Excel and cover letters...")
    try:
        # Try to import email sender
        try:
            from email_sender import EmailSender, CONFIG
        except ImportError:
            logger.warning("email_sender module not found - skipping email delivery")
            return True  # Continue pipeline
        
        import glob
        import os
        
        # Find project root and cover letter directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        possible_cover_dirs = [
            os.path.join(project_root, "docs", "cover_letters"),
            os.path.join(project_root, "cover_letters"),
            "./docs/cover_letters",
            "./cover_letters"
        ]
        
        cover_letters = []
        for cover_dir in possible_cover_dirs:
            if os.path.exists(cover_dir):
                cover_letters = glob.glob(os.path.join(cover_dir, "cover_letter_*.md"))
                if cover_letters:
                    logger.info(f"Found {len(cover_letters)} cover letters in {cover_dir}")
                    break
        
        # Prepare email
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
```

### **5. Defensive Step 10 Implementation**

```python
def run_feedback_processing_step(args, log_dir):
    """Step 10: Process returned Excel feedback"""
    logger.info("Step 10/10: Processing feedback...")
    try:
        # Try to import JMFS components
        try:
            from run_pipeline.core.mailman_service import MailmanService, MAILMAN_CONFIG
            from run_pipeline.core.feedback_dispatcher import FeedbackDispatcher, FEEDBACK_DISPATCHER_CONFIG
            
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
            
        except ImportError as e:
            logger.info(f"JMFS components not available ({e}) - using basic feedback check")
            
            # Fallback: Basic feedback detection
            try:
                from export_job_matches import export_job_matches
                export_path = export_job_matches(output_format='excel')
                
                if export_path and os.path.exists(export_path):
                    import pandas as pd
                    df = pd.read_excel(export_path)
                    
                    # Check for feedback in common column names
                    feedback_columns = ['reviewer_feedback', 'Feedback', 'feedback']
                    feedback_found = False
                    
                    for col in feedback_columns:
                        if col in df.columns and df[col].notna().any():
                            feedback_count = df[col].notna().sum()
                            logger.info(f"Found {feedback_count} items with feedback in column '{col}'")
                            feedback_found = True
                            break
                    
                    if not feedback_found:
                        logger.info("No feedback found in exported Excel file")
                else:
                    logger.info("No Excel file available for feedback check")
                    
            except Exception as fallback_error:
                logger.warning(f"Basic feedback check also failed: {fallback_error}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error in feedback processing step: {e}")
        return True  # Non-critical, don't fail pipeline
```

### **6. Modified Main Pipeline Function**

```python
# Add this after the existing Step 6/7 (phi3 processing):

    # JMFS Steps 7-10: Feedback Loop (Optional)
    if getattr(args, 'enable_feedback_loop', False):
        logger.info("Starting JMFS feedback loop steps...")
        
        # Step 7: Export Excel 
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

    final_step = "Pipeline with JMFS completed!" if getattr(args, 'enable_feedback_loop', False) else "Pipeline completed!"
    logger.info(final_step)
    return True
```

### **7. Fixed Step 0 Logic**

```python
# Replace existing Step 0 with this:
def run_feedback_check_step(args, log_dir):
    """Step 0: Check for and optionally process existing feedback"""
    logger.info("Step 0: Checking for existing feedback...")
    
    # If in feedback-only mode, process feedback and exit
    if getattr(args, 'feedback_only', False):
        logger.info("Running in feedback-only mode")
        return run_feedback_processing_step(args, log_dir), True  # (success, should_exit)
    
    # Otherwise, just check for feedback and optionally process
    feedback_processed = run_feedback_processing_step(args, log_dir)
    should_continue = getattr(args, 'continue_after_feedback', True)
    
    return feedback_processed, not should_continue

# In main run_pipeline function, replace Step 0 section with:
feedback_success, should_exit = run_feedback_check_step(args, log_dir)
if should_exit:
    return feedback_success
```

---

## 🧪 **Phased Testing Approach**

### **Phase 1: Basic Integration**
```bash
# Test without any JMFS components
python pipeline_main.py --max-jobs 5
# Should work exactly as before
```

### **Phase 2: Excel Export Only**
```bash
# Test Step 7 only
python pipeline_main.py --max-jobs 5 --enable-feedback-loop
# Should export Excel (even if basic format)
```

### **Phase 3: Progressive Testing**
- Add enhanced `export_job_matches.py` parameters
- Add `process_excel_cover_letters.py` functionality  
- Add JMFS components when ready

---

## ✅ **Success Criteria (Revised)**

### **Minimum Viable Implementation:**
- ✅ Pipeline runs without errors when JMFS components missing
- ✅ Steps 7-10 execute with graceful fallbacks
- ✅ Excel export works (basic or enhanced format)
- ✅ Non-critical failures don't break pipeline

### **Full Implementation (when dependencies ready):**
- ✅ Enhanced Excel export with feedback system format
- ✅ Cover letter generation for Good matches
- ✅ Email delivery with existing infrastructure
- ✅ JMFS feedback processing integration

---

## 📁 **Implementation Order**

1. **Implement defensive Steps 7-10** with fallbacks
2. **Test basic integration** without dependencies
3. **Enhance components** one by one as they become available
4. **Test progressively** with each enhancement

This approach ensures you have a working system immediately, with progressive enhancement as components become available! 🚀