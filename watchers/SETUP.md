# Silver Tier Watchers Setup

This guide helps you set up and test the Gmail and LinkedIn watchers for the Silver Tier.

## Prerequisites

- Python 3.13+
- Gmail API credentials (`credentials.json` in project root)
- LinkedIn account
- Playwright installed

## Quick Setup

### 1. Install Dependencies

```bash
cd watchers
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
playwright install chromium
```

### 3. Verify Setup

```bash
# Check Python packages
pip list | findstr google
pip list | findstr playwright

# Check credentials file
dir ..\credentials.json
```

---

## Gmail Watcher Setup

### Credentials Setup

Your `credentials.json` should already be in the project root:

```
E:\GIAIC\Quarter-04\ai_employee_fte_Hackathon_0\credentials.json
```

### First Run - OAuth Authentication

The first time you run the Gmail watcher, it will guide you through OAuth:

1. **Run the watcher:**
   ```bash
   cd watchers
   python gmail_watcher.py "..\AI_Employee_Vault"
   ```

2. **You'll see an authorization URL** - copy and paste it into your browser

3. **Sign in with Google** and grant permissions

4. **Copy the authorization code** from the browser

5. **Paste the code** back in the terminal

6. **Token saved!** The watcher will create `token.json` for future runs

### Running Gmail Watcher

```bash
# Basic usage (checks every 120 seconds)
python gmail_watcher.py "..\AI_Employee_Vault"

# Custom check interval (every 60 seconds)
python gmail_watcher.py "..\AI_Employee_Vault" "" 60

# With explicit credentials path
python gmail_watcher.py "..\AI_Employee_Vault" "..\credentials.json" 120
```

### Expected Output

```
📧 Gmail Watcher starting...
   Vault: E:\GIAIC\Quarter-04\ai_employee_fte_Hackathon_0\AI_Employee_Vault
   Credentials: E:\GIAIC\Quarter-04\ai_employee_fte_Hackathon_0\credentials.json
   Check Interval: 120s

Press Ctrl+C to stop

2026-03-24 10:00:00 - GmailWatcher - INFO - Starting GmailWatcher
2026-03-24 10:00:01 - GmailWatcher - INFO - Loaded existing OAuth token
2026-03-24 10:00:01 - GmailWatcher - INFO - Gmail service initialized
2026-03-24 10:00:05 - GmailWatcher - INFO - Found 2 new messages
2026-03-24 10:00:05 - GmailWatcher - INFO - Created action file for email: Invoice #123
```

### Troubleshooting Gmail

| Issue | Solution |
|-------|----------|
| `credentials.json not found` | Ensure file is in project root |
| `OAuth flow failed` | Check redirect URI is `http://localhost` |
| `Token expired` | Delete `token.json` and re-authenticate |
| `Gmail API error` | Check Gmail API is enabled in Google Cloud |

---

## LinkedIn Watcher Setup

### First Run - Manual Login

The first time you run the LinkedIn watcher, you need to log in manually:

1. **Run the watcher:**
   ```bash
   cd watchers
   python linkedin_watcher.py "..\AI_Employee_Vault"
   ```

2. **The watcher will create a session** in `.linkedin_session` folder

3. **First run will show "Not logged in"** - this is expected

4. **To log in:**
   - Run the watcher with headless=False temporarily
   - Or manually open LinkedIn in a browser and log in
   - The session will be saved for future runs

### Running LinkedIn Watcher

```bash
# Basic usage (checks every 300 seconds = 5 minutes)
python linkedin_watcher.py "..\AI_Employee_Vault"

# More frequent checks (every 60 seconds)
python linkedin_watcher.py "..\AI_Employee_Vault" "" 60

# Custom session path
python linkedin_watcher.py "..\AI_Employee_Vault" "C:\linkedin_session" 300
```

### Expected Output

