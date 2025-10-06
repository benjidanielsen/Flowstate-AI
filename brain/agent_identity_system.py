#!/usr/bin/env python3
"""
🤖 AGENT IDENTITY SYSTEM
⚡ Gives each AI agent a unique identity, personality, and lifecycle
🎯 Mission: Make agents feel alive and personal
"""

import sqlite3
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AgentIdentity')

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"

# Human names for agents
HUMAN_NAMES = {
    'male': [
        'Marcus', 'Alex', 'Ethan', 'Noah', 'Liam', 'Oliver', 'James', 'Lucas',
        'Mason', 'Logan', 'Elijah', 'Aiden', 'Jackson', 'Sebastian', 'Jack',
        'Owen', 'Samuel', 'Henry', 'Wyatt', 'Leo', 'Gabriel', 'Julian', 'Isaac'
    ],
    'female': [
        'Sophia', 'Emma', 'Olivia', 'Ava', 'Isabella', 'Mia', 'Charlotte', 'Amelia',
        'Harper', 'Evelyn', 'Abigail', 'Emily', 'Luna', 'Aria', 'Scarlett', 'Grace',
        'Chloe', 'Victoria', 'Riley', 'Zoe', 'Nora', 'Lily', 'Hannah', 'Layla'
    ],
    'neutral': [
        'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery', 'Quinn', 'Sage',
        'River', 'Phoenix', 'Sky', 'Rowan', 'Dakota', 'Kai', 'Ash', 'Eden'
    ]
}

# Personality traits
PERSONALITY_TRAITS = [
    'Methodical', 'Creative', 'Analytical', 'Innovative', 'Precise', 'Efficient',
    'Thorough', 'Fast', 'Careful', 'Bold', 'Strategic', 'Detail-oriented',
    'Big-picture thinker', 'Problem-solver', 'Perfectionist', 'Pragmatic',
    'Experimental', 'Conservative', 'Adaptive', 'Focused'
]

# Specializations
SPECIALIZATIONS = {
    'Backend Developer': ['API design', 'Database optimization', 'Server architecture', 'Python expert'],
    'Frontend Developer': ['UI/UX', 'React mastery', 'CSS wizard', 'Responsive design'],
    'Database Agent': ['Query optimization', 'Schema design', 'Data integrity', 'Performance tuning'],
    'DevOps Agent': ['CI/CD', 'Container orchestration', 'Infrastructure as code', 'Monitoring'],
    'Testing Agent': ['Test automation', 'Quality assurance', 'Bug hunting', 'Coverage analysis'],
    'Security Agent': ['Vulnerability assessment', 'Penetration testing', 'Secure coding', 'Compliance'],
    'Documentation Agent': ['Technical writing', 'API documentation', 'User guides', 'Knowledge management'],
    'Autonomous AI Developer': ['Code generation', 'Task automation', 'AI integration', 'Full-stack development']
}

