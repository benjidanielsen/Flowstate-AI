#!/usr/bin/env python3
"""
🤖 ENHANCED PROJECT MANAGER AI - Advanced Coordination System
⚡ GODMODE: Unlimited autonomous development authority
🎯 Mission: Orchestrate AI agent ecosystem with advanced features
🧠 Capabilities: Voting, dependency management, performance tracking, and more
"""

import asyncio
import json
import time
import logging
import sqlite3
import redis
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='🤖 [PM-ENHANCED] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/project-manager-enhanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enumeration"""
    QUEUED = "QUEUED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class VoteType(Enum):
    """Vote types for decision-making"""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ABSTAIN = "ABSTAIN"


@dataclass
class Task:
    """Task data structure"""
    id: str
    name: str
    description: str
    assigned_to: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    dependencies: List[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_duration: int  # in minutes
    actual_duration: Optional[int]
    metadata: Dict[str, Any]


@dataclass
class AgentPerformance:
    """Agent performance metrics"""
    agent_id: str
    tasks_completed: int
    tasks_failed: int
    average_completion_time: float
    success_rate: float
    current_load: int
    capabilities: List[str]
    last_active: datetime


@dataclass
class Vote:
    """Vote data structure"""
    proposal_id: str
    agent_id: str
    vote_type: VoteType
    reason: str
    timestamp: datetime


class EnhancedProjectManagerAI:
    """
    Enhanced Project Manager AI with advanced coordination capabilities
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379, db_path='godmode-state.db'):
        self.project_root = Path(__file__).parent.parent
        self.db_path = self.project_root / db_path
        
        # Initialize Redis for real-time communication
        try:
            self.redis_client = redis.StrictRedis(
                host=redis_host, 
                port=redis_port, 
                db=0, 
                decode_responses=True
            )
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {e}. Using fallback mode.")
            self.redis_available = False
        
        # Initialize SQLite database
        self.init_database()
        
        # Agent registry
        self.agents: Dict[str, AgentPerformance] = {}
        
        # Task management
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        
        # Voting system
        self.active_proposals: Dict[str, Dict] = {}
        self.votes: Dict[str, List[Vote]] = {}
        
        # System state
        self.godmode_enabled = True
        self.system_status = "INITIALIZING"
        
        logger.info("🚀 ENHANCED PROJECT MANAGER AI INITIALIZED")
    
    def init_database(self):
        """Initialize SQLite database for persistent state"""
        self.db_connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.db_cursor = self.db_connection.cursor()
        
        # Create tables
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                assigned_to TEXT,
                status TEXT NOT NULL,
                priority INTEGER NOT NULL,
                dependencies TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                estimated_duration INTEGER,
                actual_duration INTEGER,
                metadata TEXT
            )
        ''')
        
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                tasks_completed INTEGER DEFAULT 0,
                tasks_failed INTEGER DEFAULT 0,
                average_completion_time REAL DEFAULT 0.0,
                success_rate REAL DEFAULT 100.0,
                current_load INTEGER DEFAULT 0,
                capabilities TEXT,
                last_active TEXT
            )
        ''')
        
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS proposals (
                proposal_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                proposer_id TEXT NOT NULL,
                proposal_type TEXT NOT NULL,
                threshold REAL NOT NULL,
                created_at TEXT NOT NULL,
                deadline TEXT NOT NULL,
                status TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                vote_type TEXT NOT NULL,
                reason TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (proposal_id) REFERENCES proposals (proposal_id)
            )
        ''')
        
        self.db_connection.commit()
        logger.info("📊 Database initialized successfully")
    
    def register_agent(self, agent_id: str, capabilities: List[str]):
        """Register a new agent in the system"""
        performance = AgentPerformance(
            agent_id=agent_id,
            tasks_completed=0,
            tasks_failed=0,
            average_completion_time=0.0,
            success_rate=100.0,
            current_load=0,
            capabilities=capabilities,
            last_active=datetime.now()
        )
        
        self.agents[agent_id] = performance
        
        # Persist to database
        self.db_cursor.execute('''
            INSERT OR REPLACE INTO agents 
            (agent_id, capabilities, last_active)
            VALUES (?, ?, ?)
        ''', (agent_id, json.dumps(capabilities), datetime.now().isoformat()))
        self.db_connection.commit()
        
        logger.info(f"✅ Agent registered: {agent_id} with capabilities {capabilities}")
        
        # Publish to Redis
        if self.redis_available:
            self.redis_client.publish('agent_registry', json.dumps({
                'action': 'register',
                'agent_id': agent_id,
                'capabilities': capabilities,
                'timestamp': datetime.now().isoformat()
            }))
    
    def create_task(self, name: str, description: str, priority: TaskPriority, 
                   dependencies: List[str] = None, estimated_duration: int = 60,
                   metadata: Dict[str, Any] = None) -> Task:
        """Create a new task"""
        task_id = f"task_{int(time.time() * 1000)}"
        task = Task(
            id=task_id,
            name=name,
            description=description,
            assigned_to=None,
            status=TaskStatus.QUEUED,
            priority=priority,
            dependencies=dependencies or [],
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            estimated_duration=estimated_duration,
            actual_duration=None,
            metadata=metadata or {}
        )
        
        self.tasks[task_id] = task
        self.task_queue.append(task_id)
        
        # Persist to database
        self.db_cursor.execute('''
            INSERT INTO tasks 
            (id, name, description, status, priority, dependencies, created_at, estimated_duration, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id, name, description, task.status.value, task.priority.value,
            json.dumps(dependencies or []), task.created_at.isoformat(),
            estimated_duration, json.dumps(metadata or {})
        ))
        self.db_connection.commit()
        
        logger.info(f"📝 Task created: {name} (ID: {task_id}, Priority: {priority.name})")
        
        return task
    
    def assign_task_to_agent(self, task_id: str) -> Optional[str]:
        """Intelligently assign a task to the best available agent"""
        task = self.tasks.get(task_id)
        if not task:
            logger.error(f"❌ Task not found: {task_id}")
            return None
        
        # Check if dependencies are met
        if not self.are_dependencies_met(task):
            logger.info(f"⏸️ Task {task.name} blocked by dependencies")
            task.status = TaskStatus.BLOCKED
            return None
        
        # Find the best agent for this task
        best_agent = self.find_best_agent_for_task(task)
        
        if not best_agent:
            logger.warning(f"⚠️ No suitable agent found for task: {task.name}")
            return None
        
        # Assign the task
        task.assigned_to = best_agent
        task.status = TaskStatus.ASSIGNED
        task.started_at = datetime.now()
        
        # Update agent load
        self.agents[best_agent].current_load += 1
        
        # Update database
        self.db_cursor.execute('''
            UPDATE tasks 
            SET assigned_to = ?, status = ?, started_at = ?
            WHERE id = ?
        ''', (best_agent, task.status.value, task.started_at.isoformat(), task_id))
        self.db_connection.commit()
        
        logger.info(f"✅ Task {task.name} assigned to {best_agent}")
        
        # Publish to Redis
        if self.redis_available:
            self.redis_client.publish('task_assignments', json.dumps({
                'task_id': task_id,
                'task_name': task.name,
                'assigned_to': best_agent,
                'timestamp': datetime.now().isoformat()
            }))
        
        return best_agent
    
    def are_dependencies_met(self, task: Task) -> bool:
        """Check if all task dependencies are completed"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def find_best_agent_for_task(self, task: Task) -> Optional[str]:
        """Find the best agent for a task based on capabilities, load, and performance"""
        # Required capabilities for the task
        required_capabilities = task.metadata.get('required_capabilities', [])
        
        # Score each agent
        agent_scores = []
        for agent_id, performance in self.agents.items():
            # Check if agent has required capabilities
            if required_capabilities:
                if not all(cap in performance.capabilities for cap in required_capabilities):
                    continue
            
            # Calculate score based on multiple factors
            load_score = 1.0 / (performance.current_load + 1)  # Lower load is better
            success_score = performance.success_rate / 100.0
            speed_score = 1.0 / (performance.average_completion_time + 1)
            
            total_score = (load_score * 0.4) + (success_score * 0.4) + (speed_score * 0.2)
            
            agent_scores.append((agent_id, total_score))
        
        if not agent_scores:
            return None
        
        # Sort by score and return the best agent
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        return agent_scores[0][0]
    
    def complete_task(self, task_id: str, success: bool = True):
        """Mark a task as completed"""
        task = self.tasks.get(task_id)
        if not task:
            logger.error(f"❌ Task not found: {task_id}")
            return
        
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        task.completed_at = datetime.now()
        task.actual_duration = int((task.completed_at - task.started_at).total_seconds() / 60)
        
        # Update agent performance
        if task.assigned_to:
            agent = self.agents[task.assigned_to]
            agent.current_load -= 1
            
            if success:
                agent.tasks_completed += 1
            else:
                agent.tasks_failed += 1
            
            # Update average completion time
            total_tasks = agent.tasks_completed + agent.tasks_failed
            agent.average_completion_time = (
                (agent.average_completion_time * (total_tasks - 1) + task.actual_duration) / total_tasks
            )
            
            # Update success rate
            agent.success_rate = (agent.tasks_completed / total_tasks) * 100
            
            # Update database
            self.db_cursor.execute('''
                UPDATE agents 
                SET tasks_completed = ?, tasks_failed = ?, average_completion_time = ?, 
                    success_rate = ?, current_load = ?
                WHERE agent_id = ?
            ''', (
                agent.tasks_completed, agent.tasks_failed, agent.average_completion_time,
                agent.success_rate, agent.current_load, task.assigned_to
            ))
        
        # Update task in database
        self.db_cursor.execute('''
            UPDATE tasks 
            SET status = ?, completed_at = ?, actual_duration = ?
            WHERE id = ?
        ''', (task.status.value, task.completed_at.isoformat(), task.actual_duration, task_id))
        self.db_connection.commit()
        
        logger.info(f"✅ Task completed: {task.name} (Duration: {task.actual_duration} min)")
        
        # Check for unblocked tasks
        self.check_unblocked_tasks()
    
    def check_unblocked_tasks(self):
        """Check for tasks that can now be unblocked"""
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.BLOCKED and self.are_dependencies_met(task):
                task.status = TaskStatus.QUEUED
                self.task_queue.append(task_id)
                logger.info(f"🔓 Task unblocked: {task.name}")
    
    def create_proposal(self, title: str, description: str, proposer_id: str,
                       proposal_type: str, threshold: float = 0.6,
                       deadline_hours: int = 24) -> str:
        """Create a new proposal for voting"""
        proposal_id = f"proposal_{int(time.time() * 1000)}"
        deadline = datetime.now() + timedelta(hours=deadline_hours)
        
        proposal = {
            'proposal_id': proposal_id,
            'title': title,
            'description': description,
            'proposer_id': proposer_id,
            'proposal_type': proposal_type,
            'threshold': threshold,
            'created_at': datetime.now(),
            'deadline': deadline,
            'status': 'ACTIVE',
            'metadata': {}
        }
        
        self.active_proposals[proposal_id] = proposal
        self.votes[proposal_id] = []
        
        # Persist to database
        self.db_cursor.execute('''
            INSERT INTO proposals 
            (proposal_id, title, description, proposer_id, proposal_type, threshold, 
             created_at, deadline, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            proposal_id, title, description, proposer_id, proposal_type, threshold,
            proposal['created_at'].isoformat(), deadline.isoformat(), 'ACTIVE',
            json.dumps({})
        ))
        self.db_connection.commit()
        
        logger.info(f"📋 Proposal created: {title} (ID: {proposal_id})")
        
        # Publish to Redis
        if self.redis_available:
            self.redis_client.publish('proposals', json.dumps({
                'action': 'new_proposal',
                'proposal_id': proposal_id,
                'title': title,
                'description': description,
                'proposer_id': proposer_id,
                'deadline': deadline.isoformat(),
                'timestamp': datetime.now().isoformat()
            }))
        
        return proposal_id
    
    def cast_vote(self, proposal_id: str, agent_id: str, vote_type: VoteType, reason: str = ""):
        """Cast a vote on a proposal"""
        if proposal_id not in self.active_proposals:
            logger.error(f"❌ Proposal not found: {proposal_id}")
            return
        
        vote = Vote(
            proposal_id=proposal_id,
            agent_id=agent_id,
            vote_type=vote_type,
            reason=reason,
            timestamp=datetime.now()
        )
        
        self.votes[proposal_id].append(vote)
        
        # Persist to database
        self.db_cursor.execute('''
            INSERT INTO votes (proposal_id, agent_id, vote_type, reason, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (proposal_id, agent_id, vote_type.value, reason, vote.timestamp.isoformat()))
        self.db_connection.commit()
        
        logger.info(f"🗳️ Vote cast: {agent_id} voted {vote_type.value} on {proposal_id}")
        
        # Check if voting is complete
        self.check_proposal_status(proposal_id)
    
    def check_proposal_status(self, proposal_id: str):
        """Check if a proposal has reached a decision"""
        proposal = self.active_proposals.get(proposal_id)
        if not proposal or proposal['status'] != 'ACTIVE':
            return
        
        votes = self.votes.get(proposal_id, [])
        total_agents = len(self.agents)
        
        # Count votes
        approve_count = sum(1 for v in votes if v.vote_type == VoteType.APPROVE)
        reject_count = sum(1 for v in votes if v.vote_type == VoteType.REJECT)
        
        # Check if threshold is met
        threshold = proposal['threshold']
        approval_rate = approve_count / total_agents if total_agents > 0 else 0
        
        if approval_rate >= threshold:
            proposal['status'] = 'APPROVED'
            logger.info(f"✅ Proposal APPROVED: {proposal['title']}")
        elif (reject_count / total_agents) > (1 - threshold):
            proposal['status'] = 'REJECTED'
            logger.info(f"❌ Proposal REJECTED: {proposal['title']}")
        elif datetime.now() > proposal['deadline']:
            proposal['status'] = 'EXPIRED'
            logger.info(f"⏰ Proposal EXPIRED: {proposal['title']}")
        
        # Update database
        if proposal['status'] != 'ACTIVE':
            self.db_cursor.execute('''
                UPDATE proposals SET status = ? WHERE proposal_id = ?
            ''', (proposal['status'], proposal_id))
            self.db_connection.commit()
    
    def get_agent_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report for all agents"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_agents': len(self.agents),
            'agents': []
        }
        
        for agent_id, performance in self.agents.items():
            agent_data = {
                'agent_id': agent_id,
                'tasks_completed': performance.tasks_completed,
                'tasks_failed': performance.tasks_failed,
                'success_rate': round(performance.success_rate, 2),
                'average_completion_time': round(performance.average_completion_time, 2),
                'current_load': performance.current_load,
                'capabilities': performance.capabilities,
                'last_active': performance.last_active.isoformat()
            }
            report['agents'].append(agent_data)
        
        # Sort by success rate
        report['agents'].sort(key=lambda x: x['success_rate'], reverse=True)
        
        return report
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'system_status': self.system_status,
            'godmode_enabled': self.godmode_enabled,
            'total_tasks': len(self.tasks),
            'queued_tasks': sum(1 for t in self.tasks.values() if t.status == TaskStatus.QUEUED),
            'in_progress_tasks': sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS),
            'completed_tasks': sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
            'failed_tasks': sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
            'blocked_tasks': sum(1 for t in self.tasks.values() if t.status == TaskStatus.BLOCKED),
            'active_agents': len(self.agents),
            'active_proposals': len([p for p in self.active_proposals.values() if p['status'] == 'ACTIVE']),
            'redis_available': self.redis_available
        }
        
        return status
    
    async def run_coordination_loop(self):
        """Main coordination loop"""
        logger.info("🎯 Starting coordination loop")
        self.system_status = "ACTIVE"
        
        while True:
            try:
                # Process task queue
                while self.task_queue:
                    task_id = self.task_queue.pop(0)
                    self.assign_task_to_agent(task_id)
                
                # Check proposal statuses
                for proposal_id in list(self.active_proposals.keys()):
                    self.check_proposal_status(proposal_id)
                
                # Update system status
                status = self.get_system_status()
                logger.info(f"📊 System Status: {status['queued_tasks']} queued, "
                          f"{status['in_progress_tasks']} in progress, "
                          f"{status['completed_tasks']} completed")
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in coordination loop: {e}")
                await asyncio.sleep(10)


