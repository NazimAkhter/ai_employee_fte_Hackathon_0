# 📧 Complete Gmail Workflow Guide

**Read, Reply, and Send Emails Automatically with AI Employee**

---

## 🔄 Complete Gmail Workflow

```
1. Gmail Watcher → 2. Create Action File → 3. Qwen Code Processes → 4. Reply/Send → 5. Log & Archive
```

---

## 📋 Prerequisites

| Item | Status | Location |
|------|--------|----------|
| Gmail API Credentials | ✅ Required | `credentials.json` |
| Gmail Watcher Script | ✅ Created | `watchers/gmail_watcher.py` |
| Email MCP Skill | ✅ Created | `.qwen/skills/email-mcp-integration/` |
| OAuth Token | ⚠️ First-run setup | `watchers/token.json` |

---

## Step 1: Start Gmail Watcher

### Run the Watcher

```bash
cd watchers
python gmail_watcher.py "..\AI_Employee_Vault"
```

### What Happens:

1. **Authenticates with Gmail** using OAuth 2.0
2. **Monitors inbox** every 120 seconds
3. **Checks for unread, important emails**
4. **Creates action files** in `/Needs_Action/` folder

### First Run - OAuth Setup:

```
Please visit this URL to authorize this application:
https://accounts.google.com/o/oauth2/auth?...

1. Copy URL to browser
2. Sign in with Google
3. Grant permissions
4. Copy authorization code
5. Paste in terminal
6. Token saved to `watchers/token.json`
```

---

## Step 2: Gmail Watcher Reads Email

### What Gmail Watcher Does:

1. **Searches Gmail** for: `is:unread is:important`
2. **Extracts email data**:
   - From, To, Subject
   - Date received
   - Email body content
   - Attachments (metadata)
3. **Detects priority**:
   - High: Contains "urgent", "asap", "invoice", "payment"
   - Medium: Contains "meeting", "schedule", "deadline"
   - Normal: Everything else
4. **Creates action file** in `/Needs_Action/`

### Action File Format:

```markdown
---
type: email
from: "client@example.com"
to: "you@example.com"
subject: "Urgent: Project Update Needed"
date: "Tue, 25 Mar 2026 10:30:00 +0500"
received: 2026-03-25T10:30:00
priority: "high"
message_id: "gmail_msg_12345"
is_new_sender: true
status: pending
---

# 📧 Email Received

**From:** client@example.com  
**To:** you@example.com  
**Subject:** Urgent: Project Update Needed  
**Date:** Tue, 25 Mar 2026 10:30:00 +0500  
**Received:** 2026-03-25 10:30  
**Priority:** 🔴 High
**New Sender:** ⚠️ Yes - Approval required before replying

---

## 📋 Email Content

Hi,

We need an update on the project by EOD. Can you please send the latest status?

Thanks,
Client

---

## ✅ Suggested Actions

- [ ] **Create approval request** before replying (new sender)
- [ ] Read and understand email
- [ ] Draft appropriate response
- [ ] Get approval before sending
- [ ] Send response and archive

---

## 🔗 Gmail Link

[View in Gmail](https://mail.google.com/mail/u/0/#inbox/gmail_msg_12345)

---

*Action file created by Gmail Watcher*
```

---

## Step 3: Qwen Code Processes Email

### Tell Qwen Code to Process:

```
"Process all email files in the Needs_Action folder"
```

### What Qwen Code Does:

1. **Reads action files** from `/Needs_Action/`
2. **Analyzes email content**
3. **Determines appropriate response**
4. **Creates draft reply**
5. **Updates action file** with response
6. **Moves to `/Done/`** when complete

### Example Qwen Code Response:

```markdown
## 🤖 AI Processing Log

**Processed by:** Qwen Code  
**Processed at:** 2026-03-25 10:35:00  
**Status:** ✅ Completed

### Actions Taken:

1. ✅ Read email from client@example.com
2. ✅ Analyzed request for project update
3. ✅ Drafted response with current status
4. ✅ Created approval request (new sender)
5. ✅ Moved to /Done/ after approval

### Draft Response:

Dear Client,

Thank you for your inquiry. Here's the current project status:

- Phase 1: Complete (100%)
- Phase 2: In Progress (75%)
- Phase 3: Pending (0%)

Expected completion: March 30, 2026

Best regards,
[Your Name]
```

---

