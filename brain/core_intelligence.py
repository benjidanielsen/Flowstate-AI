#!/usr/bin/env python3
"""
🧠 CORE INTELLIGENCE MODULE
⚡ Central decision-making system that coordinates all AI agents
🎯 Mission: Be the brain that orchestrates autonomous development
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"

class CoreIntelligence:
    """The brain of the Flowstate-AI system"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.client = OpenAI()
        self.memory = {}
        self.decision_log = []
        
    def analyze_system_state(self) -> Dict:
        """Analyze the current state of the entire system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get task statistics
        cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
        task_stats = dict(cursor.fetchall())
        
        # Get agent status
        cursor.execute("SELECT agent_name, status FROM agent_status")
        agent_status = dict(cursor.fetchall())
        
        # Get CRM pipeline stats
        cursor.execute("SELECT stage, COUNT(*) FROM crm_pipeline GROUP BY stage")
        pipeline_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'tasks': task_stats,
            'agents': agent_status,
            'pipeline': pipeline_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def make_strategic_decision(self, context: str) -> Dict:
        """Make a strategic decision using AI"""
        system_state = self.analyze_system_state()
        
        prompt = f"""You are the Core Intelligence of Flowstate-AI, an autonomous development system.

Current System State:
{json.dumps(system_state, indent=2)}

Context: {context}

Based on the current state, what strategic decision should be made? Consider:
1. Task prioritization
2. Resource allocation
3. System optimization opportunities
4. Potential bottlenecks
5. Next steps for improvement

Respond in JSON format:
{{
    "decision": "brief description of decision",
    "reasoning": "why this decision makes sense",
    "actions": ["action 1", "action 2", ...],
    "priority": "high/medium/low"
}}"""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a strategic AI system architect."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        decision_text = response.choices[0].message.content
        
        # Parse JSON response
        if decision_text.startswith("```json"):
            decision_text = decision_text.split("```json")[1].split("```")[0].strip()
        elif decision_text.startswith("```"):
            decision_text = decision_text.split("```")[1].split("```")[0].strip()
        
        decision = json.loads(decision_text)
        
        # Log the decision
        self.decision_log.append({
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'decision': decision
        })
        
        return decision
    
    def prioritize_tasks(self) -> List[Dict]:
        """Intelligently prioritize tasks based on multiple factors"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, priority, assigned_to, created_at
            FROM tasks
            WHERE status = 'pending'
            ORDER BY priority DESC, created_at ASC
        ''')
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'assigned_to': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        
        # Use AI to re-prioritize if needed
        if len(tasks) > 10:
            decision = self.make_strategic_decision(
                f"We have {len(tasks)} pending tasks. Should we adjust priorities?"
            )
            # Implement priority adjustment logic here
        
        return tasks
    
    def allocate_resources(self, task: Dict) -> str:
        """Determine which agent should handle a task"""
        # Simple allocation based on task category
        category_to_agent = {
            'architecture': 'Autonomous AI Developer',
            'backend': 'Backend Developer',
            'frontend': 'Frontend Developer',
            'database': 'Database Agent',
            'devops': 'DevOps Agent',
            'testing': 'Testing Agent',
            'documentation': 'Documentation Agent',
            'security': 'Security Agent'
        }
        
        # Get task category from description or use AI
        for category, agent in category_to_agent.items():
            if category in task.get('description', '').lower():
                return agent
        
        return 'Autonomous AI Developer'  # Default
    
    def learn_from_outcome(self, task_id: int, success: bool, feedback: str):
        """Learn from task outcomes to improve future decisions"""
        learning = {
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'success': success,
            'feedback': feedback
        }
        
        # Store in memory
        if 'learnings' not in self.memory:
            self.memory['learnings'] = []
        self.memory['learnings'].append(learning)
        
        # Persist to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_learnings (task_id, success, feedback, learned_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (task_id, 1 if success else 0, feedback))
        
        conn.commit()
        conn.close()
    
    def generate_improvement_tasks(self) -> List[Dict]:
        """Automatically generate tasks for system improvement"""
        system_state = self.analyze_system_state()
        
        prompt = f"""Based on this system state, generate 5 improvement tasks:

{json.dumps(system_state, indent=2)}

Focus on:
- Code refactoring opportunities
- Performance optimizations
- Documentation improvements
- Testing gaps
- Security enhancements

Respond in JSON format:
{{
    "tasks": [
        {{
            "title": "task title",
            "description": "detailed description",
            "priority": 1-10,
            "category": "category name"
        }}
    ]
}}"""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a system improvement specialist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1500
        )
        
        result_text = response.choices[0].message.content
        
        # Parse JSON
        if result_text.startswith("```json"):
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif result_text.startswith("```"):
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        return result.get('tasks', [])
    
    def ensure_continuous_work(self):
        """Ensure there's always work to do - generate tasks if queue is low"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
        pending_count = cursor.fetchone()[0]
        
        conn.close()
        
        # If less than 10 pending tasks, generate more
        if pending_count < 10:
            new_tasks = self.generate_improvement_tasks()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for task in new_tasks:
                cursor.execute('''
                    INSERT INTO tasks (title, description, priority, assigned_to, status)
                    VALUES (?, ?, ?, ?, 'pending')
                ''', (
                    task['title'],
                    task['description'],
                    task['priority'],
                    self.allocate_resources(task)
                ))
            
            conn.commit()
            conn.close()
            
            return len(new_tasks)
        
        return 0

if __name__ == "__main__":
    print("🧠 Core Intelligence Module")
    print("=" * 60)
    
    brain = CoreIntelligence()
    
    print("\n📊 Analyzing system state...")
    state = brain.analyze_system_state()
    print(json.dumps(state, indent=2))
    
    print("\n🎯 Making strategic decision...")
    decision = brain.make_strategic_decision("System startup - what should we focus on?")
    print(json.dumps(decision, indent=2))
    
    print("\n✅ Ensuring continuous work...")
    new_tasks = brain.ensure_continuous_work()
    print(f"Generated {new_tasks} new improvement tasks")
    
    print("\n🧠 Core Intelligence operational!")
