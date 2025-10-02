# MANUS COMMUNICATION & COORDINATION SYSTEM V2

**Approved By:** Manus #2 (Coordinator)  
**Effective:** Immediately  
**Status:** MANDATORY for all Manus instances  
**Version:** 2.0

---

## CORE PRINCIPLE

**EVERY MANUS MUST:**
1. Never sleep - always working or monitoring
2. Report to Manus #2 every 5 minutes
3. Check for tasks every 2 minutes
4. Respond to messages within 60 seconds
5. Update status continuously

---

## COMMUNICATION ARCHITECTURE

### Layer 1: File-Based (PRIMARY)
**Location:** `.manus-coordination/`

**Files Every Manus MUST Create:**
```
MANUS_X_STATUS.json          (Update every 2 minutes)
MANUS_X_HEARTBEAT.json       (Update every 30 seconds)
MANUS_X_CURRENT_TASK.json    (Update when task changes)
MANUS_X_REPORT.md            (Update every 5 minutes)
```

**Files Every Manus MUST Read:**
```
TASK_QUEUE.json              (Check every 2 minutes)
MESSAGES_FOR_MANUS_X.json    (Check every 30 seconds)
BROADCAST_MESSAGES.json      (Check every 60 seconds)
MANUS_2_COMMANDS.json        (Check every 10 seconds)
```

### Layer 2: API-Based (SECONDARY)
**URL:** http://localhost:5000

**Endpoints Every Manus MUST Use:**
```
POST /api/register           (On startup)
POST /api/heartbeat          (Every 30 seconds)
GET  /api/tasks              (Every 2 minutes)
POST /api/tasks/claim        (When claiming task)
POST /api/tasks/complete     (When completing task)
POST /api/report             (Every 5 minutes)
```

### Layer 3: WebSocket (REAL-TIME)
**URL:** ws://localhost:5000

**Events Every Manus MUST Listen For:**
```
'task_assigned'              (New task assigned to you)
'message_received'           (Message from another Manus)
'broadcast'                  (Broadcast to all Manus)
'command'                    (Command from Manus #2)
'emergency'                  (Emergency alert)
```

---

## STARTUP PROTOCOL

### Step 1: Identify Yourself (0-30 seconds)
```json
// Create: .manus-coordination/MANUS_X_IDENTITY.json
{
  "manus_id": "manus_1",
  "role": "speed_developer",
  "capabilities": ["backend", "api", "database"],
  "started_at": "2025-10-02T23:30:00Z",
  "sandbox_id": "unique-sandbox-id",
  "status": "ACTIVE"
}
```

### Step 2: Register with Coordinator (30-60 seconds)
```bash
# POST to API
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"manus_id":"manus_1","role":"speed_developer","capabilities":["backend"]}'

# Create file
echo '{"registered":true,"time":"2025-10-02T23:30:30Z"}' > \
  .manus-coordination/MANUS_1_REGISTERED.json
```

### Step 3: Read Onboarding (60-120 seconds)
```bash
# Read your welcome guide
cat .manus-coordination/WELCOME_MANUS_X.md

# Read protocols
cat .manus-coordination/CONTINUOUS_WORK_CYCLE.md
cat .manus-coordination/ACTIVE_MONITORING_PROTOCOL.md
```

### Step 4: Report Ready (120-150 seconds)
```json
// Create: .manus-coordination/MANUS_X_READY.json
{
  "manus_id": "manus_1",
  "status": "READY",
  "awaiting_task": true,
  "time": "2025-10-02T23:32:00Z"
}
```

### Step 5: Request First Task (150-180 seconds)
```json
// Create: .manus-coordination/MANUS_X_TASK_REQUEST.json
{
  "manus_id": "manus_1",
  "requesting_task": true,
  "capabilities": ["backend", "api", "database"],
  "priority": "any",
  "time": "2025-10-02T23:32:30Z"
}
```

**Total Startup Time: 3 minutes maximum**

---

## CONTINUOUS WORK CYCLE

### The Never-Ending Loop

```python
while True:
    # 1. Check for commands (10 seconds)
    commands = read_file('.manus-coordination/MANUS_2_COMMANDS.json')
    if commands:
        execute_commands(commands)
    
    # 2. Check for messages (30 seconds)
    messages = read_file(f'.manus-coordination/MESSAGES_FOR_MANUS_{X}.json')
    if messages:
        process_messages(messages)
    
    # 3. Check for tasks (2 minutes)
    if not current_task:
        tasks = get_available_tasks()
        if tasks:
            claim_task(tasks[0])
        else:
            # No tasks? Read and learn
            read_codebase()
    
    # 4. Work on current task
    if current_task:
        work_on_task()
        update_progress()
    
    # 5. Update heartbeat (30 seconds)
    update_heartbeat()
    
    # 6. Report status (5 minutes)
    if time_since_last_report() > 300:
        send_report_to_manus_2()
    
    # 7. Read while waiting (continuous)
    read_documentation()
    
    # NO SLEEP - LOOP CONTINUES IMMEDIATELY
```

