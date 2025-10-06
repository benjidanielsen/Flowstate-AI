#!/usr/bin/env python3
"""
🧠 DECISION ENGINE
⚡ Handles task prioritization, resource allocation, and strategic decisions
🎯 Mission: Make intelligent decisions to optimize system performance
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DecisionEngine')

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"

class DecisionEngine:
    """Makes intelligent decisions for task prioritization and resource allocation"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.client = OpenAI()
        self.decision_history = []
        
    def analyze_task_complexity(self, task: Dict) -> int:
        """Analyze task complexity (1-10 scale)"""
        complexity_score = 5  # Default
        
        description = task.get('description', '').lower()
        
        # Increase complexity for certain keywords
        if any(word in description for word in ['architecture', 'system', 'infrastructure']):
            complexity_score += 2
        if any(word in description for word in ['ai', 'machine learning', 'algorithm']):
            complexity_score += 2
        if any(word in description for word in ['security', 'authentication', 'encryption']):
            complexity_score += 1
        if any(word in description for word in ['database', 'migration', 'schema']):
            complexity_score += 1
        
        # Decrease complexity for simpler tasks
        if any(word in description for word in ['documentation', 'readme', 'comment']):
            complexity_score -= 1
        if any(word in description for word in ['fix typo', 'update text', 'rename']):
            complexity_score -= 2
        
        return min(max(complexity_score, 1), 10)
    
    def estimate_task_duration(self, task: Dict) -> int:
        """Estimate task duration in minutes"""
        complexity = self.analyze_task_complexity(task)
        
        # Base duration on complexity
        base_duration = complexity * 15  # 15 minutes per complexity point
        
        # Adjust based on task category
        category = task.get('category', '').lower()
        multipliers = {
            'architecture': 1.5,
            'security': 1.3,
            'testing': 1.2,
            'documentation': 0.8,
            'refactoring': 1.1,
            'bugfix': 0.9
        }
        
        multiplier = multipliers.get(category, 1.0)
        return int(base_duration * multiplier)
    
    def calculate_task_priority(self, task: Dict) -> int:
        """Calculate dynamic priority based on multiple factors"""
        base_priority = task.get('priority', 5)
        
        # Factor 1: Complexity (higher complexity = slightly higher priority)
        complexity = self.analyze_task_complexity(task)
        complexity_bonus = complexity * 0.5
        
        # Factor 2: Dependencies (tasks with no dependencies get priority)
        dependencies = task.get('dependencies', [])
        dependency_penalty = len(dependencies) * 2
        
        # Factor 3: Age (older tasks get priority boost)
        created_at = task.get('created_at', datetime.now().isoformat())
        # Simplified age calculation
        age_bonus = 0  # Could be enhanced with actual date parsing
        
        # Factor 4: Category urgency
        category = task.get('category', '').lower()
        urgency_bonus = {
            'security': 3,
            'bugfix': 2,
            'performance': 2,
            'architecture': 1,
            'feature': 0,
            'documentation': -1
        }.get(category, 0)
        
        final_priority = base_priority + complexity_bonus - dependency_penalty + age_bonus + urgency_bonus
        
        return int(min(max(final_priority, 1), 10))
    
    def select_best_agent_for_task(self, task: Dict) -> str:
        """Select the most appropriate agent for a task"""
        description = task.get('description', '').lower()
        category = task.get('category', '').lower()
        
        # Agent specializations
        agent_keywords = {
            'Backend Developer': ['backend', 'api', 'server', 'database', 'flask', 'python'],
            'Frontend Developer': ['frontend', 'ui', 'react', 'component', 'css', 'javascript'],
            'Database Agent': ['database', 'schema', 'migration', 'query', 'sql', 'index'],
            'DevOps Agent': ['deploy', 'docker', 'kubernetes', 'ci/cd', 'infrastructure'],
            'Testing Agent': ['test', 'testing', 'qa', 'coverage', 'unit test', 'integration'],
            'Security Agent': ['security', 'authentication', 'authorization', 'vulnerability'],
            'Documentation Agent': ['documentation', 'readme', 'guide', 'tutorial', 'docs']
        }
        
        # Score each agent
        agent_scores = {}
        for agent, keywords in agent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in description or keyword in category)
            agent_scores[agent] = score
        
        # Get best match
        if agent_scores:
            best_agent = max(agent_scores, key=agent_scores.get)
            if agent_scores[best_agent] > 0:
                return best_agent
        
        # Default to Autonomous AI Developer
        return 'Autonomous AI Developer'
    
    def make_resource_allocation_decision(self) -> Dict:
        """Decide how to allocate resources across tasks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get pending tasks
        cursor.execute('''
            SELECT id, title, description, priority, assigned_to, created_at
            FROM tasks
            WHERE status = 'pending'
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
        
        # Analyze and prioritize
        task_analysis = []
        for task in tasks:
            analysis = {
                'task_id': task['id'],
                'title': task['title'],
                'calculated_priority': self.calculate_task_priority(task),
                'complexity': self.analyze_task_complexity(task),
                'estimated_duration': self.estimate_task_duration(task),
                'recommended_agent': self.select_best_agent_for_task(task)
            }
            task_analysis.append(analysis)
        
        # Sort by calculated priority
        task_analysis.sort(key=lambda x: x['calculated_priority'], reverse=True)
        
        decision = {
            'timestamp': datetime.now().isoformat(),
            'total_pending_tasks': len(tasks),
            'prioritized_tasks': task_analysis[:10],  # Top 10
            'recommendation': 'Focus on high-priority tasks first'
        }
        
        self.decision_history.append(decision)
        
        return decision
    
    def should_generate_new_tasks(self) -> bool:
        """Decide if new tasks should be generated"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
        pending_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Generate new tasks if queue is low
        threshold = 10
        return pending_count < threshold
    
    def decide_on_system_action(self, context: str) -> Dict:
        """Make a high-level system decision using AI"""
        logger.info(f"🤔 Making decision on: {context}")
        
        # Get current system state
        resource_allocation = self.make_resource_allocation_decision()
        
        prompt = f"""You are the Decision Engine for Flowstate-AI autonomous development system.

Context: {context}

Current System State:
- Pending tasks: {resource_allocation['total_pending_tasks']}
- Top priority task: {resource_allocation['prioritized_tasks'][0]['title'] if resource_allocation['prioritized_tasks'] else 'None'}

Make a strategic decision on what the system should do next. Consider:
1. Should we continue with current tasks or reprioritize?
2. Do we need to generate new tasks?
3. Should we optimize any processes?
4. Are there any bottlenecks to address?

Respond in JSON format:
{{
    "action": "continue/reprioritize/generate_tasks/optimize",
    "reasoning": "brief explanation",
    "specific_steps": ["step 1", "step 2", ...]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a strategic decision-making AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            decision_text = response.choices[0].message.content
            
            # Parse JSON
            if decision_text.startswith("```json"):
                decision_text = decision_text.split("```json")[1].split("```")[0].strip()
            elif decision_text.startswith("```"):
                decision_text = decision_text.split("```")[1].split("```")[0].strip()
            
            decision = json.loads(decision_text)
            decision['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"✅ Decision made: {decision['action']}")
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ Decision making failed: {e}")
            return {
                'action': 'continue',
                'reasoning': 'Error in decision making, defaulting to continue',
                'specific_steps': ['Continue with current tasks']
            }

if __name__ == "__main__":
    print("🧠 Decision Engine")
    print("=" * 60)
    
    engine = DecisionEngine()
    
    print("\n📊 Analyzing resource allocation...")
    allocation = engine.make_resource_allocation_decision()
    print(f"Total pending tasks: {allocation['total_pending_tasks']}")
    print(f"\nTop 5 prioritized tasks:")
    for i, task in enumerate(allocation['prioritized_tasks'][:5], 1):
        print(f"{i}. {task['title']}")
        print(f"   Priority: {task['calculated_priority']}, Complexity: {task['complexity']}")
        print(f"   Duration: {task['estimated_duration']} min, Agent: {task['recommended_agent']}")
    
    print("\n🤔 Making strategic decision...")
    decision = engine.decide_on_system_action("System startup - what should we focus on?")
    print(f"Action: {decision['action']}")
    print(f"Reasoning: {decision['reasoning']}")
    
    print("\n✅ Decision Engine operational!")
