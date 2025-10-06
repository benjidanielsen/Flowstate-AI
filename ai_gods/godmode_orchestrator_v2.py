#!/usr/bin/env python3
"""
🎯 GODMODE ORCHESTRATOR v2.0 - Master Coordination System
⚡ Ultimate autonomous develo            "python_worker": {
                "type": "uvicorn",
                "app": "python-worker.src.main:app",
                "name": "Python Worker",
                "critical": True,
                "restart_on_failure": True,
                "is_service": True,
            },thority
🚀 Mission: Coord                )
                command = [sys.executable, "-m", module_path]
            elif component_type == "uvicorn":
                command = [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    component["app"],
                    "--host",
                    "0.0.0.0",
                ]
            elif component_type == "command":
                command = component["command"]
            else:
                logger.error(f"❌ Unknown component type: {component_type}")
                return Falseall AI agents and systems for seamless autonomous operation
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
from typing import IO, Dict, List, Optional

from ai_gods.logging_config import setup_logging

# Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Setup logging
logger = setup_logging("GODMODE-v2", "godmode-orchestrator-v2.log")


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
        self.port_config = {}

        # Health monitoring
        self.last_health_check: Dict[str, datetime] = {}
        self.health_check_interval = 30  # seconds

        # Component configuration
        self.components = {
            "vscode_backend_api": {
                "type": "python",
                "script": "ai_gods.vscode_backend_api_v2",
                "name": "VSCode Backend API",
                "critical": True,
                "restart_on_failure": True,
                "is_service": True,
            },
            "vscode_agent": {
                "type": "python",
                "script": "ai_gods.vscode_agent_integration",
                "name": "VSCode Agent",
                "critical": True,
                "restart_on_failure": True,
                "is_service": True,
            },
            "communication_hub": {
                "type": "python",
                "script": "ai_gods.communication_hub_enhanced",
                "name": "Communication Hub",
                "critical": True,
                "restart_on_failure": True,
                "is_service": True,
            },
            "project_manager": {
                "type": "python",
                "script": "ai_gods.project_manager_enhanced",
                "name": "Project Manager AI",
                "critical": True,
                "restart_on_failure": True,
                "is_service": True,
            },
            "autonomous_dev": {
                "type": "python",
                "script": "ai_gods.autonomous_development_v2",
                "name": "Autonomous Development",
                "critical": False,
                "restart_on_failure": True,
                "is_service": True,
            },
            "git_agent": {
                "type": "python",
                "script": "ai_gods.git_agent",
                "name": "Git Agent",
                "critical": False,
                "restart_on_failure": False,
                "is_service": False,
            },
            "python_worker": {
                "type": "python_script",
                "script": "python-worker/src/main.py",
                "name": "Python Worker",
                "critical": True,
                "restart_on_failure": True,
                "is_service": True,
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

            # Load port configuration from the state file
            state_file = self.project_root / "godmode-state.json"
            if state_file.exists():
                try:
                    with open(state_file, "r") as f:
                        state_data = json.load(f)
                        self.port_config = state_data.get("ports", {})
                        logger.info(f"Loaded port config: {self.port_config}")
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Could not read port config from {state_file}: {e}")

            env = os.environ.copy()
            # Set component-specific ports if they exist in the config
            if (
                component_id == "python_worker"
                and "PYTHON_API_PORT" in self.port_config
            ):
                env["PYTHON_API_PORT"] = str(self.port_config["PYTHON_API_PORT"])
                logger.info(
                    f"Setting PYTHON_API_PORT to {env['PYTHON_API_PORT']} for python_worker"
                )
            if component_id == "vscode_backend_api" and "API_PORT" in self.port_config:
                env["API_PORT"] = str(self.port_config["API_PORT"])

            command = []
            component_type = component.get("type", "python")

            if component_type == "python":
                # Convert file path to module path for execution with -m
                module_path = (
                    component["script"]
                    .replace("/", ".")
                    .replace("\\", ".")
                    .replace(".py", "")
                )
                command = [sys.executable, "-m", module_path]
            elif component_type == "python_script":
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

            # Ensure PYTHONPATH is set for any python-based component
            if (
                component_type in ["python", "python_script"]
                or component_id == "python_worker"
            ):
                project_root_str = str(self.project_root)
                if "PYTHONPATH" in env:
                    env["PYTHONPATH"] = (
                        f"{project_root_str}{os.pathsep}{env['PYTHONPATH']}"
                    )
                else:
                    env["PYTHONPATH"] = project_root_str

            process = subprocess.Popen(
                command,
                stdout=log_file,
                stderr=log_file,
                cwd=cwd,
                shell=is_shell,
                env=env,
            )

            self.processes[component_id] = process
            self.last_health_check[component_id] = datetime.now()
            logger.info(f"✅ {component['name']} started (PID: {process.pid})")
            return True
        except Exception as e:
            logger.error(
                f"❌ Failed to start {self.components.get(component_id, {}).get('name', component_id)}: {e}",
                exc_info=True,
            )
            return False

    async def stop_component(self, component_id: str):
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
            logger.error(f"❌ Error stopping {component_name}: {e}", exc_info=True)

        if component_id in self.processes:
            del self.processes[component_id]

    async def check_component_health(self, component_id: str):
        """Check if a component is healthy"""
        if component_id not in self.processes:
            # If it's not in the process list, it's either completed or never started.
            # We consider it "healthy" from a monitoring perspective to avoid trying to restart it.
            return True

        process = self.processes[component_id]
        component = self.components[component_id]
        is_service = component.get("is_service", True)

        if process.poll() is not None:
            # Process has terminated
            exit_code = process.poll()

            # If it's a task (not a service) and it exited cleanly, it's a success.
            if not is_service and exit_code == 0:
                logger.info(f"✅ Task '{component['name']}' completed successfully.")
                # Remove it from monitoring.
                del self.processes[component_id]
                return True  # It's "healthy" because it finished as expected.

            # For all other cases (services stopping, tasks failing), it's an unhealthy state.
            logger.warning(
                f"⚠️ Component '{component['name']}' has stopped unexpectedly (exit code: {exit_code})"
            )
            logger.error(f"❌ {component['name']} is unhealthy")
            return False

        # For running services, we could add more sophisticated checks here. For now, running is healthy.
        return True

    async def monitor_health(self):
        """Periodically check the health of all components."""
        while self.running:
            unhealthy_components = []
            component_keys = list(self.processes.keys())  # Create a copy of keys
            for component_id in component_keys:
                if not await self.check_component_health(component_id):
                    unhealthy_components.append(component_id)

            if unhealthy_components:
                logger.warning(
                    f"🚨 Unhealthy components detected: {', '.join(unhealthy_components)}"
                )
                await self.handle_failures(unhealthy_components)
            else:
                running_components = [
                    self.components[cid]["name"]
                    for cid in self.processes
                    if self.processes[cid].poll() is None
                ]
                if running_components:
                    logger.info(
                        f"✅ All monitored components are healthy: {', '.join(running_components)}"
                    )

            await asyncio.sleep(self.health_check_interval)

    async def handle_failures(self, unhealthy_components: List[str]):
        """Handle component failures."""
        for component_id in unhealthy_components:
            component = self.components[component_id]
            if component.get("restart_on_failure", False):
                logger.info(f"🔄 Restarting {component['name']}...")
                await self.stop_component(component_id)
                await asyncio.sleep(2)  # Wait a bit before restarting
                await self.start_component(component_id)
            elif component["critical"]:
                logger.critical(
                    f"💥 Critical component {component['name']} failed and cannot be restarted. Shutting down GODMODE."
                )
                await self.stop_godmode()

    async def start_godmode(self):
        """Start all GODMODE components in the correct order."""
        logger.info("🎯 STARTING GODMODE...")
        self.running = True

        start_order = [
            "python_worker",
            "vscode_backend_api",
            "vscode_agent",
            "communication_hub",
            "project_manager",
            "autonomous_dev",
            "git_agent",
        ]

        for component_id in start_order:
            if not await self.start_component(component_id):
                if self.components[component_id]["critical"]:
                    logger.critical(
                        f"💥 Failed to start critical component {self.components[component_id]['name']}. Aborting GODMODE startup."
                    )
                    await self.stop_godmode()
                    return

        self.godmode_enabled = True
        logger.info("✅ GODMODE ACTIVATED - All systems operational")

        # Start health monitoring
        asyncio.create_task(self.monitor_health())

    async def stop_godmode(self):
        """Stop all GODMODE components."""
        logger.info("🛑 STOPPING GODMODE...")
        self.running = False
        self.godmode_enabled = False

        stop_order = [
            "git_agent",
            "autonomous_dev",
            "project_manager",
            "communication_hub",
            "vscode_agent",
            "vscode_backend_api",
        ]

        for component_id in stop_order:
            if component_id in self.processes:
                await self.stop_component(component_id)

        logger.info("✅ GODMODE DEACTIVATED")

    async def run(self):
        """Main orchestration loop"""
        logger.info("🎯 GODMODE ORCHESTRATOR v2.0 RUNNING...")

        # Start GODMODE
        await self.start_godmode()

        try:
            # Main loop
            while self.running:
                await asyncio.sleep(1)

        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("⚠️ Orchestrator run loop interrupted.")
        finally:
            # Cleanup
            if self.godmode_enabled:
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

    main_task = asyncio.create_task(orchestrator.run())

    try:
        await main_task
    except asyncio.CancelledError:
        logger.info("Main task cancelled.")

    logger.info("✅ GODMODE ORCHESTRATOR v2.0 SHUTDOWN COMPLETE")


if __name__ == "__main__":
    # Ensure log directory exists
    log_dir = Path("godmode-logs")
    log_dir.mkdir(exist_ok=True)

    # Run
    asyncio.run(main())