## Step 4: Reply to Email (3 Methods)

### Method 1: Using Gmail MCP (Recommended)

#### Setup Email MCP Server:

```bash
# Install email MCP server
git clone https://github.com/modelcontextprotocol/servers.git
cd servers/src/email
npm install

# Configure in Qwen Code MCP settings
{
  "mcpServers": {
    "email": {
      "command": "node",
      "args": ["/path/to/servers/src/email/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    }
  }
}
```

#### Send Reply via MCP:

```bash
# Using mcp-client.py
cd .qwen/skills/browsing-with-playwright/scripts

python mcp-client.py call -u http://localhost:8765 -t email_send \
  -p '{
    "to": "client@example.com",
    "subject": "Re: Urgent: Project Update Needed",
    "body": "Dear Client,\n\nThank you for your inquiry...\n\nBest regards,\n[Your Name]",
    "in_reply_to": "gmail_msg_12345"
  }'
```

### Method 2: Using Gmail Watcher (Simple)

#### Create Reply Script:

```python
# watchers/send_reply.py
#!/usr/bin/env python3
"""Send email reply via Gmail API."""

import sys
import base64
from pathlib import Path
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def send_reply(to_email: str, subject: str, body: str, in_reply_to: str = None):
    """Send email reply."""
    
    # Load credentials
    token_path = Path(__file__).parent / 'token.json'
    creds = Credentials.from_authorized_user_file(token_path, [
        'https://www.googleapis.com/auth/gmail.send'
    ])
    
    # Build service
    service = build('gmail', 'v1', credentials=creds)
    
    # Create message
    message = MIMEText(body)
    message['to'] = to_email
    message['from'] = 'me'
    message['subject'] = subject
    
    if in_reply_to:
        message['In-Reply-To'] = in_reply_to
        message['References'] = in_reply_to
    
    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    # Send
    try:
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        print(f'✅ Email sent! Message ID: {sent_message["id"]}')
        return sent_message
    except Exception as e:
        print(f'❌ Error sending email: {e}')
        return None

if __name__ == '__main__':
    # Example usage
    send_reply(
        to_email='client@example.com',
        subject='Re: Urgent: Project Update Needed',
        body='Dear Client,\n\nThank you for your inquiry...\n\nBest regards,\n[Your Name]',
        in_reply_to='gmail_msg_12345'
    )
```

#### Run Reply Script:

```bash
cd watchers
python send_reply.py
```

### Method 3: Manual Send (HITL Approval)

#### 1. Create Approval File:

```markdown
---
type: approval_request
action: email_send
to: client@example.com
subject: Re: Urgent: Project Update Needed
created: 2026-03-25T10:35:00Z
status: pending
---

# 📧 Email Approval Required

**To:** client@example.com  
**Subject:** Re: Urgent: Project Update Needed  
**Created:** 2026-03-25 10:35

---

## Draft Content

Dear Client,

Thank you for your inquiry. Here's the current project status:

- Phase 1: Complete (100%)
- Phase 2: In Progress (75%)
- Phase 3: Pending (0%)

Expected completion: March 30, 2026

Best regards,
[Your Name]

---

## To Approve

**Move to:** `/Approved/`

AI will send email automatically once approved.

---

## To Reject

**Move to:** `/Rejected/`

Please provide reason:
- [ ] Content needs revision
- [ ] Wrong recipient
- [ ] Not ready to send
- [ ] Other: _______________

---

*Approval request created by AI Employee*
```

#### 2. Move to Approved Folder:

```bash
# In Windows Explorer, drag file to Approved folder
# Or via command:
move "Needs_Action\APPROVAL_EMAIL_*.md" "Approved\"
```

#### 3. Send Approved Email:

```bash
cd watchers
python send_approved_emails.py "..\AI_Employee_Vault"
```

---

## Step 5: Log & Archive

### Update Action File:

```markdown
---

## 🤖 Processing Log

**Posted by:** AI Employee  
**Sent at:** 2026-03-25 10:40:00  
**Status:** ✅ Sent Successfully
**Message ID:** gmail_sent_67890

### Email Sent:

**To:** client@example.com  
**Subject:** Re: Urgent: Project Update Needed  
**Response Time:** 10 minutes

---

*Action file updated by AI Employee*
```

### Move to Done:

```bash
# Move completed action file
move "Needs_Action\EMAIL_*.md" "Done\"
```

