# 📧 Email MCP Server Setup Guide

**Send and Reply to Emails using MCP Server**

---

## 📋 Prerequisites

| Item | Status |
|------|--------|
| Node.js | ✅ Required (v18+) |
| Gmail API Credentials | ✅ Already have (credentials.json) |
| Gmail OAuth Token | ✅ Already generated (watchers/token.json) |

---

## Step 1: Install Email MCP Server

### Option A: Use Official MCP Email Server

```bash
# Create folder for MCP servers
mkdir C:\mcp-servers
cd C:\mcp-servers

# Clone MCP servers repository
git clone https://github.com/modelcontextprotocol/servers.git
cd servers

# Install email MCP server
cd src/email
npm install
```

### Option B: Use Pre-built MCP Server

```bash
# Install via npx (no installation needed)
npx -y @modelcontextprotocol/server-email
```

---

## Step 2: Configure MCP in Qwen Code

### Create MCP Configuration

Create file: `.qwen/mcp.json`

```json
{
  "mcpServers": {
    "email": {
      "command": "node",
      "args": ["C:/mcp-servers/servers/src/email/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "E:/GIAIC/Quarter-04/ai_employee_fte_Hackathon_0/credentials.json",
        "GMAIL_TOKEN": "E:/GIAIC/Quarter-04/ai_employee_fte_Hackathon_0/watchers/token.json"
      }
    }
  }
}
```

### Alternative: Use npx (Recommended)

Create file: `.qwen/mcp.json`

```json
{
  "mcpServers": {
    "email": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-email"],
      "env": {
        "GMAIL_CREDENTIALS": "E:/GIAIC/Quarter-04/ai_employee_fte_Hackathon_0/credentials.json",
        "GMAIL_TOKEN": "E:/GIAIC/Quarter-04/ai_employee_fte_Hackathon_0/watchers/token.json"
      }
    }
  }
}
```

---

## Step 3: Verify MCP Server

### Test Connection

```bash
# Navigate to project
cd E:\GIAIC\Quarter-04\ai_employee_fte_Hackathon_0

# Test MCP server
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py list ^
  -s "npx -y @modelcontextprotocol/server-email"
```

### Expected Output

```
Available Tools:
  email_send              - Send an email
  email_draft_create      - Create an email draft
  email_search            - Search emails
  email_read              - Read an email
```

---

## Step 4: Send Email via MCP

### Method 1: Using mcp-client.py

```bash
cd watchers

# Send a new email
python mcp-client.py call ^
  -s "npx -y @modelcontextprotocol/server-email" ^
  -t email_send ^
  -p "{\"to\": \"client@example.com\", \"subject\": \"Hello\", \"body\": \"Dear Client, This is a test email.\"}"
```

### Method 2: Reply to Email

```bash
# Reply to existing email (include message ID)
python mcp-client.py call ^
  -s "npx -y @modelcontextprotocol/server-email" ^
  -t email_send ^
  -p "{\"to\": \"client@example.com\", \"subject\": \"Re: Invoice #123\", \"body\": \"Dear Client, Thank you for your inquiry...\", \"in_reply_to\": \"gmail_msg_12345\"}"
```

### Method 3: Create Draft

```bash
# Create draft (for approval before sending)
python mcp-client.py call ^
  -s "npx -y @modelcontextprotocol/server-email" ^
  -t email_draft_create ^
  -p "{\"to\": \"client@example.com\", \"subject\": \"Proposal\", \"body\": \"Dear Client, Please find our proposal...\"}"
```

---

## Step 5: Search and Read Emails

### Search Emails

```bash
# Search for unread emails
python mcp-client.py call ^
  -s "npx -y @modelcontextprotocol/server-email" ^
  -t email_search ^
  -p "{\"query\": \"is:unread is:important\"}"
```

### Read Specific Email

```bash
# Read email by message ID
python mcp-client.py call ^
  -s "npx -y @modelcontextprotocol/server-email" ^
  -t email_read ^
  -p "{\"message_id\": \"gmail_msg_12345\"}"
```

---

## 🔄 Complete Email Reply Workflow

### Step 1: Gmail Watcher Creates Action File

