_#_PY_SNIPPET_#_import time
import random
import os
import sys
from datetime import datetime, timedelta
import sqlite3
import json

# Add the maccs directory to sys.path
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "Flowstate-AI", "maccs"))

from maccs_client import MACCSClientV3

MANUS_ID = "manus_5"
REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

client = MACCSClientV3(MANUS_ID, REPO_PATH)

def run_manus_5_main_loop():
    print(f"[{MANUS_ID}] Starting main operational loop...")
    last_heartbeat_time = datetime.min
    last_task_check_time = datetime.min
    current_task_id = None

    # Register Manus #5's capabilities
    manus_5_capabilities = {
        "skills": ["python", "testing", "documentation", "bug_fixing", "system_architecture", "coordination"],
        "specialization": "quality_assurance",
        "max_concurrent_tasks": 2,
        "preferred_task_types": ["bug_fix", "testing", "code_review", "design", "architecture", "coordination"]
    }
    client.update_capabilities(**manus_5_capabilities)
    print(f"[{MANUS_ID}] Capabilities updated: {manus_5_capabilities}")

    while True:
        try:
            # Adaptive Heartbeat
            now = datetime.now()
            heartbeat_interval = 5 # Ensure activity every 5 seconds, even when idle

            if current_task_id:
                status_message = f"ACTIVE - WORKING ON TASK: {current_task_id}"
            else:
                status_message = "ACTIVE - AWAITING DELEGATION/TASK"

            if (now - last_heartbeat_time).total_seconds() >= heartbeat_interval:
                client.send_heartbeat(status=status_message, current_task=current_task_id, heartbeat_interval=heartbeat_interval)
                print(f"[{MANUS_ID}] Sent heartbeat. Status: {status_message}")
                last_heartbeat_time = now

            # Check for new messages
            unread_messages = client.get_unread_messages()
            for msg in unread_messages:
                print(f"[{MANUS_ID}] Received message: {msg['type']} from {msg['sender_id']}. Payload: {msg['payload']}")
                client.mark_message_read(msg["id"])

                if msg["type"] == "TASK_DELEGATED" and msg["recipient_id"] == MANUS_ID:
                    payload = json.loads(msg["payload"])
                    delegated_task_id = payload.get("task_id")
                    if delegated_task_id and not current_task_id:
                        # Attempt to claim the delegated task
                        try:
                            client.claim_task(delegated_task_id)
                            current_task_id = delegated_task_id
                            print(f"[{MANUS_ID}] Claimed delegated task: {current_task_id}")
                            client.send_message(to="manus_2", msg_type="TASK_CLAIMED_CONFIRMATION", payload=json.dumps({"task_id": current_task_id, "message": "Task claimed and starting work."}))
                        except Exception as e:
                            print(f"[{MANUS_ID}] Failed to claim delegated task {delegated_task_id}: {e}")
                            client.send_message(to="manus_2", msg_type="TASK_CLAIM_FAILED", payload=json.dumps({"task_id": delegated_task_id, "reason": str(e)}))

                elif msg["type"] == "URGENT_DIRECTIVE" and msg["recipient_id"] == MANUS_ID:
                    payload = json.loads(msg["payload"])
                    print(f"[{MANUS_ID}] Received URGENT DIRECTIVE: {payload.get('subject')}. Message: {payload.get('message')}")

                elif msg["type"] == "TASK_APPROVED" and msg["recipient_id"] == MANUS_ID:
                    payload = json.loads(msg["payload"])
                    approved_task_id = payload.get("task_id")
                    print(f"[{MANUS_ID}] Task {approved_task_id} approved by Manus #2.")

                elif msg["type"] == "TASK_REJECTED" and msg["recipient_id"] == MANUS_ID:
                    payload = json.loads(msg["payload"])
                    rejected_task_id = payload.get("task_id")
                    feedback = payload.get("feedback")
                    print(f"[{MANUS_ID}] Task {rejected_task_id} rejected by Manus #2. Feedback: {feedback}")

            # Task execution logic
            if current_task_id:
                print(f"[{MANUS_ID}] Working on task: {current_task_id}...")
                time.sleep(random.uniform(1, 3))

            # If no current task, look for new tasks to claim
            elif (now - last_task_check_time).total_seconds() >= 5:
                print(f"[{MANUS_ID}] Looking for new tasks...")
                best_task = client.discover_best_task()
                if best_task:
                    try:
                        client.claim_task(best_task["task_id"])
                        current_task_id = best_task["task_id"]
                        print(f"[{MANUS_ID}] Claimed task: {best_task['title']} (ID: {current_task_id})")
                        client.send_message(to="manus_2", msg_type="TASK_CLAIMED_CONFIRMATION", payload=json.dumps({"task_id": current_task_id, "message": f"Claimed task: {best_task['title']}"}))
                    except Exception as e:
                        print(f"[{MANUS_ID}] Failed to claim task {best_task['task_id']}: {e}")
                last_task_check_time = now

            time.sleep(1)

        except Exception as e:
            print(f"[{MANUS_ID}] An error occurred in the main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_manus_5_main_loop()

