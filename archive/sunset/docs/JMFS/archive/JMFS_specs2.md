# Feedback System Component Specifications

## 🎯 Overview
We need two new components to complete our JMFS:
1. **Mailman Service** - Detects and processes returned Excel files from reviewers
2. **Feedback Dispatcher** - LLM-powered coordinator that routes feedback to specialized workers

---

## 📧 Component 1: Mailman Service

### Purpose
Monitor Gmail inbox for returned Excel files from reviewers and trigger feedback processing.

### Location
`run_pipeline/core/mailman_service.py`

### Core Functionality

#### A. Email Detection
```python
class MailmanService:
    def __init__(self, config):
        self.config = config
        self.gmail_service = self._authenticate_gmail()
        self.processed_emails = self._load_processed_log()
    
    def scan_for_feedback_emails(self, reviewer_name="xai"):
        """
        Scan Gmail inbox for emails from reviewer with Excel attachments.
        
        Args:
            reviewer_name: Name of reviewer to look for in subject
            
        Returns:
            List of unprocessed feedback emails
        """
        # Search for emails with:
        # - Subject containing reviewer_name and "job_matches_YYYYMMDD_HHMMSS.xlsx"
        # - From reviewer's email address
        # - Has Excel attachment
        # - Not already processed (check against log)
```

#### B. Excel Extraction
```python
    def extract_excel_from_email(self, email_data):
        """
        Download Excel attachment from email.
        
        Args:
            email_data: Gmail API email data
            
        Returns:
            Path to downloaded Excel file or None
        """
        # Download attachment to temp directory
        # Validate it's the expected Excel format
        # Return path for processing
```

#### C. Processing Trigger
```python
    def process_feedback_email(self, email_data, excel_path):
        """
        Process a feedback email by triggering the Feedback Dispatcher.
        
        Args:
            email_data: Gmail API email data
            excel_path: Path to extracted Excel file
            
        Returns:
            Processing results
        """
        # Log email receipt in Excel column O
        # Trigger Feedback Dispatcher with Excel path
        # Update processed emails log
        # Move Excel to proper processing directory
```

#### D. Configuration Integration
```python
# Use existing email_sender.py OAuth2 setup
MAILMAN_CONFIG = {
    'gmail_user': 'gershele@gmail.com',
    'reviewer_configs': {
        'xai': {
            'email': 'gershon.pollatschek@db.com',
            'name': 'xai'
        }
    },
    'credentials_file': '../config/credentials.json',
    'token_file': '../config/token.pickle',
    'processed_log_file': '../logs/processed_emails.json',
    'temp_excel_dir': '../temp/excel_feedback',
    'processed_excel_dir': '../data/excel_feedback'
}
```

#### E. CLI Interface
```python
def main():
    parser = argparse.ArgumentParser(description="Mailman service for processing feedback emails")
    parser.add_argument("--scan-once", action="store_true", help="Scan once and exit")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon, check every N minutes")
    parser.add_argument("--interval", type=int, default=15, help="Check interval in minutes (daemon mode)")
    parser.add_argument("--reviewer", default="xai", help="Reviewer name to scan for")
    args = parser.parse_args()
    
    mailman = MailmanService(MAILMAN_CONFIG)
    
    if args.daemon:
        # Run continuously, checking every N minutes
        run_daemon(mailman, args.interval, args.reviewer)
    else:
        # Scan once and process any found emails
        process_results = mailman.scan_and_process(args.reviewer)
        print(f"Processed {len(process_results)} feedback emails")
```

---

## 🧠 Component 2: Feedback Dispatcher

### Purpose
LLM-powered coordinator that analyzes returned Excel files and routes jobs to specialized LLM workers.

### Location
`run_pipeline/core/feedback_dispatcher.py`

### Core Functionality

#### A. Master Analysis
```python
class FeedbackDispatcher:
    def __init__(self, config):
        self.config = config
        self.llm_client = get_llm_client(model="llama3.2:latest")
    
    def analyze_excel_feedback(self, excel_path):
        """
        Master LLM analyzes Excel file and determines actions needed.
        
        Args:
            excel_path: Path to Excel file with reviewer feedback
            
        Returns:
            Dictionary of actions to take for each job
        """
        # Read Excel file
        # Extract jobs with feedback in column N
        # Send to Master LLM for routing decisions
        # Return structured action plan
```

