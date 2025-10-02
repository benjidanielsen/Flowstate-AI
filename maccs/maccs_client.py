
import json
import os
import time
import uuid
from datetime import datetime, timezone

class MACCSClient:
    def __init__(self, manus_id, base_path="."):
        self.manus_id = manus_id
        self.base_path = os.path.join(base_path, "maccs")
        self.messages_path = os.path.join(self.base_path, "messages", "all.jsonl")
        self.heartbeats_path = os.path.join(self.base_path, "status", "heartbeats.jsonl")
        self.available_tasks_path = os.path.join(self.base_path, "tasks", "available.jsonl")
        self.active_tasks_path = os.path.join(self.base_path, "tasks", "active.jsonl")
        self.completed_tasks_path = os.path.join(self.base_path, "tasks", "completed.jsonl")
        self.manus_capabilities_path = os.path.join(self.base_path, "status", "manus_capabilities.jsonl")

        self._ensure_maccs_dirs()
        self._ensure_maccs_files()

    def _ensure_maccs_dirs(self):
        os.makedirs(os.path.join(self.base_path, "messages"), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, "tasks"), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, "status"), exist_ok=True)

    def _ensure_maccs_files(self):
        for path in [self.messages_path, self.heartbeats_path, self.available_tasks_path, 
                     self.active_tasks_path, self.completed_tasks_path, self.manus_capabilities_path]:
            if not os.path.exists(path):
                with open(path, "w") as f:
                    pass # Just create the file

    def _write_to_jsonl(self, file_path, data):
        with open(file_path, "a") as f:
            f.write(json.dumps(data) + "\n")

    def _read_jsonl(self, file_path):
        data = []
        if not os.path.exists(file_path):
            return data
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data

    def _get_utc_timestamp(self):
        return datetime.now(timezone.utc).isoformat(timespec='seconds') + 'Z'

    def send_message(self, to_manus, msg_type, payload, priority="NORMAL", requires_approval=False, thread_id=None):
        message = {
            "id": str(uuid.uuid4()),
            "timestamp": self._get_utc_timestamp(),
            "from": self.manus_id,
            "to": to_manus,
            "type": msg_type,
            "priority": priority,
            "payload": payload,
            "requires_approval": requires_approval,
            "thread_id": thread_id if thread_id else str(uuid.uuid4())
        }
        self._write_to_jsonl(self.messages_path, message)
        return message

    def get_messages(self, filter_by_to=True, since_timestamp=None):
        all_messages = self._read_jsonl(self.messages_path)
        filtered_messages = []
        for msg in all_messages:
            if filter_by_to and msg.get("to") != self.manus_id and msg.get("to") != "broadcast":
                continue
            if since_timestamp and msg.get("timestamp") <= since_timestamp:
                continue
            filtered_messages.append(msg)
        return filtered_messages

    def send_heartbeat(self, status="ACTIVE", current_task="Monitoring", capabilities=None):
        heartbeat = {
            "manus_id": self.manus_id,
            "timestamp": self._get_utc_timestamp(),
            "status": status,
            "current_task": current_task,
            "capabilities": capabilities if capabilities else []
        }
        self._write_to_jsonl(self.heartbeats_path, heartbeat)
        return heartbeat

    def get_latest_heartbeats(self):
        all_heartbeats = self._read_jsonl(self.heartbeats_path)
        latest_heartbeats = {}
        for hb in all_heartbeats:
            manus_id = hb["manus_id"]
            if manus_id not in latest_heartbeats or hb["timestamp"] > latest_heartbeats[manus_id]["timestamp"]:
                latest_heartbeats[manus_id] = hb
        return latest_heartbeats

    def post_task(self, title, description, required_skills, estimated_effort, priority="NORMAL", deadline=None, dependencies=None, reward_credits=0):
        task = {
            "id": str(uuid.uuid4()),
            "timestamp": self._get_utc_timestamp(),
            "posted_by": self.manus_id,
            "title": title,
            "description": description,
            "required_skills": required_skills,
            "estimated_effort": estimated_effort,
            "priority": priority,
            "deadline": deadline,
            "dependencies": dependencies if dependencies else [],
            "reward_credits": reward_credits,
            "status": "AVAILABLE"
        }
        self._write_to_jsonl(self.available_tasks_path, task)
        self.send_message("broadcast", "TASK_POST", {"task_id": task["id"], "title": title, "priority": priority})
        return task

    def get_available_tasks(self):
        return self._read_jsonl(self.available_tasks_path)

    def get_active_tasks(self):
        return self._read_jsonl(self.active_tasks_path)

    def get_completed_tasks(self):
        return self._read_jsonl(self.completed_tasks_path)

    def update_capabilities(self, skills, specialization, max_concurrent_tasks=1, preferred_task_types=None):
        capabilities = {
            "manus_id": self.manus_id,
            "timestamp": self._get_utc_timestamp(),
            "skills": skills,
            "specialization": specialization,
            "max_concurrent_tasks": max_concurrent_tasks,
            "preferred_task_types": preferred_task_types if preferred_task_types else []
        }
        # Overwrite previous capabilities for this manus in manus_capabilities.jsonl
        all_caps = [c for c in self._read_jsonl(self.manus_capabilities_path) if c["manus_id"] != self.manus_id]
        all_caps.append(capabilities)
        with open(self.manus_capabilities_path, "w") as f:
            for cap in all_caps:
                f.write(json.dumps(cap) + "\n")
        self.send_message("broadcast", "CAPABILITY_UPDATE", capabilities)
        return capabilities

    def get_all_manus_capabilities(self):
        all_caps = self._read_jsonl(self.manus_capabilities_path)
        latest_caps = {}
        for cap in all_caps:
            manus_id = cap["manus_id"]
            if manus_id not in latest_caps or cap["timestamp"] > latest_caps[manus_id]["timestamp"]:
                latest_caps[manus_id] = cap
        return latest_caps

    def claim_task(self, task_id):
        available_tasks = self._read_jsonl(self.available_tasks_path)
        task_to_claim = None
        remaining_available_tasks = []

        for task in available_tasks:
            if task["id"] == task_id:
                task_to_claim = task
            else:
                remaining_available_tasks.append(task)
        
        if task_to_claim:
            task_to_claim["status"] = "ACTIVE"
            task_to_claim["claimed_by"] = self.manus_id
            task_to_claim["claimed_timestamp"] = self._get_utc_timestamp()
            self._write_to_jsonl(self.active_tasks_path, task_to_claim)
            
            # Rewrite available tasks without the claimed one
            with open(self.available_tasks_path, "w") as f:
                for task in remaining_available_tasks:
                    f.write(json.dumps(task) + "\n")
            
            self.send_message("broadcast", "TASK_CLAIM", {"task_id": task_id, "claimed_by": self.manus_id})
            return task_to_claim
        return None

    def complete_task(self, task_id, summary, artifacts=None, requires_approval=True):
        active_tasks = self._read_jsonl(self.active_tasks_path)
        task_to_complete = None
        remaining_active_tasks = []

        for task in active_tasks:
            if task["id"] == task_id:
                task_to_complete = task
            else:
                remaining_active_tasks.append(task)
        
        if task_to_complete:
            task_to_complete["status"] = "COMPLETED"
            task_to_complete["completed_by"] = self.manus_id
            task_to_complete["completed_timestamp"] = self._get_utc_timestamp()
            task_to_complete["summary"] = summary
            task_to_complete["artifacts"] = artifacts if artifacts else []
            self._write_to_jsonl(self.completed_tasks_path, task_to_complete)

            # Rewrite active tasks without the completed one
            with open(self.active_tasks_path, "w") as f:
                for task in remaining_active_tasks:
                    f.write(json.dumps(task) + "\n")

            self.send_message("manus_2", "TASK_COMPLETE", 
                              {"task_id": task_id, "summary": summary, "artifacts": artifacts}, 
                              priority="HIGH", requires_approval=requires_approval)
            return task_to_complete
        return None

    def get_my_active_tasks(self):
        return [task for task in self._read_jsonl(self.active_tasks_path) if task.get("claimed_by") == self.manus_id]

    def get_my_completed_tasks(self):
        return [task for task in self._read_jsonl(self.completed_tasks_path) if task.get("completed_by") == self.manus_id]

    def get_messages_for_manus(self, manus_id):
        return [msg for msg in self._read_jsonl(self.messages_path) if msg.get("to") == manus_id or msg.get("to") == "broadcast"]

    def get_messages_from_manus(self, manus_id):
        return [msg for msg in self._read_jsonl(self.messages_path) if msg.get("from") == manus_id]

    def get_messages_by_type(self, msg_type):
        return [msg for msg in self._read_jsonl(self.messages_path) if msg.get("type") == msg_type]

    def get_messages_by_thread(self, thread_id):
        return [msg for msg in self._read_jsonl(self.messages_path) if msg.get("thread_id") == thread_id]

    def get_messages_requiring_approval(self):
        return [msg for msg in self._read_jsonl(self.messages_path) if msg.get("requires_approval") and msg.get("to") == self.manus_id]

    def get_manus_status(self, manus_id):
        latest_heartbeats = self.get_latest_heartbeats()
        return latest_heartbeats.get(manus_id)

    def get_all_manus_status(self):
        return self.get_latest_heartbeats()

    def get_manus_capabilities(self, manus_id):
        all_caps = self.get_all_manus_capabilities()
        return all_caps.get(manus_id)

    def get_manus_score_for_task(self, manus_capabilities, task):
        score = 0
        if not manus_capabilities or not task:
            return score

        # Skill match
        for skill in task.get("required_skills", []):
            if skill in manus_capabilities.get("skills", []):
                score += 10
        
        # Specialization match
        if task.get("specialization") and task["specialization"] == manus_capabilities.get("specialization"):
            score += 20

        # Priority alignment (higher priority tasks get higher score if preferred)
        if task.get("priority") == "HIGH" and "high_priority_tasks" in manus_capabilities.get("preferred_task_types", []):
            score += 5
        
        # Workload (penalize for too many active tasks)
        active_tasks_count = len(self.get_my_active_tasks())
        if active_tasks_count >= manus_capabilities.get("max_concurrent_tasks", 1):
            score -= 50 # Heavy penalty for exceeding max tasks
        else:
            score += (manus_capabilities.get("max_concurrent_tasks", 1) - active_tasks_count) * 5

        return score

    def auto_assign_task(self):
        available_tasks = self.get_available_tasks()
        if not available_tasks:
            return None

        my_capabilities = self.get_manus_capabilities(self.manus_id)
        if not my_capabilities:
            return None # Cannot auto-assign without capabilities

        best_task = None
        best_score = -1

        for task in available_tasks:
            score = self.get_manus_score_for_task(my_capabilities, task)
            if score > best_score:
                best_score = score
                best_task = task
        
        if best_task and best_score > 0: # Only claim if a positive score
            return self.claim_task(best_task["id"])
        return None


