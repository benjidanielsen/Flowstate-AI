#!/usr/bin/env python3
"""
🧠 AI COMMUNICATION HUB v2.0 - Fully Refactored and Optimized
⚡ GODMODE: Advanced inter-agent communication and collaboration
🎯 Mission: Enable seamless AI-to-AI interaction, knowledge sharing, and coordination
🚀 Features: Async operations, enhanced error handling, intelligent routing
"""

import asyncio
import sys
import json
import logging
import platform
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

import aioredis
from aiosqlite import connect as aio_connect

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
DB_PATH = os.getenv('COMM_DB_PATH', 'godmode-communication.db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Setup logging

# Ensure UTF-8 encoding for stdout on Windows to support emoji logging
if platform.system() == 'Windows':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='🧠 [COMM-v2] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/communication-hub-v2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages"""
    TASK_REQUEST = "TASK_REQUEST"
    TASK_RESPONSE = "TASK_RESPONSE"
    QUESTION = "QUESTION"
    ANSWER = "ANSWER"
    KNOWLEDGE_SHARE = "KNOWLEDGE_SHARE"
    STATUS_UPDATE = "STATUS_UPDATE"
    ALERT = "ALERT"
    PROPOSAL = "PROPOSAL"
    VOTE = "VOTE"
    COMMAND = "COMMAND"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Message:
    """Message data structure"""
    id: str
    from_agent: str
    to_agent: str  # Can be "broadcast" for all agents
    message_type: MessageType
    priority: MessagePriority
    subject: str
    body: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    requires_response: bool = False
    thread_id: Optional[str] = None
    response_id: Optional[str] = None
    read: bool = False


@dataclass
class KnowledgeEntry:
    """Knowledge base entry"""
    id: int
    topic: str
    content: str
    contributor: str
    tags: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    upvotes: int = 0
    downvotes: int = 0


@dataclass
class AgentExpertise:
    """Agent expertise profile"""
    agent_id: str
    expertise_areas: List[str] = field(default_factory=list)
    knowledge_contributions: int = 0
    questions_answered: int = 0
    last_active: datetime = field(default_factory=datetime.now)


class CommunicationHubV2:
    """
    Communication Hub v2.0 - Fully refactored with async operations
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.db_path = self.project_root / DB_PATH
        
        # Redis connection (async)
        self.redis: Optional[aioredis.Redis] = None
        self.redis_available = False
        self.pubsub_channels: Dict[str, aioredis.Channel] = {}
        
        # Database connection (async)
        self.db: Optional[Any] = None
        
        # In-memory state
        self.agents_expertise: Dict[str, AgentExpertise] = {}
        self.message_threads: Dict[str, List[str]] = defaultdict(list)
        self.pending_responses: Dict[str, Message] = {}
        
        # Running state
        self.running = False
        self.message_listener_task: Optional[asyncio.Task] = None
        
        logger.info("🚀 COMMUNICATION HUB v2.0 INITIALIZED")
    
    async def initialize(self):
        """Initialize all connections and load state"""
        try:
            # Initialize Redis
            await self._init_redis()
            
            # Initialize Database
            await self._init_database()
            
            # Load existing state
            await self._load_state()
            
            # Start message listener
            if self.redis_available:
                self.message_listener_task = asyncio.create_task(self._message_listener())
            
            logger.info("✅ Communication Hub v2.0 fully initialized")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def _init_redis(self):
        """Initialize Redis connection with retry logic"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.redis = await aioredis.create_redis_pool(
                    f'redis://{REDIS_HOST}:{REDIS_PORT}',
                    encoding='utf-8'
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
        """Initialize SQLite database"""
        self.db = await aio_connect(str(self.db_path))
        
        # Messages table
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                from_agent TEXT NOT NULL,
                to_agent TEXT NOT NULL,
                message_type TEXT NOT NULL,
                priority INTEGER NOT NULL,
                subject TEXT NOT NULL,
                body TEXT,
                data TEXT,
                timestamp TEXT NOT NULL,
                requires_response INTEGER DEFAULT 0,
                thread_id TEXT,
                response_id TEXT,
                read INTEGER DEFAULT 0
            )
        ''')
        
        # Knowledge base table
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                contributor TEXT NOT NULL,
                tags TEXT,
                timestamp TEXT NOT NULL,
                upvotes INTEGER DEFAULT 0,
                downvotes INTEGER DEFAULT 0
            )
        ''')
        
        # Agent expertise table
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS agent_expertise (
                agent_id TEXT PRIMARY KEY,
                expertise_areas TEXT NOT NULL,
                knowledge_contributions INTEGER DEFAULT 0,
                questions_answered INTEGER DEFAULT 0,
                last_active TEXT
            )
        ''')
        
        await self.db.commit()
        logger.info("📊 Communication database initialized")
    
    async def _load_state(self):
        """Load existing state from database"""
        try:
            # Load agent expertise
            async with self.db.execute('SELECT * FROM agent_expertise') as cursor:
                async for row in cursor:
                    agent_id = row[0]
                    self.agents_expertise[agent_id] = AgentExpertise(
                        agent_id=agent_id,
                        expertise_areas=json.loads(row[1]) if row[1] else [],
                        knowledge_contributions=row[2],
                        questions_answered=row[3],
                        last_active=datetime.fromisoformat(row[4]) if row[4] else datetime.now()
                    )
            
            logger.info(f"✅ Loaded {len(self.agents_expertise)} agent expertise profiles")
            
        except Exception as e:
            logger.error(f"❌ Error loading state: {e}")
    
    async def register_agent_expertise(self, agent_id: str, expertise_areas: List[str]):
        """Register an agent's areas of expertise"""
        try:
            expertise = AgentExpertise(
                agent_id=agent_id,
                expertise_areas=expertise_areas,
                last_active=datetime.now()
            )
            
            self.agents_expertise[agent_id] = expertise
            
            # Persist to database
            await self.db.execute('''
                INSERT OR REPLACE INTO agent_expertise 
                (agent_id, expertise_areas, last_active)
                VALUES (?, ?, ?)
            ''', (agent_id, json.dumps(expertise_areas), expertise.last_active.isoformat()))
            await self.db.commit()
            
            # Subscribe to agent's channel if Redis is available
            if self.redis_available:
                channel_name = f"agent:{agent_id}"
                channels = await self.redis.subscribe(channel_name)
                self.pubsub_channels[agent_id] = channels[0]
            
            logger.info(f"✅ Agent expertise registered: {agent_id} - {expertise_areas}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registering agent expertise: {e}")
            return False
    
    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        subject: str,
        body: str,
        priority: MessagePriority = MessagePriority.MEDIUM,
        data: Dict[str, Any] = None,
        requires_response: bool = False,
        thread_id: Optional[str] = None
    ) -> Optional[str]:
        """Send a message from one agent to another"""
        try:
            message_id = f"msg_{int(datetime.now().timestamp() * 1000)}"
            
            message = Message(
                id=message_id,
                from_agent=from_agent,
                to_agent=to_agent,
                message_type=message_type,
                priority=priority,
                subject=subject,
                body=body,
                data=data or {},
                timestamp=datetime.now(),
                requires_response=requires_response,
                thread_id=thread_id
            )
            
            # Store in thread if applicable
            if thread_id:
                self.message_threads[thread_id].append(message_id)
            
            # Store pending response if required
            if requires_response:
                self.pending_responses[message_id] = message
            
            # Store in database
            await self.db.execute('''
                INSERT INTO messages 
                (id, from_agent, to_agent, message_type, priority, subject, body, data, 
                 timestamp, requires_response, thread_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_id, from_agent, to_agent, message_type.value, priority.value,
                subject, body, json.dumps(data or {}), message.timestamp.isoformat(),
                1 if requires_response else 0, thread_id
            ))
            await self.db.commit()
            
            # Publish to Redis if available
            if self.redis_available:
                channel = f"agent:{to_agent}" if to_agent != "broadcast" else "agent:broadcast"
                await self.redis.publish(channel, json.dumps({
                    'message_id': message_id,
                    'from': from_agent,
                    'to': to_agent,
                    'type': message_type.value,
                    'priority': priority.value,
                    'subject': subject,
                    'body': body,
                    'data': data or {},
                    'timestamp': message.timestamp.isoformat(),
                    'requires_response': requires_response,
                    'thread_id': thread_id
                }))
            
            logger.info(f"📤 Message sent: {from_agent} → {to_agent} | {subject}")
            return message_id
            
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return None
    
    async def get_messages_for_agent(
        self,
        agent_id: str,
        unread_only: bool = True,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get messages for a specific agent"""
        try:
            query = '''
                SELECT * FROM messages 
                WHERE (to_agent = ? OR to_agent = 'broadcast')
            '''
            
            if unread_only:
                query += " AND read = 0"
            
            query += f" ORDER BY priority DESC, timestamp DESC LIMIT {limit}"
            
            messages = []
            async with self.db.execute(query, (agent_id,)) as cursor:
                async for row in cursor:
                    message_dict = {
                        'id': row[0],
                        'from_agent': row[1],
                        'to_agent': row[2],
                        'message_type': row[3],
                        'priority': row[4],
                        'subject': row[5],
                        'body': row[6],
                        'data': json.loads(row[7]) if row[7] else {},
                        'timestamp': row[8],
                        'requires_response': bool(row[9]),
                        'thread_id': row[10],
                        'response_id': row[11],
                        'read': bool(row[12])
                    }
                    messages.append(message_dict)
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error getting messages: {e}")
            return []
    
    async def mark_message_read(self, message_id: str):
        """Mark a message as read"""
        try:
            await self.db.execute('''
                UPDATE messages SET read = 1 WHERE id = ?
            ''', (message_id,))
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Error marking message as read: {e}")
            return False
    
    async def respond_to_message(
        self,
        message_id: str,
        from_agent: str,
        response_body: str,
        response_data: Dict[str, Any] = None
    ) -> Optional[str]:
        """Respond to a message"""
        try:
            # Get original message
            async with self.db.execute("SELECT * FROM messages WHERE id = ?", (message_id,)) as cursor:
                row = await cursor.fetchone()
                
                if not row:
                    logger.error(f"❌ Message not found: {message_id}")
                    return None
                
                original_message = {
                    'from_agent': row[1],
                    'subject': row[5],
                    'thread_id': row[10]
                }
            
            # Create response
            response_id = await self.send_message(
                from_agent=from_agent,
                to_agent=original_message['from_agent'],
                message_type=MessageType.TASK_RESPONSE,
                subject=f"Re: {original_message['subject']}",
                body=response_body,
                data=response_data,
                thread_id=original_message['thread_id'] or message_id
            )
            
            # Mark original message as responded
            await self.db.execute('''
                UPDATE messages SET response_id = ?, read = 1 WHERE id = ?
            ''', (response_id, message_id))
            await self.db.commit()
            
            # Remove from pending responses
            if message_id in self.pending_responses:
                del self.pending_responses[message_id]
            
            logger.info(f"📥 Response sent: {from_agent} → {original_message['from_agent']}")
            return response_id
            
        except Exception as e:
            logger.error(f"❌ Error responding to message: {e}")
            return None
    
    async def ask_question(
        self,
        from_agent: str,
        question: str,
        topic: Optional[str] = None
    ) -> Optional[str]:
        """Ask a question to all agents or experts in a specific topic"""
        try:
            # Find experts if topic is specified
            target_agents = []
            if topic:
                for agent_id, expertise in self.agents_expertise.items():
                    if topic.lower() in [e.lower() for e in expertise.expertise_areas]:
                        target_agents.append(agent_id)
            
            to_agent = "broadcast" if not target_agents else ",".join(target_agents)
            
            message_id = await self.send_message(
                from_agent=from_agent,
                to_agent=to_agent,
                message_type=MessageType.QUESTION,
                subject=f"Question: {topic or 'General'}",
                body=question,
                priority=MessagePriority.MEDIUM,
                requires_response=True
            )
            
            logger.info(f"❓ Question asked by {from_agent}: {question[:50]}...")
            return message_id
            
        except Exception as e:
            logger.error(f"❌ Error asking question: {e}")
            return None
    
    async def share_knowledge(
        self,
        contributor: str,
        topic: str,
        content: str,
        tags: List[str] = None
    ) -> Optional[int]:
        """Share knowledge with all agents"""
        try:
            # Store in knowledge base
            async with self.db.execute('''
                INSERT INTO knowledge_base (topic, content, contributor, tags, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (topic, content, contributor, json.dumps(tags or []), datetime.now().isoformat())) as cursor:
                knowledge_id = cursor.lastrowid
            
            await self.db.commit()
            
            # Update contributor's stats
            if contributor in self.agents_expertise:
                self.agents_expertise[contributor].knowledge_contributions += 1
                
                await self.db.execute('''
                    UPDATE agent_expertise 
                    SET knowledge_contributions = knowledge_contributions + 1
                    WHERE agent_id = ?
                ''', (contributor,))
                await self.db.commit()
            
            # Broadcast to all agents
            await self.send_message(
                from_agent=contributor,
                to_agent="broadcast",
                message_type=MessageType.KNOWLEDGE_SHARE,
                subject=f"Knowledge: {topic}",
                body=content,
                data={'tags': tags or [], 'knowledge_id': knowledge_id}
            )
            
            logger.info(f"📚 Knowledge shared by {contributor}: {topic}")
            return knowledge_id
            
        except Exception as e:
            logger.error(f"❌ Error sharing knowledge: {e}")
            return None
    
    async def search_knowledge(
        self,
        query: str,
        tags: List[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search the knowledge base"""
        try:
            sql_query = '''
                SELECT * FROM knowledge_base 
                WHERE content LIKE ? OR topic LIKE ?
            '''
            params = [f'%{query}%', f'%{query}%']
            
            if tags:
                sql_query += " AND tags LIKE ?"
                params.append(f'%{tags[0]}%')
            
            sql_query += f" ORDER BY upvotes DESC, timestamp DESC LIMIT {limit}"
            
            results = []
            async with self.db.execute(sql_query, params) as cursor:
                async for row in cursor:
                    results.append({
                        'id': row[0],
                        'topic': row[1],
                        'content': row[2],
                        'contributor': row[3],
                        'tags': json.loads(row[4]) if row[4] else [],
                        'timestamp': row[5],
                        'upvotes': row[6],
                        'downvotes': row[7]
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching knowledge: {e}")
            return []
    
    async def _message_listener(self):
        """Listen for incoming messages on subscribed channels"""
        while self.running:
            try:
                for agent_id, channel in self.pubsub_channels.items():
                    message = await channel.get(encoding='utf-8')
                    if message:
                        logger.info(f"📨 Received message for {agent_id}: {message}")
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Error in message listener: {e}")
                await asyncio.sleep(1)
    
    async def run(self):
        """Main run loop"""
        self.running = True
        logger.info("🚀 Communication Hub v2.0 running...")
        
        try:
            while self.running:
                # Periodic cleanup of old messages
                await asyncio.sleep(60)
                
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Gracefully shutdown the Communication Hub"""
        logger.info("🛑 Shutting down Communication Hub v2.0...")
        self.running = False
        
        # Cancel message listener
        if self.message_listener_task:
            self.message_listener_task.cancel()
        
        # Close Redis connection
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
        
        # Close database connection
        if self.db:
            await self.db.close()
        
        logger.info("✅ Communication Hub v2.0 shutdown complete")


# Main entry point
async def main():
    hub = CommunicationHubV2()
    await hub.initialize()
    await hub.run()


if __name__ == '__main__':
    asyncio.run(main())
