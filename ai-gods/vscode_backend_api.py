#!/usr/bin/env python3
"""
VSCode Backend API Server
Provides REST API and WebSocket endpoints for VSCode extension integration
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
import redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize Redis connection
try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    redis_client.ping()
    logger.info("✅ Connected to Redis")
except Exception as e:
    logger.warning(f"⚠️ Redis not available: {e}. Using in-memory fallback.")
    redis_client = None

# Initialize SQLite database
DB_PATH = 'vscode_integration.db'

def init_database():
    """Initialize the SQLite database for VSCode integration"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_status (
            agent_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            current_task TEXT,
            progress INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'QUEUED',
            assigned_to TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

init_database()

# ===== API Endpoints =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'redis': redis_client is not None
    })

@app.route('/api/agents/status', methods=['GET'])
def get_agent_status():
    """Get status of all AI agents"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM agent_status')
        agents = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify(agents)
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/status/<agent_id>', methods=['POST'])
def update_agent_status(agent_id):
    """Update status of a specific agent"""
    try:
        data = request.json
        status = data.get('status')
        current_task = data.get('current_task', '')
        progress = data.get('progress', 0)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO agent_status (agent_id, status, current_task, progress, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (agent_id, status, current_task, progress, datetime.now()))
        
        conn.commit()
        conn.close()
        
        # Publish update to Redis
        if redis_client:
            redis_client.publish('agent_status_update', json.dumps({
                'agent_id': agent_id,
                'status': status,
                'current_task': current_task,
                'progress': progress
            }))
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating agent status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
        tasks = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify(tasks)
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        assigned_to = data.get('assigned_to', '')
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (name, description, assigned_to)
            VALUES (?, ?, ?)
        ''', (name, description, assigned_to))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Publish task creation to Redis
        if redis_client:
            redis_client.publish('task_update', json.dumps({
                'action': 'created',
                'task_id': task_id,
                'name': name
            }))
        
        return jsonify({'success': True, 'task_id': task_id})
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    try:
        data = request.json
        status = data.get('status')
        assigned_to = data.get('assigned_to')
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if status:
            updates.append('status = ?')
            params.append(status)
        
        if assigned_to:
            updates.append('assigned_to = ?')
            params.append(assigned_to)
        
        updates.append('updated_at = ?')
        params.append(datetime.now())
        
        params.append(task_id)
        
        cursor.execute(f'''
            UPDATE tasks
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)
        
        conn.commit()
        conn.close()
        
        # Publish task update to Redis
        if redis_client:
            redis_client.publish('task_update', json.dumps({
                'action': 'updated',
                'task_id': task_id,
                'status': status
            }))
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Get overall system status"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Count agents by status
        cursor.execute('SELECT COUNT(*) as count FROM agent_status WHERE status = "ACTIVE"')
        active_agents = cursor.fetchone()['count']
        
        # Count tasks by status
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE status = "QUEUED"')
        queued_tasks = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE status = "IN_PROGRESS"')
        in_progress_tasks = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE status = "COMPLETED"')
        completed_tasks = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE status = "FAILED"')
        failed_tasks = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM tasks')
        total_tasks = cursor.fetchone()['count']
        
        conn.close()
        
        # Determine system status
        system_status = 'IDLE'
        if active_agents > 0:
            system_status = 'ACTIVE'
        elif failed_tasks > 0:
            system_status = 'ERROR'
        
        return jsonify({
            'system_status': system_status,
            'active_agents': active_agents,
            'total_tasks': total_tasks,
            'queued_tasks': queued_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'godmode_enabled': active_agents > 0
        })
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/command', methods=['POST'])
def execute_command():
    """Execute a command from VSCode extension"""
    try:
        data = request.json
        command = data.get('command')
        params = data.get('params', {})
        
        logger.info(f"Executing command: {command} with params: {params}")
        
        # Handle different commands
        if command == 'stop_godmode':
            # Stop all AI agents
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('UPDATE agent_status SET status = "STOPPED"')
            conn.commit()
            conn.close()
            
            if redis_client:
                redis_client.publish('system_command', json.dumps({'command': 'stop'}))
            
            return jsonify({'success': True, 'message': 'GODMODE stopped'})
        
        elif command == 'fix_everything':
            # Trigger self-healing system
            if redis_client:
                redis_client.publish('system_command', json.dumps({'command': 'fix_everything'}))
            
            return jsonify({'success': True, 'message': 'Auto-fix initiated'})
        
        else:
            return jsonify({'error': 'Unknown command'}), 400
        
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/communication/question', methods=['POST'])
def ask_question():
    """Ask a question to the AI agents"""
    try:
        data = request.json
        question = data.get('question')
        topic = data.get('topic')
        from_agent = data.get('from_agent', 'vscode-extension')
        
        # Publish question to Redis for agents to answer
        if redis_client:
            message_id = f"q_{datetime.now().timestamp()}"
            redis_client.publish('agent_questions', json.dumps({
                'id': message_id,
                'question': question,
                'topic': topic,
                'from': from_agent
            }))
            
            # Wait for response (simplified - in production, use proper async handling)
            # For now, return a placeholder
            return jsonify({
                'answer': 'Question received. Agents are processing...',
                'message_id': message_id
            })
        else:
            return jsonify({'error': 'Communication system not available'}), 503
        
    except Exception as e:
        logger.error(f"Error asking question: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/communication/knowledge', methods=['POST'])
def share_knowledge():
    """Share knowledge with the AI agents"""
    try:
        data = request.json
        topic = data.get('topic')
        content = data.get('content')
        tags = data.get('tags', [])
        from_agent = data.get('from_agent', 'vscode-extension')
        
        # Publish knowledge to Redis
        if redis_client:
            redis_client.publish('knowledge_sharing', json.dumps({
                'topic': topic,
                'content': content,
                'tags': tags,
                'from': from_agent,
                'timestamp': datetime.now().isoformat()
            }))
            
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Communication system not available'}), 503
        
    except Exception as e:
        logger.error(f"Error sharing knowledge: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/communication/knowledge/search', methods=['GET'])
def search_knowledge():
    """Search the knowledge base"""
    try:
        query = request.args.get('query', '')
        tags = request.args.get('tags', '').split(',') if request.args.get('tags') else []
        
        # In a full implementation, this would query the Communication Hub's knowledge base
        # For now, return a placeholder
        return jsonify([])
        
    except Exception as e:
        logger.error(f"Error searching knowledge: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting VSCode Backend API Server...")
    logger.info("📡 Listening on http://localhost:3001")
    app.run(host='0.0.0.0', port=3001, debug=True)
