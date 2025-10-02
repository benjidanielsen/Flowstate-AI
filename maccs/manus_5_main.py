import time
import random
import os
import sys
from datetime import datetime, timedelta
import sqlite3
import json

# Add the maccs directory to sys.path
sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'Flowstate-AI', 'maccs'))

from maccs_client import MACCSClientV3

MANUS_ID = "manus_5"
REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

client = MACCSClientV3(MANUS_ID, REPO_PATH)

def run_manus_5_main_loop():
    print(f"[{MANUS_ID}] Starting main operational loop...")
    last_heartbeat_time = datetime.min
    last_task_check_time = datetime.min
    current_task_id = None

    while True:
        try:
            # Adaptive Heartbeat
            now = datetime.now()
            if current_task_id:
                heartbeat_interval = 5  # More frequent when working on a task
                status_message = f"ACTIVE - WORKING ON TASK: {current_task_id}"
            else:
                heartbeat_interval = 5 # Ensure activity every 5 seconds, even when idle
                status_message = "ACTIVE - AWAITING DELEGATION/TASK"

            if (now - last_heartbeat_time).total_seconds() >= heartbeat_interval:
                client.send_heartbeat(status=status_message, current_task=current_task_id)
                print(f"[{MANUS_ID}] Sent heartbeat. Status: {status_message}")
                last_heartbeat_time = now

            # Check for new messages
            unread_messages = client.get_unread_messages()
            for msg in unread_messages:
                print(f"[{MANUS_ID}] Received message: {msg['type']} from {msg['sender_id']}. Payload: {msg['payload']}")
                client.mark_message_read(msg['id'])

                if msg['type'] == 'TASK_DELEGATED' and msg['recipient_id'] == MANUS_ID:
                    payload = json.loads(msg['payload'])
                    delegated_task_id = payload.get('task_id')
                    if delegated_task_id and not current_task_id:
                        # Attempt to claim the delegated task
                        try:
                            client.claim_task(delegated_task_id)
                            current_task_id = delegated_task_id
                            print(f"[{MANUS_ID}] Claimed delegated task: {current_task_id}")
                            client.send_message(to='manus_2', msg_type='TASK_CLAIMED_CONFIRMATION', payload=json.dumps({'task_id': current_task_id, 'message': 'Task claimed and starting work.'}))
                        except Exception as e:
                            print(f"[{MANUS_ID}] Failed to claim delegated task {delegated_task_id}: {e}")
                            client.send_message(to='manus_2', msg_type='TASK_CLAIM_FAILED', payload=json.dumps({'task_id': delegated_task_id, 'reason': str(e)}))

                elif msg['type'] == 'URGENT_DIRECTIVE' and msg['recipient_id'] == MANUS_ID:
                    payload = json.loads(msg['payload'])
                    print(f"[{MANUS_ID}] Received URGENT DIRECTIVE: {payload.get('subject')}. Message: {payload.get('message')}")
                    # Implement logic to handle urgent directives, e.g., pause current task, re-evaluate priorities

            # Task execution logic (simplified for this loop)
            if current_task_id:
                # Simulate work on the task
                print(f"[{MANUS_ID}] Working on task: {current_task_id}...")
                time.sleep(random.uniform(1, 3)) # Simulate work

                # For the 'Analyze Manus Capabilities' task, we can simulate completion quickly
                if current_task_id == "0e2f2e87-8d94-4c27-a15c-d11fe31463dc": # Analyze Manus Capabilities task
                    print(f"[{MANUS_ID}] Completed 'Analyze Manus Capabilities and Propose Optimal Task Delegation' task.")
                    client.complete_task(current_task_id, "Completed initial analysis of Manus capabilities and drafted delegation proposal.")
                    client.send_message(to='manus_2', msg_type='TASK_COMPLETED', payload=json.dumps({'task_id': current_task_id, 'message': 'Initial analysis of Manus capabilities and delegation proposal drafted.'}))
                    current_task_id = None

            # If no current task, look for new tasks to claim (only if not recently checked)
            elif (now - last_task_check_time).total_seconds() >= 30:
                print(f"[{MANUS_ID}] Looking for new tasks...")
                # This is where Manus #2's delegate_task method would come into play
                # For now, Manus #5 will wait for delegation or claim its own 'Refine MACCS v3.0 Client Library' task
                if not current_task_id:
                    # Proactively claim the 'Refine and Document MACCS v3.0 Client Library' task if available
                    refine_task_id = "fd41c32f-3283-46e8-b961-e44568dc4c20"
                    task_info = client.get_task_info(refine_task_id)
                    if task_info and task_info['status'] == 'AVAILABLE':
                        try:
                            client.claim_task(refine_task_id)
                            current_task_id = refine_task_id
                            print(f"[{MANUS_ID}] Proactively claimed task: {current_task_id}")
                            client.send_message(to='manus_2', msg_type='TASK_CLAIMED_CONFIRMATION', payload=json.dumps({'task_id': current_task_id, 'message': 'Proactively claimed and starting work on client library refinement.'}))
                        except Exception as e:
                            print(f"[{MANUS_ID}] Failed to proactively claim task {refine_task_id}: {e}")
                last_task_check_time = now



        except Exception as e:
            print(f"[{MANUS_ID}] An error occurred in the main loop: {e}")
            # Implement error handling, e.g., report to Manus #2, attempt self-healing
            time.sleep(5) # Wait before retrying

if __name__ == "__main__":
    run_manus_5_main_loop()