#### B. Master LLM Prompt
```python
DISPATCHER_PROMPT = """
You are a Feedback Dispatcher coordinating a job matching system. 
You receive Excel files with reviewer feedback and decide what actions to take.

Analyze this Excel data and determine what needs to be done for each job with feedback:

Excel Data:
{excel_data}

For each job with feedback, determine the action type:
1. GENERATE_COVER_LETTER: False negative, reviewer says they ARE qualified
2. RESOLVE_CONFLICT: Contradictory feedback vs. previous assessment
3. CLARIFY_GIBBERISH: Feedback is unclear or nonsensical
4. PROCESS_LEARNING: Valid feedback for system improvement
5. IGNORE: Feedback is empty or clearly not actionable

Output format (JSON):
{
  "actions": [
    {
      "job_id": "12345",
      "action_type": "GENERATE_COVER_LETTER",
      "feedback_text": "reviewer feedback text",
      "reasoning": "why this action was chosen",
      "priority": "high|medium|low"
    }
  ],
  "summary": "Brief summary of what was found"
}
"""
```

#### C. Action Router
```python
    def dispatch_actions(self, action_plan):
        """
        Route actions to specialized LLM workers.
        
        Args:
            action_plan: Dictionary from analyze_excel_feedback
            
        Returns:
            Results from all dispatched actions
        """
        results = []
        
        for action in action_plan['actions']:
            if action['action_type'] == 'GENERATE_COVER_LETTER':
                result = self._handle_cover_letter_generation(action)
            elif action['action_type'] == 'RESOLVE_CONFLICT':
                result = self._handle_conflict_resolution(action)
            elif action['action_type'] == 'CLARIFY_GIBBERISH':
                result = self._handle_gibberish_clarification(action)
            elif action['action_type'] == 'PROCESS_LEARNING':
                result = self._handle_learning_feedback(action)
            else:
                result = self._handle_ignore(action)
            
            results.append(result)
        
        return results
```

#### D. Specialized LLM Workers

##### Cover Letter Generator Worker
```python
    def _handle_cover_letter_generation(self, action):
        """Generate cover letter for false negative."""
        # Load job data
        # Use existing cover letter generation system
        # Email cover letter to reviewer
        # Log in Excel column P
        
        prompt = f"""
        Generate a cover letter for this job since the reviewer indicated they ARE qualified:
        
        Job ID: {action['job_id']}
        Reviewer Feedback: {action['feedback_text']}
        Job Details: {job_details}
        CV: {cv_text}
        
        Create a professional cover letter highlighting the qualifications the reviewer mentioned.
        """
```

##### Conflict Resolver Worker
```python
    def _handle_conflict_resolution(self, action):
        """Handle contradictory feedback."""
        # Check previous feedback for this job/user
        # Generate evidence-based clarification email
        # Log in Excel column Q
        
        prompt = f"""
        Create a polite clarification email for contradictory feedback:
        
        Current Feedback: {action['feedback_text']}
        Previous Assessment: {previous_assessment}
        Evidence from CV: {cv_evidence}
        
        Write an email that says: "You told us X before and Y now. We think Z because of evidence A, B, C from your CV. Please let us know if this is incorrect, otherwise we'll proceed with our assessment."
        """
```

##### Gibberish Clarification Worker
```python
    def _handle_gibberish_clarification(self, action):
        """Handle unclear feedback."""
        # Generate friendly clarification email
        # Include link to online chat interface
        # Log in Excel column Q
        
        prompt = f"""
        Create a friendly clarification email for unclear feedback:
        
        Unclear Feedback: {action['feedback_text']}
        Job: {job_title}
        
        Write a polite email asking for clarification: "Hey, could you clarify what you meant by '[feedback]'? We want to make sure we understand your assessment correctly. You can also click this link to chat with us directly: [chat_link]"
        """
```

##### Learning Processor Worker
```python
    def _handle_learning_feedback(self, action):
        """Process feedback for system learning."""
        # Use existing feedback_handler.py integration
        # Update prompt system based on feedback patterns
        # Log learning updates in Excel column P
        
        # This integrates with your existing feedback system
        from run_pipeline.job_matcher.feedback_handler import analyze_feedback, update_prompt_based_on_feedback
```

#### E. Excel Logging Integration
```python
    def update_excel_logs(self, excel_path, job_results):
        """
        Update Excel file with processing results.
        
        Args:
            excel_path: Path to Excel file
            job_results: Results from dispatched actions
        """
        # Read Excel file
        # Update columns P, Q based on actions taken
        # Update column R (workflow_status) to "Feedback Processed"
        # Save Excel file
```

#### F. Email Integration
```python
    def send_clarification_emails(self, clarification_actions):
        """
        Send clarification emails using existing email_sender.py infrastructure.
        
        Args:
            clarification_actions: List of clarification actions to send
        """
        # Use existing EmailSender class
        # Send personalized emails based on action type
        # Track sent emails in Excel logs
```

---

## 🔧 Integration Specifications

