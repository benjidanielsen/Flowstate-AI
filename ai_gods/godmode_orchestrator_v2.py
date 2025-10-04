#!/usr/bin/env python3
"""
🎯 GODMODE ORCHESTRATOR v2.0 - Master Coordination System
⚡ Ultimate autonomous development authority
🚀 Mission: Coordinate all AI agents and systems for seamless autonomous operation
🧠 Features: Multi-agent coordination, health monitoring, auto-recovery
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Setup logging
# Force UTF-8 encoding for all handlers to prevent UnicodeEncodeError on Windows
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="🎯 [GODMODE-v2] %(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "godmode-logs/godmode-orchestrator-v2.log", encoding="utf-8"
        ),
        logging.StreamHandler(sys.stdout),  # Explicitly use stdout
    ],
    encoding="utf-8",  # This is for the basicConfig, might not be inherited by handlers always
)

# For StreamHandler, we need to be more direct on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except TypeError:
        # In some environments (like older Python versions or certain terminals),
        # reconfigure might not be available. We try an alternative.
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

logger = logging.getLogger(__name__)


class GODMODEOrchestratorV2:
    """
    GODMODE Orchestrator v2.0 - Master coordinator for all AI agents and systems
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent

        # Component processes
        self.processes: Dict[str, subprocess.Popen] = {}

        # System state
        self.running = False
        self.godmode_enabled = False

        # Health monitoring
        self.last_health_check = {}
        self.health_check_interval = 30  # seconds

        # Component configuration
        self.components = {
            "backend_api": {
                "type": "python",
                "script": "ai_gods/vscode_backend_api_v2.py",
                "name": "VSCode Backend API",
                "critical": True,
                "restart_on_failure": True,
            },
            "project_manager": {
                "type": "python",
                "script": "ai_gods/project_manager_v2.py",
                "name": "Project Manager AI",
                "critical": True,
                "restart_on_failure": True,
            },
            "communication_hub": {
                "type": "python",
                "script": "ai_gods/communication_hub_v2.py",
                "name": "Communication Hub",
                "critical": True,
                "restart_on_failure": True,
            },
            "autonomous_dev": {
                "type": "python",
                "script": "ai_gods/autonomous_development_v2.py",
                "name": "Autonomous Development",
                "critical": False,
                "restart_on_failure": True,
            },
            "python_worker": {
                "type": "command",
                "command": [
                    "python",
                    "-m",
                    "uvicorn",
                    "src.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                ],
                "cwd": "python-worker",
                "name": "Python Worker",
                "critical": True,
                "restart_on_failure": True,
            },
            "godmode_dashboard": {
                "type": "python",
                "script": "godmode-dashboard/app_enhanced.py",
                "name": "Godmode Dashboard",
                "critical": True,
                "restart_on_failure": True,
            },
            "backend_server": {
                "type": "command",
                "command": ["npm", "run", "dev"],
                "cwd": "backend",
                "name": "Backend API Server",
                "critical": True,
                "restart_on_failure": True,
            },
            "frontend_server": {
                "type": "command",
                "command": [
                    "npm",
                    "run",
                    "dev",
                    "--",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "3000",
                ],
                "cwd": "frontend",
                "name": "Frontend Server",
                "critical": True,
                "restart_on_failure": True,
            },
        }

        logger.info("🚀 GODMODE ORCHESTRATOR v2.0 INITIALIZED")

    async def start_component(self, component_id: str) -> bool:
        """Start a component"""
        try:
            component = self.components.get(component_id)
            if not component:
                logger.error(f"❌ Unknown component: {component_id}")
                return False

            logger.info(f"🚀 Starting {component['name']}...")

            log_dir = self.project_root / "godmode-logs"
            log_dir.mkdir(exist_ok=True)
            log_file_path = log_dir / f"{component_id}.log"

            command = []
            component_type = component.get("type", "python")

            if component_type == "python":
                script_path = self.project_root / component["script"]
                if not script_path.exists():
                    logger.error(f"❌ Script not found: {script_path}")
                    return False
                command = [sys.executable, str(script_path)]
            elif component_type == "command":
                command = component["command"]
            else:
                logger.error(f"❌ Unknown component type: {component_type}")
                return False

            cwd = self.project_root / component.get("cwd", "")

            log_file = open(log_file_path, "a", encoding="utf-8")

            is_shell = (
                True
                if sys.platform == "win32" and component_type == "command"
                else False
            )

            process = subprocess.Popen(
                command,
                stdout=log_file,
                stderr=log_file,
                cwd=cwd,
                shell=is_shell,
            )

            self.processes[component_id] = process
            self.last_health_check[component_id] = datetime.now()

            logger.info(f"✅ {component['name']} started (PID: {process.pid})")
            return True

        except Exception as e:
            logger.error(f"❌ Error starting {component_id}: {e}")
            return False

    async def stop_component(self, component_id: str) -> bool:
        """Stop a component"""
        try:
            if component_id not in self.processes:
                logger.warning(f"⚠️ Component not running: {component_id}")
                return False

            process = self.processes[component_id]
            component = self.components[component_id]

            logger.info(f"🛑 Stopping {component['name']}...")

            # Try graceful shutdown first
            process.terminate()

            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Force killing {component['name']}...")
                process.kill()
                process.wait()

            del self.processes[component_id]
            logger.info(f"✅ {component['name']} stopped")
            return True

        except Exception as e:
            logger.error(f"❌ Error stopping {component_id}: {e}")
            return False

    async def check_component_health(self, component_id: str) -> bool:
        """Check if a component is healthy"""
        if component_id not in self.processes:
            return False

        process = self.processes[component_id]

        # Check if process is still running
        if process.poll() is not None:
            logger.warning(
                f"⚠️ Component {component_id} has stopped (exit code: {process.returncode})"
            )
            return False

        return True

    async def health_monitor_loop(self):
        """Monitor health of all components"""
        while self.running:
            try:
                for component_id, component in self.components.items():
                    if component_id in self.processes:
                        healthy = await self.check_component_health(component_id)

                        if not healthy:
                            logger.error(f"❌ {component['name']} is unhealthy")

                            # Restart if configured
                            if component["restart_on_failure"]:
                                logger.info(f"🔄 Restarting {component['name']}...")
                                await self.stop_component(component_id)
                                await asyncio.sleep(2)
                                await self.start_component(component_id)

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"❌ Error in health monitor: {e}")
                await asyncio.sleep(self.health_check_interval)

    async def start_godmode(self):
        """Start GODMODE - all systems"""
        logger.info("🎯 STARTING GODMODE...")

        self.running = True
        self.godmode_enabled = True

        # Start all components in order
        start_order = [
            "backend_api",
            "communication_hub",
            "project_manager",
            "autonomous_dev",
            "python_worker",
            "godmode_dashboard",
            "backend_server",
            "frontend_server",
        ]

        for component_id in start_order:
            success = await self.start_component(component_id)
            if not success and self.components[component_id]["critical"]:
                logger.error(f"❌ Failed to start critical component: {component_id}")
                logger.error("❌ GODMODE startup failed")
                await self.stop_godmode()
                return False

            # Wait a bit between starts
            await asyncio.sleep(2)

        logger.info("✅ GODMODE ACTIVATED - All systems operational")
        return True

    async def stop_godmode(self):
        """Stop GODMODE - all systems"""
        logger.info("🛑 STOPPING GODMODE...")

        self.godmode_enabled = False

        # Stop all components in reverse order
        stop_order = [
            "autonomous_dev",
            "project_manager",
            "communication_hub",
            "backend_api",
        ]

        for component_id in stop_order:
            if component_id in self.processes:
                await self.stop_component(component_id)
                await asyncio.sleep(1)

        self.running = False
        logger.info("✅ GODMODE DEACTIVATED")

    async def run(self):
        """Main orchestration loop"""
        logger.info("🎯 GODMODE ORCHESTRATOR v2.0 RUNNING...")

        # Start GODMODE
        success = await self.start_godmode()

        if not success:
            logger.error("❌ Failed to start GODMODE")
            return

        # Start health monitor
        health_monitor_task = asyncio.create_task(self.health_monitor_loop())

        try:
            # Main loop
            while self.running:
                # Log status periodically
                if datetime.now().second % 60 == 0:
                    active_components = len(self.processes)
                    logger.info(
                        f"📊 Status: {active_components}/{len(self.components)} components running"
                    )

                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("⚠️ Keyboard interrupt received")
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
        finally:
            # Cleanup
            health_monitor_task.cancel()
            await self.stop_godmode()

    def signal_handler(self, signum, frame):
        """Handle system signals"""
        logger.info(f"⚠️ Received signal {signum}")
        self.running = False


async def main():
    """Main entry point"""
    orchestrator = GODMODEOrchestratorV2()

    # Setup signal handlers
    signal.signal(signal.SIGINT, orchestrator.signal_handler)
    signal.signal(signal.SIGTERM, orchestrator.signal_handler)

    # Run orchestrator
    await orchestrator.run()

    logger.info("✅ GODMODE ORCHESTRATOR v2.0 SHUTDOWN COMPLETE")


if __name__ == "__main__":
    # Ensure log directory exists
    log_dir = Path("godmode-logs")
    log_dir.mkdir(exist_ok=True)

    # Run
    asyncio.run(main())

