"""
Mailman Service for JMFS: Monitors Gmail inbox for returned Excel feedback files and triggers feedback processing.
"""
import argparse
import os
import time
import json
import base64
from typing import List, Dict, Any

from googleapiclient.discovery import build #type: ignore
from googleapiclient.errors import HttpError #type: ignore
from googleapiclient.http import MediaIoBaseDownload #type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow #type: ignore
from google.auth.transport.requests import Request
import pickle
import io

# Placeholder for Gmail API authentication and helpers
# from run_pipeline.email_sender import get_gmail_service

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

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

class MailmanService:
    def __init__(self, config):
        self.config = config
        self.gmail_service = self._get_gmail_service()
        self.processed_emails = self._load_processed_log()

    def _get_gmail_service(self):
        creds = None
        if os.path.exists(self.config['token_file']):
            with open(self.config['token_file'], 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config['credentials_file'], SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.config['token_file'], 'wb') as token:
                pickle.dump(creds, token)
        return build('gmail', 'v1', credentials=creds)

    def scan_for_feedback_emails(self, reviewer_name="xai") -> List[Dict[str, Any]]:
        reviewer_email = self.config['reviewer_configs'][reviewer_name]['email']
        query = f'from:{reviewer_email} has:attachment filename:xlsx'
        try:
            results = self.gmail_service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            feedback_emails = []
            for msg in messages:
                msg_id = msg['id']
                if msg_id in self.processed_emails:
                    continue
                msg_data = self.gmail_service.users().messages().get(userId='me', id=msg_id).execute()
                feedback_emails.append(msg_data)
            return feedback_emails
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def extract_excel_from_email(self, email_data) -> str:
        msg_id = email_data['id']
        for part in email_data.get('payload', {}).get('parts', []):
            if part['filename'].endswith('.xlsx'):
                att_id = part['body'].get('attachmentId')
                if att_id:
                    att = self.gmail_service.users().messages().attachments().get(userId='me', messageId=msg_id, id=att_id).execute()
                    data = att['data']
                    file_data = io.BytesIO(base64.urlsafe_b64decode(data))
                    out_path = os.path.join(self.config['temp_excel_dir'], f'{msg_id}_{part["filename"]}')
                    os.makedirs(self.config['temp_excel_dir'], exist_ok=True)
                    with open(out_path, 'wb') as f:
                        f.write(file_data.read())
                    return out_path
        return ""

    def process_feedback_email(self, email_data, excel_path):
        msg_id = email_data['id']
        # Call feedback dispatcher
        try:
            import subprocess
            result = subprocess.run([
                'python',
                os.path.join(os.path.dirname(__file__), 'feedback_dispatcher.py'),
                '--excel', excel_path,
                '--reviewer', self.config['reviewer_configs']['xai']['name']
            ], capture_output=True, text=True)
            status = 'success' if result.returncode == 0 else 'error'
            output = result.stdout + result.stderr
        except Exception as e:
            status = 'error'
            output = str(e)
        self.processed_emails.add(msg_id)
        self._save_processed_log()
        return {'msg_id': msg_id, 'excel_path': excel_path, 'status': status, 'output': output}

    def scan_and_process(self, reviewer_name="xai"):
        emails = self.scan_for_feedback_emails(reviewer_name)
        results = []
        for email in emails:
            excel_path = self.extract_excel_from_email(email)
            if excel_path:
                result = self.process_feedback_email(email, excel_path)
                results.append(result)
        return results

    def _load_processed_log(self):
        log_path = self.config['processed_log_file']
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                return set(json.load(f))
        return set()

    def _save_processed_log(self):
        log_path = self.config['processed_log_file']
        with open(log_path, 'w') as f:
            json.dump(list(self.processed_emails), f)

def run_daemon(mailman, interval, reviewer):
    print(f"[Mailman] Running in daemon mode, checking every {interval} minutes...")
    while True:
        mailman.scan_and_process(reviewer)
        time.sleep(interval * 60)

def main():
    parser = argparse.ArgumentParser(description="Mailman service for processing feedback emails")
    parser.add_argument("--scan-once", action="store_true", help="Scan once and exit")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon, check every N minutes")
    parser.add_argument("--interval", type=int, default=15, help="Check interval in minutes (daemon mode)")
    parser.add_argument("--reviewer", default="xai", help="Reviewer name to scan for")
    args = parser.parse_args()

    mailman = MailmanService(MAILMAN_CONFIG)

    if args.daemon:
        run_daemon(mailman, args.interval, args.reviewer)
    else:
        process_results = mailman.scan_and_process(args.reviewer)
        print(f"Processed {len(process_results)} feedback emails")

if __name__ == "__main__":
    main()
