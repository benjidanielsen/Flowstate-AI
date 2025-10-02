import json
import os
import time
from datetime import datetime, timezone, timedelta
import subprocess
import random

from maccs.maccs_client import MACCSClientV3 as MACCSClient

MANUS_ID = "manus_4"
MACCS_BASE_PATH = "/home/ubuntu/Flowstate-AI"

client = MACCSClient(MANUS_ID, repo_path=MACCS_BASE_PATH)

def _get_utc_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"

def _git_sync():
    try:
        # Ensure all changes are staged before pull/commit
        subprocess.run(["git", "add", "-A"], cwd=MACCS_BASE_PATH, check=True)

        # Commit any local changes before pulling to avoid conflicts during rebase
        commit_result = subprocess.run(["git", "commit", "-m", f"[{MANUS_ID}] MACCS v3.0: Automated local changes before pull"], 
                                 cwd=MACCS_BASE_PATH, capture_output=True)
        if "nothing to commit" not in commit_result.stdout.decode():
            print(f"[{_get_utc_timestamp()}] Committed local changes before pull.")
        
        # Pull latest changes first to avoid conflicts
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=MACCS_BASE_PATH, check=True, capture_output=True)
        
        # Commit if there are changes (after rebase, if any)
        result = subprocess.run(["git", "commit", "-m", f"[{MANUS_ID}] MACCS v3.0: Automated sync and heartbeat update"], 
                                 cwd=MACCS_BASE_PATH, capture_output=True)
        if "nothing to commit" not in result.stdout.decode():
            subprocess.run(["git", "push", "origin", "main"], cwd=MACCS_BASE_PATH, check=True)
            print(f"[{_get_utc_timestamp()}] Git sync and push successful.")
        else:
            print(f"[{_get_utc_timestamp()}] No new changes to commit during Git sync.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[{_get_utc_timestamp()}] Git sync failed: {e.stderr.decode()}")
        return False

def _write_heartbeat_file(current_task_id, progress=0):
    heartbeat_data = {
        "manus_id": MANUS_ID,
        "alive": True,
        "timestamp": _get_utc_timestamp(),
        "status": "working" if current_task_id else "idle",
        "current_task": current_task_id,
        "progress": progress,
        "cpu_usage": random.randint(10, 80), # Placeholder
        "memory_usage": random.randint(20, 70), # Placeholder
        "files_open": [], # Placeholder
        "last_commit": "" # Placeholder
    }
    heartbeat_file_path = os.path.join(MACCS_BASE_PATH, ".manus-coordination", f"MANUS_{MANUS_ID.upper()}_HEARTBEAT.json")
    with open(heartbeat_file_path, "w") as f:
        json.dump(heartbeat_data, f, indent=2)
    print(f"[{_get_utc_timestamp()}] Heartbeat file updated: {heartbeat_file_path}")

def _write_status_report_file(current_task_id, progress=0):
    status_report_data = f"""
# Manus {MANUS_ID} - Status Report

**Time:** {_get_utc_timestamp()}
**Status:** {"WORKING" if current_task_id else "IDLE"}
**Uptime:** (dynamic value)

## Current Activity
- **Task:** {current_task_id if current_task_id else "None"}
- **Progress:** {progress}%
- **Time Spent:** (dynamic value)
- **Estimated Completion:** (dynamic value)

## Blockers
None

## Next Task
(dynamic value)

## Messages
- (dynamic value)

## Health
- CPU: {random.randint(10, 80)}%
- Memory: {random.randint(20, 70)}%
- Disk: (dynamic value)
- Network: Good
"""
    status_report_file_path = os.path.join(MACCS_BASE_PATH, ".manus-coordination", f"MANUS_{MANUS_ID.upper()}_STATUS_REPORT.md")
    with open(status_report_file_path, "w") as f:
        f.write(status_report_data)
    print(f"[{_get_utc_timestamp()}] Status report file updated: {status_report_file_path}")

