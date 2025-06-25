# Change Specifications for Existing Scripts

## 🎯 Overview
We have two existing scripts that are perfect building blocks for our feedback system:
1. `export_job_matches.py` - Already exports job data to Excel
2. `process_excel_cover_letters.py` - Already generates cover letters from Excel

These need modifications to support our feedback loop architecture with proper logging columns and LLM orchestration.

---

## 📊 Script 1: `export_job_matches.py` Changes

### Current Functionality Analysis
- ✅ Exports job data to Excel/CSV
- ✅ Has openpyxl integration for Excel formatting
- ✅ Processes job JSON files from JOB_DATA_DIR
- ✅ Supports job ID filtering
- ✅ Auto-adjusts column widths

### Required Changes

#### A. Column Structure Update
**Current**: Exports whatever matching results are found
**New**: Must export with our standardized A-R column structure

```python
def get_standard_columns():
    """Define the standard column structure A-R for feedback system"""
    return {
        # A-K: Job Data (existing)
        'A': 'URL',
        'B': 'Job description', 
        'C': 'Position title',
        'D': 'Location',
        'E': 'Job domain',
        'F': 'Match level',
        'G': 'Evaluation date',
        'H': 'Has domain gap',
        'I': 'Domain assessment',
        'J': 'No-go rationale',
        'K': 'Application narrative',
        
        # L-R: Logging Columns (new)
        'L': 'export_job_matches_log',
        'M': 'generate_cover_letters_log',
        'N': 'reviewer_feedback',
        'O': 'mailman_log', 
        'P': 'process_feedback_log',
        'Q': 'reviewer_support_log',
        'R': 'workflow_status'
    }
```

#### B. New Function: `extract_job_data_for_feedback_system()`
```python
def extract_job_data_for_feedback_system(job_data):
    """
    Extract job data in our standardized A-K format for feedback system.
    
    Args:
        job_data: Parsed JSON data of a job
        
    Returns:
        Dictionary with columns A-K populated
    """
    web_details = job_data.get("web_details", {})
    llama_eval = job_data.get("llama32_evaluation", {})
    
    return {
        'URL': job_data.get('url', ''),
        'Job description': web_details.get('concise_description', ''),
        'Position title': web_details.get('position_title', ''),
        'Location': web_details.get('location', ''),
        'Job domain': extract_job_domain_from_data(job_data),
        'Match level': llama_eval.get('cv_to_role_match', ''),
        'Evaluation date': llama_eval.get('evaluation_date', ''),
        'Has domain gap': determine_domain_gap(llama_eval),
        'Domain assessment': llama_eval.get('domain_knowledge_assessment', ''),
        'No-go rationale': llama_eval.get('no_go_rationale', ''),
        'Application narrative': llama_eval.get('application_narrative', '')
    }
```

#### C. New Function: `initialize_logging_columns()`
```python
def initialize_logging_columns(timestamp):
    """
    Initialize logging columns L-R with default values.
    
    Args:
        timestamp: Current timestamp for export operation
        
    Returns:
        Dictionary with columns L-R initialized
    """
    return {
        'export_job_matches_log': f"Exported at {timestamp}, v1.0, success",
        'generate_cover_letters_log': '',  # To be filled by cover letter processor
        'reviewer_feedback': '',           # To be filled by reviewer
        'mailman_log': '',                # To be filled when Excel returned
        'process_feedback_log': '',       # To be filled by feedback processor
        'reviewer_support_log': '',       # To be filled by support system
        'workflow_status': 'Exported'     # Master status tracking
    }
```

