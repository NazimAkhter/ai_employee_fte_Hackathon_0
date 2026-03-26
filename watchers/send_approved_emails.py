#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send Approved Emails - Processes /Approved folder and sends all pending emails.

Usage:
    python send_approved_emails.py <vault_path>
    
Example:
    python send_approved_emails.py "..\AI_Employee_Vault"
"""

import sys
import re
from pathlib import Path
from datetime import datetime

# Import Gmail sender
from send_reply import GmailSender


class ApprovedEmailSender:
    """Send all approved emails from vault."""
    
    def __init__(self, vault_path: str):
        """
        Initialize sender.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        
        # Ensure folders exist
        self.approved_folder.mkdir(parents=True, exist_ok=True)
        self.done_folder.mkdir(parents=True, exist_ok=True)
        
        # Initialize Gmail sender
        try:
            self.gmail_sender = GmailSender(str(self.vault_path.parent / 'watchers' / 'token.json'))
        except Exception as e:
            print(f"Warning: Could not initialize Gmail sender: {e}")
            self.gmail_sender = None
        
        # Stats
        self.sent_count = 0
        self.error_count = 0
    
    def process_all(self) -> dict:
        """
        Process all approved emails.
        
        Returns:
            Dict with processing stats
        """
        stats = {
            'sent': 0,
            'errors': 0,
            'files': []
        }
        
        # Find all approval files
        approval_files = list(self.approved_folder.glob('APPROVAL_EMAIL_*.md'))
        approval_files.extend(self.approved_folder.glob('EMAIL_APPROVAL_*.md'))
        
        if not approval_files:
            print("📭 No approved emails to send")
            return stats
        
        print(f"📧 Found {len(approval_files)} approved email(s)")
        
        for filepath in sorted(approval_files):
            try:
                result = self.process_file(filepath)
                stats['sent'] += 1
                stats['files'].append(result)
                self.sent_count += 1
            except Exception as e:
                print(f"❌ Error processing {filepath.name}: {e}")
                stats['errors'] += 1
                self.error_count += 1
        
        return stats
    
    def process_file(self, filepath: Path) -> dict:
        """
        Process single approval file.
        
        Args:
            filepath: Path to approval file
            
        Returns:
            Dict with processing result
        """
        print(f"\n📧 Processing: {filepath.name}")
        
        # Read file
        content = filepath.read_text(encoding='utf-8')
        
        # Extract email details
        details = self._extract_details(content)
        
        print(f"   To: {details['to']}")
        print(f"   Subject: {details['subject']}")
        
        # Send email
        if self.gmail_sender:
            try:
                sent_message = self.gmail_sender.send_email(
                    to=details['to'],
                    subject=details['subject'],
                    body=details['body'],
                    in_reply_to=details.get('in_reply_to')
                )
                
                # Update file
                self._update_file(filepath, 'sent', sent_message.get('id', 'unknown'))
                
                # Move to Done
                self._move_to_done(filepath)
                
                print(f"   ✅ Email sent! Message ID: {sent_message.get('id')}")
                
                return {
                    'file': filepath.name,
                    'to': details['to'],
                    'subject': details['subject'],
                    'message_id': sent_message.get('id'),
                    'status': 'sent'
                }
                
            except Exception as e:
                print(f"   ❌ Send failed: {e}")
                self._update_file(filepath, 'failed', str(e))
                raise
        else:
            print("   ⚠️ Gmail sender not initialized")
            self._update_file(filepath, 'failed', 'Gmail sender not initialized')
            raise Exception('Gmail sender not initialized')
    
    def _extract_details(self, content: str) -> dict:
        """Extract email details from approval file."""
        
        def extract_field(pattern, text):
            match = re.search(pattern, text, re.MULTILINE)
            return match.group(1) if match else None
        
        # Extract from frontmatter
        to_email = extract_field(r'to: "([^"]+)"', content)
        subject = extract_field(r'subject: "([^"]+)"', content)
        in_reply_to = extract_field(r'in_reply_to: "([^"]+)"', content)
        
        # Extract draft content (between ## Draft Content and next section)
        body_match = re.search(r'## Draft Content\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        body = body_match.group(1).strip() if body_match else ''
        
        # Remove "To Approve" and "To Reject" sections from body
        body = re.sub(r'\n## To (Approve|Reject).*', '', body, flags=re.DOTALL)
        body = body.strip()
        
        return {
            'to': to_email,
            'subject': subject,
            'body': body,
            'in_reply_to': in_reply_to
        }
    
    def _update_file(self, filepath: Path, status: str, message_id: str = ''):
        """Update approval file with status."""
        content = filepath.read_text(encoding='utf-8')
        
        # Update status in frontmatter
        content = re.sub(
            r'status: pending',
            f'status: {status}',
            content
        )
        
        # Add processing log
        log_entry = f'''
---

## 🤖 Processing Log

**Sent by:** AI Employee  
**Sent at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {status.title()}
**Message ID:** {message_id}
'''
        
        content += log_entry
        filepath.write_text(content, encoding='utf-8')
    
    def _move_to_done(self, filepath: Path):
        """Move processed file to Done folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{filepath.stem}_sent_{timestamp}.md"
        dest_path = self.done_folder / new_name
        
        filepath.rename(dest_path)
        print(f"   📁 Moved to Done: {new_name}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python send_approved_emails.py <vault_path>")
        print("\nExample:")
        print('  python send_approved_emails.py "..\\AI_Employee_Vault"')
        sys.exit(1)
    
    vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Process approved emails
    sender = ApprovedEmailSender(str(vault_path))
    print(f"📧 Approved Email Sender")
    print(f"   Vault: {vault_path}")
    print(f"   Approved Folder: {sender.approved_folder}")
    print()
    
    stats = sender.process_all()
    
    print(f"\n{'='*50}")
    print(f"📊 Processing Complete")
    print(f"   Sent: {stats['sent']} emails")
    print(f"   Errors: {stats['errors']}")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
