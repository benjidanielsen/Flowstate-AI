#!/usr/bin/env python3
"""
📊 GODMODE AI MONITORING DASHBOARD
⚡ Real-time AI activity monitor with progress bars
🎯 Shows what each AI is doing with visual progress indicators
🔄 Updates every 2 seconds with live status
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import logging
import os
import sqlite3
from typing import Dict, List, Any
import asyncio
import glob

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'godmode-dashboard-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

class GodmodeMonitor:
    """
    Real-time AI monitoring system
    Tracks all AI agents and their current activities
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.ai_status = {}
        self.task_history = []
        self.system_stats = {
            "total_ais": 0,
            "active_ais": 0,
            "completed_tasks": 0,
            "active_tasks": 0,
            "system_uptime": datetime.now()
        }
        
        # AI Agent definitions
        self.ai_agents = {
            "project-manager": {"name": "Project Manager", "icon": "🤖", "color": "#4080FF"},
            "backend-developer": {"name": "Backend Developer", "icon": "💻", "color": "#57A9FB"},
            "frontend-developer": {"name": "Frontend Developer", "icon": "🎨", "color": "#37D4CF"},
            "database-ai": {"name": "Database AI", "icon": "🗄️", "color": "#23C343"},
            "tester-ai": {"name": "Tester AI", "icon": "🔬", "color": "#FBE842"},
            "fixer-ai": {"name": "Fixer AI", "icon": "🛠️", "color": "#FF9A2E"},
            "devops-ai": {"name": "DevOps AI", "icon": "🚀", "color": "#A9AEB8"},
            "documentation-ai": {"name": "Documentation AI", "icon": "📚", "color": "#4080FF"},
            "support-ai": {"name": "Support AI", "icon": "🆘", "color": "#57A9FB"},
            "innovation-ai": {"name": "Innovation AI", "icon": "💡", "color": "#37D4CF"},
            "ai-communication-hub": {"name": "Communication Hub", "icon": "📡", "color": "#23C343"},
            "collective-memory-system": {"name": "Collective Memory", "icon": "🧠", "color": "#FBE842"}
        }
        
        # Initialize monitoring
        self.initialize_monitoring()
        
        # Start background monitoring
        self.start_monitoring_thread()
    
    def initialize_monitoring(self):
        """Initialize the monitoring system"""
        # Create monitoring directories
        monitoring_dirs = [
            "godmode-dashboard/static",
            "godmode-dashboard/templates", 
            "ai-status",
            "task-progress",
            "monitoring-logs"
        ]
        
        for directory in monitoring_dirs:
            (self.project_root / directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize AI status
        for ai_id, ai_info in self.ai_agents.items():
            self.ai_status[ai_id] = {
                "id": ai_id,
                "name": ai_info["name"],
                "icon": ai_info["icon"],
                "color": ai_info["color"],
                "status": "INITIALIZING",
                "current_task": "Starting up...",
                "progress": 0,
                "last_update": datetime.now().isoformat(),
                "tasks_completed": 0,
                "uptime": datetime.now(),
                "performance_score": 100,
                "current_activity": "Initializing systems"
            }
    
    def start_monitoring_thread(self):
        """Start background monitoring thread"""
        def monitor_loop():
            while True:
                try:
                    self.update_ai_status()
                    self.update_system_stats()
                    self.broadcast_updates()
                    time.sleep(2)  # Update every 2 seconds
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("🔄 AI Monitoring thread started")
    
    def update_ai_status(self):
        """Update status of all AI agents"""
        try:
            # Check for AI status files
            status_dir = self.project_root / "ai-status"
            
            for ai_id in self.ai_agents.keys():
                status_file = status_dir / f"{ai_id}_status.json"
                
                if status_file.exists():
                    try:
                        with open(status_file, 'r') as f:
                            status_data = json.load(f)
                        
                        # Update AI status
                        self.ai_status[ai_id].update({
                            "status": status_data.get("status", "UNKNOWN"),
                            "current_task": status_data.get("current_task", "No task assigned"),
                            "progress": status_data.get("progress", 0),
                            "last_update": status_data.get("timestamp", datetime.now().isoformat()),
                            "current_activity": status_data.get("activity", "Idle")
                        })
                        
                    except json.JSONDecodeError:
                        continue
                else:
                    # Simulate AI activity for demo (remove in production)
                    self.simulate_ai_activity(ai_id)
            
            # Check task progress files
            self.update_task_progress()
            
        except Exception as e:
            logger.error(f"Error updating AI status: {e}")
    
    def simulate_ai_activity(self, ai_id: str):
        """Simulate AI activity for demonstration (remove in production)"""
        import random
        
        # Sample tasks for each AI type
        sample_tasks = {
            "project-manager": [
                "Coordinating AI team activities",
                "Planning next development phase", 
                "Reviewing task assignments",
                "Monitoring system performance"
            ],
            "backend-developer": [
                "Implementing Frazer Method API",
                "Optimizing database queries",
                "Building authentication system",
                "Creating REST endpoints"
            ],
            "frontend-developer": [
                "Building responsive dashboard",
                "Implementing React components",
                "Optimizing UI performance",
                "Adding mobile support"
            ],
            "database-ai": [
                "Running database migrations",
                "Optimizing query performance",
                "Backing up data",
                "Analyzing data patterns"
            ],
            "tester-ai": [
                "Running unit tests",
                "Performing integration testing",
                "Checking code coverage",
                "Validating API endpoints"
            ],
            "innovation-ai": [
                "Generating new feature ideas",
                "Analyzing future trends",
                "Researching breakthrough technologies",
                "Creating innovation reports"
            ],
            "collective-memory-system": [
                "Syncing knowledge across AIs",
                "Processing cross-domain learning",
                "Updating memory database",
                "Analyzing knowledge patterns"
            ]
        }
        
        # Get current AI status
        current_status = self.ai_status[ai_id]
        
        # Simulate progress
        if current_status["progress"] >= 100:
            # Start new task
            tasks = sample_tasks.get(ai_id, ["Working on system improvements"])
            new_task = random.choice(tasks)
            
            self.ai_status[ai_id].update({
                "current_task": new_task,
                "progress": random.randint(1, 15),
                "status": "ACTIVE",
                "current_activity": new_task,
                "tasks_completed": current_status["tasks_completed"] + 1
            })
        else:
            # Continue current task
            progress_increment = random.randint(2, 8)
            new_progress = min(100, current_status["progress"] + progress_increment)
            
            self.ai_status[ai_id]["progress"] = new_progress
            
            if new_progress == 100:
                self.ai_status[ai_id]["status"] = "COMPLETED"
    
    def update_task_progress(self):
        """Update task progress from progress tracking files"""
        try:
            progress_dir = self.project_root / "progress-tracking"
            
            if progress_dir.exists():
                for progress_file in progress_dir.glob("*.json"):
                    try:
                        with open(progress_file, 'r') as f:
                            task_data = json.load(f)
                        
                        # Update AI status based on task progress
                        assigned_ai = task_data.get("assigned_ai")
                        if assigned_ai in self.ai_status:
                            self.ai_status[assigned_ai].update({
                                "current_task": task_data.get("task", "Unknown task"),
                                "status": task_data.get("status", "UNKNOWN"),
                                "last_update": task_data.get("updated_at", datetime.now().isoformat())
                            })
                    
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            logger.error(f"Error updating task progress: {e}")
    
    def update_system_stats(self):
        """Update overall system statistics"""
        try:
            active_count = len([ai for ai in self.ai_status.values() if ai["status"] in ["ACTIVE", "WORKING"]])
            completed_tasks = sum(ai["tasks_completed"] for ai in self.ai_status.values())
            
            self.system_stats.update({
                "total_ais": len(self.ai_agents),
                "active_ais": active_count,
                "completed_tasks": completed_tasks,
                "active_tasks": len([ai for ai in self.ai_status.values() if ai["progress"] > 0 and ai["progress"] < 100]),
                "uptime_seconds": (datetime.now() - self.system_stats["system_uptime"]).total_seconds()
            })
            
        except Exception as e:
            logger.error(f"Error updating system stats: {e}")
    
    def broadcast_updates(self):
        """Broadcast updates to connected clients"""
        try:
            # Get top 15 most active AIs (not overwhelming)
            active_ais = sorted(
                self.ai_status.values(),
                key=lambda x: (x["status"] == "ACTIVE", x["progress"]),
                reverse=True
            )[:15]
            
            update_data = {
                "ai_status": active_ais,
                "system_stats": self.system_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            socketio.emit('status_update', update_data)
            
        except Exception as e:
            logger.error(f"Error broadcasting updates: {e}")
    
    def get_dashboard_data(self):
        """Get current dashboard data"""
        # Return top 15 most relevant AIs
        active_ais = sorted(
            self.ai_status.values(),
            key=lambda x: (x["status"] == "ACTIVE", x["progress"], x["tasks_completed"]),
            reverse=True
        )[:15]
        
        return {
            "ai_status": active_ais,
            "system_stats": self.system_stats,
            "timestamp": datetime.now().isoformat()
        }

# Initialize monitor
monitor = GodmodeMonitor()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """API endpoint for current status"""
    return jsonify(monitor.get_dashboard_data())

@app.route('/api/ai/<ai_id>')
def get_ai_details(ai_id):
    """Get detailed info for specific AI"""
    if ai_id in monitor.ai_status:
        return jsonify(monitor.ai_status[ai_id])
    return jsonify({"error": "AI not found"}), 404

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected to monitoring dashboard")
    emit('status_update', monitor.get_dashboard_data())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected from monitoring dashboard")

if __name__ == '__main__':
    # Create HTML template
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 GODMODE AI Monitor</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
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
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .system-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .ai-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .ai-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .ai-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }
        
        .ai-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .ai-icon {
            font-size: 2em;
            margin-right: 15px;
        }
        
        .ai-info h3 {
            margin-bottom: 5px;
        }
        
        .ai-status {
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .status-ACTIVE { background: #23C343; }
        .status-WORKING { background: #FBE842; color: #333; }
        .status-COMPLETED { background: #37D4CF; }
        .status-INITIALIZING { background: #A9AEB8; }
        .status-ERROR { background: #FF4444; }
        
        .ai-task {
            margin: 15px 0;
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .progress-container {
            margin: 15px 0;
        }
        
        .progress-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4080FF, #57A9FB);
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        .ai-stats {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
            font-size: 0.8em;
            opacity: 0.8;
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .last-update {
            text-align: center;
            margin-top: 30px;
            opacity: 0.7;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .ai-grid {
                grid-template-columns: 1fr;
            }
            
            .system-stats {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 GODMODE AI MONITOR</h1>
        <p>Real-time AI Development Army Status</p>
    </div>
    
    <div class="system-stats">
        <div class="stat-card">
            <div class="stat-value" id="total-ais">0</div>
            <div>Total AIs</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="active-ais">0</div>
            <div>Active AIs</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="completed-tasks">0</div>
            <div>Completed Tasks</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="active-tasks">0</div>
            <div>Active Tasks</div>
        </div>
    </div>
    
    <div class="ai-grid" id="ai-grid">
        <!-- AI cards will be populated here -->
    </div>
    
    <div class="last-update">
        Last updated: <span id="last-update">Never</span>
    </div>
    
    <script>
        const socket = io();
        
        socket.on('status_update', function(data) {
            updateDashboard(data);
        });
        
        function updateDashboard(data) {
            // Update system stats
            document.getElementById('total-ais').textContent = data.system_stats.total_ais;
            document.getElementById('active-ais').textContent = data.system_stats.active_ais;
            document.getElementById('completed-tasks').textContent = data.system_stats.completed_tasks;
            document.getElementById('active-tasks').textContent = data.system_stats.active_tasks;
            
            // Update AI grid
            const aiGrid = document.getElementById('ai-grid');
            aiGrid.innerHTML = '';
            
            data.ai_status.forEach(ai => {
                const aiCard = createAICard(ai);
                aiGrid.appendChild(aiCard);
            });
            
            // Update timestamp
            const now = new Date();
            document.getElementById('last-update').textContent = now.toLocaleTimeString();
        }
        
        function createAICard(ai) {
            const card = document.createElement('div');
            card.className = 'ai-card';
            if (ai.status === 'ACTIVE') {
                card.classList.add('pulse');
            }
            
            card.innerHTML = `
                <div class="ai-header">
                    <div class="ai-icon">${ai.icon}</div>
                    <div class="ai-info">
                        <h3>${ai.name}</h3>
                        <span class="ai-status status-${ai.status}">${ai.status}</span>
                    </div>
                </div>
                
                <div class="ai-task">
                    <strong>Current Task:</strong><br>
                    ${ai.current_task}
                </div>
                
                <div class="progress-container">
                    <div class="progress-label">
                        <span>Progress</span>
                        <span>${ai.progress}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${ai.progress}%"></div>
                    </div>
                </div>
                
                <div class="ai-stats">
                    <span>Tasks: ${ai.tasks_completed}</span>
                    <span>Score: ${ai.performance_score}%</span>
                </div>
            `;
            
            return card;
        }
        
        // Initial load
        fetch('/api/status')
            .then(response => response.json())
            .then(data => updateDashboard(data))
            .catch(error => console.error('Error loading initial data:', error));
    </script>
</body>
</html>'''
    
    # Save template
    template_dir = Path(__file__).parent / "templates"
    template_dir.mkdir(exist_ok=True)
    
    with open(template_dir / "dashboard.html", 'w') as f:
        f.write(template_content)
    
    logger.info("🚀 Starting GODMODE AI Monitoring Dashboard on http://localhost:3333")
    socketio.run(app, host='0.0.0.0', port=3333, debug=False)
