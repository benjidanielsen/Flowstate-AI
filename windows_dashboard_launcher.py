#!/usr/bin/env python3
"""
🔥 WINDOWS DASHBOARD LAUNCHER 🔥
Ultra-optimized dashboard for Windows deployment

Features:
- Windows-native optimization
- Auto-port detection and management
- Error-proof startup sequence
- Real-time AI monitoring
- Beautiful Windows-compatible UI
"""

import os
import sys
import time
import json
import platform
import subprocess
import threading
import webbrowser
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import logging

# Suppress Flask development server warning
import warnings
warnings.filterwarnings("ignore", message=".*development server.*")

# Import our enhanced sync engine
try:
    from enhanced_ai_sync_engine import EnhancedManusSyncEngine, EnhancedManusInterface, ManusRole
except ImportError:
    print("❌ Enhanced sync engine not found. Please ensure enhanced_ai_sync_engine.py is in the same directory.")
    sys.exit(1)

class WindowsDashboard:
    """Windows-optimized dashboard for AI monitoring"""
    
    def __init__(self, port=3333):
        self.port = port
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'flowstate_ai_windows_dashboard'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", logger=False, engineio_logger=False)
        
        # Initialize enhanced sync engine
        self.sync_engine = None
        self.manus_interface = None
        self.running = False
        self.update_thread = None
        
        # Setup logging
        self._setup_logging()
        
        # Setup routes
        self._setup_routes()
        
        # Setup WebSocket handlers
        self._setup_websocket_handlers()
        
        self.logger.info("🪟 Windows Dashboard initialized")
    
    def _setup_logging(self):
        """Setup Windows-compatible logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"dashboard_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("WindowsDashboard")
        
        # Suppress Flask/SocketIO logs
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        logging.getLogger('socketio').setLevel(logging.ERROR)
        logging.getLogger('engineio').setLevel(logging.ERROR)
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            return render_template('windows_dashboard.html')
        
        @self.app.route('/api/health')
        def health_check():
            if self.manus_interface:
                return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
            return jsonify({'status': 'initializing', 'timestamp': datetime.now().isoformat()})
        
        @self.app.route('/api/dashboard')
        def api_dashboard():
            if self.manus_interface:
                try:
                    data = self.manus_interface.get_system_health()
                    return jsonify(data)
                except Exception as e:
                    return jsonify({'error': str(e), 'timestamp': datetime.now().isoformat()})
            return jsonify({'error': 'Sync engine not initialized', 'timestamp': datetime.now().isoformat()})
        
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            return send_from_directory('static', filename)
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            self.logger.info("🔌 Client connected to dashboard")
            if self.manus_interface:
                try:
                    data = self.manus_interface.get_system_health()
                    emit('dashboard_update', data)
                except Exception as e:
                    emit('error', {'message': str(e)})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.logger.info("🔌 Client disconnected from dashboard")
        
        @self.socketio.on('request_update')
        def handle_update_request():
            if self.manus_interface:
                try:
                    data = self.manus_interface.get_system_health()
                    emit('dashboard_update', data)
                except Exception as e:
                    emit('error', {'message': str(e)})
    
    def _create_dashboard_template(self):
        """Create the Windows-optimized dashboard HTML template"""
        template_dir = Path("templates")
        template_dir.mkdir(exist_ok=True)
        
        html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 FlowState-AI Dashboard - Windows</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .header {
            background: rgba(0,0,0,0.2);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #4080FF;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            font-weight: 700;
        }
        
        .platform-info {
            font-size: 1.1em;
            opacity: 0.9;
            margin-top: 10px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        }
        
        .card h3 {
            color: #4080FF;
            margin-bottom: 20px;
            font-size: 1.4em;
            font-weight: 600;
        }
        
        .metric-large {
            font-size: 3em;
            font-weight: 700;
            text-align: center;
            margin: 20px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .metric-medium {
            font-size: 1.8em;
            font-weight: 600;
            margin: 15px 0;
        }
        
        .metric-label {
            font-size: 0.9em;
            opacity: 0.8;
            text-align: center;
            margin-top: 5px;
        }
        
        .health-excellent { color: #23C343; }
        .health-good { color: #57A9FB; }
        .health-warning { color: #FBE842; }
        .health-critical { color: #FF9A2E; }
        .health-emergency { color: #FF4757; }
        
        .progress-bar {
            width: 100%;
            height: 12px;
            background: rgba(255,255,255,0.2);
            border-radius: 6px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4080FF, #57A9FB);
            transition: width 0.5s ease;
            border-radius: 6px;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 20px;
        }
        
        .status-item {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .live-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #23C343;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        .error-prevention {
            background: rgba(35,195,67,0.2);
            border-left: 4px solid #23C343;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 25px;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(10px);
            font-size: 0.9em;
        }
        
        .connected { border-left: 4px solid #23C343; }
        .disconnected { border-left: 4px solid #FF4757; }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        
        .windows-optimization {
            background: rgba(64,128,255,0.2);
            border: 2px solid #4080FF;
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connection-status">
        <span class="live-indicator"></span>
        <span id="connection-text">Connecting...</span>
    </div>
    
    <div class="header">
        <h1>🔥 FlowState-AI Dashboard</h1>
        <p>Windows-Optimized AI Development Monitoring</p>
        <div class="platform-info" id="platform-info">
            <span class="live-indicator"></span>
            Loading system information...
        </div>
    </div>
    
    <div class="dashboard-grid">
        <!-- System Health Overview -->
        <div class="card">
            <h3>🎯 System Health</h3>
            <div class="metric-large" id="health-status">LOADING</div>
            <div class="metric-label">Overall System Status</div>
            
            <div class="metric-medium" id="performance-score">0%</div>
            <div class="metric-label">Performance Score</div>
            
            <div class="progress-bar">
                <div class="progress-fill" id="performance-bar" style="width: 0%"></div>
            </div>
        </div>
        
        <!-- System Resources -->
        <div class="card">
            <h3>💻 System Resources</h3>
            <div class="status-grid">
                <div class="status-item">
                    <div class="metric-medium" id="cpu-usage">0%</div>
                    <div class="metric-label">CPU Usage</div>
                </div>
                <div class="status-item">
                    <div class="metric-medium" id="memory-usage">0%</div>
                    <div class="metric-label">Memory Usage</div>
                </div>
            </div>
            
            <div class="windows-optimization">
                <strong>🪟 Windows Optimizations Active</strong>
                <div style="font-size: 0.9em; margin-top: 5px; opacity: 0.8;">
                    High-priority process, UTF-8 encoding, optimized paths
                </div>
            </div>
        </div>
        
        <!-- AI Manus Status -->
        <div class="card">
            <h3>🤖 AI Manus Status</h3>
            <div id="manus-status">
                <div class="status-item">
                    <div class="metric-medium">Initializing...</div>
                    <div class="metric-label">AI Agents</div>
                </div>
            </div>
        </div>
        
        <!-- Error Prevention -->
        <div class="card">
            <h3>🛡️ Error Prevention</h3>
            <div id="error-prevention-list">
                <div class="error-prevention">
                    <strong>Proactive Error Prevention Active</strong>
                    <div style="font-size: 0.9em; margin-top: 5px;">
                        Monitoring for potential issues...
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Performance Metrics -->
        <div class="card full-width">
            <h3>📊 Performance Metrics</h3>
            <div class="status-grid">
                <div class="status-item">
                    <div class="metric-medium" id="uptime">0h</div>
                    <div class="metric-label">Uptime</div>
                </div>
                <div class="status-item">
                    <div class="metric-medium" id="tasks-per-hour">0</div>
                    <div class="metric-label">Tasks/Hour</div>
                </div>
                <div class="status-item">
                    <div class="metric-medium" id="error-rate">0%</div>
                    <div class="metric-label">Error Rate</div>
                </div>
                <div class="status-item">
                    <div class="metric-medium" id="response-time">0ms</div>
                    <div class="metric-label">Avg Response</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        let connected = false;
        
        // Connection status
        socket.on('connect', function() {
            connected = true;
            updateConnectionStatus(true);
            console.log('🔌 Connected to dashboard');
        });
        
        socket.on('disconnect', function() {
            connected = false;
            updateConnectionStatus(false);
            console.log('🔌 Disconnected from dashboard');
        });
        
        // Dashboard updates
        socket.on('dashboard_update', function(data) {
            updateDashboard(data);
        });
        
        socket.on('error', function(data) {
            console.error('❌ Dashboard error:', data.message);
        });
        
        function updateConnectionStatus(isConnected) {
            const statusElement = document.getElementById('connection-status');
            const textElement = document.getElementById('connection-text');
            
            if (isConnected) {
                statusElement.className = 'connection-status connected';
                textElement.textContent = 'Connected';
            } else {
                statusElement.className = 'connection-status disconnected';
                textElement.textContent = 'Disconnected';
            }
        }
        
        function updateDashboard(data) {
            try {
                // Platform info
                if (data.platform) {
                    document.getElementById('platform-info').innerHTML = 
                        '<span class="live-indicator"></span>' + 
                        `Running on ${data.platform} - AI Sync Engine Active`;
                }
                
                // System health
                if (data.system_health) {
                    const health = data.system_health;
                    
                    const healthElement = document.getElementById('health-status');
                    healthElement.textContent = health.status.toUpperCase();
                    healthElement.className = 'metric-large health-' + health.status;
                    
                    const scoreElement = document.getElementById('performance-score');
                    scoreElement.textContent = Math.round(health.performance_score) + '%';
                    
                    const barElement = document.getElementById('performance-bar');
                    barElement.style.width = health.performance_score + '%';
                    
                    document.getElementById('cpu-usage').textContent = Math.round(health.cpu_usage) + '%';
                    document.getElementById('memory-usage').textContent = Math.round(health.memory_usage) + '%';
                }
                
                // Performance metrics
                if (data.performance_metrics) {
                    const metrics = data.performance_metrics;
                    document.getElementById('uptime').textContent = Math.round(metrics.uptime_hours) + 'h';
                    document.getElementById('tasks-per-hour').textContent = Math.round(metrics.tasks_per_hour);
                    document.getElementById('error-rate').textContent = (metrics.error_rate * 100).toFixed(1) + '%';
                    document.getElementById('response-time').textContent = Math.round(metrics.avg_response_time) + 'ms';
                }
                
                // Manus status
                if (data.manus_instances) {
                    updateManusStatus(data.manus_instances);
                }
                
                // Error prevention
                if (data.error_prevention) {
                    updateErrorPrevention(data.error_prevention);
                }
                
            } catch (error) {
                console.error('❌ Dashboard update error:', error);
            }
        }
        
        function updateManusStatus(instances) {
            const container = document.getElementById('manus-status');
            container.innerHTML = '';
            
            Object.values(instances).forEach(manus => {
                const statusDiv = document.createElement('div');
                statusDiv.className = 'status-item';
                statusDiv.innerHTML = `
                    <div class="metric-medium">${manus.id}</div>
                    <div class="metric-label">${manus.status} - ${manus.role}</div>
                `;
                container.appendChild(statusDiv);
            });
        }
        
        function updateErrorPrevention(prevention) {
            const container = document.getElementById('error-prevention-list');
            container.innerHTML = '';
            
            Object.entries(prevention).forEach(([errorType, data]) => {
                const preventionDiv = document.createElement('div');
                preventionDiv.className = 'error-prevention';
                preventionDiv.innerHTML = `
                    <strong>${errorType.replace('_', ' ').toUpperCase()}</strong>
                    <div style="font-size: 0.9em; margin-top: 5px;">
                        Prevented: ${data.prevention_count} times
                        ${data.auto_fix ? '(Auto-fix enabled)' : ''}
                    </div>
                `;
                container.appendChild(preventionDiv);
            });
        }
        
        // Request updates every 5 seconds
        setInterval(() => {
            if (connected) {
                socket.emit('request_update');
            }
        }, 5000);
        
        // Initial load
        fetch('/api/dashboard')
            .then(response => response.json())
            .then(data => updateDashboard(data))
            .catch(error => console.error('❌ Initial load error:', error));
    </script>
</body>
</html>
        '''
        
        with open(template_dir / 'windows_dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info("✅ Dashboard template created")
    
    def _find_available_port(self, start_port=3333):
        """Find an available port starting from the given port"""
        import socket
        
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        
        raise RuntimeError("No available ports found")
    
    def _dashboard_update_loop(self):
        """Continuous dashboard updates"""
        while self.running:
            try:
                if self.manus_interface:
                    data = self.manus_interface.get_system_health()
                    self.socketio.emit('dashboard_update', data)
                
                time.sleep(3)  # Update every 3 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Dashboard update error: {e}")
                time.sleep(10)
    
    def start(self, auto_open_browser=True):
        """Start the Windows-optimized dashboard"""
        try:
            self.logger.info("🚀 Starting Windows Dashboard...")
            
            # Find available port
            self.port = self._find_available_port(self.port)
            self.logger.info(f"📡 Using port {self.port}")
            
            # Create dashboard template
            self._create_dashboard_template()
            
            # Initialize enhanced sync engine
            self.logger.info("🤖 Initializing Enhanced AI Sync Engine...")
            self.manus_interface = EnhancedManusInterface(
                "manus_windows_dashboard",
                ManusRole.QUALITY_ENHANCER,
                ["python", "ai_systems", "dashboard", "windows_optimization", "monitoring"]
            )
            
            # Apply Windows optimizations
            if self.manus_interface.optimize_for_windows():
                self.logger.info("🪟 Windows optimizations applied")
            
            # Start update thread
            self.running = True
            self.update_thread = threading.Thread(target=self._dashboard_update_loop, daemon=True)
            self.update_thread.start()
            
            # Open browser
            if auto_open_browser:
                def open_browser():
                    time.sleep(2)  # Wait for server to start
                    webbrowser.open(f'http://localhost:{self.port}')
                
                threading.Thread(target=open_browser, daemon=True).start()
            
            self.logger.info(f"🔥 Dashboard starting at http://localhost:{self.port}")
            self.logger.info("🎯 Windows-optimized AI monitoring active!")
            
            # Start Flask app
            self.socketio.run(
                self.app, 
                host='localhost', 
                port=self.port, 
                debug=False,
                use_reloader=False,
                log_output=False
            )
            
        except Exception as e:
            self.logger.error(f"❌ Dashboard startup failed: {e}")
            raise
    
    def stop(self):
        """Stop the dashboard"""
        self.running = False
        if self.manus_interface and self.manus_interface.sync_engine:
            self.manus_interface.sync_engine.stop_enhanced_engine()
        self.logger.info("🛑 Windows Dashboard stopped")

def main():
    """Main entry point for Windows dashboard"""
    print("🔥 FLOWSTATE-AI WINDOWS DASHBOARD")
    print("=" * 50)
    print("🪟 Windows-optimized AI monitoring system")
    print("⚡ Enhanced performance and error prevention")
    print("📊 Real-time AI development tracking")
    print("")
    
    try:
        # Create and start dashboard
        dashboard = WindowsDashboard()
        
        print(f"🚀 Starting dashboard...")
        print(f"📡 Will open automatically in your browser")
        print(f"🛑 Press Ctrl+C to stop")
        print("")
        
        dashboard.start(auto_open_browser=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down dashboard...")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
