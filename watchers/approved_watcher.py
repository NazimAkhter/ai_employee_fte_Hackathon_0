#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Approved Email Watcher - Automatically monitors Approved folder and sends emails.

This script continuously monitors the /Approved folder for new approval files
and automatically sends emails via Gmail API when files are detected.

Usage:
    python approved_watcher.py [--vault-path "..\\AI_Employee_Vault"] [--interval 30]
"""

import sys
import time
import base64
import re
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    print("❌ Google auth not installed!")
    print("Run: pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)


class ApprovedEmailWatcher:
    """Watches Approved folder and sends emails automatically."""
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks (default: 30)
        """
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        self.check_interval = check_interval
        
        # Ensure folders exist
        self.approved_folder.mkdir(parents=True, exist_ok=True)
        self.done_folder.mkdir(parents=True, exist_ok=True)
        
        # Authenticate
        self.service = self._authenticate()
        
        # Track processed files
        self.processed_files = set()
        
        # Stats
        self.sent_count = 0
        self.error_count = 0
        
        # Setup logging
        import logging
        self.logger = logging.getLogger('ApprovedEmailWatcher')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        
        # Log file
        log_file = Path(__file__).parent / 'logs' / 'approved_watcher.log'
        log_file.parent.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        token_path = Path(__file__).parent / 'token.json'
        
        if not token_path.exists():
            raise FileNotFoundError(
                f'OAuth token not found at {token_path}\n'
                'Run: python gmail_watcher.py ..\\AI_Employee_Vault'
            )
        
        creds = Credentials.from_authorized_user_file(token_path, [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify'
        ])
        
        return build('gmail', 'v1', credentials=creds)
    
    def run(self):
        """Main watch loop."""
        self.logger.info("=" * 60)
        self.logger.info("Approved Email Watcher Starting...")
        self.logger.info(f"   Vault: {self.vault_path}")
        self.logger.info(f"   Approved: {self.approved_folder}")
        self.logger.info(f"   Check Interval: {self.check_interval}s")
        self.logger.info("=" * 60)
        self.logger.info("Waiting for approval files... (Press Ctrl+C to stop)")
        
        try:
            while True:
                self._check_and_send()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info("\nWatcher stopped by user")
            self.logger.info(f"Total sent: {self.sent_count}, Errors: {self.error_count}")
    
    def _check_and_send(self):
        """Check for new approval files and send emails."""
        # Find approval files (both APPROVAL_EMAIL_*.md and EMAIL_*.md in Approved folder)
        approval_files = list(self.approved_folder.glob('APPROVAL_EMAIL_*.md'))
        approval_files.extend(self.approved_folder.glob('EMAIL_*.md'))
        
        # Remove duplicates and already processed
        approval_files = list(set(approval_files))
        
        if not approval_files:
            self.logger.debug("No approval files found")
            return
        
        self.logger.info(f"Found {len(approval_files)} approval file(s)")
        
        for filepath in approval_files:
            # Skip already processed
            file_sig = f"{filepath}:{filepath.stat().st_mtime}"
            if file_sig in self.processed_files:
                continue
            
            try:
                self._process_file(filepath)
                self.processed_files.add(file_sig)
            except Exception as e:
                self.logger.error(f"Error processing {filepath.name}: {e}")
                self.error_count += 1
    
    def _process_file(self, filepath: Path):
        """Process single approval file and send email."""
        self.logger.info(f"\nProcessing: {filepath.name}")

        # Read file
        content = filepath.read_text(encoding='utf-8')

        # Extract email details
        email_data = self._extract_details(content)
        original_content = self._extract_original_content(content)

        self.logger.info(f"   To: {email_data['to']}")
        self.logger.info(f"   Subject: {email_data['subject']}")

        # Generate reply using Qwen Code
        self.logger.info("   Generating reply with Qwen Code...")
        body = self._generate_reply_with_qwen(email_data, original_content)
        
        if not body:
            self.logger.info("   Using fallback reply")
            body = self._fallback_reply(original_content)
        
        self.logger.info(f"   Reply generated ({len(body)} chars)")

        # Send email
        self.logger.info("   Sending...")
        message_id = self._send_email(
            to=email_data['to'],
            subject=email_data['subject'],
            body=body,
            in_reply_to=email_data.get('in_reply_to')
        )

        self.logger.info(f"   Sent! Message ID: {message_id}")

        # Update file
        self._update_file(filepath, 'sent', message_id, body)

        # Move to Done
        self._move_to_done(filepath)

        self.sent_count += 1
        self.logger.info(f"   Moved to Done")
    
    def _extract_original_content(self, content: str) -> str:
        """Extract original email content."""
        match = re.search(r'## 📋 Email Content\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if match:
            return match.group(1).strip()[:500]
        
        # Fallback
        fm_end = content.find('---', 3)
        if fm_end > 0:
            return content[fm_end+3:].strip()[:500]
        
        return content[:500]
    
    def _generate_reply_with_qwen(self, email_data: dict, original_content: str) -> str:
        """
        Generate reply using Qwen Code.
        
        Creates a request file for Qwen Code to process.
        """
        # Create request file for Qwen Code
        temp_file = self.approved_folder / f'_qwen_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        request = f"""---
type: qwen_reply_request
created: {datetime.now().isoformat()}
---

# 🤖 Qwen Code - Generate Email Reply

**From:** {email_data.get('from', 'Unknown')}  
**Subject:** {email_data.get('subject', 'No Subject')}

## Original Message

{original_content}

---

## Task

Generate a professional email reply. Return ONLY the reply body text.
"""
        
        temp_file.write_text(request, encoding='utf-8')
        
        # In production, would call Qwen Code API here
        # For now, return None to use fallback
        return None
    
    def _fallback_reply(self, original_content: str) -> str:
        """Generate fallback reply based on content."""
        content_lower = original_content.lower()
        
        # Meeting
        if any(kw in content_lower for kw in ['meeting', 'schedule', 'appointment', 'friday', 'pm', 'am']):
            return """Dear Valued Client,

Thank you for your meeting request.

We have received your message and will check availability. Our team will respond with time slots within 24 hours.

Best regards,
AI Employee Team"""
        
        # Greeting
        if any(kw in content_lower for kw in ['hello', 'greeting', 'hi ', 'hey']):
            return """Dear Valued Client,

Thank you for your kind greeting!

We appreciate you reaching out. How can we assist you?

Best regards,
AI Employee Team"""
        
        # Default
        return """Dear Valued Client,

Thank you for your email.

We have received your message and will respond within 24 hours.

Best regards,
AI Employee Team"""
    
    def _extract_details(self, content: str) -> dict:
        """Extract email details from approval file or email file."""
        def extract_field(pattern, text):
            match = re.search(pattern, text, re.MULTILINE)
            return match.group(1) if match else None
        
        # Try to extract 'to' field (approval file) or 'from' field (email file)
        to_email = extract_field(r'to: "([^"]+)"', content)
        from_email = extract_field(r'from: "([^"]+)"', content)
        subject = extract_field(r'subject: "([^"]+)"', content)
        in_reply_to = extract_field(r'in_reply_to: "([^"]+)"', content)
        message_id = extract_field(r'message_id: "([^"]+)"', content)
        
        # If it's an email file (has from, no to), reply to sender
        if from_email and not to_email:
            # Extract email address from "Name <email@.com>" format
            email_match = re.search(r'<([^>]+)>', from_email)
            reply_to = email_match.group(1) if email_match else from_email
            
            # Add Re: to subject if not present
            if subject and not subject.lower().startswith('re:'):
                subject = f'Re: {subject}'
            
            return {
                'to': reply_to,
                'subject': subject,
                'in_reply_to': message_id
            }
        
        return {
            'to': to_email,
            'subject': subject,
            'in_reply_to': in_reply_to
        }
    
    def _extract_body(self, content: str) -> str:
        """Extract reply body from approval file or email file."""
        # Look for draft content section (approval file)
        match = re.search(r'## Draft Content\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if match:
            body = match.group(1).strip()
            # Remove approval sections
            body = re.sub(r'\n## To (Approve|Reject).*', '', body, flags=re.DOTALL)
            return body.strip()
        
        # Look for email content section (email file)
        match = re.search(r'## 📋 Email Content\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Fallback: use content after frontmatter
        fm_end = content.find('---', 3)
        if fm_end > 0:
            return content[fm_end+3:].strip()[:2000]
        
        return content[:2000]
    
    def _send_email(self, to: str, subject: str, body: str, in_reply_to: str = None) -> str:
        """Send email via Gmail API."""
        message = MIMEText(body)
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject
        
        if in_reply_to:
            message['In-Reply-To'] = in_reply_to
            message['References'] = in_reply_to
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        sent_message = self.service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return sent_message['id']
    
    def _update_file(self, filepath: Path, status: str, message_id: str, reply_body: str = ""):
        """Update approval file with status."""
        content = filepath.read_text(encoding='utf-8')
        content = re.sub(r'status: pending', f'status: {status}', content)

        log_entry = f"""
---

## 🤖 Sent

**Sent at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** {status.title()}
**Message ID:** {message_id}
"""
        if reply_body:
            log_entry += f"\n**Reply:** {reply_body[:200]}...\n"
        
        content += log_entry
        filepath.write_text(content, encoding='utf-8')
    
    def _move_to_done(self, filepath: Path):
        """Move processed file to Done folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{filepath.stem}_sent_{timestamp}.md"
        dest_path = self.done_folder / new_name
        filepath.rename(dest_path)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='📧 Approved Email Watcher - Auto-send from Approved folder'
    )
    parser.add_argument('--vault-path', default=r'..\AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=30,
                       help='Check interval in seconds (default: 30)')
    
    args = parser.parse_args()
    
    try:
        watcher = ApprovedEmailWatcher(args.vault_path, args.interval)
        watcher.run()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nTo authenticate, run:")
        print("   python gmail_watcher.py ..\\AI_Employee_Vault")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
