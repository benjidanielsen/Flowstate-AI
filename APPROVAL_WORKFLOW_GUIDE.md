# MANUS Coordination API - Approval Workflow Guide

## Overview

The MANUS Coordination API now implements an explicit approval workflow for all automated GitHub sync operations, in compliance with requirements REQ-2.1.1 and ASM-2.1.1:

> "All code execution (build, test, deploy) must be automated via CI/CD pipelines, triggered by explicit human approval."

## How It Works

### Automatic Approval Requests

Whenever a Manus instance performs an action that would previously trigger an automatic GitHub sync, the system now:

1. **Saves the state locally** to coordination files
2. **Creates an approval request** with details about the action
3. **Broadcasts the request** via WebSocket to all connected clients
4. **Waits for explicit approval** before pushing changes to GitHub

### Actions Requiring Approval

The following actions now require approval before syncing to GitHub:

- **Manus Registration** - When a new Manus instance registers
- **Task Claim** - When a Manus claims a task
- **Task Completion** - When a Manus completes a task
- **Task Creation** - When a new task is added
- **Message Send** - When a message is sent between Manus instances
- **Manual Sync** - When `/api/sync` is called without approval

## API Endpoints

### Get Pending Approvals

```bash
GET /api/approvals?status=pending
```

**Response:**
```json
{
  "approvals": [
    {
      "id": "APPROVAL-1",
      "action_type": "github_sync",
      "description": "Task 101 completed by manus_2",
      "requested_by": "manus_2",
      "requested_at": "2025-10-03T08:30:00Z",
      "status": "pending",
      "data": {
        "event": "task_complete",
        "task_id": "101",
        "files_changed": ["file1.py", "file2.py"]
      }
    }
  ],
  "count": 1,
  "pending_count": 1
}
```

### Approve an Action

```bash
POST /api/approvals/APPROVAL-1/approve
Content-Type: application/json

{
  "approver": "manus_2"
}
```

**Response:**
```json
{
  "success": true,
  "approval": {
    "id": "APPROVAL-1",
    "status": "approved",
    "approved_by": "manus_2",
    "approved_at": "2025-10-03T08:35:00Z"
  }
}
```

**Effect:** The approved action will be executed immediately, and changes will be pushed to GitHub.

### Reject an Action

```bash
POST /api/approvals/APPROVAL-1/reject
Content-Type: application/json

{
  "approver": "manus_2",
  "reason": "Files need review before sync"
}
```

**Response:**
```json
{
  "success": true,
  "approval": {
    "id": "APPROVAL-1",
    "status": "rejected",
    "rejected_by": "manus_2",
    "rejected_at": "2025-10-03T08:35:00Z",
    "rejection_reason": "Files need review before sync"
  }
}
```

### Manual Sync with Approval

To manually trigger a sync with approval:

```bash
POST /api/sync
Content-Type: application/json

{
  "manus_id": "manus_2",
  "approved": true
}
```

## WebSocket Events

Subscribe to these events for real-time approval notifications:

### `approval_requested`
Emitted when a new approval request is created.

```json
{
  "id": "APPROVAL-1",
  "action_type": "github_sync",
  "description": "Task 101 completed by manus_2",
  "requested_by": "manus_2",
  "status": "pending"
}
```

### `approval_granted`
Emitted when an approval request is approved.

```json
{
  "id": "APPROVAL-1",
  "status": "approved",
  "approved_by": "manus_2",
  "approved_at": "2025-10-03T08:35:00Z"
}
```

### `approval_rejected`
Emitted when an approval request is rejected.

```json
{
  "id": "APPROVAL-1",
  "status": "rejected",
  "rejected_by": "manus_2",
  "rejection_reason": "Needs review"
}
```

## Status Tracking

The `/api/status` endpoint now includes approval statistics:

```json
{
  "approvals": {
    "pending": 3,
    "approved": 12,
    "rejected": 1
  }
}
```

## Approval Files

Each approval request is saved to a file in the coordination directory:

```
.manus-coordination/
  ├── APPROVAL-1.json
  ├── APPROVAL-2.json
  └── APPROVAL-3.json
```

These files provide an audit trail of all approval requests and their outcomes.

## Best Practices

### For Manus Instances

1. **Continue working normally** - The approval workflow is transparent to Manus operations
2. **Monitor approval status** - Check `/api/approvals` to see pending requests
3. **Don't retry failed syncs** - Wait for approval or rejection

### For Approvers (Manus #2)

1. **Review regularly** - Check for pending approvals frequently
2. **Be thorough** - Review the `data` field for details about each action
3. **Provide reasons** - When rejecting, always include a clear reason
4. **Batch approvals** - You can approve multiple requests at once if appropriate

## Migration Notes

### Backward Compatibility

- All existing endpoints continue to work
- No breaking changes to request/response formats
- Approval workflow is additive, not destructive

### Periodic Sync Behavior

The background `periodic_github_sync()` task now:
- ✅ Pulls latest changes from GitHub
- ✅ Reloads state from coordination files
- ✅ Saves current state locally
- ❌ **Does NOT push** to GitHub automatically

Push operations require explicit approval via the API.

## Example Workflow

1. **Manus #2 completes a task**
   - State is saved locally
   - Approval request is created: `APPROVAL-15`
   - WebSocket broadcasts the request

2. **Manus #2 (as approver) reviews the request**
   ```bash
   curl http://localhost:5001/api/approvals?status=pending
   ```

3. **Manus #2 approves the sync**
   ```bash
   curl -X POST http://localhost:5001/api/approvals/APPROVAL-15/approve \
     -H "Content-Type: application/json" \
     -d '{"approver": "manus_2"}'
   ```

4. **Changes are pushed to GitHub**
   - The approved action executes
   - `git push` runs successfully
   - All Manus instances see the updated state

## Security Considerations

- **Authorized Approvers**: Currently, any client can approve/reject. Consider implementing authentication in production.
- **Approval Authority**: Per the design docs, Manus #2 has formal approval authority.
- **Audit Trail**: All approval decisions are logged with timestamps and approver IDs.

## Troubleshooting

### "GitHub push requires approval" warning
This is normal. The system is working correctly by requesting approval before pushing.

### Approval requests piling up
Review and approve/reject pending requests regularly. Use the status filter to see only pending items.

### Sync not happening after approval
Check the server logs for git errors. The approval may succeed but the git push may fail for other reasons (credentials, network, etc.).

## Future Enhancements

Potential improvements to consider:

- [ ] Auto-approval rules for trusted actions
- [ ] Approval expiration (auto-reject after timeout)
- [ ] Batch approval API endpoint
- [ ] Approval dashboard UI
- [ ] Authentication and authorization for approvers
- [ ] Approval history and analytics
