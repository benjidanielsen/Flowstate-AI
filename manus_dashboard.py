#!/usr/bin/env python3
"""
📊 MANUS ACTIVITY MONITORING DASHBOARD
Real-time monitoring of all Manus instances, tasks, and performance metrics
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time

app = Flask(__name__)
CORS(app)

# Configuration
SYNC_DB_PATH = Path("/home/ubuntu/.manus-sync/sync_engine.db")
DASHBOARD_PORT = 3334

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(SYNC_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_manus_instances():
    """Get all registered Manus instances with their current status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, role, capabilities, current_task, status, progress, 
               files_claimed, last_heartbeat, performance_score
        FROM manus_instances
        ORDER BY id
    ''')
    
    instances = []
    for row in cursor.fetchall():
        instances.append({
            'id': row['id'],
            'role': row['role'],
            'capabilities': json.loads(row['capabilities']),
            'current_task': row['current_task'],
            'status': row['status'],
            'progress': row['progress'],
            'files_claimed': json.loads(row['files_claimed']),
            'last_heartbeat': row['last_heartbeat'],
            'performance_score': row['performance_score']
        })
    
    conn.close()
    return instances

def get_active_tasks():
    """Get all active tasks."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, description, assigned_to, priority, status, 
               dependencies, estimated_duration, created_at, started_at, 
               completed_at, files_involved
        FROM sync_tasks
        WHERE status IN ('pending', 'in_progress')
        ORDER BY priority ASC, created_at DESC
        LIMIT 20
    ''')
    
    tasks = []
    for row in cursor.fetchall():
        # Calculate progress based on time
        progress = 0
        if row['started_at']:
            started = datetime.fromisoformat(row['started_at'])
            elapsed = (datetime.now() - started).total_seconds() / 60
            estimated = row['estimated_duration']
            progress = min(int((elapsed / estimated) * 100), 99) if estimated > 0 else 0
        
        tasks.append({
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'assigned_to': row['assigned_to'],
            'priority': row['priority'],
            'status': row['status'],
            'dependencies': json.loads(row['dependencies']),
            'estimated_duration': row['estimated_duration'],
            'created_at': row['created_at'],
            'started_at': row['started_at'],
            'completed_at': row['completed_at'],
            'files_involved': json.loads(row['files_involved']),
            'progress': progress
        })
    
    conn.close()
    return tasks

def get_completed_tasks_24h():
    """Get tasks completed in the last 24 hours."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    
    cursor.execute('''
        SELECT id, title, assigned_to, completed_at, started_at
        FROM sync_tasks
        WHERE status = 'completed' AND completed_at >= ?
        ORDER BY completed_at DESC
    ''', (yesterday,))
    
    completed_tasks = []
    for row in cursor.fetchall():
        duration = 0
        if row['started_at'] and row['completed_at']:
            started = datetime.fromisoformat(row['started_at'])
            completed = datetime.fromisoformat(row['completed_at'])
            duration = int((completed - started).total_seconds() / 60)
        
        completed_tasks.append({
            'id': row['id'],
            'title': row['title'],
            'assigned_to': row['assigned_to'],
            'completed_at': row['completed_at'],
            'duration_minutes': duration
        })
    
    conn.close()
    return completed_tasks

def get_performance_stats():
    """Get performance statistics for all Manus instances."""
    completed_tasks = get_completed_tasks_24h()
    
    stats = {}
    for task in completed_tasks:
        manus_id = task['assigned_to']
        if manus_id not in stats:
            stats[manus_id] = {
                'tasks_completed': 0,
                'total_time': 0,
                'longest_tasks': []
            }
        
        stats[manus_id]['tasks_completed'] += 1
        stats[manus_id]['total_time'] += task['duration_minutes']
        stats[manus_id]['longest_tasks'].append({
            'title': task['title'],
            'duration': task['duration_minutes']
        })
    
    # Sort and keep only top 2 longest tasks
    for manus_id in stats:
        stats[manus_id]['longest_tasks'].sort(key=lambda x: x['duration'], reverse=True)
        stats[manus_id]['longest_tasks'] = stats[manus_id]['longest_tasks'][:2]
    
    return stats

def get_system_health():
    """Get overall system health metrics."""
    instances = get_manus_instances()
    tasks = get_active_tasks()
    
    active_count = sum(1 for i in instances if i['status'] == 'ACTIVE')
    pending_tasks = sum(1 for t in tasks if t['status'] == 'pending')
    in_progress_tasks = sum(1 for t in tasks if t['status'] == 'in_progress')
    
    # Check for stale heartbeats
    stale_instances = 0
    for instance in instances:
        if instance['last_heartbeat']:
            last_beat = datetime.fromisoformat(instance['last_heartbeat'])
            if (datetime.now() - last_beat).total_seconds() > 120:  # 2 minutes
                stale_instances += 1
    
    health_score = 100
    if stale_instances > 0:
        health_score -= (stale_instances * 20)
    if pending_tasks > 10:
        health_score -= 10
    
    return {
        'active_instances': active_count,
        'total_instances': len(instances),
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'stale_instances': stale_instances,
        'health_score': max(0, health_score)
    }

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/instances')
def api_instances():
    """API endpoint for Manus instances."""
    return jsonify(get_manus_instances())

@app.route('/api/tasks')
def api_tasks():
    """API endpoint for active tasks."""
    return jsonify(get_active_tasks())

@app.route('/api/performance')
def api_performance():
    """API endpoint for performance statistics."""
    return jsonify(get_performance_stats())

@app.route('/api/health')
def api_health():
    """API endpoint for system health."""
    return jsonify(get_system_health())

@app.route('/api/dashboard')
def api_dashboard():
    """Combined API endpoint for all dashboard data."""
    return jsonify({
        'instances': get_manus_instances(),
        'tasks': get_active_tasks(),
        'performance': get_performance_stats(),
        'health': get_system_health(),
        'timestamp': datetime.now().isoformat()
    })

def main():
    """Start the dashboard server."""
    print("=" * 60)
    print("🚀 MANUS ACTIVITY MONITORING DASHBOARD")
    print("=" * 60)
    print(f"📊 Dashboard URL: http://localhost:{DASHBOARD_PORT}")
    print(f"📁 Database: {SYNC_DB_PATH}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=DASHBOARD_PORT, debug=False)

if __name__ == '__main__':
    main()
