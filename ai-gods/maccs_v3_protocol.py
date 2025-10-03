#!/usr/bin/env python3
"""
🌐 MACCS v3.0 - Multi-Agent Coordination and Communication System
⚡ GODMODE: Advanced inter-agent communication and coordination
🎯 Mission: Enable seamless collaboration between AI agents with zero latency
🚀 Features: Event-driven messaging, heartbeat monitoring, task delegation, conflict resolution
"""

import asyncio
import sys
import json
import logging
import platform
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Callable
import aiosqlite

# Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
DB_PATH = os.getenv('MACCS_DB_PATH', 'maccs-v3.db')
HEARTBEAT_INTERVAL = int(os.getenv('HEARTBEAT_INTERVAL', 30))  # seconds
HEARTBEAT_TIMEOUT = int(os.getenv('HEARTBEAT_TIMEOUT', 300))  # 5 minutes

# Setup logging

# Ensure UTF-8 encoding for stdout on Windows to support emoji logging
if platform.system() == 'Windows':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='🌐 [MACCS-v3] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/maccs-v3.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent status types"""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class MessageType(Enum):
    """Message types"""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_UPDATE = "task_update"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    QUERY = "query"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    HEARTBEAT = "heartbeat"
    VOTE_REQUEST = "vote_request"
    VOTE_RESPONSE = "vote_response"
    KNOWLEDGE_SHARE = "knowledge_share"
    ERROR_REPORT = "error_report"
    FIX_REQUEST = "fix_request"


