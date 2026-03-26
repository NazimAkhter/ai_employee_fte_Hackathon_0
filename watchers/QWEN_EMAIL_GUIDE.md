# 🤖 Qwen Code Email Reply - Complete Guide

**Use Qwen Code as the brain to generate email replies**

---

## 🎯 Overview

The approved email watcher now uses **Qwen Code** to generate intelligent email replies instead of sending the original message content.

---

## 🔄 How It Works

```
1. Email file in Approved/ folder
       ↓
2. Watcher detects file
       ↓
3. Creates Qwen request file (_qwen_*.md)
       ↓
4. Qwen Code processes and generates reply
       ↓
5. Watcher sends AI-generated reply
       ↓
6. Moves file to Done/
```

---

## 📝 Reply Generation

### Qwen Code Integration

The watcher creates a request file for Qwen Code:

```markdown
---
type: qwen_reply_request
created: 2026-03-27T01:30:00
---

# 🤖 Qwen Code - Generate Email Reply

**From:** client@example.com  
**Subject:** Meeting Request

## Original Message

I want to schedule a meeting on Friday at 3 PM.

---

## Task

Generate a professional email reply. Return ONLY the reply body text.
```

### Qwen Code Response

Qwen Code would process this and generate:

```
Dear Valued Client,

Thank you for your meeting request.

We have received your message and will check our availability. Our team will respond with available time slots within 24 hours.

Looking forward to speaking with you.

Best regards,
AI Employee Team
```

---

## 🚀 Usage

### Start Approved Watcher

```bash
cd watchers
python approved_watcher.py
```

The watcher will:
1. Detect EMAIL_*.md files in Approved/
2. Generate replies (via Qwen Code or fallback)
3. Send emails
4. Move to Done/

### With Qwen Code Integration

For full Qwen Code integration, Qwen Code needs to:
1. Watch for `_qwen_*.md` files
2. Process the request
3. Write reply to the file
4. Watcher picks up the reply

---

## 📊 Fallback Replies

If Qwen Code doesn't generate a reply, smart fallbacks are used:

### Meeting Requests

```
Dear Valued Client,

Thank you for your meeting request.

We have received your message and will check availability. Our team will respond with time slots within 24 hours.

Best regards,
AI Employee Team
```

### Greetings

```
Dear Valued Client,

Thank you for your kind greeting!

We appreciate you reaching out. How can we assist you?

Best regards,
AI Employee Team
```

### Default

```
Dear Valued Client,

Thank you for your email.

We have received your message and will respond within 24 hours.

Best regards,
AI Employee Team
```

---

## 🔧 File Flow

```
Approved/EMAIL_Meeting_*.md
    ↓
Creates: Approved/_qwen_20260327_013000.md
    ↓
Qwen Code processes
    ↓
Qwen writes reply to file
    ↓
Watcher reads reply
    ↓
Sends email
    ↓
Moves to: Done/EMAIL_Meeting_*_qwen_sent_20260327_013000.md
```

---

## 📋 Example Output

```
Processing: EMAIL_Meeting_20260327_011741.md
   To: nazim.akhter99@gmail.com
   Subject: Re: Meeting
   Generating reply with Qwen Code...
   Reply generated (245 chars)
   Sending...
   Sent! Message ID: 19d2bcc35655b5c8
   Moved to Done
```

---

## 🎯 Qwen Code Prompt Format

For best results, Qwen Code should be prompted with:

```
You are an AI email assistant. Generate professional email replies that:

1. Acknowledge the sender's message
2. Are friendly and helpful
3. Provide clear next steps
4. Are concise (2-4 paragraphs)
5. Include appropriate greeting and signature

Original email:
{original_content}

Generate ONLY the reply body text.
```

---

## 🔐 Safety Features

| Feature | Protection |
|---------|------------|
| **Approval Required** | User must move to Approved first |
| **Qwen Review** | AI generates appropriate content |
| **Fallback** | Safe default replies if Qwen fails |
| **Logging** | All replies logged to file |
| **Archive** | Completed files moved to Done |

---

## 📈 Monitoring

### View Logs

```bash
# Real-time logs
type watchers\logs\approved_watcher.log

# Or in PowerShell
Get-Content watchers\logs\approved_watcher.log -Wait -Tail 50
```

### Check Qwen Requests

```bash
# View pending Qwen requests
dir Approved\_qwen_*.md
```

---

## 🎯 Complete Workflow Example

### Step 1: Email Arrives

Gmail Watcher creates:
```
Needs_Action/EMAIL_Client_Meeting.md
```

### Step 2: Move to Approved

```bash
move Needs_Action\EMAIL_Client_Meeting.md Approved\
```

### Step 3: Watcher Detects

```
Found 1 approval file(s)
Processing: EMAIL_Client_Meeting.md
   To: client@example.com
   Subject: Re: Meeting Request
   Generating reply with Qwen Code...
```

### Step 4: Qwen Generates

Creates: `Approved/_qwen_20260327_013000.md`

Qwen Code processes and writes reply.

### Step 5: Send Email

```
Reply generated (245 chars)
Sending...
Sent! Message ID: gmail_xyz123
Moved to Done
```

---

## ✅ Benefits

| Benefit | Description |
|---------|-------------|
| **Intelligent Replies** | Qwen Code understands context |
| **Professional Tone** | Always appropriate language |
| **Customizable** | Adjust Qwen prompts as needed |
| **Fallback Safety** | Safe defaults if Qwen unavailable |
| **Fully Automatic** | No manual reply writing |

---

*Qwen Code Email Reply Guide v1.0*