#### D. Enhanced `export_to_excel()` with Feedback System Formatting
```python
def export_to_excel_feedback_system(matches, output_file):
    """
    Export matching results to Excel format with feedback system structure.
    
    Args:
        matches: List of matching results with A-R columns
        output_file: Path to the output Excel file
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Job Matches"
    
    # Get column definitions
    columns = get_standard_columns()
    headers = list(columns.values())
    
    # Write headers
    ws.append(headers)
    
    # Apply header formatting
    for cell in ws[1]:
        cell.font = Font(bold=True, name="Liberation Sans")
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Write data rows
    for match in matches:
        row_data = [match.get(col_name, '') for col_name in columns.values()]
        ws.append(row_data)
    
    # Apply column-specific formatting
    apply_feedback_system_formatting(ws)
    
    wb.save(output_file)

def apply_feedback_system_formatting(ws):
    """Apply specific formatting for feedback system columns"""
    
    # Column widths (in characters, roughly)
    column_widths = {
        'A': 12,   # URL
        'B': 60,   # Job description  
        'C': 30,   # Position title
        'D': 24,   # Location
        'E': 29,   # Job domain
        'F': 13,   # Match level
        'G': 21,   # Evaluation date
        'H': 16,   # Has domain gap
        'I': 36,   # Domain assessment
        'J': 36,   # No-go rationale
        'K': 36,   # Application narrative
        'L': 25,   # export_job_matches_log
        'M': 25,   # generate_cover_letters_log
        'N': 36,   # reviewer_feedback (3 inches)
        'O': 20,   # mailman_log
        'P': 25,   # process_feedback_log
        'Q': 25,   # reviewer_support_log
        'R': 15    # workflow_status
    }
    
    # Apply column widths and text wrapping
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width
        
        # Enable text wrapping for specific columns
        if col_letter in ['B', 'I', 'J', 'K', 'N']:  # Long text columns
            for row in ws.iter_rows(min_col=ord(col_letter)-64, max_col=ord(col_letter)-64):
                for cell in row:
                    cell.alignment = Alignment(wrap_text=True, vertical="top")
    
    # Special formatting for reviewer feedback column (N)
    feedback_col = 'N'
    for row in ws.iter_rows(min_col=14, max_col=14):  # Column N
        for cell in row:
            cell.font = Font(name="Liberation Sans")
            cell.alignment = Alignment(wrap_text=True, vertical="top")
```

#### E. New CLI Arguments
```python
# Add to argument parser
parser.add_argument("--feedback-system", action="store_true", 
                   help="Export in feedback system format with A-R columns")
parser.add_argument("--reviewer-name", default="xai",
                   help="Reviewer name for filename (default: xai)")
```

#### F. Modified Main Function
```python
def export_job_matches(output_format='excel', output_file=None, job_ids=None, 
                      feedback_system=False, reviewer_name="xai"):
    """
    Export job matching results to CSV or Excel format.
    
    Args:
        output_format: Format to export to ('csv' or 'excel') 
        output_file: Path to the output file. If None, a default name will be used.
        job_ids: List of specific job IDs to export
        feedback_system: If True, export in feedback system format with A-R columns
        reviewer_name: Name of reviewer for filename
        
    Returns:
        Path to the generated file
    """
    # Generate filename with feedback system format if requested
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if feedback_system:
            output_file = f"job_matches_{timestamp}.{output_format}"
        else:
            output_file = f"job_export_{timestamp}.{output_format}"
    
    # ... rest of existing logic ...
    
    # Use appropriate extraction method
    if feedback_system:
        matches = [
            {**extract_job_data_for_feedback_system(job_data),
             **initialize_logging_columns(timestamp)}
            for job_data in processed_jobs
        ]
        export_to_excel_feedback_system(matches, output_file)
    else:
        # Use existing logic for backward compatibility
        matches = [extract_matching_results(job_data) for job_data in processed_jobs]
        export_to_excel(matches, output_file)
```

---

## 📝 Script 2: `process_excel_cover_letters.py` Changes

### Current Functionality Analysis
- ✅ Reads Excel files with pandas
- ✅ Generates cover letters using template system
- ✅ Has configurable column names
- ✅ Uses existing cover letter infrastructure

### Required Changes

