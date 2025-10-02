#!/usr/bin/env python3.11
"""
MANUS COORDINATION API
Simple Flask API for real-time Manus instance coordination
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import json
from datetime import datetime
from pathlib import Path
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'manus-coordination-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory state
manus_instances = {}
available_tasks = []
task_assignments = {}
heartbeats = {}

COORD_DIR = Path("/home/ubuntu/Flowstate-AI/.manus-coordination")

# Load existing tasks
def load_tasks():
    global available_tasks
    task_file = COORD_DIR / "AVAILABLE_TASKS.md"
    if task_file.exists():
        content = task_file.read_text()
        # Parse tasks from markdown
        for line in content.split('\n'):
            if line.startswith('**TASK-'):
                task_id = line.split('**')[1].split(':')[0]
                available_tasks.append({
                    'id': task_id,
                    'description': line,
                    'status': 'available',
                    'claimed_by': None
                })

@app.route('/api/register', methods=['POST'])
def register_manus():
    """Register a new Manus instance"""
    data = request.json
    manus_id = data.get('manus_id')
    role = data.get('role')
    capabilities = data.get('capabilities', [])
    
    manus_instances[manus_id] = {
        'id': manus_id,
        'role': role,
        'capabilities': capabilities,
        'status': 'active',
        'registered_at': datetime.now().isoformat(),
        'last_seen': datetime.now().isoformat()
    }
    
    # Broadcast to all connected clients
    socketio.emit('manus_registered', manus_instances[manus_id])
    
    return jsonify({
        'success': True,
        'manus_id': manus_id,
        'message': f'Manus {manus_id} registered successfully'
    })

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """Update Manus heartbeat"""
    data = request.json
    manus_id = data.get('manus_id')
    status = data.get('status', {})
    
    if manus_id in manus_instances:
        manus_instances[manus_id]['last_seen'] = datetime.now().isoformat()
        manus_instances[manus_id]['status'] = status.get('status', 'active')
        heartbeats[manus_id] = datetime.now().isoformat()
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Manus not registered'}), 404

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get available tasks"""
    return jsonify({
        'tasks': available_tasks,
        'count': len(available_tasks)
    })

@app.route('/api/tasks/claim', methods=['POST'])
def claim_task():
    """Claim a task"""
    data = request.json
    manus_id = data.get('manus_id')
    task_id = data.get('task_id')
    
    for task in available_tasks:
        if task['id'] == task_id and task['status'] == 'available':
            task['status'] = 'claimed'
            task['claimed_by'] = manus_id
            task['claimed_at'] = datetime.now().isoformat()
            
            task_assignments[task_id] = manus_id
            
            # Broadcast task claim
            socketio.emit('task_claimed', {
                'task_id': task_id,
                'manus_id': manus_id
            })
            
            return jsonify({
                'success': True,
                'task': task
            })
    
    return jsonify({'success': False, 'error': 'Task not available'}), 404

@app.route('/api/tasks/complete', methods=['POST'])
def complete_task():
    """Mark task as complete"""
    data = request.json
    manus_id = data.get('manus_id')
    task_id = data.get('task_id')
    
    for task in available_tasks:
        if task['id'] == task_id and task['claimed_by'] == manus_id:
            task['status'] = 'complete'
            task['completed_at'] = datetime.now().isoformat()
            
            # Broadcast task completion
            socketio.emit('task_completed', {
                'task_id': task_id,
                'manus_id': manus_id
            })
            
            return jsonify({
                'success': True,
                'task': task
            })
    
    return jsonify({'success': False, 'error': 'Task not found or not claimed by you'}), 404

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get overall system status"""
    return jsonify({
        'manus_instances': manus_instances,
        'tasks': {
            'total': len(available_tasks),
            'available': len([t for t in available_tasks if t['status'] == 'available']),
            'claimed': len([t for t in available_tasks if t['status'] == 'claimed']),
            'complete': len([t for t in available_tasks if t['status'] == 'complete'])
        },
        'heartbeats': heartbeats
    })

@app.route('/api/broadcast', methods=['POST'])
def broadcast_message():
    """Broadcast message to all Manus instances"""
    data = request.json
    message = data.get('message')
    from_manus = data.get('from_manus')
    
    socketio.emit('broadcast', {
        'from': from_manus,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({'success': True})

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'message': 'Connected to Manus Coordination API'})

@socketio.on('manus_update')
def handle_manus_update(data):
    """Handle Manus status update"""
    manus_id = data.get('manus_id')
    if manus_id in manus_instances:
        manus_instances[manus_id].update(data)
        emit('manus_updated', data, broadcast=True)

# Background task to check for stale Manus instances
def check_stale_instances():
    while True:
        time.sleep(60)  # Check every minute
        now = datetime.now()
        for manus_id, instance in list(manus_instances.items()):
            last_seen = datetime.fromisoformat(instance['last_seen'])
            if (now - last_seen).seconds > 300:  # 5 minutes
                instance['status'] = 'stale'
                socketio.emit('manus_stale', {'manus_id': manus_id})

if __name__ == '__main__':
    # Load tasks on startup
    load_tasks()
    
    # Start background thread
    thread = threading.Thread(target=check_stale_instances, daemon=True)
    thread.start()
    
    print("🚀 Manus Coordination API starting on http://localhost:5000")
    print(f"📋 Loaded {len(available_tasks)} tasks")
    print("💬 WebSocket enabled for real-time updates")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
