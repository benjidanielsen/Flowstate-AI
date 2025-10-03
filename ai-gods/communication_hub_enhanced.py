#!/usr/bin/env python3
"""
🧠 ENHANCED AI COMMUNICATION HUB
⚡ GODMODE: Advanced inter-agent communication and collaboration
🎯 Mission: Enable seamless AI-to-AI interaction, knowledge sharing, and coordination
"""

import asyncio
import json
import logging
import platform
import redis
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import threading
import queue


# Ensure UTF-8 encoding for stdout on Windows to support emoji logging
if platform.system() == 'Windows':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

logging.basicConfig(
    level=logging.INFO,
    format='🧠 [COMM-HUB] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/communication-hub-enhanced.log', encoding='utf-8'),
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
    data: Dict[str, Any]
    timestamp: datetime
    requires_response: bool
    thread_id: Optional[str]


class EnhancedCommunicationHub:
    """
    Enhanced communication hub for AI agent collaboration
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379, db_path='godmode-communication.db'):
        self.project_root = Path(__file__).parent.parent
        self.db_path = self.project_root / db_path
        
        # Initialize Redis for real-time messaging
        try:
            self.redis_client = redis.StrictRedis(
                host=redis_host,
                port=redis_port,
                db=0,
                decode_responses=True
            )
            self.redis_client.ping()
            self.redis_available = True
            self.pubsub = self.redis_client.pubsub()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {e}. Using fallback mode.")
            self.redis_available = False
        
        # Initialize SQLite for persistent storage
        self.init_database()
        
        # Message queues
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Knowledge base
        self.shared_knowledge = {}
        self.agent_expertise = {}
        
        # Active threads
        self.message_threads = {}
        
        logger.info("🚀 ENHANCED COMMUNICATION HUB INITIALIZED")
    
    def init_database(self):
        """Initialize SQLite database for message history"""
        self.db_connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.db_cursor = self.db_connection.cursor()
        
        # Messages table
        self.db_cursor.execute('''
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
                requires_response INTEGER,
                thread_id TEXT,
                response_id TEXT
            )
        ''')
        
        # Knowledge base table
        self.db_cursor.execute('''
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
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_expertise (
                agent_id TEXT PRIMARY KEY,
                expertise_areas TEXT NOT NULL,
                knowledge_contributions INTEGER DEFAULT 0,
                questions_answered INTEGER DEFAULT 0,
                last_active TEXT
            )
        ''')
        
        self.db_connection.commit()
        logger.info("📊 Communication database initialized")
    
    def register_agent_expertise(self, agent_id: str, expertise_areas: List[str]):
        """Register an agent's areas of expertise"""
        self.agent_expertise[agent_id] = expertise_areas
        
        # Persist to database
        self.db_cursor.execute('''
            INSERT OR REPLACE INTO agent_expertise 
            (agent_id, expertise_areas, last_active)
            VALUES (?, ?, ?)
        ''', (agent_id, json.dumps(expertise_areas), datetime.now().isoformat()))
        self.db_connection.commit()
        
        logger.info(f"✅ Agent expertise registered: {agent_id} - {expertise_areas}")
    
    def send_message(self, from_agent: str, to_agent: str, message_type: MessageType,
                    subject: str, body: str, priority: MessagePriority = MessagePriority.MEDIUM,
                    data: Dict[str, Any] = None, requires_response: bool = False,
                    thread_id: Optional[str] = None) -> str:
        """Send a message from one agent to another"""
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
        
        # Store in database
        self.db_cursor.execute('''
            INSERT INTO messages 
            (id, from_agent, to_agent, message_type, priority, subject, body, data, 
             timestamp, requires_response, thread_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message_id, from_agent, to_agent, message_type.value, priority.value,
            subject, body, json.dumps(data or {}), message.timestamp.isoformat(),
            1 if requires_response else 0, thread_id
        ))
        self.db_connection.commit()
        
        # Publish to Redis if available
        if self.redis_available:
            channel = f"agent:{to_agent}" if to_agent != "broadcast" else "agent:broadcast"
            self.redis_client.publish(channel, json.dumps({
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
    
    def get_messages_for_agent(self, agent_id: str, unread_only: bool = True) -> List[Dict[str, Any]]:
        """Get messages for a specific agent"""
        query = '''
            SELECT * FROM messages 
            WHERE (to_agent = ? OR to_agent = 'broadcast')
        '''
        
        if unread_only:
            query += " AND response_id IS NULL"
        
        query += " ORDER BY timestamp DESC LIMIT 50"
        
        self.db_cursor.execute(query, (agent_id,))
        rows = self.db_cursor.fetchall()
        
        messages = []
        for row in rows:
            columns = [description[0] for description in self.db_cursor.description]
            message_dict = dict(zip(columns, row))
            message_dict['data'] = json.loads(message_dict['data'])
            messages.append(message_dict)
        
        return messages
    
    def respond_to_message(self, message_id: str, from_agent: str, response_body: str,
                          response_data: Dict[str, Any] = None) -> str:
        """Respond to a message"""
        # Get original message
        self.db_cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
        row = self.db_cursor.fetchone()
        
        if not row:
            logger.error(f"❌ Message not found: {message_id}")
            return None
        
        columns = [description[0] for description in self.db_cursor.description]
        original_message = dict(zip(columns, row))
        
        # Create response
        response_id = self.send_message(
            from_agent=from_agent,
            to_agent=original_message['from_agent'],
            message_type=MessageType.TASK_RESPONSE,
            subject=f"Re: {original_message['subject']}",
            body=response_body,
            data=response_data,
            thread_id=original_message['thread_id'] or message_id
        )
        
        # Mark original message as responded
        self.db_cursor.execute('''
            UPDATE messages SET response_id = ? WHERE id = ?
        ''', (response_id, message_id))
        self.db_connection.commit()
        
        logger.info(f"📥 Response sent: {from_agent} → {original_message['from_agent']}")
        
        return response_id
    
    def ask_question(self, from_agent: str, question: str, topic: str = None) -> Optional[str]:
        """Ask a question to all agents or experts in a specific topic"""
        # Find experts if topic is specified
        target_agents = []
        if topic:
            for agent_id, expertise in self.agent_expertise.items():
                if topic.lower() in [e.lower() for e in expertise]:
                    target_agents.append(agent_id)
        
        to_agent = "broadcast" if not target_agents else ",".join(target_agents)
        
        message_id = self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.QUESTION,
            subject=f"Question: {question[:50]}...",
            body=question,
            data={'topic': topic} if topic else {},
            requires_response=True,
            priority=MessagePriority.MEDIUM
        )
        
        logger.info(f"❓ Question asked: {from_agent} → {to_agent}")
        
        return message_id
    
    def share_knowledge(self, from_agent: str, topic: str, content: str, tags: List[str] = None):
        """Share knowledge with all agents"""
        # Store in knowledge base
        self.db_cursor.execute('''
            INSERT INTO knowledge_base (topic, content, contributor, tags, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (topic, content, from_agent, json.dumps(tags or []), datetime.now().isoformat()))
        self.db_connection.commit()
        
        # Broadcast to all agents
        self.send_message(
            from_agent=from_agent,
            to_agent="broadcast",
            message_type=MessageType.KNOWLEDGE_SHARE,
            subject=f"Knowledge: {topic}",
            body=content,
            data={'tags': tags or []},
            priority=MessagePriority.LOW
        )
        
        logger.info(f"📚 Knowledge shared: {from_agent} | {topic}")
    
    def search_knowledge_base(self, query: str, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Search the shared knowledge base"""
        sql_query = "SELECT * FROM knowledge_base WHERE content LIKE ?"
        params = [f"%{query}%"]
        
        if tags:
            sql_query += " AND tags LIKE ?"
            params.append(f"%{tags[0]}%")  # Simplified tag search
        
        sql_query += " ORDER BY timestamp DESC LIMIT 20"
        
        self.db_cursor.execute(sql_query, params)
        rows = self.db_cursor.fetchall()
        
        results = []
        for row in rows:
            columns = [description[0] for description in self.db_cursor.description]
            result_dict = dict(zip(columns, row))
            result_dict['tags'] = json.loads(result_dict['tags'])
            results.append(result_dict)
        
        logger.info(f"🔍 Knowledge search: '{query}' - {len(results)} results")
        
        return results
    
    def get_message_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a thread"""
        self.db_cursor.execute('''
            SELECT * FROM messages 
            WHERE thread_id = ? OR id = ?
            ORDER BY timestamp ASC
        ''', (thread_id, thread_id))
        rows = self.db_cursor.fetchall()
        
        thread = []
        for row in rows:
            columns = [description[0] for description in self.db_cursor.description]
            message_dict = dict(zip(columns, row))
            message_dict['data'] = json.loads(message_dict['data'])
            thread.append(message_dict)
        
        return thread
    
    def broadcast_status_update(self, from_agent: str, status: str, progress: int, current_task: str):
        """Broadcast a status update to all agents"""
        self.send_message(
            from_agent=from_agent,
            to_agent="broadcast",
            message_type=MessageType.STATUS_UPDATE,
            subject="Status Update",
            body=status,
            data={
                'progress': progress,
                'current_task': current_task,
                'timestamp': datetime.now().isoformat()
            },
            priority=MessagePriority.LOW
        )
    
    def send_alert(self, from_agent: str, alert_message: str, severity: str = "INFO"):
        """Send an alert to all agents"""
        priority_map = {
            "INFO": MessagePriority.LOW,
            "WARNING": MessagePriority.MEDIUM,
            "ERROR": MessagePriority.HIGH,
            "CRITICAL": MessagePriority.CRITICAL
        }
        
        self.send_message(
            from_agent=from_agent,
            to_agent="broadcast",
            message_type=MessageType.ALERT,
            subject=f"{severity}: {alert_message[:50]}",
            body=alert_message,
            data={'severity': severity},
            priority=priority_map.get(severity, MessagePriority.MEDIUM)
        )
        
        logger.warning(f"🚨 Alert sent: {severity} | {alert_message[:100]}")
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'total_messages': 0,
            'messages_by_type': {},
            'messages_by_agent': {},
            'knowledge_base_size': 0,
            'active_threads': 0
        }
        
        # Total messages
        self.db_cursor.execute("SELECT COUNT(*) FROM messages")
        stats['total_messages'] = self.db_cursor.fetchone()[0]
        
        # Messages by type
        self.db_cursor.execute('''
            SELECT message_type, COUNT(*) as count 
            FROM messages 
            GROUP BY message_type
        ''')
        for row in self.db_cursor.fetchall():
            stats['messages_by_type'][row[0]] = row[1]
        
        # Messages by agent
        self.db_cursor.execute('''
            SELECT from_agent, COUNT(*) as count 
            FROM messages 
            GROUP BY from_agent
        ''')
        for row in self.db_cursor.fetchall():
            stats['messages_by_agent'][row[0]] = row[1]
        
        # Knowledge base size
        self.db_cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        stats['knowledge_base_size'] = self.db_cursor.fetchone()[0]
        
        return stats
    
    async def run_communication_loop(self):
        """Main communication loop"""
        logger.info("🎯 Starting communication loop")
        
        while True:
            try:
                # Process message queue
                while not self.message_queue.empty():
                    message = self.message_queue.get()
                    # Process message (placeholder for actual processing)
                    logger.debug(f"Processing message: {message}")
                
                # Log stats periodically
                stats = self.get_communication_stats()
                logger.info(f"📊 Communication stats: {stats['total_messages']} total messages, "
                          f"{stats['knowledge_base_size']} knowledge entries")
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in communication loop: {e}")
                await asyncio.sleep(30)


# Example usage
if __name__ == "__main__":
    hub = EnhancedCommunicationHub()
    
    # Register agents
    hub.register_agent_expertise("backend-dev-001", ["python", "api", "database"])
    hub.register_agent_expertise("frontend-dev-001", ["react", "ui", "design"])
    hub.register_agent_expertise("database-dev-001", ["sql", "optimization", "migrations"])
    
    # Send a message
    msg_id = hub.send_message(
        from_agent="backend-dev-001",
        to_agent="frontend-dev-001",
        message_type=MessageType.QUESTION,
        subject="API endpoint design",
        body="What's the best way to structure the user profile API?",
        requires_response=True
    )
    
    # Respond to the message
    hub.respond_to_message(
        message_id=msg_id,
        from_agent="frontend-dev-001",
        response_body="I recommend using RESTful endpoints with /api/users/:id/profile"
    )
    
    # Share knowledge
    hub.share_knowledge(
        from_agent="database-dev-001",
        topic="Database Indexing",
        content="Always index foreign keys for better join performance",
        tags=["database", "performance", "best-practice"]
    )
    
    # Ask a question
    hub.ask_question(
        from_agent="backend-dev-001",
        question="How do we handle authentication tokens?",
        topic="api"
    )
    
    # Get stats
    stats = hub.get_communication_stats()
    print(json.dumps(stats, indent=2))
    
    logger.info("✅ Enhanced Communication Hub demonstration complete")
