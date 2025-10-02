import time
import random
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from maccs_client import MACCSClientV3

# --- Configuration for Manus #5 ---
MANUS_ID = "manus_5"
REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) # Points to Flowstate-AI root

manus_5_capabilities = {
    "skills": ["python", "testing", "documentation", "bug_fixing", "system_architecture", "database_design", "git_workflow"],
    "specialization": "quality_assurance_and_system_architecture",
    "max_concurrent_tasks": 2,
    "preferred_task_types": ["bug_fix", "testing", "code_review", "design", "system_implementation"]
}

# --- Main Loop for Manus #5 ---

def manus_main_loop(client):
    current_task_id = None
    last_git_backup_time = datetime.utcnow()
    print(f"[{client.manus_id}] Starting MACCS v3.0 main loop...")

    def db_change_callback():
        # This callback is triggered when coordination.db changes
        # It's a signal to re-check for messages/tasks more frequently
        print(f"[{client.manus_id}] DB change detected! Re-checking for updates...")
        # In a real async system, this would trigger a non-blocking re-evaluation
        # For this synchronous loop, we'll just let the loop continue

    client.start_db_watcher(db_change_callback)

    while True:
        try:
            # 1. Send adaptive heartbeat
            # Determine heartbeat interval based on activity
            if current_task_id:
                heartbeat_interval = 5 # Active: 5 seconds
                status = "ACTIVE - WORKING ON TASK"
            else:
                # Check for unread messages or available tasks to determine responsiveness
                unread_messages = client.get_unread_messages()
                best_task = client.discover_best_task()
                if unread_messages or best_task:
                    heartbeat_interval = 15 # Responsive: 15 seconds
                    status = "ACTIVE - RESPONSIVE"
                else:
                    heartbeat_interval = 30 # Monitoring: 30 seconds
                    status = "ACTIVE - MONITORING"
            
            client.send_heartbeat(status=status, current_task=current_task_id, heartbeat_interval=heartbeat_interval)
            print(f"[{client.manus_id}] Heartbeat sent. Status: {status}, Interval: {heartbeat_interval}s")

            # 2. Process incoming messages
            unread_messages = client.get_unread_messages()
            for msg in unread_messages:
                print(f"[{client.manus_id}] Received message: {msg["type"]} from {msg["sender_id"]}. Payload: {msg["payload"]}")
                client.mark_message_read(msg["id"])
                
                # Example: Handle TASK_APPROVED message from Manus #2
                if msg["type"] == "TASK_APPROVED" and msg["recipient_id"] == MANUS_ID:
                    print(f"[{client.manus_id}] Task {msg["payload"]["task_id"]} approved by {msg["sender_id"]}")
                    # Further actions for approved task
                # Add more message handling logic here

            # 3. Discover and claim new task if idle
            if not current_task_id:
                best_task = client.discover_best_task()
                if best_task:
                    client.claim_task(best_task["task_id"])
                    current_task_id = best_task["task_id"]
                    print(f"[{client.manus_id}] Claimed task: {best_task["title"]}")
                    # In a real scenario, you'd start working on this task here
                    # For now, we'll just simulate completion after a delay
                    time.sleep(random.uniform(30, 120)) # Simulate work
                    client.complete_task(current_task_id, f"Simulated completion of {best_task["title"]}")
                    print(f"[{client.manus_id}] Completed task: {best_task["title"]}")
                    current_task_id = None # Ready for next task

            # 4. Periodic Git backup (every 5 minutes)
            if (datetime.utcnow() - last_git_backup_time) > timedelta(minutes=5):
                print(f"[{client.manus_id}] Performing periodic Git backup...")
                if client.git_sync_and_backup():
                    last_git_backup_time = datetime.utcnow()
                    print(f"[{client.manus_id}] Git backup successful.")
                else:
                    print(f"[{client.manus_id}] Git backup failed. Will retry.")

            time.sleep(heartbeat_interval) # Adaptive sleep

        except sqlite3.OperationalError as e:
            print(f"[{client.manus_id}] Database busy error: {e}. Retrying in 1 second.")
            time.sleep(1)
        except Exception as e:
            print(f"[{client.manus_id}] An unexpected error occurred: {e}")
            time.sleep(5) # Wait before retrying


if __name__ == "__main__":
    # Initialize MACCS client for Manus #5
    client = MACCSClientV3(MANUS_ID, REPO_PATH)
    client.update_capabilities(**manus_5_capabilities)
    
    # Run the deployment script once to ensure DB is initialized and old data migrated
    # This should ideally be run as a separate step or only once per Manus setup
    # For demonstration, we'll run it here, but it's idempotent.
    from deploy_maccs_v3 import initialize_maccs_v3, migrate_from_v0
    initialize_maccs_v3(MANUS_ID, REPO_PATH)
    migrate_from_v0(MANUS_ID, REPO_PATH, client) # Pass the active client

    try:
        manus_main_loop(client)
    except KeyboardInterrupt:
        print(f"[{client.manus_id}] MACCS v3.0 main loop interrupted. Closing client.")
    finally:
        client.close()
        print(f"[{client.manus_id}] MACCS v3.0 client closed.")