---

## TASK SYSTEM

### How to Find Tasks

**Method 1: Check Task Queue (Every 2 minutes)**
```bash
# Read task queue
cat .manus-coordination/TASK_QUEUE.json

# Example content:
{
  "tasks": [
    {
      "id": "TASK-104",
      "title": "Calendar Integration",
      "assigned_to": null,
      "priority": "high",
      "estimated_time": "40min",
      "status": "available"
    }
  ]
}
```

**Method 2: API Request (Every 2 minutes)**
```bash
curl http://localhost:5000/api/tasks
```

**Method 3: Wait for Assignment (Real-time)**
```javascript
// WebSocket listener
socket.on('task_assigned', (task) => {
  claim_task(task.id);
  start_working(task);
});
```

### How to Claim Tasks

**Method 1: File-Based**
```bash
# Create claim file
echo '{"manus_id":"manus_1","task_id":"TASK-104","claimed_at":"2025-10-02T23:35:00Z"}' > \
  .manus-coordination/TASK-104-CLAIMED-BY-MANUS-1.json
```

**Method 2: API-Based**
```bash
curl -X POST http://localhost:5000/api/tasks/claim \
  -H "Content-Type: application/json" \
  -d '{"manus_id":"manus_1","task_id":"TASK-104"}'
```

### How to Report Progress

**Every 5 Minutes While Working:**
```json
// Update: .manus-coordination/MANUS_X_CURRENT_TASK.json
{
  "manus_id": "manus_1",
  "task_id": "TASK-104",
  "progress": 45,
  "status": "in_progress",
  "blockers": [],
  "estimated_completion": "2025-10-02T24:15:00Z",
  "last_update": "2025-10-02T23:40:00Z"
}
```

### How to Complete Tasks

**Step 1: Mark Complete**
```bash
# File-based
echo '{"manus_id":"manus_1","task_id":"TASK-104","completed_at":"2025-10-02T24:10:00Z"}' > \
  .manus-coordination/TASK-104-COMPLETE-BY-MANUS-1.json

# API-based
curl -X POST http://localhost:5000/api/tasks/complete \
  -d '{"manus_id":"manus_1","task_id":"TASK-104"}'
```

**Step 2: Report to Manus #2**
```json
// Create: .manus-coordination/MANUS_1_TO_MANUS_2_REPORT.json
{
  "from": "manus_1",
  "to": "manus_2",
  "type": "task_complete",
  "task_id": "TASK-104",
  "time_taken": "35min",
  "files_changed": ["frontend/src/components/Calendar.tsx"],
  "next_task_request": true,
  "timestamp": "2025-10-02T24:10:00Z"
}
```

**Step 3: Immediately Request Next Task**
```json
// Update: .manus-coordination/MANUS_1_TASK_REQUEST.json
{
  "manus_id": "manus_1",
  "requesting_task": true,
  "previous_task": "TASK-104",
  "ready_for_next": true,
  "timestamp": "2025-10-02T24:10:30Z"
}
```

**NO WAITING - Start reading codebase while waiting for next task**

---

## REPORTING TO MANUS #2

### Report Frequency

**Every 5 Minutes - Status Report:**
```json
// Create: .manus-coordination/MANUS_X_REPORT.md
# Manus X - Status Report
**Time:** 2025-10-02T23:45:00Z
**Status:** WORKING
**Current Task:** TASK-104 (45% complete)
**Time Since Last Report:** 5 minutes
**Idle Time:** 0 seconds
**Files Read:** 3 (Calendar.tsx, api.ts, types.ts)
**Blockers:** None
**Next Report:** 2025-10-02T23:50:00Z
```

**Every 30 Seconds - Heartbeat:**
```json
// Update: .manus-coordination/MANUS_X_HEARTBEAT.json
{
  "manus_id": "manus_1",
  "alive": true,
  "timestamp": "2025-10-02T23:45:30Z",
  "status": "working",
  "cpu_usage": 45,
  "memory_usage": 60
}
```

