---
name: hitl-approval-workflow
description: |
  Human-in-the-Loop approval workflow for sensitive actions. Create approval
  request files, wait for human decision, and execute approved actions.
  Required for payments, new email recipients, and other sensitive operations.
---

# Human-in-the-Loop (HITL) Approval Workflow

Safe execution of sensitive actions with human approval.

## Overview

This skill enables Qwen Code to:
- Identify actions requiring human approval
- Create structured approval request files
- Wait for human decision (approve/reject)
- Execute approved actions safely
- Log all approval decisions

## Actions Requiring Approval

| Action Type | Trigger | Approval File Location |
|-------------|---------|------------------------|
| **Payment** | Any payment >$100 | `/Pending_Approval/PAYMENT_*.md` |
| **New Email Recipient** | First time sending to address | `/Pending_Approval/EMAIL_*.md` |
| **Message Sending** | WhatsApp/SMS to new contact | `/Pending_Approval/MESSAGE_*.md` |
| **File Deletion** | Deleting files >30 days old | `/Pending_Approval/DELETE_*.md` |
| **Software Install** | New dependency/package | `/Pending_Approval/INSTALL_*.md` |
| **Config Change** | System configuration changes | `/Pending_Approval/CONFIG_*.md` |

## Approval File Format

```markdown
---
type: approval_request
action: payment
amount: 500.00
currency: USD
recipient: Client A Corp
recipient_account: ****1234
reason: Invoice #1234 payment
created: 2026-03-24T10:30:00Z
expires: 2026-03-25T10:30:00Z
status: pending
priority: high
---

# 💳 Payment Approval Required

**Action:** Payment Transfer  
**Amount:** $500.00 USD  
**Recipient:** Client A Corp (Bank: ****1234)  
**Reason:** Invoice #1234 payment  
**Created:** 2026-03-24 10:30  
**Expires:** 2026-03-25 10:30 (24 hours)  
**Priority:** 🔴 High

---

## 📋 Details

### Invoice Information
- **Invoice Number:** #1234
- **Date Received:** 2026-03-20
- **Due Date:** 2026-04-01
- **Category:** Professional Services

### Verification Completed
- [x] Invoice matches purchase order
- [x] Service was delivered
- [x] Amount matches contract
- [x] Recipient bank verified

---

## 💡 AI Recommendation

**Recommendation:** ✅ APPROVE

**Reasoning:**
- Invoice is legitimate and verified
- Payment is within budget
- Recipient is trusted vendor
- Early payment qualifies for 2% discount

---

## 🔐 To Approve

**Move this file to:** `/Approved/` folder

The AI will execute the payment automatically once approved.

---

## 🚫 To Reject

**Move this file to:** `/Rejected/` folder

**Please add a comment** explaining the rejection reason:
- [ ] Budget concerns
- [ ] Service not delivered
- [ ] Incorrect amount
- [ ] Other: _______________

---

## ⏰ Auto-Expiry

If no action is taken within 24 hours:
- File will be moved to `/Needs_Action/` with reminder
- Escalation notification will be created

---

*Approval request created by HITL Workflow skill*
```

## Usage

### Create Approval Request

```bash
# Tell Qwen Code to create approval request
"Create an approval request for paying invoice #1234 ($500) to Client A"
```

### Check Pending Approvals

```bash
# List pending approvals
"What approval requests are pending?"
```

### Process Approved Files

```bash
# Process all approved actions
"Process all files in /Approved folder"
```

## Workflow: Payment Approval

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Invoice         │ ──→ │ Create Approval  │ ──→ │ Wait for Human  │
│ Received        │     │ Request File     │     │ Decision        │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                        ┌───────────────────────────────┤
                        │                               │
                        ↓                               ↓
              ┌─────────────────┐             ┌─────────────────┐
              │ Move to /Approved│             │ Move to /Rejected│
              │ AI executes      │             │ AI logs reason   │
              │ payment          │             │ notifies sender  │
              └─────────────────┘             └─────────────────┘
```

## Workflow: Email Approval (New Recipient)

```markdown
---
type: approval_request
action: email_send
to: newclient@example.com
subject: Project Proposal
created: 2026-03-24T11:00:00Z
status: pending
---

# 📧 Email Approval Required

**To:** newclient@example.com (NEW RECIPIENT)  
**Subject:** Project Proposal  
**Created:** 2026-03-24 11:00

---

## Draft Content

Dear New Client,

Thank you for your inquiry. We would be happy to...

[Full email draft here]

---

## To Approve
Move to `/Approved/`

## To Reject
Move to `/Rejected/` with reason
```

## Approval Status Values

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `pending` | Awaiting human decision | Wait |
| `approved` | Human approved | Execute action |
| `rejected` | Human rejected | Log and notify |
| `expired` | No response within timeout | Escalate |
| `executed` | Action completed | Archive |

## Timeout and Escalation

### Default Timeouts

| Priority | Timeout | Escalation |
|----------|---------|------------|
| Critical | 1 hour | Immediate notification |
| High | 4 hours | Dashboard alert |
| Normal | 24 hours | Reminder file |
| Low | 7 days | Weekly summary |

### Escalation Process

1. **Timeout reached:** Create reminder in `/Needs_Action/`
2. **Update Dashboard:** Add to pending approvals count
3. **Second timeout:** Create urgent flag
4. **Final:** Add to weekly briefing

## Safety Rules

### Never Auto-Approve

| Condition | Action |
|-----------|--------|
| New payment recipient | Always require approval |
| Amount >$1000 | Require explicit approval |
| International transfer | Require approval + documentation |
| First email to address | Require approval |
| Bulk sending (>5 recipients) | Require approval |

### Always Log

- Approval creation timestamp
- Human decision timestamp
- Action execution timestamp
- Any errors or issues

## Best Practices

1. **Be specific** - Include all relevant details in approval request
2. **Add recommendation** - Help human make informed decision
3. **Set reasonable timeout** - Match priority to urgency
4. **Verify before asking** - Complete due diligence first
5. **Log everything** - Full audit trail of decisions

## Error Handling

- **Approval file moved incorrectly:** Create correction note
- **Action execution fails:** Create error report, notify user
- **Timeout without response:** Escalate per priority rules
- **Duplicate approval:** Merge requests, notify user

## Dashboard Integration

Update Dashboard.md with approval stats:

```markdown
## ⏳ Pending Approval

| Metric | Count |
|--------|-------|
| Payments | 2 |
| Emails | 1 |
| Other | 0 |
| **Total** | **3** |
```

## Related Skills

| Skill | Integration |
|-------|-------------|
| `email-mcp-integration` | Email approval workflow |
| `plan-generator` | Plans with approval steps |
| `dashboard-auto-updater` | Track pending approvals |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Approval not processed | Check file is in /Approved folder |
| Wrong approval type | Recreate with correct action type |
| Timeout too short | Adjust based on priority |
| Missing details | Add verification checklist |

---

*Skill version: 1.0 | Silver Tier | Compatible with Qwen Code*
