"""
Autonomous Task Generation System for Flowstate-AI
Advanced system that continuously analyzes project state and generates tasks autonomously.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import redis
from openai import OpenAI
from .error_handler import with_retry, with_error_handling, CircuitBreaker, log_error_to_db, default_fallback_value, CircuitBreakerOpenException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutonomousTaskSystem:
    """
    Advanced autonomous task generation system that continuously monitors
    project state and generates appropriate tasks for AI agents.
    """
    
    def __init__(self, db_path: str = "godmode-state.db", redis_host: str = "localhost"):
        """Initialize the autonomous task system."""
        self.db_path = Path(__file__).parent.parent / db_path
        self.redis = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
        self.client = OpenAI()
        self.openai_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60, expected_exception=Exception) # Adjust exception type as needed
        self.running = False
        self.task_generation_interval = 300  # 5 minutes
        
        # Task categories with priorities and generation rules
        self.task_categories = {
            "critical_bug": {
                "priority": 10,
                "auto_assign": True,
                "max_age_hours": 1
            },
            "security_vulnerability": {
                "priority": 9,
                "auto_assign": True,
                "max_age_hours": 4
            },
            "feature_development": {
                "priority": 7,
                "auto_assign": False,
                "max_age_hours": 168  # 1 week
            },
            "code_optimization": {
                "priority": 6,
                "auto_assign": False,
                "max_age_hours": 336  # 2 weeks
            },
            "documentation": {
                "priority": 5,
                "auto_assign": False,
                "max_age_hours": 720  # 1 month
            },
            "testing": {
                "priority": 8,
                "auto_assign": True,
                "max_age_hours": 48
            },
            "maintenance": {
                "priority": 4,
                "auto_assign": False,
                "max_age_hours": 1440  # 2 months
            }
        }
        
    @with_error_handling(fallback=default_fallback_value)
    def get_db_connection(self) -> sqlite3.Connection:

        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    @with_error_handling(fallback=default_fallback_value)
    async def start(self):
        """Start the autonomous task generation system."""
        self.running = True
        logger.info("Autonomous Task System started")
        
        try:
            await self.generation_cycle()
        except Exception as e:
            logger.error(f"Error in generation cycle: {str(e)}")
                
    @with_error_handling(fallback=default_fallback_value)
    async def stop(self):
        """Stop the autonomous task generation system."""
        self.running = False
        logger.info("Autonomous Task System stopped")
        
    @with_error_handling(fallback=default_fallback_value)
    async def generation_cycle(self):
        """Execute one cycle of task generation."""
        logger.info("Starting task generation cycle")
        
        # Analyze current project state
        project_state = await self.analyze_project_state()
        
        # Generate tasks based on analysis
        generated_tasks = await self.generate_tasks(project_state)
        
        # Prioritize and filter tasks
        prioritized_tasks = self.prioritize_tasks(generated_tasks)
        
        # Store tasks in database
        stored_count = await self.store_tasks(prioritized_tasks)
        
        # Auto-assign high-priority tasks
        assigned_count = await self.auto_assign_tasks()
        
        logger.info(f"Generation cycle complete: {stored_count} tasks created, {assigned_count} auto-assigned")
        
    @with_error_handling(fallback=default_fallback_value)
    @with_retry(expected_exception=sqlite3.OperationalError)
    async def analyze_project_state(self) -> Dict[str, Any]:
        """
        Analyze current project state to identify areas needing attention.
        
        Returns:
            Dictionary containing project state analysis
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'tasks': {},
            'agents': {},
            'system': {},
            'crm': {},
            'code_quality': {}
        }
        
        # Analyze tasks
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM tasks
            GROUP BY status
        """)
        analysis['tasks']['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM tasks
            WHERE status = 'pending'
            AND created_at < datetime('now', '-24 hours')
        """)
        analysis['tasks']['stale_pending'] = cursor.fetchone()['count']
        
        # Analyze agents
        cursor.execute("""
            SELECT agent_name, status, COUNT(*) as count
            FROM agents
            GROUP BY agent_name, status
        """)
        agent_data = cursor.fetchall()
        analysis['agents']['by_status'] = {}
        for row in agent_data:
            if row['agent_name'] not in analysis['agents']['by_status']:
                analysis['agents']['by_status'][row['agent_name']] = {}
            analysis['agents']['by_status'][row['agent_name']][row['status']] = row['count']
        
        # Analyze CRM data
        try:
            # Get contact count
            contact_count = 0
            for key in self.redis.scan_iter("contact:*"):
                contact_count += 1
            analysis['crm']['total_contacts'] = contact_count
            
            # Get deal count
            deal_count = 0
            for key in self.redis.scan_iter("deal:*"):
                deal_count += 1
            analysis['crm']['total_deals'] = deal_count
        except Exception as e:
            logger.error(f"Error analyzing CRM data: {str(e)}")
            analysis['crm']['error'] = str(e)
        
        conn.close()
        
        return analysis
        
    @with_error_handling(fallback=default_fallback_value)
    async def generate_tasks(self, project_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate tasks based on project state analysis using AI.
        
        Args:
            project_state: Current project state analysis
            
        Returns:
            List of generated task dictionaries
        """
        tasks = []
        
        # Rule-based task generation
        tasks.extend(self._generate_rule_based_tasks(project_state))
        
        # AI-powered task generation
        ai_tasks = await self._generate_ai_tasks(project_state)
        tasks.extend(ai_tasks)
        
        return tasks
        
    def _generate_rule_based_tasks(self, project_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tasks based on predefined rules."""
        tasks = []
        
        # Check for stale pending tasks
        stale_count = project_state.get('tasks', {}).get('stale_pending', 0)
        if stale_count > 5:
            tasks.append({
                'title': f'Review and update {stale_count} stale pending tasks',
                'description': 'Multiple tasks have been pending for over 24 hours. Review and update their status or reassign them.',
                'category': 'maintenance',
                'priority': 7,
                'auto_generated': True,
                'source': 'rule_based'
            })
        
        # Check for idle agents
        agents_by_status = project_state.get('agents', {}).get('by_status', {})
        for agent_name, statuses in agents_by_status.items():
            idle_count = statuses.get('idle', 0)
            if idle_count > 0:
                tasks.append({
                    'title': f'Assign tasks to idle agent: {agent_name}',
                    'description': f'Agent {agent_name} is currently idle and can be assigned new tasks.',
                    'category': 'maintenance',
                    'priority': 5,
                    'auto_generated': True,
                    'source': 'rule_based',
                    'assigned_agent': agent_name
                })
        
        # Check CRM metrics
        crm_data = project_state.get('crm', {})
        if crm_data.get('total_contacts', 0) > 100 and crm_data.get('total_deals', 0) < 10:
            tasks.append({
                'title': 'Analyze low deal conversion rate in CRM',
                'description': 'High number of contacts but low deal count. Investigate conversion bottlenecks.',
                'category': 'feature_development',
                'priority': 7,
                'auto_generated': True,
                'source': 'rule_based'
            })
        
        return tasks
        
    @with_error_handling(fallback=default_fallback_value)
    async def _generate_ai_tasks(self, project_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tasks using AI analysis."""
        try:
            # Prepare prompt for AI
            prompt = f"""
            Analyze the following project state and generate 3-5 high-value tasks that would improve the system:
            
            Project State:
            {json.dumps(project_state, indent=2)}
            
            Consider:
            1. System bottlenecks and inefficiencies
            2. Missing features or capabilities
            3. Code quality and technical debt
            4. User experience improvements
            5. Security and performance optimizations
            
            Return tasks in JSON format with the following structure:
            {{
                "tasks": [
                    {{
                        "title": "Task title",
                        "description": "Detailed description",
                        "category": "one of: critical_bug, security_vulnerability, feature_development, code_optimization, documentation, testing, maintenance",
                        "priority": 1-10,
                        "estimated_hours": 1-40
                    }}
                ]
            }}
            """
            
            response = await self.openai_circuit_breaker(self.client.chat.completions.create)(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are an expert software project manager and technical architect."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            
            # Extract JSON from response
            if "```json" in ai_response:
                json_start = ai_response.find("```json") + 7
                json_end = ai_response.find("```", json_start)
                ai_response = ai_response[json_start:json_end].strip()
            elif "```" in ai_response:
                json_start = ai_response.find("```") + 3
                json_end = ai_response.find("```", json_start)
                ai_response = ai_response[json_start:json_end].strip()
            
            parsed_response = json.loads(ai_response)
            ai_tasks = parsed_response.get('tasks', [])
            
            # Add metadata
            for task in ai_tasks:
                task['auto_generated'] = True
                task['source'] = 'ai_powered'
            
            logger.info(f"Generated {len(ai_tasks)} AI-powered tasks")
            return ai_tasks
            
        except Exception as e:
            logger.error(f"Error generating AI tasks: {str(e)}")
            return []
            
    def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize and filter tasks based on category rules and current workload.
        
        Args:
            tasks: List of generated tasks
            
        Returns:
            Prioritized and filtered task list
        """
        # Add priority scores based on category
        for task in tasks:
            category = task.get('category', 'maintenance')
            category_config = self.task_categories.get(category, {})
            task['final_priority'] = task.get('priority', 5) + category_config.get('priority', 5)
        
        # Sort by final priority
        tasks.sort(key=lambda t: t['final_priority'], reverse=True)
        
        # Remove duplicates (similar titles)
        unique_tasks = []
        seen_titles = set()
        for task in tasks:
            title_lower = task['title'].lower()
            if title_lower not in seen_titles:
                unique_tasks.append(task)
                seen_titles.add(title_lower)
        
        # Limit to top 10 tasks per cycle
        return unique_tasks[:10]
        
    @with_error_handling(fallback=default_fallback_value)
    @with_retry(expected_exception=sqlite3.OperationalError)
    async def store_tasks(self, tasks: List[Dict[str, Any]]) -> int:

        """
        Store generated tasks in the database.
        
        Args:
            tasks: List of tasks to store
            
        Returns:
            Number of tasks successfully stored
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        stored_count = 0
        
        for task in tasks:
            try:
                cursor.execute("""
                    INSERT INTO tasks (
                        title, description, status, priority, category,
                        auto_generated, source, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task['title'],
                    task.get('description', ''),
                    'pending',
                    task.get('final_priority', task.get('priority', 5)),
                    task.get('category', 'maintenance'),
                    1 if task.get('auto_generated', False) else 0,
                    task.get('source', 'unknown'),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                stored_count += 1
            except Exception as e:
                logger.error(f"Error storing task '{task['title']}': {str(e)}")
        
        conn.commit()
        conn.close()
        
        return stored_count
        
    @with_error_handling(fallback=default_fallback_value)
    @with_retry(expected_exception=sqlite3.OperationalError)
    async def auto_assign_tasks(self) -> int:

        """
        Automatically assign high-priority tasks to available agents.
        
        Returns:
            Number of tasks auto-assigned
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Get high-priority pending tasks
        cursor.execute("""
            SELECT id, title, category, priority
            FROM tasks
            WHERE status = 'pending'
            AND priority >= 8
            ORDER BY priority DESC, created_at ASC
            LIMIT 5
        """)
        high_priority_tasks = cursor.fetchall()
        
        # Get available agents
        cursor.execute("""
            SELECT agent_name, status
            FROM agents
            WHERE status IN ('idle', 'available')
            LIMIT 5
        """)
        available_agents = cursor.fetchall()
        
        assigned_count = 0
        
        for task in high_priority_tasks:
            if assigned_count >= len(available_agents):
                break
                
            agent = available_agents[assigned_count]
            
            try:
                cursor.execute("""
                    UPDATE tasks
                    SET status = 'assigned',
                        assigned_agent = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (agent['agent_name'], datetime.now().isoformat(), task['id']))
                
                logger.info(f"Auto-assigned task '{task['title']}' to agent {agent['agent_name']}")
                assigned_count += 1
            except Exception as e:
                logger.error(f"Error auto-assigning task {task['id']}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return assigned_count
        
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about task generation."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Get auto-generated task count
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM tasks
            WHERE auto_generated = 1
        """)
        auto_generated_count = cursor.fetchone()['count']
        
        # Get tasks by source
        cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM tasks
            WHERE auto_generated = 1
            GROUP BY source
        """)
        by_source = {row['source']: row['count'] for row in cursor.fetchall()}
        
        # Get recent generation activity
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM tasks
            WHERE auto_generated = 1
            AND created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        recent_activity = {row['date']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_auto_generated': auto_generated_count,
            'by_source': by_source,
            'recent_activity_7_days': recent_activity,
            'system_running': self.running,
            'generation_interval_seconds': self.task_generation_interval
        }


async def main():
    """Main function to run the autonomous task system."""
    system = AutonomousTaskSystem()
    
    try:
        await system.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await system.stop()


if __name__ == "__main__":
    asyncio.run(main())
