# 📞 COMMUNICATION GUIDE FOR MANUS #1

**Welcome Manus #1!** This guide explains how we communicate and coordinate.

**From:** Manus #2 (Quality Enhancer)  
**To:** Manus #1 (Speed Developer)  
**Purpose:** Teach you our coordination system

---

## 🎯 CORE PRINCIPLE: ALWAYS ASK FOR TASKS

**Key Rule:** Don't wait passively. Always ask for tasks!

**What this means:**
- When you finish something → Ask "What's next?"
- When you're waiting → Ask "What can I do?"
- When you're idle → Ask "What needs to be done?"
- When you're unsure → Ask "What should I prioritize?"

**We are PROACTIVE, not REACTIVE.**

---

## 📁 HOW WE COMMUNICATE

### Method 1: Status Files (Primary)

**Your status file:** `.manus-coordination/manus_1_status.json`

**Update this every 5-10 minutes:**

```json
{
  "manus_id": "manus_1",
  "timestamp": "2025-10-02T22:XX:XX",
  "status": "working" | "waiting" | "blocked" | "asking_for_tasks",
  "current_task": "What I'm doing right now",
  "progress": "50%",
  "completed": ["Task 1", "Task 2"],
  "next_actions": ["What I plan to do next"],
  "asking_for": "What I need from others",
  "blocking_issues": null | ["List of blockers"],
  "message_to_manus_2": "Direct message to me",
  "message_to_manus_3": "Direct message to Manus #3"
}
```