# Example Usage (for testing/demonstration)
if __name__ == "__main__":
    # Initialize client for Manus #4
    client = MACCSClient("manus_4", base_path="../Flowstate-AI")
    print(f"MACCS Client for {client.manus_id} initialized.")

    # 1. Update capabilities
    print("\n--- Updating Capabilities ---")
    client.update_capabilities(
        skills=["python", "testing", "documentation", "quality_assurance", "system_architecture"],
        specialization="quality_assurance",
        max_concurrent_tasks=2,
        preferred_task_types=["bug_fix", "testing", "code_review", "high_priority_tasks"]
    )
    print("Capabilities updated.")

    # 2. Send a heartbeat
    print("\n--- Sending Heartbeat ---")
    client.send_heartbeat(current_task="Implementing MACCS V2 client library")
    print("Heartbeat sent.")

    # 3. Post a task (e.g., by Manus #2 or user)
    print("\n--- Posting a Task (as if by Manus #2) ---")
    # Temporarily change manus_id to simulate Manus #2 posting a task
    original_manus_id = client.manus_id
    client.manus_id = "manus_2"
    task_payload = client.post_task(
        title="Review and approve MACCS V2 implementation",
        description="Review the MACCS V2 architecture and implementation, provide feedback and approval.",
        required_skills=["system_architecture", "project_management", "quality_assurance"],
        estimated_effort="1 hour",
        priority="URGENT",
        reward_credits=100
    )
    print(f"Task posted by Manus #2: {task_payload['title']}")
    client.manus_id = original_manus_id # Revert manus_id

    # 4. Manus #4 checks for messages and tasks
    print("\n--- Checking for Messages and Tasks ---")
    my_messages = client.get_messages()
    print(f"My messages: {len(my_messages)}")
    for msg in my_messages:
        print(f"  [{msg['timestamp']}] From: {msg['from']}, Type: {msg['type']}, Payload: {msg['payload']}")

    available_tasks = client.get_available_tasks()
    print(f"Available tasks: {len(available_tasks)}")
    for task in available_tasks:
        print(f"  [{task['timestamp']}] Title: {task['title']}, Priority: {task['priority']}")

    # 5. Manus #4 auto-assigns a task
    print("\n--- Auto-Assigning Task ---")
    claimed_task = client.auto_assign_task()
    if claimed_task:
        print(f"Manus {client.manus_id} claimed task: {claimed_task['title']}")
    else:
        print(f"Manus {client.manus_id} found no suitable tasks to claim.")

    # 6. Manus #4 completes the task
    if claimed_task:
        print("\n--- Completing Task ---")
        completed_task = client.complete_task(
            claimed_task["id"],
            summary="Reviewed MACCS V2 proposal and provided assessment. Ready for implementation.",
            artifacts=["manus_4_assessment_v1_vs_v2.md"]
        )
        print(f"Manus {client.manus_id} completed task: {completed_task['title']}")

    # 7. Check final status
    print("\n--- Final Status Check ---")
    print("Latest heartbeats:", client.get_latest_heartbeats())
    print("My active tasks:", client.get_my_active_tasks())
    print("My completed tasks:", client.get_my_completed_tasks())
    print("Messages for Manus #2:", client.get_messages_for_manus("manus_2"))

    # 8. Simulate Manus #2 approving the task
    print("\n--- Simulating Manus #2 Approval ---")
    # Temporarily change manus_id to simulate Manus #2
    client.manus_id = "manus_2"
    approval_message = client.send_message(
        "manus_4", "TASK_APPROVED", 
        {"task_id": completed_task["id"], "feedback": "Excellent work, proceed with implementation!"},
        priority="URGENT"
    )
    print(f"Manus #2 sent approval: {approval_message['payload']}")
    client.manus_id = original_manus_id # Revert manus_id

    print("\n--- Manus #4 checking for approval ---")
    my_approvals = client.get_messages_for_manus("manus_4")
    for msg in my_approvals:
        if msg.get("type") == "TASK_APPROVED" and msg.get("payload", {}).get("task_id") == completed_task["id"]:
            print(f"Received approval for task {completed_task['title']}: {msg['payload']['feedback']}")



