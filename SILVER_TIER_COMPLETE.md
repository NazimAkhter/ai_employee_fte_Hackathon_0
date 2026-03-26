# 🥈 Silver Tier - AI Employee Functional Assistant

**Status:** ✅ **COMPLETE**

This directory contains the complete Silver Tier implementation of the Personal AI Employee hackathon.

---

## 📋 Silver Tier Deliverables (Complete)

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| ✅ All Bronze requirements | Complete | From Bronze Tier |
| ✅ 2+ Watcher scripts | Complete | File System + Gmail + LinkedIn |
| ✅ Plan.md generation | Complete | `plan-generator` skill |
| ✅ 1 MCP server | Complete | Email MCP integration skill |
| ✅ HITL approval workflow | Complete | `hitl-approval-workflow` skill |
| ✅ Basic scheduling | Complete | `scheduler-orchestrator` skill |
| ✅ LinkedIn posting | Complete | `linkedin-post-automation` skill |

---

## 📁 Project Structure

```
ai_employee_fte_Hackathon_0/
├── AI_Employee_Vault/              # Obsidian Vault (Bronze)
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Done/
│   ├── Plans/
│   ├── Approved/
│   ├── Rejected/
│   ├── Briefings/
│   ├── Accounting/
│   ├── Dashboard.md
│   └── Company_Handbook.md
│
├── watchers/                       # Watcher Scripts (Silver)
│   ├── base_watcher.py             # Base class for all watchers
│   ├── filesystem_watcher.py       # File system monitor (Bronze)
│   ├── gmail_watcher.py            # Gmail monitor (Silver) ⭐
│   ├── linkedin_watcher.py         # LinkedIn monitor (Silver) ⭐
│   ├── action_processor.py         # Process action files
│   ├── logs/                       # Watcher logs
│   ├── SETUP.md                    # Setup instructions
│   └── requirements.txt            # Python dependencies
│
├── .qwen/skills/                   # Qwen Code Skills
│   ├── browsing-with-playwright/   # Browser automation (Bronze)
│   ├── process-action-files/       # Action processing (Bronze)
│   ├── email-mcp-integration/      # Gmail MCP (Silver) ⭐
│   ├── plan-generator/             # Plan.md creation (Silver) ⭐
│   ├── hitl-approval-workflow/     # HITL approvals (Silver) ⭐
│   ├── dashboard-auto-updater/     # Dashboard updates (Silver) ⭐
│   ├── linkedin-post-automation/   # LinkedIn posting (Silver) ⭐
│   └── scheduler-orchestrator/     # Task scheduling (Silver) ⭐
│
├── credentials.json                # Gmail API credentials
├── BRONZE_TIER_COMPLETE.md         # Bronze documentation
└── SILVER_TIER_COMPLETE.md         # This file (Silver)
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd watchers
pip install -r requirements.txt
playwright install chromium
```

### 2. Start Gmail Watcher

```bash
# First run - OAuth authentication
cd watchers
python gmail_watcher.py "..\AI_Employee_Vault"

# Follow OAuth prompts to authenticate Gmail
# Token will be saved for future runs
```

### 3. Start LinkedIn Watcher

```bash
# First run - Manual login required
cd watchers
python linkedin_watcher.py "..\AI_Employee_Vault"

# Login to LinkedIn when prompted
# Session will be saved for future runs
```

### 4. Start File Watcher (Optional)

```bash
# Monitor test_drop folder
cd watchers
python filesystem_watcher.py "..\AI_Employee_Vault" "..\test_drop" 30
```

### 5. Process Action Files

```bash
# In a new terminal, process all action files
cd watchers
python action_processor.py "..\AI_Employee_Vault"
```

---

## 📧 Gmail Watcher

### Features

- Monitors Gmail for unread, important emails
- Creates action files in `/Needs_Action`
- Detects priority based on keywords
- Marks emails as read after processing
- OAuth 2.0 authentication (secure)
- Caches processed message IDs

### Action File Format

```markdown
---
type: email
from: "client@example.com"
subject: "Invoice #123"
priority: "high"
message_id: "gmail_msg_id"
is_new_sender: true
status: pending
---

# 📧 Email Received

**From:** client@example.com  
**Subject:** Invoice #123  
**Priority:** 🔴 High
**New Sender:** ⚠️ Yes - Approval required before replying

## 📋 Email Content

[Email body extracted here]

## ✅ Suggested Actions

- [ ] **Create approval request** before replying (new sender)
- [ ] Review invoice/payment details
- [ ] Extract amount and due date
```