@dataclass
class Agent:
    """Agent data structure"""
    agent_id: str
    name: str
    role: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Message data structure"""
    message_id: str
    from_agent: str
    to_agent: Optional[str]  # None for broadcast
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False


@dataclass
class Task:
    """Task data structure"""
    task_id: str
    name: str
    description: str
    assigned_to: Optional[str] = None
    status: str = "QUEUED"
    priority: str = "MEDIUM"
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MACCSv3:
    """
    Multi-Agent Coordination and Communication System v3.0
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.db_path = self.project_root / DB_PATH
        
        # Database connection
        self.db: Optional[aiosqlite.Connection] = None
        
        # In-memory state
        self.agents: Dict[str, Agent] = {}
        self.message_queue: List[Message] = []
        self.tasks: Dict[str, Task] = {}
        
        # Event handlers
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        
        # Running state
        self.running = False
        
        logger.info("🚀 MACCS v3.0 INITIALIZED")
    
    async def initialize(self):
        """Initialize MACCS v3.0"""
        try:
            # Initialize database
            await self._init_database()
            
            # Load agents
            await self._load_agents()
            
            # Load tasks
            await self._load_tasks()
            
            # Load pending messages
            await self._load_pending_messages()
            
            logger.info("✅ MACCS v3.0 initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def _init_database(self):
        """Initialize SQLite database"""
        self.db = await aiosqlite.connect(str(self.db_path))
        
        # Agents table
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL,
                current_task TEXT,
                capabilities TEXT,
                last_heartbeat TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        # Messages table
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                from_agent TEXT NOT NULL,
                to_agent TEXT,
                message_type TEXT NOT NULL,
                priority INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                processed INTEGER DEFAULT 0
            )
        ''')
        
        # Tasks table
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                assigned_to TEXT,
                status TEXT DEFAULT 'QUEUED',
                priority TEXT DEFAULT 'MEDIUM',
                dependencies TEXT,
                created_at TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        # Create indices for performance
        await self.db.execute('CREATE INDEX IF NOT EXISTS idx_messages_to_agent ON messages(to_agent, processed)')
        await self.db.execute('CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to, status)')
        
        await self.db.commit()
        logger.info("📊 MACCS database initialized")
    
    async def _load_agents(self):
        """Load registered agents"""
        try:
            async with self.db.execute('SELECT * FROM agents') as cursor:
                async for row in cursor:
                    agent = Agent(
                        agent_id=row[0],
                        name=row[1],
                        role=row[2],
                        status=AgentStatus(row[3]),
                        current_task=row[4],
                        capabilities=json.loads(row[5]) if row[5] else [],
                        last_heartbeat=datetime.fromisoformat(row[6]),
                        metadata=json.loads(row[7]) if row[7] else {}
                    )
                    self.agents[agent.agent_id] = agent
            
            logger.info(f"✅ Loaded {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"❌ Error loading agents: {e}")
    
    async def _load_tasks(self):
        """Load tasks"""
        try:
            async with self.db.execute('SELECT * FROM tasks') as cursor:
                async for row in cursor:
                    task = Task(
                        task_id=row[0],
                        name=row[1],
                        description=row[2],
                        assigned_to=row[3],
                        status=row[4],
                        priority=row[5],
                        dependencies=json.loads(row[6]) if row[6] else [],
                        created_at=datetime.fromisoformat(row[7]),
                        metadata=json.loads(row[8]) if row[8] else {}
                    )
                    self.tasks[task.task_id] = task
            
            logger.info(f"✅ Loaded {len(self.tasks)} tasks")
            
        except Exception as e:
            logger.error(f"❌ Error loading tasks: {e}")
    
    async def _load_pending_messages(self):
        """Load pending messages"""
        try:
            async with self.db.execute('SELECT * FROM messages WHERE processed = 0 ORDER BY priority DESC, timestamp ASC') as cursor:
                async for row in cursor:
                    message = Message(
                        message_id=row[0],
                        from_agent=row[1],
                        to_agent=row[2],
                        message_type=MessageType(row[3]),
                        priority=MessagePriority(row[4]),
                        content=json.loads(row[5]),
                        timestamp=datetime.fromisoformat(row[6]),
                        processed=bool(row[7])
                    )
                    self.message_queue.append(message)
            
            logger.info(f"✅ Loaded {len(self.message_queue)} pending messages")
            
        except Exception as e:
            logger.error(f"❌ Error loading messages: {e}")
    
    async def register_agent(
        self,
        agent_id: str,
        name: str,
        role: str,
        capabilities: List[str] = None
    ) -> bool:
        """Register a new agent"""
        try:
            if agent_id in self.agents:
                logger.warning(f"⚠️ Agent {agent_id} already registered")
                return False
            
            agent = Agent(
                agent_id=agent_id,
                name=name,
                role=role,
                capabilities=capabilities or []
            )
            
            self.agents[agent_id] = agent
            
            # Persist to database
            await self.db.execute('''
                INSERT INTO agents (agent_id, name, role, status, capabilities, last_heartbeat, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_id, name, role, agent.status.value,
                json.dumps(agent.capabilities), agent.last_heartbeat.isoformat(),
                json.dumps(agent.metadata)
            ))
            await self.db.commit()
            
            logger.info(f"✅ Agent registered: {name} ({agent_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registering agent: {e}")
            return False
    
    async def update_agent_status(
        self,
        agent_id: str,
        status: AgentStatus,
        current_task: Optional[str] = None
    ):
        """Update agent status"""
        try:
            if agent_id not in self.agents:
                logger.warning(f"⚠️ Unknown agent: {agent_id}")
                return
            
            agent = self.agents[agent_id]
            agent.status = status
            agent.current_task = current_task
            agent.last_heartbeat = datetime.now()
            
            # Persist to database
            await self.db.execute('''
                UPDATE agents 
                SET status = ?, current_task = ?, last_heartbeat = ?
                WHERE agent_id = ?
            ''', (status.value, current_task, agent.last_heartbeat.isoformat(), agent_id))
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ Error updating agent status: {e}")
    
    async def send_message(
        self,
        from_agent: str,
        to_agent: Optional[str],
        message_type: MessageType,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """Send a message to another agent or broadcast"""
        try:
            message_id = f"msg_{int(datetime.now().timestamp() * 1000)}"
            
            message = Message(
                message_id=message_id,
                from_agent=from_agent,
                to_agent=to_agent,
                message_type=message_type,
                priority=priority,
                content=content
            )
            
            self.message_queue.append(message)
            
            # Persist to database
            await self.db.execute('''
                INSERT INTO messages (message_id, from_agent, to_agent, message_type, priority, content, timestamp, processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_id, from_agent, to_agent, message_type.value,
                priority.value, json.dumps(content), message.timestamp.isoformat(), 0
            ))
            await self.db.commit()
            
            logger.info(f"📨 Message sent: {from_agent} → {to_agent or 'ALL'} ({message_type.value})")
            return message_id
            
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return ""
    
    async def get_messages(self, agent_id: str) -> List[Message]:
        """Get messages for a specific agent"""
        messages = []
        
        for message in self.message_queue:
            if not message.processed:
                # Check if message is for this agent or broadcast
                if message.to_agent == agent_id or message.to_agent is None:
                    messages.append(message)
        
        # Sort by priority and timestamp
        messages.sort(key=lambda m: (m.priority.value, m.timestamp), reverse=True)
        
        return messages
    
    async def mark_message_processed(self, message_id: str):
        """Mark a message as processed"""
        try:
            # Update in-memory
            for message in self.message_queue:
                if message.message_id == message_id:
                    message.processed = True
                    break
            
            # Update database
            await self.db.execute('''
                UPDATE messages SET processed = 1 WHERE message_id = ?
            ''', (message_id,))
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ Error marking message processed: {e}")
    
    async def create_task(
        self,
        name: str,
        description: str,
        priority: str = "MEDIUM",
        dependencies: List[str] = None
    ) -> str:
        """Create a new task"""
        try:
            task_id = f"task_{int(datetime.now().timestamp() * 1000)}"
            
            task = Task(
                task_id=task_id,
                name=name,
                description=description,
                priority=priority,
                dependencies=dependencies or []
            )
            
            self.tasks[task_id] = task
            
            # Persist to database
            await self.db.execute('''
                INSERT INTO tasks (task_id, name, description, priority, dependencies, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_id, name, description, priority,
                json.dumps(task.dependencies), task.created_at.isoformat(),
                json.dumps(task.metadata)
            ))
            await self.db.commit()
            
            logger.info(f"✅ Task created: {name} ({task_id})")
            return task_id
            
        except Exception as e:
            logger.error(f"❌ Error creating task: {e}")
            return ""
    
    async def assign_task(self, task_id: str, agent_id: str):
        """Assign a task to an agent"""
        try:
            if task_id not in self.tasks:
                logger.warning(f"⚠️ Unknown task: {task_id}")
                return
            
            if agent_id not in self.agents:
                logger.warning(f"⚠️ Unknown agent: {agent_id}")
                return
            
            task = self.tasks[task_id]
            task.assigned_to = agent_id
            task.status = "ASSIGNED"
            
            # Update database
            await self.db.execute('''
                UPDATE tasks SET assigned_to = ?, status = ? WHERE task_id = ?
            ''', (agent_id, "ASSIGNED", task_id))
            await self.db.commit()
            
            # Send task assignment message
            await self.send_message(
                from_agent="MACCS",
                to_agent=agent_id,
                message_type=MessageType.TASK_ASSIGNMENT,
                content={
                    'task_id': task_id,
                    'name': task.name,
                    'description': task.description,
                    'priority': task.priority
                },
                priority=MessagePriority.HIGH
            )
            
            logger.info(f"✅ Task assigned: {task_id} → {agent_id}")
            
        except Exception as e:
            logger.error(f"❌ Error assigning task: {e}")
    
    async def heartbeat_monitor(self):
        """Monitor agent heartbeats"""
        while self.running:
            try:
                now = datetime.now()
                timeout_threshold = now - timedelta(seconds=HEARTBEAT_TIMEOUT)
                
                for agent_id, agent in self.agents.items():
                    if agent.last_heartbeat < timeout_threshold:
                        if agent.status != AgentStatus.OFFLINE:
                            logger.warning(f"⚠️ Agent {agent_id} heartbeat timeout")
                            await self.update_agent_status(agent_id, AgentStatus.OFFLINE)
                            
                            # Reassign tasks if any
                            if agent.current_task:
                                await self._reassign_task(agent.current_task)
                
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                
            except Exception as e:
                logger.error(f"❌ Error in heartbeat monitor: {e}")
                await asyncio.sleep(HEARTBEAT_INTERVAL)
    
    async def _reassign_task(self, task_id: str):
        """Reassign a task to another available agent"""
        try:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            
            # Find available agent
            available_agents = [
                agent for agent in self.agents.values()
                if agent.status == AgentStatus.IDLE
            ]
            
            if available_agents:
                new_agent = available_agents[0]
                logger.info(f"🔄 Reassigning task {task_id} to {new_agent.agent_id}")
                await self.assign_task(task_id, new_agent.agent_id)
            else:
                logger.warning(f"⚠️ No available agents to reassign task {task_id}")
                task.status = "QUEUED"
                task.assigned_to = None
                
                await self.db.execute('''
                    UPDATE tasks SET status = ?, assigned_to = ? WHERE task_id = ?
                ''', ("QUEUED", None, task_id))
                await self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ Error reassigning task: {e}")
    
    async def run(self):
        """Main MACCS coordination loop"""
        self.running = True
        logger.info("🌐 MACCS v3.0 running...")
        
        # Start heartbeat monitor
        heartbeat_task = asyncio.create_task(self.heartbeat_monitor())
        
        try:
            while self.running:
                # Process messages
                # (Message processing would be handled by individual agents)
                
                await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
        finally:
            heartbeat_task.cancel()
            logger.info("🛑 MACCS v3.0 stopped")
    
    async def shutdown(self):
        """Gracefully shutdown"""
        logger.info("🛑 Shutting down MACCS v3.0...")
        self.running = False
        
        if self.db:
            await self.db.close()
        
        logger.info("✅ Shutdown complete")


# Main entry point
async def main():
    project_root = Path(__file__).parent.parent
    maccs = MACCSv3(project_root)
    await maccs.initialize()
    await maccs.run()


if __name__ == '__main__':
    asyncio.run(main())
