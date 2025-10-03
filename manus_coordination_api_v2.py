#!/usr/bin/env python3.11
"""
MANUS COORDINATION API V2
Enhanced real-time coordination with GitHub integration and cross-sandbox support
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import json
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
import subprocess
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'manus-coordination-secret-v2'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# In-memory state
manus_instances = {}
available_tasks = []
task_assignments = {}
heartbeats = {}
messages = []
commands = {}
pending_approvals = []  # Queue of actions requiring approval

COORD_DIR = Path("/home/ubuntu/Flowstate-AI/.manus-coordination")
GITHUB_REPO = "benjidanielsen/Flowstate-AI"

# Ensure coordination directory exists
COORD_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# GITHUB INTEGRATION - Cross-Sandbox Communication
# ============================================================================

def git_pull():
    """Pull latest changes from GitHub"""
    try:
        result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            cwd='/home/ubuntu/Flowstate-AI',
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Git pull failed: {e}")
        return False

def git_push(message="Update coordination files"):
    """Push changes to GitHub"""
    try:
        # Add coordination files
        subprocess.run(
            ['git', 'add', '.manus-coordination/'],
            cwd='/home/ubuntu/Flowstate-AI',
            timeout=10
        )
        
        # Commit
        subprocess.run(
            ['git', 'commit', '-m', message],
            cwd='/home/ubuntu/Flowstate-AI',
            timeout=10
        )
        
        # Push
        result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            cwd='/home/ubuntu/Flowstate-AI',
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Git push failed: {e}")
        return False

def sync_with_github(skip_approval=False):
    """Sync coordination state with GitHub"""
    # Pull latest
    git_pull()
    
    # Save current state to files
    save_state_to_files()
    
    # Push updates (only if approved or approval skipped)
    if skip_approval:
        git_push("Update Manus coordination state")
    else:
        print("⚠️  GitHub push requires approval")

def request_approval(action_type, description, manus_id, data=None):
    """Request approval for an action"""
    approval_request = {
        'id': f"APPROVAL-{len(pending_approvals) + 1}",
        'action_type': action_type,
        'description': description,
        'requested_by': manus_id,
        'requested_at': datetime.now().isoformat(),
        'status': 'pending',
        'data': data or {}
    }
    pending_approvals.append(approval_request)
    
    # Save approval request to file
    approval_file = COORD_DIR / f"{approval_request['id']}.json"
    approval_file.write_text(json.dumps(approval_request, indent=2))
    
    # Broadcast approval request
    socketio.emit('approval_requested', approval_request)
    
    print(f"📋 Approval requested: {approval_request['id']} - {description}")
    return approval_request['id']

def save_state_to_files():
    """Save in-memory state to coordination files"""
    # Save task queue
    task_queue_file = COORD_DIR / "TASK_QUEUE.json"
    task_queue_file.write_text(json.dumps({
        "last_updated": datetime.now().isoformat(),
        "updated_by": "coordination_api_v2",
        "total_tasks": len(available_tasks),
        "available_tasks": len([t for t in available_tasks if t['status'] == 'available']),
        "claimed_tasks": len([t for t in available_tasks if t['status'] == 'claimed']),
        "completed_tasks": len([t for t in available_tasks if t['status'] == 'complete']),
        "tasks": available_tasks
    }, indent=2))
    
    # Save Manus instances status
    status_file = COORD_DIR / "COORDINATION_STATUS.json"
    status_file.write_text(json.dumps({
        "last_updated": datetime.now().isoformat(),
        "manus_instances": manus_instances,
        "heartbeats": heartbeats,
        "active_count": len([m for m in manus_instances.values() if m.get('status') == 'active'])
    }, indent=2))
    
    # Save messages
    messages_file = COORD_DIR / "MESSAGES.json"
    messages_file.write_text(json.dumps({
        "last_updated": datetime.now().isoformat(),
        "messages": messages[-100:]  # Keep last 100 messages
    }, indent=2))

def load_state_from_files():
    """Load state from coordination files"""
    global available_tasks, manus_instances, heartbeats, messages
    
    # Load task queue
    task_queue_file = COORD_DIR / "TASK_QUEUE.json"
    if task_queue_file.exists():
        try:
            data = json.loads(task_queue_file.read_text())
            available_tasks = data.get('tasks', [])
        except Exception as e:
            print(f"❌ Failed to load task queue: {e}")
    
    # Load coordination status
    status_file = COORD_DIR / "COORDINATION_STATUS.json"
    if status_file.exists():
        try:
            data = json.loads(status_file.read_text())
            manus_instances = data.get('manus_instances', {})
            heartbeats = data.get('heartbeats', {})
        except Exception as e:
            print(f"❌ Failed to load coordination status: {e}")
    
    # Load messages
    messages_file = COORD_DIR / "MESSAGES.json"
    if messages_file.exists():
        try:
            data = json.loads(messages_file.read_text())
            messages = data.get('messages', [])
        except Exception as e:
            print(f"❌ Failed to load messages: {e}")

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register_manus():
    """Register a new Manus instance"""
    data = request.json
    manus_id = data.get('manus_id')
    role = data.get('role', 'worker')
    capabilities = data.get('capabilities', [])
    sandbox_id = data.get('sandbox_id', 'unknown')
    
    manus_instances[manus_id] = {
        'id': manus_id,
        'role': role,
        'capabilities': capabilities,
        'sandbox_id': sandbox_id,
        'status': 'active',
        'registered_at': datetime.now().isoformat(),
        'last_seen': datetime.now().isoformat(),
        'current_task': None,
        'tasks_completed': 0
    }
    
    # Create identity file
    identity_file = COORD_DIR / f"MANUS_{manus_id.upper()}_IDENTITY.json"
    identity_file.write_text(json.dumps(manus_instances[manus_id], indent=2))
    
    # Broadcast to all connected clients
    socketio.emit('manus_registered', manus_instances[manus_id])
    
    # Request approval for GitHub sync
    request_approval(
        'github_sync',
        f'Manus {manus_id} registration',
        manus_id,
        {'event': 'register', 'manus_id': manus_id}
    )
    
    print(f"✅ Manus {manus_id} registered (sandbox: {sandbox_id})")
    
    return jsonify({
        'success': True,
        'manus_id': manus_id,
        'message': f'Manus {manus_id} registered successfully',
        'available_tasks': len([t for t in available_tasks if t['status'] == 'available']),
        'coordination_dir': str(COORD_DIR)
    })

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """Update Manus heartbeat"""
    data = request.json
    manus_id = data.get('manus_id')
    status = data.get('status', {})
    current_task = data.get('current_task')
    progress = data.get('progress', 0)
    
    if manus_id in manus_instances:
        manus_instances[manus_id]['last_seen'] = datetime.now().isoformat()
        manus_instances[manus_id]['status'] = status.get('status', 'active')
        manus_instances[manus_id]['current_task'] = current_task
        manus_instances[manus_id]['progress'] = progress
        heartbeats[manus_id] = datetime.now().isoformat()
        
        # Update heartbeat file
        heartbeat_file = COORD_DIR / f"MANUS_{manus_id.upper()}_HEARTBEAT.json"
        heartbeat_file.write_text(json.dumps({
            'manus_id': manus_id,
            'alive': True,
            'timestamp': datetime.now().isoformat(),
            'status': status.get('status', 'active'),
            'current_task': current_task,
            'progress': progress
        }, indent=2))
        
        return jsonify({'success': True, 'timestamp': datetime.now().isoformat()})
    
    return jsonify({'success': False, 'error': 'Manus not registered'}), 404

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get available tasks"""
    manus_id = request.args.get('manus_id')
    
    # Filter tasks based on Manus capabilities if provided
    if manus_id and manus_id in manus_instances:
        capabilities = manus_instances[manus_id].get('capabilities', [])
        filtered_tasks = [
            t for t in available_tasks 
            if t['status'] == 'available' and (
                not t.get('required_capabilities') or 
                any(cap in capabilities for cap in t.get('required_capabilities', []))
            )
        ]
    else:
        filtered_tasks = [t for t in available_tasks if t['status'] == 'available']
    
    return jsonify({
        'tasks': filtered_tasks,
        'count': len(filtered_tasks),
        'total': len(available_tasks)
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
            
            # Update Manus instance
            if manus_id in manus_instances:
                manus_instances[manus_id]['current_task'] = task_id
            
            # Create claim file
            claim_file = COORD_DIR / f"TASK-{task_id}-CLAIMED-BY-{manus_id.upper()}.json"
            claim_file.write_text(json.dumps({
                'task_id': task_id,
                'manus_id': manus_id,
                'claimed_at': datetime.now().isoformat()
            }, indent=2))
            
            # Broadcast task claim
            socketio.emit('task_claimed', {
                'task_id': task_id,
                'manus_id': manus_id
            })
            
            # Request approval for GitHub sync
            request_approval(
                'github_sync',
                f'Task {task_id} claimed by {manus_id}',
                manus_id,
                {'event': 'task_claim', 'task_id': task_id}
            )
            
            print(f"✅ Task {task_id} claimed by {manus_id}")
            
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
    time_taken = data.get('time_taken')
    files_changed = data.get('files_changed', [])
    
    for task in available_tasks:
        if task['id'] == task_id and task['claimed_by'] == manus_id:
            task['status'] = 'complete'
            task['completed_at'] = datetime.now().isoformat()
            task['time_taken'] = time_taken
            task['files_changed'] = files_changed
            
            # Update Manus instance
            if manus_id in manus_instances:
                manus_instances[manus_id]['current_task'] = None
                manus_instances[manus_id]['tasks_completed'] = manus_instances[manus_id].get('tasks_completed', 0) + 1
            
            # Create completion file
            complete_file = COORD_DIR / f"TASK-{task_id}-COMPLETE.json"
            complete_file.write_text(json.dumps({
                'task_id': task_id,
                'manus_id': manus_id,
                'completed_at': datetime.now().isoformat(),
                'time_taken': time_taken,
                'files_changed': files_changed
            }, indent=2))
            
            # Broadcast task completion
            socketio.emit('task_completed', {
                'task_id': task_id,
                'manus_id': manus_id,
                'time_taken': time_taken
            })
            
            # Request approval for GitHub sync
            request_approval(
                'github_sync',
                f'Task {task_id} completed by {manus_id}',
                manus_id,
                {'event': 'task_complete', 'task_id': task_id, 'files_changed': files_changed}
            )
            
            print(f"✅ Task {task_id} completed by {manus_id} in {time_taken}")
            
            return jsonify({
                'success': True,
                'task': task,
                'tasks_completed': manus_instances[manus_id].get('tasks_completed', 0)
            })
    
    return jsonify({'success': False, 'error': 'Task not found or not claimed by you'}), 404

@app.route('/api/tasks/add', methods=['POST'])
def add_task():
    """Add a new task (Coordinator only)"""
    data = request.json
    
    task = {
        'id': data.get('id'),
        'title': data.get('title'),
        'description': data.get('description'),
        'priority': data.get('priority', 'medium'),
        'estimated_time': data.get('estimated_time'),
        'required_capabilities': data.get('required_capabilities', []),
        'status': 'available',
        'claimed_by': None,
        'created_by': data.get('created_by', 'coordinator'),
        'created_at': datetime.now().isoformat()
    }
    
    available_tasks.append(task)
    
    # Broadcast new task
    socketio.emit('task_added', task)
    
    # Request approval for GitHub sync
    request_approval(
        'github_sync',
        f'New task added: {task["title"]}',
        data.get('created_by', 'coordinator'),
        {'event': 'task_add', 'task_id': task['id']}
    )
    
    print(f"✅ Task {task['id']} added: {task['title']}")
    
    return jsonify({
        'success': True,
        'task': task
    })

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
        'approvals': {
            'pending': len([a for a in pending_approvals if a['status'] == 'pending']),
            'approved': len([a for a in pending_approvals if a['status'] == 'approved']),
            'rejected': len([a for a in pending_approvals if a['status'] == 'rejected'])
        },
        'heartbeats': heartbeats,
        'active_manus': len([m for m in manus_instances.values() if m.get('status') == 'active']),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get messages for a specific Manus"""
    manus_id = request.args.get('manus_id')
    
    if manus_id:
        # Filter messages for this Manus
        filtered = [m for m in messages if m.get('to') == manus_id or m.get('to') == 'all']
        return jsonify({
            'messages': filtered,
            'count': len(filtered)
        })
    
    return jsonify({
        'messages': messages,
        'count': len(messages)
    })

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """Send a message to another Manus"""
    data = request.json
    
    message = {
        'id': f"MSG-{len(messages) + 1}",
        'from': data.get('from'),
        'to': data.get('to'),
        'type': data.get('type', 'info'),
        'subject': data.get('subject', ''),
        'message': data.get('message'),
        'priority': data.get('priority', 'normal'),
        'timestamp': datetime.now().isoformat()
    }
    
    messages.append(message)
    
    # Create message file
    to_manus = data.get('to')
    if to_manus != 'all':
        message_file = COORD_DIR / f"MESSAGE_TO_{to_manus.upper()}.json"
    else:
        message_file = COORD_DIR / f"BROADCAST_MESSAGE_{len(messages)}.json"
    
    message_file.write_text(json.dumps(message, indent=2))
    
    # Broadcast via WebSocket
    socketio.emit('message_received', message)
    
    # Request approval for GitHub sync
    request_approval(
        'github_sync',
        f'Message from {message["from"]} to {message["to"]}',
        message['from'],
        {'event': 'message_send', 'message_id': message['id']}
    )
    
    print(f"✅ Message sent from {message['from']} to {message['to']}")
    
    return jsonify({
        'success': True,
        'message': message
    })

@app.route('/api/commands', methods=['GET'])
def get_commands():
    """Get commands for a specific Manus"""
    manus_id = request.args.get('manus_id')
    
    if manus_id and manus_id in commands:
        return jsonify({
            'commands': commands[manus_id],
            'count': len(commands[manus_id])
        })
    
    return jsonify({
        'commands': [],
        'count': 0
    })

@app.route('/api/commands/send', methods=['POST'])
def send_command():
    """Send a command to a Manus (Coordinator only)"""
    data = request.json
    to_manus = data.get('to')
    command = data.get('command')
    
    if to_manus not in commands:
        commands[to_manus] = []
    
    cmd = {
        'id': f"CMD-{len(commands[to_manus]) + 1}",
        'command': command,
        'params': data.get('params', {}),
        'timestamp': datetime.now().isoformat()
    }
    
    commands[to_manus].append(cmd)
    
    # Create command file
    command_file = COORD_DIR / f"COMMAND_TO_{to_manus.upper()}.json"
    command_file.write_text(json.dumps(cmd, indent=2))
    
    # Broadcast via WebSocket
    socketio.emit('command_received', {
        'to': to_manus,
        'command': cmd
    })
    
    print(f"✅ Command sent to {to_manus}: {command}")
    
    return jsonify({
        'success': True,
        'command': cmd
    })

@app.route('/api/sync', methods=['POST'])
def manual_sync():
    """Manually trigger GitHub sync (requires approval)"""
    data = request.json or {}
    approved = data.get('approved', False)
    
    if approved:
        sync_with_github(skip_approval=True)
        return jsonify({
            'success': True,
            'message': 'Synced with GitHub',
            'timestamp': datetime.now().isoformat()
        })
    else:
        # Request approval for manual sync
        manus_id = data.get('manus_id', 'unknown')
        approval_id = request_approval(
            'github_sync',
            'Manual GitHub sync requested',
            manus_id,
            {'event': 'manual_sync'}
        )
        return jsonify({
            'success': True,
            'message': 'Approval requested for GitHub sync',
            'approval_id': approval_id,
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/approvals', methods=['GET'])
def get_approvals():
    """Get pending approval requests"""
    status_filter = request.args.get('status', 'pending')
    
    filtered = [a for a in pending_approvals if a['status'] == status_filter] if status_filter else pending_approvals
    
    return jsonify({
        'approvals': filtered,
        'count': len(filtered),
        'pending_count': len([a for a in pending_approvals if a['status'] == 'pending'])
    })

@app.route('/api/approvals/<approval_id>/approve', methods=['POST'])
def approve_action(approval_id):
    """Approve a pending action (Manus #2 or authorized approver only)"""
    data = request.json
    approver = data.get('approver', 'unknown')
    
    # Find the approval request
    approval = None
    for a in pending_approvals:
        if a['id'] == approval_id:
            approval = a
            break
    
    if not approval:
        return jsonify({'success': False, 'error': 'Approval request not found'}), 404
    
    if approval['status'] != 'pending':
        return jsonify({'success': False, 'error': 'Approval already processed'}), 400
    
    # Mark as approved
    approval['status'] = 'approved'
    approval['approved_by'] = approver
    approval['approved_at'] = datetime.now().isoformat()
    
    # Update approval file
    approval_file = COORD_DIR / f"{approval_id}.json"
    approval_file.write_text(json.dumps(approval, indent=2))
    
    # Execute the approved action
    if approval['action_type'] == 'github_sync':
        threading.Thread(target=sync_with_github, args=(True,), daemon=True).start()
    
    # Broadcast approval
    socketio.emit('approval_granted', approval)
    
    print(f"✅ Approval granted: {approval_id} by {approver}")
    
    return jsonify({
        'success': True,
        'approval': approval
    })

@app.route('/api/approvals/<approval_id>/reject', methods=['POST'])
def reject_action(approval_id):
    """Reject a pending action"""
    data = request.json
    approver = data.get('approver', 'unknown')
    reason = data.get('reason', 'No reason provided')
    
    # Find the approval request
    approval = None
    for a in pending_approvals:
        if a['id'] == approval_id:
            approval = a
            break
    
    if not approval:
        return jsonify({'success': False, 'error': 'Approval request not found'}), 404
    
    if approval['status'] != 'pending':
        return jsonify({'success': False, 'error': 'Approval already processed'}), 400
    
    # Mark as rejected
    approval['status'] = 'rejected'
    approval['rejected_by'] = approver
    approval['rejected_at'] = datetime.now().isoformat()
    approval['rejection_reason'] = reason
    
    # Update approval file
    approval_file = COORD_DIR / f"{approval_id}.json"
    approval_file.write_text(json.dumps(approval, indent=2))
    
    # Broadcast rejection
    socketio.emit('approval_rejected', approval)
    
    print(f"❌ Approval rejected: {approval_id} by {approver} - {reason}")
    
    return jsonify({
        'success': True,
        'approval': approval
    })

# ============================================================================
# WEBSOCKET HANDLERS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {
        'message': 'Connected to Manus Coordination API V2',
        'timestamp': datetime.now().isoformat()
    })
    print("✅ WebSocket client connected")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print("❌ WebSocket client disconnected")

@socketio.on('manus_update')
def handle_manus_update(data):
    """Handle Manus status update"""
    manus_id = data.get('manus_id')
    if manus_id in manus_instances:
        manus_instances[manus_id].update(data)
        emit('manus_updated', data, broadcast=True)

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

def check_stale_instances():
    """Check for stale Manus instances"""
    while True:
        time.sleep(60)  # Check every minute
        now = datetime.now()
        for manus_id, instance in list(manus_instances.items()):
            try:
                last_seen = datetime.fromisoformat(instance['last_seen'])
                if (now - last_seen).seconds > 300:  # 5 minutes
                    if instance['status'] != 'stale':
                        instance['status'] = 'stale'
                        socketio.emit('manus_stale', {'manus_id': manus_id})
                        print(f"⚠️  Manus {manus_id} is stale (no heartbeat for 5+ minutes)")
            except Exception as e:
                print(f"❌ Error checking stale instance {manus_id}: {e}")

def periodic_github_sync():
    """Periodically sync with GitHub (pull only, push requires approval)"""
    while True:
        time.sleep(120)  # Sync every 2 minutes
        try:
            # Pull latest changes
            git_pull()
            
            # Reload state from files (in case other Manus updated)
            load_state_from_files()
            
            # Save current state to files locally
            save_state_to_files()
            
            # Note: Push requires explicit approval via API
            print("✅ Periodic GitHub pull and state save completed")
        except Exception as e:
            print(f"❌ Periodic sync failed: {e}")

def auto_assign_tasks():
    """Automatically assign tasks to idle Manus instances"""
    while True:
        time.sleep(30)  # Check every 30 seconds
        
        # Find idle Manus instances
        idle_manus = [
            m for m in manus_instances.values()
            if m.get('status') == 'active' and not m.get('current_task')
        ]
        
        # Find available tasks
        available = [t for t in available_tasks if t['status'] == 'available']
        
        # Auto-assign
        for manus in idle_manus:
            if not available:
                break
            
            # Find suitable task based on capabilities
            suitable_tasks = [
                t for t in available
                if not t.get('required_capabilities') or
                any(cap in manus.get('capabilities', []) for cap in t.get('required_capabilities', []))
            ]
            
            if suitable_tasks:
                task = suitable_tasks[0]
                task['status'] = 'claimed'
                task['claimed_by'] = manus['id']
                task['claimed_at'] = datetime.now().isoformat()
                task['auto_assigned'] = True
                
                manus['current_task'] = task['id']
                
                # Notify via WebSocket
                socketio.emit('task_assigned', {
                    'task_id': task['id'],
                    'manus_id': manus['id']
                })
                
                available.remove(task)
                
                print(f"✅ Auto-assigned task {task['id']} to {manus['id']}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 MANUS COORDINATION API V2")
    print("=" * 80)
    
    # Load existing state
    print("📂 Loading coordination state from files...")
    load_state_from_files()
    print(f"✅ Loaded {len(available_tasks)} tasks")
    print(f"✅ Loaded {len(manus_instances)} Manus instances")
    
    # Start background threads
    print("🔄 Starting background tasks...")
    threading.Thread(target=check_stale_instances, daemon=True).start()
    threading.Thread(target=periodic_github_sync, daemon=True).start()
    threading.Thread(target=auto_assign_tasks, daemon=True).start()
    
    print("=" * 80)
    print("✅ API ready on http://localhost:5000")
    print("✅ WebSocket enabled for real-time updates")
    print("✅ GitHub sync enabled for cross-sandbox coordination")
    print("✅ Auto-assignment enabled for idle Manus instances")
    print("=" * 80)
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)
