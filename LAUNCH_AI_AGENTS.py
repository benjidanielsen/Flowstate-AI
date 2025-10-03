#!/usr/bin/env python3
"""
🚀 AUTONOMOUS AI AGENT LAUNCHER
Starts all AI agents for 24/7 autonomous development
No user intervention required - full GODMODE operation
"""

import subprocess
import sys
import time
import os
import logging
import platform
from pathlib import Path
from datetime import datetime

# Ensure UTF-8 encoding for stdout on Windows to support emoji logging
if platform.system() == 'Windows':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Setup logging
log_dir = Path(__file__).parent / "godmode-logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='🚀 [AI-LAUNCHER] %(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'ai-launcher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIAgentLauncher:
    """Launches and manages all autonomous AI agents"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.ai_gods_dir = self.project_root / "ai-gods"
        self.processes = {}
        self.python_cmd = self.get_python_command()
        
    def get_python_command(self):
        """Detect the correct Python command"""
        for cmd in ['python3.11', 'python3', 'python']:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    logger.info(f"✅ Using Python command: {cmd}")
                    return cmd
            except:
                continue
        logger.error("❌ No Python installation found!")
        sys.exit(1)
    
    def check_dependencies(self):
        """Ensure required packages are installed"""
        logger.info("📦 Checking Python dependencies...")
        required = ['flask', 'flask_socketio', 'requests']
        
        try:
            for package in required:
                __import__(package)
            logger.info("✅ All dependencies installed")
            return True
        except ImportError as e:
            logger.warning(f"⚠️  Missing dependency: {e}")
            logger.info("📥 Installing missing packages...")
            subprocess.run([self.python_cmd, '-m', 'pip', 'install', 
                          'flask', 'flask-socketio', 'flask-cors', 'requests'],
                         check=False)
            return True
    
    def create_godmode_directories(self):
        """Create all necessary directories for AI agents"""
        directories = [
            "godmode-logs",
            "godmode-dashboard",
            "ai-communication",
            "task-queues",
            "progress-tracking",
            "innovation-reports",
            "collective-memory",
            "knowledge-sharing"
        ]
        
        for directory in directories:
            (self.project_root / directory).mkdir(exist_ok=True)
        
        logger.info("📁 GODMODE directory structure ready")
    
    def start_agent(self, agent_name, script_path):
        """Start an individual AI agent"""
        try:
            logger.info(f"🤖 Starting {agent_name}...")
            
            # Start process in background
            if sys.platform == 'win32':
                # Windows: Use pythonw to run without console window
                process = subprocess.Popen(
                    [self.python_cmd, str(script_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            else:
                # Linux/Mac: Run in background
                process = subprocess.Popen(
                    [self.python_cmd, str(script_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True
                )
            
            self.processes[agent_name] = process
            logger.info(f"✅ {agent_name} started (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {agent_name}: {e}")
            return False
    
    def launch_all_agents(self):
        """Launch all AI agents in the correct order"""
        logger.info("=" * 60)
        logger.info("🚀 LAUNCHING AUTONOMOUS AI AGENT SYSTEM")
        logger.info("=" * 60)
        
        # Check prerequisites
        self.check_dependencies()
        self.create_godmode_directories()
        
        # Define agents in startup order
        agents = [
            ("Collective Memory", self.ai_gods_dir / "collective-memory-system.py"),
            ("Communication Hub", self.ai_gods_dir / "ai-communication-hub.py"),
            ("AI Democracy", self.ai_gods_dir / "ai-democracy-system.py"),
            ("Innovation AI", self.ai_gods_dir / "innovation-ai.py"),
            ("Project Manager", self.ai_gods_dir / "project-manager.py")
        ]
        
        # Start each agent with delay
        for agent_name, script_path in agents:
            if script_path.exists():
                self.start_agent(agent_name, script_path)
                time.sleep(2)  # Give each agent time to initialize
            else:
                logger.warning(f"⚠️  {agent_name} script not found: {script_path}")
        
        logger.info("=" * 60)
        logger.info(f"✅ LAUNCHED {len(self.processes)} AI AGENTS")
        logger.info("🎯 AUTONOMOUS DEVELOPMENT MODE ACTIVE")
        logger.info("=" * 60)
        
        # Log agent status
        self.log_agent_status()
    
    def log_agent_status(self):
        """Write agent status to file for monitoring"""
        status_file = self.project_root / "godmode-logs" / "agent-status.json"
        
        import json
        status = {
            "timestamp": datetime.now().isoformat(),
            "active_agents": len(self.processes),
            "agents": {}
        }
        
        for name, process in self.processes.items():
            status["agents"][name] = {
                "pid": process.pid,
                "status": "RUNNING" if process.poll() is None else "STOPPED"
            }
        
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info(f"📊 Agent status saved to {status_file}")
    
    def monitor_agents(self):
        """Monitor agent health (runs indefinitely)"""
        logger.info("👁️  Monitoring agent health...")
        logger.info("Press Ctrl+C to stop monitoring (agents will continue running)")
        
        try:
            while True:
                time.sleep(30)  # Check every 30 seconds
                
                for name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        logger.warning(f"⚠️  {name} has stopped! Restarting...")
                        # Find the script path and restart
                        script_name = name.lower().replace(" ", "-") + ".py"
                        script_path = self.ai_gods_dir / script_name
                        if script_path.exists():
                            self.start_agent(name, script_path)
                
                # Update status file
                self.log_agent_status()
                
        except KeyboardInterrupt:
            logger.info("\n👋 Monitoring stopped. AI agents continue running in background.")
    
    def stop_all_agents(self):
        """Stop all running agents"""
        logger.info("🛑 Stopping all AI agents...")
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ Stopped {name}")
            except:
                process.kill()
                logger.info(f"⚠️  Force killed {name}")
        
        logger.info("✅ All agents stopped")

def main():
    """Main entry point"""
    launcher = AIAgentLauncher()
    
    # Check if we should stop agents
    if len(sys.argv) > 1 and sys.argv[1] == 'stop':
        launcher.stop_all_agents()
        return
    
    # Launch all agents
    launcher.launch_all_agents()
    
    # Monitor agents (optional - can be run in background)
    if '--monitor' in sys.argv:
        launcher.monitor_agents()
    else:
        logger.info("")
        logger.info("🎉 AI AGENTS LAUNCHED SUCCESSFULLY!")
        logger.info("")
        logger.info("💡 Tips:")
        logger.info("  - Agents are running in the background")
        logger.info("  - Check godmode-logs/ai-launcher.log for details")
        logger.info("  - Check godmode-logs/agent-status.json for status")
        logger.info("  - Run with --monitor to watch agent health")
        logger.info("  - Run with 'stop' argument to stop all agents")
        logger.info("")
        logger.info("🚀 AUTONOMOUS DEVELOPMENT IS NOW ACTIVE!")

if __name__ == "__main__":
    main()
