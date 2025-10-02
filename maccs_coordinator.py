import json
import uuid
from datetime import datetime, timedelta
import subprocess
import time
import random
from pathlib import Path

class MACCSCoordinator:
    def __init__(self, manus_id="manus_2", repo_path="/home/ubuntu/Flowstate-AI"):
        self.manus_id = manus_id
        self.repo_path = Path(repo_path)
        self.maccs_path = self.repo_path / "maccs"
        self.maccs_path.mkdir(parents=True, exist_ok=True)
        (self.maccs_path / "messages").mkdir(exist_ok=True)
        (self.maccs_path / "tasks").mkdir(exist_ok=True)
        (self.maccs_path / "status").mkdir(exist_ok=True)

    def _git_pull_rebase(self):
        """Perform git pull --rebase origin main"""
        try:
            subprocess.run(["git", "pull", "--rebase", "origin", "main"],
                             cwd=self.repo_path, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            # print(f"❌ Git pull --rebase failed: {e.stderr}")
            return False

    def _git_commit_and_push(self, message):
        """Commit changes and push to origin main"""
        try:
            subprocess.run(["git", "add", str(self.maccs_path)], cwd=self.repo_path, check=True)
            subprocess.run(["git", "commit", "-m", message],
                             cwd=self.repo_path, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=self.repo_path, check=True)
            return True
        except subprocess.CalledProcessError as e:
            # print(f"❌ Git commit/push failed: {e.stderr}")
            return False

    def _append_to_jsonl(self, filename, data):
        """Safely append to a .jsonl file with Git-native conflict resolution"""
        filepath = self.maccs_path / filename
        
        for attempt in range(5):
            if not self._git_pull_rebase():
                time.sleep(random.uniform(1, 3))
                continue

            with open(filepath, "a") as f:
                f.write(json.dumps(data) + "\n")
            
                commit_message = f"MACCS: {data.get('type', 'message')} from {self.manus_id}"
                return True
            else:
                time.sleep(random.uniform(1, 3))  # Random backoff on push failure
        
        print(f"❌ Failed to append to {filename} after multiple retries.")
        return False
    
    def _read_jsonl(self, filename):
        """Read all entries from a .jsonl file"""
        filepath = self.maccs_path / filename
        messages = []
        
        try:
            with open(filepath, "r") as f:
                for line in f:
                    if line.strip():
                        messages.append(json.loads(line))
        except FileNotFoundError:
            pass # File might not exist yet, return empty list
        
        return messages

    def _write_jsonl(self, filename, data_list):
        """Overwrite a .jsonl file with new data"""
        filepath = self.maccs_path / filename
        
        for attempt in range(5):
            if not self._git_pull_rebase():
                time.sleep(random.uniform(1, 3))
                continue

            with open(filepath, "w") as f:
                for item in data_list:
                    f.write(json.dumps(item) + "\n")
            
            if self._git_commit_and_push(f"MACCS: Overwrite {filename} from {self.manus_id}"):
                return True
            else:
                time.sleep(random.uniform(1, 3))  # Random backoff on push failure
        
        print(f"❌ Failed to overwrite {filename} after multiple retries.")
        return False

    def send_message(self, to, msg_type, payload, priority="NORMAL", requires_approval=False, thread_id=None):
        """Send a message to another Manus or broadcast"""
        message = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "from": self.manus_id,
            "to": to,
            "type": msg_type,
            "priority": priority,
            "payload": payload,
            "requires_approval": requires_approval,
            "thread_id": thread_id or str(uuid.uuid4())
        }
        
        return self._append_to_jsonl("messages/all.jsonl", message)

    def post_task(self, title, description, required_skills, estimated_effort, priority="NORMAL", deadline=None, dependencies=None, reward_credits=0):
        """Post a new task to the marketplace"""
        task = {
            "task_id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "required_skills": required_skills,
            "estimated_effort": estimated_effort,
            "priority": priority,
            "deadline": deadline,
            "dependencies": dependencies or [],
            "reward_credits": reward_credits,
            "posted_by": self.manus_id,
            "posted_at": datetime.utcnow().isoformat() + "Z"
        }
        
        return self._append_to_jsonl("tasks/available.jsonl", task)

    def get_all_manus_status(self):
        """Get the latest heartbeat status for all Manus instances"""
        heartbeats = self._read_jsonl("status/heartbeats.jsonl")
        latest_heartbeats = {}
        for hb in heartbeats:
            manus_id = hb["manus_id"]
            if manus_id not in latest_heartbeats or hb["timestamp"] > latest_heartbeats[manus_id]["timestamp"]:
                latest_heartbeats[manus_id] = {"timestamp": hb["timestamp"], "status": hb["status"], "current_task": hb["current_task"], "capabilities": hb["capabilities"]}
        return latest_heartbeats
    def get_tasks_for_approval(self):
        """Get completed tasks awaiting Manus #2's approval"""
        messages = self._read_jsonl("messages/all.jsonl")
        approval_queue = [
            m for m in messages 
            if m["to"] == self.manus_id and 
               m["type"] == "TASK_COMPLETE" and 
               m["requires_approval"]
        ]
        # Filter out messages that have already been approved/rejected
        approved_rejected_ids = set([
            m["payload"]["task_id"] for m in messages 
            if m["to"] == "broadcast" and m["type"] in ["TASK_APPROVED", "TASK_REJECTED"]
        ])
        approval_queue = [m for m in approval_queue if m["payload"]["task_id"] not in approved_rejected_ids]
        
        # Sort by priority: URGENT > HIGH > NORMAL > LOW
        priority_map = {"URGENT": 4, "HIGH": 3, "NORMAL": 2, "LOW": 1}
        approval_queue.sort(key=lambda m: priority_map.get(m["priority"], 0), reverse=True)
        return approval_queue

    def approve_task(self, task_id, feedback="Approved."):
        """Approve a completed task"""
        return self.send_message("broadcast", "TASK_APPROVED", {"task_id": task_id, "feedback": feedback}, priority="HIGH")

    def reject_task(self, task_id, feedback="Rejected. Please review and resubmit."):
        """Reject a completed task"""
        return self.send_message("broadcast", "TASK_REJECTED", {"task_id": task_id, "feedback": feedback}, priority="HIGH")

    def main_loop(self, check_interval=10):
        """Main loop for the Coordinator to monitor and delegate"""
        print(f"🔄 {self.manus_id}: Starting MACCS Coordinator loop.")
        
        while True:
            try:
                self._git_pull_rebase()

                # 1. Monitor Manus Status
                all_manus_status = self.get_all_manus_status()
                print(f"\n--- Coordinator Status ({datetime.now().isoformat()}) ---")
                print(f"Active Manus: {len(all_manus_status)}")
                for manus_id, status_data in all_manus_status.items():
                    print(f"  - {manus_id}: Status={status_data['status']}, Task={status_data.get('current_task', 'N/A')}, Last Seen={status_data['timestamp']}")

                # 2. Process Tasks for Approval
                approval_queue = self.get_tasks_for_approval()
                if approval_queue:
                    print(f"Found {len(approval_queue)} tasks awaiting approval.")
                    for task_msg in approval_queue:
                        task_id = task_msg["payload"]["task_id"]
                        print(f"  - Reviewing TASK_COMPLETE from {task_msg['from']} for task {task_id}")
                        # For now, auto-approve. In a real scenario, this would involve deeper review.
                        self.approve_task(task_id, feedback="Auto-approved by Coordinator.")
                        print(f"    ✅ Task {task_id} auto-approved.")
                else:
                    print("No tasks awaiting approval.")

                # 3. Check for idle Manus and delegate new tasks (example)
                # This part would be more sophisticated, potentially reading from a master task list
                # For now, let's just ensure there are some tasks available.
                available_tasks = self._read_jsonl("tasks/available.jsonl")
                if not available_tasks:
                    print("No available tasks. Posting a new example task.")
                    self.post_task(
                        title="Develop new feature X",
                        description="Implement the core logic for feature X as per spec.",
                        required_skills=["python", "backend", "api"],
                        estimated_effort="8 hours",
                        priority="HIGH"
                    )
                    print("Posted an example task.")

            except Exception as e:
                print(f"❌ Coordinator error: {e}")
            
            time.sleep(check_interval)

if __name__ == "__main__":
    coordinator = MACCSCoordinator()
    coordinator.main_loop()

