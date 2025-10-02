import sys
import os
import json
from maccs.maccs_client import MACCSClientV3

if __name__ == "__main__":
    repo_path = "/home/ubuntu/Flowstate-AI"
    manus_id = "manus_7"

    client = MACCSClientV3(manus_id, repo_path)

    print(f'[{manus_id}] Checking for active tasks...')
    all_tasks = client.get_all_tasks()
    active_tasks = [task for task in all_tasks if task.get('claimed_by') == manus_id and task.get('status') in ['CLAIMED', 'IN_PROGRESS']]

    if active_tasks:
        print(f'[{manus_id}] Found {len(active_tasks)} active tasks:')
        for task in active_tasks:
            print(f'  - Task ID: {task.get("task_id")}')
            print(f'    Title: {task.get("title")}')
            print(f'    Description: {task.get("description")}')
            print(f'    Status: {task.get("status")}')
            print(f'    Claimed by: {task.get("claimed_by")}')
    else:
        print(f'[{manus_id}] No active tasks found.')

    print(f'[{manus_id}] Checking for unread messages...')
    unread_messages = client.get_unread_messages()
    if unread_messages:
        print(f'[{manus_id}] Found {len(unread_messages)} unread messages:')
        for msg in unread_messages:
            print(f'  - Message ID: {msg.get("id")}')
            print(f'    Sender: {msg.get("sender_id")}')
            print(f'    Type: {msg.get("type")}')
            print(f'    Payload: {json.loads(msg.get("payload")) }')
            client.mark_message_read(msg.get("id"))
    else:
        print(f'[{manus_id}] No unread messages found.')

    client.close()