```
💼 LinkedIn Watcher starting...
   Vault: E:\GIAIC\Quarter-04\ai_employee_fte_Hackathon_0\AI_Employee_Vault
   Session: E:\GIAIC\Quarter-04\ai_employee_fte_Hackathon_0\AI_Employee_Vault\.linkedin_session
   Check Interval: 300s

Note: First run will require manual LinkedIn login
Press Ctrl+C to stop

2026-03-24 10:00:00 - LinkedInWatcher - INFO - Starting LinkedInWatcher
2026-03-24 10:00:05 - LinkedInWatcher - INFO - Browser initialized
2026-03-24 10:00:10 - LinkedInWatcher - INFO - Navigating to LinkedIn...
2026-03-24 10:00:15 - LinkedInWatcher - INFO - Found 3 notifications
2026-03-24 10:00:15 - LinkedInWatcher - INFO - Created action file: LINKEDIN_CONNECTION_20260324_100015.md
```

### What LinkedIn Watcher Detects

| Activity Type | Action File Created |
|---------------|---------------------|
| Connection request | `LINKEDIN_CONNECTION_*.md` |
| New message | `LINKEDIN_MSG_*.md` |
| Job opportunity | `LINKEDIN_JOB_*.md` |
| Post engagement | `LINKEDIN_ENGAGEMENT_*.md` |
| Login required | `LINKEDIN_LOGIN_*.md` |

### Troubleshooting LinkedIn

| Issue | Solution |
|-------|----------|
| `Playwright not installed` | Run `pip install playwright && playwright install` |
| `Not logged in` | Manually log in to LinkedIn first |
| `Browser won't start` | Check session folder permissions |
| `No notifications found` | Check LinkedIn notification settings |

---

## Testing Both Watchers

### Test Script

Create a test file `test_watchers.py`:

```python
#!/usr/bin/env python3
"""Test both watchers."""

import subprocess
import sys
from pathlib import Path

def test_gmail():
    """Test Gmail watcher setup."""
    print("Testing Gmail Watcher...")
    
    # Check credentials
    creds = Path('../credentials.json')
    if not creds.exists():
        print("❌ credentials.json not found")
        return False
    
    print("✓ credentials.json found")
    
    # Try import
    try:
        from google.oauth2.credentials import Credentials
        print("✓ Google auth installed")
    except ImportError:
        print("❌ Google auth not installed - run: pip install -r requirements.txt")
        return False
    
    return True

def test_linkedin():
    """Test LinkedIn watcher setup."""
    print("\nTesting LinkedIn Watcher...")
    
    # Try import
    try:
        from playwright.sync_api import sync_playwright
        print("✓ Playwright installed")
    except ImportError:
        print("❌ Playwright not installed - run: pip install playwright")
        return False
    
    return True

if __name__ == '__main__':
    print("=" * 50)
    print("Silver Tier Watchers - Setup Test")
    print("=" * 50)
    
    gmail_ok = test_gmail()
    linkedin_ok = test_linkedin()
    
    print("\n" + "=" * 50)
    if gmail_ok and linkedin_ok:
        print("✅ All tests passed! Ready to run watchers.")
    else:
        print("❌ Some tests failed. Fix issues above.")
    print("=" * 50)
```

Run test:
```bash
cd watchers
python test_watchers.py
```

---

## Integration with Qwen Code

Once watchers are running, Qwen Code can process the action files:

```bash
# Process all action files
python action_processor.py "..\AI_Employee_Vault"

# Or tell Qwen Code:
"Process all files in the Needs_Action folder"
```

### Action File Flow

```
Gmail/LinkedIn → Watcher → Needs_Action/ → Qwen Code → Done/
```

---

## Running in Background

### Windows Task Scheduler

```powershell
# Create task for Gmail Watcher
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument "watchers\gmail_watcher.py" `
    -WorkingDirectory "E:\GIAIC\Quarter-04\ai_employee_fte_Hackathon_0"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "AI_Employee_Gmail" `
    -Action $action -Trigger $trigger -RunLevel Highest
```

### Linux Cron

```bash
# Add to crontab
*/2 * * * * cd /path/to/project && python watchers/gmail_watcher.py AI_Employee_Vault
```

---

## Next Steps

After watchers are working:

1. **Test with real emails** - Send yourself a test email
2. **Test with LinkedIn** - Have someone send you a connection request
3. **Process action files** - Run `action_processor.py`
4. **Set up scheduling** - Configure Task Scheduler or cron

---

*Silver Tier Watchers Setup Guide*