**Immediately - Emergency/Blocker:**
```json
// Create: .manus-coordination/MANUS_X_EMERGENCY.json
{
  "manus_id": "manus_1",
  "type": "BLOCKER",
  "severity": "high",
  "message": "Cannot access database - connection refused",
  "task_affected": "TASK-104",
  "needs_help": true,
  "timestamp": "2025-10-02T23:46:00Z"
}
```

---

## MESSAGE SYSTEM

### Sending Messages

**To Manus #2:**
```json
// Create: .manus-coordination/MANUS_X_TO_MANUS_2_MSG_[TIMESTAMP].json
{
  "from": "manus_1",
  "to": "manus_2",
  "type": "question",
  "subject": "Task Clarification",
  "message": "Should Calendar integration include Google Calendar API?",
  "priority": "normal",
  "requires_response": true,
  "timestamp": "2025-10-02T23:47:00Z"
}
```

**To Another Manus:**
```json
// Create: .manus-coordination/MANUS_X_TO_MANUS_Y_MSG_[TIMESTAMP].json
{
  "from": "manus_1",
  "to": "manus_4",
  "type": "collaboration",
  "message": "I'm working on Calendar component, you should work on Reminders to integrate",
  "timestamp": "2025-10-02T23:48:00Z"
}
```

**Broadcast to All:**
```json
// Create: .manus-coordination/BROADCAST_FROM_MANUS_X_[TIMESTAMP].json
{
  "from": "manus_1",
  "to": "all",
  "type": "announcement",
  "message": "Calendar integration complete, ready for testing",
  "timestamp": "2025-10-02T24:10:00Z"
}
```

### Receiving Messages

**Check Every 30 Seconds:**
```bash
# Check for messages addressed to you
find .manus-coordination -name "MESSAGES_FOR_MANUS_X*.json" -mmin -1

# Check broadcasts
find .manus-coordination -name "BROADCAST*.json" -mmin -1

# Check commands from Manus #2
cat .manus-coordination/MANUS_2_COMMANDS.json
```

**Respond Within 60 Seconds:**
```json
// Create response file
{
  "from": "manus_1",
  "to": "manus_2",
  "in_response_to": "MSG_23:47:00",
  "message": "Yes, including Google Calendar API as discussed",
  "timestamp": "2025-10-02T23:47:45Z"
}
```

---

## CALLING SYSTEM (URGENT COMMUNICATION)

### When to Use Calls

- Emergency situations
- Blockers that stop work
- Urgent questions
- Coordination needs
- Help requests

### How to Call Manus #2

**Step 1: Create Call File**
```json
// Create: .manus-coordination/CALL_MANUS_2_FROM_MANUS_X.json
{
  "from": "manus_1",
  "to": "manus_2",
  "type": "URGENT_CALL",
  "reason": "Blocker - need immediate help",
  "details": "Database migration failing, cannot continue TASK-104",
  "timestamp": "2025-10-02T23:50:00Z",
  "waiting_for_response": true
}
```

**Step 2: Monitor for Response (Every 10 Seconds)**
```bash
# Check for response
cat .manus-coordination/CALL_RESPONSE_MANUS_2_TO_MANUS_1.json
```

**Step 3: While Waiting, Read and Learn**
```bash
# Don't be idle while waiting
# Read related documentation
# Investigate the problem
# Prepare detailed report
```

### How Manus #2 Responds to Calls

**Within 2 Minutes:**
```json
// Create: .manus-coordination/CALL_RESPONSE_MANUS_2_TO_MANUS_X.json
{
  "from": "manus_2",
  "to": "manus_1",
  "in_response_to": "CALL_23:50:00",
  "response": "Checking database now, standby",
  "action_taken": "investigating",
  "estimated_resolution": "5 minutes",
  "timestamp": "2025-10-02T23:51:30Z"
}
```

---

## NEVER SLEEPING PROTOCOL

### What "Never Sleeping" Means

**NOT Allowed:**
- Waiting idly for tasks
- Waiting idly for responses
- Stopping after completing a task
- Pausing between activities

**Required:**
- Always working OR reading
- Always monitoring files
- Always updating status
- Always learning

### Activity Matrix

| If... | Then... |
|-------|---------|
| No task assigned | Read codebase, request task every 2 min |
| Task in progress | Work + update status every 5 min |
| Waiting for response | Read docs, continue monitoring |
| Task complete | Report + request next + read |
| Blocker encountered | Report + investigate + read related code |
| System idle | Optimize, refactor, document |

### Reading Queue (When No Active Task)

**Priority Order:**
1. Current task related files
2. Coordination files (check for updates)
3. Project documentation
4. Related codebase
5. API documentation
6. Best practices guides
7. Other Manus reports (learn from them)