```bash
# Watcher is already running, monitoring Gmail
# When new email arrives, creates:
# Needs_Action/EMAIL_Invoice_123.md
```

### Step 2: Qwen Code Processes Email

Tell Qwen Code:
```
"Process the email file in Needs_Action folder and draft a reply"
```

### Step 3: Send Reply via MCP

```bash
# After Qwen Code drafts reply, send it:
cd watchers

python mcp-client.py call ^
  -s "npx -y @modelcontextprotocol/server-email" ^
  -t email_send ^
  -p "{\"to\": \"client@example.com\", \"subject\": \"Re: Invoice #123\", \"body\": \"Dear Client,\\n\\nThank you for your inquiry.\\n\\nBest regards,\\n[Your Name]\", \"in_reply_to\": \"gmail_msg_12345\"}"
```

---

## 📝 Quick Reference Commands

### Send New Email

```bash
python mcp-client.py call -s "npx -y @modelcontextprotocol/server-email" -t email_send -p "{\"to\": \"email@example.com\", \"subject\": \"Test\", \"body\": \"Hello\"}"
```

### Reply to Email

```bash
python mcp-client.py call -s "npx -y @modelcontextprotocol/server-email" -t email_send -p "{\"to\": \"email@example.com\", \"subject\": \"Re: Original\", \"body\": \"Reply text\", \"in_reply_to\": \"gmail_msg_id\"}"
```

### Create Draft

```bash
python mcp-client.py call -s "npx -y @modelcontextprotocol/server-email" -t email_draft_create -p "{\"to\": \"email@example.com\", \"subject\": \"Draft\", \"body\": \"Draft content\"}"
```

### Search Emails

```bash
python mcp-client.py call -s "npx -y @modelcontextprotocol/server-email" -t email_search -p "{\"query\": \"is:unread\"}"
```

### Read Email

```bash
python mcp-client.py call -s "npx -y @modelcontextprotocol/server-email" -t email_read -p "{\"message_id\": \"gmail_msg_123\"}"
```

---

## 🔧 Troubleshooting

### Issue: MCP Server Not Found

```
Error: Cannot find module '@modelcontextprotocol/server-email'
```

**Solution:**
```bash
# Install globally
npm install -g @modelcontextprotocol/server-email

# Or use full path
node C:/mcp-servers/servers/src/email/index.js
```

### Issue: OAuth Token Invalid

```
Error: Invalid OAuth token
```

**Solution:**
```bash
# Delete old token and re-authenticate
del watchers\token.json
python gmail_watcher.py ..\AI_Employee_Vault
```

### Issue: MCP Server Won't Start

```
Error: Cannot start MCP server
```

**Solution:**
```bash
# Test server manually
npx -y @modelcontextprotocol/server-email

# Check if it outputs available tools
```

---

## 📊 MCP Email Server Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `email_send` | Send email | to, subject, body, in_reply_to |
| `email_draft_create` | Create draft | to, subject, body |
| `email_search` | Search emails | query |
| `email_read` | Read email | message_id |
| `email_list` | List emails | max_results |

---

## 🎯 Example: Complete Email Reply

### 1. Check for New Emails

```bash
python mcp-client.py call -s "npx -y @modelcontextprotocol/server-email" -t email_search -p "{\"query\": \"is:unread\"}"
```

### 2. Read the Email

```bash
python mcp-client.py call -s "npx -y @modelcontextprotocol/server-email" -t email_read -p "{\"message_id\": \"gmail_abc123\"}"
```

### 3. Send Reply

```bash
python mcp-client.py call -s "npx -y @modelcontextprotocol/server-email" -t email_send -p "{\"to\": \"sender@example.com\", \"subject\": \"Re: Original Subject\", \"body\": \"Dear Sender,\\n\\nThank you for your email.\\n\\nBest regards\", \"in_reply_to\": \"gmail_abc123\"}"
```

---

## ✅ Verification Checklist

- [ ] Node.js installed (v18+)
- [ ] MCP email server installed
- [ ] `.qwen/mcp.json` created
- [ ] OAuth token exists (`watchers/token.json`)
- [ ] MCP server lists tools successfully
- [ ] Can send test email
- [ ] Can reply to email

---

*Email MCP Server Setup Guide v1.0*
