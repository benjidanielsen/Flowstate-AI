#!/usr/bin/env python3
"""
💬 AGENT COMMUNICATION SYSTEM
⚡ Enables agents to communicate, collaborate, and avoid conflicts
🎯 Mission: Seamless multi-agent coordination
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AgentComm')

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"

class AgentCommunication:
    """Handles all agent-to-agent communication"""
    
    def __init__(self):
        self.db_path = DB_PATH
    
    def send_message(self, from_agent: str, to_agent: str, message_type: str, 
                     subject: str, content: str, priority: int = 5) -> int:
        """
        Send a message from one agent to another
        
        Message types:
        - task_request: Request another agent to do something
        - task_offer: Offer to help with a task
        - status_update: Share progress on a task
        - question: Ask for help or clarification
        - answer: Respond to a question
        - warning: Alert about potential issue
        - conflict: Report a conflict that needs resolution
        - acknowledgment: Confirm receipt of message
        
        Priority: 1 (urgent) to 10 (low)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agent_messages 
            (from_agent, to_agent, message_type, subject, content, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (from_agent, to_agent, message_type, subject, content, priority))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"📨 {from_agent} → {to_agent}: {message_type} - {subject}")
        
        # Log to activity log
        self._log_activity(from_agent, 'message_sent', 
                          f"Sent {message_type} to {to_agent}: {subject}")
        
        return message_id
    
    def get_messages(self, agent_name: str, status: str = 'pending') -> List[Dict]:
        """Get all messages for an agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, from_agent, message_type, subject, content, priority, created_at
            FROM agent_messages
            WHERE to_agent = ? AND status = ?
            ORDER BY priority ASC, created_at ASC
        ''', (agent_name, status))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'from': row[1],
                'type': row[2],
                'subject': row[3],
                'content': row[4],
                'priority': row[5],
                'created_at': row[6]
            })
        
        conn.close()
        return messages
    
    def acknowledge_message(self, message_id: int, agent_name: str) -> bool:
        """Mark a message as acknowledged"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE agent_messages
            SET status = 'acknowledged', acknowledged_at = CURRENT_TIMESTAMP
            WHERE id = ? AND to_agent = ?
        ''', (message_id, agent_name))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            logger.info(f"✅ {agent_name} acknowledged message #{message_id}")
        
        return success
    
    def start_collaboration(self, task_id: int, lead_agent: str, 
                           collaborating_agents: List[str]) -> int:
        """Start a collaborative task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        agents_json = json.dumps(collaborating_agents)
        
        cursor.execute('''
            INSERT INTO agent_collaborations
            (task_id, lead_agent, collaborating_agents, status)
            VALUES (?, ?, ?, 'active')
        ''', (task_id, lead_agent, agents_json))
        
        collab_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"🤝 Collaboration started: {lead_agent} + {', '.join(collaborating_agents)}")
        
        # Notify all collaborators
        for agent in collaborating_agents:
            self.send_message(
                lead_agent, agent, 'task_request',
                f'Collaboration on Task #{task_id}',
                f'You have been invited to collaborate on task #{task_id}. {lead_agent} is the lead.',
                priority=3
            )
        
        return collab_id
    
    def report_conflict(self, agent1: str, agent2: str, conflict_type: str, 
                       description: str) -> int:
        """Report a conflict between agents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agent_conflicts
            (agent1, agent2, conflict_type, description, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (agent1, agent2, conflict_type, description))
        
        conflict_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.warning(f"⚠️ CONFLICT: {agent1} ↔ {agent2} - {conflict_type}")
        
        # Notify Project Manager
        self.send_message(
            'System', 'Project Manager', 'warning',
            f'Conflict between {agent1} and {agent2}',
            f'Type: {conflict_type}\n{description}',
            priority=1
        )
        
        return conflict_id
    
    def resolve_conflict(self, conflict_id: int, resolution: str, 
                        resolved_by: str) -> bool:
        """Resolve a conflict"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE agent_conflicts
            SET resolution = ?, resolved_by = ?, status = 'resolved',
                resolved_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (resolution, resolved_by, conflict_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        
        if success:
            # Get conflict details
            cursor.execute('''
                SELECT agent1, agent2, conflict_type
                FROM agent_conflicts WHERE id = ?
            ''', (conflict_id,))
            row = cursor.fetchone()
            
            if row:
                agent1, agent2, conflict_type = row
                logger.info(f"✅ CONFLICT RESOLVED by {resolved_by}: {agent1} ↔ {agent2}")
                
                # Notify both agents
                for agent in [agent1, agent2]:
                    self.send_message(
                        resolved_by, agent, 'status_update',
                        f'Conflict Resolved: {conflict_type}',
                        f'Resolution: {resolution}',
                        priority=2
                    )
        
        conn.close()
        return success
    
    def check_for_conflicts(self, agent_name: str, task_id: int) -> List[Dict]:
        """
        Check if an agent working on a task would conflict with others
        Returns list of potential conflicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if other agents are working on the same task
        cursor.execute('''
            SELECT assigned_agent FROM tasks
            WHERE id = ? AND status = 'in_progress' AND assigned_agent != ?
        ''', (task_id, agent_name))
        
        conflicts = []
        for row in cursor.fetchall():
            other_agent = row[0]
            conflicts.append({
                'type': 'duplicate_work',
                'agent': other_agent,
                'task_id': task_id,
                'severity': 'high'
            })
        
        conn.close()
        return conflicts
    
    def broadcast_message(self, from_agent: str, message_type: str, 
                         subject: str, content: str, priority: int = 5) -> List[int]:
        """Send a message to all active agents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT human_name FROM agents WHERE status = 'active'
        ''')
        
        message_ids = []
        for row in cursor.fetchall():
            agent_name = row[0]
            if agent_name != from_agent:
                msg_id = self.send_message(
                    from_agent, agent_name, message_type, 
                    subject, content, priority
                )
                message_ids.append(msg_id)
        
        conn.close()
        logger.info(f"📢 {from_agent} broadcast to {len(message_ids)} agents")
        return message_ids
    
    def get_collaboration_status(self, task_id: int) -> Optional[Dict]:
        """Get collaboration status for a task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT lead_agent, collaborating_agents, status, created_at
            FROM agent_collaborations
            WHERE task_id = ? AND status = 'active'
        ''', (task_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'lead': row[0],
                'collaborators': json.loads(row[1]),
                'status': row[2],
                'started_at': row[3]
            }
        return None
    
    def _log_activity(self, agent_name: str, action_type: str, description: str):
        """Log activity to activity_log table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO activity_log (agent_name, action_type, description)
                VALUES (?, ?, ?)
            ''', (agent_name, action_type, description))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")

if __name__ == "__main__":
    print("💬 Agent Communication System")
    print("=" * 60)
    
    comm = AgentCommunication()
    
    print("\n🧪 Testing communication system...")
    
    # Test sending messages
    msg_id = comm.send_message(
        'Layla', 'Sophia', 'status_update',
        'Task Progress', 'Completed 5 tasks successfully!',
        priority=5
    )
    print(f"  ✅ Message sent: ID {msg_id}")
    
    # Test getting messages
    messages = comm.get_messages('Sophia')
    print(f"  ✅ Sophia has {len(messages)} pending messages")
    
    # Test collaboration
    collab_id = comm.start_collaboration(
        task_id=100,
        lead_agent='Sophia',
        collaborating_agents=['Layla', 'Emma', 'Marcus']
    )
    print(f"  ✅ Collaboration started: ID {collab_id}")
    
    # Test conflict reporting
    conflict_id = comm.report_conflict(
        'Layla', 'Marcus', 'duplicate_work',
        'Both agents trying to work on the same file'
    )
    print(f"  ✅ Conflict reported: ID {conflict_id}")
    
    # Test conflict resolution
    comm.resolve_conflict(
        conflict_id, 
        'Layla will handle frontend, Marcus will handle backend',
        'Sophia'
    )
    print(f"  ✅ Conflict resolved by Sophia")
    
    # Test broadcast
    msg_ids = comm.broadcast_message(
        'Sophia', 'status_update',
        'Daily Standup', 'Great work everyone! Keep it up!',
        priority=7
    )
    print(f"  ✅ Broadcast sent to {len(msg_ids)} agents")
    
    print("\n✅ Communication system operational!")
