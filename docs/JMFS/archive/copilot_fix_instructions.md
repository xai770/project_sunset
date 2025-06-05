# Copilot Instructions: Fix JMFS Steps 8-10 Import Path Issues

## Problem Summary
The JMFS pipeline Steps 8-10 are failing due to import path issues when running from `run_pipeline/core/pipeline_orchestrator.py`. Step 7 (Excel export) works perfectly, but Steps 8-10 can't find the required modules.

## Current Error Messages
```
Step 8: WARNING - process_excel_cover_letters module not found - skipping cover letter generation
Step 9: WARNING - email_sender module not found - skipping email delivery  
Step 10: ERROR - [Errno 2] No such file or directory: '../config/credentials.json'
```

## File Structure Context
```
run_pipeline/
├── core/
│   └── pipeline_orchestrator.py  # <-- Running from here
├── process_excel_cover_letters.py  # <-- Needs to import this
├── email_sender.py                 # <-- Needs to import this
└── ...
config/
└── credentials.json                 # <-- Needs to access this
```

## Required Changes in `run_pipeline/core/pipeline_orchestrator.py`

### 1. Fix Step 8 (Cover Letter Generation) Import
**Current (broken) import attempt:**
```python
import process_excel_cover_letters
```

**Fix to:**
```python
from run_pipeline import process_excel_cover_letters
```

### 2. Fix Step 9 (Email Delivery) Import  
**Current (broken) import attempt:**
```python
import email_sender
```

**Fix to:**
```python
from run_pipeline import email_sender
```

### 3. Fix Step 10 (Feedback Processing) Credentials Path
**Current (broken) path:**
```python
'../config/credentials.json'
```

**Fix to:**
```python
'config/credentials.json'
```

## Implementation Requirements

### For Steps 8-10 Functions:
1. **Add proper imports at the top of the file:**
   ```python
   from run_pipeline import process_excel_cover_letters
   from run_pipeline import email_sender
   ```

2. **Update try/except blocks** to handle imports gracefully:
   ```python
   try:
       from run_pipeline import process_excel_cover_letters
       # ... rest of step 8 logic
   except ImportError as e:
       logger.warning(f"Could not import process_excel_cover_letters: {e}")
       return
   ```

3. **Fix file paths** to be relative to the project root, not the current module location.

### Specific Function Updates Needed:

#### Step 8: `jmfs_step_8_generate_cover_letters()`
- Import: `from run_pipeline import process_excel_cover_letters`
- Call: `process_excel_cover_letters.main()` or whatever the correct function name is

#### Step 9: `jmfs_step_9_email_reviewer()`  
- Import: `from run_pipeline import email_sender`
- Call: `email_sender.send_email()` or whatever the correct function name is

#### Step 10: `jmfs_step_10_process_feedback()`
- Fix credentials path: `'config/credentials.json'`
- Ensure any other file paths are correct relative to project root

## Testing Validation
After making these changes, the pipeline should:
1. ✅ Generate cover letters for the "Good" match (Model Validation Specialist job)
2. ✅ Send email with Excel + cover letter attachments  
3. ✅ Process feedback without credential path errors

## Expected Success Output
```
2025-05-26 XX:XX:XX - pipeline - INFO - Step 8/10: Generated cover letter for job [ID]
2025-05-26 XX:XX:XX - pipeline - INFO - Step 9/10: Email sent successfully to reviewer
2025-05-26 XX:XX:XX - pipeline - INFO - Step 10/10: Feedback processing initialized
```

## Notes for Copilot
- **Preserve existing error handling** - the try/except blocks should remain for graceful degradation
- **Don't change the function signatures** - only fix the imports and paths
- **Test the import paths** - make sure they work from the `run_pipeline/core/` context
- **Keep logging consistent** - maintain the existing logging pattern for success/failure

## Context from Senior Claude
These Steps 8-10 were recently integrated into the main pipeline and haven't been tested end-to-end yet. The logic is correct, just the import paths need adjustment for the new integration context.

The Excel export (Step 7) works perfectly and shows proper A-R column structure, so we're very close to having a fully functional JMFS feedback loop!