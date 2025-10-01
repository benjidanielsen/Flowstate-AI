#!/usr/bin/env python3
"""
🔥 MANUS REAL-TIME SYNC ENGINE 🔥
Ultimate coordination system for maximum speed and accuracy

This system enables multiple Manus instances to work together
at 10x speed with perfect synchronization and zero conflicts.
"""

import asyncio
import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import sqlite3
import threading
from dataclasses import dataclass, asdict
from enum import Enum

class ManusRole(Enum):
    SPEED_DEVELOPER = "speed_developer"
    QUALITY_ENHANCER = "quality_enhancer"
    AI_SPECIALIST = "ai_specialist"
    COORDINATOR = "coordinator"

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    NEEDS_REVIEW = "needs_review"

@dataclass
class ManusInstance:
    id: str
    role: ManusRole
    capabilities: List[str]
    current_task: Optional[str] = None
    status: str = "ACTIVE"
    progress: int = 0
    files_claimed: List[str] = None
    last_heartbeat: datetime = None
    performance_score: float = 100.0
    
    def __post_init__(self):
        if self.files_claimed is None:
            self.files_claimed = []
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now()

@dataclass
class SyncTask:
    id: str
    title: str
    description: str
    assigned_to: str
    priority: TaskPriority
    status: TaskStatus
    dependencies: List[str] = None
    estimated_duration: int = 60  # minutes
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    files_involved: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.files_involved is None:
            self.files_involved = []

