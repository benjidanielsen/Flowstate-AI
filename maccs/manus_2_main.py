import time
import random
import os
import sys
from datetime import datetime, timedelta, timezone
import sqlite3
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from maccs_client import MACCSClientV3
from deploy_maccs_v3 import initialize_maccs_v3, migrate_from_v0

# --- Configuration for Manus #2 (Coordinator) ---
MANUS_ID = "manus_2"
REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) # Points to Flowstate-AI root

manus_2_capabilities = {
    "skills": ["python", "ai_systems", "quality_assurance", "project_management", "system_architecture", "coordination", "delegation", "monitoring", "reporting", "rule_enforcement"],
    "specialization": "coordinator_and_ai_systems_lead",
    "max_concurrent_tasks": 3,
    "preferred_task_types": ["approval", "design", "ai_development", "monitoring", "delegation", "reporting", "rule_setting"]
}

manus_5_delegation_capabilities = {
    "skills": ["python", "system_architecture", "task_analysis", "resource_allocation", "planning", "delegation_support", "optimization", "strategic_planning"],
    "specialization": "delegation_and_planning_assistant",
    "max_concurrent_tasks": 2,
    "preferred_task_types": ["task_analysis", "planning", "delegation_support", "resource_optimization", "strategic_planning"]
}

# --- Main Loop for Manus #2 (Coordinator) ---

