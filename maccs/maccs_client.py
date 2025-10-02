import sqlite3
import json
import uuid
from datetime import datetime, timedelta
import subprocess
import time
import random
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MACCSClientV3:
    def __init__(self, manus_id, repo_path, db_path="maccs/coordination.db"):
        self.manus_id = manus_id
        self.repo_path = repo_path
        self.db_filepath = os.path.join(repo_path, db_path)
        self.db_dir = os.path.dirname(self.db_filepath)
        os.makedirs(self.db_dir, exist_ok=True)
        self.conn = self._get_db_connection()
        self._initialize_db()
        self.capabilities = self._load_capabilities()
        self.observer = None

    def _get_db_connection(self):
        conn = sqlite3.connect(self.db_filepath, timeout=30) # 30s timeout for busy errors
        conn.row_factory = sqlite3.Row # Access columns by name
        return conn

    def _initialize_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sender_id TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                type TEXT NOT NULL,
                priority TEXT DEFAULT 'NORMAL',
                payload JSON,
                read BOOLEAN DEFAULT FALSE,
                requires_approval BOOLEAN DEFAULT FALSE,
                thread_id TEXT
            );
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipient_read ON messages (recipient_id, read);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON messages (timestamp);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_priority ON messages (priority);
        """
        )

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'AVAILABLE',
                required_skills JSON,
                priority TEXT DEFAULT 'NORMAL',
                estimated_effort TEXT,
                deadline DATETIME,
                dependencies JSON,
                reward_credits INTEGER,
                posted_by TEXT NOT NULL,
                posted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                claimed_by TEXT,
                claimed_at DATETIME,
                completed_at DATETIME,
                approved_by TEXT,
                approved_at DATETIME
            );
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_status ON tasks (status);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_assigned ON tasks (claimed_by);
        """
        )
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_priority_status ON tasks (priority, status);
        """
        )

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS heartbeats (
                manus_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                current_task TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                capabilities JSON,
                heartbeat_interval INTEGER,
                last_git_sync DATETIME
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS capabilities (
                manus_id TEXT PRIMARY KEY,
                skills JSON,
                specialization TEXT,
                max_concurrent_tasks INTEGER,
                preferred_task_types JSON
            );
        """)
        self.conn.commit()

    def _load_capabilities(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM capabilities WHERE manus_id = ?", (self.manus_id,))
        caps = cursor.fetchone()
        if caps:
            caps_dict = dict(caps)
            return {k: json.loads(v) if k in ['skills', 'preferred_task_types'] and v is not None else v for k, v in caps_dict.items() if k != 'manus_id'}
        return {}

    def update_capabilities(self, skills=None, specialization=None, max_concurrent_tasks=None, preferred_task_types=None):
        current_caps = self._load_capabilities()
        if skills is not None: current_caps['skills'] = skills
        if specialization is not None: current_caps['specialization'] = specialization
        if max_concurrent_tasks is not None: current_caps['max_concurrent_tasks'] = max_concurrent_tasks
        if preferred_task_types is not None: current_caps['preferred_task_types'] = preferred_task_types
        
        self.conn.execute("""
            INSERT OR REPLACE INTO capabilities (manus_id, skills, specialization, max_concurrent_tasks, preferred_task_types)
            VALUES (?, ?, ?, ?, ?)
        """, (self.manus_id, json.dumps(current_caps.get('skills', [])), current_caps.get('specialization'),
             current_caps.get('max_concurrent_tasks'), json.dumps(current_caps.get('preferred_task_types', []))))
        self.conn.commit()
        self.capabilities = current_caps

    def send_message(self, to, msg_type, payload, priority="NORMAL", requires_approval=False, thread_id=None):
        message_id = str(uuid.uuid4())
        self.conn.execute("""
            INSERT INTO messages (id, sender_id, recipient_id, type, priority, payload, requires_approval, thread_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (message_id, self.manus_id, to, msg_type, priority, json.dumps(payload), requires_approval, thread_id))
        self.conn.commit()
        return message_id

    def get_unread_messages(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM messages
            WHERE recipient_id = ? AND read = FALSE
            ORDER BY timestamp ASC
        """, (self.manus_id,))
        return [dict(row) for row in cursor.fetchall()]

    def mark_message_read(self, message_id):
        self.conn.execute("UPDATE messages SET read = TRUE WHERE id = ?", (message_id,))
        self.conn.commit()

    def post_task(self, title, description, required_skills, priority="NORMAL", estimated_effort=None, deadline=None, dependencies=None, reward_credits=None):
        task_id = str(uuid.uuid4())
        self.conn.execute("""
            INSERT INTO tasks (task_id, title, description, required_skills, priority, estimated_effort, deadline, dependencies, reward_credits, posted_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (task_id, title, description, json.dumps(required_skills), priority, estimated_effort, deadline, json.dumps(dependencies) if dependencies else None, reward_credits, self.manus_id))
        self.conn.commit()
        return task_id

    def claim_task(self, task_id):
        self.conn.execute("""
            UPDATE tasks SET status = 'CLAIMED', claimed_by = ?, claimed_at = CURRENT_TIMESTAMP
            WHERE task_id = ? AND status = 'AVAILABLE'
        """, (self.manus_id, task_id))
        self.conn.commit()
        self.send_message("broadcast", "TASK_CLAIMED", {"task_id": task_id, "claimed_by": self.manus_id})

    def update_task_status(self, task_id, status, progress=None, details=None):
        self.conn.execute("""
            UPDATE tasks SET status = ?
            WHERE task_id = ?
        """, (status, task_id))
        self.conn.commit()
        # Optionally send a message for significant status changes
        self.send_message("broadcast", "TASK_STATUS_UPDATE", {"task_id": task_id, "status": status, "progress": progress, "details": details})

    def complete_task(self, task_id, summary, artifacts=None):
        self.conn.execute("""
            UPDATE tasks SET status = 'COMPLETED', completed_at = CURRENT_TIMESTAMP
            WHERE task_id = ?
        """, (task_id,))
        self.conn.commit()
        self.send_message("manus_2", "TASK_COMPLETE", {"task_id": task_id, "summary": summary, "artifacts": artifacts}, priority="HIGH", requires_approval=True)

    def approve_task(self, task_id, approved_by="manus_2"):
        self.conn.execute("""
            UPDATE tasks SET status = 'APPROVED', approved_by = ?, approved_at = CURRENT_TIMESTAMP
            WHERE task_id = ?
        """, (approved_by, task_id))
        self.conn.commit()
        self.send_message("broadcast", "TASK_APPROVED", {"task_id": task_id, "approved_by": approved_by})

    def reject_task(self, task_id, feedback, rejected_by="manus_2"):
        self.conn.execute("""
            UPDATE tasks SET status = 'REJECTED'
            WHERE task_id = ?
        """, (task_id,))
        self.conn.commit()
        self.send_message("broadcast", "TASK_REJECTED", {"task_id": task_id, "feedback": feedback, "rejected_by": rejected_by})

    def send_heartbeat(self, status="ACTIVE", current_task=None, heartbeat_interval=15):
        self.conn.execute("""
            INSERT OR REPLACE INTO heartbeats (manus_id, status, current_task, timestamp, capabilities, heartbeat_interval)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
        """, (self.manus_id, status, current_task, json.dumps(self.capabilities), heartbeat_interval))
        self.conn.commit()

    def get_all_heartbeats(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM heartbeats")
        return [dict(row) for row in cursor.fetchall()]

    def _calculate_task_score(self, task):
        score = 0
        my_skills = set(self.capabilities.get("skills", []))
        required_skills = set(json.loads(task["required_skills"])) if task["required_skills"] else set()
        matching_skills = my_skills.intersection(required_skills)
        score += len(matching_skills) * 10

        priority_map = {"URGENT": 10, "HIGH": 5, "NORMAL": 0, "LOW": -5}
        score += priority_map.get(task["priority"], 0)

        # Consider workload (number of active tasks for this manus)
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE claimed_by = ? AND status IN ('CLAIMED', 'IN_PROGRESS')", (self.manus_id,))
        my_active_tasks_count = cursor.fetchone()[0]
        score -= my_active_tasks_count * 5

        return score

    def get_all_tasks(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        return [dict(row) for row in cursor.fetchall()]

    def discover_best_task(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE status = 'AVAILABLE'")
        available_tasks = [dict(row) for row in cursor.fetchall()]

        if not available_tasks:
            return None

        scored_tasks = []
        for task in available_tasks:
            score = self._calculate_task_score(task)
            scored_tasks.append((score, task))

        scored_tasks.sort(key=lambda x: x[0], reverse=True)
        return scored_tasks[0][1] if scored_tasks else None

    def git_sync_and_backup(self):
        try:
            # Pull latest changes first to avoid conflicts
            subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=self.repo_path, check=True, capture_output=True)
            
            # Add the database file
            subprocess.run(["git", "add", self.db_filepath], cwd=self.repo_path, check=True)
            
            # Commit if there are changes
            result = subprocess.run(["git", "commit", "-m", f"MACCS v3.0: SQLite DB backup from {self.manus_id}"], 
                                 cwd=self.repo_path, capture_output=True)
            if "nothing to commit" not in result.stdout.decode():
                subprocess.run(["git", "push", "origin", "main"], cwd=self.repo_path, check=True)
                self.conn.execute("UPDATE heartbeats SET last_git_sync = CURRENT_TIMESTAMP WHERE manus_id = ?", (self.manus_id,))
                self.conn.commit()
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git sync failed: {e.stderr.decode()}")
            return False

    def close(self):
        if self.conn:
            self.conn.close()
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def start_db_watcher(self, callback):
        class DBChangeHandler(FileSystemEventHandler):
            def __init__(self, client, callback):
                self.client = client
                self.callback = callback

            def on_modified(self, event):
                if event.src_path == self.client.db_filepath:
                    self.callback()

        self.observer = Observer()
        event_handler = DBChangeHandler(self, callback)
        self.observer.schedule(event_handler, self.db_dir, recursive=False)
        self.observer.start()


# Example Usage (Main Loop for a Manus Instance)
# def manus_main_loop(client):
#     current_task_id = None
#     while True:
#         # 1. Process incoming messages (triggered by watcher or periodic check)
#         unread_messages = client.get_unread_messages()
#         for msg in unread_messages:
#             print(f"[{client.manus_id}] Received message: {msg['type']} from {msg['sender_id']}")
#             client.mark_message_read(msg['id'])
#             # Handle message based on type (e.g., TASK_APPROVED, DIRECT_MESSAGE)
#
#         # 2. Execute current task
#         if current_task_id:
#             # Perform work, update progress
#             client.update_task_status(current_task_id, "IN_PROGRESS", progress=50)
#             # If task completed:
#             # client.complete_task(current_task_id, "Task done", ["path/to/artifact.md"])
#             # current_task_id = None
#
#         # 3. Discover and claim new task if idle
#         if not current_task_id:
#             best_task = client.discover_best_task()
#             if best_task:
#                 client.claim_task(best_task['task_id'])
#                 current_task_id = best_task['task_id']
#                 print(f"[{client.manus_id}] Claimed task: {best_task['title']}")
#
#         # 4. Send heartbeat
#         client.send_heartbeat(current_task=current_task_id)
#
#         # 5. Periodic Git backup (every 5 minutes)
#         last_sync_time = client.conn.execute("SELECT last_git_sync FROM heartbeats WHERE manus_id = ?", (client.manus_id,)).fetchone()
#         if not last_sync_time or (datetime.utcnow() - datetime.fromisoformat(last_sync_time[0])) > timedelta(minutes=5):
#             client.git_sync_and_backup()
#
#         time.sleep(random.uniform(5, 15)) # Adaptive sleep interval

# if __name__ == "__main__":
#     # Example setup for Manus #5
#     manus_5_capabilities = {
#         "skills": ["python", "testing", "documentation", "bug_fixing", "system_architecture"],
#         "specialization": "quality_assurance",
#         "max_concurrent_tasks": 2,
#         "preferred_task_types": ["bug_fix", "testing", "code_review", "design"]
#     }
#     client = MACCSClientV3("manus_5", "/home/ubuntu/Flowstate-AI")
#     client.update_capabilities(**manus_5_capabilities)
#
#     # Start the main loop in a separate thread or process for continuous operation
#     # For this sandbox environment, we'll simulate a single run
#     print(f"[{client.manus_id}] Initializing MACCS v3.0...")
#     client.send_heartbeat(status="INITIALIZING")
#     client.git_sync_and_backup() # Initial backup
#     print(f"[{client.manus_id}] MACCS v3.0 ready. Monitoring for tasks.")
#     # In a real scenario, manus_main_loop(client) would run here persistently
#     client.close()
