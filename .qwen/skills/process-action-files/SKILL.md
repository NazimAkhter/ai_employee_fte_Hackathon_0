---
name: process-action-files
description: |
  Process action files in the Obsidian vault's /Needs_Action folder.
  Read action items, execute tasks, update Dashboard.md, and move files to /Done.
  Use when you need to process incoming files, emails, messages, or any action items.
---

# Process Action Files Skill

Process action files from the Obsidian vault and execute required tasks.

## Overview

This skill enables Qwen Code to:
- Read action files from `/Needs_Action`
- Analyze and categorize action items
- Execute required tasks
- Update `Dashboard.md` with progress
- Move completed files to `/Done`

## Folder Structure

```
Vault/
├── Inbox/              # Raw incoming items
├── Needs_Action/       # Items requiring processing ← Work here
├── Done/               # Completed tasks ← Move here when done
├── Plans/              # Multi-step task plans
├── Approved/           # Approved actions
├── Rejected/           # Rejected actions
├── Briefings/          # Reports and briefings
├── Accounting/         # Financial records
└── Dashboard.md        # Real-time status
```

## Usage

### Process All Pending Actions

```bash
# Tell Qwen Code to process all action files
"Process all files in /Needs_Action folder and move them to /Done when complete"
```

### Process Specific File

```bash
# Process a specific action file
"Process the file FILE_invoice_20260324.md in /Needs_Action"
```

### Check Pending Actions

```bash
# List all pending action items
"What action items are pending in /Needs_Action?"
```

## Action File Format

Action files follow this structure:

```markdown
---
type: file_drop
original_name: "invoice.pdf"
file_type: "PDF Document"
priority: "high"
status: pending
---

# 📄 File Dropped for Processing

**File:** `invoice.pdf`
**Priority:** 🔴 High

## ✅ Suggested Actions

- [ ] Review and categorize for accounting
- [ ] Extract amount and vendor information

## 📝 Notes

<!-- Add notes here -->
```

## Processing Workflow

1. **Read** all files in `/Needs_Action`
2. **Analyze** each file's type and priority
3. **Execute** suggested actions
4. **Update** checkboxes in the file (change `[ ]` to `[x]`)
5. **Add** completion notes
6. **Update** `Dashboard.md` stats
7. **Move** file to `/Done` with timestamp

## Dashboard Update Pattern

After processing, update `Dashboard.md`:

```markdown
## 📊 Quick Stats

| Metric | Count |
|--------|-------|
| ⚠️ Needs Action | {count} |
| ✅ Done Today | {count} |
```

## Human-in-the-Loop

For actions requiring approval:

1. Create file in `/Pending_Approval/` with details
2. Wait for user to move file to `/Approved/` or `/Rejected/`
3. Execute approved actions
4. Log result in file

## Examples

### Example 1: Process Invoice

```bash
# Input: FILE_invoice_20260324.md in /Needs_Action
# Qwen Code actions:
1. Read file and extract invoice details
2. Categorize as accounting item
3. Extract amount and vendor
4. Update file with findings
5. Move to /Accounting/
6. Update Dashboard.md
```

### Example 2: Process Document

```bash
# Input: FILE_contract_20260324.md in /Needs_Action
# Qwen Code actions:
1. Read and summarize document
2. Extract key dates and deadlines
3. Create follow-up tasks if needed
4. Move to /Done/
5. Update Dashboard.md
```

## Error Handling

- **File not found:** Log error and continue with next file
- **Permission denied:** Create error note and skip file
- **Unclear action:** Add note requesting clarification
- **Requires approval:** Move to `/Pending_Approval/`

## Best Practices

1. **Always log actions** - Document what you did in the file
2. **Update Dashboard** - Keep stats current after each action
3. **One file at a time** - Complete fully before moving to next
4. **Preserve original data** - Never delete original content
5. **Add timestamps** - Record when actions were completed

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't read file | Check file encoding (should be UTF-8) |
| Can't move file | Check file isn't open in another program |
| Dashboard not updating | Ensure you're updating the correct path |
| Missing permissions | Run Qwen Code with appropriate file access |

## Related Skills

- `browsing-with-playwright` - For web-based actions
- `filesystem` - Built-in file operations

---

*Skill version: 1.0 | Compatible with Qwen Code*
