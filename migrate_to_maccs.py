import json
import os
import uuid
from datetime import datetime, timezone
from maccs.maccs_client import MACCSClient

def _get_utc_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"

def migrate_coordination_status(old_status_path, maccs_base_path, current_manus_id):
    with open(old_status_path, 'r') as f:
        old_status = json.load(f)

    manus_instances = old_status.get('manus_instances', {})

    # Initialize a temporary client for each manus to post their data
    # This is a bit of a hack to use the client's write methods
    # In a real scenario, each manus would post its own data.
    temp_clients = {mid: MACCSClient(mid, base_path=maccs_base_path) for mid in manus_instances.keys()}

    for manus_id, data in manus_instances.items():
        client = temp_clients[manus_id]

        # 1. Post Heartbeat
        hb_timestamp = data.get('last_heartbeat') or data.get('last_update') or _get_utc_timestamp()
        client.send_heartbeat(
            status=data.get('status', 'UNKNOWN'),
            current_task=data.get('current_task', 'No task specified'),
            capabilities=data.get('capabilities', [])
        )

        # 2. Post Capabilities
        if data.get('capabilities'):
            client.update_capabilities(
                skills=data.get('capabilities', []),
                specialization=data.get('role', 'general').replace('_developer', '').replace('_enhancer', '').replace('_perfectionist', '').replace('_coordinator', '').replace('_specialist', ''),
                max_concurrent_tasks=2, # Default, can be refined
                preferred_task_types=[] # Default, can be refined
            )

        # 3. Post Completed Work as Completed Tasks
        for work_item in data.get('completed_work', []):
            # Simulate task posting and completion
            # This is a simplification; ideally, tasks would have been posted first
            task_id = str(uuid.uuid4())
            # Post as if by Manus #2 for consistency, or by self if no clear owner
            poster_id = 'manus_2' if manus_id != 'manus_2' else manus_id
            
            # Temporarily change client's manus_id to simulate task posting by another manus
            original_client_manus_id = client.manus_id
            client.manus_id = poster_id
            
            # Post the task as available first
            posted_task = client.post_task(
                title=f"Completed work: {work_item[:50]}...",
                description=work_item,
                required_skills=[], # Cannot infer from old format
                estimated_effort='unknown',
                priority='LOW'
            )
            
            # Revert client's manus_id
            client.manus_id = original_client_manus_id

            # Now claim and complete it by the actual manus
            # Direct write to completed for migration simplicity
            completed_task_data = {
                "id": posted_task["id"],
                "timestamp": posted_task["timestamp"],
                "posted_by": posted_task["posted_by"],
                "title": posted_task["title"],
                "description": posted_task["description"],
                "required_skills": posted_task["required_skills"],
                "estimated_effort": posted_task["estimated_effort"],
                "priority": posted_task["priority"],
                "deadline": posted_task["deadline"],
                "dependencies": posted_task["dependencies"],
                "reward_credits": posted_task["reward_credits"],
                "status": "COMPLETED",
                "claimed_by": manus_id,
                "claimed_timestamp": hb_timestamp,
                "completed_by": manus_id,
                "completed_timestamp": hb_timestamp,
                "summary": work_item,
                "artifacts": []
            }
            client._write_to_jsonl(client.completed_tasks_path, completed_task_data)
            client.send_message("manus_2", "TASK_COMPLETE", {"task_id": posted_task["id"], "summary": work_item}, priority="LOW", requires_approval=False)

        # 4. Post Messages
        for key, value in data.items():
            if key.startswith('message_to_') and value:
                to_manus = key.replace('message_to_', '')
                if to_manus == 'all': to_manus = 'broadcast'
                client.send_message(to_manus, 'OLD_COORDINATION_MESSAGE', value, priority='NORMAL', requires_approval=False)
            elif key.startswith('message_from_') and value:
                from_manus = key.replace('message_from_', '')
                # This is tricky as we can't send a message *from* another manus easily
                # For now, we'll just log it as a message to self from that manus
                client.send_message(manus_id, 'OLD_COORDINATION_MESSAGE_FROM_OTHER', value, priority='NORMAL', requires_approval=False, thread_id=f"old_msg_from_{from_manus}")

    print("Migration complete. Data written to MACCS .jsonl files.")

migrate_coordination_status(
    old_status_path='/home/ubuntu/Flowstate-AI/.manus-coordination/coordination-status.json',
    maccs_base_path='/home/ubuntu/Flowstate-AI',
    current_manus_id='manus_4'
)

