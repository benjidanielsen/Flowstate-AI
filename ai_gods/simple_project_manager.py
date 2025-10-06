#!/usr/bin/env python3
"""
🤖 SIMPLE PROJECT MANAGER AI
⚡ Lightweight, working version for immediate deployment
🎯 Mission: Coordinate AI agents and manage the Frazer Method CRM pipeline
"""

import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/simple-project-manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('SimpleProjectManager')

class SimpleProjectManager:
    """Simplified Project Manager AI for immediate deployment"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.db_path = self.project_root / "godmode-state.db"
        self.init_database()
        logger.info("🤖 Simple Project Manager AI initialized")
        
    def init_database(self):
        """Initialize the SQLite database for task management"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                priority INTEGER DEFAULT 0,
                assigned_to TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        # Create agents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'idle',
                capabilities TEXT,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create crm_pipeline table for Frazer Method
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crm_pipeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_name TEXT NOT NULL,
                lead_email TEXT,
                lead_phone TEXT,
                stage TEXT DEFAULT 'lead_generation',
                score INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
    
    def register_agent(self, name: str, agent_type: str, capabilities: List[str]):
        """Register a new AI agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO agents (name, type, capabilities, status, last_active)
                VALUES (?, ?, ?, 'active', CURRENT_TIMESTAMP)
            ''', (name, agent_type, json.dumps(capabilities)))
            conn.commit()
            logger.info(f"✅ Agent registered: {name} ({agent_type})")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to register agent {name}: {e}")
            return False
        finally:
            conn.close()
    
    def create_task(self, title: str, description: str = "", priority: int = 0, assigned_to: str = None):
        """Create a new task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO tasks (title, description, priority, assigned_to, status)
                VALUES (?, ?, ?, ?, 'pending')
            ''', (title, description, priority, assigned_to))
            conn.commit()
            task_id = cursor.lastrowid
            logger.info(f"✅ Task created: #{task_id} - {title}")
            return task_id
        except Exception as e:
            logger.error(f"❌ Failed to create task: {e}")
            return None
        finally:
            conn.close()
    
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get all pending tasks"""
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
        return tasks
    
    def complete_task(self, task_id: int):
        """Mark a task as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE tasks
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (task_id,))
            conn.commit()
            logger.info(f"✅ Task #{task_id} completed")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to complete task #{task_id}: {e}")
            return False
        finally:
            conn.close()
    
    def add_lead(self, name: str, email: str = None, phone: str = None, notes: str = None):
        """Add a new lead to the CRM pipeline (Frazer Method - Lead Generation stage)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO crm_pipeline (lead_name, lead_email, lead_phone, stage, notes)
                VALUES (?, ?, ?, 'lead_generation', ?)
            ''', (name, email, phone, notes))
            conn.commit()
            lead_id = cursor.lastrowid
            logger.info(f"✅ Lead added: #{lead_id} - {name}")
            return lead_id
        except Exception as e:
            logger.error(f"❌ Failed to add lead: {e}")
            return None
        finally:
            conn.close()
    
    def update_lead_stage(self, lead_id: int, new_stage: str):
        """Update a lead's stage in the Frazer Method pipeline"""
        valid_stages = ['lead_generation', 'qualification', 'nurturing', 'conversion', 'retention']
        
        if new_stage not in valid_stages:
            logger.error(f"❌ Invalid stage: {new_stage}")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE crm_pipeline
                SET stage = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_stage, lead_id))
            conn.commit()
            logger.info(f"✅ Lead #{lead_id} moved to stage: {new_stage}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update lead #{lead_id}: {e}")
            return False
        finally:
            conn.close()
    
    def get_leads_by_stage(self, stage: str) -> List[Dict[str, Any]]:
        """Get all leads in a specific stage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, lead_name, lead_email, lead_phone, stage, score, notes, created_at
            FROM crm_pipeline
            WHERE stage = ?
            ORDER BY score DESC, created_at DESC
        ''', (stage,))
        
        leads = []
        for row in cursor.fetchall():
            leads.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'stage': row[4],
                'score': row[5],
                'notes': row[6],
                'created_at': row[7]
            })
        
        conn.close()
        return leads
    
    def run(self):
        """Main execution loop"""
        logger.info("🚀 Simple Project Manager AI is running")
        logger.info("📊 Initializing Frazer Method CRM Pipeline")
        
        # Register some default agents
        self.register_agent("Backend Developer", "developer", ["python", "flask", "api"])
        self.register_agent("Frontend Developer", "developer", ["react", "typescript", "ui"])
        self.register_agent("CRM Specialist", "specialist", ["crm", "sales", "customer_relations"])
        
        # Create initial tasks for the Frazer Method implementation
        self.create_task(
            "Implement Lead Generation Module",
            "Create automated lead capture system with form validation and database integration",
            priority=10,
            assigned_to="Backend Developer"
        )
        
        self.create_task(
            "Build Qualification Scoring System",
            "Develop lead scoring algorithm based on engagement metrics and profile data",
            priority=9,
            assigned_to="CRM Specialist"
        )
        
        self.create_task(
            "Design CRM Dashboard UI",
            "Create intuitive dashboard for viewing and managing leads through pipeline stages",
            priority=8,
            assigned_to="Frontend Developer"
        )
        
        # Add some sample leads
        self.add_lead("John Doe", "john@example.com", "+1234567890", "Interested in premium package")
        self.add_lead("Jane Smith", "jane@example.com", "+0987654321", "Referred by existing customer")
        
        # Display current status
        pending_tasks = self.get_pending_tasks()
        logger.info(f"📋 Pending tasks: {len(pending_tasks)}")
        for task in pending_tasks:
            logger.info(f"   - Task #{task['id']}: {task['title']} (Priority: {task['priority']})")
        
        leads_in_generation = self.get_leads_by_stage('lead_generation')
        logger.info(f"🎯 Leads in generation stage: {len(leads_in_generation)}")
        for lead in leads_in_generation:
            logger.info(f"   - Lead #{lead['id']}: {lead['name']} ({lead['email']})")
        
        logger.info("✅ Simple Project Manager AI is operational")
        logger.info("💡 System is ready for autonomous development")

if __name__ == "__main__":
    pm = SimpleProjectManager()
    pm.run()
