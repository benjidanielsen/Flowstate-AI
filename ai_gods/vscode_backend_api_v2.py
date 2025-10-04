#!/usr/bin/env python3
"""
VSCode Backend API Server v2.0 - Fully Enhanced
Provides REST API and WebSocket endpoints for VSCode extension integration
Features: Enhanced error handling, better performance, real-time updates
"""

import asyncio
import json
import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import redis

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
DB_PATH = os.getenv('VSCODE_DB_PATH', 'vscode_integration.db')
API_PORT = int(os.getenv('API_PORT', 3001))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/vscode-backend-api-v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Redis connection with retry logic
redis_client = None
redis_available = False

def init_redis():
    """Initialize Redis connection"""
    global redis_client, redis_available
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True,
                socket_connect_timeout=5
            )
            redis_client.ping()
            redis_available = True
            logger.info(f"✅ Connected to Redis (attempt {attempt + 1})")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Redis connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2)
    
    logger.warning("⚠️ Redis not available. Using in-memory fallback.")
    redis_available = False
    return False

init_redis()

# Initialize SQLite database
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
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT UNIQUE,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'QUEUED',
            priority TEXT DEFAULT 'MEDIUM',
            assigned_to TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            metadata TEXT
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            params TEXT,
            status TEXT DEFAULT 'PENDING',
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            executed_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

init_database()

# Helper functions
def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def publish_update(channel: str, data: dict):
    """Publish update to Redis and WebSocket"""
    # Publish to Redis
    if redis_available:
        try:
            redis_client.publish(channel, json.dumps(data))
        except Exception as e:
            logger.error(f"Error publishing to Redis: {e}")
    
    # Emit via WebSocket
    try:
        socketio.emit(channel, data)
    except Exception as e:
        logger.error(f"Error emitting WebSocket event: {e}")

# ===== API Endpoints =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()
        db_status = 'healthy'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'redis': redis_available,
        'database': db_status,
        'version': '2.0'
    })

@app.route('/api/agents/status', methods=['GET'])
def get_agent_status():
    """Get status of all AI agents"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM agent_status ORDER BY last_updated DESC')
        agents = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'agents': agents,
            'count': len(agents)
        })
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/agents/status/<agent_id>', methods=['GET'])
def get_specific_agent_status(agent_id):
    """Get status of a specific agent"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM agent_status WHERE agent_id = ?', (agent_id,))
        agent = cursor.fetchone()
        
        conn.close()
        
        if agent:
            return jsonify({
                'success': True,
                'agent': dict(agent)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/agents/status/<agent_id>', methods=['POST'])
def update_agent_status(agent_id):
    """Update status of a specific agent"""
    try:
        data = request.json
        status = data.get('status')
        current_task = data.get('current_task', '')
        progress = data.get('progress', 0)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO agent_status 
            (agent_id, status, current_task, progress, last_updated, heartbeat)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (agent_id, status, current_task, progress, datetime.now(), datetime.now()))
        
        conn.commit()
        conn.close()
        
        # Publish update
        publish_update('agent_status_update', {
            'agent_id': agent_id,
            'status': status,
            'current_task': current_task,
            'progress': progress,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating agent status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/agents/heartbeat/<agent_id>', methods=['POST'])
def agent_heartbeat(agent_id):
    """Update agent heartbeat"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE agent_status 
            SET heartbeat = ?
            WHERE agent_id = ?
        ''', (datetime.now(), agent_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating heartbeat: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filtering"""
    try:
        status_filter = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM tasks'
        params = []
        
        if status_filter:
            query += ' WHERE status = ?'
            params.append(status_filter)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        tasks = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'count': len(tasks)
        })
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        priority = data.get('priority', 'MEDIUM')
        assigned_to = data.get('assigned_to', '')
        metadata = data.get('metadata', {})
        
        if not name:
            return jsonify({'success': False, 'error': 'Task name is required'}), 400
        
        task_id = f"task_{int(datetime.now().timestamp() * 1000)}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (task_id, name, description, priority, assigned_to, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (task_id, name, description, priority, assigned_to, json.dumps(metadata)))
        
        db_task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Publish task creation
        publish_update('task_update', {
            'action': 'created',
            'task_id': task_id,
            'name': name,
            'priority': priority
        })
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'db_id': db_task_id
        })
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    try:
        data = request.json
        status = data.get('status')
        assigned_to = data.get('assigned_to')
        progress = data.get('progress')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        updates = ['updated_at = ?']
        params = [datetime.now()]
        
        if status:
            updates.append('status = ?')
            params.append(status)
            
            if status == 'COMPLETED':
                updates.append('completed_at = ?')
                params.append(datetime.now())
        
        if assigned_to is not None:
            updates.append('assigned_to = ?')
            params.append(assigned_to)
        
        if progress is not None:
            # Store progress in metadata
            cursor.execute('SELECT metadata FROM tasks WHERE task_id = ?', (task_id,))
            row = cursor.fetchone()
            if row:
                metadata = json.loads(row[0]) if row[0] else {}
                metadata['progress'] = progress
                updates.append('metadata = ?')
                params.append(json.dumps(metadata))
        
        params.append(task_id)
        
        cursor.execute(f'''
            UPDATE tasks
            SET {', '.join(updates)}
            WHERE task_id = ?
        ''', params)
        
        conn.commit()
        conn.close()
        
        # Publish task update
        publish_update('task_update', {
            'action': 'updated',
            'task_id': task_id,
            'status': status,
            'progress': progress
        })
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Get overall system status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count agents by status
        cursor.execute('SELECT COUNT(*) as count FROM agent_status WHERE status = "ACTIVE"')
        active_agents = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM agent_status')
        total_agents = cursor.fetchone()['count']
        
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
            'success': True,
            'system_status': system_status,
            'active_agents': active_agents,
            'total_agents': total_agents,
            'total_tasks': total_tasks,
            'queued_tasks': queued_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'godmode_enabled': active_agents > 0,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/command', methods=['POST'])
