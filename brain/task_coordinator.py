#!/usr/bin/env python3
"""
🎯 TASK COORDINATOR
⚡ Intelligently assigns tasks to agents and prevents conflicts
🎯 Mission: Seamless multi-agent task execution without crashes
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
import logging

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TaskCoordinator')

class TaskCoordinator:
    """Coordinates task assignment across multiple agents"""
    
    def __init__(self):
        self.db_path = DB_PATH
    
    def assign_task_to_best_agent(self, task_id: int) -> Optional[str]:
        """
        Intelligently assign a task to the best available agent
        Returns agent name or None if no suitable agent found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get task details
        cursor.execute('SELECT title, description, priority FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        
        if not task:
            conn.close()
            return None
        
        title, description, priority = task
        
        # Determine task type from title/description
        task_type = self._categorize_task(title, description)
        
        # Find best agent for this task type
        best_agent = self._find_best_agent_for_task(task_type, cursor)
        
        if best_agent:
            # Check for conflicts
            conflicts = self._check_conflicts(best_agent, task_id, cursor)
            
            if conflicts:
                logger.warning(f"⚠️ Conflicts detected for {best_agent} on task #{task_id}")
                # Try to resolve or find alternative agent
                best_agent = self._find_alternative_agent(task_type, best_agent, cursor)
            
            if best_agent:
                # Assign task
                cursor.execute('''
                    UPDATE tasks SET assigned_agent = ? WHERE id = ?
                ''', (best_agent, task_id))
                conn.commit()
                
                logger.info(f"✅ Task #{task_id} assigned to {best_agent}")
        
        conn.close()
        return best_agent
    
    def _categorize_task(self, title: str, description: str) -> str:
        """Categorize task based on title and description"""
        text = (title + " " + description).lower()
        
        if any(word in text for word in ['frontend', 'react', 'ui', 'component', 'css', 'design']):
            return 'frontend'
        elif any(word in text for word in ['backend', 'api', 'database', 'server', 'endpoint']):
            return 'backend'
        elif any(word in text for word in ['test', 'qa', 'bug', 'quality']):
            return 'testing'
        elif any(word in text for word in ['deploy', 'ci/cd', 'docker', 'kubernetes', 'infrastructure']):
            return 'devops'
        elif any(word in text for word in ['security', 'auth', 'encryption', 'vulnerability']):
            return 'security'
        elif any(word in text for word in ['database', 'migration', 'schema', 'sql']):
            return 'database'
        elif any(word in text for word in ['document', 'readme', 'guide', 'docs']):
            return 'documentation'
        elif any(word in text for word in ['crm', 'customer', 'lead', 'support']):
            return 'crm'
        else:
            return 'general'
    
    def _find_best_agent_for_task(self, task_type: str, cursor) -> Optional[str]:
        """Find the best agent for a specific task type"""
        
        # Map task types to agent roles
        role_mapping = {
            'frontend': 'Frontend Specialist',
            'backend': 'Backend Specialist',
            'testing': 'Testing Specialist',
            'devops': 'DevOps Engineer',
            'security': 'Security Specialist',
            'database': 'Database Administrator',
            'documentation': 'Documentation Writer',
            'crm': 'CRM Support Agent',
            'general': 'Autonomous AI Developer'
        }
        
        preferred_role = role_mapping.get(task_type, 'Autonomous AI Developer')
        
        # Find agent with that role
        cursor.execute('''
            SELECT human_name, tasks_completed, tasks_failed
            FROM agents
            WHERE role = ? AND status = 'active'
            ORDER BY tasks_completed ASC
            LIMIT 1
        ''', (preferred_role,))
        
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Fallback to any available agent
        cursor.execute('''
            SELECT human_name
            FROM agents
            WHERE status = 'active'
            ORDER BY tasks_completed ASC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        return result[0] if result else None
    
    def _check_conflicts(self, agent_name: str, task_id: int, cursor) -> List[str]:
        """Check if agent has conflicts with this task"""
        conflicts = []
        
        # Check if agent is already working on a task
        cursor.execute('''
            SELECT id, title FROM tasks
            WHERE assigned_agent = ? AND status = 'in_progress'
        ''', (agent_name,))
        
        active_tasks = cursor.fetchall()
        
        if active_tasks:
            conflicts.append(f"Agent already working on {len(active_tasks)} task(s)")
        
        return conflicts
    
    def _find_alternative_agent(self, task_type: str, excluded_agent: str, cursor) -> Optional[str]:
        """Find an alternative agent when primary choice has conflicts"""
        
        role_mapping = {
            'frontend': 'Frontend Specialist',
            'backend': 'Backend Specialist',
            'testing': 'Testing Specialist',
            'devops': 'DevOps Engineer',
            'security': 'Security Specialist',
            'database': 'Database Administrator',
            'documentation': 'Documentation Writer',
            'crm': 'CRM Support Agent',
            'general': 'Autonomous AI Developer'
        }
        
        preferred_role = role_mapping.get(task_type, 'Autonomous AI Developer')
        
        # Find another agent with same role
        cursor.execute('''
            SELECT human_name
            FROM agents
            WHERE role = ? AND status = 'active' AND human_name != ?
            ORDER BY tasks_completed ASC
            LIMIT 1
        ''', (preferred_role, excluded_agent))
        
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Fallback to Project Manager Assistant for coordination
        cursor.execute('''
            SELECT human_name
            FROM agents
            WHERE role = 'Project Manager Assistant' AND status = 'active'
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        return result[0] if result else None
    
    def create_collaboration(self, task_id: int, lead_agent: str, 
                           collaborators: List[str]) -> bool:
        """Create a collaborative task assignment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update task with lead agent
        cursor.execute('''
            UPDATE tasks SET assigned_agent = ? WHERE id = ?
        ''', (lead_agent, task_id))
        
        # Create collaboration record
        import json
        cursor.execute('''
            INSERT INTO agent_collaborations
            (task_id, lead_agent, collaborating_agents, status)
            VALUES (?, ?, ?, 'active')
        ''', (task_id, lead_agent, json.dumps(collaborators)))
        
        conn.commit()
        conn.close()
        
        logger.info(f"🤝 Collaboration created: {lead_agent} + {', '.join(collaborators)}")
        return True
    
    def get_agent_workload(self, agent_name: str) -> Dict:
        """Get current workload for an agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM tasks
            WHERE assigned_agent = ? AND status = 'in_progress'
        ''', (agent_name,))
        
        active_tasks = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM tasks
            WHERE assigned_agent = ? AND status = 'pending'
        ''', (agent_name,))
        
        pending_tasks = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT tasks_completed, tasks_failed FROM agents
            WHERE human_name = ?
        ''', (agent_name,))
        
        result = cursor.fetchone()
        completed, failed = result if result else (0, 0)
        
        conn.close()
        
        return {
            'agent': agent_name,
            'active_tasks': active_tasks,
            'pending_tasks': pending_tasks,
            'completed_tasks': completed,
            'failed_tasks': failed,
            'total_workload': active_tasks + pending_tasks
        }
    
    def balance_workload(self) -> List[Dict]:
        """Balance workload across all agents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all active agents with their workloads
        cursor.execute('''
            SELECT human_name FROM agents WHERE status = 'active'
        ''')
        
        agents = [row[0] for row in cursor.fetchall()]
        workloads = [self.get_agent_workload(agent) for agent in agents]
        
        # Sort by workload
        workloads.sort(key=lambda x: x['total_workload'])
        
        # Find overloaded and underloaded agents
        avg_workload = sum(w['total_workload'] for w in workloads) / len(workloads) if workloads else 0
        
        rebalanced = []
        
        for workload in workloads:
            if workload['total_workload'] > avg_workload * 1.5:
                # Agent is overloaded
                logger.warning(f"⚠️ {workload['agent']} is overloaded: {workload['total_workload']} tasks")
                rebalanced.append({
                    'agent': workload['agent'],
                    'status': 'overloaded',
                    'workload': workload['total_workload'],
                    'avg': avg_workload
                })
        
        conn.close()
        return rebalanced

if __name__ == "__main__":
    print("🎯 Task Coordinator System")
    print("=" * 60)
    
    coordinator = TaskCoordinator()
    
    print("\n📊 Checking agent workloads...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT human_name FROM agents WHERE status = 'active' LIMIT 5")
    agents = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    for agent in agents:
        workload = coordinator.get_agent_workload(agent)
        print(f"  {agent}: {workload['active_tasks']} active, "
              f"{workload['pending_tasks']} pending, "
              f"{workload['completed_tasks']} completed")
    
    print("\n✅ Task coordinator operational!")