class AgentIdentitySystem:
    """Manages agent identities and lifecycles"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.used_names = self._get_used_names()
    
    def _get_used_names(self) -> set:
        """Get names already in use"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT human_name FROM agents WHERE status = 'active'")
            names = {row[0] for row in cursor.fetchall()}
            conn.close()
            return names
        except:
            return set()
    
    def _generate_agent_number(self) -> str:
        """Generate a unique agent number"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM agents")
        count = cursor.fetchone()[0]
        conn.close()
        
        return f"Agent-{count + 1:03d}"
    
    def _pick_human_name(self, gender: str = None) -> str:
        """Pick a unique human name"""
        if gender is None:
            gender = random.choice(['male', 'female', 'neutral'])
        
        available_names = [
            name for name in HUMAN_NAMES[gender]
            if name not in self.used_names
        ]
        
        if not available_names:
            # If all names used, pick from all genders
            all_names = HUMAN_NAMES['male'] + HUMAN_NAMES['female'] + HUMAN_NAMES['neutral']
            available_names = [name for name in all_names if name not in self.used_names]
        
        if not available_names:
            # If still no names, generate a unique one
            return f"Agent{random.randint(100, 999)}"
        
        name = random.choice(available_names)
        self.used_names.add(name)
        return name
    
    def _pick_personality_traits(self, count: int = 3) -> str:
        """Pick random personality traits"""
        traits = random.sample(PERSONALITY_TRAITS, min(count, len(PERSONALITY_TRAITS)))
        return ', '.join(traits)
    
    def _pick_specialization(self, role: str) -> str:
        """Pick specialization based on role"""
        specs = SPECIALIZATIONS.get(role, ['General development', 'Problem solving'])
        return ', '.join(random.sample(specs, min(2, len(specs))))
    
    def birth_agent(self, role: str, gender: str = None) -> Dict:
        """Create a new agent with identity"""
        agent_number = self._generate_agent_number()
        human_name = self._pick_human_name(gender)
        personality = self._pick_personality_traits()
        specialization = self._pick_specialization(role)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agents (agent_number, human_name, role, specialization, personality_traits, status)
            VALUES (?, ?, ?, ?, ?, 'active')
        ''', (agent_number, human_name, role, specialization, personality))
        
        agent_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        agent = {
            'id': agent_id,
            'agent_number': agent_number,
            'human_name': human_name,
            'role': role,
            'specialization': specialization,
            'personality_traits': personality,
            'birth_timestamp': datetime.now().isoformat(),
            'status': 'active'
        }
        
        logger.info(f"👶 Agent born: {agent_number} ({human_name}) - {role}")
        logger.info(f"   Personality: {personality}")
        logger.info(f"   Specialization: {specialization}")
        
        # Log to activity log
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO activity_log (agent_name, action_type, description, details)
                VALUES (?, ?, ?, ?)
            ''', (f"{human_name} ({agent_number})", 'agent_birth', 
                  f"New agent born: {human_name}", 
                  f"Role: {role}, Personality: {personality}"))
            conn.commit()
        except:
            pass
        
        return agent
    
    def kill_agent(self, agent_number: str, reason: str = "Task completed"):
        """Mark an agent as dead/inactive"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE agents 
            SET status = 'inactive', death_timestamp = CURRENT_TIMESTAMP
            WHERE agent_number = ?
        ''', (agent_number,))
        
        # Get agent info for logging
        cursor.execute('SELECT human_name, role FROM agents WHERE agent_number = ?', (agent_number,))
        result = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        if result:
            human_name, role = result
            logger.info(f"💀 Agent died: {agent_number} ({human_name}) - {reason}")
            
            # Log to activity log
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO activity_log (agent_name, action_type, description, details)
                    VALUES (?, ?, ?, ?)
                ''', (f"{human_name} ({agent_number})", 'agent_death', 
                      f"Agent retired: {human_name}", reason))
                conn.commit()
                conn.close()
            except:
                pass
    
    def get_agent_by_number(self, agent_number: str) -> Optional[Dict]:
        """Get agent info by agent number"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, agent_number, human_name, role, specialization, 
                   personality_traits, birth_timestamp, death_timestamp, 
                   status, tasks_completed, tasks_failed
            FROM agents WHERE agent_number = ?
        ''', (agent_number,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'agent_number': row[1],
                'human_name': row[2],
                'role': row[3],
                'specialization': row[4],
                'personality_traits': row[5],
                'birth_timestamp': row[6],
                'death_timestamp': row[7],
                'status': row[8],
                'tasks_completed': row[9],
                'tasks_failed': row[10]
            }
        return None
    
    def get_all_active_agents(self) -> List[Dict]:
        """Get all active agents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, agent_number, human_name, role, specialization, 
                   personality_traits, birth_timestamp, tasks_completed, tasks_failed
            FROM agents WHERE status = 'active'
            ORDER BY birth_timestamp DESC
        ''')
        
        agents = []
        for row in cursor.fetchall():
            agents.append({
                'id': row[0],
                'agent_number': row[1],
                'human_name': row[2],
                'role': row[3],
                'specialization': row[4],
                'personality_traits': row[5],
                'birth_timestamp': row[6],
                'tasks_completed': row[7],
                'tasks_failed': row[8]
            })
        
        conn.close()
        return agents
    
    def update_agent_stats(self, agent_number: str, task_completed: bool = True):
        """Update agent task statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if task_completed:
            cursor.execute('''
                UPDATE agents 
                SET tasks_completed = tasks_completed + 1
                WHERE agent_number = ?
            ''', (agent_number,))
        else:
            cursor.execute('''
                UPDATE agents 
                SET tasks_failed = tasks_failed + 1
                WHERE agent_number = ?
            ''', (agent_number,))
        
        conn.commit()
        conn.close()
    
    def get_agent_lifetime(self, agent_number: str) -> str:
        """Get how long an agent has been alive"""
        agent = self.get_agent_by_number(agent_number)
        if not agent:
            return "Unknown"
        
        birth = datetime.fromisoformat(agent['birth_timestamp'])
        
        if agent['death_timestamp']:
            death = datetime.fromisoformat(agent['death_timestamp'])
            lifetime = death - birth
        else:
            lifetime = datetime.now() - birth
        
        days = lifetime.days
        hours = lifetime.seconds // 3600
        minutes = (lifetime.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

if __name__ == "__main__":
    print("🤖 Agent Identity System")
    print("=" * 60)
    
    system = AgentIdentitySystem()
    
    print("\n👶 Creating new agents...")
    agent1 = system.birth_agent('Autonomous AI Developer')
    agent2 = system.birth_agent('Backend Developer', 'female')
    agent3 = system.birth_agent('Frontend Developer', 'male')
    
    print("\n📋 Active agents:")
    agents = system.get_all_active_agents()
    for agent in agents:
        print(f"\n{agent['agent_number']}: {agent['human_name']}")
        print(f"  Role: {agent['role']}")
        print(f"  Personality: {agent['personality_traits']}")
        print(f"  Specialization: {agent['specialization']}")
        print(f"  Tasks: {agent['tasks_completed']} completed, {agent['tasks_failed']} failed")
    
    print("\n✅ Agent Identity System operational!")
