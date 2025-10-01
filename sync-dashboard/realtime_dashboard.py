#!/usr/bin/env python3
"""
🔥 REAL-TIME MANUS SYNC DASHBOARD 🔥
Live monitoring of multiple Manus instances working together

Features:
- Real-time task progress visualization
- Live Manus activity monitoring  
- Performance metrics and efficiency tracking
- Conflict detection and resolution status
- Business impact measurement
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path to import sync engine
sys.path.append(str(Path(__file__).parent.parent))
from MANUS_SYNC_ENGINE import ManusSyncEngine, TaskStatus, TaskPriority

app = Flask(__name__)
app.config['SECRET_KEY'] = 'manus_sync_dashboard_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global sync engine instance
sync_engine = None
dashboard_thread = None
running = False

def init_sync_engine():
    """Initialize the sync engine"""
    global sync_engine
    sync_engine = ManusSyncEngine()
    if not sync_engine.running:
        sync_engine.start_sync_engine()

def dashboard_update_loop():
    """Continuously update dashboard data"""
    global running
    while running:
        try:
            if sync_engine:
                dashboard_data = sync_engine.get_dashboard_data()
                
                # Add additional metrics
                dashboard_data['live_metrics'] = calculate_live_metrics()
                dashboard_data['efficiency_score'] = calculate_efficiency_score()
                dashboard_data['business_impact'] = calculate_business_impact()
                
                # Emit to all connected clients
                socketio.emit('dashboard_update', dashboard_data)
            
            time.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            print(f"Dashboard update error: {e}")
            time.sleep(5)

def calculate_live_metrics():
    """Calculate real-time performance metrics"""
    if not sync_engine:
        return {}
    
    now = datetime.now()
    hour_ago = now - timedelta(hours=1)
    
    # Tasks completed in last hour
    completed_tasks = [
        task for task in sync_engine.task_queue.values()
        if task.status == TaskStatus.COMPLETED and 
           task.completed_at and task.completed_at > hour_ago
    ]
    
    # Average completion time
    completion_times = [
        (task.completed_at - task.started_at).total_seconds() / 60
        for task in completed_tasks
        if task.started_at and task.completed_at
    ]
    
    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    
    return {
        'tasks_completed_last_hour': len(completed_tasks),
        'average_completion_time_minutes': round(avg_completion_time, 1),
        'active_file_locks': len(sync_engine.active_locks),
        'total_messages_sent': get_message_count(),
        'system_uptime_hours': round((now - get_system_start_time()).total_seconds() / 3600, 1)
    }

def calculate_efficiency_score():
    """Calculate overall system efficiency score"""
    if not sync_engine or not sync_engine.manus_instances:
        return 0
    
    # Base score from Manus performance
    avg_performance = sum(
        manus.performance_score for manus in sync_engine.manus_instances.values()
    ) / len(sync_engine.manus_instances)
    
    # Penalty for conflicts and delays
    conflict_penalty = len(sync_engine.active_locks) * 2
    
    # Bonus for task completion rate
    total_tasks = len(sync_engine.task_queue)
    completed_tasks = len([t for t in sync_engine.task_queue.values() if t.status == TaskStatus.COMPLETED])
    completion_bonus = (completed_tasks / total_tasks * 20) if total_tasks > 0 else 0
    
    efficiency = max(0, min(100, avg_performance - conflict_penalty + completion_bonus))
    return round(efficiency, 1)

def calculate_business_impact():
    """Calculate business impact metrics"""
    if not sync_engine:
        return {}
    
    # Simulate business metrics based on development progress
    completed_tasks = len([t for t in sync_engine.task_queue.values() if t.status == TaskStatus.COMPLETED])
    active_manus = len([m for m in sync_engine.manus_instances.values() if m.status == 'ACTIVE'])
    
    # Estimated value generation
    estimated_value_per_task = 1000  # $1000 per completed task
    total_value_generated = completed_tasks * estimated_value_per_task
    
    # Development speed multiplier
    speed_multiplier = active_manus * 1.5 if active_manus > 1 else 1
    
    return {
        'total_value_generated': total_value_generated,
        'development_speed_multiplier': round(speed_multiplier, 1),
        'estimated_time_saved_hours': completed_tasks * 2,  # 2 hours saved per task
        'roi_percentage': round((total_value_generated / 10000) * 100, 1) if total_value_generated > 0 else 0,
        'productivity_index': round(completed_tasks * speed_multiplier, 1)
    }

def get_message_count():
    """Get total message count from database"""
    try:
        import sqlite3
        conn = sqlite3.connect(sync_engine.sync_db)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM communication_log')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

def get_system_start_time():
    """Get system start time (approximate)"""
    return datetime.now() - timedelta(hours=1)  # Assume started 1 hour ago

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/dashboard')
def api_dashboard():
    """API endpoint for dashboard data"""
    if sync_engine:
        data = sync_engine.get_dashboard_data()
        data['live_metrics'] = calculate_live_metrics()
        data['efficiency_score'] = calculate_efficiency_score()
        data['business_impact'] = calculate_business_impact()
        return jsonify(data)
    return jsonify({'error': 'Sync engine not initialized'})

@app.route('/api/create_task', methods=['POST'])
def create_task():
    """API endpoint to create new tasks"""
    from flask import request
    
    if not sync_engine:
        return jsonify({'error': 'Sync engine not initialized'})
    
    data = request.get_json()
    task_id = sync_engine.create_task(
        title=data.get('title', 'New Task'),
        description=data.get('description', ''),
        priority=TaskPriority(data.get('priority', 3)),
        files_involved=data.get('files_involved', []),
        dependencies=data.get('dependencies', [])
    )
    
    return jsonify({'task_id': task_id, 'status': 'created'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected to dashboard')
    if sync_engine:
        # Send initial data
        dashboard_data = sync_engine.get_dashboard_data()
        dashboard_data['live_metrics'] = calculate_live_metrics()
        dashboard_data['efficiency_score'] = calculate_efficiency_score()
        dashboard_data['business_impact'] = calculate_business_impact()
        emit('dashboard_update', dashboard_data)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected from dashboard')

# HTML Template for the dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 MANUS SYNC DASHBOARD</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #4080FF;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        
        .card h3 {
            color: #4080FF;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .manus-instance {
            background: rgba(64,128,255,0.2);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #4080FF;
        }
        
        .manus-active {
            border-left-color: #23C343;
            background: rgba(35,195,67,0.2);
        }
        
        .manus-inactive {
            border-left-color: #FF9A2E;
            background: rgba(255,154,46,0.2);
        }
        
        .task-item {
            background: rgba(87,169,251,0.2);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            border-left: 3px solid #57A9FB;
        }
        
        .task-high {
            border-left-color: #FF9A2E;
            background: rgba(255,154,46,0.2);
        }
        
        .task-critical {
            border-left-color: #FBE842;
            background: rgba(251,232,66,0.2);
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4080FF, #57A9FB);
            transition: width 0.3s ease;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #4080FF;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        .metric-label {
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 5px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-active { background: #23C343; }
        .status-inactive { background: #FF9A2E; }
        .status-blocked { background: #A9AEB8; }
        
        .efficiency-score {
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        
        .efficiency-excellent { color: #23C343; }
        .efficiency-good { color: #57A9FB; }
        .efficiency-warning { color: #FBE842; }
        .efficiency-poor { color: #FF9A2E; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .live-indicator {
            animation: pulse 2s infinite;
            color: #23C343;
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .two-column {
            grid-column: span 2;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔥 MANUS SYNC DASHBOARD</h1>
        <p>Real-time monitoring of AI development army</p>
        <span class="live-indicator">● LIVE</span>
    </div>
    
    <div class="dashboard-grid">
        <!-- System Overview -->
        <div class="card">
            <h3>🎯 System Overview</h3>
            <div class="metric-value" id="total-manus">0</div>
            <div class="metric-label">Active Manus Instances</div>
            
            <div class="metric-value" id="active-tasks" style="font-size: 1.5em; margin-top: 15px;">0</div>
            <div class="metric-label">Active Tasks</div>
            
            <div class="metric-value" id="completed-tasks" style="font-size: 1.5em; margin-top: 15px;">0</div>
            <div class="metric-label">Completed Tasks</div>
        </div>
        
        <!-- Efficiency Score -->
        <div class="card">
            <h3>⚡ Efficiency Score</h3>
            <div class="efficiency-score" id="efficiency-score">0%</div>
            <div class="metric-label">Overall System Performance</div>
            
            <div style="margin-top: 20px;">
                <div class="metric-value" id="speed-multiplier" style="font-size: 1.5em;">1.0x</div>
                <div class="metric-label">Development Speed</div>
            </div>
        </div>
        
        <!-- Business Impact -->
        <div class="card">
            <h3>💰 Business Impact</h3>
            <div class="metric-value" id="value-generated">$0</div>
            <div class="metric-label">Value Generated</div>
            
            <div class="metric-value" id="roi-percentage" style="font-size: 1.5em; margin-top: 15px;">0%</div>
            <div class="metric-label">ROI Percentage</div>
            
            <div class="metric-value" id="time-saved" style="font-size: 1.5em; margin-top: 15px;">0h</div>
            <div class="metric-label">Time Saved</div>
        </div>
        
        <!-- Manus Instances -->
        <div class="card two-column">
            <h3>🤖 Manus Instances</h3>
            <div id="manus-list">
                <!-- Manus instances will be populated here -->
            </div>
        </div>
        
        <!-- Active Tasks -->
        <div class="card full-width">
            <h3>📋 Active Tasks (Top 10)</h3>
            <div id="task-list">
                <!-- Tasks will be populated here -->
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        
        socket.on('dashboard_update', function(data) {
            updateDashboard(data);
        });
        
        function updateDashboard(data) {
            // System overview
            document.getElementById('total-manus').textContent = data.system_stats.active_manus_instances;
            document.getElementById('active-tasks').textContent = data.active_tasks.length;
            document.getElementById('completed-tasks').textContent = data.system_stats.completed_tasks;
            
            // Efficiency score
            const efficiency = data.efficiency_score || 0;
            const efficiencyElement = document.getElementById('efficiency-score');
            efficiencyElement.textContent = efficiency + '%';
            
            // Color code efficiency
            efficiencyElement.className = 'efficiency-score ';
            if (efficiency >= 90) efficiencyElement.className += 'efficiency-excellent';
            else if (efficiency >= 70) efficiencyElement.className += 'efficiency-good';
            else if (efficiency >= 50) efficiencyElement.className += 'efficiency-warning';
            else efficiencyElement.className += 'efficiency-poor';
            
            // Business impact
            if (data.business_impact) {
                document.getElementById('value-generated').textContent = '$' + data.business_impact.total_value_generated.toLocaleString();
                document.getElementById('roi-percentage').textContent = data.business_impact.roi_percentage + '%';
                document.getElementById('time-saved').textContent = data.business_impact.estimated_time_saved_hours + 'h';
                document.getElementById('speed-multiplier').textContent = data.business_impact.development_speed_multiplier + 'x';
            }
            
            // Manus instances
            const manusList = document.getElementById('manus-list');
            manusList.innerHTML = '';
            
            Object.values(data.manus_instances).forEach(manus => {
                const manusDiv = document.createElement('div');
                manusDiv.className = 'manus-instance ' + (manus.status === 'ACTIVE' ? 'manus-active' : 'manus-inactive');
                
                manusDiv.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="status-indicator status-${manus.status.toLowerCase()}"></span>
                            <strong>${manus.id}</strong> (${manus.role})
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 0.9em; opacity: 0.8;">${manus.progress}%</div>
                            <div style="font-size: 0.8em; opacity: 0.6;">Score: ${manus.performance_score}</div>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.9em; opacity: 0.8;">
                        ${manus.current_task || 'Waiting for tasks...'}
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${manus.progress}%"></div>
                    </div>
                `;
                
                manusList.appendChild(manusDiv);
            });
            
            // Active tasks
            const taskList = document.getElementById('task-list');
            taskList.innerHTML = '';
            
            data.active_tasks.slice(0, 10).forEach(task => {
                const taskDiv = document.createElement('div');
                const priorityClass = task.priority === 1 ? 'task-critical' : task.priority === 2 ? 'task-high' : '';
                taskDiv.className = 'task-item ' + priorityClass;
                
                const progress = task.status === 'pending' ? 0 : task.status === 'in_progress' ? 50 : 100;
                
                taskDiv.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>${task.title}</strong>
                            <div style="font-size: 0.8em; opacity: 0.7; margin-top: 4px;">
                                Assigned to: ${task.assigned_to} | Priority: ${task.priority} | Status: ${task.status}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 0.9em;">${progress}%</div>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                `;
                
                taskList.appendChild(taskDiv);
            });
        }
        
        // Initial load
        fetch('/api/dashboard')
            .then(response => response.json())
            .then(data => updateDashboard(data))
            .catch(error => console.error('Error loading dashboard:', error));
    </script>
</body>
</html>
'''

# Create templates directory and save HTML
def setup_templates():
    """Setup Flask templates"""
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    with open(templates_dir / 'dashboard.html', 'w') as f:
        f.write(DASHBOARD_HTML)

def start_dashboard(host='localhost', port=3333):
    """Start the real-time dashboard"""
    global running, dashboard_thread
    
    print("🚀 Starting Manus Sync Dashboard...")
    
    # Setup templates
    setup_templates()
    
    # Initialize sync engine
    init_sync_engine()
    
    # Start dashboard update thread
    running = True
    dashboard_thread = threading.Thread(target=dashboard_update_loop, daemon=True)
    dashboard_thread.start()
    
    print(f"🔥 Dashboard running at http://{host}:{port}")
    print("📊 Real-time Manus monitoring active!")
    
    # Start Flask app
    socketio.run(app, host=host, port=port, debug=False)

def stop_dashboard():
    """Stop the dashboard"""
    global running
    running = False
    if sync_engine:
        sync_engine.stop_sync_engine()

if __name__ == "__main__":
    start_dashboard()
