#!/usr/bin/env python3
"""
GODMODE AI MONITORING DASHBOARD - ENHANCED VERSION
Real-time AI activity monitor with Windows compatibility
Shows what each AI is doing with visual progress indicators
Updates every 2 seconds with live status
Full Windows/Linux/macOS compatibility
Robust error handling and recovery
"""

# Try to import Flask and Flask-SocketIO in a resilient way so the module can still be
# inspected by linters or imported by scripts that don't run the web server.
try:
    # type: ignore - some environments/linters may not have these packages available
    from flask import Flask, render_template, jsonify, request, send_from_directory  # type: ignore
    from flask_socketio import SocketIO, emit  # type: ignore
    FLASK_AVAILABLE = True
except Exception as _import_err:
    # Avoid raising during import; provide a flag and useful message at runtime.
    FLASK_AVAILABLE = False
    import sys as _sys
    _sys.stderr.write(
        "Warning: Flask or Flask-SocketIO could not be imported. "
        "Web server functionality will be disabled.\n"
        "To enable the dashboard run: pip install flask flask-socketio\n"
    )
    # Provide minimal placeholders to avoid NameError when tools introspect the module.
    Flask = None
    render_template = None
    jsonify = None
    request = None
    send_from_directory = None
    SocketIO = None
    emit = None

import json
import time
import threading
import platform
import sys
import io
import traceback
from datetime import datetime, timedelta
from pathlib import Path
import logging
import os
import sqlite3
from typing import Dict, List, Any, Optional
import asyncio
import glob
import psutil
import signal
from contextlib import contextmanager
import uuid
from self_improvement import SelfImprovementAgent
from github_integration import GitHubIntegration

# Enhanced logging configuration
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# Ensure stdout/stderr use UTF-8 to avoid Windows console encoding issues
def _ensure_utf8_stream(stream):
    try:
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
            return stream
        buffer = getattr(stream, 'buffer', None)
        if buffer is not None:
            return io.TextIOWrapper(buffer, encoding='utf-8', errors='replace', write_through=True)
    except Exception:
        pass
    return stream


sys.stdout = _ensure_utf8_stream(sys.stdout)
sys.stderr = _ensure_utf8_stream(sys.stderr)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'dashboard.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Flask app configuration (only create if Flask is available)
if FLASK_AVAILABLE:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'godmode-dashboard-enhanced-secret'
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development

    # Enhanced SocketIO configuration
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        logger=False,  # Disable SocketIO logging to reduce noise
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25
    )
else:
    app = None
    socketio = None

