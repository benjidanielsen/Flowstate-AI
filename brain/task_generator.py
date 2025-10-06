"""
Automatic Task Generation System for Flowstate-AI
Generates and prioritizes tasks for AI agents based on project goals and system state.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from openai import OpenAI
import sqlite3

class AutomaticTaskGenerator:
    """
    Autonomous task generation system that analyzes project state and creates tasks.
    """
    
    def __init__(self, db_path: str = "godmode-state.db"):
        """
        Initialize the task generator.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = Path(__file__).parent.parent / db_path
        self.client = OpenAI()
        self.log_file = Path(__file__).parent.parent / "logs" / "task_generator.log"
        
        # Task generation rules and priorities
        self.task_rules = {
            "code_quality": {
                "priority": 8,
                "triggers": ["test_coverage_low", "code_duplication", "missing_documentation"],
                "templates": [
                    "Increase test coverage for {module} to at least 80%",
                    "Refactor duplicate code in {module}",
                    "Add comprehensive documentation for {module}"
                ]
            },
            "feature_development": {
                "priority": 7,
                "triggers": ["feature_request", "roadmap_item"],
                "templates": [
                    "Implement {feature_name} feature",
                    "Add {functionality} to {module}",
                    "Develop {component} integration"
                ]
            },
            "bug_fixing": {
                "priority": 9,
                "triggers": ["bug_report", "error_detected", "test_failure"],
                "templates": [
                    "Fix bug: {bug_description}",
                    "Resolve error in {module}: {error_message}",
                    "Debug and fix failing test: {test_name}"
                ]
            },
            "optimization": {
                "priority": 6,
                "triggers": ["performance_issue", "resource_constraint"],
                "templates": [
                    "Optimize {module} performance",
                    "Reduce resource usage in {component}",
                    "Improve {process} efficiency"
                ]
            },
            "maintenance": {
                "priority": 5,
                "triggers": ["dependency_update", "security_patch", "code_cleanup"],
                "templates": [
                    "Update {dependency} to latest version",
                    "Apply security patch for {vulnerability}",
                    "Clean up deprecated code in {module}"
                ]
            },
            "crm_automation": {
                "priority": 7,
                "triggers": ["new_leads", "stale_deals", "customer_feedback"],
                "templates": [
                    "Process and qualify {count} new leads",
                    "Follow up on {count} stale deals",
                    "Analyze and respond to customer feedback"
                ]
            }
        }
    
    def log(self, message: str):
        """Log task generator activity."""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] Task Generator: {message}\n"
        print(log_entry.strip())
        
        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def analyze_project_state(self) -> Dict[str, Any]:
        """
        Analyze the current project state to identify areas needing attention.
        
        Returns:
            Dictionary with project state analysis
        """
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "issues": [],
            "opportunities": [],
            "metrics": {}
        }
        
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for pending tasks
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
            pending_tasks = cursor.fetchone()[0]
            analysis["metrics"]["pending_tasks"] = pending_tasks
            
            # Check for failed tasks
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'failed'")
            failed_tasks = cursor.fetchone()[0]
            analysis["metrics"]["failed_tasks"] = failed_tasks
            
            if failed_tasks > 0:
                analysis["issues"].append({
                    "type": "failed_tasks",
                    "severity": "high",
                    "count": failed_tasks,
                    "description": f"{failed_tasks} tasks have failed and need investigation"
                })
            
            # Check for stale tasks (created more than 7 days ago and still pending)
            cursor.execute("""
                SELECT COUNT(*) FROM tasks 
                WHERE status = 'pending' 
                AND datetime(created_at) < datetime('now', '-7 days')
            """)
            stale_tasks = cursor.fetchone()[0]
            analysis["metrics"]["stale_tasks"] = stale_tasks
            
            if stale_tasks > 0:
                analysis["issues"].append({
                    "type": "stale_tasks",
                    "severity": "medium",
                    "count": stale_tasks,
                    "description": f"{stale_tasks} tasks have been pending for over 7 days"
                })
            
            conn.close()
            
        except Exception as e:
            self.log(f"Error analyzing project state: {e}")
            analysis["issues"].append({
                "type": "analysis_error",
                "severity": "low",
                "description": str(e)
            })
        
        # Identify opportunities
        if pending_tasks < 5:
            analysis["opportunities"].append({
                "type": "capacity_available",
                "description": "Low pending task count suggests capacity for new initiatives"
            })
        
        return analysis
    
    def generate_tasks_from_analysis(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate tasks based on project state analysis.
        
        Args:
            analysis: Project state analysis
            
        Returns:
            List of generated tasks
        """
        generated_tasks = []
        
        # Generate tasks for identified issues
        for issue in analysis.get("issues", []):
            issue_type = issue["type"]
            
            if issue_type == "failed_tasks":
                generated_tasks.append({
                    "title": f"Investigate and resolve {issue['count']} failed tasks",
                    "description": issue["description"],
                    "priority": 9,
                    "category": "bug_fixing",
                    "estimated_hours": issue["count"] * 0.5
                })
            
            elif issue_type == "stale_tasks":
                generated_tasks.append({
                    "title": f"Review and update {issue['count']} stale tasks",
                    "description": issue["description"],
                    "priority": 6,
                    "category": "maintenance",
                    "estimated_hours": issue["count"] * 0.25
                })
        
        # Generate tasks for opportunities
        for opportunity in analysis.get("opportunities", []):
            if opportunity["type"] == "capacity_available":
                generated_tasks.append({
                    "title": "Identify and prioritize new development initiatives",
                    "description": opportunity["description"],
                    "priority": 7,
                    "category": "feature_development",
                    "estimated_hours": 2.0
                })
        
        return generated_tasks
    
    def generate_tasks_with_ai(self, context: Dict[str, Any], count: int = 5) -> List[Dict[str, Any]]:
        """
        Use AI to generate creative and contextually relevant tasks.
        
        Args:
            context: Context information for task generation
            count: Number of tasks to generate
            
        Returns:
            List of AI-generated tasks
        """
        try:
            prompt = f"""
            Based on the following context about the Flowstate-AI project, generate {count} actionable tasks that would improve the system.
            
            Context:
            {json.dumps(context, indent=2)}
            
            Generate tasks that are:
            1. Specific and actionable
            2. Aligned with project goals (autonomous AI agents, CRM automation, intelligent decision-making)
            3. Prioritized appropriately (1-10 scale, 10 being highest)
            4. Realistic in scope (1-8 hours of work)
            
            Return the tasks as a JSON array with the following structure:
            [
                {{
                    "title": "Task title",
                    "description": "Detailed description",
                    "priority": 7,
                    "category": "feature_development|bug_fixing|optimization|maintenance|crm_automation",
                    "estimated_hours": 3.0
                }}
            ]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are an expert project manager for AI development projects. Generate practical, high-value tasks."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            tasks = result.get("tasks", [])
            
            self.log(f"Generated {len(tasks)} tasks using AI")
            return tasks
            
        except Exception as e:
            self.log(f"Error generating tasks with AI: {e}")
            return []
    
    def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize tasks based on multiple factors.
        
        Args:
            tasks: List of tasks to prioritize
            
        Returns:
            Sorted list of tasks by priority
        """
        def calculate_priority_score(task):
            base_priority = task.get("priority", 5)
            
            # Adjust based on category
            category = task.get("category", "")
            category_weight = self.task_rules.get(category, {}).get("priority", 5) / 10
            
            # Adjust based on estimated effort (prefer quick wins)
            estimated_hours = task.get("estimated_hours", 4.0)
            effort_weight = 1.0 / (1.0 + estimated_hours / 10.0)
            
            # Calculate final score
            score = base_priority * (0.6 + 0.2 * category_weight + 0.2 * effort_weight)
            return score
        
        # Sort tasks by priority score (descending)
        sorted_tasks = sorted(tasks, key=calculate_priority_score, reverse=True)
        
        return sorted_tasks
    
    def create_task_in_db(self, task: Dict[str, Any]) -> Optional[int]:
        """
        Create a task in the database.
        
        Args:
            task: Task information
            
        Returns:
            Task ID if successful, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tasks (title, description, priority, status, created_at)
                VALUES (?, ?, ?, 'pending', datetime('now'))
            """, (
                task.get("title", "Untitled Task"),
                task.get("description", ""),
                task.get("priority", 5)
            ))
            
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.log(f"Created task {task_id}: {task.get('title')}")
            return task_id
            
        except Exception as e:
            self.log(f"Error creating task in database: {e}")
            return None
    
    def run_task_generation_cycle(self):
        """Run a complete task generation cycle."""
        self.log("=" * 60)
        self.log("Starting automatic task generation cycle")
        self.log("=" * 60)
        
        # Step 1: Analyze project state
        self.log("Step 1: Analyzing project state...")
        analysis = self.analyze_project_state()
        self.log(f"Analysis complete: {len(analysis['issues'])} issues, {len(analysis['opportunities'])} opportunities")
        
        # Step 2: Generate tasks from analysis
        self.log("Step 2: Generating tasks from analysis...")
        rule_based_tasks = self.generate_tasks_from_analysis(analysis)
        self.log(f"Generated {len(rule_based_tasks)} rule-based tasks")
        
        # Step 3: Generate AI-powered tasks
        self.log("Step 3: Generating AI-powered tasks...")
        ai_tasks = self.generate_tasks_with_ai(analysis, count=3)
        self.log(f"Generated {len(ai_tasks)} AI-powered tasks")
        
        # Step 4: Combine and prioritize tasks
        all_tasks = rule_based_tasks + ai_tasks
        self.log("Step 4: Prioritizing tasks...")
        prioritized_tasks = self.prioritize_tasks(all_tasks)
        
        # Step 5: Create tasks in database
        self.log("Step 5: Creating tasks in database...")
        created_count = 0
        for task in prioritized_tasks[:10]:  # Limit to top 10 tasks
            if self.create_task_in_db(task):
                created_count += 1
        
        self.log(f"Successfully created {created_count} tasks")
        self.log("=" * 60)
        self.log("Task generation cycle completed")
        self.log("=" * 60)

def main():
    """Main function to run the task generator."""
    generator = AutomaticTaskGenerator()
    generator.run_task_generation_cycle()

if __name__ == "__main__":
    main()