#### A. New Function: `update_excel_log_column()`
```python
def update_excel_log_column(excel_path, job_id, log_message, log_column='generate_cover_letters_log'):
    """
    Update the Excel file with logging information for cover letter generation.
    
    Args:
        excel_path: Path to the Excel file
        job_id: Job ID to update
        log_message: Message to log
        log_column: Column name to update (default: generate_cover_letters_log)
    """
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        
        # Find the row for this job_id
        job_row_idx = df[df['job_id'] == job_id].index
        
        if len(job_row_idx) > 0:
            # Update the log column
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.loc[job_row_idx[0], log_column] = f"{timestamp}: {log_message}"
            
            # Save back to Excel
            with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name='Job Matches', index=False)
            
            print(f"Updated log for job {job_id}: {log_message}")
        else:
            print(f"Warning: Job ID {job_id} not found in Excel file")
            
    except Exception as e:
        print(f"Error updating Excel log for job {job_id}: {e}")
```

#### B. Modified Main Function with Logging
```python
def main(excel_path, job_id_col='job_id', job_title_col='Position title', 
         narrative_col='Application narrative', output_dir=None, template_path=None,
         update_excel_log=True):
    """
    Process Excel file and generate cover letters with logging.
    
    Args:
        excel_path: Path to Excel file
        job_id_col: Column name for job ID
        job_title_col: Column name for job title  
        narrative_col: Column name for application narrative
        output_dir: Output directory for cover letters
        template_path: Path to cover letter template
        update_excel_log: Whether to update Excel with logging info
    """
    df = pd.read_excel(excel_path)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if output_dir is None:
        output_dir = os.path.join(script_dir, "docs", "cover_letters")
    
    if template_path is None:
        template_path = template_manager.find_best_template(script_dir, output_dir)
    
    profile = profile_manager.load_profile(script_dir)
    count = 0
    
    for idx, row in df.iterrows():
        job_id = str(row.get(job_id_col, '')).strip()
        job_title = str(row.get(job_title_col, '')).strip()
        narrative = str(row.get(narrative_col, '')).strip()
        
        # Determine if we should process this job
        match_level = str(row.get('Match level', '')).strip()
        should_process = (job_id and job_title and narrative and 
                         narrative.lower() != 'nan' and 
                         match_level.lower() == 'good')
        
        if should_process:
            print(f"Generating cover letter for job {job_id} ({job_title})...")
            
            # Generate cover letter (existing logic)
            job_details = {
                "job_id": job_id,
                "job_title": job_title,
                "reference_number": row.get("reference", ""),
                "company": profile.get("company", "Deutsche Bank AG"),
                "company_address": profile.get("company_address", "60262 Frankfurt"),
                "department": profile.get("department", ""),
                "primary_expertise_area": profile.get("primary_expertise_area", ""),
                "skill_area_1": profile.get("skill_area_1", ""),
                "skill_area_2": profile.get("skill_area_2", ""),
                "skill_bullets": "\n\n".join([
                    skill_library.get_available_skills().get("platform_management", ""),
                    skill_library.get_available_skills().get("data_analysis", "")
                ]),
                "specific_interest": narrative,
                "relevant_experience": profile.get("relevant_experience", ""),
                "relevant_understanding": profile.get("relevant_understanding", ""),
                "potential_contribution": profile.get("potential_contribution", ""),
                "value_proposition": profile.get("value_proposition", ""),
                "date": template_manager.format_date_german()
            }
            
            content = template_manager.generate_cover_letter(template_path, job_details)
            
            if content:
                # Save cover letter with feedback system naming convention
                cover_letter_filename = f"cover_letter_{job_id}.md"
                cover_letter_path = os.path.join(output_dir, cover_letter_filename)
                
                template_manager.save_cover_letter(content, job_id, job_title, output_dir)
                count += 1
                
                # Update Excel log
                if update_excel_log:
                    update_excel_log_column(excel_path, job_id, 
                                          f"Cover letter generated: {cover_letter_filename}")
                
                print(f"Generated: {cover_letter_filename}")
            else:
                print(f"Failed to generate cover letter for job {job_id}")
                if update_excel_log:
                    update_excel_log_column(excel_path, job_id, "Cover letter generation failed")
        else:
            # Log why we skipped this job
            if job_id and update_excel_log:
                if match_level.lower() != 'good':
                    update_excel_log_column(excel_path, job_id, 
                                          f"Skipped: Match level is '{match_level}', not 'Good'")
                else:
                    update_excel_log_column(excel_path, job_id, 
                                          "Skipped: Missing narrative or job details")
            
            print(f"Skipping row {idx}: job_id={job_id}, match_level={match_level}")
    
    print(f"Done. Generated {count} cover letters.")
    return count
```

