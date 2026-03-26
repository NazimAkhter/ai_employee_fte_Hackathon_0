#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitors Gmail for new important/unread emails.

When new emails are detected, creates action files in the Obsidian vault's
/Needs_Action folder for processing by Qwen Code.

Usage:
    python gmail_watcher.py <vault_path> [credentials_path] [check_interval]
    
Example:
    python gmail_watcher.py "C:/Users/Name/ObsidianVault" "C:/Users/Name/credentials.json" 30
"""

import sys
import os
import base64
from pathlib import Path
from datetime import datetime

# Import base class
from base_watcher import BaseWatcher

# Gmail API imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new important/unread emails and creates action items.
    """

    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.send',
              'https://www.googleapis.com/auth/gmail.modify']

    def __init__(self, vault_path: str, credentials_path: str = None, check_interval: int = 60):
        """
        Initialize the Gmail watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            credentials_path: Path to Gmail credentials JSON (default: credentials.json in project root)
            check_interval: Seconds between checks (default: 60)
        """
        super().__init__(vault_path, check_interval)
        
        # Set credentials path
        if credentials_path:
            self.credentials_path = Path(credentials_path)
        else:
            # Default to credentials.json in project root
            self.credentials_path = Path(__file__).parent.parent / 'credentials.json'
        
        # Token file for OAuth
        self.token_path = Path(__file__).parent / 'token.json'
        
        # Keywords for priority detection
        self.priority_keywords = ['urgent', 'asap', 'invoice', 'payment', 'receipt', 
                                   'contract', 'agreement', 'help', 'important']
        
        # Track processed message IDs
        self.processed_ids = set()
        
        # Load processed IDs from file if exists
        self._load_processed_ids()
        
        # Initialize Gmail service
        self.service = self._authenticate_gmail()
        
        self.logger.info(f'Gmail credentials: {self.credentials_path}')
        self.logger.info(f'Gmail token: {self.token_path}')

    def _authenticate_gmail(self):
        """
        Authenticate with Gmail API using OAuth 2.0.
        
        Returns:
            Gmail API service object
        """
        creds = None
        
        # Load existing token if available
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
                self.logger.info('Loaded existing OAuth token')
            except Exception as e:
                self.logger.warning(f'Could not load token: {e}')
                self.token_path.unlink(missing_ok=True)
                creds = None
        
        # Refresh token if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self.logger.info('Refreshed OAuth token')
            except Exception as e:
                self.logger.warning(f'Could not refresh token: {e}')
                creds = None
        
        # Run OAuth flow if no valid credentials
        if not creds or not creds.valid:
            if not self.credentials_path.exists():
                raise FileNotFoundError(
                    f'Gmail credentials not found at {self.credentials_path}\n'
                    f'Please create a credentials.json file from Google Cloud Console.'
                )
            
            self.logger.info('Starting OAuth flow...')
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0, open_browser=False)
                
                # Save token for future use
                self.token_path.write_text(creds.to_json())
                self.logger.info(f'OAuth token saved to {self.token_path}')
            except Exception as e:
                self.logger.error(f'OAuth flow failed: {e}')
                raise
        
        # Build Gmail service
        try:
            service = build('gmail', 'v1', credentials=creds)
            self.logger.info('Gmail service initialized')
            return service
        except Exception as e:
            self.logger.error(f'Could not build Gmail service: {e}')
            raise

    def _load_processed_ids(self):
        """Load previously processed message IDs from cache file."""
        cache_file = Path(__file__).parent / 'gmail_processed_cache.txt'
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.processed_ids = set(line.strip() for line in f if line.strip())
                self.logger.info(f'Loaded {len(self.processed_ids)} processed message IDs from cache')
            except Exception as e:
                self.logger.warning(f'Could not load processed IDs cache: {e}')

    def _save_processed_ids(self):
        """Save processed message IDs to cache file."""
        cache_file = Path(__file__).parent / 'gmail_processed_cache.txt'
        try:
            with open(cache_file, 'w') as f:
                for msg_id in self.processed_ids:
                    f.write(f'{msg_id}\n')
        except Exception as e:
            self.logger.warning(f'Could not save processed IDs cache: {e}')

    def check_for_updates(self) -> list:
        """
        Check for new unread/important emails in Gmail.
        
        Returns:
            List of new message IDs
        """
        try:
            # Search for unread, important messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed messages
            new_messages = [m for m in messages if m['id'] not in self.processed_ids]
            
            if new_messages:
                self.logger.info(f'Found {len(new_messages)} new messages')
            
            return new_messages
            
        except HttpError as error:
            self.logger.error(f'Gmail API error: {error}')
            return []
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            return []

    def create_action_file(self, message: dict) -> Path:
        """
        Create a markdown action file for the email.
        
        Args:
            message: Gmail message dict with 'id' key
            
        Returns:
            Path to created action file
        """
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me', 
                id=message['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            
            from_email = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            to_email = headers.get('To', '')
            date = headers.get('Date', '')
            
            # Extract body
            body = self._extract_body(msg)
            
            # Detect priority
            priority = self._detect_priority(subject, body, from_email)
            
            # Check if from new sender
            is_new_sender = self._is_new_sender(from_email)
            
            # Generate frontmatter
            frontmatter = f'''---
type: email
from: "{from_email}"
to: "{to_email}"
subject: "{subject}"
date: "{date}"
received: {datetime.now().isoformat()}
priority: "{priority}"
message_id: "{message['id']}"
is_new_sender: {str(is_new_sender).lower()}
status: pending
---'''
            
            # Generate suggested actions
            actions = self._suggest_actions(subject, body, priority, is_new_sender)
            
            # Create content
            content = f'''{frontmatter}

# 📧 Email Received

**From:** {from_email}  
**To:** {to_email}  
**Subject:** {subject}  
**Date:** {date}  
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Priority:** {"🔴" if priority == 'high' else '🟡' if priority == 'medium' else '🟢'} {priority.title()}
{"**New Sender:** ⚠️ Yes - Approval required before replying" if is_new_sender else ''}

---

## 📋 Email Content

{body if body else '*No content extracted*'}

---

## ✅ Suggested Actions

{actions}

---

## 📝 Notes

<!-- Add any notes about this email here -->

---

## 🔗 Gmail Link

[View in Gmail](https://mail.google.com/mail/u/0/#inbox/{message['id']})

---

*Action file created by Gmail Watcher at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
'''
            
            # Generate unique filename
            safe_subject = self._sanitize_filename(subject)[:40]
            action_filepath = self.get_unique_filename(f'EMAIL_{safe_subject}')
            
            # Write action file
            action_filepath.write_text(content, encoding='utf-8')
            
            # Mark as processed
            self.processed_ids.add(message['id'])
            self._save_processed_ids()
            
            # Mark as read in Gmail
            self._mark_as_read(message['id'])
            
            self.logger.info(f'Created action file for email: {subject}')
            
            return action_filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise

    def _extract_body(self, msg: dict) -> str:
        """
        Extract the plain text body from a Gmail message.
        
        Args:
            msg: Full Gmail message dict
            
        Returns:
            Plain text body
        """
        try:
            parts = msg['payload'].get('parts', [])
            body_data = msg['payload'].get('body', {})
            
            # Try to find plain text part
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    body_data = part['body']
                    break
            
            # Decode body
            if 'data' in body_data:
                body = base64.urlsafe_b64decode(body_data['data']).decode('utf-8')
                return body[:2000]  # Limit length
            
            # Try HTML if no plain text
            for part in parts:
                if part['mimeType'] == 'text/html':
                    body_data = part['body']
                    if 'data' in body_data:
                        html = base64.urlsafe_b64decode(body_data['data']).decode('utf-8')
                        # Simple HTML to text conversion
                        import re
                        text = re.sub('<[^<]+?>', '', html)
                        return text[:2000]
            
            return ''
            
        except Exception as e:
            self.logger.warning(f'Could not extract body: {e}')
            return msg.get('snippet', '')

    def _detect_priority(self, subject: str, body: str, from_email: str) -> str:
        """
        Detect email priority based on content.
        
        Args:
            subject: Email subject
            body: Email body
            from_email: Sender email
            
        Returns:
            Priority level: 'high', 'medium', or 'normal'
        """
        text = f'{subject} {body}'.lower()
        
        # High priority keywords
        if any(kw in text for kw in self.priority_keywords):
            return 'high'
        
        # Check for urgent sender domains
        urgent_domains = ['boss', 'ceo', 'client', 'customer']
        if any(d in from_email.lower() for d in urgent_domains):
            return 'high'
        
        # Medium priority indicators
        medium_keywords = ['meeting', 'schedule', 'deadline', 'review', 'update']
        if any(kw in text for kw in medium_keywords):
            return 'medium'
        
        return 'normal'

    def _is_new_sender(self, from_email: str) -> bool:
        """
        Check if this is a new sender (not in processed emails).
        
        Args:
            from_email: Sender email address
            
        Returns:
            True if new sender
        """
        # Extract email domain for trusted domains
        trusted_domains = ['gmail.com', 'company.com']  # Add your trusted domains
        
        # For now, consider all senders as potentially new
        # In production, maintain a database of known senders
        return True

    def _suggest_actions(self, subject: str, body: str, priority: str, is_new_sender: bool) -> str:
        """
        Suggest actions based on email content.
        
        Args:
            subject: Email subject
            body: Email body
            priority: Priority level
            is_new_sender: Whether sender is new
            
        Returns:
            Markdown list of suggested actions
        """
        suggestions = []
        text = f'{subject} {body}'.lower()
        
        # New sender requires approval
        if is_new_sender:
            suggestions.append('- [ ] **Create approval request** before replying (new sender)')
        
        # Invoice/payment related
        if any(kw in text for kw in ['invoice', 'payment', 'bill', 'receipt']):
            suggestions.append('- [ ] Review invoice/payment details')
            suggestions.append('- [ ] Extract amount and due date')
            suggestions.append('- [ ] Create accounting entry')
            suggestions.append('- [ ] Schedule payment if approved')
        
        # Meeting related
        if any(kw in text for kw in ['meeting', 'schedule', 'calendar', 'appointment']):
            suggestions.append('- [ ] Check calendar availability')
            suggestions.append('- [ ] Respond with available times')
            suggestions.append('- [ ] Add to calendar once confirmed')
        
        # Urgent/ASAP
        if any(kw in text for kw in ['urgent', 'asap', 'emergency', 'immediate']):
            suggestions.append('- [ ] **Process immediately** (urgent)')
            suggestions.append('- [ ] Determine required response time')
            suggestions.append('- [ ] Escalate if needed')
        
        # Default actions
        if not suggestions:
            suggestions.append('- [ ] Read and understand email')
            suggestions.append('- [ ] Draft appropriate response')
            if is_new_sender:
                suggestions.append('- [ ] Get approval before sending')
            suggestions.append('- [ ] Send response and archive')
        
        return '\n'.join(suggestions)

    def _sanitize_filename(self, text: str) -> str:
        """
        Sanitize text for use in filename.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove invalid filename characters
        invalid_chars = '<>:"/\\|？*'
        for char in invalid_chars:
            text = text.replace(char, '_')
        return text.strip()

    def _mark_as_read(self, message_id: str):
        """
        Mark a Gmail message as read.
        
        Args:
            message_id: Gmail message ID
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.debug(f'Marked message {message_id} as read')
        except Exception as e:
            self.logger.warning(f'Could not mark message as read: {e}')


def main():
    """Main entry point."""
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python gmail_watcher.py <vault_path> [credentials_path] [check_interval]")
        print("\nExample:")
        print('  python gmail_watcher.py "C:/Users/Name/ObsidianVault"')
        print('  python gmail_watcher.py "C:/Vault" "C:/credentials.json" 60')
        sys.exit(1)
    
    vault_path = sys.argv[1]
    credentials_path = sys.argv[2] if len(sys.argv) > 2 else None
    check_interval = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    
    # Validate vault path
    if not Path(vault_path).exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Create and run watcher
    try:
        watcher = GmailWatcher(vault_path, credentials_path, check_interval)
        print(f"📧 Gmail Watcher starting...")
        print(f"   Vault: {vault_path}")
        print(f"   Credentials: {watcher.credentials_path}")
        print(f"   Check Interval: {check_interval}s")
        print(f"\nPress Ctrl+C to stop\n")
        
        watcher.run()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\nTo get Gmail credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials")
        print("5. Download credentials.json")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
