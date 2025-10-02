import json
import uuid
from datetime import datetime
import subprocess
import time
import random
from pathlib import Path

class MACCSClient:
    def __init__(self, manus_id, capabilities, repo_path="/home/ubuntu/Flowstate-AI"):
        self.manus_id = manus_id
        self.capabilities = capabilities
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
            print(f"❌ Git pull --rebase failed: {e.stderr}")
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
            print(f"❌ Git commit/push failed: {e.stderr}")
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
            
            if self._git_commit_and_push(f"MACCS: {data.get('type', 'message')} from {self.manus_id}"):
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
    
    def get_my_messages(self, unread_only=True):
        """Get messages addressed to this Manus"""
        messages = self._read_jsonl("messages/all.jsonl")
        my_messages = [m for m in messages if m["to"] == self.manus_id or m["to"] == "broadcast"]
        
        # Placeholder for unread_only logic - would need a persistent way to track read messages
        # For now, we'll return all messages for this Manus
        return my_messages
    
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
    
    def discover_and_claim_task(self):
        """Find and claim the best matching task"""
        available_tasks = self._read_jsonl("tasks/available.jsonl")
        
        if not available_tasks:
            return None
        
        # Filter out tasks already claimed by this manus (if any state is kept)
        # This client is stateless, so it relies on the central log for claims

        # Calculate match scores
        scored_tasks = []
        for task in available_tasks:
            score = self._calculate_task_score(task)
            scored_tasks.append((score, task))
        
        # Get highest scoring task
        scored_tasks.sort(reverse=True, key=lambda x: x[0])
        
        if scored_tasks:
            best_task = scored_tasks[0][1]
            # Check if the task is still available (not claimed by another Manus in the meantime)
            # This requires another pull and check before claiming
            current_available_tasks = self._read_jsonl("tasks/available.jsonl")
            if any(t['task_id'] == best_task['task_id'] for t in current_available_tasks):
                if self.claim_task(best_task["task_id"]):
                    return best_task
        return None
    
    def claim_task(self, task_id):
        """Claim a specific task"""
        # First, remove from available.jsonl
        available_tasks = self._read_jsonl("tasks/available.jsonl")
        task_to_claim = next((t for t in available_tasks if t["task_id"] == task_id), None)
        
        if not task_to_claim:
            print(f"❌ Task {task_id} not found or already claimed.")
            return False

        remaining_available_tasks = [t for t in available_tasks if t["task_id"] != task_id]
        if not self._write_jsonl("tasks/available.jsonl", remaining_available_tasks):
            return False # Failed to update available tasks

        # Then, add to active.jsonl
        task_to_claim["claimed_by"] = self.manus_id
        task_to_claim["claimed_at"] = datetime.utcnow().isoformat() + "Z"
        if not self._append_to_jsonl("tasks/active.jsonl", task_to_claim):
            return False # Failed to add to active tasks

        # Send a message to broadcast the claim
        return self.send_message("broadcast", "TASK_CLAIM", {
            "task_id": task_id,
            "claimed_by": self.manus_id,
            "claimed_at": datetime.utcnow().isoformat() + "Z"
        })
    
    def complete_task(self, task_id, summary, artifacts=None):
        """Mark task as complete and submit for approval"""
        artifacts = artifacts or []
        # Remove from active.jsonl
        active_tasks = self._read_jsonl("tasks/active.jsonl")
        task_to_complete = next((t for t in active_tasks if t["task_id"] == task_id and t["claimed_by"] == self.manus_id), None)

        if not task_to_complete:
            print(f"❌ Task {task_id} not found or not claimed by {self.manus_id}.")
            return False

        remaining_active_tasks = [t for t in active_tasks if t["task_id"] != task_id]
        if not self._write_jsonl("tasks/active.jsonl", remaining_active_tasks):
            return False

        # Add to completed.jsonl
        task_to_complete["status"] = "completed"
        task_to_complete["completed_by"] = self.manus_id
        task_to_complete["completed_at"] = datetime.utcnow().isoformat() + "Z"
        task_to_complete["summary"] = summary
        task_to_complete["artifacts"] = artifacts
        if not self._append_to_jsonl("tasks/completed.jsonl", task_to_complete):
            return False

        # Send message to Manus #2 for approval
        return self.send_message("manus_2", "TASK_COMPLETE", {
            "task_id": task_id,
            "summary": summary,
            "artifacts": artifacts,
            "completed_by": self.manus_id,
            "completed_at": datetime.utcnow().isoformat() + "Z"
        }, priority="HIGH", requires_approval=True)
    
    def send_heartbeat(self, status="ACTIVE", current_task=None):
        """Send heartbeat to announce presence"""
        heartbeat = {
            "manus_id": self.manus_id,
            "status": status,
            "current_task": current_task,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "capabilities": self.capabilities # Include capabilities in heartbeat
        }
        return self._append_to_jsonl("status/heartbeats.jsonl", heartbeat)
    
    def _calculate_task_score(self, task):
        """Calculate how well this task matches our capabilities"""
        score = 0
        
        # Skill matching
        my_skills = set(self.capabilities.get("skills", []))
        required_skills = set(task.get("required_skills", []))
        matching_skills = my_skills.intersection(required_skills)
        score += len(matching_skills) * 10
        
        # Priority bonus
        if task.get("priority") == "HIGH":
            score += 5
        elif task.get("priority") == "URGENT":
            score += 10
        
        # Workload penalty (assuming we can get active tasks for this manus)
        active_tasks = self._read_jsonl("tasks/active.jsonl")
        my_active_tasks = [t for t in active_tasks if t.get("claimed_by") == self.manus_id]
        score -= len(my_active_tasks) * 5
        
        return score

    def get_active_tasks(self):
        """Get tasks currently claimed by this Manus"""
        active_tasks = self._read_jsonl("tasks/active.jsonl")
        return [t for t in active_tasks if t.get("claimed_by") == self.manus_id]

    def get_all_manus_status(self):
        """Get the latest heartbeat status for all Manus instances"""
        heartbeats = self._read_jsonl("status/heartbeats.jsonl")
        latest_heartbeats = {}
        for hb in heartbeats:
            manus_id = hb['manus_id']
            if manus_id not in latest_heartbeats or hb['timestamp'] > latest_heartbeats[manus_id]['timestamp']:
                latest_heartbeats[manus_id] = hb
        return latest_heartbeats

    def main_loop(self, work_function, idle_function=None, heartbeat_interval=15):
        """Main loop for continuous operation"""
        print(f"🔄 {self.manus_id}: Starting continuous work cycle (MACCS v2.0)")
        
        current_heartbeat_interval = heartbeat_interval # Start in RESPONSIVE mode
        last_git_sync = time.time()

        while True:
            try:
                # 1. SYNC: Pull latest from GitHub periodically
                if time.time() - last_git_sync > 30: # Sync every 30 seconds
                    self._git_pull_rebase()
                    last_git_sync = time.time()

                # 2. PROCESS: Handle incoming messages (simple read for now)
                # In a real implementation, this would involve parsing all.jsonl
                # and acting on messages addressed to this manus.
                # For this simulation, we'll just acknowledge new messages.
                new_messages = self.get_my_messages(unread_only=True)
                if new_messages:
                    print(f"💬 {self.manus_id}: Received {len(new_messages)} new messages.")
                    # In a full implementation, process these messages and update last_read_timestamp

                # 3. EXECUTE: Work on current task
                active_tasks = self.get_active_tasks()
                if active_tasks:
                    current_task = active_tasks[0] # Assume one task at a time for simplicity
                    print(f"🔨 {self.manus_id}: Working on task: {current_task['title']}")
                    work_function(current_task) # Call the provided work function
                    # The work_function should call complete_task when done
                else:
                    # 4. DISCOVER: Find new work if idle
                    print(f"💤 {self.manus_id}: Idle. Discovering tasks...")
                    claimed_task = self.discover_and_claim_task()
                    if claimed_task:
                        print(f"✅ {self.manus_id}: Claimed task: {claimed_task['title']}")
                        current_heartbeat_interval = 5 # Switch to ACTIVE mode
                    elif idle_function:
                        idle_function() # Call the provided idle function

                # 5. HEARTBEAT: Announce presence
                self.send_heartbeat(status="ACTIVE" if active_tasks else "IDLE", current_task=active_tasks[0]['task_id'] if active_tasks else None)
                
                # 6. ADAPT: Adjust interval based on activity (simplified)
                if active_tasks:
                    current_heartbeat_interval = 5  # ACTIVE
                elif new_messages:
                    current_heartbeat_interval = 15 # RESPONSIVE
                else:
                    current_heartbeat_interval = 30 # MONITORING
                
            except Exception as e:
                print(f"❌ {self.manus_id}: Error in work cycle - {e}")
                current_heartbeat_interval = 30  # Back off on errors
            
            # Wait with jitter to prevent thundering herd
            time.sleep(current_heartbeat_interval + random.uniform(-2, 2))

# Example Usage (for testing/demonstration)
if __name__ == '__main__':
    # Example: Create a Manus client
    # Replace with actual Manus ID and capabilities
    client = MACCSClient(
        manus_id="manus_test_maccs",
        capabilities={
            "skills": ["python", "testing", "documentation"],
            "specialization": "general",
            "max_concurrent_tasks": 1
        }
    )

    def example_work_function(task):
        print(f"🔨 {client.manus_id}: Performing work for task: {task['title']}")
        time.sleep(random.uniform(5, 15)) # Simulate work
        client.complete_task(task['task_id'], summary=f"Completed {task['title']}")
        print(f"✅ {client.manus_id}: Finished task: {task['title']}")

    def example_idle_function():
        print(f"💤 {client.manus_id}: No tasks, performing idle activities...")
        time.sleep(random.uniform(5, 10))

    # Start the main loop
    try:
        client.main_loop(
            work_function=example_work_function,
            idle_function=example_idle_function
        )
    except KeyboardInterrupt:
        print(f"\n⚠️  {client.manus_id}: Stopping MACCS client.")