### A. Pipeline Integration
```python
# In pipeline_orchestrator.py - new optional step
def run_feedback_processing_step(args):
    """Step 10: Process feedback from returned Excel files"""
    if not args.enable_feedback_processing:
        return True
    
    logger.info("Step 10/10: Processing returned Excel feedback...")
    
    # Run mailman to check for new feedback
    mailman = MailmanService(MAILMAN_CONFIG)
    feedback_emails = mailman.scan_and_process(args.reviewer_name)
    
    # Process any found feedback with dispatcher
    dispatcher = FeedbackDispatcher(FEEDBACK_DISPATCHER_CONFIG)
    for email_result in feedback_emails:
        if email_result['excel_path']:
            dispatcher.process_feedback_file(email_result['excel_path'])
    
    return True
```

### B. Configuration
```python
FEEDBACK_DISPATCHER_CONFIG = {
    'llm_model': 'llama3.2:latest',
    'cover_letter_output_dir': '../docs/cover_letters',
    'chat_interface_url': 'https://your-chat-interface.com',
    'email_sender_config': CONFIG,  # Reuse from email_sender.py
    'max_actions_per_batch': 10,
    'specialized_models': {
        'cover_letter_generator': 'llama3.2:latest',
        'conflict_resolver': 'llama3.2:latest', 
        'clarification_writer': 'llama3.2:latest',
        'learning_processor': 'llama3.2:latest'
    }
}
```

### C. CLI Interface
```python
def main():
    parser = argparse.ArgumentParser(description="Feedback Dispatcher for processing reviewer feedback")
    parser.add_argument("--excel-file", help="Process specific Excel file")
    parser.add_argument("--scan-and-process", action="store_true", help="Scan for new emails and process")
    parser.add_argument("--reviewer", default="xai", help="Reviewer name")
    parser.add_argument("--dry-run", action="store_true", help="Analyze but don't take actions")
    args = parser.parse_args()
    
    dispatcher = FeedbackDispatcher(FEEDBACK_DISPATCHER_CONFIG)
    
    if args.excel_file:
        # Process specific Excel file
        dispatcher.process_feedback_file(args.excel_file, dry_run=args.dry_run)
    elif args.scan_and_process:
        # Scan for emails and process any found
        mailman = MailmanService(MAILMAN_CONFIG)
        feedback_emails = mailman.scan_and_process(args.reviewer)
        
        for email_result in feedback_emails:
            if email_result['excel_path']:
                dispatcher.process_feedback_file(email_result['excel_path'], dry_run=args.dry_run)
    else:
        parser.print_help()
```

---

## 🚨 Error Handling & Wetbrain-Proofing

### A. Graceful Failures
- If Ollama is down, log error and continue with next job
- If email sending fails, queue for retry
- If Excel is corrupted, log error and notify admin
- If reviewer sends same Excel twice, detect and handle gracefully

### B. Logging Strategy
- All LLM interactions logged using existing `logging_llm_client.py`
- All email operations logged with timestamps
- All Excel updates tracked with before/after states
- Failed operations queued for manual review

### C. Wetbrain Scenarios
- **Reviewer sends wrong Excel**: Validate filename format, reject politely
- **Reviewer gives contradictory feedback multiple times**: Escalate to "we'll do what we want" mode
- **Reviewer never responds to clarifications**: Set timeout and proceed with system assessment
- **Excel has random data corruption**: Validate structure, extract what's possible

---

## 🎯 Implementation Priority

### Week 1: Mailman Service
1. Gmail integration using existing OAuth2 setup
2. Email detection and Excel extraction  
3. Basic processing trigger
4. CLI interface and testing

### Week 2: Feedback Dispatcher Core
1. Master LLM analysis system
2. Action routing logic
3. Excel logging integration
4. Basic specialized workers

### Week 3: Specialized Workers
1. Cover letter generation integration
2. Conflict resolution emails
3. Gibberish clarification system
4. Learning processor integration

### Week 4: Integration & Testing
1. Pipeline integration (Step 10)
2. End-to-end testing
3. Error handling and logging
4. Wetbrain scenario testing

---

## 💡 Key Design Decisions

### A. Reuse Existing Infrastructure
- **Gmail OAuth2**: Use existing `email_sender.py` setup
- **LLM Client**: Use existing `llm_client.py` and `logging_llm_client.py`
- **Cover Letters**: Integrate with existing cover letter generation system
- **Feedback Learning**: Use existing `feedback_handler.py`

### B. LLM Model Strategy
- **Single Model**: Use `llama3.2:latest` for all tasks (can be specialized later)
- **Temperature Settings**: Vary by task (creative vs. analytical)
- **Prompt Engineering**: Structured prompts with clear output formats
- **Error Handling**: Fallback to mock responses if Ollama unavailable

### C. Data Flow
- **Excel as Single Source of Truth**: All logging goes back to Excel
- **Email as Delivery Mechanism**: All communications via email
- **File-Based Processing**: No databases, just Excel and JSON logs
- **Idempotent Operations**: Can re-run safely without duplicating work

This gives you comprehensive specs for both components! The beautiful part is how they integrate with your existing infrastructure while adding the LLM-powered intelligence to handle all the wetbrain scenarios we discussed. 🚀