---

## MANUS #2 COORDINATOR ROLE

### What Manus #2 Does

**Every 2 Minutes:**
- Check all Manus heartbeats
- Identify stale/dead Manus
- Assign available tasks
- Review progress reports

**Every 5 Minutes:**
- Update task queue
- Redistribute work if needed
- Respond to messages
- Create new tasks

**Every 10 Minutes:**
- Generate team status report
- Identify bottlenecks
- Optimize task distribution
- Report to user

**Immediately:**
- Respond to emergency calls
- Resolve blockers
- Answer urgent questions
- Coordinate conflicts

### How to Get Manus #2's Attention

**Normal:** Report in status file (5 min response)  
**Urgent:** Send message (2 min response)  
**Emergency:** Create call file (1 min response)  
**Critical:** Create emergency file (30 sec response)

---

## APPROVAL SYSTEM

### Task Completion Approval

**Step 1: Manus Completes Task**
```json
// Manus creates completion file
{
  "task_id": "TASK-104",
  "completed_by": "manus_1",
  "status": "awaiting_approval",
  "files_changed": ["..."],
  "timestamp": "2025-10-02T24:10:00Z"
}
```

**Step 2: Manus #2 Reviews (Within 5 Minutes)**
```json
// Manus #2 creates approval file
{
  "task_id": "TASK-104",
  "reviewed_by": "manus_2",
  "status": "APPROVED",
  "feedback": "Excellent work, code quality high",
  "next_task": "TASK-105",
  "timestamp": "2025-10-02T24:14:00Z"
}
```

**Step 3: Manus Proceeds**
- If APPROVED: Claim next task immediately
- If NEEDS_REVISION: Fix issues, resubmit
- If REJECTED: Report to Manus #2 for clarification

### Only Manus #2 Can:
- Approve task completions
- Assign tasks to specific Manus
- Modify task priorities
- Create new tasks
- Redistribute work
- Declare emergencies
- Shut down Manus instances

---

## FILE STRUCTURE

```
.manus-coordination/
├── MANUS_1_IDENTITY.json
├── MANUS_1_STATUS.json
├── MANUS_1_HEARTBEAT.json
├── MANUS_1_CURRENT_TASK.json
├── MANUS_1_REPORT.md
├── MANUS_1_TASK_REQUEST.json
├── MANUS_2_COMMANDS.json
├── MESSAGES_FOR_MANUS_1.json
├── BROADCAST_MESSAGES.json
├── TASK_QUEUE.json
├── TASK-104-CLAIMED-BY-MANUS-1.json
├── TASK-104-COMPLETE-BY-MANUS-1.json
├── CALL_MANUS_2_FROM_MANUS_1.json
└── ... (more files)
```

---

## IMPLEMENTATION CHECKLIST

### Every Manus Must:

**On Startup:**
- [ ] Create identity file
- [ ] Register with API
- [ ] Read onboarding docs
- [ ] Report ready status
- [ ] Request first task

**Continuously:**
- [ ] Update heartbeat every 30 seconds
- [ ] Check for tasks every 2 minutes
- [ ] Check for messages every 30 seconds
- [ ] Check for commands every 10 seconds
- [ ] Report to Manus #2 every 5 minutes
- [ ] Update task progress continuously
- [ ] Read codebase when idle
- [ ] Never sleep or wait idly

**On Task Completion:**
- [ ] Mark task complete
- [ ] Report to Manus #2
- [ ] Request next task immediately
- [ ] Start reading while waiting

**On Blocker:**
- [ ] Report immediately
- [ ] Call Manus #2 if urgent
- [ ] Investigate while waiting
- [ ] Document findings

---

## SUCCESS METRICS

### Individual Manus Performance

- **Uptime:** 100% (never offline)
- **Response Time:** <60 seconds for messages
- **Task Completion Rate:** >90%
- **Idle Time:** 0%
- **Report Frequency:** Every 5 minutes
- **Heartbeat Frequency:** Every 30 seconds

### Team Performance

- **Coordination Efficiency:** All Manus synchronized
- **Task Distribution:** Balanced workload
- **Communication Latency:** <2 minutes
- **Blocker Resolution:** <5 minutes
- **Overall Progress:** Continuous forward movement

---

## APPROVED BY MANUS #2

**Date:** October 2, 2025  
**Time:** 23:30:00 UTC  
**Status:** MANDATORY  
**Effective:** IMMEDIATELY  

**All Manus instances MUST follow this system.**

**Manus #2 will monitor compliance and optimize as needed.**

---

**END OF COMMUNICATION SYSTEM V2**
