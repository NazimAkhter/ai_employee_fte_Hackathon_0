---
name: plan-generator
description: |
  Generate Plan.md files for multi-step tasks. Break down complex tasks into
  actionable steps with checkboxes, estimates, and dependencies. Use when
  facing tasks requiring 3+ steps or multiple tool interactions.
---

# Plan Generator

Create structured Plan.md files for multi-step task execution.

## Overview

This skill enables Qwen Code to:
- Analyze complex tasks and break them into steps
- Create Plan.md files with checkboxes
- Track progress on multi-step tasks
- Estimate time and dependencies
- Link related action files

## When to Create a Plan

Create a Plan.md when a task requires:

| Criteria | Example |
|----------|---------|
| **3+ steps** | "Process invoice, update accounting, send receipt" |
| **Multiple tools** | "Read email → Browser lookup → Send reply" |
| **External dependencies** | "Wait for approval before sending" |
| **Time estimate >10 min** | "Research and summarize 5 articles" |
| **Unclear requirements** | "Figure out what client needs and deliver" |

## Plan.md Format

```markdown
---
type: plan
task: Process client invoice and send receipt
created: 2026-03-24T10:00:00Z
status: in_progress
priority: high
estimated_steps: 5
estimated_time: 15 minutes
---

# 📋 Plan: Process Client Invoice

**Task:** Process client invoice and send receipt  
**Created:** 2026-03-24 10:00  
**Status:** 🔄 In Progress  
**Priority:** 🔴 High

---

## 🎯 Objective

Process the invoice from Client A, categorize it in accounting, and send a confirmation receipt.

---

## ✅ Steps

- [ ] **Step 1:** Read invoice file and extract details
  - Estimated: 2 min
  - Dependencies: None
  - Status: ⏳ Pending

- [ ] **Step 2:** Categorize expense in accounting system
  - Estimated: 3 min
  - Dependencies: Step 1
  - Status: ⏳ Pending

- [ ] **Step 3:** Create approval request for payment
  - Estimated: 2 min
  - Dependencies: Step 2
  - Status: ⏳ Pending

- [ ] **Step 4:** Wait for human approval
  - Estimated: Variable
  - Dependencies: Step 3
  - Status: ⏳ Pending

- [ ] **Step 5:** Send confirmation receipt to client
  - Estimated: 3 min
  - Dependencies: Step 4 (approval required)
  - Status: ⏳ Pending

---

## 📎 Related Files

- **Source:** `/Needs_Action/FILE_invoice_20260324.md`
- **Approval:** `/Pending_Approval/PAYMENT_ClientA_20260324.md`
- **Output:** `/Accounting/invoice_20260324_processed.md`

---

## 📊 Progress

| Metric | Value |
|--------|-------|
| Total Steps | 5 |
| Completed | 0 |
| In Progress | 0 |
| Pending | 5 |
| Blocked | 0 |

---

## 🚧 Blockers

*None currently*

---

## 📝 Notes

<!-- Add notes during execution -->

---

*Plan created by Plan Generator skill*
```

## Usage

### Create Plan from Action File

```bash
# Tell Qwen Code to create a plan
"Create a plan for processing the invoice in Needs_Action folder"
```

### Update Plan Progress

```bash
# Update plan after completing steps
"Update the plan - completed steps 1 and 2"
```

### Get Plan Status

```bash
# Check plan progress
"What's the status of PLAN_invoice_20260324.md?"
```

## Plan Creation Workflow

1. **Read** the action file(s) to understand the task
2. **Identify** all required steps
3. **Determine** dependencies between steps
4. **Estimate** time for each step
5. **Create** Plan.md in `/Plans/` folder
6. **Link** plan back to original action file
7. **Execute** steps one by one, updating progress

## Step Status Values

| Status | Symbol | Meaning |
|--------|--------|---------|
| Pending | ⏳ | Not started |
| In Progress | 🔄 | Currently working |
| Completed | ✅ | Done |
| Blocked | 🚧 | Waiting on dependency |
| Skipped | ⏭️ | Not required |

## Progress Tracking

After each step:

1. Update checkbox: `[ ]` → `[x]`
2. Update status: `⏳ Pending` → `✅ Completed`
3. Add completion note with timestamp
4. Update progress table
5. Move to next step

## Example: Email Response Plan

```markdown
---
type: plan
task: Respond to client inquiry about project status
created: 2026-03-24T14:00:00Z
status: in_progress
---

# 📋 Plan: Client Email Response

## ✅ Steps

- [ ] **Step 1:** Read client email and understand request
- [ ] **Step 2:** Gather project status from team
- [ ] **Step 3:** Draft response email
- [ ] **Step 4:** Create approval file (new recipient)
- [ ] **Step 5:** Wait for approval
- [ ] **Step 6:** Send email and log

## 📎 Related Files

- **Source:** `/Needs_Action/EMAIL_client_inquiry.md`
- **Approval:** `/Pending_Approval/EMAIL_newclient_approval.md`
```

## Example: Research Plan

```markdown
---
type: plan
task: Research competitors and summarize findings
created: 2026-03-24T09:00:00Z
estimated_time: 30 minutes
---

# 📋 Plan: Competitor Research

## ✅ Steps

- [ ] **Step 1:** Search for top 5 competitors
- [ ] **Step 2:** Visit each competitor website
- [ ] **Step 3:** Extract pricing information
- [ ] **Step 4:** Extract feature lists
- [ ] **Step 5:** Create comparison table
- [ ] **Step 6:** Write summary with recommendations
```

## Best Practices

1. **Be specific** - Each step should be clearly actionable
2. **Include estimates** - Helps track if task is going as planned
3. **Note dependencies** - Critical for understanding blockers
4. **Link related files** - Makes navigation easier
5. **Update progress** - Keep plan current during execution
6. **Add notes** - Document any issues or learnings

## Error Handling

- **Step fails:** Mark as blocked, create note explaining why
- **New step discovered:** Add to plan, update total count
- **Task scope changes:** Update objective, add note
- **Plan takes too long:** Flag for review, adjust estimates

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| `process-action-files` | Creates plans for complex actions |
| `email-mcp-integration` | Plans for email workflows |
| `hitl-approval-workflow` | Plans with approval steps |
| `browsing-with-playwright` | Plans with browser automation |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Plan too vague | Break steps into smaller, specific actions |
| Missing dependencies | Review step order, add dependency notes |
| Estimates wrong | Update based on actual time, learn for next |
| Plan not updated | Set reminder to update after each step |

## Related Skills

- `process-action-files` - For processing action files
- `hitl-approval-workflow` - For approval steps in plans
- `dashboard-auto-updater` - For tracking plan progress

---

*Skill version: 1.0 | Silver Tier | Compatible with Qwen Code*
