#!/usr/bin/env python3
"""
📡 SIMPLE COMMUNICATION HUB
⚡ Lightweight messaging system for AI agent coordination
🎯 Mission: Enable seamless communication between AI agents
"""

import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/simple-communication-hub.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('SimpleCommunicationHub')

class SimpleCommunicationHub:
    """Simplified Communication Hub for agent messaging"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.db_path = self.project_root / "godmode-state.db"
        self.init_database()
        logger.info("📡 Simple Communication Hub initialized")
        
    def init_database(self):
        """Initialize the SQLite database for messaging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_agent TEXT NOT NULL,
                to_agent TEXT,
                message_type TEXT DEFAULT 'info',
                subject TEXT,
                content TEXT NOT NULL,
                status TEXT DEFAULT 'unread',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP
            )
        ''')
        
        # Create agent_status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_status (
                agent_name TEXT PRIMARY KEY,
                status TEXT DEFAULT 'offline',
                last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                current_task TEXT,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Communication database initialized")
    
    def send_message(self, from_agent: str, to_agent: Optional[str], message_type: str, 
                    subject: str, content: str) -> int:
        """Send a message from one agent to another (or broadcast if to_agent is None)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO messages (from_agent, to_agent, message_type, subject, content, status)
                VALUES (?, ?, ?, ?, ?, 'unread')
            ''', (from_agent, to_agent, message_type, subject, content))
            conn.commit()
            message_id = cursor.lastrowid
            
            if to_agent:
                logger.info(f"📨 Message #{message_id} sent from {from_agent} to {to_agent}: {subject}")
            else:
                logger.info(f"📢 Broadcast #{message_id} from {from_agent}: {subject}")
            
            return message_id
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            return None
        finally:
            conn.close()
    
    def get_messages(self, agent_name: str, status: str = 'unread') -> List[Dict[str, Any]]:
        """Get messages for a specific agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, from_agent, message_type, subject, content, created_at
            FROM messages
            WHERE (to_agent = ? OR to_agent IS NULL) AND status = ?
            ORDER BY created_at DESC
        ''', (agent_name, status))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'from': row[1],
                'type': row[2],
                'subject': row[3],
                'content': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return messages
    
    def mark_as_read(self, message_id: int) -> bool:
        """Mark a message as read"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE messages
                SET status = 'read', read_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (message_id,))
            conn.commit()
            logger.info(f"✅ Message #{message_id} marked as read")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to mark message as read: {e}")
            return False
        finally:
            conn.close()
    
    def update_agent_status(self, agent_name: str, status: str, current_task: str = None, 
                           metadata: Dict[str, Any] = None) -> bool:
        """Update an agent's status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            metadata_json = json.dumps(metadata) if metadata else None
            cursor.execute('''
                INSERT OR REPLACE INTO agent_status (agent_name, status, last_heartbeat, current_task, metadata)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)
            ''', (agent_name, status, current_task, metadata_json))
            conn.commit()
            logger.info(f"✅ Agent status updated: {agent_name} - {status}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update agent status: {e}")
            return False
        finally:
            conn.close()
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get the current status of an agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT status, last_heartbeat, current_task, metadata
            FROM agent_status
            WHERE agent_name = ?
        ''', (agent_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'agent': agent_name,
                'status': row[0],
                'last_heartbeat': row[1],
                'current_task': row[2],
                'metadata': json.loads(row[3]) if row[3] else None
            }
        return None
    
    def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT agent_name, status, last_heartbeat, current_task
            FROM agent_status
            ORDER BY last_heartbeat DESC
        ''')
        
        agents = []
        for row in cursor.fetchall():
            agents.append({
                'agent': row[0],
                'status': row[1],
                'last_heartbeat': row[2],
                'current_task': row[3]
            })
        
        conn.close()
        return agents
    
    def run(self):
        """Main execution loop"""
        logger.info("🚀 Simple Communication Hub is running")
        
        # Update hub status
        self.update_agent_status("Communication Hub", "online", "Facilitating agent communication")
        
        # Send a welcome broadcast
        self.send_message(
            "Communication Hub",
            None,
            "announcement",
            "System Online",
            "The Flowstate-AI communication system is now operational. All agents can now communicate seamlessly."
        )
        
        # Display current agent statuses
        agents = self.get_all_agents_status()
        logger.info(f"👥 Active agents: {len(agents)}")
        for agent in agents:
            logger.info(f"   - {agent['agent']}: {agent['status']} (Task: {agent['current_task'] or 'None'})")
        
        logger.info("✅ Simple Communication Hub is operational")
        logger.info("💬 Ready to facilitate agent communication")

if __name__ == "__main__":
    hub = SimpleCommunicationHub()
    hub.run()
