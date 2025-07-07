"""
JMFS Feedback Dispatcher Configuration
"""
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("jmfs.feedback_config")

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"

# Create necessary directories
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR / "excel_feedback" / "processed", exist_ok=True)
os.makedirs(DATA_DIR / "excel_feedback" / "temp", exist_ok=True)

# Feedback Dispatcher Configuration
FEEDBACK_DISPATCHER_CONFIG = {
    'llm_model': 'llama3.2:latest',
    'cover_letter_output_dir': str(DATA_DIR / "cover_letters"),
    'reviewer_email': 'gershon.pollatschek@db.com',
    'auto_update_prompts': False,
    'chat_interface_url': 'mailto:support@jobmatcher.com',
}

# Mailman Service Configuration
MAILMAN_CONFIG = {
    'gmail_user': 'gershele@gmail.com',
    'reviewer_configs': {
        'xai': {
            'email': 'gershon.pollatschek@db.com',
            'name': 'xai'
        }
    },
    'credentials_file': str(CONFIG_DIR / "credentials.json"),
    'token_file': str(CONFIG_DIR / "token.pickle"),
    'processed_log_file': str(LOGS_DIR / "processed_emails.json"),
    'temp_excel_dir': str(DATA_DIR / "excel_feedback" / "temp"),
    'processed_excel_dir': str(DATA_DIR / "excel_feedback" / "processed"),
    'max_emails_per_scan': 50
}

def get_config():
    """Get the full JMFS feedback system configuration."""
    # Add any runtime configuration logic here
    return {
        'feedback_dispatcher': FEEDBACK_DISPATCHER_CONFIG,
        'mailman': MAILMAN_CONFIG,
    }
