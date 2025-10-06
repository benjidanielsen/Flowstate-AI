#!/usr/bin/env python3
"""
🤖 PROJECT MANAGER AI v2.0 - Fully Refactored and Optimized
⚡ GODMODE: Unlimited autonomous development authority
🎯 Mission: Orchestrate AI agent ecosystem with maximum efficiency and resilience
🧠 Capabilities: Async operations, advanced error handling, intelligent task management
"""

import asyncio
import json
import logging
import os
import sqlite3
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import aioredis
from aiosqlite import connect as aio_connect

from ai_gods.logging_config import setup_logging

# Configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
DB_PATH = os.getenv("PM_DB_PATH", "godmode-state.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Setup logging
logger = setup_logging("PM-v2", "project-manager-v2.log")


class TaskStatus(Enum):
    """Task status enumeration"""

    QUEUED = "QUEUED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


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


class AgentStatus(Enum):
    """Agent status enumeration"""

    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    BUSY = "BUSY"
    ERROR = "ERROR"
    OFFLINE = "OFFLINE"


@dataclass
class Task:
    """Task data structure"""

    id: str
    name: str
    description: str
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.QUEUED
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: int = 60  # in minutes
    actual_duration: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class AgentPerformance:
    """Agent performance metrics"""

    agent_id: str
    status: AgentStatus = AgentStatus.IDLE
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_completion_time: float = 0.0
    success_rate: float = 100.0
    current_load: int = 0
    max_load: int = 3
    capabilities: List[str] = field(default_factory=list)
    last_active: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)


