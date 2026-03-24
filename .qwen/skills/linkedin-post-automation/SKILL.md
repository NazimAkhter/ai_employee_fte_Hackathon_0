---
name: linkedin-post-automation
description: |
  Automate LinkedIn posting for business lead generation. Create, schedule,
  and post content to LinkedIn using browser automation. Always requires
  human approval before posting.
---

# LinkedIn Post Automation

Post to LinkedIn for business lead generation.

## Overview

This skill enables Qwen Code to:
- Draft LinkedIn posts for business promotion
- Navigate LinkedIn and post content
- Schedule posts for optimal times
- Track engagement metrics
- Generate content ideas

## Prerequisites

- Playwright MCP server running
- LinkedIn account credentials
- Human approval before each post
- Content guidelines document

## Usage

### Create Post Draft

```bash
# Tell Qwen Code to create a LinkedIn post draft
"Create a LinkedIn post about our new service offering"
```

### Post to LinkedIn

```bash
# After approval, post to LinkedIn
"Post the approved LinkedIn draft to LinkedIn"
```

### Schedule Post

```bash
# Schedule for optimal time
"Schedule this post for tomorrow 9:00 AM"
```

## Post Creation Workflow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Content Idea    │ ──→ │ Draft Post       │ ──→ │ Create Approval │
│ (from brief)    │     │ (with hashtags)  │     │ Request File    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                        ┌───────────────────────────────┤
                        │                               │
                        ↓                               ↓
              ┌─────────────────┐             ┌─────────────────┐
              │ Move to /Approved│             │ Move to /Rejected│
              │ Post via browser │             │ Revise content   │
              │ Log engagement   │             │                  │
              └─────────────────┘             └─────────────────┘
```

## Post Format

```markdown
---
type: linkedin_post
topic: New Service Launch
created: 2026-03-24T10:00:00Z
scheduled: 2026-03-25T09:00:00Z
status: draft
approval_required: true
---

# 💼 LinkedIn Post Draft

**Topic:** New Service Launch  
**Created:** 2026-03-24 10:00  
**Scheduled:** 2026-03-25 09:00 (optimal engagement time)  
**Status:** 📝 Draft

---

## Post Content

🚀 Exciting News! We're launching our new AI Employee service!

Tired of repetitive tasks taking up your time? Our Digital FTE can:
✅ Process emails automatically
✅ Manage your calendar
✅ Handle data entry 24/7
✅ Generate reports on demand

Get 85% cost savings compared to traditional hiring.

Learn more: [Your Website Link]

#AIEmployee #Automation #Productivity #DigitalTransformation #Innovation

---

## Post Details

| Attribute | Value |
|-----------|-------|
| Character Count | 287 |
| Hashtag Count | 5 |
| Link Included | Yes |
| Media | Optional: Product screenshot |

---

## Target Audience

- Business owners
- Operations managers
- Tech decision makers
- Startups looking to scale

---

## To Approve

**Move to:** `/Approved/`

AI will post automatically once approved.

---

## To Reject

**Move to:** `/Rejected/`

Please provide feedback:
- [ ] Tone not right
- [ ] Message unclear
- [ ] Wrong timing
- [ ] Other: _______________

---

*Post draft created by LinkedIn Automation skill*
```

## Browser Automation Steps

### Post to LinkedIn

```python
# Step 1: Navigate to LinkedIn
browser_navigate: {"url": "https://www.linkedin.com/feed/"}

# Step 2: Wait for page to load
browser_wait_for: {"text": "Start a post"}

# Step 3: Click post creation box
browser_snapshot  # Get element refs
browser_click: {"element": "Start a post box", "ref": "e42"}

# Step 4: Type post content
browser_type: {
    "element": "Post text area",
    "ref": "e50",
    "text": "🚀 Exciting News!...",
    "submit": false
}

# Step 5: Add hashtags (already in text)

# Step 6: Click Post button
browser_click: {"element": "Post button", "ref": "e60"}

# Step 7: Wait for confirmation
browser_wait_for: {"text": "Your post has been shared"}

# Step 8: Take screenshot for log
browser_take_screenshot: {"filename": "linkedin_post_20260324.png"}
```

## Content Guidelines

### Best Practices

| Element | Guideline |
|---------|-----------|
| **Length** | 150-300 characters optimal |
| **Hashtags** | 3-5 relevant hashtags |
| **Emoji** | 1-3 for visual appeal |
| **Links** | Include CTA link |
| **Timing** | Post 8-10 AM or 12-1 PM weekdays |
| **Frequency** | 3-5 posts per week |

### Content Types

| Type | Purpose | Example |
|------|---------|---------|
| **Announcement** | New features, launches | "Exciting news..." |
| **Educational** | Tips, how-tos | "5 ways to..." |
| **Social Proof** | Testimonials, results | "Client success..." |
| **Behind Scenes** | Team, culture | "Meet our team..." |
| **Engagement** | Questions, polls | "What's your..." |

## Approval File Format

```markdown
---
type: approval_request
action: linkedin_post
post_id: LINKEDIN_20260324_001
created: 2026-03-24T10:00:00Z
status: pending
---

# 📱 LinkedIn Post Approval

**Post ID:** LINKIN_20260324_001  
**Content:** New Service Launch  
**Scheduled:** 2026-03-25 09:00

---

## Preview

🚀 Exciting News! We're launching our new AI Employee service!
...

## To Approve
Move to `/Approved/`

## To Reject
Move to `/Rejected/`

---

*Approval request for LinkedIn post*
```

## Engagement Tracking

After posting, log:

```markdown
## 📊 Engagement (Post-Post)

| Metric | Value |
|--------|-------|
| Views | (check after 24h) |
| Likes | (check after 24h) |
| Comments | (check after 24h) |
| Shares | (check after 24h) |
```

## Safety Rules

| Rule | Description |
|------|-------------|
| **Always approve** | Never post without approval |
| **Check content** | Verify no typos before posting |
| **Respect limits** | Don't exceed LinkedIn posting limits |
| **Track results** | Log engagement for analysis |
| **Business only** | Only post business-related content |

## Error Handling

- **Login failed:** Notify user, check credentials
- **Post failed:** Save draft, create error report
- **Rate limited:** Wait 24 hours, notify user
- **Element not found:** Re-snapshot page, retry

## Best Practices

1. **Draft first** - Always create draft before posting
2. **Get approval** - Never skip approval step
3. **Schedule wisely** - Post during peak engagement hours
4. **Track results** - Monitor engagement metrics
5. **Vary content** - Mix content types for engagement

## Related Skills

| Skill | Integration |
|-------|-------------|
| `browsing-with-playwright` | Browser automation |
| `hitl-approval-workflow` | Post approval |
| `plan-generator` | Content calendar planning |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't login | Check credentials, 2FA status |
| Post button not found | Refresh page, re-snapshot |
| Character limit | LinkedIn allows 3000 chars |
| Post not visible | Check privacy settings |

---

*Skill version: 1.0 | Silver Tier | Compatible with Qwen Code*