class GodmodeMonitorEnhanced:
    """
    Enhanced Real-time AI monitoring system
    Tracks all AI agents and their current activities with robust error handling
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.dashboard_dir = Path(__file__).parent
        self.static_dir = self.dashboard_dir / "static"
        self.templates_dir = self.dashboard_dir / "templates"
        self.db_path = self.dashboard_dir / "dashboard.db"
        
        # Create necessary directories
        self._create_directories()
        
        # Initialize data structures
        self.ai_status = {}
        self.task_history = []
        self.system_stats = {
            "total_ais": 0,
            "active_ais": 0,
            "completed_tasks": 0,
            "active_tasks": 0,
            "system_uptime": datetime.now(),
            "errors_count": 0,
            "recovery_count": 0
        }
        
        # Enhanced AI Agent definitions with profile pictures
        self.ai_agents = {
            "project-manager": {
                "name": "Project Manager", 
                "icon": "PM", 
                "color": "#4080FF",
                "profile_pic": "/static/profile_pictures/project_manager.png",
                "description": "Coordinates all AI agents and manages project workflow"
            },
            "backend-developer": {
                "name": "Backend Developer", 
                "icon": "BE", 
                "color": "#57A9FB",
                "profile_pic": "/static/profile_pictures/backend_developer.png",
                "description": "Develops server-side logic and API endpoints"
            },
            "frontend-developer": {
                "name": "Frontend Developer", 
                "icon": "FE", 
                "color": "#37D4CF",
                "profile_pic": "/static/profile_pictures/frontend_developer.png",
                "description": "Creates user interfaces and client-side functionality"
            },
            "database-ai": {
                "name": "Database AI", 
                "icon": "DB", 
                "color": "#23C343",
                "profile_pic": "/static/profile_pictures/database_ai.png",
                "description": "Manages database operations and optimizations"
            },
            "tester-ai": {
                "name": "Tester AI", 
                "icon": "QA", 
                "color": "#FBE842",
                "profile_pic": "/static/profile_pictures/tester_ai.png",
                "description": "Performs quality assurance and automated testing"
            },
            "fixer-ai": {
                "name": "Fixer AI", 
                "icon": "FX", 
                "color": "#FF9A2E",
                "profile_pic": "/static/profile_pictures/fixer_ai.png",
                "description": "Identifies and resolves bugs and issues"
            },
            "devops-ai": {
                "name": "DevOps AI", 
                "icon": "ENG", 
                "color": "#A9AEB8",
                "profile_pic": "/static/profile_pictures/devops_ai.png",
                "description": "Handles deployment and infrastructure management"
            },
            "documentation-ai": {
                "name": "Documentation AI", 
                "icon": "DOC", 
                "color": "#4080FF",
                "profile_pic": "/static/profile_pictures/documentation_ai.png",
                "description": "Creates and maintains project documentation"
            },
            "support-ai": {
                "name": "Support AI", 
                "icon": "SUP", 
                "color": "#57A9FB",
                "profile_pic": "/static/profile_pictures/support_ai.png",
                "description": "Provides user support and troubleshooting"
            },
            "innovation-ai": {
                "name": "Innovation AI", 
                "icon": "INN", 
                "color": "#37D4CF",
                "profile_pic": "/static/profile_pictures/innovation_ai.png",
                "description": "Generates new ideas and breakthrough solutions"
            },
            "ai-communication-hub": {
                "name": "Communication Hub", 
                "icon": "COM", 
                "color": "#23C343",
                "profile_pic": "/static/profile_pictures/communication_hub.png",
                "description": "Facilitates communication between AI agents"
            },
            "collective-memory-system": {
                "name": "Collective Memory", 
                "icon": "MEM", 
                "color": "#FBE842",
                "profile_pic": "/static/profile_pictures/collective_memory.png",
                "description": "Stores and retrieves shared knowledge and experiences"
            }
        }
        
        # System monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.error_count = 0
        self.last_error_time = None
        self.self_improvement_agent = SelfImprovementAgent(self)
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            try:
                self.github_integration = GitHubIntegration("Flowstate-AI", "Flowstate-AI", github_token)  # Assuming repo owner and name are 'Flowstate-AI'
                logger.info("GitHub integration enabled")
            except Exception as integration_error:
                logger.error(f"Failed to initialize GitHub integration: {integration_error}")
                self.github_integration = None
        else:
            self.github_integration = None
            logger.info("GitHub integration disabled: GITHUB_TOKEN not provided")

        # Initialize the monitoring system
        try:
            self._init_database()
            self.initialize_monitoring()
            logger.info("GodmodeMonitorEnhanced initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize monitor: {e}")
            self._handle_initialization_error(e)
    
    def _create_directories(self):
        """Create necessary directories with proper error handling"""
        try:
            directories = [
                self.static_dir,
                self.static_dir / "css",
                self.static_dir / "js", 
                self.static_dir / "profile_pictures",
                self.templates_dir,
                self.dashboard_dir / "logs"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                
            # Set permissions (Unix-like systems only)
            if platform.system() != 'Windows':
                for directory in directories:
                    os.chmod(directory, 0o755)
                    
            logger.info("Dashboard directories created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            raise
    
    def _init_database(self):
        """Initialize SQLite database for dashboard data"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            cursor = conn.cursor()
            
            # AI status table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_status (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT DEFAULT 'INITIALIZING',
                    current_task TEXT,
                    progress INTEGER DEFAULT 0,
                    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tasks_completed INTEGER DEFAULT 0,
                    performance_score REAL DEFAULT 100.0,
                    error_count INTEGER DEFAULT 0,
                    uptime_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Task history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ai_id TEXT NOT NULL,
                    task_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    duration_seconds INTEGER,
                    success BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # System events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    severity TEXT DEFAULT 'INFO',
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    additional_data TEXT DEFAULT '{}'
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Dashboard database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    @contextmanager
    def _get_db_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _handle_initialization_error(self, error: Exception):
        """Handle initialization errors gracefully"""
        logger.error(f"ALERT: Initialization error: {error}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Try to continue with minimal functionality
        self.ai_status = {}
        for ai_id, ai_info in self.ai_agents.items():
            self.ai_status[ai_id] = {
                "id": ai_id,
                "name": ai_info["name"],
                "icon": ai_info["icon"],
                "color": ai_info["color"],
                "status": "ERROR",
                "current_task": f"Initialization failed: {str(error)[:100]}",
                "progress": 0,
                "last_update": datetime.now().isoformat(),
                "tasks_completed": 0,
                "uptime": datetime.now(),
                "performance_score": 0,
                "current_activity": "System recovery needed"
            }
    
    def initialize_monitoring(self):
        """Initialize the monitoring system with error recovery"""
        try:
            # Initialize AI status
            for ai_id, ai_info in self.ai_agents.items():
                self.ai_status[ai_id] = {
                    "id": ai_id,
                    "name": ai_info["name"],
                    "icon": ai_info["icon"],
                    "color": ai_info["color"],
                    "profile_pic": ai_info["profile_pic"],
                    "description": ai_info["description"],
                    "status": "INITIALIZING",
                    "current_task": "Starting up...",
                    "progress": 0,
                    "last_update": datetime.now().isoformat(),
                    "tasks_completed": 0,
                    "uptime": datetime.now(),
                    "performance_score": 100,
                    "current_activity": "Initializing systems",
                    "error_count": 0,
                    "last_heartbeat": datetime.now().isoformat()
                }
            
            # Save initial status to database
            self._save_ai_status_to_db()
            
            # Start monitoring thread
            self.start_monitoring()
            self.self_improvement_agent = SelfImprovementAgent(self)
            
            # Initialize GitHub integration
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                self.github_integration = GitHubIntegration("Flowstate-AI", "Flowstate-AI", github_token) # Assuming repo owner and name are 'Flowstate-AI'
            else:
                logger.warning("GITHUB_TOKEN environment variable not set. GitHub integration will be disabled.")
                self.github_integration = None
            
            logger.info("Monitoring system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring: {e}")
            self._handle_initialization_error(e)
    
    def _save_ai_status_to_db(self):
        """Save AI status to database"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                for ai_id, status in self.ai_status.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO ai_status 
                        (id, name, status, current_task, progress, last_update, 
                         tasks_completed, performance_score, error_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        ai_id,
                        status["name"],
                        status["status"],
                        status["current_task"],
                        status["progress"],
                        status["last_update"],
                        status["tasks_completed"],
                        status["performance_score"],
                        status.get("error_count", 0)
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save AI status to database: {e}")
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if self.monitoring_active:
            return
        
        try:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop, 
                daemon=True, 
                name="DashboardMonitor"
            )
            self.monitoring_thread.start()
            logger.info("Dashboard monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            self.monitoring_active = False
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Dashboard monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop with error recovery"""
        logger.info("Monitoring loop started")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            while self.monitoring_active:
                try:
                    # Update AI status
                    self._update_ai_status()

                    # Update system stats
                    self._update_system_stats()

                    # Check for heartbeats
                    self._check_heartbeats()

                    # Emit updates via SocketIO
                    self._emit_status_update()

                    # Run self-improvement cycle in this thread's event loop
                    loop.run_until_complete(
                        self.self_improvement_agent.run_self_improvement_cycle()
                    )

                    # Log performance metrics
                    self._log_performance_metrics()

                    # Sleep for 2 seconds
                    time.sleep(2)

                except Exception as e:
                    self.error_count += 1
                    self.last_error_time = datetime.now()
                    logger.error(f"Monitoring loop error: {e}")

                    # Log error to database
                    self._log_system_event("MONITORING_ERROR", str(e), "ERROR")

                    # Sleep longer on error
                    time.sleep(10)

                    # Attempt recovery if too many errors
                    if self.error_count > 10:
                        self._attempt_recovery()
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            except Exception:
                logger.debug("Failed to shutdown async generators cleanly", exc_info=True)
            finally:
                asyncio.set_event_loop(None)
                loop.close()
    
    def _update_ai_status(self):
        """Update AI status with simulated or real data"""
        try:
            current_time = datetime.now()
            
            for ai_id, status in self.ai_status.items():
                # Simulate AI activity if no real data
                if status["status"] == "INITIALIZING":
                    # Gradually initialize AIs
                    if current_time.second % 10 == 0:
                        status["status"] = "ACTIVE"
                        status["current_task"] = "Ready for tasks"
                        status["progress"] = 0
                        status["current_activity"] = "Waiting for assignments"
                
                elif status["status"] == "ACTIVE":
                    # Simulate occasional task updates
                    if current_time.second % 30 == 0:
                        tasks = [
                            "Processing data",
                            "Analyzing requirements", 
                            "Generating code",
                            "Running tests",
                            "Optimizing performance",
                            "Updating documentation"
                        ]
                        status["current_task"] = f"{tasks[current_time.second % len(tasks)]}"
                        status["progress"] = min(100, status["progress"] + 10)
                        
                        if status["progress"] >= 100:
                            status["tasks_completed"] += 1
                            status["progress"] = 0
                
                # Update timestamps
                status["last_update"] = current_time.isoformat()
                status["last_heartbeat"] = current_time.isoformat()
            
            # Save to database periodically
            if current_time.second % 30 == 0:
                self._save_ai_status_to_db()
                
        except Exception as e:
            logger.error(f"Failed to update AI status: {e}")
    
    def _update_system_stats(self):
        """Update system statistics"""
        try:
            active_ais = len([ai for ai in self.ai_status.values() if ai["status"] == "ACTIVE"])
            total_tasks = sum(ai["tasks_completed"] for ai in self.ai_status.values())
            
            self.system_stats.update({
                "total_ais": len(self.ai_status),
                "active_ais": active_ais,
                "completed_tasks": total_tasks,
                "active_tasks": len([ai for ai in self.ai_status.values() if ai["progress"] > 0]),
                "errors_count": self.error_count,
                "uptime": str(datetime.now() - self.system_stats["system_uptime"])
            })
            
        except Exception as e:
            logger.error(f"Failed to update system stats: {e}")
    
    def _check_heartbeats(self):
        """Check for stale AI heartbeats"""
        try:
            current_time = datetime.now()
            
            for ai_id, status in self.ai_status.items():
                last_heartbeat = datetime.fromisoformat(status["last_heartbeat"])
                
                # Mark as inactive if no heartbeat for 5 minutes
                if current_time - last_heartbeat > timedelta(minutes=5):
                    if status["status"] == "ACTIVE":
                        status["status"] = "INACTIVE"
                        status["current_task"] = "No heartbeat received"
                        status["current_activity"] = "Connection lost"
                        logger.warning(f"AI {ai_id} marked as INACTIVE (no heartbeat)")
                        
        except Exception as e:
            logger.error(f"Failed to check heartbeats: {e}")
    
    def _emit_status_update(self):
        """Emit status update via SocketIO"""
        try:
            dashboard_data = self.get_dashboard_data()
            socketio.emit('status_update', dashboard_data)
            
        except Exception as e:
            logger.error(f"Failed to emit status update: {e}")
    
    def _log_performance_metrics(self):
        """Log performance metrics to database"""
        try:
            if datetime.now().second % 60 == 0:  # Log every minute
                with self._get_db_connection() as conn:
                    cursor = conn.cursor()
                    
                    # System metrics
                    cpu_percent = psutil.cpu_percent()
                    memory_percent = psutil.virtual_memory().percent
                    
                    metrics = [
                        ("cpu_usage", cpu_percent),
                        ("memory_usage", memory_percent),
                        ("active_ais", self.system_stats["active_ais"]),
                        ("completed_tasks", self.system_stats["completed_tasks"]),
                        ("error_count", self.error_count)
                    ]
                    
                    for metric_name, metric_value in metrics:
                        cursor.execute('''
                            INSERT INTO performance_metrics (metric_name, metric_value)
                            VALUES (?, ?)
                        ''', (metric_name, metric_value))
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Failed to log performance metrics: {e}")
    
    def _log_system_event(self, event_type: str, description: str, severity: str = "INFO"):
        """Log system event to database"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO system_events (event_type, description, severity)
                    VALUES (?, ?, ?)
                ''', (event_type, description, severity))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log system event: {e}")
    
    def _attempt_recovery(self):
        """Attempt system recovery"""
        logger.info("Attempting dashboard recovery...")
        
        try:
            # Reset error count
            self.error_count = 0
            
            # Reset AI status
            for ai_id, status in self.ai_status.items():
                if status["status"] in ["ERROR", "INACTIVE"]:
                    status["status"] = "INITIALIZING"
                    status["current_task"] = "Recovering..."
                    status["progress"] = 0
            
            # Log recovery attempt
            self._log_system_event("RECOVERY_ATTEMPT", "Dashboard recovery initiated", "INFO")
            
            logger.info("Dashboard recovery completed")
            
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
    
    def _sanitize_for_json(self, value: Any):
        """Convert dashboard payload data into JSON-serialisable structures."""
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, dict):
            return {key: self._sanitize_for_json(val) for key, val in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._sanitize_for_json(item) for item in value]
        return value


    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'ai_agents': list(self.ai_status.values()),
                'system_stats': self.system_stats,
                'platform_info': {
                    'system': platform.system(),
                    'version': platform.version(),
                    'python_version': sys.version,
                    'cpu_count': psutil.cpu_count(),
                logger.warning(f"Heartbeat from unknown AI: {ai_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to process heartbeat from {ai_id}: {e}")
            return False

# Initialize the enhanced monitor
monitor = GodmodeMonitorEnhanced()

# Flask Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Dashboard route error: {e}")
        return f"Dashboard Error: {e}", 500

@app.route('/api/status')
def api_status():
    """API endpoint for dashboard status"""
    try:
        return jsonify(monitor.get_dashboard_data())
    except Exception as e:
        logger.error(f"API status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agent_status')
def api_agent_status():
    """API endpoint for agent status"""
    try:
        return jsonify(monitor._sanitize_for_json({
            'agents': list(monitor.ai_status.values()),
            'timestamp': datetime.now().isoformat()
        }))
    except Exception as e:
        logger.error(f"API agent status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/heartbeat', methods=['POST'])
def api_heartbeat():
    """API endpoint for receiving heartbeats"""
    try:
        data = request.get_json()
        ai_id = data.get('ai_id')
        task_info = data.get('task_info', {})
        
        success = monitor.receive_heartbeat(ai_id, task_info)
        
        return jsonify({
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"API heartbeat error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files with error handling"""
    try:
        return send_from_directory(monitor.static_dir, filename)
    except Exception as e:
        logger.error(f"Static file error: {e}")
        return "File not found", 404

# SocketIO Events
@socketio.on('connect')
def handle_connect(auth=None):
    """Handle client connection"""
    try:
        logger.info(f"Client connected: {request.sid}")
        emit('status_update', monitor.get_dashboard_data())
    except Exception as e:
        logger.error(f"SocketIO connect error: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        logger.info(f"Client disconnected: {request.sid}")
    except Exception as e:
        logger.error(f"SocketIO disconnect error: {e}")

@socketio.on('request_update')
def handle_request_update():
    """Handle manual update request"""
    try:
        emit('status_update', monitor.get_dashboard_data())
    except Exception as e:
        logger.error(f"SocketIO update request error: {e}")

# Create basic HTML template if it doesn't exist
def create_basic_template():
    """Create a basic HTML template for the dashboard"""
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GODMODE AI Dashboard - Enhanced</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: white; }
        .header { text-align: center; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #2a2a2a; padding: 20px; border-radius: 10px; text-align: center; }
        .agents { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .agent-card { background: #2a2a2a; padding: 20px; border-radius: 10px; border-left: 4px solid #4080FF; }
        .agent-header { display: flex; align-items: center; margin-bottom: 15px; }
        .agent-icon { font-size: 24px; margin-right: 10px; }
        .progress-bar { background: #444; height: 20px; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #4080FF, #57A9FB); transition: width 0.3s; }
        .status { padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
        .status.active { background: #23C343; }
        .status.inactive { background: #FF4444; }
        .status.initializing { background: #FBE842; color: #000; }
        .timestamp { text-align: center; margin-top: 20px; color: #888; }
    </style>
</head>
<body>
    <div class="header">
        <h1>GODMODE AI Dashboard - Enhanced</h1>
        <p>Real-time AI Agent Monitoring with Windows Compatibility</p>
    </div>
    
    <div class="stats" id="stats">
        <!-- Stats will be populated by JavaScript -->
    </div>
    
    <div class="agents" id="agents">
        <!-- Agents will be populated by JavaScript -->
    </div>
    
    <div class="timestamp" id="timestamp">
        <!-- Timestamp will be updated by JavaScript -->
    </div>

    <script>
        const socket = io();
        
        socket.on('status_update', function(data) {
            updateDashboard(data);
        });
        
        function updateDashboard(data) {
            // Update stats
            const statsHtml = `
                <div class="stat-card">
                    <h3>Total AIs</h3>
                    <div style="font-size: 24px; color: #4080FF;">${data.system_stats.total_ais}</div>
                </div>
                <div class="stat-card">
                    <h3>Active AIs</h3>
                    <div style="font-size: 24px; color: #23C343;">${data.system_stats.active_ais}</div>
                </div>
                <div class="stat-card">
                    <h3>Completed Tasks</h3>
                    <div style="font-size: 24px; color: #FBE842;">${data.system_stats.completed_tasks}</div>
                </div>
                <div class="stat-card">
                    <h3>System Health</h3>
                    <div style="font-size: 24px; color: ${data.health_status === 'healthy' ? '#23C343' : data.health_status === 'warning' ? '#FBE842' : '#FF4444'};">${data.health_status.toUpperCase()}</div>
                </div>
            `;
            document.getElementById('stats').innerHTML = statsHtml;
            
            // Update agents
            const agentsHtml = data.ai_agents.map(agent => `
                <div class="agent-card">
                    <div class="agent-header">
                        <span class="agent-icon">${agent.icon}</span>
                        <div>
                            <h3 style="margin: 0;">${agent.name}</h3>
                            <span class="status ${agent.status.toLowerCase()}">${agent.status}</span>
                        </div>
                    </div>
                    <div><strong>Current Task:</strong> ${agent.current_task}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${agent.progress}%;"></div>
                    </div>
                    <div style="font-size: 12px; color: #888;">
                        Progress: ${agent.progress}% | Tasks: ${agent.tasks_completed} | Score: ${agent.performance_score.toFixed(1)}
                    </div>
                </div>
            `).join('');
            document.getElementById('agents').innerHTML = agentsHtml;
            
            // Update timestamp
            document.getElementById('timestamp').innerHTML = `Last updated: ${new Date(data.timestamp).toLocaleString()}`;
        }
        
        // Request initial update
        socket.emit('request_update');
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            socket.emit('request_update');
        }, 30000);
    </script>
</body>
</html>'''
    
    template_path = monitor.templates_dir / "dashboard.html"
    try:
        template_path.write_text(template_content)
        logger.info("Basic dashboard template created")
    except Exception as e:
        logger.error(f"Failed to create template: {e}")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Graceful shutdown
def signal_handler(sig, frame):
    logger.info("Shutting down dashboard...")
    monitor.stop_monitoring()
    sys.exit(0)

if platform.system() != 'Windows':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

# Main execution
if __name__ == '__main__':
    try:
        # Create basic template if it doesn't exist
        if not (monitor.templates_dir / "dashboard.html").exists():
            create_basic_template()
        
        logger.info("Starting GODMODE Dashboard Enhanced...")
        logger.info(f"Platform: {platform.system()}")
        logger.info(f"Python: {sys.version}")
        logger.info(f"Dashboard will be available at http://localhost:3333")
        
        # Run the Flask app with SocketIO
        socketio.run(
            app,
            host='0.0.0.0',
            port=3333,
            debug=False,  # Disable debug in production
            use_reloader=False,  # Disable reloader to prevent issues
            log_output=False  # Reduce log noise
        )
        
    except Exception as e:
        logger.error(f"Failed to start dashboard: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        monitor.stop_monitoring()
