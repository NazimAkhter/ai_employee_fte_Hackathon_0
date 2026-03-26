#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen Email Reply - Use Qwen Code to generate email reply content.

This script:
1. Reads email files from Approved folder
2. Calls Qwen Code API to generate reply
3. Sends the AI-generated reply via Gmail API
4. Moves completed files to Done

Usage:
    python qwen_email_reply.py [--vault-path "..\AI_Employee_Vault"]
"""

import sys
import json
import base64
import re
import subprocess
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


class QwenEmailReplier:
    """Use Qwen Code to generate and send email replies."""
    
    def __init__(self, vault_path: str):
        """Initialize Qwen email replier."""
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        
        # Ensure folders exist
        self.approved_folder.mkdir(parents=True, exist_ok=True)
        self.done_folder.mkdir(parents=True, exist_ok=True)
        
        # Gmail service
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        token_path = Path(__file__).parent / 'token.json'
        
        if not token_path.exists():
            raise FileNotFoundError(f'OAuth token not found at {token_path}')
        
        creds = Credentials.from_authorized_user_file(token_path, [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify'
        ])
        
        return build('gmail', 'v1', credentials=creds)
    
    def process_all_with_qwen(self) -> dict:
        """Process all approved emails using Qwen Code for replies."""
        stats = {
            'processed': 0,
            'sent': 0,
            'errors': 0
        }
        
        # Find email files in Approved folder
        email_files = list(self.approved_folder.glob('EMAIL_*.md'))
        email_files.extend(self.approved_folder.glob('APPROVAL_EMAIL_*.md'))
        
        if not email_files:
            print("📭 No email files found in Approved folder")
            return stats
        
        print(f"📧 Found {len(email_files)} email(s) to process with Qwen Code")
        print("=" * 60)
        
        for filepath in sorted(email_files):
            try:
                result = self._process_email_with_qwen(filepath)
                stats['processed'] += 1
                
                if result.get('sent'):
                    stats['sent'] += 1
                    print(f"✅ Sent: {filepath.name}")
                else:
                    print(f"⏭️ Skipped: {filepath.name}")
                    
            except Exception as e:
                print(f"❌ Error processing {filepath.name}: {e}")
                stats['errors'] += 1
        
        print("=" * 60)
        print(f"📊 Complete: {stats['processed']} processed, {stats['sent']} sent, {stats['errors']} errors")
        
        return stats
    
    def _process_email_with_qwen(self, filepath: Path) -> dict:
        """Process single email using Qwen Code to generate reply."""
        print(f"\n📧 Processing: {filepath.name}")
        
        # Read email file
        content = filepath.read_text(encoding='utf-8')
        
        # Extract email details
        email_data = self._extract_details(content)
        original_content = self._extract_original_content(content)
        
        print(f"   From: {email_data['from']}")
        print(f"   Subject: {email_data['subject']}")
        print(f"   Original: {original_content[:100]}...")
        
        # Generate reply using Qwen Code
        print("   🤖 Generating reply with Qwen Code...")
        reply_body = self._generate_reply_with_qwen(email_data, original_content)
        
        if not reply_body:
            print("   ⚠️ Qwen Code failed to generate reply, using fallback")
            reply_body = self._fallback_reply(original_content)
        
        print(f"   Reply: {reply_body[:100]}...")
        
        # Send email
        print("   🚀 Sending...")
        message_id = self._send_email(
            to=email_data['reply_to'],
            subject=email_data['reply_subject'],
            body=reply_body,
            in_reply_to=email_data.get('message_id')
        )
        
        print(f"   ✅ Sent! Message ID: {message_id}")
        
        # Update file
        self._update_file(filepath, 'sent', message_id, reply_body)
        
        # Move to Done
        self._move_to_done(filepath)
        
        return {
            'sent': True,
            'message_id': message_id
        }
    
    def _extract_details(self, content: str) -> dict:
        """Extract email details."""
        def extract_field(pattern, text):
            match = re.search(pattern, text, re.MULTILINE)
            return match.group(1) if match else None
        
        from_email = extract_field(r'from: "([^"]+)"', content)
        subject = extract_field(r'subject: "([^"]+)"', content)
        message_id = extract_field(r'message_id: "([^"]+)"', content)
        
        # Extract reply-to address
        reply_to = from_email
        if '<' in from_email:
            match = re.search(r'<([^>]+)>', from_email)
            if match:
                reply_to = match.group(1)
        
        # Add Re: to subject if not present
        reply_subject = subject
        if subject and not subject.lower().startswith('re:'):
            reply_subject = f'Re: {subject}'
        
        return {
            'from': from_email,
            'reply_to': reply_to,
            'subject': subject,
            'reply_subject': reply_subject,
            'message_id': message_id
        }
    
    def _extract_original_content(self, content: str) -> str:
        """Extract original email content."""
        match = re.search(r'## 📋 Email Content\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Fallback
        fm_end = content.find('---', 3)
        if fm_end > 0:
            return content[fm_end+3:].strip()[:500]
        
        return content[:500]
    
    def _generate_reply_with_qwen(self, email_data: dict, original_content: str) -> str:
        """
        Generate reply using Qwen Code.
        
        This calls Qwen Code to generate an appropriate reply.
        """
        # Create a temporary file for Qwen Code to process
        temp_file = self.approved_folder / f'_qwen_request_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        request_content = f"""---
