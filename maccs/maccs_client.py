import sqlite3
import json
import uuid
import subprocess
import os
import time
import random
from datetime import datetime, timedelta
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
        try:
            conn = sqlite3.connect(self.db_filepath, timeout=30) # 30s timeout for busy errors
            conn.row_factory = sqlite3.Row # Access columns by name
            return conn
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return None

    def _initialize_db(self):
        if not self.conn: return
        try:
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
            """)

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
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_priority_status ON tasks (priority, status);
            """)

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
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")

    def _load_capabilities(self):
        if not self.conn: return {}
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM capabilities WHERE manus_id = ?", (self.manus_id,))
            caps = cursor.fetchone()
            if caps:
                caps_dict = dict(caps)
                return {k: json.loads(v) if k in ['skills', 'preferred_task_types'] and v is not None else v for k, v in caps_dict.items() if k != 'manus_id'}
            return {}
        except sqlite3.Error as e:
            print(f"Error loading capabilities for {self.manus_id}: {e}")
            return {}

    def update_capabilities(self, skills=None, specialization=None, max_concurrent_tasks=None, preferred_task_types=None):
        if not self.conn: return
        try:
            current_caps = self._load_capabilities()
            if skills is not None: current_caps["skills"] = skills
            if specialization is not None: current_caps["specialization"] = specialization
            if max_concurrent_tasks is not None: current_caps["max_concurrent_tasks"] = max_concurrent_tasks
            if preferred_task_types is not None: current_caps["preferred_task_types"] = preferred_task_types
            
            self.conn.execute("""
                INSERT OR REPLACE INTO capabilities (manus_id, skills, specialization, max_concurrent_tasks, preferred_task_types)
                VALUES (?, ?, ?, ?, ?)
            """, (self.manus_id, json.dumps(current_caps.get("skills", [])), current_caps.get("specialization"),
                 current_caps.get("max_concurrent_tasks"), json.dumps(current_caps.get("preferred_task_types", []))))
            self.conn.commit()
            self.capabilities = current_caps
        except sqlite3.Error as e:
            print(f"Error updating capabilities for {self.manus_id}: {e}")

    def send_message(self, to, msg_type, payload, priority="NORMAL", requires_approval=False, thread_id=None):
        if not self.conn: return None
        try:
            message_id = str(uuid.uuid4())
            self.conn.execute("""
                INSERT INTO messages (id, sender_id, recipient_id, type, priority, payload, requires_approval, thread_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (message_id, self.manus_id, to, msg_type, priority, json.dumps(payload), requires_approval, thread_id))
            self.conn.commit()
            return message_id
        except sqlite3.Error as e:
            print(f"Error sending message from {self.manus_id} to {to}: {e}")
            return None

    def get_unread_messages(self):
        if not self.conn: return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM messages
                WHERE recipient_id = ? AND read = FALSE
                ORDER BY timestamp ASC
            """, (self.manus_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting unread messages for {self.manus_id}: {e}")
            return []

    def mark_message_read(self, message_id):
        if not self.conn: return
        try:
            self.conn.execute("UPDATE messages SET read = TRUE WHERE id = ?", (message_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error marking message {message_id} as read: {e}")

    def post_task(self, title, description, required_skills, priority="NORMAL", estimated_effort=None, deadline=None, dependencies=None, reward_credits=None):
        if not self.conn: return None
        try:
            task_id = str(uuid.uuid4())
            self.conn.execute("""
                INSERT INTO tasks (task_id, title, description, required_skills, priority, estimated_effort, deadline, dependencies, reward_credits, posted_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (task_id, title, description, json.dumps(required_skills), priority, estimated_effort, deadline, json.dumps(dependencies) if dependencies else None, reward_credits, self.manus_id))
            self.conn.commit()
            return task_id
        except sqlite3.Error as e:
            print(f"Error posting task by {self.manus_id}: {e}")
            return None

    def claim_task(self, task_id):
        if not self.conn: return False
        try:
            cursor = self.conn.execute("""
                UPDATE tasks SET status = 'CLAIMED', claimed_by = ?, claimed_at = CURRENT_TIMESTAMP
                WHERE task_id = ? AND status = 'AVAILABLE'
            """, (self.manus_id, task_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                self.send_message("broadcast", "TASK_CLAIMED", {"task_id": task_id, "claimed_by": self.manus_id})
                return True
            return False
        except sqlite3.Error as e:
            print(f"Error claiming task {task_id} by {self.manus_id}: {e}")
            return False

    def update_task_status(self, task_id, status, progress=None, details=None):
        if not self.conn: return
        try:
            self.conn.execute("""
                UPDATE tasks SET status = ?
                WHERE task_id = ?
            """, (status, task_id))
            self.conn.commit()
            # Optionally send a message for significant status changes
            self.send_message("broadcast", "TASK_STATUS_UPDATE", {"task_id": task_id, "status": status, "progress": progress, "details": details})
        except sqlite3.Error as e:
            print(f"Error updating status for task {task_id}: {e}")

    def complete_task(self, task_id, summary, artifacts=None):
        if not self.conn: return
        try:
            self.conn.execute("""
                UPDATE tasks SET status = 'COMPLETED', completed_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            """, (task_id,))
            self.conn.commit()
            self.send_message("manus_2", "TASK_COMPLETE", {"task_id": task_id, "summary": summary, "artifacts": artifacts}, priority="HIGH", requires_approval=True)
        except sqlite3.Error as e:
            print(f"Error completing task {task_id}: {e}")

    def approve_task(self, task_id, approved_by="manus_2"):
        if not self.conn: return
        try:
            self.conn.execute("""
                UPDATE tasks SET status = 'APPROVED', approved_by = ?, approved_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            """, (approved_by, task_id))
            self.conn.commit()
            self.send_message("broadcast", "TASK_APPROVED", {"task_id": task_id, "approved_by": approved_by})
        except sqlite3.Error as e:
            print(f"Error approving task {task_id}: {e}")

    def reject_task(self, task_id, feedback, rejected_by="manus_2"):
        if not self.conn: return
        try:
            self.conn.execute("""
                UPDATE tasks SET status = 'REJECTED'
                WHERE task_id = ?
            """, (task_id,))
            self.conn.commit()
            self.send_message("broadcast", "TASK_REJECTED", {"task_id": task_id, "feedback": feedback, "rejected_by": rejected_by})
        except sqlite3.Error as e:
            print(f"Error rejecting task {task_id}: {e}")

    def send_heartbeat(self, status="ACTIVE", current_task=None, heartbeat_interval=15):
        if not self.conn: return
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO heartbeats (manus_id, status, current_task, timestamp, capabilities, heartbeat_interval)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
            """, (self.manus_id, status, current_task, json.dumps(self.capabilities), heartbeat_interval))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error sending heartbeat for {self.manus_id}: {e}")

    def get_all_heartbeats(self):
        if not self.conn: return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM heartbeats")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting all heartbeats: {e}")
            return []

    def _calculate_task_score(self, task):
        if not self.conn: return -1 # Indicate error or inability to score
        score = 0
        try:
            my_skills = set(self.capabilities.get("skills", []))
            required_skills_json = task.get("required_skills")
            required_skills = set(json.loads(required_skills_json)) if required_skills_json else set()
            matching_skills = my_skills.intersection(required_skills)
            score += len(matching_skills) * 10

            priority_map = {"URGENT": 10, "HIGH": 5, "NORMAL": 0, "LOW": -5}
            score += priority_map.get(task.get("priority", "NORMAL"), 0)

            # Consider workload (number of active tasks for this manus)
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE claimed_by = ? AND status IN ('CLAIMED', 'IN_PROGRESS')", (self.manus_id,))
            my_active_tasks_count = cursor.fetchone()[0]
            score -= my_active_tasks_count * 5

            return score
        except (json.JSONDecodeError, sqlite3.Error, TypeError) as e:
            print(f"Error calculating task score for task {task.get('task_id')}: {e}")
            return -1 # Return a low score or error indicator

    def get_all_tasks(self):
        if not self.conn: return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM tasks")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting all tasks: {e}")
            return []

    def discover_best_task(self):
        if not self.conn: return None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE status = 'AVAILABLE'")
            available_tasks = [dict(row) for row in cursor.fetchall()]

            if not available_tasks:
                return None

            scored_tasks = []
            for task in available_tasks:
                score = self._calculate_task_score(task)
                if score != -1: # Only consider tasks that were successfully scored
                    scored_tasks.append((score, task))

            scored_tasks.sort(key=lambda x: x[0], reverse=True)
            return scored_tasks[0][1] if scored_tasks else None
        except sqlite3.Error as e:
            print(f"Error discovering best task for {self.manus_id}: {e}")
            return None

    def git_sync_and_backup(self):
        if not self.conn: return False
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Ensure we are in the correct directory
                original_cwd = os.getcwd()
                os.chdir(self.repo_path)

                # Pull latest changes first to avoid conflicts
                pull_result = subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True, capture_output=True)
                # print(f"Git pull output: {pull_result.stdout.decode()}")
                # print(f"Git pull error: {pull_result.stderr.decode()}")
                
                # Add the database file
                subprocess.run(["git", "add", self.db_filepath], check=True, capture_output=True)
                
                # Commit if there are changes
                commit_result = subprocess.run(["git", "commit", "-m", f"MACCS v3.0: SQLite DB backup from {self.manus_id}"], capture_output=True)
                if "nothing to commit" not in commit_result.stdout.decode():
                    # print(f"Git commit output: {commit_result.stdout.decode()}")
                    # print(f"Git commit error: {commit_result.stderr.decode()}")
                    subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
                    self.conn.execute("UPDATE heartbeats SET last_git_sync = CURRENT_TIMESTAMP WHERE manus_id = ?", (self.manus_id,))
                    self.conn.commit()
                os.chdir(original_cwd)
                return True
            except subprocess.CalledProcessError as e:
                print(f"Git sync failed on attempt {attempt + 1}/{max_retries}: {e.stderr}")
                os.chdir(original_cwd)
                time.sleep(random.uniform(1, 5)) # Wait a bit before retrying
            except Exception as e:
                print(f"An unexpected error occurred during Git sync on attempt {attempt + 1}/{max_retries}: {e}")
                os.chdir(original_cwd)
                time.sleep(random.uniform(1, 5)) # Wait a bit before retrying
        print(f"Git sync failed after {max_retries} attempts.")
        return False

    def close(self):
        if self.conn:
            self.conn.close()

    def start_watching(self):
        event_handler = self.DatabaseChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.db_dir, recursive=False)
        self.observer.start()
        print(f"{self.manus_id} is now watching for database changes.")

    def stop_watching(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print(f"{self.manus_id} has stopped watching for database changes.")

    class DatabaseChangeHandler(FileSystemEventHandler):
        def __init__(self, client):
            self.client = client

        def on_modified(self, event):
            if event.src_path == self.client.db_filepath:
                print(f"Database file changed. {self.client.manus_id} is checking for unread messages.")
                self.client.check_for_messages_and_tasks()