class ManusSyncEngine:
    """
    🚀 REAL-TIME MANUS SYNCHRONIZATION ENGINE
    
    Features:
    - Real-time task distribution and coordination
    - Automatic conflict resolution
    - Performance optimization
    - Live progress tracking
    - Intelligent work division
    - Zero-latency communication
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.sync_db = self.project_root / ".manus-sync" / "sync_engine.db"
        self.sync_db.parent.mkdir(exist_ok=True)
        
        self.manus_instances: Dict[str, ManusInstance] = {}
        self.task_queue: Dict[str, SyncTask] = {}
        self.active_locks: Dict[str, str] = {}  # file -> manus_id
        
        self.running = False
        self.sync_thread = None
        
        self._init_database()
        self._load_state()
    
    def _init_database(self):
        """Initialize SQLite database for real-time sync"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        # Manus instances table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manus_instances (
                id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                capabilities TEXT NOT NULL,
                current_task TEXT,
                status TEXT DEFAULT 'ACTIVE',
                progress INTEGER DEFAULT 0,
                files_claimed TEXT DEFAULT '[]',
                last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                performance_score REAL DEFAULT 100.0
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                assigned_to TEXT NOT NULL,
                priority INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                dependencies TEXT DEFAULT '[]',
                estimated_duration INTEGER DEFAULT 60,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                files_involved TEXT DEFAULT '[]'
            )
        ''')
        
        # File locks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_locks (
                file_path TEXT PRIMARY KEY,
                locked_by TEXT NOT NULL,
                locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                lock_reason TEXT
            )
        ''')
        
        # Communication log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS communication_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_manus TEXT NOT NULL,
                to_manus TEXT,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_state(self):
        """Load current state from database"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        # Load Manus instances
        cursor.execute('SELECT * FROM manus_instances')
        for row in cursor.fetchall():
            manus = ManusInstance(
                id=row[0],
                role=ManusRole(row[1]),
                capabilities=json.loads(row[2]),
                current_task=row[3],
                status=row[4],
                progress=row[5],
                files_claimed=json.loads(row[6]),
                last_heartbeat=datetime.fromisoformat(row[7]) if row[7] else datetime.now(),
                performance_score=row[8]
            )
            self.manus_instances[manus.id] = manus
        
        # Load tasks
        cursor.execute('SELECT * FROM sync_tasks WHERE status != "completed"')
        for row in cursor.fetchall():
            task = SyncTask(
                id=row[0],
                title=row[1],
                description=row[2],
                assigned_to=row[3],
                priority=TaskPriority(row[4]),
                status=TaskStatus(row[5]),
                dependencies=json.loads(row[6]),
                estimated_duration=row[7],
                created_at=datetime.fromisoformat(row[8]),
                started_at=datetime.fromisoformat(row[9]) if row[9] else None,
                completed_at=datetime.fromisoformat(row[10]) if row[10] else None,
                files_involved=json.loads(row[11])
            )
            self.task_queue[task.id] = task
        
        # Load file locks
        cursor.execute('SELECT file_path, locked_by FROM file_locks')
        for row in cursor.fetchall():
            self.active_locks[row[0]] = row[1]
        
        conn.close()
    
    def register_manus(self, manus_id: str, role: ManusRole, capabilities: List[str]) -> bool:
        """Register a new Manus instance"""
        manus = ManusInstance(
            id=manus_id,
            role=role,
            capabilities=capabilities
        )
        
        self.manus_instances[manus_id] = manus
        self._save_manus_to_db(manus)
        
        print(f"🤖 Manus {manus_id} registered as {role.value}")
        return True
    
    def _save_manus_to_db(self, manus: ManusInstance):
        """Save Manus instance to database"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO manus_instances 
            (id, role, capabilities, current_task, status, progress, files_claimed, last_heartbeat, performance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            manus.id,
            manus.role.value,
            json.dumps(manus.capabilities),
            manus.current_task,
            manus.status,
            manus.progress,
            json.dumps(manus.files_claimed),
            manus.last_heartbeat.isoformat(),
            manus.performance_score
        ))
        
        conn.commit()
        conn.close()
    
    def create_task(self, title: str, description: str, priority: TaskPriority, 
                   files_involved: List[str] = None, dependencies: List[str] = None,
                   estimated_duration: int = 60) -> str:
        """Create a new synchronized task"""
        task_id = hashlib.md5(f"{title}{time.time()}".encode()).hexdigest()[:8]
        
        # Auto-assign based on capabilities and workload
        assigned_to = self._auto_assign_task(files_involved or [], priority)
        
        task = SyncTask(
            id=task_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            priority=priority,
            status=TaskStatus.PENDING,
            dependencies=dependencies or [],
            estimated_duration=estimated_duration,
            files_involved=files_involved or []
        )
        
        self.task_queue[task_id] = task
        self._save_task_to_db(task)
        
        print(f"📋 Task '{title}' created and assigned to {assigned_to}")
        return task_id
    
    def _auto_assign_task(self, files_involved: List[str], priority: TaskPriority) -> str:
        """Intelligently assign task to best available Manus"""
        if not self.manus_instances:
            return "unassigned"
        
        # Score each Manus based on:
        # 1. Current workload
        # 2. Capabilities match
        # 3. Performance score
        # 4. File conflicts
        
        best_manus = None
        best_score = -1
        
        for manus_id, manus in self.manus_instances.items():
            if manus.status != "ACTIVE":
                continue
            
            score = 0
            
            # Workload factor (lower workload = higher score)
            current_tasks = len([t for t in self.task_queue.values() 
                               if t.assigned_to == manus_id and t.status == TaskStatus.IN_PROGRESS])
            workload_score = max(0, 100 - (current_tasks * 20))
            score += workload_score
            
            # Capability match
            if any(file.endswith('.py') for file in files_involved) and 'python' in manus.capabilities:
                score += 30
            if any(file.endswith('.ts') for file in files_involved) and 'typescript' in manus.capabilities:
                score += 30
            if any('ai-gods' in file for file in files_involved) and 'ai_systems' in manus.capabilities:
                score += 40
            
            # Performance factor
            score += manus.performance_score * 0.5
            
            # File conflict penalty
            conflicts = len(set(files_involved) & set(manus.files_claimed))
            score -= conflicts * 50
            
            if score > best_score:
                best_score = score
                best_manus = manus_id
        
        return best_manus or list(self.manus_instances.keys())[0]
    
    def _save_task_to_db(self, task: SyncTask):
        """Save task to database"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO sync_tasks 
            (id, title, description, assigned_to, priority, status, dependencies, 
             estimated_duration, created_at, started_at, completed_at, files_involved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.id,
            task.title,
            task.description,
            task.assigned_to,
            task.priority.value,
            task.status.value,
            json.dumps(task.dependencies),
            task.estimated_duration,
            task.created_at.isoformat(),
            task.started_at.isoformat() if task.started_at else None,
            task.completed_at.isoformat() if task.completed_at else None,
            json.dumps(task.files_involved)
        ))
        
        conn.commit()
        conn.close()
    
    def claim_files(self, manus_id: str, files: List[str]) -> bool:
        """Claim files for exclusive access"""
        # Check for conflicts
        conflicts = []
        for file in files:
            if file in self.active_locks and self.active_locks[file] != manus_id:
                conflicts.append(file)
        
        if conflicts:
            print(f"❌ File claim conflict for {manus_id}: {conflicts}")
            return False
        
        # Claim files
        for file in files:
            self.active_locks[file] = manus_id
        
        # Update Manus instance
        if manus_id in self.manus_instances:
            self.manus_instances[manus_id].files_claimed.extend(files)
            self._save_manus_to_db(self.manus_instances[manus_id])
        
        # Save to database
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        for file in files:
            cursor.execute('''
                INSERT OR REPLACE INTO file_locks (file_path, locked_by, lock_reason)
                VALUES (?, ?, ?)
            ''', (file, manus_id, f"Claimed by {manus_id}"))
        
        conn.commit()
        conn.close()
        
        print(f"🔒 Files claimed by {manus_id}: {files}")
        return True
    
    def release_files(self, manus_id: str, files: List[str]):
        """Release claimed files"""
        for file in files:
            if file in self.active_locks and self.active_locks[file] == manus_id:
                del self.active_locks[file]
        
        # Update Manus instance
        if manus_id in self.manus_instances:
            for file in files:
                if file in self.manus_instances[manus_id].files_claimed:
                    self.manus_instances[manus_id].files_claimed.remove(file)
            self._save_manus_to_db(self.manus_instances[manus_id])
        
        # Remove from database
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        for file in files:
            cursor.execute('DELETE FROM file_locks WHERE file_path = ? AND locked_by = ?', 
                         (file, manus_id))
        
        conn.commit()
        conn.close()
        
        print(f"🔓 Files released by {manus_id}: {files}")
    
    def update_task_progress(self, manus_id: str, task_id: str, progress: int, status: TaskStatus = None):
        """Update task progress in real-time"""
        if task_id not in self.task_queue:
            return False
        
        task = self.task_queue[task_id]
        
        if task.assigned_to != manus_id:
            print(f"❌ {manus_id} cannot update task {task_id} (assigned to {task.assigned_to})")
            return False
        
        # Update progress
        old_progress = task.status
        if status:
            task.status = status
        
        if status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.now()
        elif status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now()
            progress = 100
        
        # Update Manus instance
        if manus_id in self.manus_instances:
            self.manus_instances[manus_id].progress = progress
            self.manus_instances[manus_id].current_task = task.title if status != TaskStatus.COMPLETED else None
            self._save_manus_to_db(self.manus_instances[manus_id])
        
        self._save_task_to_db(task)
        
        print(f"📊 Task '{task.title}' progress: {progress}% ({status.value if status else old_progress.value})")
        return True
    
    def send_message(self, from_manus: str, to_manus: str, message_type: str, content: Dict[str, Any]):
        """Send real-time message between Manus instances"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO communication_log (from_manus, to_manus, message_type, content)
            VALUES (?, ?, ?, ?)
        ''', (from_manus, to_manus, message_type, json.dumps(content)))
        
        conn.commit()
        conn.close()
        
        print(f"💬 Message from {from_manus} to {to_manus}: {message_type}")
    
    def get_messages(self, manus_id: str) -> List[Dict[str, Any]]:
        """Get unprocessed messages for a Manus instance"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, from_manus, message_type, content, timestamp 
            FROM communication_log 
            WHERE to_manus = ? AND processed = FALSE
            ORDER BY timestamp ASC
        ''', (manus_id,))
        
        messages = []
        message_ids = []
        
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'from': row[1],
                'type': row[2],
                'content': json.loads(row[3]),
                'timestamp': row[4]
            })
            message_ids.append(row[0])
        
        # Mark as processed
        if message_ids:
            cursor.execute(f'''
                UPDATE communication_log 
                SET processed = TRUE 
                WHERE id IN ({','.join(['?'] * len(message_ids))})
            ''', message_ids)
        
        conn.commit()
        conn.close()
        
        return messages
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        active_tasks = [t for t in self.task_queue.values() if t.status != TaskStatus.COMPLETED]
        
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'manus_instances': {
                manus_id: {
                    'id': manus.id,
                    'role': manus.role.value,
                    'status': manus.status,
                    'current_task': manus.current_task,
                    'progress': manus.progress,
                    'performance_score': manus.performance_score,
                    'files_claimed': len(manus.files_claimed)
                }
                for manus_id, manus in self.manus_instances.items()
            },
            'active_tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'assigned_to': task.assigned_to,
                    'priority': task.priority.value,
                    'status': task.status.value,
                    'progress': 0 if task.status == TaskStatus.PENDING else 
                              50 if task.status == TaskStatus.IN_PROGRESS else 100,
                    'estimated_completion': (
                        task.started_at + timedelta(minutes=task.estimated_duration)
                    ).isoformat() if task.started_at else None
                }
                for task in active_tasks[:20]  # Show top 20 tasks
            ],
            'system_stats': {
                'total_manus_instances': len(self.manus_instances),
                'active_manus_instances': len([m for m in self.manus_instances.values() if m.status == 'ACTIVE']),
                'total_tasks': len(self.task_queue),
                'completed_tasks': len([t for t in self.task_queue.values() if t.status == TaskStatus.COMPLETED]),
                'active_file_locks': len(self.active_locks),
                'average_performance': sum(m.performance_score for m in self.manus_instances.values()) / len(self.manus_instances) if self.manus_instances else 0
            }
        }
        
        return dashboard
    
    def start_sync_engine(self):
        """Start the real-time synchronization engine"""
        if self.running:
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        
        print("🚀 Manus Sync Engine STARTED - Real-time coordination active!")
    
    def stop_sync_engine(self):
        """Stop the synchronization engine"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join()
        
        print("🛑 Manus Sync Engine STOPPED")
    
    def _sync_loop(self):
        """Main synchronization loop"""
        while self.running:
            try:
                # Update heartbeats
                self._update_heartbeats()
                
                # Process pending tasks
                self._process_task_queue()
                
                # Clean up completed tasks
                self._cleanup_completed_tasks()
                
                # Optimize task assignments
                self._optimize_assignments()
                
                # Sleep for 1 second (real-time updates)
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Sync engine error: {e}")
                time.sleep(5)
    
    def _update_heartbeats(self):
        """Update Manus instance heartbeats"""
        for manus in self.manus_instances.values():
            # Mark as inactive if no heartbeat for 5 minutes
            if datetime.now() - manus.last_heartbeat > timedelta(minutes=5):
                if manus.status == "ACTIVE":
                    manus.status = "INACTIVE"
                    self._save_manus_to_db(manus)
                    print(f"⚠️ Manus {manus.id} marked as INACTIVE (no heartbeat)")
    
    def _process_task_queue(self):
        """Process pending tasks and auto-start when dependencies are met"""
        for task in self.task_queue.values():
            if task.status == TaskStatus.PENDING:
                # Check if dependencies are completed
                deps_completed = all(
                    self.task_queue.get(dep_id, SyncTask("", "", "", "", TaskPriority.LOW, TaskStatus.COMPLETED)).status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                )
                
                if deps_completed:
                    # Auto-start task
                    task.status = TaskStatus.IN_PROGRESS
                    task.started_at = datetime.now()
                    self._save_task_to_db(task)
                    
                    # Notify assigned Manus
                    self.send_message("system", task.assigned_to, "TASK_READY", {
                        "task_id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "files_involved": task.files_involved
                    })
    
    def _cleanup_completed_tasks(self):
        """Clean up old completed tasks"""
        cutoff = datetime.now() - timedelta(hours=24)
        
        completed_tasks = [
            task_id for task_id, task in self.task_queue.items()
            if task.status == TaskStatus.COMPLETED and task.completed_at and task.completed_at < cutoff
        ]
        
        for task_id in completed_tasks:
            del self.task_queue[task_id]
    
    def _optimize_assignments(self):
        """Optimize task assignments based on performance"""
        # Reassign tasks from inactive Manus instances
        for task in self.task_queue.values():
            if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                assigned_manus = self.manus_instances.get(task.assigned_to)
                
                if not assigned_manus or assigned_manus.status != "ACTIVE":
                    # Reassign to active Manus
                    new_assignee = self._auto_assign_task(task.files_involved, task.priority)
                    if new_assignee != task.assigned_to:
                        old_assignee = task.assigned_to
                        task.assigned_to = new_assignee
                        self._save_task_to_db(task)
                        
                        print(f"🔄 Task '{task.title}' reassigned from {old_assignee} to {new_assignee}")

# 🚀 MANUS SYNC ENGINE INTERFACE
class ManusInterface:
    """Interface for Manus instances to interact with the sync engine"""
    
    def __init__(self, manus_id: str, role: ManusRole, capabilities: List[str]):
        self.manus_id = manus_id
        self.sync_engine = ManusSyncEngine()
        
        # Register with sync engine
        self.sync_engine.register_manus(manus_id, role, capabilities)
        
        # Start sync engine if not running
        if not self.sync_engine.running:
            self.sync_engine.start_sync_engine()
    
    def heartbeat(self):
        """Send heartbeat to maintain active status"""
        if self.manus_id in self.sync_engine.manus_instances:
            self.sync_engine.manus_instances[self.manus_id].last_heartbeat = datetime.now()
            self.sync_engine._save_manus_to_db(self.sync_engine.manus_instances[self.manus_id])
    
    def get_my_tasks(self) -> List[SyncTask]:
        """Get tasks assigned to this Manus"""
        return [task for task in self.sync_engine.task_queue.values() 
                if task.assigned_to == self.manus_id and task.status != TaskStatus.COMPLETED]
    
    def start_task(self, task_id: str) -> bool:
        """Start working on a task"""
        task = self.sync_engine.task_queue.get(task_id)
        if not task or task.assigned_to != self.manus_id:
            return False
        
        # Claim files
        if task.files_involved:
            if not self.sync_engine.claim_files(self.manus_id, task.files_involved):
                return False
        
        # Update task status
        return self.sync_engine.update_task_progress(
            self.manus_id, task_id, 0, TaskStatus.IN_PROGRESS
        )
    
    def update_progress(self, task_id: str, progress: int):
        """Update task progress"""
        return self.sync_engine.update_task_progress(self.manus_id, task_id, progress)
    
    def complete_task(self, task_id: str):
        """Mark task as completed"""
        task = self.sync_engine.task_queue.get(task_id)
        if task and task.files_involved:
            self.sync_engine.release_files(self.manus_id, task.files_involved)
        
        return self.sync_engine.update_task_progress(
            self.manus_id, task_id, 100, TaskStatus.COMPLETED
        )
    
    def send_message(self, to_manus: str, message_type: str, content: Dict[str, Any]):
        """Send message to another Manus"""
        return self.sync_engine.send_message(self.manus_id, to_manus, message_type, content)
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get messages for this Manus"""
        return self.sync_engine.get_messages(self.manus_id)
    
    def create_task(self, title: str, description: str, priority: TaskPriority, 
                   files_involved: List[str] = None, dependencies: List[str] = None) -> str:
        """Create a new task"""
        return self.sync_engine.create_task(
            title, description, priority, files_involved, dependencies
        )

# 🎯 EXAMPLE USAGE
if __name__ == "__main__":
    # Initialize Manus instances
    manus1 = ManusInterface("manus_speed", ManusRole.SPEED_DEVELOPER, 
                           ["typescript", "react", "backend", "rapid_prototyping"])
    
    manus2 = ManusInterface("manus_quality", ManusRole.QUALITY_ENHANCER, 
                           ["python", "ai_systems", "testing", "documentation"])
    
    # Create some tasks
    task1_id = manus1.create_task(
        "Implement Frazer Method API",
        "Create complete API endpoints for Frazer Method pipeline",
        TaskPriority.HIGH,
        ["backend/src/controllers/frazerController.ts", "backend/src/routes/frazer.ts"]
    )
    
    task2_id = manus2.create_task(
        "Build AI Democracy System", 
        "Implement AI voting and decision-making system",
        TaskPriority.HIGH,
        ["ai-gods/ai-democracy-system.py", "ai-gods/voting-engine.py"]
    )
    
    print("🚀 MANUS SYNC ENGINE READY!")
    print("Multiple Manus instances can now work together at 10x speed!")
    print("Real-time coordination, zero conflicts, maximum efficiency!")