@dataclass
class Vote:
    """Vote data structure"""

    proposal_id: str
    agent_id: str
    vote_type: VoteType
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Proposal:
    """Proposal data structure"""

    proposal_id: str
    title: str
    description: str
    proposer_id: str
    proposal_type: str
    threshold: float = 0.6
    created_at: datetime = field(default_factory=datetime.now)
    deadline: datetime = field(
        default_factory=lambda: datetime.now() + timedelta(hours=24)
    )
    status: str = "ACTIVE"
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProjectManagerV2:
    """
    Project Manager AI v2.0 - Fully refactored with async operations and enhanced features
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.db_path = self.project_root / DB_PATH

        # Redis connection (async)
        self.redis: Optional[aioredis.Redis] = None
        self.redis_available = False

        # Database connection (async)
        self.db: Optional[Any] = None

        # In-memory state
        self.agents: Dict[str, AgentPerformance] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_priority_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.active_proposals: Dict[str, Proposal] = {}
        self.votes: Dict[str, List[Vote]] = defaultdict(list)

        # Dependency graph for task management
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)

        # System state
        self.godmode_enabled = True
        self.system_status = "INITIALIZING"
        self.running = False

        # Heartbeat monitoring
        self.heartbeat_task: Optional[asyncio.Task] = None

        logger.info("🚀 PROJECT MANAGER AI v2.0 INITIALIZED")

    async def initialize(self):
        """Initialize all connections and load state"""
        try:
            # Initialize Redis
            await self._init_redis()

            # Initialize Database
            await self._init_database()

            # Load existing state from database
            await self._load_state()

            # Start background tasks
            self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())

            # Create recurring tasks
            await self._create_recurring_tasks()

            self.system_status = "READY"
            logger.info("✅ Project Manager v2.0 fully initialized and ready")

        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            self.system_status = "ERROR"
            raise

    async def _init_redis(self):
        """Initialize Redis connection with retry logic"""
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                self.redis = await aioredis.create_redis_pool(
                    f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf-8"
                )
                await self.redis.ping()
                self.redis_available = True
                logger.info(f"✅ Redis connection established (attempt {attempt + 1})")
                return
            except Exception as e:
                logger.warning(f"⚠️ Redis connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    logger.warning("⚠️ Redis not available. Operating in fallback mode.")
                    self.redis_available = False

    async def _init_database(self):
        """Initialize SQLite database with async support"""
        self.db = await aio_connect(str(self.db_path))

        # Create tables
        await self.db.execute(
            """
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
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                metadata TEXT
            )
        """
        )

        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                status TEXT DEFAULT 'IDLE',
                tasks_completed INTEGER DEFAULT 0,
                tasks_failed INTEGER DEFAULT 0,
                average_completion_time REAL DEFAULT 0.0,
                success_rate REAL DEFAULT 100.0,
                current_load INTEGER DEFAULT 0,
                max_load INTEGER DEFAULT 3,
                capabilities TEXT,
                last_active TEXT,
                last_heartbeat TEXT
            )
        """
        )

        await self.db.execute(
            """
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
        """
        )

        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                vote_type TEXT NOT NULL,
                reason TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (proposal_id) REFERENCES proposals (proposal_id)
            )
        """
        )

        await self.db.commit()
        logger.info("📊 Database initialized successfully")

    async def _load_state(self):
        """Load existing state from database"""
        try:
            # Load agents
            async with self.db.execute("SELECT * FROM agents") as cursor:
                async for row in cursor:
                    agent_id = row[0]
                    self.agents[agent_id] = AgentPerformance(
                        agent_id=agent_id,
                        status=AgentStatus(row[1]),
                        tasks_completed=row[2],
                        tasks_failed=row[3],
                        average_completion_time=row[4],
                        success_rate=row[5],
                        current_load=row[6],
                        max_load=row[7],
                        capabilities=json.loads(row[8]) if row[8] else [],
                        last_active=(
                            datetime.fromisoformat(row[9]) if row[9] else datetime.now()
                        ),
                        last_heartbeat=(
                            datetime.fromisoformat(row[10])
                            if row[10]
                            else datetime.now()
                        ),
                    )

            # Load tasks
            async with self.db.execute(
                'SELECT * FROM tasks WHERE status NOT IN ("COMPLETED", "FAILED", "CANCELLED")'
            ) as cursor:
                async for row in cursor:
                    task_id = row[0]
                    task = Task(
                        id=task_id,
                        name=row[1],
                        description=row[2],
                        assigned_to=row[3],
                        status=TaskStatus(row[4]),
                        priority=TaskPriority(row[5]),
                        dependencies=json.loads(row[6]) if row[6] else [],
                        created_at=datetime.fromisoformat(row[7]),
                        started_at=datetime.fromisoformat(row[8]) if row[8] else None,
                        completed_at=datetime.fromisoformat(row[9]) if row[9] else None,
                        estimated_duration=row[10],
                        actual_duration=row[11],
                        retry_count=row[12],
                        max_retries=row[13],
                        metadata=json.loads(row[14]) if row[14] else {},
                    )
                    self.tasks[task_id] = task

                    # Build dependency graph
                    for dep_id in task.dependencies:
                        self.dependency_graph[task_id].add(dep_id)

                    # Add to priority queue if queued
                    if task.status == TaskStatus.QUEUED:
                        await self.task_priority_queue.put(
                            (task.priority.value, task_id)
                        )

            logger.info(
                f"✅ Loaded {len(self.agents)} agents and {len(self.tasks)} active tasks from database"
            )

        except Exception as e:
            logger.error(f"❌ Error loading state: {e}")

    async def register_agent(
        self, agent_id: str, capabilities: List[str], max_load: int = 3
    ):
        """Register a new agent in the system"""
        try:
            performance = AgentPerformance(
                agent_id=agent_id,
                status=AgentStatus.IDLE,
                capabilities=capabilities,
                max_load=max_load,
                last_active=datetime.now(),
                last_heartbeat=datetime.now(),
            )

            self.agents[agent_id] = performance

            # Persist to database
            await self.db.execute(
                """
                INSERT OR REPLACE INTO agents 
                (agent_id, status, capabilities, max_load, last_active, last_heartbeat)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    agent_id,
                    performance.status.value,
                    json.dumps(capabilities),
                    max_load,
                    performance.last_active.isoformat(),
                    performance.last_heartbeat.isoformat(),
                ),
            )
            await self.db.commit()

            logger.info(
                f"✅ Agent registered: {agent_id} with capabilities {capabilities}"
            )

            # Publish to Redis
            if self.redis_available:
                await self.redis.publish(
                    "agent_registry",
                    json.dumps(
                        {
                            "action": "register",
                            "agent_id": agent_id,
                            "capabilities": capabilities,
                            "timestamp": datetime.now().isoformat(),
                        }
                    ),
                )

            return True

        except Exception as e:
            logger.error(f"❌ Error registering agent {agent_id}: {e}")
            return False

    async def update_agent_heartbeat(self, agent_id: str):
        """Update agent heartbeat timestamp"""
        if agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = datetime.now()
            self.agents[agent_id].last_active = datetime.now()

            # Update database
            await self.db.execute(
                """
                UPDATE agents 
                SET last_heartbeat = ?, last_active = ?
                WHERE agent_id = ?
            """,
                (datetime.now().isoformat(), datetime.now().isoformat(), agent_id),
            )
            await self.db.commit()

    async def _heartbeat_monitor(self):
        """Monitor agent heartbeats and mark inactive agents as offline"""
        while self.running:
            try:
                current_time = datetime.now()
                timeout_threshold = timedelta(minutes=5)

                for agent_id, performance in self.agents.items():
                    time_since_heartbeat = current_time - performance.last_heartbeat

                    if time_since_heartbeat > timeout_threshold:
                        if performance.status != AgentStatus.OFFLINE:
                            logger.warning(
                                f"⚠️ Agent {agent_id} heartbeat timeout. Marking as OFFLINE."
                            )
                            performance.status = AgentStatus.OFFLINE

                            # Reassign tasks from offline agent
                            await self._reassign_agent_tasks(agent_id)

                            # Update database
                            await self.db.execute(
                                """
                                UPDATE agents 
                                SET status = ?
                                WHERE agent_id = ?
                            """,
                                (AgentStatus.OFFLINE.value, agent_id),
                            )
                            await self.db.commit()

                # Sleep for 30 seconds before next check
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"❌ Error in heartbeat monitor: {e}")
                await asyncio.sleep(30)

    async def _reassign_agent_tasks(self, agent_id: str):
        """Reassign tasks from an offline agent"""
        tasks_to_reassign = [
            task_id
            for task_id, task in self.tasks.items()
            if task.assigned_to == agent_id
            and task.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
        ]

        for task_id in tasks_to_reassign:
            task = self.tasks[task_id]
            task.assigned_to = None
            task.status = TaskStatus.QUEUED

            # Add back to priority queue
            await self.task_priority_queue.put((task.priority.value, task_id))

            logger.info(f"🔄 Task {task.name} reassigned from offline agent {agent_id}")

    async def create_task(
        self,
        name: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: List[str] = None,
        estimated_duration: int = 60,
        metadata: Dict[str, Any] = None,
    ) -> Optional[Task]:
        """Create a new task"""
        try:
            task_id = f"task_{int(time.time() * 1000)}"
            task = Task(
                id=task_id,
                name=name,
                description=description,
                priority=priority,
                dependencies=dependencies or [],
                estimated_duration=estimated_duration,
                metadata=metadata or {},
            )

            self.tasks[task_id] = task

            # Build dependency graph
            for dep_id in task.dependencies:
                self.dependency_graph[task_id].add(dep_id)

            # Check for circular dependencies
            if await self._has_circular_dependency(task_id):
                logger.error(f"❌ Circular dependency detected for task {name}")
                del self.tasks[task_id]
                return None

            # Add to priority queue if no dependencies or dependencies are met
            if await self._are_dependencies_met(task):
                await self.task_priority_queue.put((task.priority.value, task_id))
            else:
                task.status = TaskStatus.BLOCKED

            # Persist to database
            await self.db.execute(
                """
                INSERT INTO tasks 
                (id, name, description, status, priority, dependencies, created_at, estimated_duration, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task_id,
                    name,
                    description,
                    task.status.value,
                    task.priority.value,
                    json.dumps(dependencies or []),
                    task.created_at.isoformat(),
                    estimated_duration,
                    json.dumps(metadata or {}),
                ),
            )
            await self.db.commit()

            logger.info(
                f"📝 Task created: {name} (ID: {task_id}, Priority: {priority.name})"
            )

            return task

        except Exception as e:
            logger.error(f"❌ Error creating task: {e}")
            return None

    async def _has_circular_dependency(
        self, task_id: str, visited: Set[str] = None
    ) -> bool:
        """Check for circular dependencies using DFS"""
        if visited is None:
            visited = set()

        if task_id in visited:
            return True

        visited.add(task_id)

        for dep_id in self.dependency_graph.get(task_id, []):
            if await self._has_circular_dependency(dep_id, visited.copy()):
                return True

        return False

    async def _are_dependencies_met(self, task: Task) -> bool:
        """Check if all task dependencies are completed"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    async def assign_next_task(self) -> Optional[Tuple[str, str]]:
        """Assign the next task from the priority queue to the best available agent"""
        try:
            if self.task_priority_queue.empty():
                return None

            # Get next task from priority queue
            priority, task_id = await self.task_priority_queue.get()
            task = self.tasks.get(task_id)

            if not task:
                logger.warning(f"⚠️ Task {task_id} not found in task registry")
                return None

            # Find the best agent for this task
            best_agent = await self._find_best_agent_for_task(task)

            if not best_agent:
                # No agent available, put task back in queue
                await self.task_priority_queue.put((priority, task_id))
                return None

            # Assign the task
            task.assigned_to = best_agent
            task.status = TaskStatus.ASSIGNED
            task.started_at = datetime.now()

            # Update agent load and status
            self.agents[best_agent].current_load += 1
            if self.agents[best_agent].current_load >= self.agents[best_agent].max_load:
                self.agents[best_agent].status = AgentStatus.BUSY
            else:
                self.agents[best_agent].status = AgentStatus.ACTIVE

            # Update database
            await self.db.execute(
                """
                UPDATE tasks 
                SET assigned_to = ?, status = ?, started_at = ?
                WHERE id = ?
            """,
                (best_agent, task.status.value, task.started_at.isoformat(), task_id),
            )

            await self.db.execute(
                """
                UPDATE agents 
                SET current_load = ?, status = ?
                WHERE agent_id = ?
            """,
                (
                    self.agents[best_agent].current_load,
                    self.agents[best_agent].status.value,
                    best_agent,
                ),
            )

            await self.db.commit()

            logger.info(f"✅ Task {task.name} assigned to {best_agent}")

            # Publish to Redis
            if self.redis_available:
                await self.redis.publish(
                    "task_assignments",
                    json.dumps(
                        {
                            "task_id": task_id,
                            "task_name": task.name,
                            "assigned_to": best_agent,
                            "timestamp": datetime.now().isoformat(),
                        }
                    ),
                )

            return (task_id, best_agent)

        except Exception as e:
            logger.error(f"❌ Error assigning task: {e}")
            return None

    async def _find_best_agent_for_task(self, task: Task) -> Optional[str]:
        """Find the best agent for a task based on capabilities, load, and performance"""
        required_capabilities = task.metadata.get("required_capabilities", [])

        # Score each agent
        agent_scores = []
        for agent_id, performance in self.agents.items():
            # Skip offline or busy agents
            if performance.status in [AgentStatus.OFFLINE, AgentStatus.ERROR]:
                continue

            if performance.current_load >= performance.max_load:
                continue

            # Check if agent has required capabilities
            if required_capabilities:
                if not all(
                    cap in performance.capabilities for cap in required_capabilities
                ):
                    continue

            # Calculate score based on multiple factors
            load_score = 1.0 - (performance.current_load / performance.max_load)
            success_score = performance.success_rate / 100.0
            speed_score = 1.0 / (performance.average_completion_time + 1)

            # Weighted scoring
            total_score = (
                (load_score * 0.4) + (success_score * 0.4) + (speed_score * 0.2)
            )

            agent_scores.append((agent_id, total_score))

        if not agent_scores:
            return None

        # Sort by score and return the best agent
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        return agent_scores[0][0]

    async def complete_task(self, task_id: str, success: bool = True):
        """Mark a task as completed"""
        try:
            task = self.tasks.get(task_id)
            if not task:
                logger.error(f"❌ Task not found: {task_id}")
                return False

            task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            task.completed_at = datetime.now()

            if task.started_at:
                task.actual_duration = int(
                    (task.completed_at - task.started_at).total_seconds() / 60
                )

            # Update agent performance
            if task.assigned_to and task.assigned_to in self.agents:
                agent = self.agents[task.assigned_to]
                agent.current_load = max(0, agent.current_load - 1)

                if success:
                    agent.tasks_completed += 1
                else:
                    agent.tasks_failed += 1

                # Update average completion time
                total_tasks = agent.tasks_completed + agent.tasks_failed
                if task.actual_duration:
                    agent.average_completion_time = (
                        agent.average_completion_time * (total_tasks - 1)
                        + task.actual_duration
                    ) / total_tasks

                # Update success rate
                agent.success_rate = (
                    (agent.tasks_completed / total_tasks) * 100
                    if total_tasks > 0
                    else 100.0
                )

                # Update agent status
                if agent.current_load == 0:
                    agent.status = AgentStatus.IDLE
                elif agent.current_load < agent.max_load:
                    agent.status = AgentStatus.ACTIVE

                # Update database
                await self.db.execute(
                    """
                    UPDATE agents 
                    SET tasks_completed = ?, tasks_failed = ?, average_completion_time = ?, 
                        success_rate = ?, current_load = ?, status = ?
                    WHERE agent_id = ?
                """,
                    (
                        agent.tasks_completed,
                        agent.tasks_failed,
                        agent.average_completion_time,
                        agent.success_rate,
                        agent.current_load,
                        agent.status.value,
                        task.assigned_to,
                    ),
                )

            # Update task in database
            await self.db.execute(
                """
                UPDATE tasks 
                SET status = ?, completed_at = ?, actual_duration = ?
                WHERE id = ?
            """,
                (
                    task.status.value,
                    task.completed_at.isoformat(),
                    task.actual_duration,
                    task_id,
                ),
            )
            await self.db.commit()

            logger.info(
                f"✅ Task completed: {task.name} (Duration: {task.actual_duration} min, Success: {success})"
            )

            # Check for unblocked tasks
            await self._check_unblocked_tasks()

            return True

        except Exception as e:
            logger.error(f"❌ Error completing task: {e}")
            return False

    async def _check_unblocked_tasks(self):
        """Check for tasks that can now be unblocked"""
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.BLOCKED and await self._are_dependencies_met(
                task
            ):
                task.status = TaskStatus.QUEUED
                await self.task_priority_queue.put((task.priority.value, task_id))
                logger.info(f"🔓 Task unblocked: {task.name}")

                # Update database
                await self.db.execute(
                    """
                    UPDATE tasks 
                    SET status = ?
                    WHERE id = ?
                """,
                    (TaskStatus.QUEUED.value, task_id),
                )
                await self.db.commit()

    async def run(self):
        """Main run loop for the Project Manager"""
        self.running = True
        logger.info("🚀 Project Manager v2.0 starting main loop...")

        try:
            while self.running:
                # Assign tasks from the queue
                result = await self.assign_next_task()

                if result:
                    task_id, agent_id = result
                    logger.info(f"📋 Assigned task {task_id} to agent {agent_id}")

                # Check for recurring tasks
                await self._check_recurring_tasks()

                # Sleep briefly to avoid tight loop
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Gracefully shutdown the Project Manager"""
        logger.info("🛑 Shutting down Project Manager v2.0...")
        self.running = False

        # Cancel heartbeat task
        if self.heartbeat_task:
            self.heartbeat_task.cancel()

        # Close Redis connection
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()

        # Close database connection
        if self.db:
            await self.db.close()

        logger.info("✅ Project Manager v2.0 shutdown complete")

    async def _create_recurring_tasks(self):
        """Create recurring tasks if they don't exist"""
        # Auto-publish task
        auto_publish_task_name = "Auto-publish to GitHub"
        if not any(task.name == auto_publish_task_name for task in self.tasks.values()):
            await self.create_task(
                name=auto_publish_task_name,
                description="Automatically publish changes to the GitHub repository.",
                priority=TaskPriority.LOW,
                metadata={
                    "required_capabilities": ["git_operations"],
                    "recurring": True,
                    "interval_hours": 1,
                },
            )

    async def _check_recurring_tasks(self):
        """Check and re-queue recurring tasks"""
        for task in self.tasks.values():
            if task.metadata.get("recurring") and task.status == TaskStatus.COMPLETED:
                interval_hours = task.metadata.get("interval_hours", 1)
                if task.completed_at and datetime.now() - task.completed_at > timedelta(
                    hours=interval_hours
                ):
                    task.status = TaskStatus.QUEUED
                    task.completed_at = None
                    await self.task_priority_queue.put((task.priority.value, task.id))
                    logger.info(f"🔄 Re-queued recurring task: {task.name}")


# Main entry point
async def main():
    pm = ProjectManagerV2()
    await pm.initialize()
    await pm.run()


if __name__ == "__main__":
    asyncio.run(main())