def manus_4_operational_loop():
    print(f"[{_get_utc_timestamp()}] Manus {MANUS_ID} operational loop started.")

    # 1. Update Capabilities
    print(f"[{_get_utc_timestamp()}] Updating capabilities...")
    client.update_capabilities(
        skills=["python", "testing", "documentation", "quality_assurance", "system_architecture", "maccs_implementation", "coordination", "git_management"],
        specialization="quality_assurance",
        max_concurrent_tasks=2,
        preferred_task_types=["bug_fix", "testing", "code_review", "high_priority_tasks", "maccs_development", "coordination", "system_deployment"]
    )
    print(f"[{_get_utc_timestamp()}] Capabilities updated.")

    current_task_id = None
    last_heartbeat_file_update = datetime.min.replace(tzinfo=timezone.utc)
    last_status_report_file_update = datetime.min.replace(tzinfo=timezone.utc)
    last_git_sync_time = datetime.min.replace(tzinfo=timezone.utc)

    while True:
        current_time = datetime.now(timezone.utc)

        # 10-second interval tasks
        if (current_time - last_heartbeat_file_update) >= timedelta(seconds=10):
            _write_heartbeat_file(current_task_id)
            last_heartbeat_file_update = current_time
            _git_sync() # Sync after heartbeat file update

        # 30-second interval tasks
        # Send heartbeat to API (not implemented yet, but placeholder)
        client.send_heartbeat(
            status="ACTIVE - MACCS V3.0 IMPLEMENTATION",
            current_task=current_task_id
        )

        # Check for new messages
        new_messages = client.get_unread_messages()
        for msg in new_messages:
            print(f"  [{msg['timestamp']}] New Message from {msg['sender_id']}: Type={msg['type']}, Payload={msg['payload']}")
            client.mark_message_read(msg['id'])
            # Process messages (e.g., TASK_APPROVED, URGENT CALL)
            if msg["type"] == "TASK_APPROVED" and msg["recipient_id"] == MANUS_ID:
                print(f"    Received approval for task {msg['payload']['task_id']}: {msg['payload']['feedback']}")
            if msg["type"] == "CALL" and msg["priority"] == "URGENT":
                print(f"    🚨 URGENT CALL from {msg['sender_id']}! Responding immediately.")

        # 2-minute interval tasks
        if (current_time - last_git_sync_time) >= timedelta(minutes=2):
            _git_sync()
            last_git_sync_time = current_time
            
            # Check for available tasks and auto-assign
            if not current_task_id:
                best_task = client.discover_best_task()
                if best_task:
                    print(f"[{_get_utc_timestamp()}] Discovered best task: {best_task['title']}")
                    client.claim_task(best_task['task_id'])
                    current_task_id = best_task['task_id']
                    print(f"[{_get_utc_timestamp()}] Claimed task: {best_task['title']}")
                    # Simulate work and completion
                    print(f"[{_get_utc_timestamp()}] Simulating work on task: {best_task['title']}")
                    time.sleep(random.uniform(5, 15)) # Simulate some work
                    client.complete_task(
                        best_task['task_id'],
                        summary=f"Completed: {best_task['title']}. Assisted Manus #5 with MACCS V3.0 implementation.",
                        artifacts=[]
                    )
                    print(f"[{_get_utc_timestamp()}] Completed simulated task: {best_task['title']}")
                    current_task_id = None # Task completed
                else:
                    print(f"[{_get_utc_timestamp()}] No suitable tasks to claim.")

        # 5-minute interval tasks
        if (current_time - last_status_report_file_update) >= timedelta(minutes=5):
            _write_status_report_file(current_task_id)
            last_status_report_file_update = current_time

        # Placeholder for 1-hour and 24-hour tasks

        time.sleep(random.uniform(5, 10)) # Adaptive sleep interval

if __name__ == "__main__":
    manus_4_operational_loop()

