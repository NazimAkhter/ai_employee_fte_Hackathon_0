---
name: email-mcp-integration
description: |
  Gmail integration via Email MCP server. Send, draft, search, and read emails.
  Use when tasks require email communication, sending replies, or managing inbox.
  Always requires human approval before sending to new recipients.
---

# Email MCP Integration

Send, draft, and manage emails via Gmail MCP server.

## Overview

This skill enables Qwen Code to:
- Send emails via Gmail
- Create draft emails for approval
- Search and read existing emails
- Manage email threads
- Handle attachments

## MCP Server Setup

### Install Email MCP Server

```bash
# Clone and install the email MCP server
git clone https://github.com/modelcontextprotocol/servers.git
cd servers/src/email
npm install
```

### Configure MCP Server

Add to your Qwen Code MCP configuration:

```json
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

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`
6. Run the OAuth flow to get access token

## Usage

### Send Email

```bash
# Send an email
python mcp-client.py call -u http://localhost:8765 -t email_send \
  -p '{"to": "recipient@example.com", "subject": "Meeting Tomorrow", "body": "Hi, just confirming our meeting tomorrow at 2pm."}'
```

### Create Draft (for approval)

```bash
# Create draft email
python mcp-client.py call -u http://localhost:8765 -t email_draft_create \
  -p '{"to": "client@example.com", "subject": "Invoice #123", "body": "Please find attached invoice..."}'
```

### Search Emails

```bash
# Search emails
python mcp-client.py call -u http://localhost:8765 -t email_search \
  -p '{"query": "is:unread from:important@client.com"}'
```

### Read Email

```bash
# Read specific email
python mcp-client.py call -u http://localhost:8765 -t email_read \
  -p '{"message_id": "msg_12345"}'
```

## Workflow: Email Response

1. **Read** incoming email from action file
2. **Draft** response using `email_draft_create`
3. **Create approval file** in `/Pending_Approval/`
4. **Wait** for user to move to `/Approved/`
5. **Send** email after approval
6. **Log** sent email in action file

## Workflow: New Recipient Safety

For **first-time recipients**, always:

1. Create draft (don't send directly)
2. Create approval file with recipient details
3. Wait for explicit approval
4. Add recipient to "trusted" list after approval

## Email Action File Format

```markdown
---
type: email
from: client@example.com
subject: Urgent: Project Update Needed
received: 2026-03-24T10:30:00Z
priority: high
status: pending
---

# 📧 Email Received

**From:** client@example.com  
**Subject:** Urgent: Project Update Needed  
**Received:** 2026-03-24 10:30

## Content

Hi, we need an update on the project by EOD.

## ✅ Suggested Actions

- [ ] Draft response with project status
- [ ] Get approval before sending
- [ ] Send email and log response
```

## Approval File Format

```markdown
---
type: approval_request
action: email_send
to: newclient@example.com
subject: Project Update
created: 2026-03-24T11:00:00Z
status: pending
---

# 📧 Email Approval Required

**To:** newclient@example.com (NEW RECIPIENT)  
**Subject:** Project Update  
**Draft Location:** /Drafts/draft_20260324_1100.md

## Draft Content

Dear Client,

Thank you for your inquiry. Here is the project update...

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with reason.
```

## Safety Rules

| Rule | Description |
|------|-------------|
| **New Recipient Check** | Always approve first email to new address |
| **Attachment Warning** | Flag emails with attachments for review |
| **Sensitive Content** | Financial/legal emails need approval |
| **Bulk Sending** | Never send to >5 recipients without approval |
| **Reply All** | Confirm before using reply-all |

## Error Handling

- **Authentication Failed:** Refresh OAuth token
- **Rate Limited:** Wait 60 seconds and retry
- **Invalid Recipient:** Log error, notify user
- **Send Failed:** Save as draft, create error report

## Best Practices

1. **Always log sent emails** in the action file
2. **Use drafts for approval** workflow
3. **Check spam folder** before marking as unread
4. **Quote original message** in replies
5. **Add timestamps** to all email actions

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Auth failed | Re-run OAuth flow, check credentials |
| Can't send | Check Gmail API quota, verify account |
| Draft not created | Verify write permissions to Drafts folder |
| MCP not connected | Restart server: `node index.js` |

## Related Skills

- `hitl-approval-workflow` - For approval workflow
- `process-action-files` - For processing email action files
- `browsing-with-playwright` - For webmail fallback

---

*Skill version: 1.0 | Silver Tier | Compatible with Qwen Code*
