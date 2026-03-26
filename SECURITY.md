# 🔐 Security Guide - Protect Your Secrets

**What's Protected and How**

---

## ✅ Files Now Ignored by Git

The following files are now in `.gitignore` and will NOT be committed:

### Credentials & Tokens
- `credentials.json` - Gmail OAuth credentials
- `token.json` - Gmail OAuth token
- `*.env` - Environment variables
- `secrets.json` - Any secret configurations

### Session Data
- `.linkedin_session/` - LinkedIn browser session
- `gmail_session/` - Gmail session data
- `*.session` - Any session files

### Logs
- `watchers/logs/` - All watcher logs
- `*.log` - Log files

### Cache Files
- `__pycache__/` - Python cache
- `*_cache*` - Cache files
- `_qwen_*.md` - Temporary Qwen request files

### IDE & OS Files
- `.vscode/`, `.idea/` - IDE settings
- `.DS_Store`, `Thumbs.db` - OS files

---

## 📁 Current Sensitive Files

These files exist and are protected by `.gitignore`:

| File | Location | Purpose |
|------|----------|---------|
| `credentials.json` | Project root | Gmail OAuth credentials |
| `token.json` | `watchers/` | Gmail OAuth token |
| `.linkedin_session/` | `AI_Employee_Vault/` | LinkedIn session |
| `gmail_processed_cache.txt` | `watchers/` | Gmail cache |
| `linkedin_processed_cache.json` | `watchers/` | LinkedIn cache |
| `*.log` | `watchers/logs/` | All logs |

---

## 🔒 Best Practices

### 1. Never Commit Secrets

```bash
# Before committing, always check:
git status

# Review what will be committed:
git diff --cached
```

### 2. Use Environment Variables

For production, use `.env` file (already ignored):

```bash
# Copy example
copy .env.example .env

# Edit .env with your secrets (never commit!)
```

### 3. Backup Secrets Securely

```bash
# Backup to encrypted location
# Example: Use Windows BitLocker or VeraCrypt
```

### 4. Rotate Credentials Regularly

- Gmail OAuth: Every 90 days
- API Keys: Every 60 days
- Tokens: Auto-rotated (refresh tokens)

---

## 🛡️ What's Protected

### ✅ Now Ignored (Safe)

```
credentials.json          ✅ Protected
token.json                ✅ Protected
.linkedin_session/        ✅ Protected
watchers/logs/            ✅ Protected
*.env                     ✅ Protected
__pycache__/              ✅ Protected
```

### ⚠️ Still Tracked (Review)

```
AI_Employee_Vault/        ⚠️ Contains emails (review content)
QWEN.md                   ✅ Safe (no secrets)
watchers/*.py             ✅ Safe (code only)
```

---

## 📋 Security Checklist

- [x] `.gitignore` created
- [x] `credentials.json` ignored
- [x] `token.json` ignored
- [x] Session folders ignored
- [x] Log files ignored
- [x] `.env.example` created
- [ ] Review vault content before committing
- [ ] Enable 2FA on Google account
- [ ] Rotate credentials every 90 days
- [ ] Use encrypted backup for credentials

---

## 🚨 If You Accidentally Commit Secrets

### 1. Remove from Git History

```bash
# Remove file from all commits
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch credentials.json" \
  --prune-empty --tag-name-filter cat -- --all

# Push changes
git push origin --force --all
```

### 2. Rotate Compromised Credentials

1. Go to Google Cloud Console
2. Delete compromised credentials
3. Create new credentials
4. Update `credentials.json`

### 3. Notify Team

If working in a team, notify them to:
- Pull latest changes
- Delete any cached credentials
- Get new credentials if needed

---

## 🔐 Vault Security

### What's Safe to Commit

```markdown
✅ Dashboard.md           (no personal data)
✅ Company_Handbook.md    (public rules)
✅ Plans/*.md            (task plans)
✅ Briefings/*.md        (business summaries)
```

### What to Review Before Committing

```markdown
⚠️ Needs_Action/*.md     (may contain emails)
⚠️ Done/*.md             (may contain sensitive info)
⚠️ Accounting/*.md       (financial data)
⚠️ Inbox/*.md            (raw incoming data)
```

### Recommendation

Create separate `.gitignore` for vault:

```bash
# Add to .gitignore
AI_Employee_Vault/Needs_Action/
AI_Employee_Vault/Done/
AI_Employee_Vault/Inbox/
AI_Employee_Vault/Accounting/
```

---

## 📖 Additional Resources

- [Git Security Best Practices](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure)
- [Google OAuth Security](https://developers.google.com/identity/protocols/oauth2/security-best-practices)
- [12-Factor App - Config](https://12factor.net/config)

---

*Security Guide v1.0 - Last updated: 2026-03-27*
