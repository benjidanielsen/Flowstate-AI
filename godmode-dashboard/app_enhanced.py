#!/usr/bin/env python3
"""
📊 GODMODE AI MONITORING DASHBOARD - v2.0 "THE BIG PICTURE"
⚡ Real-time AI activity and Project Manager Log
"""

from __future__ import annotations

import logging
import os
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - import guard exercised indirectly
    from flask import Flask, jsonify, render_template, request
    from flask_socketio import SocketIO
except Exception as exc:  # pragma: no cover - exercised when Flask is missing
    Flask = None  # type: ignore[assignment]
    jsonify = None  # type: ignore[assignment]
    render_template = None  # type: ignore[assignment]
    request = None  # type: ignore[assignment]
    SocketIO = None  # type: ignore[assignment]
    FLASK_AVAILABLE = False
    _FLASK_IMPORT_ERROR = exc
else:  # pragma: no cover - logging only
    FLASK_AVAILABLE = True
    _FLASK_IMPORT_ERROR = None

import psutil

# --- Basic Configuration ---
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

DASHBOARD_HOST = os.getenv("GODMODE_DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.getenv("GODMODE_DASHBOARD_PORT", "3333"))
POLL_INTERVAL_SECONDS = float(os.getenv("GODMODE_DASHBOARD_POLL_SECONDS", "5"))
INSTALL_HINT = "pip install flask flask-socketio"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "dashboard_v2.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

if FLASK_AVAILABLE:
    app: Optional[Flask] = Flask(__name__)
    app.config["SECRET_KEY"] = "godmode-dashboard-v2-secret"
    socketio: Optional[SocketIO] = SocketIO(
        app, cors_allowed_origins="*", async_mode="threading"
    )
else:
    app = None
    socketio = None

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

def broadcast_update() -> None:
    """Broadcast a full update of system status to all clients."""

    if not (FLASK_AVAILABLE and app and socketio):
        return

    with app.app_context():
        data = {
            "system_stats": get_system_stats(),
            "ai_agents": get_ai_agent_status(),
            "log_entries": list(project_manager_log),
        }
        socketio.emit("full_update", data)

# --- Background Task ---

def background_monitor() -> None:
    """Continuously broadcast updates in the background."""

    while True:
        try:
            broadcast_update()
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Error in background monitor: %s", exc)

        if socketio is not None:
            socketio.sleep(POLL_INTERVAL_SECONDS)
        else:
            time.sleep(POLL_INTERVAL_SECONDS)

# --- Flask & SocketIO Routes ---

if FLASK_AVAILABLE:

    @app.route("/")
    def index():
        """Serve the main dashboard page."""

        ensure_dashboard_template()
        return render_template("dashboard.html")

    @app.route("/log", methods=["POST"])
    def receive_log():
        """API endpoint for agents to post log entries."""

        data = request.json
        if not data or "entry" not in data:
            return (
                jsonify({"status": "error", "message": "Invalid log entry format"}),
                400,
            )

        log_entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "entry": data["entry"],
        }

        project_manager_log.appendleft(log_entry)
        socketio.emit("new_log_entry", log_entry)

        return jsonify({"status": "success"}), 200

    @socketio.on("connect")
    def handle_connect():
        """Handle a new client connection."""

        logger.info("Client connected. Sending initial state.")
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


def ensure_dashboard_template() -> Path:
    """Ensure the dashboard template exists on disk."""

    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    dashboard_file = templates_dir / "dashboard.html"
    if not dashboard_file.exists():
        logger.info("Dashboard template not found, creating it.")
        dashboard_file.write_text(DASHBOARD_TEMPLATE)
    return dashboard_file


def _dependency_error_message() -> str:
    return (
        "Flask and Flask-SocketIO are required to run the dashboard. "
        f"Install them with: {INSTALL_HINT}"
    )


def main() -> int:
    """Entry point used by the CLI and tooling."""

    ensure_dashboard_template()

    if not (FLASK_AVAILABLE and app and socketio):
        message = _dependency_error_message()
        logger.error(message)
        if _FLASK_IMPORT_ERROR:
            logger.debug("Underlying import error: %s", _FLASK_IMPORT_ERROR)
        print(message)
        if _FLASK_IMPORT_ERROR:
            print(f"Import error: {_FLASK_IMPORT_ERROR}")
        return 1

    socketio.start_background_task(target=background_monitor)

    public_host = (
        "localhost" if DASHBOARD_HOST in {"0.0.0.0", "::"} else DASHBOARD_HOST
    )
    logger.info(
        "🚀 Starting GODMODE Dashboard v2.0 on http://%s:%s",
        public_host,
        DASHBOARD_PORT,
    )

    socketio.run(
        app,
        host=DASHBOARD_HOST,
        port=DASHBOARD_PORT,
        debug=False,
        use_reloader=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
 