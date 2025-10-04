#!/usr/bin/env python3
"""
📊 GODMODE AI MONITORING DASHBOARD - v2.0 "THE BIG PICTURE"
⚡ Real-time AI activity and Project Manager Log
"""

import json
import time
import threading
import platform
import sys
import traceback
from datetime import datetime
from pathlib import Path
import logging
import os
from typing import Dict, List, Any
from collections import deque

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import psutil

# --- Basic Configuration ---
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'dashboard_v2.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'godmode-dashboard-v2-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# --- In-Memory Data Store ---
# Using deque for a capped-size, thread-safe list of log entries
project_manager_log = deque(maxlen=100)

# --- Core Application Logic ---

def get_system_stats():
    """Gathers basic system statistics."""
    return {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "timestamp": datetime.now().isoformat()
    }

def get_ai_agent_status():
    """Placeholder for AI agent status. In a real scenario, this would poll other services."""
    # This is mock data for demonstration purposes.
    # In the future, this will be fed by the actual AI agents.
    return [
        {"name": "Proactive Problem Solver", "status": "Idle", "task": "Monitoring system health..."},
        {"name": "AI Performance Tuner", "status": "Idle", "task": "Awaiting analysis tasks..."},
        {"name": "Godmode Orchestrator", "status": "Active", "task": "Coordinating system overhaul."},
    ]

def broadcast_update():
    """Broadcasts a full update of system status to all clients."""
    with app.app_context():
        data = {
            "system_stats": get_system_stats(),
            "ai_agents": get_ai_agent_status(),
            "log_entries": list(project_manager_log)
        }
        socketio.emit('full_update', data)

# --- Background Task ---

def background_monitor():
    """Continuously broadcasts updates in the background."""
    while True:
        try:
            broadcast_update()
        except Exception as e:
            logger.error(f"Error in background monitor: {e}")
        socketio.sleep(5) # Broadcast every 5 seconds

# --- Flask & SocketIO Routes ---

@app.route('/')
def index():
    """Serves the main dashboard page."""
    return render_template('dashboard.html')

@app.route('/log', methods=['POST'])
def receive_log():
    """API endpoint for the Project Manager (or other AIs) to post log entries."""
    data = request.json
    if not data or 'entry' not in data:
        return jsonify({"status": "error", "message": "Invalid log entry format"}), 400
    
    log_entry = {
        "timestamp": datetime.now().strftime('%H:%M:%S'),
        "entry": data['entry']
    }
    
    # Add to our log and broadcast it
    project_manager_log.appendleft(log_entry)
    socketio.emit('new_log_entry', log_entry)
    
    return jsonify({"status": "success"}), 200

@socketio.on('connect')
def handle_connect():
    """Handles a new client connection."""
    logger.info("Client connected. Sending initial state.")
    # Send a full update to the newly connected client
    broadcast_update()

# --- HTML Template ---
# For simplicity, the HTML is embedded here. In a larger app, this would be in a separate file.

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GODMODE Dashboard v2</title>
    <style>
        :root {
            --bg-color: #1a1a1a;
            --primary-color: #2a2a2a;
            --secondary-color: #3a3a3a;
            --font-color: #e0e0e0;
            --accent-color: #00aaff;
            --green: #28a745;
            --yellow: #ffc107;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--font-color);
            margin: 0;
            padding: 20px;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1.5fr;
            gap: 20px;
            max-width: 1600px;
            margin: auto;
        }
        .header {
            grid-column: 1 / -1;
            text-align: center;
            border-bottom: 1px solid var(--secondary-color);
            padding-bottom: 10px;
            margin-bottom: 10px;
        }
        h1, h2 {
            margin: 0;
            color: var(--accent-color);
        }
        .card {
            background-color: var(--primary-color);
            border-radius: 8px;
            padding: 20px;
            border: 1px solid var(--secondary-color);
        }
        .log-container {
            height: 70vh;
            overflow-y: auto;
            padding-right: 10px;
        }
        .log-entry {
            background-color: var(--secondary-color);
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
            border-left: 3px solid var(--accent-color);
            animation: fadeIn 0.5s ease;
        }
        .log-entry .timestamp {
            font-weight: bold;
            color: var(--yellow);
            margin-right: 10px;
        }
        .agent-status .agent {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid var(--secondary-color);
        }
        .agent-status .agent:last-child {
            border-bottom: none;
        }
        .agent-status .status {
            font-weight: bold;
        }
        .agent-status .status.Active { color: var(--green); }
        .agent-status .status.Idle { color: var(--yellow); }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>GODMODE Dashboard v2.0</h1>
        <p>Live System Monitoring & Project Manager Log</p>
    </div>

    <div class="container">
        <div class="card">
            <h2>AI Agent Status</h2>
            <div id="agent-status-container" class="agent-status">
                <!-- Agent statuses will be injected here -->
            </div>
        </div>
        <div class="card">
            <h2>Project Manager's Live Log</h2>
            <div id="log-container" class="log-container">
                <!-- Log entries will be injected here -->
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        const socket = io();

        socket.on('connect', () => {
            console.log('Connected to dashboard server.');
        });

        socket.on('full_update', (data) => {
            console.log('Received full update:', data);
            updateAgents(data.ai_agents);
            updateLogs(data.log_entries);
        });

        socket.on('new_log_entry', (logEntry) => {
            console.log('New log entry:', logEntry);
            addLogEntry(logEntry, true);
        });

        function updateAgents(agents) {
            const container = document.getElementById('agent-status-container');
            container.innerHTML = agents.map(agent => `
                <div class="agent">
                    <div>
                        <strong>${agent.name}</strong>
                        <p style="margin: 5px 0 0; font-size: 0.9em; color: #aaa;">Task: ${agent.task}</p>
                    </div>
                    <span class="status ${agent.status}">${agent.status}</span>
                </div>
            `).join('');
        }

        function updateLogs(logEntries) {
            const container = document.getElementById('log-container');
            container.innerHTML = ''; // Clear existing logs
            logEntries.forEach(entry => addLogEntry(entry, false));
        }

        function addLogEntry(logEntry, fromTop) {
            const container = document.getElementById('log-container');
            const entryDiv = document.createElement('div');
            entryDiv.className = 'log-entry';
            entryDiv.innerHTML = `<span class="timestamp">[${logEntry.timestamp}]</span>${logEntry.entry}`;
            
            if (fromTop) {
                container.prepend(entryDiv);
            } else {
                container.appendChild(entryDiv);
            }
        }
    </script>
</body>
</html>
""";

# --- Main Execution ---

if __name__ == '__main__':
    # Create templates directory and the dashboard file if they don't exist
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    dashboard_file = templates_dir / "dashboard.html"
    if not dashboard_file.exists():
        logger.info("Dashboard template not found, creating it.")
        dashboard_file.write_text(DASHBOARD_TEMPLATE)

    # Start the background thread for monitoring
    socketio.start_background_task(target=background_monitor)
    
    logger.info("🚀 Starting GODMODE Dashboard v2.0...")
    logger.info(f"🔗 Access it at http://localhost:3333")
    
    # Run the Flask app with SocketIO
    socketio.run(
        app,
        host='0.0.0.0',
        port=3333,
        debug=False,
        use_reloader=False
    )