#### C. New CLI Arguments
```python
# Add to argument parser
parser.add_argument("--job-title-col", default="Position title", 
                   help="Column name for job title (default: Position title)")
parser.add_argument("--narrative-col", default="Application narrative", 
                   help="Column name for application narrative (default: Application narrative)")
parser.add_argument("--no-excel-log", action="store_true",
                   help="Don't update Excel file with logging information")
```

#### D. Integration with Email System
```python
def email_cover_letters_to_reviewer(excel_path, cover_letter_dir, reviewer_email, reviewer_name="xai"):
    """
    Email the Excel file and generated cover letters to the reviewer.
    
    Args:
        excel_path: Path to the Excel file
        cover_letter_dir: Directory containing generated cover letters
        reviewer_email: Email address of the reviewer
        reviewer_name: Name of the reviewer
    """
    try:
        # Import email sender
        from email_sender import EmailSender, CONFIG
        
        # Prepare attachments
        attachments = [excel_path]
        
        # Add all generated cover letters
        cover_letter_files = glob.glob(os.path.join(cover_letter_dir, "cover_letter_*.md"))
        attachments.extend(cover_letter_files)
        
        # Prepare email
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = os.path.basename(excel_path)
        subject = f"{reviewer_name} {excel_filename}"
        
        body = f"""Hi {reviewer_name},

Attached are the job matches and cover letters for your review:

- Excel file: {excel_filename}
- {len(cover_letter_files)} cover letters generated for 'Good' matches

Please review the matches and add any feedback in the 'reviewer_feedback' column if needed.

Best regards,
Job Matching System
"""
        
        # Send email
        sender = EmailSender(CONFIG)
        success = sender.send_email(reviewer_email, subject, body, attachments)
        
        if success:
            print(f"Successfully emailed {len(attachments)} files to {reviewer_email}")
            return True
        else:
            print(f"Failed to email files to {reviewer_email}")
            return False
            
    except Exception as e:
        print(f"Error emailing files: {e}")
        return False
```

---

## 🔄 Integration Points

### A. Pipeline Integration
Both scripts should be callable from the main pipeline:

```python
# In pipeline_orchestrator.py
from export_job_matches import export_job_matches
from process_excel_cover_letters import main as process_cover_letters

# Step 7: Export Excel
excel_file = export_job_matches(
    output_format='excel',
    feedback_system=True,
    reviewer_name=args.reviewer_name
)

# Step 8: Generate cover letters
cover_letter_count = process_cover_letters(
    excel_path=excel_file,
    update_excel_log=True
)
```

### B. Backward Compatibility
Both scripts maintain their existing functionality:
- `export_job_matches.py` works as before without `--feedback-system` flag
- `process_excel_cover_letters.py` works as before without Excel logging

### C. Error Handling
- Graceful handling of missing columns
- Proper logging of failures
- Continue processing even if individual jobs fail

---

## 🎯 Implementation Priority

### Phase 1: Export Script Enhancement
1. Add A-R column structure to `export_job_matches.py`
2. Implement feedback system formatting
3. Add logging column initialization
4. Test Excel export with proper formatting

### Phase 2: Cover Letter Script Enhancement  
1. Add Excel logging functionality to `process_excel_cover_letters.py`
2. Implement match level filtering (only "Good" matches)
3. Add email integration capability
4. Test cover letter generation with logging

### Phase 3: Pipeline Integration
1. Integrate both scripts into pipeline orchestrator
2. Add proper CLI arguments
3. Test end-to-end Excel export → cover letter generation → email delivery
4. Validate logging column updates

This gives us a solid foundation for the feedback system while maintaining backward compatibility with existing functionality! 🚀