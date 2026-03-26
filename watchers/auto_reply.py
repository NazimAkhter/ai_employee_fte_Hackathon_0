#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatic Email Reply - Auto-reply to emails from action files.

This script automatically:
1. Reads action files from Needs_Action folder
2. Uses Qwen Code logic to draft replies
3. Sends replies automatically (or with approval)
4. Moves completed files to Done folder

Usage:
    python auto_reply.py [--auto] [--vault-path "..\\AI_Employee_Vault"]

    --auto: Send without approval (use with caution!)
    --vault-path: Path to Obsidian vault
"""

import sys
import argparse
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


class AutoEmailReplier:
    """Automatically reply to emails."""
    
    def __init__(self, vault_path: str, auto_send: bool = False):
        """
        Initialize auto replier.
        
        Args:
            vault_path: Path to Obsidian vault
            auto_send: If True, send without approval
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.auto_send = auto_send
        
        # Ensure folders exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.approved.mkdir(parents=True, exist_ok=True)
        self.done.mkdir(parents=True, exist_ok=True)
        
        # Authenticate
        self.service = self._authenticate()
        
        # Stats
        self.processed = 0
        self.sent = 0
        self.errors = 0
    
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
    
    def process_all(self) -> dict:
        """
        Process all email action files.
        
        Returns:
            Dict with processing stats
        """
        stats = {
            'processed': 0,
            'sent': 0,
            'errors': 0,
            'files': []
        }
        
        # Find all email action files
        email_files = list(self.needs_action.glob('EMAIL_*.md'))
        
        if not email_files:
            print("📭 No email action files found")
            return stats
        
        print(f"📧 Found {len(email_files)} email(s) to process")
        print("=" * 60)
        
        for filepath in sorted(email_files):
            try:
                result = self.process_email(filepath)
                stats['processed'] += 1
                stats['files'].append(result)
                self.processed += 1
                
                if result.get('sent'):
                    stats['sent'] += 1
                    self.sent += 1
                    
            except Exception as e:
                print(f"❌ Error processing {filepath.name}: {e}")
                stats['errors'] += 1
                self.errors += 1
        
        return stats
    
    def process_email(self, filepath: Path) -> dict:
        """
        Process single email and send reply.
        
        Args:
            filepath: Path to action file
            
        Returns:
            Dict with processing result
        """
        print(f"\n📧 Processing: {filepath.name}")
        
        # Read action file
        content = filepath.read_text(encoding='utf-8')
        
        # Extract email details
        email_data = self._extract_email_details(content)
        
        print(f"   From: {email_data['from']}")
        print(f"   Subject: {email_data['subject']}")
        print(f"   Priority: {email_data['priority']}")
        
        # Check if approval required
        requires_approval = email_data.get('is_new_sender', False) or \
                           any(kw in email_data['subject'].lower() for kw in ['invoice', 'payment', 'contract'])
        
        if requires_approval and not self.auto_send:
            print(f"   ⚠️ Requires approval (new sender or sensitive)")
            
            # Create approval file
            approval_path = self._create_approval_file(filepath, email_data, content)
            print(f"   📁 Approval file created: {approval_path.name}")
            
            return {
                'file': filepath.name,
                'sent': False,
                'status': 'pending_approval',
                'approval_file': approval_path.name
            }
        
        # Generate reply
        reply_body = self._generate_reply(email_data, content)
        
        print(f"   📝 Reply generated ({len(reply_body)} chars)")
        
        # Send email
        if self.auto_send or not requires_approval:
            print(f"   🚀 Sending reply...")
            
            try:
                message_id = self._send_reply(
                    to=email_data['from'],
                    subject=f"Re: {email_data['subject']}",
                    body=reply_body,
                    in_reply_to=email_data.get('message_id')
                )
                
                print(f"   ✅ Sent! Message ID: {message_id}")
                
                # Update action file
                self._update_file(filepath, 'sent', message_id, reply_body)
                
                # Move to Done
                self._move_to_done(filepath)
                
                return {
                    'file': filepath.name,
                    'sent': True,
                    'status': 'sent',
                    'message_id': message_id
                }
                
            except Exception as e:
                print(f"   ❌ Send failed: {e}")
                self._update_file(filepath, 'failed', str(e), reply_body)
                raise
        
        return {
            'file': filepath.name,
            'sent': False,
            'status': 'skipped'
        }
    
    def _extract_email_details(self, content: str) -> dict:
        """Extract email details from action file."""
        
        def extract_field(pattern, text):
            match = re.search(pattern, text, re.MULTILINE)
            return match.group(1) if match else None
        
        # Extract from frontmatter
        from_email = extract_field(r'from: "([^"]+)"', content)
        subject = extract_field(r'subject: "([^"]+)"', content)
        msg_id = extract_field(r'message_id: "([^"]+)"', content)
        priority = extract_field(r'priority: "([^"]+)"', content)
        is_new_sender = extract_field(r'is_new_sender: (true|false)', content) == 'true'
        
        # Extract email content
        content_match = re.search(r'## 📋 Email Content\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        email_body = content_match.group(1).strip() if content_match else ''
        
        return {
            'from': from_email,
            'subject': subject,
            'message_id': msg_id,
            'priority': priority or 'normal',
            'is_new_sender': is_new_sender,
            'body': email_body
        }
    
    def _generate_reply(self, email_data: dict, original_content: str) -> str:
        """
        Generate reply based on email content.
        
        This uses simple pattern matching. For AI-generated replies,
        integrate with Qwen Code.
        """
        subject = email_data['subject'].lower()
        body = email_data['body'].lower()
        
        # Invoice/Payment related
        if any(kw in subject for kw in ['invoice', 'payment', 'bill']):
            return f"""Dear Valued Client,

Thank you for your inquiry regarding the invoice/payment.

We have received your message and are processing your request. Our accounting team will respond with the payment details within 24 hours.

If you have any urgent questions, please don't hesitate to contact us.

Best regards,
AI Employee Team
---
This is an automated response. A team member will follow up shortly."""
        
        # Meeting/Schedule related
        if any(kw in subject for kw in ['meeting', 'schedule', 'appointment', 'call']):
            return f"""Dear Valued Client,

Thank you for your meeting request.

We have received your message and will check our availability. Our team will respond with available time slots within 24 hours.

Looking forward to speaking with you.

Best regards,
AI Employee Team
---
This is an automated response. A team member will follow up shortly."""
        
        # General inquiry
        if any(kw in subject for kw in ['inquiry', 'question', 'help', 'information']):
            return f"""Dear Valued Client,

Thank you for contacting us.

We have received your inquiry and appreciate your interest. Our team will review your message and provide a detailed response within 24 hours.

If your matter is urgent, please reply with "URGENT" in the subject line.

Best regards,
AI Employee Team
---
This is an automated response. A team member will follow up shortly."""
        
        # Default reply
        return f"""Dear Valued Client,

Thank you for your email.

We have received your message regarding "{email_data['subject']}" and will respond within 24 hours.

If you have any urgent matters, please don't hesitate to contact us directly.

Best regards,
AI Employee Team
---
This is an automated response. A team member will follow up shortly."""
    
    def _send_reply(self, to: str, subject: str, body: str, in_reply_to: str = None) -> str:
        """Send reply via Gmail API."""
        
        # Create message
        message = MIMEText(body)
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject
        
        if in_reply_to:
            message['In-Reply-To'] = in_reply_to
            message['References'] = in_reply_to
        
        # Encode
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send
        sent_message = self.service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return sent_message['id']
    
    def _create_approval_file(self, filepath: Path, email_data: dict, content: str) -> Path:
        """Create approval request file."""
        
        approval_content = f"""---
type: approval_request
action: email_reply
to: "{email_data['from']}"
subject: "Re: {email_data['subject']}"
original_file: "{filepath.name}"
created: {datetime.now().isoformat()}
status: pending
---

# 📧 Email Reply Approval Required

**To:** {email_data['from']}  
**Subject:** Re: {email_data['subject']}  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Original Email

**From:** {email_data['from']}  
**Subject:** {email_data['subject']}

{email_data['body'][:500]}...

---

## To Approve

**Move this file to:** `/Approved/` folder

AI will send reply automatically once approved.

---

## To Reject

**Move this file to:** `/Rejected/` folder

---

*Approval request created by Auto Email Replier*
"""
        
        approval_path = self.approved / f"APPROVAL_{filepath.name}"
        approval_path.write_text(approval_content, encoding='utf-8')
        
        return approval_path
    
    def _update_file(self, filepath: Path, status: str, message_id: str, reply_body: str):
        """Update action file with status."""
        content = filepath.read_text(encoding='utf-8')
        
        # Update status
        content = re.sub(r'status: pending', f'status: {status}', content)
        
        # Add reply log
        log_entry = f"""
---

## 🤖 Auto Reply Log

**Sent at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {status.title()}  
**Message ID:** {message_id}

### Reply Sent:

{reply_body[:500]}...
"""
        
        content += log_entry
        filepath.write_text(content, encoding='utf-8')
    
    def _move_to_done(self, filepath: Path):
        """Move processed file to Done folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{filepath.stem}_replied_{timestamp}.md"
        dest_path = self.done / new_name
        
        filepath.rename(dest_path)
        print(f"   📁 Moved to Done: {new_name}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='📧 Automatic Email Replier',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Process with approval:
    python auto_reply.py
  
  Process without approval (auto-send):
    python auto_reply.py --auto
  
  Custom vault path:
    python auto_reply.py --vault-path "C:\\Vault"
        """
    )
    
    parser.add_argument('--auto', action='store_true',
                       help='Send replies without approval (use with caution!)')
    parser.add_argument('--vault-path', default=r'..\AI_Employee_Vault',
                       help='Path to Obsidian vault')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📧 Automatic Email Replier")
    print("=" * 60)
    print(f"   Vault: {args.vault_path}")
    print(f"   Auto-Send: {args.auto}")
    print("=" * 60)
    
    try:
        replier = AutoEmailReplier(args.vault_path, args.auto)
        stats = replier.process_all()
        
        print("\n" + "=" * 60)
        print("📊 Processing Complete")
        print(f"   Processed: {stats['processed']} emails")
        print(f"   Sent: {stats['sent']} emails")
        print(f"   Errors: {stats['errors']}")
        print("=" * 60)
        
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
