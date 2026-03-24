---
name: dashboard-auto-updater
description: |
  Automatically update Dashboard.md with real-time stats, task progress,
  and system status. Keep the AI Employee dashboard current after every
  action and on scheduled intervals.
---

# Dashboard Auto-Updater

Keep Dashboard.md synchronized with vault state.

## Overview

This skill enables Qwen Code to:
- Count files in each vault folder
- Update stats tables automatically
- Track daily/weekly metrics
- Log recent activities
- Generate status summaries

## Dashboard Sections

```markdown
# 🎯 AI Employee Dashboard

## 📊 Quick Stats          ← Auto-updated
## 📥 Inbox               ← Auto-updated
## ⚠️ Needs Action        ← Auto-updated
## ⏳ Pending Approval    ← Auto-updated
## ✅ Recent Completed    ← Auto-updated
## 📈 Business Metrics    ← Auto-updated
## 🤖 Agent Status        ← Auto-updated
```

## Usage

### Full Dashboard Update

```bash
# Tell Qwen Code to update dashboard
"Update the Dashboard.md with current stats"
```

### After Action Processing

```bash
# Auto-triggered after processing action files
# Updates counts and adds to recent completed
```

### Scheduled Update

```bash
# Run every hour via scheduler
"Update Dashboard.md stats and timestamp"
```

## Stats Calculation

### Folder Counts

```python
# Pseudo-code for counting
inbox_count = count_files("/Inbox", "*.md")
needs_action_count = count_files("/Needs_Action", "*.md")
done_today = count_files("/Done", "*_done_*.md", today=True)
pending_approval = count_files("/Pending_Approval", "*.md")
approved = count_files("/Approved", "*.md")
```

### Metrics Table

| Metric | Source | Update Trigger |
|--------|--------|----------------|
| Inbox Items | `/Inbox/*.md` | New file detected |
| Needs Action | `/Needs_Action/*.md` | Action file created |
| Done Today | `/Done/*_done_*.md` | File completed |
| Pending Approval | `/Pending_Approval/*.md` | Approval requested |

## Update Triggers

| Trigger | Action |
|---------|--------|
| **File processed** | Update counts, add to recent |
| **Approval created** | Increment pending count |
| **Approval decided** | Update counts, log decision |
| **Hourly** | Full stats refresh |
| **Daily (midnight)** | Reset daily counters |
| **On demand** | Immediate full update |

## Dashboard Format

```markdown
---
type: dashboard
last_updated: 2026-03-24T14:30:00Z
status: active
---

# 🎯 AI Employee Dashboard

**Last Updated:** 2026-03-24 14:30
**Status:** 🟢 Active

---

## 📊 Quick Stats

| Metric | Count |
|--------|-------|
| 📥 Inbox Items | 3 |
| ⚠️ Needs Action | 5 |
| ✅ Done Today | 12 |
| ⏳ Pending Approval | 2 |

---

## 📥 Inbox

*New items awaiting initial processing*

1. FILE_document_20260324_1400.md - Received 14:00
2. EMAIL_client_inquiry.md - Received 13:45
3. MESSAGE_urgent_request.md - Received 13:30

---

## ⚠️ Needs Action

*Items requiring immediate attention*

1. FILE_invoice_urgent_20260324.md - 🔴 High priority
2. EMAIL_payment_received.md - 🟢 Normal priority
3. TASK_followup_required.md - 🟡 Medium priority

---

## ⏳ Pending Approval

*Actions awaiting human approval*

1. PAYMENT_ClientA_500.md - $500.00 - Created 10:30
2. EMAIL_newclient_proposal.md - Email to new recipient

---

## ✅ Recent Completed Tasks

*Last 5 completed tasks*

1. FILE_receipt_20260324_1415.md - Processed 14:15
2. EMAIL_reply_project_update.md - Sent 14:00
3. FILE_contract_reviewed.md - Completed 13:45
4. TASK_daily_backup.md - Done 13:30
5. EMAIL_invoice_sent.md - Sent 13:15

---

## 📈 Business Metrics

### Revenue This Week
- **Target:** $10,000
- **Actual:** $4,500
- **Status:** 🟡 On Track (45%)

### Active Projects
1. Project Alpha - Due Jan 15 - Budget $2,000
2. Project Beta - Due Jan 30 - Budget $3,500

### Upcoming Deadlines
- 2026-03-25: Client A deliverable
- 2026-03-28: Monthly report due

---

## 🤖 Agent Status

| Agent | Status | Last Active |
|-------|--------|-------------|
| File Watcher | 🟢 Running | 14:29 |
| Email Watcher | 🟢 Running | 14:28 |
| Main Processor | 🟢 Ready | 14:30 |
| Scheduler | 🟢 Active | 14:00 |

---

## 📝 Quick Notes

- 2026-03-24: System running smoothly
- 2026-03-23: Added new email watcher

---

*Dashboard auto-updated by AI Employee*
```

## Update Workflow

1. **Scan** all vault folders
2. **Count** files in each category
3. **List** recent items (last 5 per section)
4. **Calculate** business metrics
5. **Update** timestamp
6. **Write** updated Dashboard.md

## Timestamp Handling

```python
# Update timestamp correctly
import re
from datetime import datetime

content = re.sub(
    r'last_updated:.*',
    f'last_updated: {datetime.now().isoformat()}',
    content,
    count=1  # Only replace first occurrence
)
```

## Recent Items Format

```markdown
1. FILE_invoice_20260324_1400.md - Processed 14:00
   - Type: file_drop
   - Priority: high
   - Action: Processed and moved to /Done
```

## Error Handling

- **Dashboard locked:** Retry after 5 seconds
- **Write failed:** Log error, continue operations
- **Corrupt file:** Create backup, regenerate from vault state
- **Missing sections:** Add missing sections with defaults

## Best Practices

1. **Update after every action** - Keep stats current
2. **Use atomic writes** - Prevent partial updates
3. **Backup before major changes** - Save previous version
4. **Validate counts** - Double-check calculations
5. **Format consistently** - Maintain readable structure

## Integration Points

| Component | Integration |
|-----------|-------------|
| `process-action-files` | Trigger update after processing |
| `hitl-approval-workflow` | Update pending approval count |
| `plan-generator` | Track active plans |
| `scheduler-orchestrator` | Scheduled hourly updates |

## Performance

| Operation | Expected Time |
|-----------|---------------|
| Full scan | <1 second |
| Count files | <100ms |
| Write update | <500ms |
| Total update | <2 seconds |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Counts wrong | Re-scan vault, verify file patterns |
| Timestamp broken | Check regex pattern, fix format |
| Missing sections | Add section template |
| Update fails | Check file permissions |

## Related Skills

- `process-action-files` - Triggers updates after processing
- `hitl-approval-workflow` - Updates approval counts
- `scheduler-orchestrator` - Scheduled updates

---

*Skill version: 1.0 | Silver Tier | Compatible with Qwen Code*