### Mark as Read in Gmail:

Gmail Watcher already marks emails as read when creating action files.

---

## 📁 Complete File Flow

```
Gmail Inbox
    ↓ (Gmail Watcher)
Needs_Action/EMAIL_*.md
    ↓ (Qwen Code processes)
[Draft created]
    ↓ (HITL Approval)
Pending_Approval/APPROVAL_EMAIL_*.md
    ↓ (User moves to Approved)
Approved/
    ↓ (Send script)
[Email Sent via Gmail API]
    ↓ (Log & Archive)
Done/EMAIL_*_completed.md
```

---

## 🎯 Quick Commands Reference

### Start Gmail Watcher:
```bash
python gmail_watcher.py "..\AI_Employee_Vault"
```

### Process Emails with Qwen Code:
```
"Process all email files in Needs_Action folder"
```

### Send Email via MCP:
```bash
python mcp-client.py call -u http://localhost:8765 -t email_send \
  -p '{"to": "client@example.com", "subject": "Hello", "body": "Message"}'
```

### Send Email via Script:
```bash
python send_reply.py
```

### Check Pending Approvals:
```bash
dir Approved\*.md
```

---

## 🔧 Complete Setup Script

Create `setup_gmail.py`:

```python
#!/usr/bin/env python3
"""Complete Gmail setup and workflow."""

import sys
from pathlib import Path

def setup_gmail():
    """Setup Gmail integration."""
    
    print("📧 Gmail Workflow Setup")
    print("=" * 50)
    
    # Check credentials
    creds = Path('credentials.json')
    if not creds.exists():
        print("❌ credentials.json not found!")
        print("Download from Google Cloud Console")
        return False
    print("✓ credentials.json found")
    
    # Check dependencies
    try:
        from google.oauth2.credentials import Credentials
        print("✓ Google auth installed")
    except ImportError:
        print("❌ Install: pip install google-auth")
        return False
    
    # Check vault
    vault = Path('AI_Employee_Vault')
    if not vault.exists():
        print("❌ AI_Employee_Vault not found!")
        return False
    print("✓ Vault found")
    
    # Check folders
    folders = ['Needs_Action', 'Done', 'Approved', 'Pending_Approval']
    for folder in folders:
        (vault / folder).mkdir(exist_ok=True)
    print("✓ Folders created")
    
    print("\n✅ Gmail setup complete!")
    print("\nNext steps:")
    print("1. Run: python gmail_watcher.py")
    print("2. Complete OAuth authentication")
    print("3. Wait for emails to be processed")
    
    return True

if __name__ == '__main__':
    setup_gmail()
```

Run setup:
```bash
python setup_gmail.py
```

---

## 📊 Example Workflow: Complete Email Thread

### Incoming Email:

```
From: client@company.com
Subject: Invoice #123 Payment Status

Hi,

Can you please confirm the payment status for invoice #123?

Thanks,
Client
```

### Action File Created:

```
Needs_Action/EMAIL_Invoice_Payment_20260325_103000.md
```

### Qwen Code Response:

```markdown
## Draft Reply:

Dear Client,

Thank you for your inquiry.

Invoice #123 has been processed and payment was sent on March 20, 2026.

Payment Details:
- Amount: $500.00
- Method: Bank Transfer
- Reference: INV123-PAY

Please confirm receipt.

Best regards,
[Your Name]
```

### Approval & Send:

1. Move to `/Approved/`
2. Run send script
3. Email sent via Gmail API
4. Log updated
5. Move to `/Done/`

---

## 🛡️ Safety Rules (HITL)

| Rule | Description |
|------|-------------|
| **New sender approval** | Always approve first email to new address |
| **Payment keywords** | Emails with "invoice", "payment" need approval |
| **Bulk sending** | >5 recipients requires approval |
| **Attachments** | Flag for review before sending |
| **Sensitive content** | Legal/financial needs approval |

---

## 📈 Metrics to Track

| Metric | Target |
|--------|--------|
| Response time | <1 hour |
| Approval rate | 100% for new senders |
| Accuracy | >95% correct responses |
| Archive rate | 100% logged |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| OAuth failed | Delete `token.json`, re-authenticate |
| No emails found | Check Gmail labels, ensure unread |
| Can't send | Verify Gmail API permissions |
| MCP not connecting | Check server is running |

---

*Complete Gmail Workflow Guide v1.0*