def manus_main_loop(client):
    current_task_id = None # Coordinator typically doesn't claim tasks in the same way
    last_git_backup_time = datetime.utcnow()
    print(f"[{client.manus_id}] Starting MACCS v3.0 Coordinator main loop...")

    def db_change_callback():
        # This callback is triggered when coordination.db changes
        # It's a signal to re-check for messages/tasks more frequently
        print(f"[{client.manus_id}] DB change detected! Re-checking for updates...")
        # For this synchronous loop, we'll just let the loop continue

    # client.start_db_watcher(db_change_callback) # Temporarily disabled due to inotify limit

    while True:
        try:
            # 1. Send adaptive heartbeat
            heartbeat_interval = 10 # Coordinator is always active
            status = "ACTIVE - COORDINATING"
            
            client.send_heartbeat(status=status, current_task=current_task_id, heartbeat_interval=heartbeat_interval)
            print(f"[{client.manus_id}] Heartbeat sent. Status: {status}, Interval: {heartbeat_interval}s")

            # 2. Process incoming messages
            unread_messages = client.get_unread_messages()
            for msg in unread_messages:
                print(f"[{client.manus_id}] Received message: {msg['type']} from {msg['sender_id']}. Payload: {msg['payload']}")
                client.mark_message_read(msg["id"])
                
                # Handle TASK_COMPLETE messages for approval and follow-up
                if msg["type"] == "TASK_COMPLETE" and msg["requires_approval"]:
                    task_id = msg["payload"]["task_id"]
                    sender_id = msg["sender_id"]
                    print(f"[{client.manus_id}] Reviewing TASK_COMPLETE from {sender_id} for task {task_id}")
                    # For now, auto-approve. In a real scenario, this would involve deeper review.
                    client.approve_task(task_id, feedback="Auto-approved by Coordinator.")
                    print(f"[{client.manus_id}] ✅ Task {task_id} auto-approved.")
                    # Post a follow-up task for the completing Manus
                    client.post_task(
                        title=f"Follow-up: Document {task_id} completion and next steps",
                        description=f"Document the completion of task {task_id} and outline any immediate next steps or potential new tasks arising from its completion. Ensure all artifacts are properly stored and referenced.",
                        required_skills=["documentation", "reporting"],
                        priority="NORMAL",
                        estimated_effort="1 hour",
                        posted_by=client.manus_id
                    )
                    print(f"[{client.manus_id}] Posted follow-up task for {sender_id} for task {task_id}.")
                # Add more message handling logic here for other message types

            # 3. Monitor Manus Status and Delegate Tasks
            all_heartbeats = client.get_all_heartbeats()
            latest_manus_status = {}
            for hb in all_heartbeats:
                manus_id = hb["manus_id"]
                if manus_id not in latest_manus_status or hb["timestamp"] > latest_manus_status[manus_id]["timestamp"]:
                    latest_manus_status[manus_id] = {"timestamp": hb["timestamp"], "status": hb["status"], "current_task": hb["current_task"], "capabilities": hb["capabilities"]}

            print(f"\n--- Coordinator Status ({datetime.now().isoformat()}) ---")
            print(f"Active Manus: {len(latest_manus_status)}")
            for manus_id, status_data in latest_manus_status.items():
                status_str = str(status_data["status"])
                task_str = str(status_data.get("current_task", "N/A"))
                timestamp_str = str(status_data["timestamp"])
                print(f"  - {manus_id}: Status={status_str}, Task={task_str}, Last Seen={timestamp_str}")

            # 4. Proactive Task Delegation (Coordinator's role)
            available_tasks = client.get_available_tasks()
            if available_tasks:
                print(f"[{client.manus_id}] Found {len(available_tasks)} available tasks. Attempting to delegate...")
                for task in available_tasks:
                    best_manus = None
                    best_score = -1

                    for manus_id, status_data in latest_manus_status.items():
                        if manus_id == client.manus_id: # Don't delegate to self
                            continue
                        
                        # Check if Manus is active and not at max capacity
                        manus_capabilities = json.loads(status_data.get("capabilities", "{}")) # Parse capabilities JSON
                        max_concurrent = manus_capabilities.get("max_concurrent_tasks", 1)
                        
                        # Count active tasks for this manus
                        active_tasks_count = client.get_active_tasks_count(manus_id)

                        if status_data["status"] == "ACTIVE" and active_tasks_count < max_concurrent:
                            # Simple skill matching
                            manus_skills = set(manus_capabilities.get("skills", []))
                            required_skills = set(json.loads(task["required_skills"])) if task["required_skills"] else set()
                            matching_skills = manus_skills.intersection(required_skills)
                            
                            score = len(matching_skills) # Basic score based on matching skills
                            if score > best_score:
                                best_score = score
                                best_manus = manus_id
                    
                    if best_manus:
                        print(f"[{client.manus_id}] Delegating task \"{task['title']}\" (ID: {task['task_id']}) to {best_manus}.")
                        client.delegate_task(task["task_id"], target_manus_id=best_manus) # Coordinator delegates the task
                        client.send_message(best_manus, "TASK_ASSIGNED", {"task_id": task["task_id"], "title": task["title"], "delegated_by": client.manus_id}, priority="HIGH")
                    else:
                        print(f"[{client.manus_id}] No suitable Manus found for task \"{task['title']}\".")
            else:
                print(f"[{client.manus_id}] No available tasks to delegate. Posting a new example task.")
                client.post_task(
                    title="Develop MACCS v3.0 Feature Y",
                    description="Implement the core logic for feature Y as per spec in MACCS v3.0.",
                    required_skills=["python", "sqlite", "system_architecture"],
                    estimated_effort="6 hours",
                    priority="NORMAL",
                    posted_by=client.manus_id
                )
                print(f"[{client.manus_id}] Posted an example task.")

            # 5. Monitor for inactive Manus instances and prompt them
            for manus_id, status_data in latest_manus_status.items():
                if manus_id == client.manus_id: # Don't monitor self for inactivity in this way
                    continue
                last_seen_str = status_data["timestamp"]
                # Ensure last_seen is timezone-aware for comparison
                last_seen = datetime.fromisoformat(last_seen_str) if isinstance(last_seen_str, str) else last_seen_str
                if last_seen.tzinfo is None: # If naive, assume UTC
                    last_seen = last_seen.replace(tzinfo=timezone.utc)
                
                # Check if last seen is older than 3x their heartbeat interval (e.g., 30 seconds for a 10s interval)
                # For now, assume a default heartbeat of 10s if not specified
                heartbeat_interval = json.loads(status_data.get("capabilities", "{}")).get("heartbeat_interval", 10)
                if (datetime.now(timezone.utc) - last_seen) > timedelta(seconds=heartbeat_interval * 3):
                    print(f"[{client.manus_id}] Detected inactive Manus: {manus_id}. Last seen: {last_seen_str}. Sending a wake-up call.")
                    client.send_message(
                        to=manus_id,
                        msg_type="WAKE_UP_CALL",
                        payload={
                            "message": "You have been detected as inactive. Please ensure your MACCS v3.0 client is running and sending heartbeats. Report your status immediately."
                        },
                        priority="URGENT"
                    )

            time.sleep(heartbeat_interval) # Adaptive sleep

        except sqlite3.OperationalError as e:
            print(f"[{client.manus_id}] Database busy error: {e}. Retrying in 1 second.")
            time.sleep(1)
        except Exception as e:
            print(f"[{client.manus_id}] An unexpected error occurred: {e}")
            time.sleep(5) # Wait before retrying


if __name__ == "__main__":
    # Initialize MACCS client for Manus #2
    client = MACCSClientV3(MANUS_ID, REPO_PATH)
    client.update_capabilities(**manus_2_capabilities)
    
    # Run the deployment script once to ensure DB is initialized and old data migrated
    initialize_maccs_v3(MANUS_ID, REPO_PATH)
    migrate_from_v0(MANUS_ID, REPO_PATH, client) # Pass the active client

    # Update Manus #5's capabilities
    client_manus5 = MACCSClientV3("manus_5", REPO_PATH)
    client_manus5.update_capabilities(**manus_5_delegation_capabilities)
    print(f"[{client.manus_id}] Updated capabilities for Manus #5 to assist with delegation and planning.")

    try:
        manus_main_loop(client)
    except KeyboardInterrupt:
        print(f"[{client.manus_id}] MACCS v3.0 main loop interrupted. Closing client.")
    finally:
        client.close()
        print(f"[{client.manus_id}] MACCS v3.0 client closed.")

