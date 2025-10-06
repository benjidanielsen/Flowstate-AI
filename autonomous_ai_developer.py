#!/usr/bin/env python3
"""
🤖 AUTONOMOUS AI DEVELOPER
⚡ Self-operating AI agent that works 24/7 without human intervention
🎯 Mission: Continuously develop the Flowstate-AI system autonomously
"""

import os
import sys
import time
import json
import sqlite3
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# Setup
PROJECT_ROOT = Path(__file__).parent.absolute()
DB_PATH = PROJECT_ROOT / "godmode-state.db"
LOG_PATH = PROJECT_ROOT / "godmode-logs" / "autonomous-ai-developer.log"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('AutonomousAIDeveloper')

# OpenAI client (API key is already set in environment)
client = OpenAI()

class AutonomousAIDeveloper:
    """Autonomous AI Developer that works continuously"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.db_path = DB_PATH
        self.running = True
        self.agent_name = "Autonomous AI Developer"
        logger.info("🤖 Autonomous AI Developer initialized")
        
    def get_next_task(self):
        """Get the next pending task from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, priority, assigned_to
            FROM tasks
            WHERE status = 'pending'
            ORDER BY priority DESC, created_at ASC
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'assigned_to': row[4]
            }
        return None
    
    def mark_task_in_progress(self, task_id):
        """Mark a task as in progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks
            SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (task_id,))
        conn.commit()
        conn.close()
        logger.info(f"📝 Task #{task_id} marked as in progress")
    
    def complete_task(self, task_id, result):
        """Mark a task as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (task_id,))
        conn.commit()
        conn.close()
        logger.info(f"✅ Task #{task_id} completed: {result}")
    
    def fail_task(self, task_id, error):
        """Mark a task as failed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks
            SET status = 'failed', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (task_id,))
        conn.commit()
        conn.close()
        logger.error(f"❌ Task #{task_id} failed: {error}")
    
    def update_heartbeat(self, current_task=None):
        """Update agent heartbeat in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO agent_status (agent_name, status, last_heartbeat, current_task)
            VALUES (?, 'active', CURRENT_TIMESTAMP, ?)
        ''', (self.agent_name, current_task))
        conn.commit()
        conn.close()
    
    def generate_code_with_ai(self, task_title, task_description):
        """Use OpenAI to generate code for a task"""
        try:
            prompt = f"""You are an expert Python/JavaScript developer working on the Flowstate-AI project.

Task: {task_title}
Description: {task_description}

Generate the necessary code to complete this task. Provide:
1. File path (relative to project root)
2. Complete file content
3. Brief explanation

Respond in JSON format:
{{
    "file_path": "path/to/file.py",
    "content": "complete file content here",
    "explanation": "brief explanation"
}}"""

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are an expert software developer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            # Try to parse JSON response
            if result.startswith("```json"):
                result = result.split("```json")[1].split("```")[0].strip()
            elif result.startswith("```"):
                result = result.split("```")[1].split("```")[0].strip()
            
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"❌ AI code generation failed: {e}")
            return None
    
    def write_file(self, file_path, content):
        """Write generated code to a file"""
        try:
            full_path = self.project_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"📝 File written: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to write file {file_path}: {e}")
            return False
    
    def commit_and_push(self, message):
        """Commit and push changes to GitHub"""
        try:
            # Configure git if not already done
            subprocess.run(['git', 'config', 'user.name', 'Autonomous AI Developer'], 
                         cwd=self.project_root, check=False)
            subprocess.run(['git', 'config', 'user.email', 'ai@flowstate.dev'], 
                         cwd=self.project_root, check=False)
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], cwd=self.project_root, check=True)
            
            # Commit
            subprocess.run(['git', 'commit', '-m', message], 
                         cwd=self.project_root, check=True)
            
            # Push
            subprocess.run(['git', 'push'], cwd=self.project_root, check=True)
            
            logger.info(f"✅ Changes committed and pushed: {message}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git operation failed: {e}")
            return False
    
    def execute_task(self, task):
        """Execute a task using AI"""
        logger.info(f"🚀 Executing task #{task['id']}: {task['title']}")
        
        self.mark_task_in_progress(task['id'])
        self.update_heartbeat(f"Working on: {task['title']}")
        
        try:
            # Generate code using AI
            logger.info("🤖 Generating code with AI...")
            result = self.generate_code_with_ai(task['title'], task['description'])
            
            if not result:
                self.fail_task(task['id'], "AI code generation failed")
                return False
            
            # Write the generated code
            logger.info(f"📝 Writing file: {result['file_path']}")
            if not self.write_file(result['file_path'], result['content']):
                self.fail_task(task['id'], "Failed to write file")
                return False
            
            # Commit and push
            commit_message = f"AI: {task['title']}\n\n{result['explanation']}"
            logger.info("📤 Committing to GitHub...")
            self.commit_and_push(commit_message)
            
            # Mark task as completed
            self.complete_task(task['id'], result['explanation'])
            
            logger.info(f"✅ Task #{task['id']} completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            self.fail_task(task['id'], str(e))
            return False
    
    def run(self):
        """Main execution loop - runs forever"""
        logger.info("🚀 Autonomous AI Developer starting...")
        logger.info("♾️  Running in continuous mode (will never stop)")
        logger.info(f"📁 Project: {self.project_root}")
        logger.info(f"🗄️  Database: {self.db_path}")
        
        iteration = 0
        
        while self.running:
            iteration += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 Iteration #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'='*60}")
            
            # Update heartbeat
            self.update_heartbeat("Checking for tasks...")
            
            # Get next task
            task = self.get_next_task()
            
            if task:
                logger.info(f"📋 Found task: #{task['id']} - {task['title']}")
                self.execute_task(task)
            else:
                logger.info("💤 No pending tasks. Waiting...")
                time.sleep(30)  # Wait 30 seconds before checking again
            
            # Small delay between iterations
            time.sleep(5)
        
        logger.info("🛑 Autonomous AI Developer stopped")

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🤖 AUTONOMOUS AI DEVELOPER")
    logger.info("=" * 70)
    logger.info("")
    
    developer = AutonomousAIDeveloper()
    
    try:
        developer.run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Received stop signal")
        developer.running = False
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