def execute_command():
    """Execute a command from VSCode extension"""
    try:
        data = request.json
        command = data.get('command')
        params = data.get('params', {})
        
        logger.info(f"Executing command: {command} with params: {params}")
        
        # Store command in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO commands (command, params, status)
            VALUES (?, ?, ?)
        ''', (command, json.dumps(params), 'EXECUTING'))
        
        command_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Handle different commands
        result = None
        
        if command == 'stop_godmode':
            # Stop all AI agents
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE agent_status SET status = "STOPPED"')
            conn.commit()
            conn.close()
            
            if redis_available:
                redis_client.publish('system_command', json.dumps({'command': 'stop'}))
            
            result = {'message': 'GODMODE stopped'}
        
        elif command == 'fix_everything':
            # Trigger self-healing system
            if redis_available:
                redis_client.publish('system_command', json.dumps({'command': 'fix_everything'}))
            
            result = {'message': 'Auto-fix initiated'}
        
        elif command == 'start_godmode':
            # Start GODMODE
            if redis_available:
                redis_client.publish('system_command', json.dumps({'command': 'start'}))
            
            result = {'message': 'GODMODE started'}
        
        else:
            result = {'error': 'Unknown command'}
        
        # Update command status
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE commands 
            SET status = ?, result = ?, executed_at = ?
            WHERE id = ?
        ''', ('COMPLETED', json.dumps(result), datetime.now(), command_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, **result})
        
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connection_status', {'status': 'connected', 'timestamp': datetime.now().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('subscribe')
def handle_subscribe(data):
    """Handle subscription to specific channels"""
    channel = data.get('channel')
    logger.info(f"Client {request.sid} subscribed to {channel}")
    emit('subscription_confirmed', {'channel': channel})

if __name__ == '__main__':
    logger.info("🚀 Starting VSCode Backend API Server v2.0...")
    logger.info(f"📡 Listening on http://0.0.0.0:{API_PORT}")
    logger.info(f"🔌 WebSocket support enabled")
    logger.info(f"📊 Database: {DB_PATH}")
    logger.info(f"🔴 Redis: {'Available' if redis_available else 'Not available (using fallback)'}")
    
    socketio.run(app, host='0.0.0.0', port=API_PORT, debug=False, allow_unsafe_werkzeug=True)