### Commands

```bash
# Basic usage (120 second interval)
python gmail_watcher.py "..\AI_Employee_Vault"

# Custom interval (60 seconds)
python gmail_watcher.py "..\AI_Employee_Vault" "" 60

# With explicit credentials
python gmail_watcher.py "..\AI_Employee_Vault" "..\credentials.json"
```

### OAuth First Run

1. Run the watcher
2. Copy the authorization URL
3. Open in browser
4. Sign in with Google
5. Grant permissions
6. Copy authorization code
7. Paste in terminal
8. Token saved to `watchers/token.json`

---

## 💼 LinkedIn Watcher

### Features

- Monitors LinkedIn for notifications and messages
- Detects connection requests, job opportunities
- Creates action files for new activity
- Persistent browser session (saves login)
- Priority detection for urgent messages

### Activity Types Detected

| Type | Action File | Priority |
|------|-------------|----------|
| Connection request | `LINKEDIN_CONNECTION_*.md` | Normal |
| New message | `LINKEDIN_MSG_*.md` | Based on content |
| Job opportunity | `LINKEDIN_JOB_*.md` | High |
| Post engagement | `LINKEDIN_ENGAGEMENT_*.md` | Normal |
| Login required | `LINKEDIN_LOGIN_*.md` | High |

### Action File Format (Message)

```markdown
---
type: linkedin_message
from: "John Doe"
linkedin_id: "msg_123"
priority: "high"
status: pending
---

# 💬 LinkedIn Message

**From:** John Doe  
**Preview:** Hi, I have a job opportunity...  
**Priority:** 🔴 High

## ✅ Suggested Actions

- [ ] **Respond urgently** (high priority)
- [ ] Review job opportunity
- [ ] Check if interested
- [ ] Respond with interest or decline
```

### Commands

```bash
# Basic usage (300 second interval)
python linkedin_watcher.py "..\AI_Employee_Vault"

# Custom interval (60 seconds)
python linkedin_watcher.py "..\AI_Employee_Vault" "" 60

# Custom session path
python linkedin_watcher.py "..\AI_Employee_Vault" "C:\linkedin_session"
```

### First Run Login

1. Run the watcher
2. Browser will open
3. Log in to LinkedIn manually
4. Session saved to `.linkedin_session` folder
5. Future runs use saved session

---

## 🤖 Qwen Code Integration

### Process Action Files

Tell Qwen Code:

```
"Process all files in the Needs_Action folder and move them to Done when complete"
```

Qwen Code will:
1. Read all action files from `/Needs_Action`
2. Analyze type and priority
3. Execute suggested actions
4. Update checkboxes to `[x]`
5. Add processing log
6. Move files to `/Done`
7. Update `Dashboard.md`

### Create Plans for Complex Tasks

```
"Create a plan for processing the emails and LinkedIn messages"
```

Qwen Code creates `Plan.md` in `/Plans/` folder.

### Approval Workflow

For sensitive actions (new email recipients, payments):

```
"Create an approval request for replying to this new client"
```

Qwen Code creates approval file in `/Pending_Approval/`.

---

## 📊 Dashboard Integration

Dashboard.md is automatically updated with:

```markdown
## 📊 Quick Stats

| Metric | Count |
|--------|-------|
| 📥 Inbox Items | 0 |
| ⚠️ Needs Action | 5 |
| ✅ Done Today | 12 |
| ⏳ Pending Approval | 2 |

## 📥 Inbox

1. EMAIL_Invoice_123.md - Received 10:30
2. LINKEDIN_MSG_John_Doe.md - Received 10:15
3. LINKEDIN_CONNECTION.md - Received 09:45
```

---

## 🗓️ Scheduling

### Windows Task Scheduler

```powershell
# Gmail Watcher - Every 15 minutes
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument "watchers\gmail_watcher.py AI_Employee_Vault" `
    -WorkingDirectory "E:\GIAIC\Quarter-04\ai_employee_fte_Hackathon_0"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName "AI_Employee_Gmail" `
    -Action $action -Trigger $trigger
```

