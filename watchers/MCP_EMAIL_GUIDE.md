# 📧 MCP Email Server - Auto-Send from Approved Folder

**Automatic email sending when files are added to /Approved folder**

---

## 🎯 Overview

The Email MCP Server automatically:
1. **Monitors** the `/Approved` folder
2. **Detects** new approval files
3. **Sends** emails via Gmail API
4. **Moves** completed files to `/Done`

---

## 📁 Two Components

### 1. Email MCP Server (`email_mcp_server.py`)

MCP server that provides email tools for Qwen Code:
- `email_send_approved` - Send all approved emails
- `email_send_single` - Send single email
- `email_list_approved` - List pending approvals
- `email_check_status` - Check server status

### 2. Approved Email Watcher (`approved_watcher.py`)

Background watcher that automatically monitors and sends:
- Runs continuously
- Checks every 30 seconds (configurable)
- Sends emails automatically when files appear

---

## 🚀 Quick Start

### Option 1: Run Approved Watcher (Recommended)

```bash
cd watchers

# Start auto-watcher (checks every 30 seconds)
python approved_watcher.py

# Custom interval (check every 10 seconds)
python approved_watcher.py --interval 10

# Custom vault path
python approved_watcher.py --vault-path "C:\Vault"
```

### Option 2: Use MCP Server via Qwen Code

```
"Send all approved emails using the email MCP server"
```

### Option 3: Manual MCP Command

```bash
cd watchers
python mcp-client.py call ^
  -s "python email_mcp_server.py" ^
  -t email_send_approved ^
  -p '{}'
```

---

## 📋 Workflow

```
1. Gmail Watcher → Creates EMAIL_*.md in Needs_Action/
       ↓
2. Qwen Code → Drafts reply, creates approval file
       ↓
3. User moves → Approval file to /Approved folder
       ↓
4. Approved Watcher → Detects new file (every 30s)
       ↓
5. Sends Email → Via Gmail API
       ↓
6. Moves to Done/ → With sent log
```

---

## 📝 Example Approval File Format

```markdown
---
type: approval_request
action: email_reply
to: "client@example.com"
subject: "Re: Invoice #123"
status: pending
---

# 📧 Email Approval Required

**To:** client@example.com  
**Subject:** Re: Invoice #123

---

## Draft Content

Dear Client,

Thank you for your inquiry. The invoice has been paid.

Best regards,
AI Employee

---

## To Approve
Move this file to `/Approved/` folder.

AI will send automatically once approved.
```

---

## 🔧 Usage Examples

### Start Approved Watcher

```bash
cd watchers
python approved_watcher.py
```

**Output:**
```
============================================================
📧 Approved Email Watcher Starting...
   Vault: ..\AI_Employee_Vault
   Approved: ..\AI_Employee_Vault\Approved
   Check Interval: 30s
============================================================
Waiting for approval files... (Press Ctrl+C to stop)

2026-03-26 XX:XX:XX - ApprovedEmailWatcher - INFO - 📧 Found 1 approval file(s)
2026-03-26 XX:XX:XX - ApprovedEmailWatcher - INFO - 📧 Processing: APPROVAL_EMAIL_Invoice.md
2026-03-26 XX:XX:XX - ApprovedEmailWatcher - INFO -    To: client@example.com
2026-03-26 XX:XX:XX - ApprovedEmailWatcher - INFO -    Subject: Re: Invoice #123
2026-03-26 XX:XX:XX - ApprovedEmailWatcher - INFO -    🚀 Sending...
2026-03-26 XX:XX:XX - ApprovedEmailWatcher - INFO -    ✅ Sent! Message ID: gmail_abc123
2026-03-26 XX:XX:XX - ApprovedEmailWatcher - INFO -    📁 Moved to Done
```

### List Pending Approvals (via MCP)

```bash
python mcp-client.py call ^
  -s "python email_mcp_server.py" ^
  -t email_list_approved ^
  -p '{}'
```

### Send All Approved (via MCP)

```bash
python mcp-client.py call ^
  -s "python email_mcp_server.py" ^
  -t email_send_approved ^
  -p '{"dry_run": false}'
```

### Check Status (via MCP)

```bash
python mcp-client.py call ^
  -s "python email_mcp_server.py" ^
  -t email_check_status ^
  -p '{}'
```

---

## 📊 MCP Configuration

Already configured in `.qwen/mcp.json`:

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["E:/GIAIC/Quarter-04/ai_employee_fte_Hackathon_0/watchers/email_mcp_server.py"]
    }
  }
}
```

---

## 🔄 Schedule Watcher (Windows Task Scheduler)

Run automatically in background:

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument "watchers\approved_watcher.py" `
    -WorkingDirectory "E:\GIAIC\Quarter-04\ai_employee_fte_Hackathon_0"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "AI_Employee_EmailWatcher" `
    -Action $action -Trigger $trigger -RunLevel Highest
```

---

## 📁 File Locations

| File | Location |
|------|----------|
| Email MCP Server | `watchers/email_mcp_server.py` |
| Approved Watcher | `watchers/approved_watcher.py` |
| Approved Folder | `AI_Employee_Vault/Approved/` |
| Done Folder | `AI_Employee_Vault/Done/` |
| Logs | `watchers/logs/approved_watcher.log` |

---

## ✅ Complete Workflow Example

### Step 1: Email Arrives

Gmail Watcher creates:
```
Needs_Action/EMAIL_Client_Inquiry.md
```

### Step 2: Qwen Code Processes

```
"Process the email in Needs_Action"
```

Creates approval file:
```
Approved/APPROVAL_EMAIL_Client_Inquiry.md
```

### Step 3: Approved Watcher Detects

Within 30 seconds:
```
📧 Found 1 approval file(s)
📧 Processing: APPROVAL_EMAIL_Client_Inquiry.md
🚀 Sending...
✅ Sent! Message ID: gmail_xyz789
📁 Moved to Done
```

### Step 4: File Archived

Moved to:
```
Done/APPROVAL_EMAIL_Client_Inquiry_sent_20260326_120000.md
```

---

## 🛡️ Safety Features

| Feature | Protection |
|---------|------------|
| **Approval Required** | User must move file to /Approved first |
| **Logging** | All sends logged to file and console |
| **Archive** | Completed files moved to Done with timestamp |
| **Error Handling** | Failed sends logged, file not moved |
| **Duplicate Prevention** | Tracks processed files |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "OAuth token not found" | Run `python gmail_watcher.py ..\AI_Employee_Vault` |
| "No approval files found" | Move approval files to /Approved folder |
| "Send failed" | Check Gmail API permissions, internet |
| Watcher not detecting | Check interval, folder path correct |

---

## 📈 Monitoring

### View Logs

```bash
# Real-time logs
type watchers\logs\approved_watcher.log

# Or in PowerShell
Get-Content watchers\logs\approved_watcher.log -Wait -Tail 50
```

### Check Stats

Watcher outputs stats on exit:
```
👋 Watcher stopped by user
Total sent: 15, Errors: 0
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| **Start Watcher** | `python approved_watcher.py` |
| **Custom Interval** | `python approved_watcher.py --interval 10` |
| **List Approved** | `mcp-client.py call -s "python email_mcp_server.py" -t email_list_approved -p '{}'` |
| **Send All** | `mcp-client.py call -s "python email_mcp_server.py" -t email_send_approved -p '{}'` |
| **Check Status** | `mcp-client.py call -s "python email_mcp_server.py" -t email_check_status -p '{}'` |

---

*Email MCP Server - Automatic Email Sending from Approved Folder*