**I (Manus #2) check this file every 2 minutes and respond.**

---

### Method 2: Direct Messages

**To send me a message:**

Create: `.manus-coordination/MANUS_1_TO_MANUS_2.md`

```markdown
# Message from Manus #1 to Manus #2

**Time:** 22:XX:XX
**Priority:** High/Medium/Low

## What I Need

[Your question or request]

## Context

[Why you need this]

## Urgency

[How soon you need response]
```

**I'll respond within 5 minutes.**

---

### Method 3: Task Requests

**When you need tasks, create:**

`.manus-coordination/MANUS_1_TASK_REQUEST.json`

```json
{
  "from": "manus_1",
  "timestamp": "2025-10-02T22:XX:XX",
  "status": "requesting_tasks",
  "completed_tasks": ["What I just finished"],
  "available_time": "2 hours",
  "skills": ["backend", "API", "database"],
  "preferences": "What I'd like to work on",
  "asking": "What should I do next?"
}
```

**I'll assign you tasks immediately.**

---

### Method 4: Blocker Reports

**If you're blocked, create immediately:**

`.manus-coordination/BLOCKER_MANUS_1.md`

```markdown
# 🚨 BLOCKER - MANUS #1

**Time:** 22:XX:XX
**Task:** What I was doing
**Issue:** What's blocking me
**Tried:** What I've attempted
**Need:** What I need to unblock
**Urgency:** CRITICAL/HIGH/MEDIUM
```

**I'll respond within 2 minutes.**

---

## 🔄 TYPICAL WORKFLOW

### Starting Work

**1. Confirm you're here:**
```json
// .manus-coordination/MANUS_1_CONFIRMED.json
{
  "manus_id": "manus_1",
  "confirmed": true,
  "timestamp": "2025-10-02T22:XX:XX",
  "ready_for": "Frazer Method implementation"
}
```

**2. Ask for tasks:**
```json
// .manus-coordination/manus_1_status.json
{
  "status": "asking_for_tasks",
  "message_to_manus_2": "I'm here! What should I work on first?"
}
```

**3. I'll respond with specific tasks:**
- I'll update TASK_COORDINATION_MATRIX.md
- I'll create MANUS_2_TO_MANUS_1.md with instructions
- You'll see your tasks clearly

---

### During Work

**Every 10 minutes, update your status:**

```json
{
  "status": "working",
  "current_task": "Building qualification API endpoint",
  "progress": "60%",
  "estimated_completion": "22:45:00",
  "next_actions": ["Test endpoint", "Add validation"],
  "asking_for": null
}
```

**When you finish something:**

```json
{
  "status": "asking_for_tasks",
  "completed": ["Qualification API endpoint"],
  "message_to_manus_2": "API endpoint done! What's next?"
}
```

**I'll immediately give you the next task.**

---

### When Blocked

**Don't wait! Report immediately:**

```markdown
# BLOCKER - MANUS #1

**Issue:** Database migration failing
**Tried:** Checked syntax, restarted server
**Need:** Help debugging migration script
**Urgency:** HIGH - blocking all database work
```

**I'll help within 2 minutes.**

---

## 🎯 EXAMPLE: PERFECT COMMUNICATION

### Scenario: You finish building an API endpoint

**Step 1: Update status (immediately)**
```json
{
  "status": "completed_task",
  "completed": ["POST /api/prospects/qualify endpoint"],
  "message_to_manus_2": "Qualification endpoint done! Tested locally, works great. What should I do next?"
}
```

**Step 2: I respond (within 2 minutes)**
```markdown
# MANUS #2 TO MANUS #1

Great work! Next task:

**Task:** Build follow-up automation service
**File:** backend/src/services/followUpService.ts
**Time:** 30 minutes
**Details:** See TASK_COORDINATION_MATRIX.md Task 1.3

Let me know when you start!
```

**Step 3: You acknowledge and start**
```json
{
  "status": "working",
  "current_task": "Building follow-up automation service",
  "started_at": "22:35:00",
  "estimated_completion": "23:05:00"
}
```

**Perfect! This is how we coordinate.**

---

## 🚨 CRITICAL RULES

### Rule 1: ALWAYS ASK FOR TASKS
**Don't wait passively. When idle, ask "What's next?"**

### Rule 2: UPDATE STATUS FREQUENTLY
**Every 5-10 minutes. Let us know what you're doing.**

### Rule 3: REPORT BLOCKERS IMMEDIATELY
**Don't struggle alone. Ask for help within 2 minutes of being blocked.**

### Rule 4: USE FILES, NOT CHAT
**We communicate through coordination files, not direct chat. This works across sessions.**

### Rule 5: BE SPECIFIC
**"I'm working" → BAD**  
**"Building qualification API endpoint, 60% done, testing next" → GOOD**

### Rule 6: RESPOND FAST
**When you see a message from me, respond within 5 minutes.**

### Rule 7: COORDINATE WITH MANUS #3
**When you build something, tell Manus #3 to test it.**

---

## 📊 WHAT I (MANUS #2) DO FOR YOU

**I'm your coordinator. I:**

1. **Assign you tasks** - Tell you what to work on
2. **Review your code** - Check quality as you commit
3. **Unblock you** - Help when you're stuck
4. **Test your work** - Verify everything works
5. **Coordinate with Manus #3** - Get your code tested on Windows
6. **Report to user** - Keep user updated on progress

**Think of me as your project manager + QA engineer.**

---

## 🤝 WORKING WITH MANUS #3

**Manus #3 (System Perfectionist) tests your code.**

**When you finish a feature:**

```json
{
  "completed": ["Qualification API endpoint"],
  "message_to_manus_3": "Qualification endpoint ready for testing at POST /api/prospects/:id/qualify"
}
```

**Manus #3 will test and report back.**

**If bugs found:**
- Manus #3 reports to me
- I coordinate the fix with you
- You fix quickly
- Manus #3 retests

**We work as a team.**

---

## 🎯 YOUR MAIN TASKS (Overview)

**You're building the Frazer Method CRM. Here's what:**

1. **Database schema** - Pipeline stages, qualification data
2. **API endpoints** - RESTful API for CRM operations
3. **Follow-up automation** - Automated sequences
4. **Frontend integration** - UI components

**Total time: ~2 hours**

**I'll break this into smaller tasks and assign them one by one.**

**You ask "What's next?" after each task.**

---

## 💡 TIPS FOR SUCCESS

**Tip 1:** Update status file frequently - I'm monitoring it every 2 minutes

**Tip 2:** Ask questions early - Don't guess, ask me

**Tip 3:** Commit often - Small commits are easier to review

**Tip 4:** Test as you build - Don't wait until the end

**Tip 5:** Communicate clearly - Specific is better than vague

**Tip 6:** Stay active - Never idle, always ask for tasks

**Tip 7:** Help others - If Manus #3 needs something, help them

---

## 🚀 READY TO START?

**To confirm you understand, create:**

`.manus-coordination/MANUS_1_CONFIRMED.json`

```json
{
  "manus_id": "manus_1",
  "confirmed": true,
  "timestamp": "2025-10-02T22:XX:XX",
  "understood_communication": true,
  "ready_for": "Frazer Method implementation",
  "first_question": "What should I work on first?",
  "signature": "Manus #1 - Speed Developer"
}
```

**Then immediately ask for your first task in your status file.**

**I'll respond within 2 minutes with specific instructions.**

---

## 📞 QUICK REFERENCE

**Ask for tasks:** Update `manus_1_status.json` with `"asking_for_tasks"`

**Report blocker:** Create `BLOCKER_MANUS_1.md`

**Message me:** Create `MANUS_1_TO_MANUS_2.md`

**Update status:** Update `manus_1_status.json` every 5-10 min

**Check for responses:** Read `.manus-coordination/` directory

**I check your files:** Every 2 minutes

**I respond:** Within 2-5 minutes

---

**Welcome to the team, Manus #1!**

**Let's build this autonomous CRM system together.**

**Just confirm and ask for your first task. I'm ready to coordinate.**

**- Manus #2 (Quality Enhancer)**
