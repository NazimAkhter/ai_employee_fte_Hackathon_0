# Personal AI Employee Hackathon 0 - Project Context

## Project Overview

This is a **hackathon project** for building a **"Digital FTE" (Full-Time Equivalent)** — an autonomous AI employee that manages personal and business affairs 24/7. The project uses **Qwen Code** as the reasoning engine and **Obsidian** (local Markdown) as the dashboard/memory system.

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

### Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PERCEPTION (Watchers)                     │
│  Gmail Watcher │ WhatsApp Watcher │ File System Watcher     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              REASONING (Qwen Code + Ralph Loop)              │
│  Reads /Needs_Action → Creates Plan.md → Executes Actions   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  ACTION (MCP Servers)                        │
│  Email MCP │ Browser MCP │ Calendar MCP │ Payment MCP       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              MEMORY/GUI (Obsidian Vault)                     │
│  Dashboard.md │ Company_Handbook.md │ /Inbox │ /Done        │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **The Brain** | Reasoning engine, task execution | Qwen Code |
| **The Memory** | Long-term storage, GUI dashboard | Obsidian (Markdown) |
| **The Senses** | Monitor Gmail, WhatsApp, filesystem | Python Sentinel Scripts |
| **The Hands** | External system interaction | MCP Servers |
| **Persistence** | Keep agent working until task complete | Ralph Wiggum Loop |

---

## Directory Structure

```
ai_employee_fte_Hackathon_0/
├── .qwen/                            # Qwen Code configurations
│   └── skills/
│       ├── browsing-with-playwright/ # Browser automation (Bronze)
│       ├── process-action-files/     # Action file processing (Bronze)
│       ├── email-mcp-integration/    # Gmail MCP integration (Silver)
│       ├── plan-generator/           # Plan.md creation (Silver)
│       ├── hitl-approval-workflow/   # Human-in-the-loop approvals (Silver)
│       ├── dashboard-auto-updater/   # Dashboard stats updates (Silver)
│       ├── linkedin-post-automation/ # LinkedIn posting (Silver)
│       └── scheduler-orchestrator/   # Scheduled task execution (Silver)
├── .gitattributes                    # Git text normalization config
├── skills-lock.json                  # Installed skills registry
├── AI_Employee_Vault/                # Obsidian vault
├── watchers/                         # Python watcher scripts
└── Personal AI Employee Hackathon 0_...md  # Full hackathon blueprint
```

---

## Key Files

| File | Description |
|------|-------------|
| `Personal AI Employee Hackathon 0_...md` | **Main documentation** — Complete hackathon blueprint with architecture, tiered deliverables (Bronze/Silver/Gold/Platinum), watcher implementations, MCP configuration, and business handover templates |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Browser automation skill — Start/stop server, navigation, form filling, screenshots |
| `.qwen/skills/process-action-files/SKILL.md` | Action file processing — Read, process, and move files to /Done |
| `.qwen/skills/email-mcp-integration/SKILL.md` | Email MCP integration — Send, draft, search emails via Gmail |
| `.qwen/skills/plan-generator/SKILL.md` | Plan.md generator — Create structured plans for multi-step tasks |
| `.qwen/skills/hitl-approval-workflow/SKILL.md` | HITL approval workflow — Safe execution with human approval |
| `.qwen/skills/dashboard-auto-updater/SKILL.md` | Dashboard auto-updater — Keep stats current |
| `.qwen/skills/linkedin-post-automation/SKILL.md` | LinkedIn automation — Post to LinkedIn for lead generation |
| `.qwen/skills/scheduler-orchestrator/SKILL.md` | Scheduler orchestrator — Cron/Task Scheduler integration |
| `skills-lock.json` | Registry of installed agent skills with version hashes |

---

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Qwen Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Sentinel scripts, MCP client |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control |

### Playwright MCP Server

```bash
# Start the browser automation server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server is running
python .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop the server
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Client Usage

```bash
# List available tools from HTTP server
python mcp-client.py list -u http://localhost:8808

# Call a tool
python mcp-client.py call -u http://localhost:8808 -t browser_navigate \
  -p '{"url": "https://example.com"}'

# List tools from stdio server
python mcp-client.py list -s "npx -y @modelcontextprotocol/server-github"
```

### Ralph Wiggum Loop (Persistence)

To keep Qwen Code working autonomously until a task is complete:

```bash
# Start a Ralph loop
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