# Example usage
if __name__ == "__main__":
    pm = EnhancedProjectManagerAI()
    
    # Register some agents
    pm.register_agent("backend-dev-001", ["python", "typescript", "api_development"])
    pm.register_agent("frontend-dev-001", ["react", "typescript", "ui_design"])
    pm.register_agent("database-dev-001", ["sql", "database_design", "optimization"])
    
    # Create some tasks
    task1 = pm.create_task(
        name="Implement User Authentication",
        description="Build JWT-based authentication system",
        priority=TaskPriority.HIGH,
        estimated_duration=120,
        metadata={'required_capabilities': ['python', 'api_development']}
    )
    
    task2 = pm.create_task(
        name="Design Login UI",
        description="Create responsive login page",
        priority=TaskPriority.MEDIUM,
        dependencies=[task1.id],
        estimated_duration=90,
        metadata={'required_capabilities': ['react', 'ui_design']}
    )
    
    # Assign tasks
    pm.assign_task_to_agent(task1.id)
    
    # Create a proposal
    proposal_id = pm.create_proposal(
        title="Migrate to PostgreSQL",
        description="Migrate from SQLite to PostgreSQL for better scalability",
        proposer_id="backend-dev-001",
        proposal_type="architecture_change",
        threshold=0.75
    )
    
    # Cast votes
    pm.cast_vote(proposal_id, "backend-dev-001", VoteType.APPROVE, "Better performance")
    pm.cast_vote(proposal_id, "frontend-dev-001", VoteType.APPROVE, "Agree with backend")
    pm.cast_vote(proposal_id, "database-dev-001", VoteType.APPROVE, "This is my expertise")
    
    # Generate reports
    performance_report = pm.get_agent_performance_report()
    print(json.dumps(performance_report, indent=2))
    
    system_status = pm.get_system_status()
    print(json.dumps(system_status, indent=2))
    
    logger.info("✅ Enhanced Project Manager AI demonstration complete")
