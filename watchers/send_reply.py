#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send Email Reply - Sends email replies via Gmail API.

Usage:
    python send_reply.py <to_email> <subject> <body> [in_reply_to]
    
Example:
    python send_reply.py "client@example.com" "Re: Invoice" "Dear Client..." "gmail_msg_123"
"""

import sys
import base64
from pathlib import Path
from email.mime.text import MIMEText
from datetime import datetime

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    print("Google auth not installed. Run: pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)


class GmailSender:
    """Send emails via Gmail API."""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, token_path: str = None):
        """
        Initialize Gmail sender.
        
        Args:
            token_path: Path to OAuth token file (default: watchers/token.json)
        """
        if token_path:
            self.token_path = Path(token_path)
        else:
            self.token_path = Path(__file__).parent / 'token.json'
        
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        if not self.token_path.exists():
            raise FileNotFoundError(
                f'OAuth token not found at {self.token_path}\n'
                'Run gmail_watcher.py first to authenticate.'
            )
        
        creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        service = build('gmail', 'v1', credentials=creds)
        return service
    
    def send_email(self, to: str, subject: str, body: str, 
                   in_reply_to: str = None, cc: str = None) -> dict:
        """
        Send email via Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            in_reply_to: Message ID to reply to (optional)
            cc: CC recipient (optional)
            
        Returns:
            Gmail message dict with 'id' key
        """
        # Create message
        message = MIMEText(body)
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject
        
        if in_reply_to:
            message['In-Reply-To'] = in_reply_to
            message['References'] = in_reply_to
        
        if cc:
            message['Cc'] = cc
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send
        try:
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f'✅ Email sent successfully!')
            print(f'   Message ID: {sent_message["id"]}')
            print(f'   To: {to}')
            print(f'   Subject: {subject}')
            
            return sent_message
            
        except Exception as e:
            print(f'❌ Error sending email: {e}')
            raise
    
    def send_reply(self, original_email_file: str, reply_body: str) -> dict:
        """
        Send reply to an email from action file.
        
        Args:
            original_email_file: Path to EMAIL_*.md action file
            reply_body: Reply content
            
        Returns:
            Gmail message dict
        """
        # Parse action file
        content = Path(original_email_file).read_text(encoding='utf-8')
        
        # Extract email details
        import re
        
        def extract_field(pattern, text):
            match = re.search(pattern, text)
            return match.group(1) if match else None
        
        # Extract from frontmatter
        from_match = extract_field(r'from: "([^"]+)"', content)
        subject_match = extract_field(r'subject: "([^"]+)"', content)
        msg_id = extract_field(r'message_id: "([^"]+)"', content)
        
        if not from_match or not subject_match:
            raise ValueError('Could not extract email details from action file')
        
        # Create reply subject
        reply_subject = subject_match
        if not reply_subject.lower().startswith('re:'):
            reply_subject = f'Re: {subject_match}'
        
        # Send reply
        return self.send_email(
            to=from_match,
            subject=reply_subject,
            body=reply_body,
            in_reply_to=msg_id
        )


def main():
    """Main entry point."""
    if len(sys.argv) < 4:
        print("Usage: python send_reply.py <to_email> <subject> <body> [in_reply_to]")
        print("\nExample:")
        print('  python send_reply.py "client@example.com" "Re: Invoice" "Dear Client..." "gmail_msg_123"')
        sys.exit(1)
    
    to_email = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    in_reply_to = sys.argv[4] if len(sys.argv) > 4 else None
    
    try:
        sender = GmailSender()
        sender.send_email(to_email, subject, body, in_reply_to)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\nTo authenticate, run:")
        print("  python gmail_watcher.py ..\\AI_Employee_Vault")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