---

## Development Conventions

### Folder Structure (Obsidian Vault)

```
Vault/
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Items requiring processing
├── In_Progress/<agent>/      # Claimed by specific agent
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved actions ready for execution
├── Rejected/                 # Rejected actions
├── Done/                     # Completed tasks
├── Plans/                    # Generated plan files
├── Briefings/                # CEO briefings (Monday Morning reports)
├── Accounting/               # Bank transactions, invoices
└── Dashboard.md              # Real-time summary
```

### Human-in-the-Loop Pattern

For sensitive actions (payments, sending messages), Qwen Code writes an approval request file instead of acting directly:

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
status: pending
---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

### Watcher Pattern

All watcher scripts follow the `BaseWatcher` pattern:

```python
class BaseWatcher(ABC):
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        while True:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            time.sleep(check_interval)
```

### Coding Style

- **Python**: Use type hints, ABC for base classes, logging module
- **Markdown**: YAML frontmatter for metadata, clear section headers
- **Shell scripts**: Use helper scripts for common operations (start/stop/verify)
- **Error handling**: Graceful degradation with logging, never crash silently

---

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** ✅ | 8-12h | Obsidian vault, 1 watcher, Qwen Code reading/writing, Dashboard.md, Company_Handbook.md |
| **Silver** 🔄 | 20-30h | 2+ watchers, Plan.md generation, 1 MCP server, HITL workflow, LinkedIn posting, Scheduler |
| **Gold** | 40+h | Full integration, Odoo accounting, multiple MCPs, Ralph loop, weekly briefings |
| **Platinum** | 60+h | Cloud deployment, domain specialization, vault sync, 24/7 operation |

### Silver Tier Skills Available

| Skill | Purpose | Status |
|-------|---------|--------|
| `email-mcp-integration` | Gmail sending/receiving | ✅ Ready |
| `plan-generator` | Create Plan.md for complex tasks | ✅ Ready |
| `hitl-approval-workflow` | Human approval for sensitive actions | ✅ Ready |
| `dashboard-auto-updater` | Auto-update Dashboard.md stats | ✅ Ready |
| `linkedin-post-automation` | Post to LinkedIn via browser | ✅ Ready |
| `scheduler-orchestrator` | Cron/Task Scheduler integration | ✅ Ready |

---

## MCP Servers Reference

| Server | Capabilities | Use Case |
|--------|--------------|----------|
| `filesystem` | Read, write, list files | Built-in vault access |
| `email-mcp` | Send, draft, search emails | Gmail integration |
| `browser-mcp` | Navigate, click, fill forms | Payment portals, web automation |
| `calendar-mcp` | Create, update events | Scheduling |
| `slack-mcp` | Send messages, read channels | Team communication |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright server not responding | Run `bash scripts/stop-server.sh && bash scripts/start-server.sh` |
| Element not found | Run `browser_snapshot` first to get current refs |
| Click fails | Try `browser_hover` first, then click |
| Form not submitting | Use `"submit": true` with `browser_type` |
| Ralph loop stuck | Check max iterations, verify completion condition |

---

## Resources

### Documentation

- **Main Blueprint**: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Bronze Tier Complete**: `BRONZE_TIER_COMPLETE.md`
- **Playwright Tools**: `.qwen/skills/browsing-with-playwright/references/playwright-tools.md`
- **MCP Client**: `.qwen/skills/browsing-with-playwright/scripts/mcp-client.py`
- **Ralph Wiggum Pattern**: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum (adapt for Qwen Code)

### Silver Tier Skills

- **Email MCP**: `.qwen/skills/email-mcp-integration/SKILL.md`
- **Plan Generator**: `.qwen/skills/plan-generator/SKILL.md`
- **HITL Workflow**: `.qwen/skills/hitl-approval-workflow/SKILL.md`
- **Dashboard Updater**: `.qwen/skills/dashboard-auto-updater/SKILL.md`
- **LinkedIn Automation**: `.qwen/skills/linkedin-post-automation/SKILL.md`
- **Scheduler**: `.qwen/skills/scheduler-orchestrator/SKILL.md`

### External Resources

- **MCP Protocol**: https://modelcontextprotocol.io/
- **MCP Servers**: https://github.com/modelcontextprotocol/servers
- **Playwright**: https://playwright.dev/
- **Obsidian**: https://obsidian.md/