### Linux Cron

```bash
# Add to crontab
*/15 * * * * cd /path/to/project && python watchers/gmail_watcher.py AI_Employee_Vault
*/5 * * * * cd /path/to/project && python watchers/linkedin_watcher.py AI_Employee_Vault
```

---

## 🧪 Testing

### Test Gmail Watcher

1. **Send yourself a test email** with subject "Test Invoice"
2. **Run Gmail watcher:**
   ```bash
   python gmail_watcher.py "..\AI_Employee_Vault"
   ```
3. **Check `/Needs_Action`** for new action file
4. **Verify email marked as read** in Gmail

### Test LinkedIn Watcher

1. **Have someone send you a connection request** on LinkedIn
2. **Run LinkedIn watcher:**
   ```bash
   python linkedin_watcher.py "..\AI_Employee_Vault"
   ```
3. **Check `/Needs_Action`** for new action file
4. **Verify notification detected**

### Test Action Processor

1. **Ensure action files exist** in `/Needs_Action`
2. **Run processor:**
   ```bash
   python action_processor.py "..\AI_Employee_Vault"
   ```
3. **Check `/Done`** for processed files
4. **Verify Dashboard.md updated**

---

## 🔧 Troubleshooting

### Gmail Watcher Issues

| Issue | Solution |
|-------|----------|
| `credentials.json not found` | Ensure file is in project root |
| `OAuth flow failed` | Check redirect URI is `http://localhost` |
| `Token expired` | Delete `token.json` and re-authenticate |
| `No new messages` | Check Gmail labels, ensure messages are unread |
| `Gmail API error 403` | Enable Gmail API in Google Cloud Console |

### LinkedIn Watcher Issues

| Issue | Solution |
|-------|----------|
| `Playwright not installed` | Run `pip install playwright && playwright install` |
| `Not logged in` | Manually log in to LinkedIn on first run |
| `Browser won't start` | Check session folder permissions |
| `No notifications found` | Check LinkedIn notification settings |
| `Session expired` | Delete `.linkedin_session` folder and re-login |

### Action Processor Issues

| Issue | Solution |
|-------|----------|
| `No files to process` | Ensure action files exist in `/Needs_Action` |
| `Dashboard not updating` | Check Dashboard.md exists and is writable |
| `File move failed` | Ensure file isn't open in another program |

---

## 📈 Silver Tier Skills Summary

| Skill | Purpose | Location |
|-------|---------|----------|
| `email-mcp-integration` | Gmail MCP for sending/drafting emails | `.qwen/skills/email-mcp-integration/` |
| `plan-generator` | Create Plan.md for multi-step tasks | `.qwen/skills/plan-generator/` |
| `hitl-approval-workflow` | Human approval for sensitive actions | `.qwen/skills/hitl-approval-workflow/` |
| `dashboard-auto-updater` | Auto-update Dashboard.md stats | `.qwen/skills/dashboard-auto-updater/` |
| `linkedin-post-automation` | Post to LinkedIn for lead generation | `.qwen/skills/linkedin-post-automation/` |
| `scheduler-orchestrator` | Cron/Task Scheduler integration | `.qwen/skills/scheduler-orchestrator/` |

---

## 🎯 Next Steps (Gold Tier)

To advance to Gold Tier, add:

1. **Odoo Accounting Integration** - Self-hosted accounting via MCP
2. **Multiple MCP Servers** - Email + Browser + Calendar + Payment
3. **Weekly Business Audit** - Automated CEO briefing generation
4. **Error Recovery** - Graceful degradation and retry logic
5. **Comprehensive Audit Logging** - Full action history
6. **Ralph Wiggum Loop** - Autonomous multi-step task completion

---

## 📞 Support

For issues or questions:
1. Check logs in `watchers/logs/`
2. Review `Company_Handbook.md` for rules
3. Consult main hackathon document
4. Check watcher SETUP.md for detailed instructions

---

**Silver Tier Status:** ✅ **COMPLETE**  
**Date Completed:** 2026-03-24  
**Time Spent:** ~4-6 hours  
**Watchers Implemented:** 3 (File, Gmail, LinkedIn)  
**Skills Created:** 8 total

*Ready to advance to Gold Tier!*