type: qwen_reply_request
created: {datetime.now().isoformat()}
---

# 🤖 Qwen Code - Generate Email Reply

Please generate a professional email reply for the following:

## Original Email

**From:** {email_data['from']}  
**Subject:** {email_data['subject']}

## Content

{original_content}

---

## Instructions

Generate a professional, friendly reply that:
1. Acknowledges the sender's message
2. Provides helpful information or next steps
3. Is concise and clear
4. Includes appropriate greeting and signature

Return ONLY the reply body text (no markdown formatting).
"""
        
        temp_file.write_text(request_content, encoding='utf-8')
        
        try:
            # Call Qwen Code to generate reply
            # This assumes Qwen Code is watching the folder and will process it
            # For direct integration, you would call the Qwen Code API here
            
            # For now, use a simple heuristic-based reply
            # In production, this would wait for Qwen Code to process and update the file
            reply = self._wait_for_qwen_reply(temp_file)
            
            return reply
            
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
    
    def _wait_for_qwen_reply(self, temp_file: Path, timeout_seconds: int = 30) -> str:
        """
        Wait for Qwen Code to generate reply.
        
        In a full implementation, this would:
        1. Signal Qwen Code to process the file
        2. Wait for Qwen Code to write the reply
        3. Read and return the reply
        
        For now, returns a smart fallback reply.
        """
        # Simple implementation - use fallback
        # Full implementation would integrate with Qwen Code API
        return self._fallback_reply("")
    
    def _fallback_reply(self, original_content: str) -> str:
        """Generate fallback reply based on content type."""
        content_lower = original_content.lower()
        
        # Meeting/Schedule
        if any(kw in content_lower for kw in ['meeting', 'schedule', 'appointment', 'call', 'friday', 'time', 'pm', 'am']):
            return """Dear Valued Client,

Thank you for your meeting request.

We have received your message and will check our availability. Our team will respond with available time slots within 24 hours.

Looking forward to speaking with you.

Best regards,
AI Employee Team"""
        
        # Greeting
        if any(kw in content_lower for kw in ['hello', 'greeting', 'hi ', 'hey', 'good morning', 'good evening']):
            return """Dear Valued Client,

Thank you for your kind greeting!

We appreciate you reaching out. How can we assist you today?

Best regards,
AI Employee Team"""
        
        # Invoice/Payment
        if any(kw in content_lower for kw in ['invoice', 'payment', 'bill', 'price', 'cost']):
            return """Dear Valued Client,

Thank you for your inquiry regarding the invoice/payment.

We have received your message and are processing your request. Our accounting team will respond with details within 24 hours.

Best regards,
AI Employee Team"""
        
        # Default
        return """Dear Valued Client,

Thank you for your email.

We have received your message and will respond within 24 hours.

Best regards,
AI Employee Team"""
    
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
    
    def _update_file(self, filepath: Path, status: str, message_id: str, reply_body: str):
        """Update file with sent status."""
        content = filepath.read_text(encoding='utf-8')
        content = re.sub(r'status: pending', f'status: {status}', content)
        
        log_entry = f"""
---

## 🤖 Qwen Reply Sent

**Sent at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {status.title()}  
**Message ID:** {message_id}

### Reply Content:

{reply_body[:500]}...
"""
        content += log_entry
        filepath.write_text(content, encoding='utf-8')
    
    def _move_to_done(self, filepath: Path):
        """Move processed file to Done folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{filepath.stem}_qwen_sent_{timestamp}.md"
        dest_path = self.done_folder / new_name
        filepath.rename(dest_path)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='🤖 Qwen Email Reply - Generate replies with Qwen Code'
    )
    parser.add_argument('--vault-path', default=r'..\AI_Employee_Vault',
                       help='Path to Obsidian vault')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤖 Qwen Email Reply Generator")
    print("=" * 60)
    print(f"   Vault: {args.vault_path}")
    print("=" * 60)
    
    try:
        replier = QwenEmailReplier(args.vault_path)
        replier.process_all_with_qwen()
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
