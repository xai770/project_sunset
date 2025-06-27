#!/usr/bin/env python3
"""
Email Automation for Job Application Documents using Gmail OAuth2

This script sends newly created cover letters and job reviews from email account to work email,
with tracking to prevent resending previously sent documents.
"""
import os
import json
import glob
import pickle
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow #type: ignore
from googleapiclient.discovery import build #type: ignore
from google.auth.transport.requests import Request

# Configuration (update paths as needed for run_pipeline)
CONFIG = {
    'gmail_user': 'gershele@gmail.com',
    'work_email': 'gershon.pollatschek@db.com',
    'cover_letter_dir': os.path.join(os.path.dirname(__file__), '../docs/cover_letters'),
    'job_docs_dir': os.path.join(os.path.dirname(__file__), '../docs'),
    'sent_log_file': os.path.join(os.path.dirname(__file__), '../logs/sent_documents_log.json'),
    'send_all_ratings': True,
    'credentials_file': os.path.join(os.path.dirname(__file__), '../config/credentials.json'),
    'token_file': os.path.join(os.path.dirname(__file__), '../config/token.pickle'),
    'batch_send': True,
    'email_subject': 'DB Internal Role search'
}

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class EmailSender:
    def __init__(self, config):
        self.config = config
        self.email_user = self.config.get('gmail_user', '')
        self.credentials_file = self.config.get('credentials_file', 'credentials.json')
        self.token_file = self.config.get('token_file', 'token.pickle')
        if not self.email_user:
            print(f"ERROR: gmail_user not configured in CONFIG.")
        if not os.path.exists(self.credentials_file):
            print(f"ERROR: OAuth2 credentials file not found at {self.credentials_file}")

    def gmail_authenticate(self):
        creds = None
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        return build('gmail', 'v1', credentials=creds)

    def create_message(self, recipient, subject, body, attachments=None):
        message = MIMEMultipart()
        message['to'] = recipient
        message['from'] = self.email_user
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        if attachments:
            for attachment in attachments:
                with open(attachment, "rb") as file:
                    part = MIMEApplication(file.read(), Name=os.path.basename(attachment))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
                message.attach(part)
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def send_email(self, recipient, subject, body, attachments=None):
        try:
            service = self.gmail_authenticate()
            message = self.create_message(recipient, subject, body, attachments)
            sent_message = service.users().messages().send(userId="me", body=message).execute()
            print(f"Message sent successfully! Message ID: {sent_message['id']}")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def get_sent_documents(self):
        log_file = self.config.get('sent_log_file')
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error reading sent log file: {log_file}. Starting with empty log.")
                return []
        return []

    def update_sent_documents(self, sent_docs):
        log_file = self.config.get('sent_log_file')
        with open(log_file, 'w') as f:
            json.dump(sent_docs, f, indent=4)

    def find_cover_letters(self):
        cover_letter_dir = self.config.get('cover_letter_dir')
        return glob.glob(f"{cover_letter_dir}/*.md") + glob.glob(f"{cover_letter_dir}/*.docx")

    def find_job_documents(self):
        job_docs_dir = self.config.get('job_docs_dir')
        return glob.glob(f"{job_docs_dir}/*.docx") + glob.glob(f"{job_docs_dir}/*.md")

    def get_document_rating(self, filepath):
        return 5

    def process_documents(self):
        sent_docs = self.get_sent_documents()
        newly_sent = []
        unsent_documents = []
        cover_letters = self.find_cover_letters()
        for cover_letter in cover_letters:
            basename = os.path.basename(cover_letter)
            if basename not in sent_docs:
                unsent_documents.append(cover_letter)
                newly_sent.append(basename)
        job_docs = self.find_job_documents()
        for job_doc in job_docs:
            basename = os.path.basename(job_doc)
            if basename not in sent_docs:
                if not self.config.get('send_all_ratings', True):
                    rating = self.get_document_rating(job_doc)
                    if rating < 3:
                        continue
                unsent_documents.append(job_doc)
                newly_sent.append(basename)
        if unsent_documents:
            if self.config.get('batch_send', False):
                subject = self.config.get('email_subject', 'DB Internal Role search')
                body = f"Attached are {len(unsent_documents)} job application documents."
                print(f"Sending batch email with {len(unsent_documents)} documents...")
                if self.send_email(self.config['work_email'], subject, body, unsent_documents):
                    sent_docs.extend(newly_sent)
                    self.update_sent_documents(sent_docs)
                    print(f"Successfully sent {len(newly_sent)} new documents in a batch.")
                else:
                    print("Failed to send batch email.")
            else:
                successful_sends = 0
                for doc in unsent_documents:
                    basename = os.path.basename(doc)
                    if "cover_letter" in doc.lower() or doc.lower().endswith('.md'):
                        subject = f"Cover Letter: {Path(basename).stem}"
                        body = f"Attached is the cover letter: {Path(basename).stem}"
                    else:
                        subject = f"Job Document: {Path(basename).stem}"
                        body = f"Attached is the job document: {Path(basename).stem}"
                    if self.send_email(self.config['work_email'], subject, body, [doc]):
                        successful_sends += 1
                    else:
                        newly_sent.remove(basename)
                if successful_sends > 0:
                    sent_docs.extend(newly_sent)
                    self.update_sent_documents(sent_docs)
                    print(f"Successfully sent {successful_sends} new documents individually.")
                else:
                    print("Failed to send any documents.")
        else:
            print("No new documents to send.")
        return len(newly_sent)

def main():
    print(f"=== Job Application Email Automation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    sender = EmailSender(CONFIG)
    num_sent = sender.process_documents()
    print(f"Email automation completed. {num_sent} documents sent.")

if __name__ == "__main__":
    main()
